# Routing Decisions Log — Lab Day 09

**Nhóm:** C401-E5
**Ngày:** 14/04/2026

> **Hướng dẫn:** Ghi lại ít nhất **3 quyết định routing** thực tế từ trace của nhóm.
> Không ghi giả định — phải từ trace thật (`artifacts/traces/`).
> 
> Mỗi entry phải có: task đầu vào → worker được chọn → route_reason → kết quả thực tế.

---

## Routing Decision #1

**Task đầu vào:**
> Ticket P1 được tạo lúc 22:47. Đúng theo SLA, ai nhận thông báo đầu tiên và qua kênh nào? Deadline escalation là mấy giờ?

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `task relates to SLA or incident`  
**MCP tools được gọi:** Không có  
**Workers called sequence:** `synthesis_worker` *(trace `workers_called` chưa log retrieval dù retrieval đã chạy trong `worker_io_logs`)*

**Trace file:** `artifacts/traces/run_20260414_174943.json`

**Kết quả thực tế:**
- final_answer (ngắn): Trả lời đúng 3 ý chính: người nhận cảnh báo đầu tiên, kênh PagerDuty và deadline escalation 22:57, có citation.
- confidence: `0.8`
- Correct routing? `Yes`

**Nhận xét:** _(Routing này đúng hay sai? Nếu sai, nguyên nhân là gì?)_

Routing đúng và output tốt. Đây là case retrieval chuẩn: câu hỏi SLA cụ thể, không cần policy tool/MCP.

---

## Routing Decision #2

**Task đầu vào:**
> Engineer cần Level 3 access để khắc phục P1 đang active. Bao nhiêu người phải phê duyệt? Ai là người phê duyệt cuối cùng?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task relates to policy or access check`  
**MCP tools được gọi:** `search_kb`, `get_ticket_info`, `check_access_permission`  
**Workers called sequence:** `policy_tool_worker -> synthesis_worker`

**Trace file:** `artifacts/traces/run_20260414_174957.json`

**Kết quả thực tế:**
- final_answer (ngắn): Trả lời đúng cần 3 approver cho Level 3 (Line Manager, IT Admin, IT Security), và IT Security là cấp phê duyệt cao nhất.
- confidence: `0.8`
- Correct routing? `Yes`

**Nhận xét:**

Routing đúng cho case policy + access. Điểm tốt là policy worker đã gọi đủ 3 MCP tools; điểm cần cải tiến là trace `workers_called` chưa phản ánh rõ retrieval step.

---

## Routing Decision #3

**Task đầu vào:**
> Mức phạt tài chính cụ thể khi đội IT vi phạm SLA P1 resolution time (không resolve trong 4 giờ) là bao nhiêu?

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `task relates to SLA or incident`  
**MCP tools được gọi:** Không có  
**Workers called sequence:** `synthesis_worker`

**Trace file:** `artifacts/traces/run_20260414_175009.json`

**Kết quả thực tế:**
- final_answer (ngắn): Abstain đúng: “Không đủ thông tin trong tài liệu nội bộ …”, có citation.
- confidence: `0.3`
- Correct routing? `Yes`

**Nhận xét:**

Routing đúng và hành vi an toàn tốt (không hallucinate). Vì confidence thấp nên `hitl_triggered=True`, phù hợp guideline.

---

## Routing Decision #4 (tuỳ chọn — bonus)

**Task đầu vào:**
> Khách hàng mua sản phẩm trong Flash Sale, lỗi NSX, yêu cầu hoàn tiền trong 5 ngày. Có được hoàn tiền không?

**Worker được chọn:** `policy_tool_worker`  
**Route reason:** `task relates to policy or access check`

**Trace file:** `artifacts/traces/run_20260414_175024.json`

**Nhận xét: Đây là trường hợp routing khó nhất trong lab. Tại sao?**

Đây là case khó vì có điều kiện đủ hoàn tiền (lỗi NSX, trong 5 ngày) nhưng bị chặn bởi ngoại lệ Flash Sale. Cần synthesis diễn đạt rõ xung đột điều kiện-vs-ngoại lệ để tránh câu trả lời mâu thuẫn.

---

## Tổng kết

### Routing Distribution

| Worker | Số câu được route | % tổng |
|--------|------------------|--------|
| retrieval_worker | 5 | 50% |
| policy_tool_worker | 5 | 50% |
| human_review | 0 | 0% |

### Routing Accuracy

> Trong số X câu nhóm đã chạy, bao nhiêu câu supervisor route đúng?

- Câu route đúng: `10 / 10` *(đánh giá theo rule hiện tại của supervisor và loại câu hỏi trong trace)*
- Câu route sai (đã sửa bằng cách nào?): `0` (không phát hiện misroute trong bộ trace mới)
- Câu trigger HITL: `2` (`run_20260414_175009.json`, `run_20260414_175024.json`)

### Lesson Learned về Routing

> Quyết định kỹ thuật quan trọng nhất nhóm đưa ra về routing logic là gì?  
> (VD: dùng keyword matching vs LLM classifier, threshold confidence cho HITL, v.v.)

1. Keyword routing hoạt động tốt cho baseline, nhưng cần rule ưu tiên cho câu multi-hop (policy + SLA) để tăng tính đầy đủ của evidence trước synthesis.
2. Nên chuẩn hoá trace schema giữa `workers_called` và `worker_io_logs` để dễ debug luồng thực tế hơn.

### Route Reason Quality

> Nhìn lại các `route_reason` trong trace — chúng có đủ thông tin để debug không?  
> Nếu chưa, nhóm sẽ cải tiến format route_reason thế nào?

Route reason hiện tại đủ để phân loại tầng cao (SLA vs policy), nhưng còn generic. Nên nâng cấp thành dạng có cấu trúc: `route=policy_tool_worker | matched_keywords=["flash sale","hoàn tiền"] | needs_tool=True | risk_high=False` để phục vụ debug và audit.
