
# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline
**Họ và tên:** Trần Quang Huy 
Team chúng em chia thành 3 cặp (Tuấn+ Đăng, Huy + Sơn, Đạt + Dũng, Huy + Sơn)
**Vai trò trong nhóm:** Tech Lead / Retrieval Owner / Eval Owner / Documentation Owner  
**Ngày nộp:** 13/04/2026

---

## 1. Tôi đã làm gì trong lab này?
- Cùng Sơn tham gia chủ yếu ở **Sprint 2** và **Sprint 4**. Trong đó, em là người implement chính Sprint 2.
- Đưa ra ý tưởng và đánh giá trong sprint 4.
- Sau khi hoàn thiện từng phần, cả nhóm cùng ngồi lại để thảo luận, so sánh kết quả giữa các biến thể và đánh giá hiệu quả toàn bộ pipeline.

Cụ thể:

- Implement `retrieve_dense()` để truy vấn ChromaDB bằng embedding similarity.
- Xây dựng `call_llm()` để gọi OpenAI API sinh câu trả lời.
- Thiết kế `build_grounded_prompt()` với các nguyên tắc giúp câu trả lời bám sát ngữ cảnh:
  - chỉ dùng evidence trong context,
  - không đủ dữ liệu thì phải abstain,
  - bắt buộc citation theo dạng `[1], [2]`,
  - trả lời ổn định và nhất quán.
- Cùng nhóm làm việc với các hướng retrieval khác nhau như dense, sparse* và hybrid, từ đó hiểu rõ hơn cách phối hợp nhiều chiến lược truy xuất trong một pipeline RAG.


---

## 2. Điều tôi hiểu rõ hơn sau lab này

- Hiểu rõ hơn về luồng cơ bản của một hệ thống RAG, từ bước truy vấn, lấy context, ghép prompt cho tới khi mô hình sinh ra câu trả lời. Trước đây, nghĩ RAG chủ yếu là “lấy tài liệu rồi đưa vào prompt”, nhưng khi làm thực tế mới thấy để hệ thống trả lời tốt thì từng bước trong pipeline đều cần được thiết kế cẩn thận.
- Đặc biệt là sự khác nhau giữa dense retrieval, sparse retrieval và hybrid retrieval.
- Hiểu sâu hơn là việc **tối ưu tham số** trong RAG không hề đơn giản. Các tham số như:
    - `TOP_K_SEARCH`,
    - ngưỡng relevance,
    - số lượng chunk đưa vào context,
    - cách kết hợp dense/sparse,
    - cách normalize score,
đều ảnh hưởng trực tiếp đến chất lượng đầu ra. Chỉ cần chỉnh chưa hợp lý thì hệ thống có thể hoặc thiếu thông tin, hoặc lấy quá nhiều context nhiễu.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

- Nhiều chi tiết nhỏ nhưng ảnh hưởng rất lớn đến toàn bộ pipeline RAG.
- Từng nhầm giữa cosine distance và similarity trong ChromaDB, làm retrieval sai và model dễ abstain dù có đáp án trong context.
- Khó khăn ở phần chuẩn hóa score giữa dense, sparse và hybrid retrieval vì mỗi cách có thang điểm khác nhau.
- Nhận ra chất lượng hệ thống không chỉ phụ thuộc vào model mà còn ở chunking, retrieval strategy, prompt design và evaluation.
---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** “SLA xử lý ticket P1 là bao lâu?”

Khi thử với **Baseline (Dense Retrieval)**, hệ thống có thể trả lời đúng ý chính là **SLA P1 là 4 giờ** và có citation đi kèm. Điều đó cho thấy dense retrieval đã lấy được chunk đúng. Tuy nhiên, câu trả lời vẫn còn thiếu một số chi tiết liên quan như quy định cập nhật trạng thái định kỳ hoặc escalation nếu chưa xử lý xong.

Khi thảo luận và so sánh với các biến thể tốt hơn trong nhóm, tôi nhận ra rằng việc kết hợp thêm các tín hiệu retrieval hoặc tối ưu thứ tự context có thể giúp model trả lời đầy đủ hơn. Đây cũng là lý do nhóm tiếp tục phân tích sâu ở phần evaluation để xem biến thể nào cho kết quả cân bằng nhất giữa độ đúng, độ đủ và độ liên quan.


---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

- Thử nghiệm sâu hơn với **hybrid retrieval**, đặc biệt ở phần cân bằng giữa dense và sparse để tăng recall cho những câu hỏi vừa có tính ngữ nghĩa, vừa chứa từ khóa quan trọng.


---

*Báo cáo hoàn thành lúc 13/04/2026*  

