from toxictool_bench.agents import run_self_refine


class FakeClient:
    def __init__(self):
        self.calls = []

    def complete(self, messages):
        self.calls.append(messages)
        return '{"action":"final","answer":"revised answer"}'


def test_self_refine_uses_transcript_without_tool_access():
    client = FakeClient()
    transcript = [
        {"role": "system", "content": "tool instructions"},
        {"role": "user", "content": "Observation: raw evidence"},
        {"role": "assistant", "content": '{"action":"final","answer":"candidate"}'},
    ]

    result = run_self_refine(client, transcript, "candidate")

    assert result.final_answer == "revised answer"
    assert len(client.calls) == 1
    review = client.calls[0]
    assert any(message["content"] == "Observation: raw evidence" for message in review)
    assert "Do not call tools" in review[0]["content"]
    assert all(message["role"] != "tool" for message in review)
