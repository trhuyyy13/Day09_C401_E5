# Routing Decisions Log — Lab Day 09

**Nhóm:** Day09_C401_E5  
**Ngày:** 2026-04-14

Nguồn trace dùng để ghi log quyết định:
- `artifacts/traces/run_20260414_172717.json`
- `artifacts/traces/run_20260414_172735.json`
- `artifacts/traces/run_20260414_172755.json`

---

## Routing Decision #1

**Task đầu vào:**
> SLA xử lý ticket P1 là bao lâu?

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `task relates to SLA or incident`  
**MCP tools được gọi:** Không có  
**Workers called sequence:** `retrieval_worker -> synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): `Phản hồi ban đầu 15 phút, resolution 4 giờ, escalation sau 10 phút không phản hồi.`
- confidence: `0.81`
- Correct routing? **Yes**

**Nhận xét:**

Route này hợp lý vì câu hỏi thuộc nhóm SLA/incident. Trace mới cho thấy retrieval lấy đúng `sla_p1_2026.txt` và synthesis trả lời grounded, nên route này đúng cả về intent lẫn kết quả.

---

## Routing Decision #2

**Task đầu vào:**
> Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task relates to policy or access check`  
**MCP tools được gọi:** `search_kb`  
**Workers called sequence:** `policy_tool_worker -> retrieval_worker -> synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): `Khách hàng có thể yêu cầu hoàn tiền trong vòng 7 ngày làm việc kể từ khi xác nhận đơn hàng.`
- confidence: `0.81`
- Correct routing? **Yes**

**Nhận xét:**

Route đúng vì task cần policy lookup về refund window. Trace cho thấy policy worker gọi `search_kb` trước, sau đó synthesis ghép câu trả lời đúng từ `policy_refund_v4.txt`.

---

## Routing Decision #3

**Task đầu vào:**
> Ai phải phê duyệt để cấp quyền Level 3?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task relates to policy or access check`  
**MCP tools được gọi:** `search_kb`, `check_access_permission`  
**Workers called sequence:** `policy_tool_worker -> retrieval_worker -> synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): `Level 3 cần phê duyệt của Line Manager, IT Admin và IT Security.`
- confidence: `0.81`
- Correct routing? **Yes**

**Nhận xét:**

Đây là case tốt cho multi-agent vì vừa cần policy/access vừa cần kiểm tra quyền cụ thể. Policy worker gọi `search_kb` rồi `check_access_permission`, nên routing và tool choice đều đúng.

---

## Tổng kết

### Routing Distribution

| Worker | Số câu được route | % tổng |
|--------|------------------|--------|
| retrieval_worker | 1 | 33.3% |
| policy_tool_worker | 2 | 66.7% |
| human_review | 0 | 0.0% |

### Routing Accuracy

Trong 3 câu đã chạy trong thư mục trace:

- Câu route đúng: 3 / 3
- Câu route sai: 0
- Câu trigger HITL: 0

### Lesson Learned về Routing

1. Rule-based routing theo intent keyword (SLA/incident vs policy/access) đang đủ chính xác cho tập trace nhỏ.
2. `route_reason` là bắt buộc để tách lỗi routing khỏi lỗi synthesis, giúp debug nhanh hơn.
3. MCP nên được bật theo từng intent cụ thể: SLA query chỉ cần retrieval, còn policy/access query mới cần tool worker.

### Route Reason Quality

`route_reason` hiện đọc được nhưng còn hơi ngắn. Nên nâng cấp format thành:

`matched_intents=[policy,access]; selected=policy_tool_worker; confidence=0.xx; fallback=false`

Format này giúp debug rõ hơn khi task chứa nhiều intent chồng lấp.
