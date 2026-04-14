# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Lương Tiến Dũng
**Vai trò trong nhóm:** Trace & Docs Owner
**Ngày nộp:** 14/04/2026
**Độ dài yêu cầu:** 500–800 từ

---

> **Lưu ý quan trọng:**
>
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

- File chính: `docs/routing_decisions.md` — ghi log chi tiết 4 quyết định routing thực tế từ trace
- Sections tôi viết: "Routing Decision #1-4" (gồm 2 ưu tiên case + 1 edge case safe behavior + 1 bonus case khó)
- Phần tổng kết: bảng routing distribution, routing accuracy analysis, lesson learned về routing strategy

**Cách công việc của tôi kết nối với phần của thành viên khác:**

- Tôi đọc 4 trace files từ `artifacts/traces/run_20260414_*.json` (được generate từ eval_trace.py của Trace Owner)
- Từ trace, tôi extract: supervisor route decision, MCP tools gọi, worker sequence, confidence level
- Tôi phân tích tại sao mỗi routing là đúng/sai, kèm lesson learned để help team optimize supervisor logic
- Output của tôi giúp team debug routing errors và refactor routing strategy cho sprint tiếp theo

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**
- File chính: `docs/routing_decisions.md` (129 dòng, 5 sections routing + 1 tổng kết)
- Trace files tham chiếu: `artifacts/traces/run_20260414_174943.json`, `run_20260414_174957.json`, `run_20260414_175009.json`, `run_20260414_175024.json`

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

> Chọn **1 quyết định** bạn trực tiếp đề xuất hoặc implement trong phần mình phụ trách.

**Quyết định:** Chọn cấu trúc ghi log routing decision theo format "Task → Route → Result → Nhận xét".

**Lý do:**
Mỗi routing decision trong lab liên quan đến state management phức tạp (trace có 20+ fields, workers lồng nhau). Thay vì viết tự do, tôi thiết kế template có cấu trúc rõ ràng để:
1. **Dễ so sánh**: Bất cứ ai review cũng biết xem task nào route đến worker nào, vì sao được/sai
2. **Dễ debug**: Khi có misroute, người đọc có thể theo trace → MCP tools → workers_called để tìm lỗi
3. **Dễ nâng cấp**: Sau này khi team thêm workers mới, chỉ cần extend template, không phải viết lại từ đầu

Template tôi dùng: **Task → Worker → Route Reason → MCP Tools → Worker Sequence → Result → Nhận xét**

**Trade-off đã chấp nhận:**
Cấu trúc cứng → khó viết những phân tích sâu sắc không khít vào box. Nhưng cái được là uniform, dễ audit cho 10-20 decisions sau.

**Bằng chứng từ trace/code:**

Routing Decision #1 (SLA Query):
```
Task: "Ticket P1 được tạo lúc 22:47. Ai nhận cảnh báo đầu tiên?"
→ Route: retrieval_worker
→ Reason: "task relates to SLA or incident"
→ Result: confidence 0.8, correct routing ✓
```

Routing Decision #2 (Policy + Access):
```
Task: "Engineer cần Level 3 access. Bao nhiêu người phê duyệt?"
→ Route: policy_tool_worker
→ MCP Tools: search_kb, get_ticket_info, check_access_permission
→ Result: confidence 0.8, correct routing ✓
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

> Mô tả 1 bug thực tế bạn gặp và sửa được trong lab hôm nay.

**Lỗi:** Routing Decision #2 ban đầu bị thiếu trường `needs_tool` trong trace, khiến tôi không thể xác định MCP có được gọi hay không.

**Symptom (pipeline làm gì sai?):**
Khi ghi log "Routing Decision #2" (Engineer cần Level 3 access), tôi thấy trace từ `run_20260414_174957.json` có `route: policy_tool_worker` nhưng `mcp_tools_used` field bị null/missing. Ban đầu tôi viết nhận xét "Không rõ MCP có được gọi không", nhưng điều này không đủ rõ ràng.

**Root cause (lỗi nằm ở đâu):**
Policy worker execute nhưng quên log `mcp_tools_used` vào trace state. Hoặc là trace schema từ graph.py không include field này cho policy_tool_worker (chỉ include cho retrieval).

**Cách sửa:**
Tôi phân tích lại trace file bằng grep:
```bash
cat run_20260414_174957.json | jq '.mcp_tools_used'
```
Phát hiện `mcp_tools_used = ["search_kb", "get_ticket_info", "check_access_permission"]` thực sự có trong file JSON. Tôi cập nhật nhận xét từ "Không rõ MCP" → "MCP đã gọi đủ 3 tools" (search_kb, get_ticket_info, check_access_permission).

**Bằng chứng trước/sau:**

Trước: `Routing Decision #2 — "MCP tools được gọi: ?"`

Sau: `Routing Decision #2 — "MCP tools được gọi: search_kb, get_ticket_info, check_access_permission"` và nhận xét "Điểm tốt là policy worker đã gọi đủ 3 MCP tools"

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

> Trả lời trung thực — không phải để khen ngợi bản thân.

**Tôi làm tốt nhất ở điểm nào?**
Tôi phân tích routing decisions rất kỹ lưỡng: không chỉ ghi kết quả, mà còn giải thích tại sao routing đúng/sai, lesson learned, và gợi ý cải tiến. Bảng "Routing Distribution" và "Tổng kết" của tôi cho cái nhìn rõ ràng về strategy: 50% retrieval, 50% policy, 0% misroute. Nhân vật độc lập case #4 (bonus) là multi-hop phức tạp nhất, tôi viết rất chi tiết tại sao nó khó.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Documentation của tôi còn thiếu ground truth labels cho 4 decisions. Tôi không có gold-standard answer để xác nhận "routing này có thật sự đúng không", chỉ đánh giá dựa vào confidence score từ trace. Nếu confidence = 0.8, tôi coi là "likely correct", nhưng đó chỉ là heuristic, không phải proof.

**Nhóm phụ thuộc vào tôi ở đâu?** _(Phần nào của hệ thống bị block nếu tôi chưa xong?)_
Nếu tôi không viết `routing_decisions.md` chi tiết, team sẽ không biết supervisor có hoạt động đúng không, không có evidence để debug routing bugs, và grading sẽ khó đánh giá routing accuracy.

**Phần tôi phụ thuộc vào thành viên khác:** _(Tôi cần gì từ ai để tiếp tục được?)_
Tôi phụ thuộc vào Trace Owner (eval_trace.py) để generate trace files hoàn chỉnh với đủ fields (supervisor_route, route_reason, workers_called, mcp_tools_used, confidence, etc.). Nếu trace fields bị thiếu hoặc sai format, phân tích của tôi sẽ incomplete.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Nếu có thêm 2 giờ, tôi sẽ:
1. **Thêm ground truth labels**: Tôi sẽ tự tay đánh giá tất cả 15 test questions để có gold-standard answer. Sau đó, tôi có thể tính routing accuracy thực tế (không phải heuristic) bằng cách so sánh supervisor route decision vs expected route decision.
2. **Viết decision tree visual**: Thay vì chỉ mô tả logic routing text, tôi vẽ flowchart: "keyword matching → route_type → supervisor_route → worker sequence → final answer", giúp team hiểu visual hơn.
3. **Optimize route_reason format**: Hiện tại route_reason đơn giản ("task relates to policy"). Tôi sẽ nâng cấp thành structured format: `route=policy_tool | matched_keywords=["flash sale"] | needs_tool=True | confidence=0.75`, để dễ parse và audit hơn.

---
