# System Architecture — Lab Day 09

**Nhóm:** Antigravity / Agentic
**Ngày:** 2026-04-14
**Version:** 1.0

---

## 1. Tổng quan kiến trúc

**Pattern đã chọn:** Supervisor-Worker
**Lý do chọn pattern này:**
Tách các xử lý (routing, lấy tài liệu, kiểm tra quy định, tổng hợp) thành các "worker" độc lập, giúp việc scale và debug từng tính năng dễ dàng (VD: module hóa việc gọi MCP riêng trong policy tool). Đồng thời, bảo đảm workflow luôn trải qua bước tổng hợp để có kiểm soát citation và tin cậy cao, tránh hallucination của Single Agent.

---

## 2. Sơ đồ Pipeline

```
     User Request
          │
          ▼
    ┌──────────────┐
    │  Supervisor  │ ──(is_high_risk)──▶ [Human Review (HITL)]
    └──────┬───────┘                            │
           │ route_decision                     │ (auto-approve/resume)
    ┌──────┴───────────────────┐                │
    │                          │                ▼
    ▼                          ▼           (retrieval_worker)
Retrieval Worker       Policy Tool Worker
(Vector Search)     (MCP Tools + Policy Logic)
    │                          │
    └──────────┬───────────────┘
               │
               ▼
         Synthesis Worker
  (Generates Answer + Citation + Confidence)
               │
               ▼
             Output 
```

---

## 3. Vai trò từng thành phần

### Supervisor (`graph.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Phân tích intent (dựa trên keyword/regex) và route request đến worker phù hợp nhất. |
| **Input** | `task` (Câu hỏi từ user) |
| **Output** | `supervisor_route`, `route_reason`, `risk_high`, `needs_tool` |
| **Routing logic** | Phân loại tĩnh qua rule-based (regex/keywords), check các case policy, lỗi, hoặc retrieval mặc định. |
| **HITL condition** | Trigger nếu nhận diện lỗi lạ (`ERR-xxx`) thông qua flag `risk_high=True` để tạm dừng checkpoint. |

### Retrieval Worker (`workers/retrieval.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Truy xuất `top_k` chunk tài liệu liên quan từ ChromaDB. |
| **Embedding model** | Hỗ trợ nhiều lựa chọn (SentenceTransformer `all-MiniLM-L6-v2`, OpenAI `text-embedding-3-small`, fallback). |
| **Top-k** | Default = 3 |
| **Stateless?** | Yes |

### Policy Tool Worker (`workers/policy_tool.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Kiểm tra quyền truy cập, phân tích thời điểm mua/nơi mua bằng rule parsing và gọi trực tiếp MCP layer để có thông tin ngoại lệ (VD: trạng thái ticket). |
| **MCP tools gọi** | `search_kb`, `get_ticket_info`, `check_access_permission`, `create_ticket` |
| **Exception cases xử lý** | Đơn hàng Flash Sale, Digital products/License key, Sản phẩm đã kích hoạt, Hạn dùng theo policy version. |

### Synthesis Worker (`workers/synthesis.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **LLM model** | OpenAI `gpt-4o-mini` hoặc `gemini-1.5-flash` kèm fallback tĩnh (rule-based). |
| **Temperature** | 0.1 (hạn chế tối đa hallucination) |
| **Grounding strategy** | Strict System Prompt, yêu cầu citation, kết hợp rule-based synthesis nếu LLM thất bại. Tính toán confidence penalty. |
| **Abstain condition** | Khi context rỗng (retrieval+policy không có thông tin), hoặc trigger confidence quá thấp (< 0.4 sẽ bật HITL flag). |

### MCP Server (`mcp_server.py`)

| Tool | Input | Output |
|------|-------|--------|
| search_kb | query, top_k | chunks, sources, total_found |
| get_ticket_info | ticket_id | ticket_id, priority, status, assignee, created_at, sla_deadline |
| check_access_permission | access_level, requester_role, is_emergency | can_grant, required_approvers, emergency_override, notes, source |
| create_ticket | priority, title, description | ticket_id, url, created_at (mock) |

---

## 4. Shared State Schema

| Field | Type | Mô tả | Ai đọc/ghi |
|-------|------|-------|-----------|
| task | str | Câu hỏi đầu vào | supervisor đọc |
| supervisor_route | str | Worker được chọn | supervisor ghi, graph đọc |
| route_reason | str | Lý do quyết định phân nhánh | supervisor ghi |
| needs_tool | bool | Báo hiệu có cần truy xuất tool | supervisor ghi, policy_tool đọc |
| risk_high | bool | Báo hiệu có risk/human_review mode | supervisor ghi |
| hitl_triggered | bool | Cờ tạm dừng hệ thống yêu cầu HITL | human_review, synthesis ghi |
| retrieved_chunks | list | Đoạn dữ liệu trích xuất từ database | retrieval/policy_tool ghi, synthesis đọc |
| retrieved_sources| list | Nguồn tài liệu | retrieval ghi, synthesis đọc |
| policy_result | dict | Kết quả check SOP/Quy định và các điều kiện | policy_tool ghi, synthesis đọc |
| mcp_tools_used | list | Lưu lại các MCP API Tools đã dùng | policy_tool ghi |
| final_answer | str | Câu trả lời cuối được formulate text | synthesis ghi |
| confidence | float | Mức tin cậy (0.0 - 1.0) | synthesis ghi |

---

## 5. Lý do chọn Supervisor-Worker so với Single Agent (Day 08)

| Tiêu chí | Single Agent (Day 08) | Supervisor-Worker (Day 09) |
|----------|----------------------|--------------------------|
| Debug khi sai | Khó — không rõ lỗi ở đâu do LLM xử lý gộp | Dễ hơn — test từng worker độc lập (có script chạy rời). |
| Thêm capability mới | Phải sửa toàn prompt, dễ gây "catastrophic forgetting" logic cũ | Thêm worker/MCP tool riêng, không cấu hình lại các node khác. |
| Routing visibility | Không có (một bước sinh ReAct chain rối) | Có chi tiết log `route_reason` và call trace trong hệ thống. |
| Ổn định và Grounding | Hallucination cao vì ôm ghép quá nhiều tool | Synthesis bị ép strict bằng context tĩnh từ Policy và Retrieval Node truyền qua. |

**Nhóm điền thêm quan sát thực tế lab:** Thiết kế worker riêng biệt cho `policy_tool` và `synthesis` đã mở ra chế độ fallback tuyệt vời. Khi hệ thống không call được LLM Service (hoặc lỗi parse), hệ thống vẫn tự động fallback ra format rule-based, điều mà Single Agent có thể nổ traceback hoặc chệch luồng hoàn toàn.

---

## 6. Giới hạn và điểm cần cải tiến

1. **Routing Logic cứng nhắc**: Supervisor hiện vẫn sử dụng Rule-based (Regex/Keywords matching) nên tỉ lệ nhầm phân nhánh có thể cao với những truy vấn phức tạp của người dùng thay vì Semantic Routing (LLM-based Router/Classifier).
2. **Policy Checking chưa thực sự mềm dẻo**: `policy_tool.py` đang lạm dụng Regex tự động để trích xuất exception. Với ngữ liệu thiên biến vạn hóa, nếu không dùng LLM-as-a-Judge hỗ trợ tại node này thì sẽ miss exception logic dễ dàng.
3. **Luồng tuyến tính khuyết thiếu Feedback Loop**: Graph hiện tại flow theo pipeline một chiều (DAG). Nếu Retrieval không tìm thấy chunk hoặc Policy cần thêm thông tin, agent không thể tự quay về re-write truy vấn để tiếp tục (self-correction).
