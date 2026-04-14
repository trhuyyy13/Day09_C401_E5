# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Vũ Hải Đăng - 2A202600339
**Vai trò trong nhóm:** Coding- Code Optimization & Review
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong Sprint 1 của Lab Day 08, tôi đảm nhận vai trò tối ưu hóa toàn bộ quá trình Embedding & Indexing cho hệ thống RAG, đồng thời rà soát và nâng cấp module tiền xử lý (preprocess) và chia nhỏ tài liệu (chunking) mà Tuấn (thành viên trong nhóm) đã làm trước đó. 

Cụ thể, đối với mã nguồn gốc của Tuấn:
- **Tiền xử lý & Chunking:** Code cũ gặp lỗi cắt câu không tự nhiên do chỉ dựa vào số lượng ký tự cứng. Tôi đã nâng cấp logic bằng cách ưu tiên cắt theo cấu trúc ngữ nghĩa (đoạn văn, tách thêm thành từng vế có vạch ngăn câu `.`) trước khi áp dụng giới hạn kích thước, giúp tránh trường hợp bị đứt câu hoặc mất ý.
- **Embedding & Indexing (tối ưu pipeline):**  
  + `_batched()` & `get_embeddings(texts)`: Gom các chunk thành batch lớn trước khi gọi API, giúp giảm số lần request, tăng tốc độ và hạn chế bị rate limit.  
  + `build_index()`: Quản lý việc đưa dữ liệu vào DB. Trước khi upsert, hàm sẽ xoá các bản ghi cũ theo `source` để tránh trùng lặp. Đồng thời có cơ chế fallback: nếu batch bị lỗi giữa chừng, hệ thống sẽ chuyển sang xử lý từng chunk riêng lẻ để không bị mất dữ liệu.

- **Diagnostic & Inspect (kiểm tra chất lượng dữ liệu):**  
  + `list_chunks()`: Lấy nhanh một số chunk mẫu từ DB để kiểm tra xem việc cắt đoạn có hợp lý không và metadata có đúng không.  
  + `inspect_metadata_coverage()`: Phân tích phân bố metadata (như `department`) và phát hiện các trường bị thiếu (ví dụ `effective_date`), giúp team kịp thời điều chỉnh lại bước preprocess.

=> Nhìn chung, các cải tiến này giúp index sạch hơn, ổn định hơn và hỗ trợ tốt cho bước retrieval phía sau.
---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, mình hiểu rõ hơn về tầm quan trọng của **chunking strategy** trong hệ thống RAG. Trước đây mình nghĩ chỉ cần cắt văn bản theo số lượng token là đủ để đưa vào embedding. Nhưng khi thử nghiệm, cách cắt cứng này dễ làm mất ngữ cảnh, khiến thông tin bị rời rạc và khó truy xuất chính xác.

Mình nhận ra rằng chunking theo **ngữ nghĩa** (theo đoạn, câu, hoặc cấu trúc nội dung) quan trọng hơn nhiều, vì nó giữ được trọn vẹn ý nghĩa của thông tin. Điều này ảnh hưởng trực tiếp đến chất lượng retrieval.

Ngoài ra, mình cũng hiểu rõ sự khác biệt giữa việc tìm đúng tài liệu và tìm đúng đoạn để trả lời. Điều này giúp mình nhìn rõ hơn cách tối ưu retrieval trong thực tế.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)  

Ở phần evaluation, điều làm mình bất ngờ là hybrid retrieval không phải lúc nào cũng tốt hơn dense. Với những câu hỏi rõ ràng, dense đã đủ hiệu quả. Khó nhất là việc cân bằng giữa dense và sparse sao cho không bị kéo theo các kết quả chỉ trùng keyword nhưng không thực sự liên quan.

Một khó khăn khác phát sinh từ chính bước chunking. Khi chunk quá dài, embedding có xu hướng bị “làm phẳng” (semantic dilution), khiến các đoạn chứa nhiều thông tin khác nhau bị biểu diễn thành vector trung bình, làm giảm khả năng phân biệt.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** Approval Matrix để cấp quyền hệ thống là tài liệu nào?

**Phân tích:**  
Đây là một trường hợp mà baseline trả lời sai nếu chỉ dựa vào keyword match. Nguyên nhân là tên tài liệu đã thay đổi, từ “Approval Matrix” sang “Access Control SOP”, nên truy vấn không còn khớp trực tiếp với tên hiện tại.  

Vấn đề cốt lõi nằm ở bước retrieval: hệ thống cần hiểu được các alias hoặc tên cũ của tài liệu, thay vì chỉ dựa vào tên file hoặc keyword hiện có. Nếu chỉ dùng keyword search thuần túy, khả năng bỏ sót là khá cao.  

Khi áp dụng Hybrid Retrieval (kết hợp semantic và keyword), kết quả được cải thiện vì embedding có thể nắm bắt sự tương đồng về ngữ nghĩa giữa các cách gọi khác nhau. Ngoài ra, việc bổ sung alias vào metadata hoặc tăng cường semantic search cũng giúp hệ thống nhận diện đúng tài liệu hơn.  

Điều này cho thấy việc làm giàu metadata và tối ưu retrieval logic đóng vai trò quan trọng trong việc nâng cao độ chính xác, đặc biệt với các truy vấn sử dụng tên gọi thay thế.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm một chút thời gian tối ưu Retrieval, tôi sẽ thử nghiệm **Hierarchical Chunking (Small-to-Big Retrieval)**. Dựa trên kết quả eval hiện tại đang cho thấy đôi lúc kích thước văn bản chunk hơi lớn khiến Embedding bị san phẳng vector (diluted), làm công cụ Vector Search bị giảm tỉ lệ Top 1.
Giải pháp của tôi sẽ là sinh ra embedding trên các đoạn văn rất ngắn (Child) chạy Batch, còn khi truy vấn sẽ lấy cả nội dung bối cảnh nguyên Section lớn (Parent) đưa vào LLM để đảm bảo đáp án chính xác nhất.

---

