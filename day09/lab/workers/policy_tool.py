"""
workers/policy_tool.py — Policy & Tool Worker
Sprint 2+3: Kiểm tra policy dựa vào context, gọi MCP tools khi cần.

Input (từ AgentState):
    - task: câu hỏi
    - retrieved_chunks: context từ retrieval_worker
    - needs_tool: True nếu supervisor quyết định cần tool call

Output (vào AgentState):
    - policy_result: {"policy_applies", "policy_name", "exceptions_found", "source", "rule"}
    - mcp_tools_used: list of tool calls đã thực hiện
    - worker_io_log: log

Gọi độc lập để test:
    python workers/policy_tool.py
"""

import os
import sys
import re
from typing import Optional
from datetime import datetime, date, timedelta

WORKER_NAME = "policy_tool_worker"

## Vu Hai Dang - 2A202600339
# ─────────────────────────────────────────────
# MCP Client — Sprint 3: Thay bằng real MCP call
# ─────────────────────────────────────────────

def _call_mcp_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Gọi MCP tool.

    Sprint 3 TODO: Implement bằng cách import mcp_server hoặc gọi HTTP.

    Hiện tại: Import trực tiếp từ mcp_server.py (trong-process mock).
    """
    from datetime import datetime

    try:
        # TODO Sprint 3: Thay bằng real MCP client nếu dùng HTTP server
        from mcp_server import dispatch_tool
        result = dispatch_tool(tool_name, tool_input)
        return {
            "tool": tool_name,
            "input": tool_input,
            "output": result,
            "error": None,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "tool": tool_name,
            "input": tool_input,
            "output": None,
            "error": {"code": "MCP_CALL_FAILED", "reason": str(e)},
            "timestamp": datetime.now().isoformat(),
        }


# ─────────────────────────────────────────────
# Policy Analysis Logic
# ─────────────────────────────────────────────

def analyze_policy(task: str, chunks: list) -> dict:
    """
    Phân tích policy dựa trên context chunks.

    TODO Sprint 2: Implement logic này với LLM call hoặc rule-based check.

    Cần xử lý các exceptions:
    - Flash Sale → không được hoàn tiền
    - Digital product / license key / subscription → không được hoàn tiền
    - Sản phẩm đã kích hoạt → không được hoàn tiền
    - Đơn hàng trước 01/02/2026 → áp dụng policy v3 (không có trong docs)

    Returns:
        dict with: policy_applies, policy_name, exceptions_found, source, rule, explanation
    """
    task_lower = task.lower()
    context_text = " ".join([c.get("text", "") for c in chunks]).lower()

    # Helper: parse dates from text (dd/mm[/yyyy], yyyy-mm-dd, dd-mm, etc.)
    def _parse_dates(text: str):
        parsed = []
        if not text:
            return parsed
        # dd/mm/yyyy or d/m/yy
        for m in re.finditer(r"\b([0-3]?\d)[/\\-]([0-1]?\d)[/\\-]([0-9]{2,4})\b", text):
            d, mo, y = m.groups()
            try:
                yy = int(y)
                if yy < 100:
                    yy += 2000
                parsed.append(date(yy, int(mo), int(d)))
            except Exception:
                continue
        # yyyy-mm-dd
        for m in re.finditer(r"\b([0-9]{4})[/\\-]([0-1]?\d)[/\\-]([0-3]?\d)\b", text):
            y, mo, d = m.groups()
            try:
                parsed.append(date(int(y), int(mo), int(d)))
            except Exception:
                continue
        # dd/mm or dd-mm (assume current year)
        for m in re.finditer(r"\b([0-3]?\d)[/\\-]([0-1]?\d)\b", text):
            d, mo = m.groups()
            try:
                yy = datetime.now().year
                parsed.append(date(yy, int(mo), int(d)))
            except Exception:
                continue
        # remove duplicates and sort
        parsed = sorted(set(parsed))
        return parsed

    def _extract_within_days(text: str) -> Optional[int]:
        if not text:
            return None
        m = re.search(r"(?:trong|within)\s*(\d{1,2})\s*(?:ngày|days?)", text)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass
        # fallback: any standalone "X ngày" mention
        m2 = re.search(r"\b(\d{1,2})\s*(?:ngày|days?)\b", text)
        if m2:
            try:
                return int(m2.group(1))
            except Exception:
                pass
        return None

    # --- Rule-based exception detection ---
    exceptions_found = []

    # Flash sale / promotion exceptions
    flash_keywords = ["flash sale", "flash-sale", "mã giảm giá", "khuyến mãi", "flashsale"]
    if any(k in task_lower or k in context_text for k in flash_keywords):
        exceptions_found.append({
            "type": "flash_sale_exception",
            "rule": "Đơn hàng Flash Sale không được hoàn tiền (Điều 3, chính sách v4).",
            "source": "policy_refund_v4.txt",
        })

    # Digital product exceptions
    digital_keywords = ["license key", "license", "subscription", "kỹ thuật số", "digital", "license-key"]
    if any(k in task_lower or k in context_text for k in digital_keywords):
        exceptions_found.append({
            "type": "digital_product_exception",
            "rule": "Sản phẩm kỹ thuật số (license key, subscription) không được hoàn tiền (Điều 3).",
            "source": "policy_refund_v4.txt",
        })

    # Activated / registered product exceptions (avoid false positive on negation: "chưa kích hoạt")
    combined_text = f"{task_lower} {context_text}"
    has_negative_activation = bool(re.search(
        r"\b(chưa|không)\s*(kích\s*hoạt|đăng\s*ký)\b|\b(not\s+(activated|registered)|unactivated|unregistered)\b",
        combined_text,
    ))
    has_positive_activation = bool(re.search(
        r"\bđã\s*(kích\s*hoạt|đăng\s*ký)\b|\b(activated|registered)\b",
        combined_text,
    ))
    if has_positive_activation and not has_negative_activation:
        exceptions_found.append({
            "type": "activated_exception",
            "rule": "Sản phẩm đã kích hoạt hoặc đăng ký tài khoản không được hoàn tiền (Điều 3).",
            "source": "policy_refund_v4.txt",
        })

    # --- Evidence extraction for refundable conditions ---
    # 1) product defect evidence
    defect_keywords = ["lỗi", "bị lỗi", "defect", "hỏng", "không hoạt động", "broken", "not working"]
    product_defect = any(k in task_lower or k in context_text for k in defect_keywords)

    # 2) timeframe evidence (within X days OR explicit order date)
    within_days_mentioned = _extract_within_days(task_lower + " " + context_text)
    parsed_dates = _parse_dates(task + " " + " ".join([c.get("text", "") for c in chunks]))
    order_dates = parsed_dates

    within_7_days = None
    if within_days_mentioned is not None:
        within_7_days = within_days_mentioned <= 7
    elif order_dates:
        # Use earliest mentioned order date as candidate
        now_date = datetime.now().date()
        try:
            delta_days = (now_date - min(order_dates)).days
            within_7_days = delta_days <= 7
        except Exception:
            within_7_days = None

    # 3) unused / unopened evidence
    unused_keywords = ["chưa sử dụng", "chưa dùng", "chưa mở seal", "chưa mở", "unused", "unopened"]
    unused_evidence = any(k in task_lower or k in context_text for k in unused_keywords)

    # Determine policy_applies conservatively: require no exceptions AND evidence for refund conditions
    missing_conditions = []
    if not product_defect:
        missing_conditions.append("no_defect_evidence")
    if within_7_days is False:
        missing_conditions.append("outside_timeframe")
    elif within_7_days is None:
        missing_conditions.append("no_timeframe_evidence")
    if not unused_evidence:
        missing_conditions.append("no_unused_evidence")

    policy_name = "refund_policy_v4"
    policy_version_note = ""
    # Detect orders placed before 01/02/2026 -> use policy v3
    cutoff = date(2026, 2, 1)
    order_before_2026_02_01 = False
    if order_dates and any(d < cutoff for d in order_dates):
        order_before_2026_02_01 = True
    # also check textual hints like "trước 01/02" without explicit year
    if re.search(r"trước\s*0?1[/\-]0?2|trc\s*01/02|before\s*01[/\-]02", task_lower + " " + context_text):
        order_before_2026_02_01 = True

    if order_before_2026_02_01:
        policy_name = "refund_policy_v3"
        policy_version_note = "Đơn hàng đặt trước 01/02/2026 áp dụng chính sách v3 (tài liệu hiện tại khác)."

    policy_applies = len(exceptions_found) == 0 and len(missing_conditions) == 0
    # TODO Sprint 2: Gọi LLM để phân tích phức tạp hơn
    # Ví dụ:
    # from openai import OpenAI
    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": "Bạn là policy analyst. Dựa vào context, xác định policy áp dụng và các exceptions."},
    #         {"role": "user", "content": f"Task: {task}\n\nContext:\n" + "\n".join([c['text'] for c in chunks])}
    #     ]
    # )
    # analysis = response.choices[0].message.content

    sources = list({c.get("source", "unknown") for c in chunks if c})

    explanation_parts = ["Rule-based analysis."]
    if exceptions_found:
        explanation_parts.append(f"Found {len(exceptions_found)} exception(s).")
    if missing_conditions:
        explanation_parts.append(f"Missing evidence: {', '.join(missing_conditions)}.")
    else:
        explanation_parts.append("All refund conditions evidenced in context.")

    return {
        "policy_applies": policy_applies,
        "policy_name": policy_name,
        "exceptions_found": exceptions_found,
        "source": sources,
        "policy_version_note": policy_version_note,
        "explanation": " ".join(explanation_parts),
        "evidence": {
            "product_defect": product_defect,
            "within_7_days": within_7_days,
            "unused_evidence": unused_evidence,
            "missing_conditions": missing_conditions,
            "order_dates": [d.isoformat() for d in order_dates],
            "order_before_2026_02_01": order_before_2026_02_01,
        },
    }


# ─────────────────────────────────────────────
# Worker Entry Point
# ─────────────────────────────────────────────

def run(state: dict) -> dict:
    """
    Worker entry point — gọi từ graph.py.

    Args:
        state: AgentState dict

    Returns:
        Updated AgentState với policy_result và mcp_tools_used
    """
    task = state.get("task", "")
    chunks = state.get("retrieved_chunks", [])
    needs_tool = state.get("needs_tool", False)

    state.setdefault("workers_called", [])
    state.setdefault("history", [])
    state.setdefault("mcp_tools_used", [])

    state["workers_called"].append(WORKER_NAME)

    worker_io = {
        "worker": WORKER_NAME,
        "input": {
            "task": task,
            "chunks_count": len(chunks),
            "needs_tool": needs_tool,
        },
        "output": None,
        "error": None,
    }

    try:
        # Step 1: Nếu chưa có chunks, gọi MCP search_kb
        if not chunks and needs_tool:
            mcp_result = _call_mcp_tool("search_kb", {"query": task, "top_k": 3})
            state["mcp_tools_used"].append(mcp_result)
            state["history"].append(f"[{WORKER_NAME}] called MCP search_kb")

            if mcp_result.get("output") and mcp_result["output"].get("chunks"):
                chunks = mcp_result["output"]["chunks"]
                state["retrieved_chunks"] = chunks

        # Step 2: Phân tích policy
        policy_result = analyze_policy(task, chunks)
        state["policy_result"] = policy_result

        # Step 3: Nếu cần thêm info từ MCP (e.g., ticket status), gọi get_ticket_info
        if needs_tool and any(kw in task.lower() for kw in ["ticket", "p1", "jira"]):
            # Try to extract ticket id from task, fallback to P1-LATEST
            ticket_match = re.search(r"([A-Za-z]+-?\d+|P1-LATEST)", task, re.IGNORECASE)
            ticket_id = ticket_match.group(1) if ticket_match else "P1-LATEST"
            mcp_result = _call_mcp_tool("get_ticket_info", {"ticket_id": ticket_id})
            state["mcp_tools_used"].append(mcp_result)
            state["history"].append(f"[{WORKER_NAME}] called MCP get_ticket_info -> {ticket_id}")

        # Step 4: Nếu yêu cầu liên quan đến cấp quyền, gọi check_access_permission
        access_keywords = ["cấp quyền", "access", "level", "cấp quyền level"]
        if needs_tool and any(kw in task.lower() for kw in access_keywords):
            # Parse access level
            access_level = None
            lvl_match = re.search(r"level\s*([1-3])", task, re.IGNORECASE)
            if not lvl_match:
                lvl_match = re.search(r"cấp quyền\s*([1-3])", task, re.IGNORECASE)
            if lvl_match:
                try:
                    access_level = int(lvl_match.group(1))
                except Exception:
                    access_level = None

            requester_role = "requester"
            if "contractor" in task.lower() or "nhà thầu" in task.lower():
                requester_role = "contractor"
            if "senior" in task.lower() or "senior" in task.lower():
                requester_role = "senior"

            is_emergency = any(k in task.lower() for k in ["khẩn cấp", "emergency", "urgent", "gấp"]) 

            if access_level is None:
                # default to highest requested level if not specified
                access_level = 3

            mcp_result = _call_mcp_tool("check_access_permission", {
                "access_level": access_level,
                "requester_role": requester_role,
                "is_emergency": bool(is_emergency),
            })
            state["mcp_tools_used"].append(mcp_result)
            state["history"].append(f"[{WORKER_NAME}] called MCP check_access_permission -> level {access_level}")

            # Attach access check output into policy_result for synthesis
            try:
                state.setdefault("policy_result", {})
                state["policy_result"]["access_check"] = mcp_result.get("output")
            except Exception:
                pass

        # richer output for supervisor + synthesis
        mcp_tools_summary = [mc.get("tool") for mc in state.get("mcp_tools_used", [])]
        worker_io["output"] = {
            "policy_applies": policy_result.get("policy_applies"),
            "policy_name": policy_result.get("policy_name"),
            "policy_version_note": policy_result.get("policy_version_note"),
            "exceptions": [ex.get("type") for ex in policy_result.get("exceptions_found", [])],
            "exceptions_count": len(policy_result.get("exceptions_found", [])),
            "evidence_summary": {
                "product_defect": policy_result.get("evidence", {}).get("product_defect"),
                "within_7_days": policy_result.get("evidence", {}).get("within_7_days"),
                "unused_evidence": policy_result.get("evidence", {}).get("unused_evidence"),
            },
            "mcp_calls": len(state.get("mcp_tools_used", [])),
            "mcp_tools": mcp_tools_summary,
            "retrieved_chunks_count": len(chunks),
            "sources": list({c.get("source", "unknown") for c in chunks}),
        }
        state["history"].append(
            f"[{WORKER_NAME}] policy_applies={policy_result.get('policy_applies')}, "
            f"exceptions={len(policy_result.get('exceptions_found', []))}, mcp_calls={len(state.get('mcp_tools_used', []))}"
        )

    except Exception as e:
        worker_io["error"] = {"code": "POLICY_CHECK_FAILED", "reason": str(e)}
        state["policy_result"] = {"error": str(e)}
        state["history"].append(f"[{WORKER_NAME}] ERROR: {e}")

    state.setdefault("worker_io_logs", []).append(worker_io)
    return state


# ─────────────────────────────────────────────
# Test độc lập
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("Policy Tool Worker — Standalone Test")
    print("=" * 50)

    test_cases = [
        {
            "task": "Khách hàng Flash Sale yêu cầu hoàn tiền vì sản phẩm lỗi — được không?",
            "retrieved_chunks": [
                {"text": "Ngoại lệ: Đơn hàng Flash Sale không được hoàn tiền.", "source": "policy_refund_v4.txt", "score": 0.9}
            ],
        },
        {
            "task": "Khách hàng muốn hoàn tiền license key đã kích hoạt.",
            "retrieved_chunks": [
                {"text": "Sản phẩm kỹ thuật số (license key, subscription) không được hoàn tiền.", "source": "policy_refund_v4.txt", "score": 0.88}
            ],
        },
        {
            "task": "Khách hàng yêu cầu hoàn tiền trong 5 ngày, sản phẩm lỗi, chưa kích hoạt.",
            "retrieved_chunks": [
                {"text": "Yêu cầu trong 7 ngày làm việc, sản phẩm lỗi nhà sản xuất, chưa dùng.", "source": "policy_refund_v4.txt", "score": 0.85}
            ],
        },
    ]

    for tc in test_cases:
        print(f"\n▶ Task: {tc['task'][:70]}...")
        result = run(tc.copy())
        pr = result.get("policy_result", {})
        print(f"  policy_applies: {pr.get('policy_applies')}")
        if pr.get("exceptions_found"):
            for ex in pr["exceptions_found"]:
                print(f"  exception: {ex['type']} — {ex['rule'][:60]}...")
        print(f"  MCP calls: {len(result.get('mcp_tools_used', []))}")

    print("\n✅ policy_tool_worker test done.")
