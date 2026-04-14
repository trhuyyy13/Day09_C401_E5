# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Trần Ngọc Sơn  
**Vai trò trong nhóm:** MCP Owner 
**Ngày nộp:** 14/4/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

**Module/file tôi chịu trách nhiệm:**
- File chính: `mcp_server.py`
- Functions tôi implement: Toàn bộ Logic Backend MCP bao gồm `tool_search_kb`, `tool_get_ticket_info`, `tool_check_access_permission` và định nghĩa `TOOL_SCHEMAS`. Ngoài ra tôi bổ sung HTTP Entrypoint bằng thư viện `FastAPI` để mô phỏng kiến trúc server client độc lập.

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Tôi tạo ra cơ chế "Plugin" bằng cách cung cấp danh sách tool discovery qua hàm `list_tools()`. Các Worker Owner (bạn Đăng & Tuấn) ở file `workers/policy_tool.py` cần gọi hàm `dispatch_tool` để query policy, mock access hoặc parse schema input từ LLM rồi chuyển payload vào server script của tôi để ra được kết quả cuối cùng. Bất kỳ tool nào mới cũng phải qua tay tôi thiết kế schema (Pydantic style) để worker có thể bind và hiểu.

**Bằng chứng:**
Tôi trực tiếp handle Sprint 1 & 3 như ghi trong `group_report.md`. File `mcp_server.py` mang kiến trúc do tôi build (có sẵn endpoint FastAPI).

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Sử dụng Singleton Cache (Lazy Loading) để kết nối ChromaDB bên trong tiến trình của MCP API Server, thay vì gọi kết nối tạo mới ở mỗi lệnh dispatch `search_kb`.

**Lý do:**
Chroma DB Persistent Client hoạt động dựa trên backend cơ sở dữ liệu SQLite cục bộ (lưu vào ổ cứng). Nếu code gọi `chromadb.PersistentClient()` và load model embedding `SentenceTransformer` ở bên trong vòng đời API mỗi lần gọi hàm `tool_search_kb`, thời gian load cực kỳ lớn (~2-3s cho vector load), bộ nhớ bị rò rỉ (memory leak) nếu chạy loop qua nhiều question, và SQLite sẽ quăng lỗi `sqlite3.OperationalError: database is locked` nếu nhiều thread cùng access database cùng lúc. 

**Trade-off đã chấp nhận:**
Khởi động Worker Tool lần đầu chạy hàm search sẽ hơi trễ do phải Init object vào RAM. Cache memory của server sẽ tăng một lượng khoảng ~500MB (bởi model `all-MiniLM-L6-v2`) xuyên suốt vòng đời.

**Bằng chứng từ trace/code:**
Tôi viết Helper này đặt ngoài root `mcp_server.py` để giữ thread-safe:
```python
# Helper: Lazy load ChromaDB & Model trong mcp_server.py
_chroma_client = None
_chroma_col = None

def get_chroma_col():
    global _chroma_client, _chroma_col
    if _chroma_client is None:
        import chromadb
        db_path = os.path.join(os.path.dirname(__file__), 'chroma_db')
        _chroma_client = chromadb.PersistentClient(path=db_path)
        _chroma_col = _chroma_client.get_or_create_collection('day09_docs')
    return _chroma_col
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** Worker Policy gọi hàm check access bị crash do sai kiểu dữ liệu truyền vào của schema từ user command.

**Symptom (pipeline làm gì sai?):**
Khi user nhập thông tin nhập nhằng: "Cho mình cấp độ level admin", `policy_tool_worker` đôi lúc pass string là "admin" cho trường `access_level` thay vì Expect là Integer theo design. Kết quả tool ném Exception TypeError "unsupported operand type" bên trong MCP Server, pipeline sập hoàn toàn và final_answer in ra string báo "SYNTHESIS_ERROR...".

**Root cause:**
Hàm `tool_check_access_permission` không sanitize datatype đầu vào của tham số `access_level` (nó chờ int để móc data trong dictionary rules). Ở thiết kế MCP chuẩn, Server phải validate schema, còn worker chỉ là client. 

**Cách sửa:**
Tôi đã thêm khối `try/except TypeError` bên trong hàm bắt nguồn của MCP dispatch `dispatch_tool`, chặn và wrap thành JSON object để gửi về Worker. Bằng cách này pipeline trace vẫn chạy trơn tru, ghi nhận lỗi dưới dạng HTTP return để Agent xử lý thay vì crash process.

**Bằng chứng trước/sau:**
*Log lỗi (Trước khi sửa):*
```
TypeError: unhashable type: 'dict' or KeyError in tool_check_access_permission
Traceback sập hoàn toàn pipeline graph
```
*Đoạn tôi wrap vào JSON error response (Sau khi sửa):*
```python
# mcp_server.py - dispatch_tool function
    except TypeError as e:
        return {
            "error": f"Invalid input for tool '{tool_name}': {e}",
            "schema": TOOL_SCHEMAS[tool_name]["inputSchema"], 
        }
```
Nhờ đó `eval_trace` hiện ra `[policy_tool_worker] ERROR...` chứ không die worker.

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**
Tôi thiết lập thành công backend cấu trúc chuẩn như giao thức MCP (có Schema format xịn xò), chia object API gọn gàng và handle mock data rành mạch, có kèm luôn feature Web HTTP API (`--serve`) cho phép dễ debug ngoài luồng trên trình duyệt `http://localhost:8080/docs`.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Cách tôi làm mock tools chưa được tổng quát lắm theo dữ kiện thực thế. Bảng `MOCK_TICKETS` bị hardcode quá tĩnh, dẫn tới vài Grading Questions như gq09 bị fail một phần do không fetch được metadata mong đợi. Giao tiếp trả JSON của tui khiến team worker phải build logic parse dict khốn đốn mất khá lâu.

**Nhóm phụ thuộc vào tôi ở đâu?**
Các feature phức tạp như Check P1/Access/Quyền đều gọi vào layer Tools của tui `mcp_server.py`. Nếu tui ko cung cấp `TOOL_SCHEMAS`, worker không thể extract entity, graph ko chạy nổi.

**Phần tôi phụ thuộc vào thành viên khác:**
Tôi chỉ cung cấp tools thô, tui cần Đăng & Tuấn (worker owner) code đúng luồng Supervisor để gọi tới tool của tui. Nếu Supervisor mà route toàn vào "Retrieval" tui như người thừa. Thêm nữa tui cần trace owner làm chức năng log format Json để trace API calls của mình.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Nếu có 2h giờ, tôi sẽ cấu hình kết nối trực tiếp framework `mcp` chuẩn bằng Python library (Model Context Protocol open source của Anthropic) để sử dụng giao thức JSON-RPC của nó thay cho Mock In-Memory hiện tại. Trace qua file log cho thấy sự liên kết In-Process như hiện tại làm rối scope và không đại diện cho kiến trúc Client-Server thực tế khi scale hệ thống agent cho enterprise.  
