# Single Agent vs Multi-Agent Comparison — Lab Day 09

**Nhóm:** Day09_C401_E5  
**Ngày:** 2026-04-14

Nguồn số liệu đã dùng:
- Day 08: `day08/lab/results/scorecard_baseline.md`, `day08/lab/results/scorecard_baseline.json`
- Day 09: 18 trace thực tế trong `day09/lab/artifacts/traces/`

---

## 1. Metrics Comparison

| Metric | Day 08 (Single Agent) | Day 09 (Multi-Agent) | Delta | Ghi chú |
|--------|----------------------|---------------------|-------|---------|
| Avg confidence | 4.20 (faithfulness proxy) | 0.631 | N/A (khác thang đo) | Day 08 là faithfulness proxy 1–5, Day 09 là confidence 0–1 |
| Avg latency (ms) | N/A | 7,679 | N/A | Day 08 không có latency metric trong scorecard |
| Abstain rate (%) | 1/10 (10.0%) | 5/18 (27.8%) | +17.8% | Day 09 hiện abstain nhiều hơn, do HITL + synthesis fallback |
| Multi-hop accuracy | 2/2 (100.0%) | N/A | N/A | Day 09 chưa có bộ trace đủ để chấm đúng/sai theo expected answer |
| Routing visibility | ✗ Không có route_reason | ✓ Có route_reason | Cải thiện | Debug theo route rõ ràng |
| MCP usage rate | N/A | 9/18 (50.0%) | N/A | 9 trace có gọi MCP tools |
| HITL rate | N/A | 5/18 (27.8%) | N/A | Có HITL khi confidence thấp |

---

## 2. Phân tích theo loại câu hỏi

### 2.1 Câu hỏi đơn giản (single-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Cao (đa số Faithfulness/Relevance = 5) | Đã trả lời được trên trace mới; confidence trung bình 0.631 |
| Latency | N/A | 2,555–20,225 ms cho các trace đã kiểm tra |
| Observation | Trả lời grounded khá ổn định | Route đúng worker, retrieval/policy context lấy được evidence thật |

**Kết luận:** Multi-agent hiện đã chạy ổn hơn so với trace lỗi trước đó; lợi thế chính vẫn là trace rõ ràng và khả năng gọi MCP theo từng loại task.

### 2.2 Câu hỏi multi-hop (cross-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | 2/2 trong nhóm câu Cross-Document (theo scorecard baseline) | Có trace multi-hop/knowledge khác nhau nhưng chưa có ground-truth để chấm |
| Routing visible? | ✗ | ✓ |
| Observation | Có thể trả lời đúng nhưng khó thấy pipeline quyết định thế nào | Có `supervisor_route`, `route_reason`, `workers_called`, `mcp_tools_used` và HITL |

**Kết luận:** Day 09 vượt trội ở khả năng quan sát pipeline multi-hop và policy/access path, đặc biệt khi cần xác định worker nào đã xử lý từng phần.

### 2.3 Câu hỏi cần abstain

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Abstain rate | 10.0% (1/10) | 27.8% (5/18) |
| Hallucination cases | Có 1 câu đánh giá thấp (gq07) | Ít hơn do pipeline ưu tiên abstain/HITL khi confidence thấp |
| Observation | Có khả năng abstain nhưng chất lượng diễn giải chưa tốt | Absent answer hiện được kiểm soát tốt hơn bằng HITL |

**Kết luận:** Day 09 hiện nghiêng về an toàn hơn ở các case mơ hồ nhờ HITL và abstain rõ hơn.

---

## 3. Debuggability Analysis

### Day 08 — Debug workflow
```
Khi answer sai -> phải đọc lại pipeline RAG end-to-end (retrieve + generate).
Không có route-level trace nên khó khoanh vùng nhanh lỗi do retrieval hay generation.
Thời gian ước tính để khoanh vùng 1 lỗi: 15-20 phút.
```

### Day 09 — Debug workflow
```
Khi answer sai -> mở trace -> xem supervisor_route + route_reason + workers_called.
Nếu route sai thì sửa supervisor, nếu retrieval rỗng thì test retrieval_worker,
nếu answer lỗi thì kiểm tra synthesis_worker/LLM config.
Thời gian ước tính để khoanh vùng 1 lỗi: 5-10 phút.
```

**Case debug thực tế:** Trace mới cho thấy route đúng, retrieval/policy lấy được evidence thật, và synthesis có thể trả lời với confidence 0.81. Khi cần debug, nhìn trace là thấy ngay task đi qua worker nào và dùng source nào.

---

## 4. Extensibility Analysis

| Scenario | Day 08 | Day 09 |
|---------|--------|--------|
| Thêm 1 tool/API mới | Chạm trực tiếp vào RAG flow | Thêm MCP tool và cập nhật route rule |
| Thêm 1 domain mới | Dễ đụng chéo prompt/retrieval | Có thể thêm worker theo domain |
| Thay đổi retrieval strategy | Chỉnh trực tiếp pipeline chính | Chỉnh độc lập trong `retrieval_worker` |
| A/B test một phần | Khó tách biệt thành phần | Dễ hơn vì worker tách module |

**Nhận xét:** Day 09 có cấu trúc mở rộng tốt hơn rõ rệt nhờ ranh giới worker + trace chuẩn, và trace mới cho thấy MCP được gọi đúng theo loại task.

---

## 5. Cost & Latency Trade-off

| Scenario | Day 08 calls | Day 09 calls |
|---------|-------------|-------------|
| Simple query | 1 LLM call | 1 synthesis call + route overhead |
| Complex query | 1 LLM call | 1 synthesis call + (0-3) MCP calls + route overhead |
| MCP tool call | N/A | Có (9/18 trace hiện tại) |

**Nhận xét về cost-benefit:** Multi-agent tăng orchestration overhead nhưng đổi lại có khả năng quan sát và mở rộng tốt hơn. Khi hệ thống ổn định API key, cần đo lại cost/latency trên cùng bộ 10 grading questions để kết luận định lượng cuối cùng.

---

## 6. Kết luận

**Multi-agent tốt hơn single-agent ở:**

1. Debuggability: trace theo route/worker rõ ràng, khoanh vùng lỗi nhanh hơn.
2. Extensibility: thêm tool qua MCP và thêm worker mà không phá toàn pipeline.

**Multi-agent kém hơn hoặc chưa chứng minh tốt hơn ở:**

1. Latency và orchestration overhead vẫn cao hơn single-agent nếu chỉ xử lý query đơn giản.

**Khi nào không nên dùng multi-agent?**

Khi bài toán rất đơn giản, không cần tool orchestration, và ưu tiên latency thấp cùng implementation tối giản.

**Nếu tiếp tục phát triển hệ thống này, nhóm sẽ thêm gì?**

1. Health-check bắt buộc cho LLM/API key trước khi chạy batch.
2. Tối ưu policy worker để giảm số bước MCP khi câu hỏi chỉ cần access check đơn giản.
3. Bộ đánh giá auto cho routing accuracy trên cùng tập grading của Day 08.
