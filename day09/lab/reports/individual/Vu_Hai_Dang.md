# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:**   Vũ Hải Đăng - 2A202600339

**Vai trò trong nhóm:** Worker Owner & Docs Owner  

**Ngày nộp:** 14/04/2026

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

**Module/file tôi chịu trách nhiệm:**
 - File chính: `workers/policy_tool.py` và `docs/routing_decisions.md`
 - Functions tôi implement:
	 - `analyze_policy(task, chunks)`: Rule-based policy analysis — phát hiện ngoại lệ (flash sale, sản phẩm kỹ thuật số, đã kích hoạt), trích xuất bằng chứng (lỗi sản phẩm, khung thời gian, chưa dùng), phân tích ngày giao dịch và trả về `policy_result` có cấu trúc (policy_applies, policy_name, exceptions_found, evidence, explanation).
	 - `run(state)`: Entrypoint của worker — điều phối fallback retrieval (`search_kb` khi thiếu chunks), chạy `analyze_policy`, gọi MCP tools (`get_ticket_info`, `check_access_permission`) khi cần, và ghi `policy_result`, `mcp_tools_used`, `worker_io_logs` vào `state` để supervisor/synthesis dùng.
	 - `_call_mcp_tool(tool_name, tool_input)`: Wrapper gọi MCP dispatcher trong-process — chuẩn hóa đầu ra (`output`, `error`, `timestamp`) và xử lý ngoại lệ để trace ổn định.
 - Sửa `tool_search_kb()` trong MCP server
 - Làm docs/routing_decisions.md


**Cách công việc của tôi kết nối với phần của thành viên khác:**

Tôi là điểm nối giữa phần điều phối (`supervisor`/`retrieval`) và bước tổng hợp câu trả lời cuối cùng. Tôi đã hoàn thiện các hàm then chốt trong `policy_tool.py`:
- `analyze_policy()` — phát hiện ngoại lệ chính sách (ví dụ: flash sale, sản phẩm kỹ thuật số, đã kích hoạt), xác định khung thời gian và trích xuất bằng chứng từ `retrieved_chunks`.
- `run()` — điều phối luồng xử lý: gọi `search_kb` khi thiếu context, gọi `get_ticket_info` hoặc `check_access_permission` khi cần, và cập nhật `state` với `policy_result` và `mcp_tools_used`.
- `_call_mcp_tool()` — wrapper chuẩn hóa kết quả cuộc gọi MCP (bao gồm `output`, `error`, `timestamp`) để trace ổn định.

Khi các hàm này chạy ổn định, `state` truyền sang `synthesis` sẽ có cấu trúc và bằng chứng rõ ràng hơn, giúp giảm khả năng tổng hợp kết luận sai ngay cả khi routing là đúng.

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**

- Trace sau cập nhật đã ghi nhận đầy đủ các trường: `policy_result`, `mcp_tools_used`, `access_check`.
- File `docs/routing_decisions.md` được hoàn thiện dựa trên trace thực tế của hệ thống.

- Commit `4ee02ec61a12214d1e28bba45bb7f5bfbdbe047d` - cập nhật `workers/policy_tool.py`.
- Commit `cb8ea9af35e40543d2b493090446bcf7353b3550` - bổ sung `docs/routing_decisions.md` và sửa MCP server.
---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Tôi chuẩn hóa stack embedding sang model OpenAI `ext-embedding-3-small` để cải thiện độ tin cậy của retrieval và tránh mismatch giữa các thành phần.

**Lý do:**
Ban đầu hệ thống dùng `all-MiniLM-L6-v2` (local) cho một số chỉ mục, nhưng sau khi đánh giá thực nghiệm tôi nhận thấy điểm tin cậy (confidence) của retrieval thường thấp và không ổn định. Vì vậy tôi chuyển toàn bộ sang model OpenAI `ext-embedding-3-small` để:
- Cải thiện độ tin cậy retrieval (tăng confidence)
- Tránh mismatch vector giữa các component
- Đảm bảo kết quả retrieval và tool call nhất quán
- Dễ debug hơn khi trace toàn pipeline

---

**Trade-off đã chấp nhận:**

- Phụ thuộc vào API key  
- Tốn chi phí embedding  

Đổi lại:
- Flow ổn định hơn  
- Kết quả đáng tin cậy hơn  
- Debug dễ hơn  

---
**Bằng chứng từ trace/code:**

**Trước khi thống nhất embedding:**
- Sử dụng `all-MiniLM-L6-v2` để tạo embedding vector.

**Sau khi đồng bộ sang `text-embedding-3-small`:**
- `search_kb` trả về chunks từ source thật (vd: `access_control_sop.txt`, `policy_refund_v4.txt`)
- `policy_result` và câu trả lời có citation ổn định hơn  
- Confidence của retrieval tăng rõ rệt  

**Code sử dụng OpenAI embedding ở mcp_server.py:**
```python
from openai import OpenAI
client = OpenAI()

def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```    
---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** False positive trong phát hiện ngoại lệ “đã kích hoạt” ở policy hoàn tiền.

**Symptom (pipeline làm gì sai?):**

Với câu có cụm phủ định như “chưa kích hoạt”, worker vẫn gắn `activated_exception` và đẩy `policy_applies=False` sai.

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**

Root cause nằm ở `analyze_policy()`: detector cũ match keyword quá rộng (`kích hoạt`, `activated`) và không tách phủ định/khẳng định.

**Cách sửa:**

Tôi tách hai tín hiệu regex: `has_positive_activation` (đã kích hoạt/registered) và `has_negative_activation` (chưa kích hoạt/không đăng ký/not activated). Chỉ gắn exception khi có positive và không có negative, đồng thời trả thêm evidence để downstream đọc rõ trạng thái.

**Bằng chứng trước/sau:**

**Trước**:  Test standalone policy worker với case *“5 ngày, lỗi NSX, chưa kích hoạt”* vẫn trả về: `policy_applies = False` và có `activated_exception` (gắn sai)
- **Task:** Khách hàng yêu cầu hoàn tiền trong 5 ngày, sản phẩm lỗi, chưa kích hoạt...
- `policy_applies`: **False**
- `exception`: `activated_exception` — Sản phẩm đã kích hoạt hoặc đăng ký tài khoản không được hoàn
- `MCP calls`: **0**

**Sau**: Không còn gắn nhầm exception
- **Task:** Khách hàng yêu cầu hoàn tiền trong 5 ngày, sản phẩm lỗi, chưa kích hoạt...
- `policy_applies`: **True**
- `MCP calls`: **0**

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**

Tôi làm tốt ở việc biến policy worker từ skeleton TODO thành module chạy thực tế: có exception handling, temporal check, MCP integration và trace log kiểm chứng được.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**

Trong phạm vi nhiệm vụ của tôi (`policy_tool.py` và `docs/routing_decisions.md`), tôi chưa chuẩn hoá hoàn toàn trace output: `workers_called` chỉ ghi tên worker, còn `worker_io_logs` ghi chi tiết `input`/`output`/`timestamp`. Vì vậy việc tổng hợp trace cho báo cáo routing và debug vẫn mất thời gian.

**Nhóm phụ thuộc vào tôi ở đâu?** _(Phần nào của hệ thống bị block nếu tôi chưa xong?)_

Nếu chưa xong: `synthesis` có thể thiếu `policy_result` chuẩn, script phân tích trace không tính được metric, và cơ chế HITL có thể không kích hoạt chính xác — làm giảm tính minh bạch và khả năng grading tự động.

**Phần tôi phụ thuộc vào thành viên khác:** _(Tôi cần gì từ ai để tiếp tục được?)_

Cần: `retrieval` cung cấp chunks có `source`/`text`; `supervisor` xác nhận `route_reason`/`needs_tool`; `mcp_server` đảm bảo output có `source`; Ops cấp `OPENAI_API_KEY`.

Cần thống nhất schema trace chung để mọi worker ghi log cùng định dạng.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Tôi sẽ làm một cải tiến: chuẩn hóa trace format tập trung cho toàn graph (route, tools, confidence) bằng helper ghi log chung. Lý do là trace hiện đủ dữ liệu nhưng còn lệch cấu trúc giữa các worker, làm debug chậm. Chuẩn hóa trace sẽ giúp đối chiếu nhanh hơn giữa code, báo cáo routing và kết quả grading.

---
