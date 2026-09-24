"""Agent orchestration for The Whisperer.

Coordinates observation, persistent creative memory, context
reconstruction and selective intervention.

The agent does not generate creative material. Its purpose is to
preserve continuity and decide whether contextual support is useful.
"""

from dataclasses import dataclass
from typing import Optional

from observer import SessionObserver, WorkflowSignal
from memory import CreativeMemory, MemoryStore
from context import CreativeContext, ContextBuilder
from intervention import InterventionDecision, InterventionPolicy


@dataclass
class AgentResponse:
    """Observable result of one Whisperer processing cycle."""

    state: str
    message: Optional[str]
    decision: InterventionDecision
    context: CreativeContext


class WhispererAgent:
    """Agentic creative-continuity system."""

    def __init__(
        self,
        memory_path: str = "creative_memory.json",
    ):
        self.memory = MemoryStore(memory_path)
        self.observer = SessionObserver()
        self.context_builder = ContextBuilder(self.memory)
        self.policy = InterventionPolicy()

    def process(
        self,
        events: list[dict],
        session_id: str,
    ) -> AgentResponse:
        """Process one set of session events."""

        signals = self.observer.observe(events)

        # Explicit artist intentions are privileged over inferred behaviour.
        self._remember_explicit_intentions(
            signals,
            session_id,
        )

        context = self.context_builder.build(signals)
        decision = self.policy.evaluate(context)

        if decision.should_intervene:
            message = self._build_continuity_message(context)

            return AgentResponse(
                state="INTERVENE",
                message=message,
                decision=decision,
                context=context,
            )

        return AgentResponse(
            state="SILENT",
            message=None,
            decision=decision,
            context=context,
        )

    def _remember_explicit_intentions(
        self,
        signals: list[WorkflowSignal],
        session_id: str,
    ) -> None:
        """Convert explicit artist notes into persistent memory."""

        existing_ids = {
            memory.memory_id
            for memory in self.memory.memories
        }

        note_number = len(existing_ids) + 1

        for signal in signals:
            if signal.signal_type != "explicit_intention":
                continue

            status = signal.metadata.get(
                "status",
                "active",
            )

            memory_id = (
                f"{session_id}-intention-{note_number}"
            )

            while memory_id in existing_ids:
                note_number += 1
                memory_id = (
                    f"{session_id}-intention-{note_number}"
                )

            memory = CreativeMemory(
                memory_id=memory_id,
                category="artist_intention",
                subject=signal.subject,
                intention=signal.metadata.get(
                    "text",
                    "",
                ),
                rationale="Explicit artist note",
                status=status,
                source_session=session_id,
            )

            self.memory.add(memory)

            existing_ids.add(memory_id)
            note_number += 1

    def _build_continuity_message(
        self,
        context: CreativeContext,
    ) -> str:
        """Construct a factual continuity cue from stored artist context."""

        memories = (
            context.related_memories
            or context.unresolved_memories
        )

        if not memories:
            return (
                "Relevant creative context is available "
                "from the previous session."
            )

        unresolved = [
            memory
            for memory in memories
            if memory.status == "unresolved"
        ]

        selected = unresolved or memories

        lines = [
            "Previous creative context:",
        ]

        for memory in selected[:3]:
            lines.append(
                f"- {memory.subject}: "
                f"{memory.intention}"
            )

        lines.append("")
        lines.append(
            "Resume from this context?"
        )

        return "\n".join(lines)

    def resolve_memory(
        self,
        memory_id: str,
    ) -> bool:
        """Allow the artist to mark a creative thread as resolved."""

        return self.memory.resolve(memory_id)
