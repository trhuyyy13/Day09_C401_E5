# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Lương Anh Tuấn

**Vai trò trong nhóm:** Sprint 1 Owner, Sprint 4 Experimenter

**Ngày nộp:** 13/04/2026

**Độ dài yêu cầu:** 500–800 từ

Team chúng em chia thành 3 cặp (Tuấn+ Đăng, Huy + Sơn, Đạt + Dũng, Huy + Sơn). Mỗi cặp đảm nhận 1 sprint, trong đó tôi và Đăng tập trung vào Sprint 1 (Indexing), Huy + Sơn làm Sprint 2 (Retrieval), Đạt + Dũng đảm nhận Sprint 3 (Evaluation). Sprint 4 cả nhóm cùng làm việc và chạy thực nghiệm để tìm ra config tốt nhất.

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong lab này, tôi tập trung vào Sprint 1 với vai trò phát triển chính cho phần indexing của pipeline RAG. Tôi đã implement hàm `get_embedding` sử dụng OpenAI API để sinh embedding cho từng chunk văn bản, hoàn thiện logic chunking chia đoạn theo paragraph và overlap, đồng thời kết nối pipeline với ChromaDB để lưu trữ embedding và metadata. Tôi cũng xử lý các lỗi phát sinh khi gọi API, đảm bảo pipeline không bị dừng khi gặp lỗi embedding. Công việc của tôi là nền tảng để các thành viên khác tiếp tục phát triển retrieval và evaluation, đảm bảo dữ liệu đã được chuẩn hóa, chia chunk hợp lý và lưu trữ đúng chuẩn cho các bước tiếp theo.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, tôi hiểu rõ hơn về cơ chế chunking và vai trò của overlap khi chia nhỏ tài liệu. Việc chia theo paragraph giúp giữ nguyên ngữ cảnh, còn overlap đảm bảo thông tin không bị mất ở ranh giới các đoạn. Tôi cũng hiểu sâu hơn về embedding: mỗi đoạn văn bản được chuyển thành vector số, cho phép tìm kiếm ngữ nghĩa thay vì chỉ dựa vào keyword. Việc lưu embedding vào vector database như ChromaDB giúp retrieval hiệu quả hơn, đặc biệt với các câu hỏi không khớp từ khóa trực tiếp mà cần hiểu ý nghĩa sâu xa.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Tôi gặp khó khăn khi debug hàm chunking, nhất là xử lý các trường hợp đoạn văn quá dài hoặc quá ngắn, và đảm bảo overlap hoạt động đúng như mong muốn. Một điều khiến tôi ngạc nhiên là việc thay đổi nhỏ trong cách chuẩn hóa văn bản (như loại bỏ ký tự thừa, chuẩn hóa dấu câu) lại ảnh hưởng rõ rệt đến chất lượng chunking và kết quả truy vấn. Ban đầu tôi nghĩ chỉ cần chia đoạn hợp lý là đủ, nhưng thực tế cho thấy nếu không chuẩn hóa tốt, embedding sẽ bị nhiễu và retrieval trả về kết quả kém chính xác. Điều này giúp tôi nhận ra tầm quan trọng của bước tiền xử lý dữ liệu trong toàn bộ pipeline RAG.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** Approval Matrix để cấp quyền hệ thống là tài liệu nào?

**Phân tích:**
- Baseline có thể trả lời sai hoặc không đủ chính xác nếu chỉ dựa vào keyword match, vì tên tài liệu đã đổi (từ "Approval Matrix" sang "Access Control SOP").
- Lỗi nằm ở retrieval: hệ thống cần khả năng nhận diện alias/tên cũ của tài liệu, không chỉ dựa vào tên file hiện tại.
- Nếu dùng hybrid retrieval (kết hợp semantic + keyword), khả năng trả lời đúng sẽ cao hơn vì embedding có thể nhận diện ngữ nghĩa tương đồng.
- Variant có cải thiện nếu bổ sung alias vào metadata hoặc tăng cường semantic search. Điều này cho thấy việc enrich metadata và cải thiện retrieval logic là rất quan trọng để hệ thống trả lời chính xác các câu hỏi dạng này.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Tôi sẽ thử bổ sung alias/tên cũ vào metadata khi indexing để retrieval nhận diện tốt hơn các câu hỏi dùng tên cũ hoặc từ khóa không khớp hoàn toàn. Ngoài ra, tôi muốn thử thêm bước normalization mạnh hơn cho text (loại bỏ ký tự thừa, chuẩn hóa dấu câu) để tăng chất lượng embedding và retrieval, giúp hệ thống trả lời chính xác hơn với các câu hỏi phức tạp hoặc diễn đạt khác biệt.

---
