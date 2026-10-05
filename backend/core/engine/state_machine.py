"""
Interview State Machine
-----------------------
Implements the deterministic state machine for the Autergo interview engine.

States (from HLD v1.0, Section 4):
    INIT -> DEVICE_CHECK -> CONSENT -> INTRODUCTION -> PROFILE
    -> CORE -> DEEP_DIVE -> VALIDATION -> CLOSING -> COMPLETE

All state transitions are explicit and validated. Any attempt to perform an
undefined transition raises StateTransitionError, guaranteeing deterministic
control flow per AUTERGO_ARCHITECTURE_BASELINE_v2.0.md §5.
"""

import logging
from enum import Enum
from typing import Optional

from backend.core.errors import StateTransitionError

logger = logging.getLogger(__name__)


class InterviewState(str, Enum):
    """Ordered interview stages."""
    INIT = "INIT"
    DEVICE_CHECK = "DEVICE_CHECK"
    CONSENT = "CONSENT"
    INTRODUCTION = "INTRODUCTION"
    PROFILE = "PROFILE"
    CORE = "CORE"
    DEEP_DIVE = "DEEP_DIVE"
    VALIDATION = "VALIDATION"
    CLOSING = "CLOSING"
    COMPLETE = "COMPLETE"


# Valid transitions: from_state -> set of allowed to_states
_VALID_TRANSITIONS: dict[InterviewState, frozenset[InterviewState]] = {
    InterviewState.INIT: frozenset({InterviewState.DEVICE_CHECK}),
    InterviewState.DEVICE_CHECK: frozenset({InterviewState.CONSENT}),
    InterviewState.CONSENT: frozenset({InterviewState.INTRODUCTION}),
    InterviewState.INTRODUCTION: frozenset({InterviewState.PROFILE}),
    InterviewState.PROFILE: frozenset({InterviewState.CORE}),
    InterviewState.CORE: frozenset({InterviewState.DEEP_DIVE}),
    InterviewState.DEEP_DIVE: frozenset({InterviewState.VALIDATION}),
    InterviewState.VALIDATION: frozenset({InterviewState.CLOSING}),
    InterviewState.CLOSING: frozenset({InterviewState.COMPLETE}),
    InterviewState.COMPLETE: frozenset(),  # terminal state
}

# Canonical linear progression map (single source of truth for the system)
STATE_TRANSITION_MAP: dict[InterviewState, InterviewState] = {
    InterviewState.INIT: InterviewState.DEVICE_CHECK,
    InterviewState.DEVICE_CHECK: InterviewState.CONSENT,
    InterviewState.CONSENT: InterviewState.INTRODUCTION,
    InterviewState.INTRODUCTION: InterviewState.PROFILE,
    InterviewState.PROFILE: InterviewState.CORE,
    InterviewState.CORE: InterviewState.DEEP_DIVE,
    InterviewState.DEEP_DIVE: InterviewState.VALIDATION,
    InterviewState.VALIDATION: InterviewState.CLOSING,
    InterviewState.CLOSING: InterviewState.COMPLETE,
}


class InterviewStateMachine:
    """
    Controls the deterministic lifecycle of a single interview session.

    Usage::

        sm = InterviewStateMachine(interview_id="uuid-here")
        sm.transition_to(InterviewState.DEVICE_CHECK)
        sm.transition_to(InterviewState.CONSENT)
        # ... etc.

    An invalid transition raises StateTransitionError.
    """

    def __init__(
        self,
        interview_id: str,
        initial_state: InterviewState = InterviewState.INIT,
    ) -> None:
        self.interview_id = interview_id
        self._state: InterviewState = initial_state
        # Optional metadata attached to the current DEEP_DIVE competency context
        self._active_competency: Optional[str] = None
        logger.info(
            "StateMachine created",
            extra={"interview_id": interview_id, "initial_state": initial_state.value},
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def state(self) -> InterviewState:
        """The current state of the interview."""
        return self._state

    @property
    def active_competency(self) -> Optional[str]:
        """
        The competency being probed in the DEEP_DIVE phase, or None otherwise.
        Set via :meth:`transition_to` ``context`` parameter.
        """
        return self._active_competency

    def transition_to(
        self,
        new_state: InterviewState,
        *,
        competency: Optional[str] = None,
    ) -> None:
        """
        Attempt a transition from the current state to *new_state*.

        Parameters
        ----------
        new_state:
            The target :class:`InterviewState`.
        competency:
            Optional competency label (only meaningful for DEEP_DIVE transitions,
            used to populate ``active_competency`` and the ``state_change`` WebSocket
            message described in AUTERGO_IMPLEMENTATION_SPEC_v2.0.md §4).

        Raises
        ------
        StateTransitionError
            If the transition is not permitted from the current state.
        """
        allowed = _VALID_TRANSITIONS.get(self._state, frozenset())
        if new_state not in allowed:
            raise StateTransitionError(
                f"Invalid transition: {self._state.value} -> {new_state.value}. "
                f"Allowed from {self._state.value}: "
                f"{[s.value for s in allowed] or 'none (terminal state)'}."
            )

        old_state = self._state
        self._state = new_state

        # Track active competency for the DEEP_DIVE phase
        if new_state == InterviewState.DEEP_DIVE:
            self._active_competency = competency
        else:
            self._active_competency = None

        logger.info(
            "State transition",
            extra={
                "interview_id": self.interview_id,
                "from_state": old_state.value,
                "to_state": new_state.value,
                "competency": competency,
            },
        )

    def advance(self, competency: Optional[str] = None) -> InterviewState:
        """
        Advance to the next sequential stage according to STATE_TRANSITION_MAP.
        If already terminal (COMPLETE), does nothing and returns COMPLETE.
        """
        if self.is_terminal():
            return self._state
        target = STATE_TRANSITION_MAP.get(self._state)
        if target:
            self.transition_to(target, competency=competency)
        return self._state

    def complete_all(self) -> None:
        """
        Rapidly advances through all remaining states until reaching COMPLETE.
        Used when an interview session finishes early or completes normally.
        """
        while not self.is_terminal():
            target = STATE_TRANSITION_MAP.get(self._state, InterviewState.COMPLETE)
            self.transition_to(target)

    def is_terminal(self) -> bool:
        """Return True if the interview has reached its terminal COMPLETE state."""
        return self._state == InterviewState.COMPLETE

    def build_state_change_event(self) -> dict:
        """
        Build the WebSocket ``state_change`` message payload as defined in
        AUTERGO_IMPLEMENTATION_SPEC_v2.0.md §4.

        Returns
        -------
        dict
            ``{"type": "state_change", "new_state": <str>, "competency": <str|None>}``
        """
        return {
            "type": "state_change",
            "new_state": self._state.value,
            "competency": self._active_competency,
        }
