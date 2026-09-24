"""Intervention policy for The Whisperer.

Determines whether the agent should surface a contextual intervention
or remain silent.

Silence is a first-class agent decision. Repetition or unusual activity
alone is not treated as evidence that the artist needs assistance.
"""

from dataclasses import dataclass, field

from context import CreativeContext


@dataclass
class InterventionDecision:
    """Result of the intervention policy."""

    should_intervene: bool
    score: float
    reason: str
    evidence: list[str] = field(default_factory=list)
    requires_confirmation: bool = False


class InterventionPolicy:
    """Transparent decision policy for the demonstrator."""

    def __init__(self, threshold: float = 2.5):
        self.threshold = threshold

    def evaluate(
        self,
        context: CreativeContext,
    ) -> InterventionDecision:

        score = 0.0
        evidence: list[str] = []

        # Re-entering a project makes continuity support more useful.
        if context.session_reentry:
            score += 0.75
            evidence.append("Project session has been reopened.")

        # Explicitly unresolved artist intentions carry the most weight.
        if context.unresolved_memories:
            score += 1.5
            evidence.append(
                f"{len(context.unresolved_memories)} unresolved "
                "creative intention(s) remain."
            )

        # A current activity that connects with remembered context
        # strengthens the case for intervention.
        if context.related_memories:
            score += 1.0
            evidence.append(
                "Current activity relates to stored creative context."
            )

        # Repetition is weak evidence by itself.
        if context.repetition_detected:
            score += 0.25
            evidence.append(
                "Repeated review of material detected."
            )

        # Active exploration should make the agent LESS eager to speak.
        if context.active_exploration:
            score -= 1.5
            evidence.append(
                "Artist appears to be actively exploring; "
                "interruption penalty applied."
            )

        should_intervene = score >= self.threshold

        if should_intervene:
            reason = (
                "Continuity support is likely to be useful: "
                "relevant unresolved context is available."
            )
        else:
            reason = (
                "No intervention warranted. "
                "Remaining silent preserves the artist's flow."
            )

        return InterventionDecision(
            should_intervene=should_intervene,
            score=round(score, 2),
            reason=reason,
            evidence=evidence,
            requires_confirmation=False,
        )
