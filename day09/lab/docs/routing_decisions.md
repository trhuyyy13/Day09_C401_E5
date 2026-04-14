# Routing Decisions Log — Lab Day 09

**Nhóm:** Day09_C401_E5  
**Ngày:** 2026-04-14

Nguồn trace dùng để ghi log quyết định:
- `artifacts/traces/run_20260414_152639.json`
- `artifacts/traces/run_20260414_152723.json`
- `artifacts/traces/run_20260414_152735.json`

---

## Routing Decision #1

**Task đầu vào:**
> SLA xử lý ticket P1 là bao lâu?

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `task relates to SLA or incident`  
**MCP tools được gọi:** Không có  
**Workers called sequence:** `retrieval_worker -> synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): `[SYNTHESIS ERROR] Không thể gọi LLM. Kiểm tra API key trong .env.`
- confidence: `0.1`
- Correct routing? **Yes**

**Nhận xét:**

Route này hợp lý vì câu hỏi thuộc nhóm SLA/incident. Lỗi output không nằm ở route mà nằm ở bước synthesis.

---

## Routing Decision #2

**Task đầu vào:**
> Khách hàng Flash Sale yêu cầu hoàn tiền vì sản phẩm lỗi — được không?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task relates to policy or access check`  
**MCP tools được gọi:** `search_kb`  
**Workers called sequence:** `policy_tool_worker -> retrieval_worker -> synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): `[SYNTHESIS ERROR] Không thể gọi LLM. Kiểm tra API key trong .env.`
- confidence: `0.1`
- Correct routing? **Yes**

**Nhận xét:**

Route đúng vì task chứa policy exception (Flash Sale). Trace xác nhận policy worker phát hiện `flash_sale_exception` trước khi sang synthesis.

---

## Routing Decision #3

**Task đầu vào:**
> Cần cấp quyền Level 3 để khắc phục P1 khẩn cấp. Quy trình là gì?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task relates to policy or access check`  
**MCP tools được gọi:** `search_kb`, `get_ticket_info`  
**Workers called sequence:** `policy_tool_worker -> retrieval_worker -> synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): `[SYNTHESIS ERROR] Không thể gọi LLM. Kiểm tra API key trong .env.`
- confidence: `0.1`
- Correct routing? **Yes**

**Nhận xét:**

Đây là case tốt cho multi-agent vì vừa cần policy/access vừa cần tín hiệu ticket P1. Route chọn policy worker trước là phù hợp và có MCP trace đầy đủ.

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

### Route Reason Quality

`route_reason` hiện đọc được nhưng còn hơi ngắn. Nên nâng cấp format thành:

`matched_intents=[policy,access]; selected=policy_tool_worker; confidence=0.xx; fallback=false`

Format này giúp debug rõ hơn khi task chứa nhiều intent chồng lấp.
