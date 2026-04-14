# Scorecard: baseline_dense
Generated: 2026-04-13 17:50

## Summary

| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.20/5 |
| Relevance | 4.60/5 |
| Context Recall | 5.00/5 |
| Completeness | 4.10/5 |

## Per-Question Results

| ID | Category | Faithful | Relevant | Recall | Complete | Sources |
|----|----------|----------|----------|--------|----------|---------|
| gq01 | SLA | 5 | 5 | 5 | 4 | support/sla-p1-2026.pdf |
| gq02 | Cross-Document | 5 | 5 | 5 | 4 | hr/leave-policy-2026.pdf, support/helpdesk-faq.md, it/access |
| gq03 | Refund | 5 | 5 | 5 | 4 | policy/refund-v4.pdf |
| gq04 | Refund | 5 | 5 | 5 | 5 | policy/refund-v4.pdf |
| gq05 | Access Control | 1 | 5 | 5 | 5 | it/access-control-sop.md |
| gq06 | Cross-Document | 5 | 5 | 5 | 5 | support/sla-p1-2026.pdf, it/access-control-sop.md |
| gq07 | Insufficient Context | 1 | 1 | None | 2 | support/sla-p1-2026.pdf, support/helpdesk-faq.md |
| gq08 | HR Policy | 5 | 5 | 5 | 4 | hr/leave-policy-2026.pdf, it/access-control-sop.md |
| gq09 | IT Helpdesk | 5 | 5 | 5 | 4 | support/helpdesk-faq.md, it/access-control-sop.md |
| gq10 | Refund | 5 | 5 | 5 | 4 | policy/refund-v4.pdf |

## Q&A Details

### [gq01] SLA xử lý ticket P1 đã thay đổi như thế nào so với phiên bản trước?

**Answer:** SLA xử lý ticket P1 đã thay đổi từ 6 giờ xuống 4 giờ trong phiên bản v2026.1 so với phiên bản trước đó [1].

**Expected:** Phiên bản hiện tại (v2026.1, có hiệu lực từ 2026-01-15) đã cập nhật SLA P1 resolution từ 6 giờ xuống còn 4 giờ. Phiên bản trước (v2025.3) không thay đổi SLA này.

**Sources:** support/sla-p1-2026.pdf

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the information from the retrieved chunk [1] regarding the change in SLA for ticket P1 from 6 hours to 4 hours in version v2026.1.
- Relevance: The answer directly addresses the change in SLA for P1 tickets, specifying the new time and comparing it to the previous version.
- Completeness: The model answer captures the main change in SLA but lacks details about the effective date and the previous version.

---

### [gq02] Khi làm việc remote, tôi phải dùng VPN và được kết nối trên tối đa bao nhiêu thiết bị?

**Answer:** Khi làm việc remote, bạn phải sử dụng VPN và được kết nối trên tối đa 2 thiết bị cùng lúc [1].

**Expected:** Khi làm việc remote và truy cập hệ thống nội bộ, VPN là bắt buộc (theo HR Leave Policy). Phần mềm VPN là Cisco AnyConnect và mỗi tài khoản được kết nối VPN trên tối đa 2 thiết bị cùng lúc (theo IT Helpdesk FAQ).

**Sources:** hr/leave-policy-2026.pdf, support/helpdesk-faq.md, it/access-control-sop.md

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the requirement to use VPN when working remotely and the limit of 2 devices, both of which are supported by the provided context.
- Relevance: Câu trả lời trực tiếp cung cấp thông tin về số lượng thiết bị tối đa có thể kết nối khi sử dụng VPN.
- Completeness: The model answer includes the requirement of using VPN and the limit of 2 devices, but it lacks the specific references to HR Leave Policy and IT Helpdesk FAQ.

---

### [gq03] Đơn hàng mua trong chương trình Flash Sale và đã kích hoạt sản phẩm có được hoàn tiền không?

**Answer:** Đơn hàng đã áp dụng mã giảm giá đặc biệt theo chương trình khuyến mãi Flash Sale và sản phẩm đã được kích hoạt sẽ không được hoàn tiền [1].

**Expected:** Không được hoàn tiền. Đơn hàng rơi vào hai ngoại lệ cùng lúc: (1) đơn hàng áp dụng mã giảm giá chương trình Flash Sale và (2) sản phẩm đã được kích hoạt — cả hai đều thuộc danh sách ngoại lệ không được hoàn tiền theo Điều 3 của chính sách.

**Sources:** policy/refund-v4.pdf

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the information provided in the retrieved chunks regarding the refund policy, specifically mentioning the exceptions for items that cannot be refunded.
- Relevance: The answer directly addresses the question about the refund policy for Flash Sale orders.
- Completeness: The model answer covers the main points but lacks the explicit mention of the two exceptions and the reference to Điều 3 of the policy.

---

### [gq04] Nếu chọn nhận store credit thay vì hoàn tiền, tôi được bao nhiêu phần trăm so với số tiền gốc?

**Answer:** Nếu chọn nhận store credit thay vì hoàn tiền, bạn sẽ nhận được 110% so với số tiền gốc [1].

**Expected:** Khách hàng có thể chọn nhận store credit (credit nội bộ) thay thế với giá trị 110% so với số tiền hoàn gốc. Đây là tùy chọn, không phải bắt buộc.

**Sources:** policy/refund-v4.pdf

**Scores:** F=5 | R=5 | Rc=5 | C=5

- Faithfulness: The answer accurately reflects the information from the retrieved chunk about receiving 110% store credit instead of a cash refund.
- Relevance: The answer directly addresses the question by stating the percentage of store credit received compared to the original amount.
- Completeness: The model answer fully covers the key points of the expected answer, including the percentage (110%) and the optional nature of the store credit.

---

### [gq05] Contractor từ bên ngoài công ty có thể được cấp quyền Admin Access không? Nếu có, cần bao nhiêu ngày và có yêu cầu đặc biệt gì?

**Answer:** Có, Contractor từ bên ngoài công ty có thể được cấp quyền Admin Access. Thời gian xử lý là 5 ngày làm việc và yêu cầu đặc biệt là phải hoàn thành training bắt buộc về security policy [2].

**Expected:** Có. Theo Access Control SOP, quy trình áp dụng cho tất cả nhân viên, contractor và third-party vendor. Admin Access (Level 4) cần phê duyệt từ IT Manager và CISO, thời gian xử lý 5 ngày làm việc, và có yêu cầu thêm: training bắt buộc về security policy.

**Sources:** it/access-control-sop.md

**Scores:** F=1 | R=5 | Rc=5 | C=5

- Faithfulness: The answer incorrectly states that external contractors can be granted Admin Access, which is not supported by the provided context.
- Relevance: The answer directly addresses the question about granting Admin Access to external contractors, including the processing time and special requirements.
- Completeness: Model answer covers all key points: approval from IT Manager and CISO, processing time of 5 working days, and mandatory training on security policy.

---

### [gq06] Lúc 2 giờ sáng xảy ra sự cố P1, on-call engineer cần cấp quyền tạm thời cho một engineer xử lý incident. Quy trình cụ thể như thế nào và quyền này tồn tại bao lâu?

**Answer:** Quy trình cấp quyền tạm thời cho engineer trong sự cố P1 như sau:

1. On-call IT Admin có thể cấp quyền tạm thời (tối đa 24 giờ) sau khi được Tech Lead phê duyệt bằng lời.
2. Sau 24 giờ, phải có ticket chính thức hoặc quyền sẽ bị thu hồi tự động.
3. Mọi quyền tạm thời phải được ghi log vào hệ thống Security Audit [1]. 

Quyền này tồn tại tối đa 24 giờ.

**Expected:** On-call IT Admin có thể cấp quyền tạm thời (tối đa 24 giờ) sau khi được Tech Lead phê duyệt bằng lời. Sau 24 giờ, phải có ticket chính thức hoặc quyền bị thu hồi tự động. Mọi quyền tạm thời phải được ghi log vào hệ thống Security Audit. Liên hệ on-call qua hotline ext. 9999 (24/7) theo SLA P1.

**Sources:** support/sla-p1-2026.pdf, it/access-control-sop.md

**Scores:** F=5 | R=5 | Rc=5 | C=5

- Faithfulness: The answer accurately reflects the escalation process for granting temporary access rights during a P1 incident as described in the retrieved chunk [1].
- Relevance: The answer directly addresses the process for granting temporary access and specifies the duration of the access.
- Completeness: Model answer covers all key points in the expected answer, including the approval process, duration of the temporary rights, logging requirements, and the need for a formal ticket.

---

### [gq07] Công ty sẽ phạt bao nhiêu nếu team IT vi phạm cam kết SLA P1?

**Answer:** Không đủ dữ liệu

**Expected:** Tài liệu hiện có không quy định mức phạt hay hình thức xử lý khi vi phạm SLA P1. Tài liệu sla-p1-2026.pdf chỉ mô tả quy trình xử lý và SLA target, không có điều khoản về penalty.

**Sources:** support/sla-p1-2026.pdf, support/helpdesk-faq.md

**Scores:** F=1 | R=1 | Rc=None | C=2

- Faithfulness: The answer 'Không đủ dữ liệu' does not address the questions about laptop issuance and reporting issues, which are clearly answered in the retrieved chunks.
- Relevance: The answer does not provide any information regarding the penalty for violating the SLA.
- Completeness: The model answer indicates a lack of data but does not address the specific details about the absence of penalty clauses or the content of the SLA document.

---

### [gq08] Nhân viên phải báo trước bao nhiêu ngày để xin nghỉ phép năm? Con số này có giống với số ngày cần giấy tờ khi nghỉ ốm không?

**Answer:** Nhân viên phải báo trước ít nhất 3 ngày làm việc để xin nghỉ phép năm [2]. Đối với nghỉ ốm, yêu cầu thông báo cho Line Manager trước 9:00 sáng ngày nghỉ, và nếu nghỉ trên 3 ngày liên tiếp thì cần giấy tờ y tế [1]. Do đó, số ngày báo trước để xin nghỉ phép năm không giống với số ngày cần giấy tờ khi nghỉ ốm.

**Expected:** Nghỉ phép năm cần báo trước ít nhất 3 ngày làm việc qua HR Portal. Nghỉ ốm cũng liên quan đến mốc 3 ngày: nếu nghỉ TRÊN 3 ngày liên tiếp thì cần giấy tờ y tế từ bệnh viện. Hai con số '3 ngày' này áp dụng cho hai tình huống khác nhau.

**Sources:** hr/leave-policy-2026.pdf, it/access-control-sop.md

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the information provided in the retrieved chunks regarding the notice period for annual leave and sick leave.
- Relevance: The answer directly addresses the question by providing the required notice period for annual leave and comparing it to the notice and documentation needed for sick leave.
- Completeness: The model answer covers the key points about the 3-day notice for annual leave and the requirement for medical documentation for sick leave over 3 days, but it lacks clarity on the similarity of the two '3-day' requirements.

---

### [gq09] Mật khẩu tài khoản công ty cần đổi định kỳ không? Nếu có, hệ thống sẽ nhắc nhở trước bao nhiêu ngày và đổi qua đâu?

**Answer:** Có, mật khẩu cần thay đổi định kỳ mỗi 90 ngày. Hệ thống sẽ nhắc nhở 7 ngày trước khi hết hạn [1].

**Expected:** Có. Mật khẩu phải được thay đổi mỗi 90 ngày. Hệ thống sẽ nhắc nhở 7 ngày trước khi hết hạn. Để đổi mật khẩu, truy cập https://sso.company.internal/reset hoặc liên hệ Helpdesk qua ext. 9000.

**Sources:** support/helpdesk-faq.md, it/access-control-sop.md

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the information provided in the retrieved chunk [1], stating that passwords must be changed every 90 days and that the system will remind users 7 days before expiration.
- Relevance: directly answers the question about password change frequency, reminder period, and process.
- Completeness: Covers most key points but misses the specific method for changing the password and the contact for Helpdesk.

---

### [gq10] Chính sách hoàn tiền hiện tại áp dụng cho đơn hàng đặt trước ngày 01/02/2026 không?

**Answer:** Chính sách hoàn tiền hiện tại không áp dụng cho đơn hàng đặt trước ngày 01/02/2026. Các đơn hàng đặt trước ngày này sẽ áp dụng theo chính sách hoàn tiền phiên bản 3 [1].

**Expected:** Không. Chính sách hoàn tiền phiên bản 4 có hiệu lực từ ngày 01/02/2026 và chỉ áp dụng cho các đơn hàng được đặt kể từ ngày đó. Các đơn hàng đặt trước ngày này sẽ áp dụng theo chính sách hoàn tiền phiên bản 3.

**Sources:** policy/refund-v4.pdf

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the information from the retrieved chunks, stating that the current refund policy does not apply to orders placed before 01/02/2026 and correctly references the previous version of the refund policy.
- Relevance: The answer directly addresses the question by stating that the current refund policy does not apply to orders placed before the specified date.
- Completeness: The model answer covers the main point about the refund policy not applying to orders before 01/02/2026 and mentions the application of version 3, but it lacks the detail about the effective date of version 4.

---

