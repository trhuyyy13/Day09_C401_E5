
# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline


# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline
**Họ và tên:** Trần Ngọc Sơn

Team chúng em chia thành 3 cặp (Tuấn+ Đăng, Huy + Sơn, Đạt + Dũng)

**Ngày nộp:** 13/04/2026

---

## 1. Đã làm gì trong lab này?

- Tham gia chủ yếu ở **Sprint 2** và **Sprint 4** cùng Huy. Trong đó, em implement chủ yếu ở Sprint 4 - Evaluation.
- Cụ thể: công việc tập trung vào việc xây dựng hướng đánh giá cho hệ thống RAG, gồm thiết kế các tiêu chí faithfulness, relevance, context recall và completeness, sau đó dùng các tiêu chí này để so sánh nhiều biến thể khác nhau như baseline, dense, sparse, hybrid và các cấu hình retrieval khác nhau.
- Theo dõi output từ pipeline retrieval/generation để kiểm tra context được lấy ra có phù hợp hay không, câu trả lời có bám sát tài liệu hay không, rồi cùng nhóm thảo luận và đánh giá kết quả chung của hệ thống.

---

## 2. Điều hiểu rõ hơn sau lab này

- Hiểu rõ hơn luồng cơ bản của RAG, từ retrieval, lấy context, build prompt đến generation và evaluation; đồng thời thấy rằng chất lượng đầu ra phụ thuộc vào toàn bộ pipeline chứ không chỉ một bước riêng lẻ.
- Phân biệt rõ hơn giữa dense retrieval, sparse retrieval và hybrid retrieval
- Nhận ra việc đánh giá hệ thống RAG không thể chỉ dựa vào đúng hay sai, mà cần thêm các tiêu chí như mức độ bám sát context, độ đầy đủ thông tin và citation để so sánh chính xác hơn giữa các variant.

---

## 3. Điều ngạc nhiên hoặc gặp khó khăn
- Khó khăn lớn nhất là đánh giá output nhất quán, vì nhiều câu trả lời đúng ý chính nhưng vẫn chưa đủ ý.
- Evaluation không chỉ để chấm điểm mà còn giúp phát hiện retrieval thiếu gì, context nhiễu ở đâu và phần nào cần tối ưu thêm.
- Qua đó thấy rõ chất lượng RAG phụ thuộc không chỉ vào model mà còn vào retrieval, chunking, prompt và evaluation.

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** “SLA xử lý ticket P1 là bao lâu?”

Đây là một ví dụ cho thấy rõ sự khác nhau giữa một câu trả lời **đúng** và một câu trả lời **đầy đủ**. Ở một số cấu hình cơ bản, hệ thống có thể trả lời đúng ý chính là **SLA P1 là 4 giờ**, nhưng vẫn thiếu các thông tin liên quan như tần suất cập nhật trạng thái hoặc điều kiện escalation.

Từ góc nhìn evaluation, trường hợp này cho thấy một câu trả lời tốt không chỉ cần đúng fact chính mà còn cần bao quát các điều kiện quan trọng trong policy. Việc phân tích theo hướng này giúp đánh giá hệ thống sát với nhu cầu thực tế hơn, thay vì chỉ kiểm tra xem mô hình có lấy đúng một chi tiết hay không.

---

## 5. Nếu có thêm thời gian, sẽ làm gì?

Nếu có thêm thời gian, sẽ tiếp tục hoàn thiện phần evaluation theo hướng chặt chẽ và nhất quán hơn. Trước hết là chuẩn hóa rubric chấm điểm để việc đánh giá giữa các câu hỏi ổn định hơn, đặc biệt với các trường hợp câu trả lời đúng nhưng chưa đủ.
---
