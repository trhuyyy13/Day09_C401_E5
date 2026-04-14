# Scorecard: variant_hybrid
Generated: 2026-04-13 17:51

## Summary

| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.60/5 |
| Relevance | 4.60/5 |
| Context Recall | 5.00/5 |
| Completeness | 3.90/5 |

## Per-Question Results

| ID | Category | Faithful | Relevant | Recall | Complete | Sources |
|----|----------|----------|----------|--------|----------|---------|
| gq01 | SLA | 5 | 5 | 5 | 4 | support/sla-p1-2026.pdf |
| gq02 | Cross-Document | 5 | 5 | 5 | 4 | hr/leave-policy-2026.pdf, support/helpdesk-faq.md |
| gq03 | Refund | 5 | 5 | 5 | 5 | policy/refund-v4.pdf |
| gq04 | Refund | 5 | 5 | 5 | 5 | policy/refund-v4.pdf |
| gq05 | Access Control | 5 | 5 | 5 | 2 | it/access-control-sop.md |
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

- Faithfulness: The answer accurately reflects the information from the retrieved chunks, specifically noting the change in SLA for ticket P1 from 6 hours to 4 hours in version v2026.1.
- Relevance: The answer directly addresses the change in SLA for P1 tickets, specifying the new time and comparing it to the previous version.
- Completeness: The model answer captures the key change in SLA from 6 hours to 4 hours and mentions the current version, but it lacks the effective date and does not specify that the previous version did not change the SLA.

---

### [gq02] Khi làm việc remote, tôi phải dùng VPN và được kết nối trên tối đa bao nhiêu thiết bị?

**Answer:** Khi làm việc remote, bạn phải sử dụng VPN và được kết nối trên tối đa 2 thiết bị cùng lúc [1].

**Expected:** Khi làm việc remote và truy cập hệ thống nội bộ, VPN là bắt buộc (theo HR Leave Policy). Phần mềm VPN là Cisco AnyConnect và mỗi tài khoản được kết nối VPN trên tối đa 2 thiết bị cùng lúc (theo IT Helpdesk FAQ).

**Sources:** hr/leave-policy-2026.pdf, support/helpdesk-faq.md

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the information provided in the retrieved chunks regarding the requirement to use VPN while working remotely and the limit of 2 devices.
- Relevance: The answer directly addresses the question about the maximum number of devices that can be connected using VPN while working remotely.
- Completeness: The model answer includes the requirement of using VPN and the limit of 2 devices, but it lacks the mention of the HR Leave Policy and the specific software used (Cisco AnyConnect).

---

### [gq03] Đơn hàng mua trong chương trình Flash Sale và đã kích hoạt sản phẩm có được hoàn tiền không?

**Answer:** Đơn hàng mua trong chương trình Flash Sale và đã kích hoạt sản phẩm sẽ không được hoàn tiền, vì đơn hàng đã áp dụng mã giảm giá đặc biệt theo chương trình khuyến mãi Flash Sale và sản phẩm đã được kích hoạt [1].

**Expected:** Không được hoàn tiền. Đơn hàng rơi vào hai ngoại lệ cùng lúc: (1) đơn hàng áp dụng mã giảm giá chương trình Flash Sale và (2) sản phẩm đã được kích hoạt — cả hai đều thuộc danh sách ngoại lệ không được hoàn tiền theo Điều 3 của chính sách.

**Sources:** policy/refund-v4.pdf

**Scores:** F=5 | R=5 | Rc=5 | C=5

- Faithfulness: The answer accurately reflects the conditions for refunds as stated in the retrieved chunks, specifically mentioning the exceptions for Flash Sale orders and activated products.
- Relevance: The answer directly addresses the question about the refund policy for Flash Sale orders and explains why refunds are not applicable.
- Completeness: The model answer covers all key points in the expected answer, including the reasons for not being eligible for a refund.

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

**Answer:** Có, contractor từ bên ngoài công ty có thể được cấp quyền Admin Access. Quy trình yêu cầu cấp quyền bao gồm việc tạo Access Request ticket trên Jira, phê duyệt của Line Manager trong 1 ngày làm việc, và kiểm tra compliance bởi IT Admin. Sau đó, IT Security sẽ thực hiện review [1]. Không có yêu cầu đặc biệt nào được nêu rõ trong context.

**Expected:** Có. Theo Access Control SOP, quy trình áp dụng cho tất cả nhân viên, contractor và third-party vendor. Admin Access (Level 4) cần phê duyệt từ IT Manager và CISO, thời gian xử lý 5 ngày làm việc, và có yêu cầu thêm: training bắt buộc về security policy.

**Sources:** it/access-control-sop.md

**Scores:** F=5 | R=5 | Rc=5 | C=2

- Faithfulness: The answer accurately reflects the information provided in the retrieved chunks, specifically regarding the process for granting access to contractors and the steps involved.
- Relevance: The answer directly addresses the question about granting Admin Access to external contractors, including the process and timeline.
- Completeness: The model answer mentions the possibility of granting Admin Access to contractors but deviates from the expected process and requirements, missing key points like the need for approval from IT Manager and CISO, the specific processing time, and the mandatory training on security policy.

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

- Faithfulness: The answer accurately summarizes the escalation process for granting temporary permissions during a P1 incident as described in the retrieved chunks.
- Relevance: The answer directly addresses the process for granting temporary access and specifies the duration of the access.
- Completeness: The model answer covers all key points in the expected answer, including the approval process, duration of the temporary rights, logging requirements, and the automatic revocation after 24 hours.

---

### [gq07] Công ty sẽ phạt bao nhiêu nếu team IT vi phạm cam kết SLA P1?

**Answer:** Không đủ dữ liệu

**Expected:** Tài liệu hiện có không quy định mức phạt hay hình thức xử lý khi vi phạm SLA P1. Tài liệu sla-p1-2026.pdf chỉ mô tả quy trình xử lý và SLA target, không có điều khoản về penalty.

**Sources:** support/sla-p1-2026.pdf, support/helpdesk-faq.md

**Scores:** F=1 | R=1 | Rc=None | C=2

- Faithfulness: The answer 'Không đủ dữ liệu' does not relate to any of the provided chunks, which contain specific information about laptops, accounts, and incident handling.
- Relevance: The answer does not provide any information regarding the penalty amount for violating the SLA.
- Completeness: The model answer indicates a lack of data but does not address the specific details about the absence of penalty clauses in the SLA documentation.

---

### [gq08] Nhân viên phải báo trước bao nhiêu ngày để xin nghỉ phép năm? Con số này có giống với số ngày cần giấy tờ khi nghỉ ốm không?

**Answer:** Nhân viên phải báo trước ít nhất 3 ngày làm việc để xin nghỉ phép năm [2]. Số ngày này không giống với số ngày cần giấy tờ khi nghỉ ốm, vì nghỉ ốm yêu cầu thông báo trước 9:00 sáng ngày nghỉ và cần giấy tờ y tế nếu nghỉ trên 3 ngày liên tiếp [1].

**Expected:** Nghỉ phép năm cần báo trước ít nhất 3 ngày làm việc qua HR Portal. Nghỉ ốm cũng liên quan đến mốc 3 ngày: nếu nghỉ TRÊN 3 ngày liên tiếp thì cần giấy tờ y tế từ bệnh viện. Hai con số '3 ngày' này áp dụng cho hai tình huống khác nhau.

**Sources:** hr/leave-policy-2026.pdf, it/access-control-sop.md

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the information provided in the retrieved chunks regarding the notice period for annual leave and the requirements for sick leave.
- Relevance: The answer directly addresses both parts of the question regarding the notice period for annual leave and the requirements for sick leave.
- Completeness: The model answer covers the key points about the 3-day notice for annual leave and the requirement for medical documentation for sick leave over 3 days, but it does not explicitly mention that both '3 days' apply to different situations.

---

### [gq09] Mật khẩu tài khoản công ty cần đổi định kỳ không? Nếu có, hệ thống sẽ nhắc nhở trước bao nhiêu ngày và đổi qua đâu?

**Answer:** Có, mật khẩu cần thay đổi định kỳ mỗi 90 ngày. Hệ thống sẽ nhắc nhở 7 ngày trước khi hết hạn [1].

**Expected:** Có. Mật khẩu phải được thay đổi mỗi 90 ngày. Hệ thống sẽ nhắc nhở 7 ngày trước khi hết hạn. Để đổi mật khẩu, truy cập https://sso.company.internal/reset hoặc liên hệ Helpdesk qua ext. 9000.

**Sources:** support/helpdesk-faq.md, it/access-control-sop.md

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the information provided in the retrieved chunk about password change requirements.
- Relevance: The answer directly addresses both parts of the question regarding password change frequency and reminder system.
- Completeness: The model answer covers the key points about the password change frequency and reminder period but misses the specific link for password reset and the contact for Helpdesk.

---

### [gq10] Chính sách hoàn tiền hiện tại áp dụng cho đơn hàng đặt trước ngày 01/02/2026 không?

**Answer:** Chính sách hoàn tiền hiện tại không áp dụng cho đơn hàng đặt trước ngày 01/02/2026. Các đơn hàng đặt trước ngày này sẽ áp dụng theo chính sách hoàn tiền phiên bản 3 [1].

**Expected:** Không. Chính sách hoàn tiền phiên bản 4 có hiệu lực từ ngày 01/02/2026 và chỉ áp dụng cho các đơn hàng được đặt kể từ ngày đó. Các đơn hàng đặt trước ngày này sẽ áp dụng theo chính sách hoàn tiền phiên bản 3.

**Sources:** policy/refund-v4.pdf

**Scores:** F=5 | R=5 | Rc=5 | C=4

- Faithfulness: The answer accurately reflects the information from the retrieved chunks, stating that the current refund policy does not apply to orders placed before 01/02/2026 and correctly references the previous version of the refund policy.
- Relevance: The answer directly addresses the question about the refund policy for orders placed before 01/02/2026.
- Completeness: The model answer covers the main point about the refund policy not applying to orders before 01/02/2026 and mentions the application of version 3, but it lacks the detail about the effective date of version 4.

---

