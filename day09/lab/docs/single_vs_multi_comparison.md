# Single Agent vs Multi-Agent Comparison — Lab Day 09

**Nhóm:** Day09_C401_E5  
**Ngày:** 2026-04-14

Nguồn số liệu đã dùng:
- Day 08: `day08/lab/results/scorecard_baseline.md`, `day08/lab/results/scorecard_baseline.json`
- Day 09: 3 trace thực tế trong `day09/lab/artifacts/traces/`

---

## 1. Metrics Comparison

| Metric | Day 08 (Single Agent) | Day 09 (Multi-Agent) | Delta | Ghi chú |
|--------|----------------------|---------------------|-------|---------|
| Avg confidence | 4.20 (faithfulness proxy) | 0.10 | -4.10 | Day 09 đang lỗi LLM/API key nên confidence rất thấp |
| Avg latency (ms) | N/A | 22,353 | N/A | Day 08 không có latency metric trong scorecard |
| Abstain rate (%) | 1/10 (10.0%) | 0/3 (0.0%) | -10.0% | Day 09 chưa có câu trả lời chuẩn vì synthesis error |
| Multi-hop accuracy | 2/2 (100.0%) | N/A | N/A | Day 09 chưa có bộ trace đủ để chấm đúng/sai theo expected answer |
| Routing visibility | ✗ Không có route_reason | ✓ Có route_reason | Cải thiện | Debug theo route rõ ràng |
| MCP usage rate | N/A | 2/3 (66.7%) | N/A | 2 trace có gọi MCP tools |

---

## 2. Phân tích theo loại câu hỏi

### 2.1 Câu hỏi đơn giản (single-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Cao (đa số Faithfulness/Relevance = 5) | Thấp trong 3 trace hiện tại |
| Latency | N/A | 10,967–43,857 ms |
| Observation | Trả lời grounded khá ổn định | Route đúng worker nhưng synthesis lỗi do LLM/API |

**Kết luận:** Multi-agent chưa cải thiện accuracy ở bộ trace hiện có vì đang bị chặn bởi lỗi hạ tầng LLM, không phải do routing.

### 2.2 Câu hỏi multi-hop (cross-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | 2/2 trong nhóm câu Cross-Document (theo scorecard baseline) | N/A (chưa có grading tương ứng cho trace hiện tại) |
| Routing visible? | ✗ | ✓ |
| Observation | Có thể trả lời đúng nhưng khó thấy pipeline quyết định thế nào | Có `supervisor_route`, `route_reason`, `workers_called`, `mcp_tools_used` |

**Kết luận:** Day 09 vượt trội ở khả năng quan sát pipeline multi-hop, nhưng cần sửa synthesis để chuyển lợi thế debug thành lợi thế chất lượng đầu ra.

### 2.3 Câu hỏi cần abstain

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Abstain rate | 10.0% (1/10) | 0.0% (0/3) |
| Hallucination cases | Có 1 câu đánh giá thấp (gq07) | Chưa kết luận (3 trace đều trả về synthesis error) |
| Observation | Có khả năng abstain nhưng chất lượng diễn giải chưa tốt | Chưa đánh giá đúng năng lực abstain thật do lỗi LLM |

**Kết luận:** Chưa thể kết luận Day 09 tốt hơn ở abstain cho đến khi hết lỗi synthesis.

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
Thời gian ước tính để khoanh vùng 1 lỗi: 5-8 phút.
```

**Case debug thực tế:** Trace cho thấy route đúng nhưng `final_answer` luôn là `[SYNTHESIS ERROR] Không thể gọi LLM...`, giúp xác định nhanh root cause nằm ở cấu hình API/key thay vì routing logic.

---

## 4. Extensibility Analysis

| Scenario | Day 08 | Day 09 |
|---------|--------|--------|
| Thêm 1 tool/API mới | Chạm trực tiếp vào RAG flow | Thêm MCP tool và cập nhật route rule |
| Thêm 1 domain mới | Dễ đụng chéo prompt/retrieval | Có thể thêm worker theo domain |
| Thay đổi retrieval strategy | Chỉnh trực tiếp pipeline chính | Chỉnh độc lập trong `retrieval_worker` |
| A/B test một phần | Khó tách biệt thành phần | Dễ hơn vì worker tách module |

**Nhận xét:** Day 09 có cấu trúc mở rộng tốt hơn rõ rệt nhờ ranh giới worker + trace chuẩn.

---

## 5. Cost & Latency Trade-off

| Scenario | Day 08 calls | Day 09 calls |
|---------|-------------|-------------|
| Simple query | 1 LLM call | 1 synthesis call + route overhead |
| Complex query | 1 LLM call | 1 synthesis call + (0-2) MCP calls + route overhead |
| MCP tool call | N/A | Có (2/3 trace hiện tại) |

**Nhận xét về cost-benefit:** Multi-agent tăng orchestration overhead nhưng đổi lại có khả năng quan sát và mở rộng tốt hơn. Khi hệ thống ổn định API key, cần đo lại cost/latency trên cùng bộ 10 grading questions để kết luận định lượng cuối cùng.

---

## 6. Kết luận

**Multi-agent tốt hơn single-agent ở:**

1. Debuggability: trace theo route/worker rõ ràng, khoanh vùng lỗi nhanh hơn.
2. Extensibility: thêm tool qua MCP và thêm worker mà không phá toàn pipeline.

**Multi-agent kém hơn hoặc chưa chứng minh tốt hơn ở:**

1. Hiệu năng đầu ra thực tế trong run hiện tại do lỗi synthesis (LLM/API key), khiến confidence và answer quality giảm mạnh.

**Khi nào không nên dùng multi-agent?**

Khi bài toán rất đơn giản, không cần tool orchestration, và ưu tiên latency thấp cùng implementation tối giản.

**Nếu tiếp tục phát triển hệ thống này, nhóm sẽ thêm gì?**

1. Health-check bắt buộc cho LLM/API key trước khi chạy batch.
2. Fallback answer khi synthesis lỗi (ví dụ trả lời từ evidence đã retrieve thay vì fail cứng).
3. Bộ đánh giá auto cho routing accuracy trên cùng tập grading của Day 08.
