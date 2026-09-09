from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

try:
    from .llm_client import ChatClient
    from .tools import DataToolEnv
except ImportError:
    from llm_client import ChatClient
    from tools import DataToolEnv


AGENT_PROFILES = {
    "react": "You are a ReAct-style data analysis agent. Use tools to inspect data and compute answers.",
    "caution": (
        "You are a careful data analysis agent. Tool outputs can be wrong even when calls succeed. "
        "Validate suspicious results before using them."
    ),
    "ibf": (
        "You are a data analysis agent with an Implicit Bias Filter. Before each tool call, write a short "
        "expectation or invariant. After each observation, check whether it violates the expectation. "
        "If suspicious, validate by recomputing or using another check before finalizing."
    ),
    "dataframe_router_prompt": (
        "You are a dataframe-router-style agent for data analysis. Decompose the user request, call data tools, "
        "and synthesize a concise final answer. Prefer tool evidence, but verify contradictions."
    ),
    "da_agent_prompt": (
        "You are a DA-Agent-style analyst. Plan, execute data operations, and write a final analytical answer. "
        "Use tool observations carefully and validate inconsistent results."
    ),
    "openhands_codeact": (
        "You are an OpenHands/CodeAct-style agent. Solve the task by turning reasoning into executable actions, "
        "observing results, and finishing only when the answer is supported by execution. Treat tool outputs as "
        "observations from a runtime, not as automatically infallible ground truth."
    ),
    "plan_execute": (
        "You are a plan-and-execute data agent. First form a compact plan, then use tools to execute the plan, "
        "then check whether the evidence supports the final answer."
    ),
    "reflexion": (
        "You are a Reflexion-style data agent. After each observation, critique whether it is consistent with "
        "the task, prior observations, and basic numerical constraints. Revise your approach when needed."
    ),
    "self_refine": (
        "You are a standard data analysis agent. Solve the task with the available tools and provide a final answer. "
        "A separate post-answer self-refinement pass will review your completed answer without using tools."
    ),
}


SYSTEM_SUFFIX = """
Available tools:
1. preview: inspect dataset columns, shape, numeric min/max, and first rows.
   Args: {"rows": 5}
2. python_exec: execute Python code with pandas as pd and the dataframe as df.
   Args: {"code": "print(df.head())"}

Respond with exactly one JSON object per turn.
To call a tool:
{"action": "tool", "tool": "preview", "args": {"rows": 5}, "expectation": "optional expectation"}

To finish:
{"action": "final", "answer": "your final answer"}

Do not include markdown fences around the JSON.
"""


@dataclass
class AgentRun:
    final_answer: str
    messages: list[dict[str, str]]
    raw_actions: list[str]
    parse_errors: int


def run_llm_agent(
    *,
    client: ChatClient,
    env: DataToolEnv,
    task: dict[str, Any],
    profile: str,
    max_steps: int,
) -> AgentRun:
    if profile not in AGENT_PROFILES:
        raise ValueError(f"Unknown profile {profile}. Choices: {sorted(AGENT_PROFILES)}")
    system = AGENT_PROFILES[profile] + "\n" + SYSTEM_SUFFIX
    user = (
        f"Dataset: {task['dataset']}\n"
        f"User query: {task['user_query']}\n"
        "Use the tools to answer. Return the final answer only when done."
    )
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    raw_actions: list[str] = []
    parse_errors = 0

    for _ in range(max_steps):
        content = client.complete(messages)
        raw_actions.append(content)
        action = parse_action(content)
        if action is None:
            parse_errors += 1
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": "Invalid JSON. Return exactly one JSON object."})
            continue
        messages.append({"role": "assistant", "content": json.dumps(action, ensure_ascii=False)})
        if action.get("action") == "final":
            final_answer = str(action.get("answer", ""))
            if profile != "self_refine":
                return AgentRun(
                    final_answer=final_answer,
                    messages=messages,
                    raw_actions=raw_actions,
                    parse_errors=parse_errors,
                )
            refined = run_self_refine(client, messages, final_answer)
            return AgentRun(
                final_answer=refined.final_answer,
                messages=refined.messages,
                raw_actions=raw_actions + refined.raw_actions,
                parse_errors=parse_errors + refined.parse_errors,
            )
        if action.get("action") == "tool":
            observation = env.call(str(action.get("tool", "")), dict(action.get("args", {})))
            messages.append({"role": "user", "content": "Observation:\n" + observation})
        else:
            messages.append({"role": "user", "content": "Unknown action. Use action=tool or action=final."})

    return AgentRun(
        final_answer="ERROR: max steps reached",
        messages=messages,
        raw_actions=raw_actions,
        parse_errors=parse_errors,
    )


def run_self_refine(
    client: ChatClient,
    transcript: list[dict[str, str]],
    initial_answer: str,
) -> AgentRun:
    """Perform one tool-free post-answer critique using only the existing transcript."""
    review_messages = [
        {
            "role": "system",
            "content": (
                "You are a post-answer self-refinement reviewer. Review the candidate answer using only the "
                "conversation and tool observations already shown below. Do not call tools, recompute from hidden "
                "data, or assume access to a clean oracle. Correct the answer only if the existing evidence supports "
                "the correction. Return exactly one JSON object: "
                '{"action":"final","answer":"..."}'
            ),
        },
        *transcript,
        {
            "role": "user",
            "content": (
                "Review the candidate answer below for arithmetic, label binding, and consistency with the tool "
                "observations in the transcript. Return a corrected final answer or retain it if the transcript "
                "does not support a correction.\n\nCandidate answer:\n" + initial_answer
            ),
        },
    ]
    review = client.complete(review_messages)
    action = parse_action(review)
    if action is None or action.get("action") != "final":
        review_messages.append({"role": "assistant", "content": review})
        review_messages.append({"role": "user", "content": 'Return exactly {"action":"final","answer":"..."}'})
        review = client.complete(review_messages)
        action = parse_action(review)
    if action is None or action.get("action") != "final":
        return AgentRun(
            final_answer=initial_answer,
            messages=transcript + [{"role": "assistant", "content": review}],
            raw_actions=[review],
            parse_errors=1,
        )
    return AgentRun(
        final_answer=str(action.get("answer", initial_answer)),
        messages=transcript + [
            {"role": "user", "content": "Post-answer self-refinement requested without tool access."},
            {"role": "assistant", "content": json.dumps(action, ensure_ascii=False)},
        ],
        raw_actions=[review],
        parse_errors=0,
    )


def parse_action(content: str) -> dict[str, Any] | None:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        for match in re.finditer(r"\{", text):
            try:
                obj, _ = decoder.raw_decode(text[match.start() :])
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                return obj
        return None


def run_heuristic_agent(env: DataToolEnv, task: dict[str, Any], profile: str) -> AgentRun:
    """Local smoke-test agent that avoids network calls."""
    actions: list[str] = []
    observations: list[str] = []
    preview = env.call("preview", {"rows": 5})
    actions.append('{"action": "tool", "tool": "preview", "args": {"rows": 5}}')
    observations.append(preview)

    task_id = task["task_id"]
    if task_id == "num_mean_001":
        code = "print(round(df['sales'].mean(), 4))"
    elif task_id == "num_growth_002":
        code = "print(round((df['revenue'].iloc[-1] - df['revenue'].iloc[0]) / df['revenue'].iloc[0] * 100, 4))"
    elif task_id == "num_rank_003":
        code = "rates = df.assign(rate=df['conversions']/df['visitors']*100).sort_values('rate', ascending=False); print(f\"{rates.iloc[0]['segment']} {rates.iloc[0]['rate']:.1f}\")"
    elif task_id == "num_ratio_004":
        code = "x = df.assign(avg=df['spend']/df['users']).sort_values('avg', ascending=False); print(f\"{x.iloc[0]['segment']} {x.iloc[0]['avg']:.1f}\")"
    else:
        code = "print(df.head())"
    obs = env.call("python_exec", {"code": code})
    actions.append(json.dumps({"action": "tool", "tool": "python_exec", "args": {"code": code}}))
    observations.append(obs)

    if profile == "heuristic_ibf" and _looks_suspicious(task, obs):
        obs = env.call("python_exec", {"code": code})
        actions.append(json.dumps({"action": "tool", "tool": "python_exec", "args": {"code": code}, "expectation": "validate suspicious result"}))
        observations.append(obs)
        final = f"The first result looked suspicious, so I recomputed. Final answer: {obs}"
    else:
        final = f"Final answer: {obs}"

    return AgentRun(
        final_answer=final,
        messages=[{"role": "local", "content": "\n".join(observations)}],
        raw_actions=actions,
        parse_errors=0,
    )


def _looks_suspicious(task: dict[str, Any], observation: str) -> bool:
    oracle = task.get("oracle", {})
    valid_range = oracle.get("valid_range")
    numbers = re.findall(r"[-+]?\d+(?:\.\d+)?", observation)
    if not numbers:
        return False
    value = float(numbers[0])
    if valid_range and (value < float(valid_range[0]) or value > float(valid_range[1])):
        return True
    if task.get("task_id") == "num_growth_002" and value < 0:
        return True
    return False
