# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Lương Anh Tuấn - 2A202600113

**Vai trò trong nhóm:** Retrieval & Synthesis Worker Owner

**Ngày nộp:** 14/04/2026

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

**Module/file tôi chịu trách nhiệm:**
- `workers/retrieval.py`
- `workers/synthesis.py`

**Functions tôi implement / cải tiến chính:**
- Trong `retrieval.py`: `_get_collection()`, `_build_index()`, `build_index()`, `search()`, `retrieve_dense()`, `run()` — dùng ChromaDB + OpenAI embedding để index và truy vấn chunks.
- Trong `synthesis.py`: `_call_llm()`, `_safe_rule_based_answer()`, `_extract_sources()`, `_build_context()`, `_estimate_confidence()`, `synthesize()`, `run()` — tổng hợp câu trả lời, bắt buộc citation, và fallback rule-based khi LLM không khả dụng.

**Vai trò trong dòng chảy hệ thống:**
Retrieval cung cấp evidence chunks cho pipeline; policy_tool chạy phân tích chính sách; synthesis tổng hợp câu trả lời dựa trên chunks và `policy_result`. Tôi đảm bảo retrieval trả về chunks chất lượng (index-viết/embedding-consistent) và synthesis chỉ trả lời khi có bằng chứng rõ ràng hoặc phải abstain.

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Kết quả retrieval của tôi là đầu vào trực tiếp cho synthesis và cũng là phần mà các thành viên làm supervisor/evaluator dựa vào để kiểm tra pipeline có route đúng và có grounded hay không. Khi Huy hoặc người phụ trách graph route sang `retrieval_worker`, state phải truyền đúng `task` và `retrieved_chunks` để synthesis có context. Khi Sơn hoặc các thành viên làm policy tool bổ sung `policy_result`, tôi cần dữ liệu đó để synthesis cite đúng nguồn và xử lý các câu hỏi liên quan đến policy hoặc access control. Ngược lại, trace và scorecard từ Đạt/Dũng giúp tôi biết retrieval đang thiếu chunk nào, câu nào cần index tốt hơn, và test case nào phải bổ sung.

**Bằng chứng:**
- Các file có test độc lập (`if __name__ == "__main__"`) và log prints (`[RETRIEVAL]`, `[SYNTHESIS]`) để kiểm chứng hành vi khi chạy standalone.
- Commit `c3f8c54ac285b157117dda62b0db505714222e8c` - hoàn thiện `retrieval.py` với ChromaDB và embedding.
- Commit `08e0e9e65b3008409b50bc832f0eb9c0e25bca27` - hoàn thiện `synthesis.py` với LLM call, rule-based fallback, và confidence estimation.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Tôi chọn thiết kế retrieval theo hướng worker stateless nhưng vẫn dùng ChromaDB persistent collection làm lớp lưu trữ trung tâm, thay vì giữ vector trong bộ nhớ tạm hoặc trả về dữ liệu mock.

**Lý do:**
Tôi gắn embedding function trực tiếp vào collection và cho `search()` truy vấn bằng `query_texts` để giảm nguy cơ lệch giữa bước index và bước query, đồng thời đơn giản hóa code gọi bên ngoài. Khi collection rỗng, worker tự build index từ toàn bộ file `.txt` trong `data/docs/`, nên pipeline vẫn chạy được ngay cả khi người dùng chưa chuẩn bị dữ liệu thủ công. Tôi cũng chuẩn hoá output của retrieval theo dạng `text/source/score/metadata`, sắp xếp theo score giảm dần và dedupe source trước khi ghi vào state, để synthesis nhận context ổn định hơn.

**Trade-off đã chấp nhận:**
Tôi chấp nhận việc worker phụ thuộc vào ChromaDB persistent storage và embedding API, đổi lại luồng retrieval nhất quán hơn, dễ debug hơn, và ít phải xử lý dữ liệu mock trong pipeline. Thiết kế này cũng làm giảm số nhánh xử lý đặc biệt ở tầng graph, vì retrieval có thể tự khởi tạo index khi collection trống.

**Bằng chứng từ trace/code:**

```python
if col.count() == 0:
	print("[RETRIEVAL] Building ChromaDB index from docs...")
	_build_index(col)

results = col.query(
	query_texts=[query],
	n_results=n,
	include=["documents", "metadatas", "distances"],
)

chunks.sort(key=lambda x: x["score"], reverse=True)
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** Retrieval đôi khi trả về quá ít hoặc không có chunks khi collection ChromaDB chưa được index đầy đủ, khiến synthesis thiếu evidence để tổng hợp câu trả lời.

**Symptom:** Một số run trước đây trả về `Retrieved: 0 chunks`; khi đó synthesis thường phải abstain hoặc chỉ trả lời rất chung chung vì không có tài liệu đủ mạnh để cite.

**Root cause:** Index chưa được build tự động khi collection trống, nên truy vấn đi vào một collection rỗng và không có tài liệu để match. Điều này làm pipeline bị “đứt” ngay ở bước đầu vào của synthesis.

**Cách sửa:**
- Trong `retrieval.py` tôi đảm bảo `_get_collection()` tự gọi `_build_index()` khi `col.count() == 0`.
- Trong `synthesis.py` tôi thêm fallback rule-based `_safe_rule_based_answer()` và `ABSTAIN_TEXT` để tránh hallucination khi không có chunks.
- Tôi cũng thêm `_estimate_confidence()` để synthesis có thể hạ mức tin cậy khi evidence yếu, thay vì trả lời chắc chắn một cách sai lệch.

**Bằng chứng trước/sau:**

```text
Trước: Retrieved: 0 chunks
Sau: [RETRIEVAL] Building ChromaDB index from docs...
Sau: [RETRIEVAL] Indexed N chunks from data/docs/
Sau: Retrieved: N chunks
```

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**
Tôi làm tốt nhất ở phần biến retrieval thành một worker có thể chạy độc lập và cho ra output ổn định. Việc chuẩn hoá `retrieved_chunks`, `retrieved_sources` và worker IO log giúp các bước sau như synthesis và grading trace dễ kiểm tra, dễ debug hơn.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Điểm tôi còn yếu là chưa tối ưu triệt để chất lượng embedding/index nên với một số câu hỏi multi-hop hoặc câu hỏi quá ngắn, retrieval vẫn có thể trả về ít tín hiệu hơn mong đợi. Tôi cũng cần cải thiện thêm coverage test cho `search()` và fallback khi ChromaDB không có dữ liệu.

**Nhóm phụ thuộc vào tôi ở đâu?**
Nhóm phụ thuộc vào tôi ở lớp evidence retrieval: nếu `retrieval.py` chưa xong hoặc trả output không đúng format, `synthesis_worker` sẽ thiếu context để tổng hợp câu trả lời, còn evaluator sẽ khó chấm được độ grounded của pipeline.

**Phần tôi phụ thuộc vào thành viên khác:**
Tôi cần Huy hoàn thiện routing/graph để biết khi nào retrieval được gọi và state được truyền ra sao. Tôi cũng phụ thuộc vào Sơn ở phần MCP tools và policy tool để có thêm bằng chứng chính sách khi query không đủ từ ChromaDB, và phụ thuộc vào Đạt/Dũng ở evaluator để biết retrieval hiện tại đang thiếu những case nào cần bổ sung.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Nếu có thêm 2 giờ, tôi sẽ thêm test unit cho `search()` bằng mock Chroma response để kiểm tra trường hợp collection rỗng và trường hợp top_k lớn hơn số chunk có thật. Tôi chọn cải tiến này vì trace hiện tại cho thấy retrieval là điểm đầu vào trực tiếp cho synthesis; nếu retrieval lệch hoặc rỗng, toàn bộ pipeline phía sau sẽ bị ảnh hưởng ngay.

---

**Files tham khảo:** `workers/retrieval.py`, `workers/synthesis.py`
