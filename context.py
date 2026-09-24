"""Context reconstruction for The Whisperer.

Combines current workflow signals with persistent creative memory so the
agent can understand the relationship between the present session and
earlier artist intentions or unresolved creative threads.
"""

from dataclasses import dataclass, field

from memory import CreativeMemory, MemoryStore
from observer import WorkflowSignal


@dataclass
class CreativeContext:
    """Current reconstructed creative context."""

    current_signals: list[WorkflowSignal] = field(default_factory=list)
    active_memories: list[CreativeMemory] = field(default_factory=list)
    unresolved_memories: list[CreativeMemory] = field(default_factory=list)

    session_reentry: bool = False
    repetition_detected: bool = False
    active_exploration: bool = False

    related_memories: list[CreativeMemory] = field(default_factory=list)


class ContextBuilder:
    """Build contextual state from observation and longitudinal memory."""

    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    def build(
        self,
        signals: list[WorkflowSignal],
    ) -> CreativeContext:

        active = self.memory_store.active_memories()
        unresolved = self.memory_store.unresolved_memories()

        session_reentry = any(
            signal.signal_type == "session_reentry"
            for signal in signals
        )

        repetition = any(
            signal.signal_type == "repetition"
            for signal in signals
        )

        # Repetition alone is not treated as a problem.
        # In the absence of unresolved context, it can simply indicate
        # that the artist is actively exploring material.
        active_exploration = repetition and not unresolved

        related = self._find_related_memories(
            signals,
            active + unresolved,
        )

        return CreativeContext(
            current_signals=signals,
            active_memories=active,
            unresolved_memories=unresolved,
            session_reentry=session_reentry,
            repetition_detected=repetition,
            active_exploration=active_exploration,
            related_memories=related,
        )

    def _find_related_memories(
        self,
        signals: list[WorkflowSignal],
        memories: list[CreativeMemory],
    ) -> list[CreativeMemory]:
        """Find memories related to subjects active in the current session."""

        current_subjects = {
            signal.subject.lower()
            for signal in signals
            if signal.subject
        }

        related: list[CreativeMemory] = []

        for memory in memories:
            subject = memory.subject.lower()

            if subject in current_subjects:
                related.append(memory)
                continue

            # Allow simple partial subject matching for the demonstrator.
            if any(
                subject in current_subject
                or current_subject in subject
                for current_subject in current_subjects
            ):
                related.append(memory)

        return self._deduplicate(related)

    @staticmethod
    def _deduplicate(
        memories: list[CreativeMemory],
    ) -> list[CreativeMemory]:
        """Remove duplicate memories while preserving their order."""

        seen: set[str] = set()
        result: list[CreativeMemory] = []

        for memory in memories:
            if memory.memory_id not in seen:
                seen.add(memory.memory_id)
                result.append(memory)

        return result
