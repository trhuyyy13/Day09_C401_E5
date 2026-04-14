# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Trần Quang Huy
**Vai trò trong nhóm:** Supervisor Owner
**Ngày nộp:** 15/04/2026
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

- File chính: `graph.py` (Supervisor Orchestrator)
- Functions tôi implement: `supervisor_node`, `route_decision` và setup shared `AgentState`

**Cách công việc của tôi kết nối với phần của thành viên khác:**

- Tôi đã kết nối với worker retrieval và policy tool bằng cách sử dụng các biến shared state (`route_reason`, `supervisor_route`, `needs_tool`, `risk_high`) để truyền dữ liệu định tuyến giữa các worker một cách trơn tru.
- Viết architecture của group để định hướng toàn cảnh (System Architecture Diagram).

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**
064a87bb52bf602e1cbf952ee65409022b493841
768fb590e73a318c4d9c4560cbbbeee9c876998a

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

> Chọn **1 quyết định** bạn trực tiếp đề xuất hoặc implement trong phần mình phụ trách.

**Quyết định:** Sử dụng Rule-based routing (Keyword & Regex matching) trong `supervisor_node` thay vì gọi LLM Classification.

**Lý do:**
Việc định tuyến bằng Regex/Keyword nhanh hơn rất nhiều (latency chỉ vài ms) so với việc phải mất 500ms-800ms đợi kết quả từ LLM. Hơn nữa, nó miễn phí và đảm bảo tính "deterministic" (ổn định). Với scope nhỏ của bài Lab này (chủ yếu là 3 mảng: xử lý lỗi hệ thống, thay đổi phân quyền/SLA và kiểm tra hoàn tiền), dùng keyword là quá đủ. Quyết định này giúp giữ latency của hệ thống thấp và ổn định cho nhánh frontend/backend giao tiếp.

**Trade-off đã chấp nhận:**
Hệ thống cứng nhắc (brittle routing). Nếu người dùng dùng từ đồng nghĩa mà danh sách keywords không hỗ trợ, supervisor sẽ tự động route về default (`retrieval_worker`), có thể dẫn đến fallback trả lời không đúng mong đợi của nhánh policy_tool (VD: trả lời bằng cách retrieve văn bản thay vì gọi MCP API).

**Bằng chứng từ trace/code:**

```python
    has_err_code = bool(re.search(r"err-\w+", task))

    if has_err_code:
        route = "human_review"
        route_reason = "unknown error code (ERR-xxx) -> human review"
        risk_high = True
    elif any(kw in task for kw in policy_keywords):
        route = "policy_tool_worker"
        route_reason = "task relates to policy or access check"
        needs_tool = True
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

> Mô tả 1 bug thực tế bạn gặp và sửa được trong lab hôm nay.

**Lỗi:** Supervisor định tuyến sai tác vụ cấp quyền truy cập.

**Symptom (pipeline làm gì sai?):**
Khi nhận request từ user: _"Cần cấp quyền Level 3 để khắc phục P1 khẩn cấp"_, hệ thống không chịu cấp phép (luôn trả lời chung chung theo docs) mà đáng lẽ phải truy cập `check_access_permission` của MCP Server để thao tác.

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**
Do lỗi định tuyến của `supervisor_node`. Trong danh sách mảng `policy_keywords` ban đầu tôi khai báo, đã bị thiếu hoàn toàn các từ khoá liên quan đến việc cấp quyền, nên nó lọt xuống cụm default `retrieval_worker` (nhận tag là keyword "P1").

**Cách sửa:**
Tôi đã bổ sung hàng loạt từ khóa chuyên sâu vào biến `policy_keywords` trong hàm `supervisor_node` gồm: `"cấp quyền"`, `"access level"`, `"level 3"`, `"license"`. Việc này giúp node phân quyền bắt trúng keyword nhanh hơn fallback SLA "P1".

**Bằng chứng trước/sau:**
Trước khi sửa (Log trace):

> [supervisor] route=retrieval_worker reason=default route

Sau khi sửa (Log trace):

> [supervisor] route=policy_tool_worker reason=task relates to policy or access check

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

> Trả lời trung thực — không phải để khen ngợi bản thân.

**Tôi làm tốt nhất ở điểm nào?**
Tôi đã thiết kế `AgentState` cực kỳ gọn gàng với trace rành mạch qua từng chặng truyền node trong Pipeline. Hơn thế nữa, báo cáo kiến trúc hệ thống cũng được vi phẫu cụ thể và trực quan nhất để team không bị loạn scope.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Do dùng rule-based thay vì sử dụng LangGraph `StateGraph`, Graph Pipeline vẫn còn thủ công dạng if/else Option A nên thiếu đi flow ngắt vòng (Interrupts) thực tế cho HITL node (vẫn đang phụ thuộc vào mock log CLI thay vì dừng pipeline toàn trình).

**Nhóm phụ thuộc vào tôi ở đâu?** _(Phần nào của hệ thống bị block nếu tôi chưa xong?)_
Nếu tôi không cấu trúc `AgentState` và `graph.py` chạy lên khung hoàn chỉnh với các wrapper node thì team làm Worker không thể wrap hàm entrypoint của họ vào flow của bài thí nghiệm.

**Phần tôi phụ thuộc vào thành viên khác:** _(Tôi cần gì từ ai để tiếp tục được?)_
Tôi phụ thuộc vào Worker Owner để rào kỹ các file `worker_contracts` vì tôi truyền dict input cho họ qua schema, nếu thiếu key/value thì node Synthesis của graph sẽ sụp đổ.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Nếu có thêm 2 giờ, tôi sẽ nâng cấp Option A bằng Python thuần lên dùng **LangGraph Node/Edge**, kết hợp một LLM-as-a-Router thật sự để phân luồng Agent. Lý do là nhìn vào trace hiện thời, nếu input của người dùng dùng Slang (từ lóng/tiếng anh xen việt), regex routing của tôi sẽ trượt hoàn toàn. Xây `StateGraph` với LangGraph cũng sẽ giúp mở khóa Breakpoint Interrupt cho human-in-the-loop duyệt thật thay vì in log mock như lab hiện tại.

---
