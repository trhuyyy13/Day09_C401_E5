# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Lương Tiến Dũng  
**Vai trò trong nhóm:** Retrieval Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong lab này mình tập trung chính ở Sprint 3, với mục tiêu tune retrieval thay vì thay đổi toàn bộ pipeline. Cụ thể, mình chọn hướng **hybrid retrieval** (kết hợp dense + sparse/BM25) vì bộ tài liệu có cả câu mô tả tự nhiên lẫn keyword đặc thù như mã lỗi hoặc tên quy trình. Mình hoàn thiện `retrieve_sparse()` để lấy candidate theo từ khóa, sau đó cùng thành viên khác viết `retrieve_hybrid()` với Reciprocal Rank Fusion để hợp nhất thứ hạng từ hai nhánh truy xuất. Mình giữ `rag_answer()` tương thích với baseline bằng cách không đổi giao diện hàm và vẫn dùng cùng grounded prompt, nhờ vậy team eval có thể so sánh A/B nhanh trên cùng tập câu hỏi. Phần của mình nối trực tiếp với Eval Owner qua hàm `compare_retrieval_strategies()`, đồng thời hỗ trợ Documentation Owner ghi lý do chọn variant vào tuning log.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)


Điều mình hiểu rõ hơn sau lab là sự khác nhau giữa “retrieval đúng tài liệu” và “retrieval đúng đoạn đủ dùng để trả lời”. Trước đây mình nghĩ chỉ cần top-1 có vẻ liên quan là ổn, nhưng khi chạy thực tế thì nhiều trường hợp dense lấy đúng source nhưng sai đoạn trọng tâm, dẫn đến câu trả lời thiếu hoặc mơ hồ. Nhờ đó mình thấy hybrid retrieval có giá trị vì dense mạnh ở ngữ nghĩa, còn sparse mạnh ở exact term; hai hướng bù trừ nhau giúp recall ổn định hơn trên tập câu hỏi đa dạng.

Mình cũng hiểu sâu hơn về grounded prompt và cơ chế abstain. Một pipeline RAG tốt không chỉ “trả lời được” mà còn phải “biết từ chối” khi evidence yếu. Trong code, guard theo `MIN_RELEVANCE_SCORE` kết hợp chuẩn hóa output về “Không đủ dữ liệu” giúp hệ thống giảm tự tin sai. Đây là điểm quan trọng khi dùng RAG cho ngữ cảnh nội bộ, vì trả lời sai quy trình còn nguy hiểm hơn trả lời thiếu.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều làm mình ngạc nhiên là hybrid không phải lúc nào cũng vượt baseline ở mọi câu hỏi. Ban đầu giả thuyết của mình là “thêm sparse thì chắc chắn tốt hơn dense”, nhưng thực tế có câu hỏi ngắn, ngữ nghĩa rõ, dense đã đủ mạnh nên hybrid chỉ cải thiện nhẹ hoặc gần như ngang nhau. Khó khăn lớn nhất là cân bằng tín hiệu giữa hai nhánh truy xuất để tránh sparse kéo lên các chunk trùng từ nhưng không đúng ý.

Phần mất thời gian debug nhất là chuẩn hóa điểm khi hợp nhất ranking. Dense dùng similarity, sparse dùng BM25 raw score, nên không thể cộng trực tiếp. Mình chuyển sang RRF để dựa trên thứ hạng thay vì thang điểm tuyệt đối, giúp kết quả ổn định hơn giữa nhiều kiểu query. Một điểm nữa là kiểm soát noise: nếu nhánh sparse giữ cả candidate điểm 0 thì context bị loãng; khi lọc score > 0, chất lượng context tốt hơn rõ rệt và câu trả lời bám evidence hơn.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)


**Câu hỏi:** “SLA xử lý ticket P1 là bao lâu?”

**Phân tích:**

Ở baseline dense, câu này thường trả lời đúng ý chính và có citation, nhưng độ ổn định phụ thuộc vào việc đoạn chứa con số SLA có nằm đúng top context hay không. Trong vài lần chạy, baseline lấy đúng tài liệu SLA nhưng ưu tiên đoạn mô tả chung trước đoạn có mốc thời gian cụ thể, khiến câu trả lời bị thiếu mức chi tiết cần thiết. Nếu chấm scorecard, mình xem đây là trường hợp “partially correct”: đúng domain, đúng nguồn, nhưng chưa đủ chuẩn về độ đầy đủ.

Khi chuyển sang hybrid, nhánh sparse giúp tăng cơ hội kéo đúng đoạn chứa cụm “P1” và “SLA” lên cao hơn. Kết quả thực tế là top context bám sát câu hỏi hơn, câu trả lời ngắn gọn và có citation ổn định hơn baseline. Theo phân tích lỗi, vấn đề chính ban đầu nằm ở **retrieval** (chọn đoạn chưa tối ưu), không phải generation, vì prompt grounded đã ép mô hình trả lời theo context. Variant hybrid cải thiện được vì nó giải quyết đúng nút nghẽn: tăng recall cho token quan trọng mà dense đôi lúc bỏ lỡ khi ưu tiên tương đồng ngữ nghĩa rộng.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, mình sẽ thử **rerank bằng cross-encoder** sau bước hybrid để xử lý trường hợp top-k vẫn còn nhiễu. Mình chọn hướng này vì kết quả A/B hiện tại cho thấy retrieval đã cải thiện, nhưng một số câu vẫn trả lời thiếu chi tiết do đoạn tốt nhất chưa luôn đứng đầu. Ngoài ra mình sẽ tinh chỉnh `dense_weight/sparse_weight` theo từng nhóm query (policy vs error code) thay vì dùng một cấu hình cố định cho toàn bộ tập test.

---
