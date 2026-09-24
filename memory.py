"""Persistent creative memory for The Whisperer.

The memory layer stores artist intentions, decisions, rationale and
unresolved creative threads across working sessions.

It deliberately models more than DAW state: The Whisperer should remember
why a creative decision mattered, not merely that a parameter changed.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import json


@dataclass
class CreativeMemory:
    """A single meaningful piece of creative context."""

    memory_id: str
    category: str
    subject: str
    intention: str
    rationale: Optional[str] = None
    status: str = "active"
    source_session: Optional[str] = None


class MemoryStore:
    """Small persistent memory store for the demonstrator."""

    def __init__(self, path: str = "creative_memory.json"):
        self.path = Path(path)
        self.memories: list[CreativeMemory] = []
        self.load()

    def add(self, memory: CreativeMemory) -> None:
        """Add or replace a memory with the same ID."""

        self.memories = [
            item for item in self.memories
            if item.memory_id != memory.memory_id
        ]

        self.memories.append(memory)
        self.save()

    def active_memories(self) -> list[CreativeMemory]:
        """Return memories that still matter to the current project."""

        return [
            memory for memory in self.memories
            if memory.status == "active"
        ]

    def unresolved_memories(self) -> list[CreativeMemory]:
        """Return unresolved creative intentions."""

        return [
            memory for memory in self.memories
            if memory.status == "unresolved"
        ]

    def resolve(self, memory_id: str) -> bool:
        """Mark an existing memory as resolved."""

        for memory in self.memories:
            if memory.memory_id == memory_id:
                memory.status = "resolved"
                self.save()
                return True

        return False

    def save(self) -> None:
        """Persist memory between sessions."""

        data = [asdict(memory) for memory in self.memories]

        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def load(self) -> None:
        """Restore memory created during previous sessions."""

        if not self.path.exists():
            return

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.memories = [
            CreativeMemory(**item)
            for item in data
        ]
