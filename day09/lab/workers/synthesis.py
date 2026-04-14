"""
workers/synthesis.py — Synthesis Worker
Sprint 2: Tổng hợp câu trả lời từ retrieved_chunks và policy_result.

Input (từ AgentState):
    - task: câu hỏi
    - retrieved_chunks: evidence từ retrieval_worker
    - policy_result: kết quả từ policy_tool_worker

Output (vào AgentState):
    - final_answer: câu trả lời cuối với citation
    - sources: danh sách nguồn tài liệu được cite
    - confidence: mức độ tin cậy (0.0 - 1.0)

Gọi độc lập để test:
    python workers/synthesis.py
"""

import os
import re

WORKER_NAME = "synthesis_worker"
ABSTAIN_TEXT = "Không đủ thông tin trong tài liệu nội bộ để trả lời chính xác câu hỏi này."

SYSTEM_PROMPT = """Bạn là trợ lý IT Helpdesk nội bộ.

Quy tắc nghiêm ngặt:
1. CHỈ trả lời dựa vào context được cung cấp. KHÔNG dùng kiến thức ngoài.
2. Nếu context không đủ để trả lời → nói rõ "Không đủ thông tin trong tài liệu nội bộ".
3. Trích dẫn nguồn cuối mỗi câu quan trọng: [tên_file].
4. Trả lời súc tích, có cấu trúc. Không dài dòng.
5. Nếu có exceptions/ngoại lệ → nêu rõ ràng trước khi kết luận.
"""


def _call_llm(messages: list) -> str:
    """
    Gọi LLM để tổng hợp câu trả lời.
    TODO Sprint 2: Implement với OpenAI hoặc Gemini.
    """
    # Option A: OpenAI
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.1,  # Low temperature để grounded
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception:
        pass

    # Option B: Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        combined = "\n".join([m["content"] for m in messages])
        response = model.generate_content(combined)
        return response.text
    except Exception:
        pass

    # Fallback: để tầng synthesize quyết định câu trả lời rule-based/abstain
    return ""


def _extract_sources(chunks: list, policy_result: dict) -> list:
    """Lấy danh sách source duy nhất từ chunks và policy_result."""
    sources = []
    for c in chunks:
        src = c.get("source", "unknown")
        if src and src not in sources:
            sources.append(src)
    for src in policy_result.get("source", []) if isinstance(policy_result, dict) else []:
        if src and src not in sources:
            sources.append(src)
    for ex in policy_result.get("exceptions_found", []) if isinstance(policy_result, dict) else []:
        ex_src = ex.get("source")
        if ex_src and ex_src not in sources:
            sources.append(ex_src)
    access_source = policy_result.get("access_check", {}).get("source") if isinstance(policy_result, dict) else None
    if access_source and access_source not in sources:
        sources.append(access_source)
    return sources


def _build_citation_suffix(sources: list) -> str:
    """Tạo hậu tố citation ổn định theo tên file source."""
    if not sources:
        return ""
    return " " + " ".join([f"[{s}]" for s in sources[:3]])


def _has_citation(answer: str) -> bool:
    return bool(re.search(r"\[[^\]]+\]", answer or ""))


def _safe_rule_based_answer(task: str, chunks: list, policy_result: dict, sources: list) -> str:
    """
    Fallback answer khi không gọi được LLM.
    Mục tiêu: grounded, ngắn gọn, có citation, không hallucinate.
    """
    if not chunks and not policy_result:
        return ABSTAIN_TEXT

    lines = []

    if policy_result:
        exceptions = policy_result.get("exceptions_found", [])
        policy_name = policy_result.get("policy_name")
        version_note = policy_result.get("policy_version_note")
        policy_applies = policy_result.get("policy_applies")

        if exceptions:
            lines.append("Có ngoại lệ policy cần ưu tiên trước khi kết luận:")
            for ex in exceptions[:3]:
                if ex.get("rule"):
                    lines.append(f"- {ex.get('rule')}")

        if policy_applies is True:
            lines.append("Theo context hiện có, policy cho phép xử lý yêu cầu.")
        elif policy_applies is False:
            lines.append("Theo context hiện có, policy không cho phép xử lý yêu cầu.")

        if policy_name:
            lines.append(f"Policy được tham chiếu: {policy_name}.")
        if version_note:
            lines.append(version_note)

        access_check = policy_result.get("access_check", {})
        if isinstance(access_check, dict) and access_check:
            can_grant = access_check.get("can_grant")
            approvers = access_check.get("required_approvers", [])
            notes = access_check.get("notes", [])
            if can_grant is not None:
                lines.append(f"Kết quả kiểm tra quyền: can_grant={can_grant}.")
            if approvers:
                lines.append("Phê duyệt yêu cầu: " + ", ".join(approvers) + ".")
            if notes:
                lines.append("Lưu ý: " + " ".join([str(n) for n in notes if n]) + ".")

    if chunks:
        top = sorted(chunks, key=lambda c: c.get("score", 0), reverse=True)[0]
        top_text = (top.get("text", "") or "").strip().replace("\n", " ")
        if top_text:
            snippet = top_text[:220] + ("..." if len(top_text) > 220 else "")
            lines.append(f"Bằng chứng nổi bật từ tài liệu: {snippet}")

    if not lines:
        return ABSTAIN_TEXT

    answer = "\n".join(lines)
    if not _has_citation(answer):
        answer += _build_citation_suffix(sources)
    return answer


def _build_context(chunks: list, policy_result: dict) -> str:
    """Xây dựng context string từ chunks và policy result."""
    parts = []

    if chunks:
        parts.append("=== TÀI LIỆU THAM KHẢO ===")
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("source", "unknown")
            text = chunk.get("text", "")
            score = chunk.get("score", 0)
            parts.append(f"[{i}] Nguồn: {source} (relevance: {score:.2f})\n{text}")

    if policy_result and policy_result.get("exceptions_found"):
        parts.append("\n=== POLICY EXCEPTIONS ===")
        for ex in policy_result["exceptions_found"]:
            parts.append(f"- {ex.get('rule', '')}")

    if policy_result and policy_result.get("policy_name"):
        parts.append("\n=== POLICY SUMMARY ===")
        parts.append(f"policy_name: {policy_result.get('policy_name')}")
        parts.append(f"policy_applies: {policy_result.get('policy_applies')}")
        if policy_result.get("policy_version_note"):
            parts.append(f"policy_version_note: {policy_result.get('policy_version_note')}")

    access_check = policy_result.get("access_check", {}) if isinstance(policy_result, dict) else {}
    if access_check:
        parts.append("\n=== ACCESS CHECK ===")
        parts.append(f"can_grant: {access_check.get('can_grant')}")
        parts.append(f"required_approvers: {access_check.get('required_approvers', [])}")
        parts.append(f"emergency_override: {access_check.get('emergency_override')}")
        if access_check.get("notes"):
            parts.append(f"notes: {access_check.get('notes')}")

    if not parts:
        return "(Không có context)"

    return "\n\n".join(parts)


def _estimate_confidence(chunks: list, answer: str, policy_result: dict) -> float:
    """
    Ước tính confidence dựa vào:
    - Số lượng và quality của chunks
    - Có exceptions không
    - Answer có abstain không

    TODO Sprint 2: Có thể dùng LLM-as-Judge để tính confidence chính xác hơn.
    """
    if not chunks:
        # Không có retrieval evidence: confidence rất thấp trừ khi policy_result có dữ liệu mạnh
        if policy_result and (policy_result.get("exceptions_found") or policy_result.get("access_check")):
            return 0.35
        return 0.1

    if "Không đủ thông tin" in answer or "không có trong tài liệu" in answer.lower():
        return 0.3  # Abstain → moderate-low

    # Weighted average của chunk scores
    if chunks:
        avg_score = sum(c.get("score", 0) for c in chunks) / len(chunks)
    else:
        avg_score = 0

    # Penalty nếu có exceptions (phức tạp hơn)
    exception_penalty = 0.05 * len(policy_result.get("exceptions_found", []))

    policy_bonus = 0.03 if policy_result and policy_result.get("policy_applies") is not None else 0.0
    citation_penalty = 0.08 if chunks and not _has_citation(answer) else 0.0

    confidence = min(0.95, avg_score - exception_penalty + policy_bonus - citation_penalty)
    return round(max(0.1, confidence), 2)


def synthesize(task: str, chunks: list, policy_result: dict) -> dict:
    """
    Tổng hợp câu trả lời từ chunks và policy context.

    Returns:
        {"answer": str, "sources": list, "confidence": float}
    """
    sources = _extract_sources(chunks, policy_result)

    # Contract: Nếu không có chunks thì phải abstain để tránh hallucination.
    if not chunks:
        if policy_result and (policy_result.get("exceptions_found") or policy_result.get("policy_name") or policy_result.get("access_check")):
            answer = _safe_rule_based_answer(task, chunks, policy_result, sources)
            if not _has_citation(answer):
                answer = answer + _build_citation_suffix(sources)
        else:
            answer = ABSTAIN_TEXT
        confidence = _estimate_confidence(chunks, answer, policy_result)
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
        }

    context = _build_context(chunks, policy_result)

    # Build messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""Câu hỏi: {task}

{context}

Hãy trả lời câu hỏi dựa vào tài liệu trên."""
        }
    ]

    answer = _call_llm(messages).strip()
    if not answer:
        answer = _safe_rule_based_answer(task, chunks, policy_result, sources)

    if chunks and not _has_citation(answer):
        answer = answer.rstrip() + _build_citation_suffix(sources)

    confidence = _estimate_confidence(chunks, answer, policy_result)

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
    }


def run(state: dict) -> dict:
    """
    Worker entry point — gọi từ graph.py.
    """
    task = state.get("task", "")
    chunks = state.get("retrieved_chunks", [])
    policy_result = state.get("policy_result", {})

    state.setdefault("workers_called", [])
    state.setdefault("history", [])
    state["workers_called"].append(WORKER_NAME)

    worker_io = {
        "worker": WORKER_NAME,
        "input": {
            "task": task,
            "chunks_count": len(chunks),
            "has_policy": bool(policy_result),
        },
        "output": None,
        "error": None,
    }

    try:
        result = synthesize(task, chunks, policy_result)
        state["final_answer"] = result["answer"]
        state["sources"] = result["sources"]
        state["confidence"] = result["confidence"]

        if result["confidence"] < 0.4:
            state["hitl_triggered"] = True
            state["history"].append(
                f"[{WORKER_NAME}] low confidence={result['confidence']} -> hitl_triggered=True"
            )

        worker_io["output"] = {
            "answer_length": len(result["answer"]),
            "sources": result["sources"],
            "confidence": result["confidence"],
            "has_citation": _has_citation(result["answer"]),
            "abstained": "Không đủ thông tin" in result["answer"],
            "policy_context_used": bool(policy_result),
        }
        state["history"].append(
            f"[{WORKER_NAME}] answer generated, confidence={result['confidence']}, "
            f"sources={result['sources']}"
        )

    except Exception as e:
        worker_io["error"] = {"code": "SYNTHESIS_FAILED", "reason": str(e)}
        state["final_answer"] = f"SYNTHESIS_ERROR: {e}"
        state["confidence"] = 0.0
        state["history"].append(f"[{WORKER_NAME}] ERROR: {e}")

    state.setdefault("worker_io_logs", []).append(worker_io)
    return state


# ─────────────────────────────────────────────
# Test độc lập
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("Synthesis Worker — Standalone Test")
    print("=" * 50)

    test_state = {
        "task": "SLA ticket P1 là bao lâu?",
        "retrieved_chunks": [
            {
                "text": "Ticket P1: Phản hồi ban đầu 15 phút kể từ khi ticket được tạo. Xử lý và khắc phục 4 giờ. Escalation: tự động escalate lên Senior Engineer nếu không có phản hồi trong 10 phút.",
                "source": "sla_p1_2026.txt",
                "score": 0.92,
            }
        ],
        "policy_result": {},
    }

    result = run(test_state.copy())
    print(f"\nAnswer:\n{result['final_answer']}")
    print(f"\nSources: {result['sources']}")
    print(f"Confidence: {result['confidence']}")

    print("\n--- Test 2: Exception case ---")
    test_state2 = {
        "task": "Khách hàng Flash Sale yêu cầu hoàn tiền vì lỗi nhà sản xuất.",
        "retrieved_chunks": [
            {
                "text": "Ngoại lệ: Đơn hàng Flash Sale không được hoàn tiền theo Điều 3 chính sách v4.",
                "source": "policy_refund_v4.txt",
                "score": 0.88,
            }
        ],
        "policy_result": {
            "policy_applies": False,
            "exceptions_found": [{"type": "flash_sale_exception", "rule": "Flash Sale không được hoàn tiền."}],
        },
    }
    result2 = run(test_state2.copy())
    print(f"\nAnswer:\n{result2['final_answer']}")
    print(f"Confidence: {result2['confidence']}")

    print("\n✅ synthesis_worker test done.")
