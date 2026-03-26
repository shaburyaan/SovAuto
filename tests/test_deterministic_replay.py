from core.testing.deterministic_replay_runner import DeterministicReplayRunner


def test_deterministic_replay_three_times() -> None:
    runner = DeterministicReplayRunner()
    steps = [{"id": "1", "type": "click"}]
    assert runner.run_three_times(steps) is True
