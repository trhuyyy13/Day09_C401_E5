# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Lê Hoàng Đạt  
**Vai trò trong nhóm:** Trace & Docs Owner (eval_trace + comparison Day 08 vs Day 09)  
**Ngày nộp:** 14/04/2026 
**Độ dài yêu cầu:** 500–800 từ

---

> **Lưu ý quan trọng:**
> - Viết ở ngôi **"tôi"**, gắn với chi tiết thật của phần bạn làm
> - Phải có **bằng chứng cụ thể**: tên file, đoạn code, kết quả trace, hoặc commit
> - Nội dung phân tích phải khác hoàn toàn với các thành viên trong nhóm
> - Deadline: Được commit **sau 18:00** (xem SCORING.md)
> - Lưu file với tên: `reports/individual/[ten_ban].md` (VD: `nguyen_van_a.md`)

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

> Mô tả cụ thể module, worker, contract, hoặc phần trace bạn trực tiếp làm.
> Không chỉ nói "tôi làm Sprint X" — nói rõ file nào, function nào, quyết định nào.

**Module/file tôi chịu trách nhiệm:**
- File chính: `day09/lab/eval_trace.py`, `day09/lab/docs/single_vs_multi_comparison.md`, `day09/lab/docs/routing_decisions.md`
- Functions tôi implement: `analyze_traces()`, `compare_single_vs_multi()` (đặc biệt phần `_extract_day08_metrics()`)

**Cách công việc của tôi kết nối với phần của thành viên khác:**

Tôi nhận output từ pipeline orchestration (`graph.py` + workers), sau đó chuẩn hóa thành trace metrics và tài liệu nộp. Phần của tôi nằm ở tầng “đánh giá và tổng hợp”: đọc tất cả trace trong `artifacts/traces`, tính routing distribution, confidence, latency, MCP usage, HITL rate; đồng thời kéo dữ liệu baseline từ Day 08 (`scorecard_baseline.json`, `scorecard_baseline.md`) để so sánh single-agent và multi-agent. Công việc này kết nối trực tiếp với teammate làm supervisor/worker vì nếu trace không đúng format thì `eval_trace.py` không phân tích được. Ngược lại, nếu tôi không hoàn thiện phần compare và docs, nhóm có code chạy nhưng thiếu bằng chứng định lượng để nộp phần Sprint 4.

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**

- Có thay đổi trực tiếp ở `compare_single_vs_multi()` trong `day09/lab/eval_trace.py` để thay TODO bằng dữ liệu thật từ Day 08.
- Có cập nhật 2 tài liệu bắt buộc theo trace thật: `day09/lab/docs/single_vs_multi_comparison.md` và `day09/lab/docs/routing_decisions.md`.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

> Chọn **1 quyết định** bạn trực tiếp đề xuất hoặc implement trong phần mình phụ trách.
> Giải thích:
> - Quyết định là gì?
> - Các lựa chọn thay thế là gì?
> - Tại sao bạn chọn cách này?
> - Bằng chứng từ code/trace cho thấy quyết định này có effect gì?

**Quyết định:** Tôi chọn “tự động đọc baseline Day 08 từ file results” thay vì hard-code số liệu trong `compare_single_vs_multi()`.

**Ví dụ:**
> "Tôi chọn dùng keyword-based routing trong supervisor_node thay vì gọi LLM để classify.
>  Lý do: keyword routing nhanh hơn (~5ms vs ~800ms) và đủ chính xác cho 5 categories.
>  Bằng chứng: trace gq01 route_reason='task contains P1 SLA keyword', latency=45ms."

**Lý do:**

Ban đầu file `eval_trace.py` chỉ có placeholder (`avg_confidence = 0.0`, `abstain_rate = "?"`, `multi_hop_accuracy = "?"`). Nếu điền tay trong docs thì nhanh nhưng rủi ro sai số và không tái lập được khi chạy lại. Tôi quyết định implement `_extract_day08_metrics()` để đọc trực tiếp `day08/lab/results/scorecard_baseline.json` và `scorecard_baseline.md`. Cách này cho phép nhóm chạy lại rồi có kết quả mới ngay, không phải sửa tay nhiều nơi. Ngoài ra, tôi xử lý luôn việc map metric giữa hai ngày: Day 08 có thang đánh giá theo scorecard, Day 09 có trace runtime metrics. Tôi tách rõ phần nào so sánh trực tiếp được (abstain rate, routing visibility) và phần nào phải ghi chú khác thang đo (confidence proxy vs confidence runtime), nhờ vậy phần report không bị “đẹp số” nhưng sai bản chất.

**Trade-off đã chấp nhận:**

Trade-off là code compare dài hơn và phụ thuộc format scorecard Day 08. Nếu tên cột hoặc markdown summary đổi, parser regex có thể phải cập nhật lại. Tôi chấp nhận điều này vì đổi lại nhóm có quy trình đánh giá ổn định, chạy lại được, và ít lỗi thủ công khi nộp.

**Bằng chứng từ trace/code:**

```python
# eval_trace.py (phần tôi implement)
def _extract_day08_metrics(results_dir: str) -> dict:
	baseline_json_path = os.path.join(results_dir, "scorecard_baseline.json")
	baseline_md_path = os.path.join(results_dir, "scorecard_baseline.md")
	...
	# abstain_rate từ answer
	abstain = sum(1 for item in data if "không đủ dữ liệu" in (item.get("answer", "").lower()))
	...
	# avg_confidence proxy từ Faithfulness trong markdown summary
	m = re.search(r"Faithfulness\s*\|\s*([0-9.]+)/5", md)
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

> Mô tả 1 bug thực tế bạn gặp và sửa được trong lab hôm nay.
> Phải có: mô tả lỗi, symptom, root cause, cách sửa, và bằng chứng trước/sau.

**Lỗi:** Báo cáo compare giữa Day 08 và Day 09 ban đầu không dùng dữ liệu thật, và có rủi ro kết luận sai vì metric placeholder.

**Symptom (pipeline làm gì sai?):**

Pipeline vẫn chạy, nhưng phần đánh giá trong `eval_trace.py` sinh kết quả “đẹp về format nhưng rỗng về nghĩa”: Day 08 bị ghi 0 hoặc `?`. Khi đẩy sang file docs, người đọc có thể tưởng nhóm chưa chạy hoặc chạy nhưng không có kết quả. Điều này làm mất điểm ở phần Sprint 4 vì rubric yêu cầu số liệu thực tế.

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**

Root cause nằm ở lớp evaluation/documentation, không nằm ở routing hay retrieval. Cụ thể, `compare_single_vs_multi()` chưa implement phần đọc dữ liệu Day 08, còn giữ TODO và baseline giả lập.

**Cách sửa:**

Tôi bổ sung hàm `_extract_day08_metrics()` để đọc scorecard Day 08 tự động, tính `abstain_rate`, `multi_hop_accuracy`, và kéo giá trị Faithfulness làm confidence proxy có ghi chú rõ. Sau đó tôi cập nhật hai file docs theo trace mới (18 trace) và ghi rõ nguồn số liệu. Tôi cũng sửa phần diễn giải để tránh so sánh nhầm giữa thang 1–5 (faithfulness proxy) và thang 0–1 (runtime confidence).

**Bằng chứng trước/sau:**
> Dán trace/log/output trước khi sửa và sau khi sửa.

Trước khi sửa: bảng compare có các giá trị `?` hoặc 0 mặc định cho Day 08 trong code TODO.  
Sau khi sửa: docs có số liệu cụ thể từ trace và baseline, ví dụ Day 09 dùng 18 traces với `avg_confidence = 0.631`, `avg_latency_ms = 7679`, `mcp_usage_rate = 9/18 (50.0%)`, `hitl_rate = 5/18 (27.8%)`.

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

> Trả lời trung thực — không phải để khen ngợi bản thân.

**Tôi làm tốt nhất ở điểm nào?**

Tôi làm tốt nhất ở việc biến trace rời rạc thành báo cáo có thể nộp: số liệu rõ, nguồn rõ, và có giải thích giới hạn metric. Tôi ưu tiên tính tái lập thay vì điền tay nên nhóm có thể chạy lại và cập nhật nhanh.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**

Tôi chưa làm phần evaluator tự chấm đúng/sai theo expected_answer cho Day 09, nên một số mục vẫn phải ghi N/A (đặc biệt multi-hop accuracy). Nếu có thêm thời gian tôi sẽ tự động hóa bước này để giảm phụ thuộc đánh giá thủ công.

**Nhóm phụ thuộc vào tôi ở đâu?** _(Phần nào của hệ thống bị block nếu tôi chưa xong?)_

Nhóm phụ thuộc vào tôi ở phần đóng gói kết quả Sprint 4. Nếu tôi chưa xong, code có thể chạy nhưng không có tài liệu định lượng để chứng minh chất lượng và so sánh Day 08 vs Day 09 theo rubric.

**Phần tôi phụ thuộc vào thành viên khác:** _(Tôi cần gì từ ai để tiếp tục được?)_

Tôi phụ thuộc vào teammate làm supervisor/worker để trace có đủ trường (`supervisor_route`, `route_reason`, `workers_called`, `mcp_tools_used`, `confidence`, `latency_ms`). Thiếu các trường này thì phần phân tích của tôi bị thiếu dữ liệu.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

> Nêu **đúng 1 cải tiến** với lý do có bằng chứng từ trace hoặc scorecard.
> Không phải "làm tốt hơn chung chung" — phải là:
> *"Tôi sẽ thử X vì trace của câu gq___ cho thấy Y."*

Tôi sẽ thêm một evaluator tự động trong `eval_trace.py` để tính “answer correctness” cho Day 09 dựa trên `expected_answer` và `expected_sources` của test set. Lý do: trace hiện đã đủ metadata nhưng phần compare vẫn còn N/A ở multi-hop accuracy. Nếu có metric này, bảng single-vs-multi sẽ đầy đủ hơn và giúp nhóm kết luận mạnh hơn về chất lượng, không chỉ về debuggability và observability.

---
