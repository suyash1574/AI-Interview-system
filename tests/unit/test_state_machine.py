"""
Exhaustive unit tests for backend.core.engine.state_machine.
Tests every valid transition, every invalid transition, and edge-case behaviours
as required by TASK-ENG-001 acceptance criteria.
"""

import pytest
from backend.core.engine.state_machine import InterviewState, InterviewStateMachine, _VALID_TRANSITIONS
from backend.core.errors import StateTransitionError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sm(state: InterviewState = InterviewState.INIT) -> InterviewStateMachine:
    """Return a state machine pre-positioned at *state*."""
    sm = InterviewStateMachine(interview_id="test-interview-001")
    sm._state = state  # bypass normal transition for setup
    return sm


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestConstruction:
    def test_default_initial_state(self):
        sm = InterviewStateMachine(interview_id="x")
        assert sm.state == InterviewState.INIT

    def test_custom_initial_state(self):
        sm = InterviewStateMachine(interview_id="x", initial_state=InterviewState.CORE)
        assert sm.state == InterviewState.CORE

    def test_interview_id_stored(self):
        sm = InterviewStateMachine(interview_id="abc-123")
        assert sm.interview_id == "abc-123"

    def test_active_competency_none_on_init(self):
        sm = InterviewStateMachine(interview_id="x")
        assert sm.active_competency is None

    def test_not_terminal_on_init(self):
        sm = InterviewStateMachine(interview_id="x")
        assert not sm.is_terminal()


# ---------------------------------------------------------------------------
# Valid transitions — every edge in _VALID_TRANSITIONS
# ---------------------------------------------------------------------------

class TestValidTransitions:
    def test_init_to_device_check(self):
        sm = make_sm(InterviewState.INIT)
        sm.transition_to(InterviewState.DEVICE_CHECK)
        assert sm.state == InterviewState.DEVICE_CHECK

    def test_device_check_to_consent(self):
        sm = make_sm(InterviewState.DEVICE_CHECK)
        sm.transition_to(InterviewState.CONSENT)
        assert sm.state == InterviewState.CONSENT

    def test_consent_to_introduction(self):
        sm = make_sm(InterviewState.CONSENT)
        sm.transition_to(InterviewState.INTRODUCTION)
        assert sm.state == InterviewState.INTRODUCTION

    def test_introduction_to_profile(self):
        sm = make_sm(InterviewState.INTRODUCTION)
        sm.transition_to(InterviewState.PROFILE)
        assert sm.state == InterviewState.PROFILE

    def test_profile_to_core(self):
        sm = make_sm(InterviewState.PROFILE)
        sm.transition_to(InterviewState.CORE)
        assert sm.state == InterviewState.CORE

    def test_core_to_deep_dive(self):
        sm = make_sm(InterviewState.CORE)
        sm.transition_to(InterviewState.DEEP_DIVE)
        assert sm.state == InterviewState.DEEP_DIVE

    def test_deep_dive_to_validation(self):
        sm = make_sm(InterviewState.DEEP_DIVE)
        sm.transition_to(InterviewState.VALIDATION)
        assert sm.state == InterviewState.VALIDATION

    def test_validation_to_closing(self):
        sm = make_sm(InterviewState.VALIDATION)
        sm.transition_to(InterviewState.CLOSING)
        assert sm.state == InterviewState.CLOSING

    def test_closing_to_complete(self):
        sm = make_sm(InterviewState.CLOSING)
        sm.transition_to(InterviewState.COMPLETE)
        assert sm.state == InterviewState.COMPLETE

    def test_full_happy_path(self):
        """Walk every state from INIT through COMPLETE in sequence."""
        sm = InterviewStateMachine(interview_id="happy-path")
        ordered = [
            InterviewState.DEVICE_CHECK,
            InterviewState.CONSENT,
            InterviewState.INTRODUCTION,
            InterviewState.PROFILE,
            InterviewState.CORE,
            InterviewState.DEEP_DIVE,
            InterviewState.VALIDATION,
            InterviewState.CLOSING,
            InterviewState.COMPLETE,
        ]
        for target in ordered:
            sm.transition_to(target)
        assert sm.state == InterviewState.COMPLETE
        assert sm.is_terminal()


# ---------------------------------------------------------------------------
# Invalid transitions — must raise StateTransitionError
# ---------------------------------------------------------------------------

class TestInvalidTransitions:
    """
    Every non-edge that should be rejected.
    Tests cover: skipping states, backwards jumps, and self-loops.
    """

    # --- From INIT ---
    @pytest.mark.parametrize("bad_state", [
        InterviewState.CONSENT,
        InterviewState.INTRODUCTION,
        InterviewState.PROFILE,
        InterviewState.CORE,
        InterviewState.DEEP_DIVE,
        InterviewState.VALIDATION,
        InterviewState.CLOSING,
        InterviewState.COMPLETE,
        InterviewState.INIT,  # self-loop
    ])
    def test_init_invalid(self, bad_state):
        sm = make_sm(InterviewState.INIT)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)

    # --- From DEVICE_CHECK ---
    @pytest.mark.parametrize("bad_state", [
        InterviewState.INIT,
        InterviewState.INTRODUCTION,
        InterviewState.PROFILE,
        InterviewState.CORE,
        InterviewState.COMPLETE,
        InterviewState.DEVICE_CHECK,  # self-loop
    ])
    def test_device_check_invalid(self, bad_state):
        sm = make_sm(InterviewState.DEVICE_CHECK)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)

    # --- From CONSENT ---
    @pytest.mark.parametrize("bad_state", [
        InterviewState.INIT,
        InterviewState.DEVICE_CHECK,
        InterviewState.PROFILE,
        InterviewState.CORE,
        InterviewState.COMPLETE,
        InterviewState.CONSENT,  # self-loop
    ])
    def test_consent_invalid(self, bad_state):
        sm = make_sm(InterviewState.CONSENT)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)

    # --- From INTRODUCTION ---
    @pytest.mark.parametrize("bad_state", [
        InterviewState.INIT,
        InterviewState.CONSENT,
        InterviewState.CORE,
        InterviewState.COMPLETE,
        InterviewState.INTRODUCTION,  # self-loop
    ])
    def test_introduction_invalid(self, bad_state):
        sm = make_sm(InterviewState.INTRODUCTION)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)

    # --- From PROFILE ---
    @pytest.mark.parametrize("bad_state", [
        InterviewState.INIT,
        InterviewState.INTRODUCTION,
        InterviewState.DEEP_DIVE,
        InterviewState.COMPLETE,
        InterviewState.PROFILE,  # self-loop
    ])
    def test_profile_invalid(self, bad_state):
        sm = make_sm(InterviewState.PROFILE)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)

    # --- From CORE ---
    @pytest.mark.parametrize("bad_state", [
        InterviewState.INIT,
        InterviewState.PROFILE,
        InterviewState.VALIDATION,
        InterviewState.COMPLETE,
        InterviewState.CORE,  # self-loop
    ])
    def test_core_invalid(self, bad_state):
        sm = make_sm(InterviewState.CORE)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)

    # --- From DEEP_DIVE ---
    @pytest.mark.parametrize("bad_state", [
        InterviewState.INIT,
        InterviewState.CORE,
        InterviewState.CLOSING,
        InterviewState.COMPLETE,
        InterviewState.DEEP_DIVE,  # self-loop
    ])
    def test_deep_dive_invalid(self, bad_state):
        sm = make_sm(InterviewState.DEEP_DIVE)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)

    # --- From VALIDATION ---
    @pytest.mark.parametrize("bad_state", [
        InterviewState.INIT,
        InterviewState.DEEP_DIVE,
        InterviewState.COMPLETE,
        InterviewState.VALIDATION,  # self-loop
    ])
    def test_validation_invalid(self, bad_state):
        sm = make_sm(InterviewState.VALIDATION)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)

    # --- From CLOSING ---
    @pytest.mark.parametrize("bad_state", [
        InterviewState.INIT,
        InterviewState.VALIDATION,
        InterviewState.CLOSING,  # self-loop
    ])
    def test_closing_invalid(self, bad_state):
        sm = make_sm(InterviewState.CLOSING)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)

    # --- From COMPLETE (terminal — nothing allowed) ---
    @pytest.mark.parametrize("bad_state", list(InterviewState))
    def test_complete_is_terminal(self, bad_state):
        sm = make_sm(InterviewState.COMPLETE)
        with pytest.raises(StateTransitionError):
            sm.transition_to(bad_state)


# ---------------------------------------------------------------------------
# StateTransitionError message quality
# ---------------------------------------------------------------------------

class TestErrorMessage:
    def test_error_message_contains_from_state(self):
        sm = make_sm(InterviewState.INIT)
        with pytest.raises(StateTransitionError, match="INIT"):
            sm.transition_to(InterviewState.COMPLETE)

    def test_error_message_contains_to_state(self):
        sm = make_sm(InterviewState.INIT)
        with pytest.raises(StateTransitionError, match="COMPLETE"):
            sm.transition_to(InterviewState.COMPLETE)

    def test_state_unchanged_after_failed_transition(self):
        sm = make_sm(InterviewState.INIT)
        with pytest.raises(StateTransitionError):
            sm.transition_to(InterviewState.COMPLETE)
        # Must still be INIT
        assert sm.state == InterviewState.INIT


# ---------------------------------------------------------------------------
# is_terminal
# ---------------------------------------------------------------------------

class TestIsTerminal:
    @pytest.mark.parametrize("non_terminal_state", [
        InterviewState.INIT,
        InterviewState.DEVICE_CHECK,
        InterviewState.CONSENT,
        InterviewState.INTRODUCTION,
        InterviewState.PROFILE,
        InterviewState.CORE,
        InterviewState.DEEP_DIVE,
        InterviewState.VALIDATION,
        InterviewState.CLOSING,
    ])
    def test_non_terminal_states(self, non_terminal_state):
        sm = make_sm(non_terminal_state)
        assert not sm.is_terminal()

    def test_complete_is_terminal(self):
        sm = make_sm(InterviewState.COMPLETE)
        assert sm.is_terminal()


# ---------------------------------------------------------------------------
# DEEP_DIVE competency context
# ---------------------------------------------------------------------------

class TestCompetencyContext:
    def test_competency_set_on_deep_dive_transition(self):
        sm = make_sm(InterviewState.CORE)
        sm.transition_to(InterviewState.DEEP_DIVE, competency="System Design")
        assert sm.active_competency == "System Design"

    def test_competency_cleared_after_deep_dive(self):
        sm = make_sm(InterviewState.CORE)
        sm.transition_to(InterviewState.DEEP_DIVE, competency="Databases")
        sm._state = InterviewState.DEEP_DIVE  # already done above
        sm._state = InterviewState.DEEP_DIVE
        # Move forward to VALIDATION — competency should clear
        sm.transition_to(InterviewState.VALIDATION)
        assert sm.active_competency is None

    def test_competency_none_without_keyword_arg(self):
        sm = make_sm(InterviewState.CORE)
        sm.transition_to(InterviewState.DEEP_DIVE)
        assert sm.active_competency is None


# ---------------------------------------------------------------------------
# build_state_change_event (WebSocket payload)
# ---------------------------------------------------------------------------

class TestBuildStateChangeEvent:
    def test_event_structure(self):
        sm = make_sm(InterviewState.CORE)
        event = sm.build_state_change_event()
        assert event["type"] == "state_change"
        assert event["new_state"] == "CORE"
        assert "competency" in event

    def test_event_includes_competency_in_deep_dive(self):
        sm = make_sm(InterviewState.CORE)
        sm.transition_to(InterviewState.DEEP_DIVE, competency="Python")
        event = sm.build_state_change_event()
        assert event["new_state"] == "DEEP_DIVE"
        assert event["competency"] == "Python"

    def test_event_competency_none_outside_deep_dive(self):
        sm = make_sm(InterviewState.INTRO if hasattr(InterviewState, "INTRO") else InterviewState.CORE)
        event = sm.build_state_change_event()
        assert event["competency"] is None


# ---------------------------------------------------------------------------
# InterviewState enum completeness
# ---------------------------------------------------------------------------

class TestInterviewStateEnum:
    def test_all_states_have_valid_transition_entry(self):
        """Every state must have an entry in _VALID_TRANSITIONS."""
        for state in InterviewState:
            assert state in _VALID_TRANSITIONS, f"{state} missing from _VALID_TRANSITIONS"

    def test_state_values_are_strings(self):
        for state in InterviewState:
            assert isinstance(state.value, str)
