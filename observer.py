"""Observation layer for The Whisperer.

Transforms low-level session events into meaningful workflow signals.

The observer does not decide whether to interrupt the artist.
Its job is only to describe what appears to be happening.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowSignal:
    """A meaningful signal inferred from session activity."""

    signal_type: str
    subject: str
    strength: float
    evidence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SessionObserver:
    """Observe session events and identify workflow patterns."""

    def observe(self, events: list[dict]) -> list[WorkflowSignal]:
        signals: list[WorkflowSignal] = []

        signals.extend(self._detect_repetition(events))
        signals.extend(self._detect_explicit_intentions(events))
        signals.extend(self._detect_session_reentry(events))

        return signals

    def _detect_repetition(
        self,
        events: list[dict]
    ) -> list[WorkflowSignal]:

        counts: dict[str, int] = {}

        for event in events:
            if event.get("type") == "region_playback":
                subject = event.get("subject", "unknown")
                counts[subject] = counts.get(subject, 0) + 1

        signals = []

        for subject, count in counts.items():
            if count >= 4:
                signals.append(
                    WorkflowSignal(
                        signal_type="repetition",
                        subject=subject,
                        strength=min(count / 10, 1.0),
                        evidence=[
                            f"{subject} reviewed {count} times"
                        ],
                        metadata={"count": count},
                    )
                )

        return signals

    def _detect_explicit_intentions(
        self,
        events: list[dict]
    ) -> list[WorkflowSignal]:

        signals = []

        for event in events:
            if event.get("type") == "artist_note":
                signals.append(
                    WorkflowSignal(
                        signal_type="explicit_intention",
                        subject=event.get("subject", "session"),
                        strength=1.0,
                        evidence=[event.get("text", "")],
                        metadata={
                            "text": event.get("text", ""),
                            "status": event.get(
                                "status",
                                "active"
                            ),
                        },
                    )
                )

        return signals

    def _detect_session_reentry(
        self,
        events: list[dict]
    ) -> list[WorkflowSignal]:

        for event in events:
            if event.get("type") == "session_opened":
                return [
                    WorkflowSignal(
                        signal_type="session_reentry",
                        subject=event.get(
                            "project",
                            "current_project"
                        ),
                        strength=1.0,
                        evidence=["Project session reopened"],
                    )
                ]

        return []
