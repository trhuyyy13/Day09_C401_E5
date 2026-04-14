# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Lê Hoàng Đạt
**Vai trò trong nhóm:** Tech Lead / Retrieval Owner / Eval Owner / Documentation Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint 3: Implement retrieve_dense() — query ChromaDB
> - implement retrieve_hybrid()
> - tôi đã implement phần retrieve_hybrid() để kết hợp kết quả từ dense retrieval (ChromaDB) và sparse retrieval (BM25) bằng phương pháp Reciprocal Rank Fusion (RRF). Sau đó điều chỉnh trọng số giữa dense và sparse để tối ưu hiệu suất. 


_________________


## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

>**hybrid retrieval**: 
>- tôi hiểu rõ hơn về cách kết hợp dense và sparse retrieval để cải thiện hiệu suất tổng thể của hệ thống RAG. 
>- Tôi đã học được cách sử dụng Reciprocal Rank Fusion (RRF) để kết hợp kết quả từ hai phương pháp này, cũng như cách điều chỉnh trọng số giữa chúng để đạt được kết quả tốt nhất.


_________________


## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> kết quả giữa baseline và hybrid retrieval không có sự cải thiện đáng kể như tôi mong đợi. Ban đầu, tôi nghĩ hybrid sẽ mang lại hiệu suất tốt hơn, nhưng thực tế cho thấy rằng việc điều chỉnh trọng số giữa hai phương pháp này là rất quan trọng. Tôi đã phải thử nhiều giá trị khác nhau cho dense_weight và sparse_weight để eval() ra kết quả tốt nhất

_________________


## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?

**Phân tích:**
- Baseline trả lời đúng vì nó có thể truy xuất thông tin chính xác từ tìm kiếm ngữ nghĩa
- Variant hybrid retrieval cũng không cải thiện đáng kể, có thể do trọng số giữa dense và sparse retrieval chưa được tối ưu, dẫn đến việc không lấy được thông tin chính xác từ cả hai phương pháp. Điều này cho thấy rằng việc điều chỉnh trọng số là rất quan trọng để cải thiện hiệu suất của hệ thống RAG.
---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> "Tôi sẽ thử điều chỉnh trọng số giữa dense và sparse retrieval vì kết quả eval cho thấy rằng hybrid retrieval không cải thiện đáng kể so với baseline, có thể do việc kết hợp chưa tối ưu."
_________________
