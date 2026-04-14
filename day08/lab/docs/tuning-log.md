# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 2026-04-13  
**Config:**
```
retrieval_mode = "dense"
chunk_size = 400 tokens
overlap = 80 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = gpt-4o-mini
```

**Scorecard Baseline:**

| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.20/5 |
| Relevance | 4.60/5 |
| Context Recall | 5.00/5 |
| Completeness | 4.00/5 |

**Câu hỏi yếu nhất (điểm thấp):**
> gq07 (1/1/2), gq05 (faithfulness 1/5), và nhóm câu completeness 4/5 (gq01/gq02/gq08/gq09/gq10).

**Giả thuyết nguyên nhân (Error Tree):**
- 2 mục Generation (Prompt không đủ grounding, Context quá dài/lost in the middle), không tick các mục retrieval/indexing vì recall đang 5.0.

---

## Variant 1 (Sprint 3)

**Ngày:** 2026-04-13  
**Biến thay đổi:** `retrieval_mode`: `"dense"` → `"hybrid"` (Dense + BM25 + RRF)  
**Lý do chọn biến này:**
> Chọn **hybrid retrieval** vì corpus có hai kiểu tín hiệu khác nhau:
> 1) câu tự nhiên dài trong policy/SOP (dense làm tốt), và  
> 2) từ khóa đặc thù như mã lỗi, SLA label, tên quy trình (BM25 làm tốt hơn).
>
> Baseline dense có rủi ro bỏ sót exact-match query (ví dụ kiểu `ERR-403-AUTH`, `P1`, `Level 3`) khi embedding ưu tiên ngữ nghĩa tổng quát.  
> Hybrid dùng **Reciprocal Rank Fusion (RRF)** để hợp nhất ưu điểm của dense và sparse, giúp tăng **context recall** mà vẫn giữ grounded generation.
>
> Nhóm chỉ đổi **1 biến retrieval_mode** để tuân thủ A/B Rule; các tham số khác giữ nguyên để so sánh công bằng.

**Config thay đổi:**
```
retrieval_mode = "hybrid"   
top_k_search = 10
top_k_select = 3
use_rerank = False
# Giữ nguyên các biến còn lại so với baseline để đo đúng tác động của retrieval_mode
```

**Scorecard Variant 1:**

| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.20/5 | 4.60/5 | +0.40 |
| Answer Relevance | 4.60/5 | 4.60/5 | N/A |
| Context Recall | 5/5 | 5/5 | N/A |
| Completeness | 4/5 | 3.90/5 | -0.1 |

**Nhận xét:**
> cải thiện gq05 (faithfulness 1→4), không cải thiện gq07, và completeness trung bình giảm 4.20→3.90.

**Kết luận:**
> hybrid không tốt hơn toàn diện; trade-off là faithfulness tăng (4.20→4.50) nhưng completeness giảm (-0.30).


---

## Tóm tắt học được

> TODO (Sprint 4): Điền sau khi hoàn thành evaluation.

1. **Lỗi phổ biến nhất trong pipeline này là gì?**  
   > Lỗi phổ biến nhất là xử lý câu hỏi thiếu/ngầm định context chưa ổn định: model thường trả "Không đủ dữ liệu" quá ngắn nên bị trừ relevance/completeness ở các câu cần vừa abstain vừa nêu hướng xử lý.

2. **Biến nào có tác động lớn nhất tới chất lượng?**  
   > Biến có tác động lớn nhất là `retrieval_mode` (dense -> hybrid). Trong run gần nhất, hybrid cải thiện faithfulness (4.20 -> 4.50) và giữ context recall cao, nhưng completeness giảm nhẹ (4.20 -> 3.90), cho thấy retrieval ảnh hưởng trực tiếp chất lượng context đầu vào.

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**  
   > Nhóm sẽ thử hybrid có điều kiện theo loại query (keyword/error code thì hybrid, policy thường thì dense), đồng thời tinh chỉnh prompt abstain để khi không đủ dữ liệu vẫn trả lời đầy đủ và rõ hướng xử lý.
