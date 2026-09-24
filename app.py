"""The Whisperer — agentic creative-continuity demonstrator.

Runs two simulated music-production sessions to demonstrate:

observe → reconstruct previous context → decide → remember current intentions

No music or creative material is generated.
"""

import json
from pathlib import Path

from agent import WhispererAgent


MEMORY_FILE = "creative_memory.json"


def load_session(filename: str) -> list[dict]:
    """Load simulated DAW events from a JSON file."""

    path = Path(filename)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def print_response(
    session_name: str,
    response,
) -> None:
    """Display the agent's decision transparently."""

    print("\n" + "=" * 60)
    print(f"THE WHISPERER — {session_name}")
    print("=" * 60)

    print(f"\nAGENT STATE: {response.state}")
    print(f"INTERVENTION SCORE: {response.decision.score}")
    print(f"DECISION: {response.decision.reason}")

    if response.decision.evidence:
        print("\nEVIDENCE")

        for item in response.decision.evidence:
            print(f"  • {item}")

    if response.message:
        print("\nWHISPERER")
        print(response.message)

    if response.state == "SILENT":
        print(
            "\nWhisperer remains silent "
            "to preserve the artist's flow."
        )


def reset_demo_memory() -> None:
    """Start the demonstrator from a clean memory state."""

    path = Path(MEMORY_FILE)

    if path.exists():
        path.unlink()


def main() -> None:
    reset_demo_memory()

    agent = WhispererAgent(
        memory_path=MEMORY_FILE,
    )

    # SESSION 1
    #
    # The artist works normally. Whisperer observes the workflow
    # and stores explicit intentions, but should not interrupt merely
    # because repeated listening occurs.
    session_1 = load_session("demo/session_01.json")

    response_1 = agent.process(
        events=session_1,
        session_id="session_01",
    )

    print_response(
        "SESSION 1 — CREATIVE WORK",
        response_1,
    )

    # SESSION 2
    #
    # The artist returns later. Persistent memory from Session 1
    # now provides relevant unresolved context.
    session_2 = load_session("demo/session_02.json")

    response_2 = agent.process(
        events=session_2,
        session_id="session_02",
    )

    print_response(
        "SESSION 2 — PROJECT RE-ENTRY",
        response_2,
    )


if __name__ == "__main__":
    main()
