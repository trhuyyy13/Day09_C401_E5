# Báo Cáo Nhóm — Lab Day 09: Multi-Agent Orchestration

**Tên nhóm:**  C401-E5 
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|


**Ngày nộp:** 14/4/2026  
**Repo:** https://github.com/trhuyyy13/Day09_C401_E5  
**Độ dài khuyến nghị:** 600–1000 từ

---

> **Hướng dẫn nộp group report:**
> 
> - File này nộp tại: `reports/group_report.md`
> - Deadline: Được phép commit **sau 18:00** (xem SCORING.md)
> - Tập trung vào **quyết định kỹ thuật cấp nhóm** — không trùng lặp với individual reports
> - Phải có **bằng chứng từ code/trace** — không mô tả chung chung
> - Mỗi mục phải có ít nhất 1 ví dụ cụ thể từ code hoặc trace thực tế của nhóm

---

## 1. Kiến trúc nhóm đã xây dựng (150–200 từ)

> Mô tả ngắn gọn hệ thống nhóm: bao nhiêu workers, routing logic hoạt động thế nào,
> MCP tools nào được tích hợp. Dùng kết quả từ `docs/system_architecture.md`.

**Hệ thống tổng quan:**

Hệ thống sử dụng kiến trúc Supervisor-Worker Pattern với 1 node Supervisor để điều phối lệnh, 3 Workers chính (`retrieval_worker`, `policy_tool_worker`, `synthesis_worker`) và 1 node phụ (human_review). Input từ user đi qua Supervisor để classify -> Quyết định chọn Worker xử lý tác vụ -> Dữ liệu vào `synthesis_worker` tổng hợp câu trả lời cuối cùng để Output và trả về cho user.


**Routing logic cốt lõi:**
> Mô tả logic supervisor dùng để quyết định route (keyword matching, LLM classifier, rule-based, v.v.)

Supervisor hiện đang dùng logic rule-based (Regex và Keyword matching). Nếu query của user chứa mã `ERR-xxx`, hệ thống route về `human_review` và đánh dấu `risk_high=True`. Nếu trong query có chứa từ khoá liên quan tới policy ("hoàn tiền", "refund", "flash sale", "access level"), hệ thống chuyển hướng sang `policy_tool_worker` kèm cờ `needs_tool=True` để check logic nâng cao của file chính sách. Mặc định hệ thống route về `retrieval_worker`.


**MCP tools đã tích hợp:**
> Liệt kê tools đã implement và 1 ví dụ trace có gọi MCP tool.

- `search_kb`: Tìm kiếm ChromaDB vector database. Ví dụ trace: `[policy_tool_worker] called MCP search_kb`
- `get_ticket_info`: Lấy dữ liệu mock JIRA ticket, ví dụ: gọi MCP `get_ticket_info` với data `P1-LATEST`.
- `check_access_permission`: Phân tích điều kiện phân quyền (access level) dựa theo rule nội bộ.
- `create_ticket`: Tạo mock ticket mới trong Jira (thực tế trả lại dummy mock_id).

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

> Chọn **1 quyết định thiết kế** mà nhóm thảo luận và đánh đổi nhiều nhất.
> Phải có: (a) vấn đề gặp phải, (b) các phương án cân nhắc, (c) lý do chọn phương án đã chọn.

**Quyết định:** Sử dụng Rule-based Keyword/Regex matching làm Routing thay vì dùng LLM-based Supervisor.

**Bối cảnh vấn đề:**

Ban đầu nhóm gặp tình trạng LLM bị hallucinate khi làm Supervisor, nhiều câu mô tả chéo bị đẩy vào sai worker dẫn đến kết quả tìm kiếm rỗng, hoặc sinh ra latency khổng lồ (tăng thêm ~2-3 giây) chỉ để quyết định đi đường nào.


**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Rule-based Keyword Routing | Latency bằng 0, độ trễ thấp, ổn định chạy cực kỳ cực kỳ chắc tay | Phải hardcode keyword, kém linh hoạt nểu data mới xuất hiện |
| LLM-based Supervisor Classifer | Rất linh hoạt phân tích ngầm theo nghĩa chứ không phụ thuộc chữ | Tốn API cost, latency cao ~2s, có rủi ro bị hallucination |

**Phương án đã chọn và lý do:**

Nhóm chọn Rule-based Regex vì ở mức độ lab hiện tại các query và test cases hoàn toàn có thể phân loại nhanh bằng pattern. Chi phí cho một RAG Agent đã khá cao nên việc giảm tải cho API Gateway để hệ thống dễ debug là sự ưu tiên lớn. Logic này chặn được triệt để việc hallucination.


**Bằng chứng từ trace/code:**
> Dẫn chứng cụ thể (VD: route_reason trong trace, đoạn code, v.v.)

```python
# graph.py đoạn code Supervisor
has_err_code = bool(re.search(r"err-\w+", task))
if has_err_code:
    route = "human_review"
    route_reason = "unknown error code (ERR-xxx) -> human review"
elif any(kw in task for kw in policy_keywords):
    route = "policy_tool_worker"
```

---

## 3. Kết quả grading questions (150–200 từ)

> Sau khi chạy pipeline với grading_questions.json (public lúc 17:00):
> - Nhóm đạt bao nhiêu điểm raw?
> - Câu nào pipeline xử lý tốt nhất?
> - Câu nào pipeline fail hoặc gặp khó khăn?

**Tổng điểm raw ước tính:** 94 / 96

**Câu pipeline xử lý tốt nhất:**
- ID: gq02, gq03 — Lý do tốt: Đây là các câu về kiểm tra quyền Access Level, nhờ có tool chuyên biệt là `check_access_permission`, MCP đã format cấu trúc list answer cực chuẩn mà base RAG rất vất vả mới lấy được.

**Câu pipeline fail hoặc partial:**
- ID: gq09 — Fail ở đâu: Multi-hop question bị đánh giá điểm thấp. 
  Root cause: Logic không chia sẻ state giữa các bước một cách toàn vẹn. State từ policy tool trả về nhưng đoạn context này ko hợp mượt vào chunk retrieval khiến synthesis missing the link.

**Câu gq07 (abstain):** Nhóm xử lý thế nào?

Câu hỏi không đủ dữ kiện, nhờ code ở `synthesis.py` bắt strict rule (confidence < 0.4), hệ thống xuất ra text an toàn: `"Không đủ thông tin trong tài liệu nội bộ để trả lời chính xác câu hỏi này."` để tránh hallucination.


**Câu gq09 (multi-hop khó nhất):** Trace ghi được 2 workers không? Kết quả thế nào?

Trace có đi đủ qua `policy_tool_worker` (nhờ keyword) -> Sinh `needs_tool` gọi MCP `search_kb` (1 worker + tool gián tiếp) -> về cuối gọi tới `synthesis_worker`. Kết quả ra partial answer bởi vì missing policy note cho năm cũ.


---

## 4. So sánh Day 08 vs Day 09 — Điều nhóm quan sát được (150–200 từ)

> Dựa vào `docs/single_vs_multi_comparison.md` — trích kết quả thực tế.

**Metric thay đổi rõ nhất (có số liệu):**

Thời gian Debug trung bình trong quá trình develop tính từ lúc gặp exception giảm từ khoảng `10 phút` (ở Day 08 - đọc ngược lại từ pipeline output rỗng) xuống còn `1-2 phút` (Day 09) nhờ có file trace array log rõ ràng từ `worker_io_logs`.


**Điều nhóm bất ngờ nhất khi chuyển từ single sang multi-agent:**

Thay vì chỉ có log terminal trôi qua nhanh, state object `AgentState` khổng lồ, nó phình to ở array dict rất lớn tới mức việc review JSON tay rất mỏi mắt. Nó cho thấy nếu không có UI cho MCP Trace thì quản lý memory ở worker orchestrator sẽ khó khăn.


**Trường hợp multi-agent KHÔNG giúp ích hoặc làm chậm hệ thống:**

Khi user gửi câu hỏi quá đơn giản mà Single RAG dư sức làm (ví dụ: "SLA của ticket P1?"). Graph vẫn buộc phải gọi loop tạo History state, sau đó gọi list chunk đi qua Synthesis. Kết quả sinh ra Latency bị push thêm ~800-1000ms là không đáng.


---

## 5. Phân công và đánh giá nhóm (100–150 từ)

> Đánh giá trung thực về quá trình làm việc nhóm.

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Huy | Thiết kế hệ thống, dev core graph.py | Sprint 1 & 3 |
| Đăng & Tuấn | Cài chromaDB, debug file JSON, code 2 workers | Sprint 2 |
| Sơn | Implement MCP local server và viết mock tools, report markdown| Sprint 1 & 3 |
| Đạt & Dũng | Chống hallucinate, setup evaluator | Sprint 2 |

**Điều nhóm làm tốt:**

Tích hợp mượt mà cơ chế server backend (Mocked MCP) và bóc tách tốt tư duy modular. Mỗi cá nhân có thể test local cái Worker của mình (nhờ đoạn `__main__` cuối file) mà không sợ break code đồng đội.


**Điều nhóm làm chưa tốt hoặc gặp vấn đề về phối hợp:**

Mỗi thành viên embedding 1 kiểu xong không thống nhất với nhau từ đầu ==> conflict 


**Nếu làm lại, nhóm sẽ thay đổi gì trong cách tổ chức?**

Cân nhắc ý tưởng dùng `LangGraph` thay vì tự viết logic state truyền tay tay bằng custom function dict vì LangGraph có check schema node sẵn, rất an toàn.


---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

> 1–2 cải tiến cụ thể với lý do có bằng chứng từ trace/scorecard.

Sẽ thay thế Rule-based Classifier bằng một mô hình LLM chuyên Classifier rẻ và nhanh (ví dụ GPT-4o-mini). Do scorecard gợi ý là các câu phức tạp đang bị fallback về retrieval_worker quá nhiều vì thiếu regex keyword (trace luôn ghi `default route`).
Và code thực thụ 1 `Human In The Loop (HITL)` Node thông qua Interrupt Stream thay vì chỉ mock text output auto-approve như hiện tại.


---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
