# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** C401_E5
**Thành viên:**
| Tên | Email |
|-----|-------|
|Vũ Hải Đăng | dangvu.cspk53@gmail.com |
|Lương Anh Tuấn | latuan1st@gmail.com |
|Trần Quang Huy | huytran.soict.hust@gmail.com |
|Lê Hoàng Đạt |  eltad2003@gmail.com |
|Lương Tiến Dũng | dungltcn272@gmail.com |
|Trần Ngọc Sơn |  trngson.work@gmail.com |

**Ngày nộp:** 2026-04-13  
**Repo:** https://github.com/trhuyyy13/Day08_C401_E5.git
**Độ dài khuyến nghị:** 600–900 từ



## 1. Pipeline nhóm đã xây dựng (150–200 từ)

> Mô tả ngắn gọn pipeline của nhóm:
> - Chunking strategy: size, overlap, phương pháp tách (by paragraph, by section, v.v.)
> - Embedding model đã dùng
> - Retrieval mode: dense / hybrid / rerank (Sprint 3 variant)

**Chunking decision:**
> VD: "Nhóm dùng chunk_size=500, overlap=50, tách theo section headers vì tài liệu có cấu trúc rõ ràng."

Nhóm dùng `chunk_size=400` tokens và `overlap=80` tokens theo cấu hình trong `index.py`. Về chiến lược, nhóm tách tài liệu theo heading (`=== ... ===`) trước, sau đó tách tiếp theo paragraph/câu nếu section dài. Cách làm này giúp giữ ngữ nghĩa theo điều khoản, giảm hiện tượng cắt ngang ý quan trọng. Trong bước preprocess, nhóm bóc tách metadata header (source, department, effective_date, access) rồi giữ metadata theo từng chunk để phục vụ truy xuất, citation và kiểm soát freshness.

**Embedding model:**

`text-embedding-3-small` (OpenAI), batch embedding theo `EMBEDDING_BATCH_SIZE=32`. Vector store dùng ChromaDB `PersistentClient`, metric cosine.

**Retrieval variant (Sprint 3):**
> Nêu rõ variant đã chọn (hybrid / rerank / query transform) và lý do ngắn gọn.

Nhóm chọn **hybrid retrieval** (dense + BM25, hợp nhất bằng weighted RRF). Lý do: bộ câu hỏi có cả truy vấn ngữ nghĩa và truy vấn thiên exact keyword/alias (ví dụ mã lỗi, tên chính sách). Hybrid giúp tăng recall cho case từ khóa mà vẫn giữ được sức mạnh ngữ nghĩa của dense.

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

> Chọn **1 quyết định thiết kế** mà nhóm thảo luận và đánh đổi nhiều nhất trong lab.
> Phải có: (a) vấn đề gặp phải, (b) các phương án cân nhắc, (c) lý do chọn.

**Quyết định:** Chọn hybrid retrieval làm variant Sprint 3 thay vì giữ dense-only

**Bối cảnh vấn đề:**

Sau Sprint 2, baseline dense chạy ổn và đạt điểm trung bình tốt, nhưng nhóm nhận thấy một số câu cần thông tin rất cụ thể theo keyword/thuật ngữ nghiệp vụ. Nếu chỉ dựa embedding similarity, top chunks có lúc đúng chủ đề nhưng chưa chắc chứa đúng mảnh evidence chi tiết để trả lời đầy đủ. Nhóm cần một thay đổi đủ nhỏ để tuân thủ A/B Rule (chỉ đổi 1 biến), nhưng đủ tác động lên context recall ở các câu có tín hiệu từ khóa mạnh.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Giữ dense-only | Đơn giản, nhanh, đã ổn định từ Sprint 2 | Dễ hụt exact keyword/alias; ít cơ chế cứu recall |
| Hybrid (dense + BM25 + RRF) | Kết hợp semantic + lexical, cải thiện recall cho query đặc thù | Tăng độ phức tạp, cần tuning fusion weight |

**Phương án đã chọn và lý do:**

Nhóm chọn hybrid và giữ nguyên các tham số còn lại (`top_k_search=10`, `top_k_select=3`, `use_rerank=False`) để đảm bảo so sánh công bằng. Thiết kế fusion bằng RRF giúp tránh phụ thuộc tuyệt đối vào thang điểm giữa dense và sparse, chỉ cần thứ hạng tương đối. Cách này phù hợp với phạm vi lab: dễ triển khai, giải thích được, và có thể mở rộng thêm rerank ở Sprint sau nếu cần.

**Bằng chứng từ scorecard/tuning-log:**

Trong scorecard, Faithfulness tăng từ **4.20 → 4.60** khi chuyển từ baseline dense sang hybrid, Relevance giữ **4.60**, Context Recall giữ **5.00**; đây là dấu hiệu variant không làm giảm khả năng retrieve nguồn kỳ vọng. Nội dung lý do chọn hybrid cũng được ghi trong `docs/tuning-log.md` phần Variant 1.

---

## 3. Kết quả grading questions (100–150 từ)

> Sau khi chạy pipeline với grading_questions.json (public lúc 17:00):
> - Câu nào pipeline xử lý tốt nhất? Tại sao?
> - Câu nào pipeline fail? Root cause ở đâu (indexing / retrieval / generation)?
> - Câu gq07 (abstain) — pipeline xử lý thế nào?

**Ước tính điểm raw:** 78 / 98

**Câu tốt nhất:** ID: gq06 — Lý do: câu multi-hop (SLA + Access Control) vẫn trả đúng quy trình cấp quyền tạm thời và mốc 24 giờ, citation rõ.

**Câu fail:** ID: gq07 — Root cause: câu hỏi yêu cầu diễn giải “không có điều khoản penalty” nhưng pipeline chỉ abstain ngắn “Không đủ dữ liệu”, chưa giải thích rõ phạm vi tài liệu đã kiểm tra.

**Câu gq07 (abstain):** Pipeline đã abstain đúng hướng (không bịa số tiền phạt), nhưng chất lượng answer còn tối giản. Bước cải tiến là thay prompt abstain sang dạng: “Không đủ dữ liệu; tài liệu hiện tại không có điều khoản penalty SLA P1”.

---

## 4. A/B Comparison — Baseline vs Variant (150–200 từ)

> Dựa vào `docs/tuning-log.md`. Tóm tắt kết quả A/B thực tế của nhóm.

**Biến đã thay đổi (chỉ 1 biến):** `retrieval_mode`: `dense` → `hybrid`

| Metric | Baseline | Variant | Delta |
|--------|---------|---------|-------|
| Faithfulness | 4.20/5 | 4.60/5 | +0.40 |
| Relevance | 4.60/5 | 4.60/5 | +0.00 |
| Context Recall | 5.00/5 | 5.00/5 | +0.00 |
| Completeness | 4.20/5 | 3.90/5 | -0.30 |

**Kết luận:**
> Variant tốt hơn hay kém hơn? Ở điểm nào?

Variant hybrid tốt hơn baseline về độ bám ngữ cảnh (faithfulness) và vẫn giữ được recall cao. Tuy nhiên completeness giảm nhẹ do một số câu trả lời hybrid ngắn hơn kỳ vọng (đặc biệt ở câu cần nhiều chi tiết điều kiện). Kết luận của nhóm: **giữ hybrid làm retrieval mặc định** vì lợi ích chính nằm ở độ tin cậy và khả năng không hallucinate, sau đó bù completeness bằng tinh chỉnh prompt hoặc thêm rerank ở vòng tiếp theo.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

> Đánh giá trung thực về quá trình làm việc nhóm.

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Đăng | Preprocess metadata, chunking theo heading/paragraph, overlap logic | Sprint 1 |
| Tuấn | Build index pipeline, batch embedding/upsert ChromaDB, metadata inspection | Sprint 1 |
| Huy | Grounded prompt, call LLM, citation guard, abstain normalization | Sprint 2 |
| Đạt | BM25 sparse retrieval, tokenization, candidate filtering | Sprint 3 |
| Dũng | Hybrid fusion (dense + sparse), RRF weighting, strategy comparison output | Sprint 3 |
| Sơn | Chạy eval/scorecard, tổng hợp A/B, viết tuning log và architecture/report | Sprint 4 |

**Điều nhóm làm tốt:**

Phân công theo sprint rõ ràng, handoff mạch lạc giữa indexing → retrieval → eval. Nhóm bám A/B Rule, không thay đổi nhiều biến cùng lúc nên đọc kết quả dễ. Khi gặp câu thiếu dữ liệu, hệ thống ưu tiên abstain nên giảm rủi ro hallucination.

**Điều nhóm làm chưa tốt:**

Completeness của variant chưa ổn định ở vài câu phức hợp; một số câu trả lời còn thiếu chi tiết dù context đã có. Việc chuẩn hóa cách ghi evidence trong answer (nêu đủ điều kiện, timeline, approval chain) cần chặt hơn để cải thiện điểm hoàn chỉnh.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

> 1–2 cải tiến cụ thể với lý do có bằng chứng từ scorecard.

1) Thêm **rerank nhẹ** sau hybrid (top-10 → rerank → top-3) để ưu tiên chunk chứa điều kiện định lượng/approval chính xác, kỳ vọng tăng Completeness.  
2) Tinh chỉnh prompt abstain và prompt tổng hợp đa-điều-kiện để câu trả lời vừa an toàn vừa đầy đủ hơn (đặc biệt cho các câu kiểu gq05/gq07).

---
