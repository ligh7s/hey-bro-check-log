import os
import pytest
from pathlib import Path
from heybrochecklog.score import score_log

"""Lazy person not going to do full unit testing."""

LOGS = [
    ('had-decoding-issues.log', {
        'EAC 0.95 log or older (-30 points)',
        'EAC <1.0 (no checksum)',
        'Gaps were not analyzed and appended (-10 points)'}),
    ('also-bad.log', {
        'Combined read/write offset cannot be verified (-5 points)',
        'Test & Copy was not used (-20 points)',
        'EAC 0.95 log or older (-30 points)',
        'EAC <1.0 (no checksum)',
        'Gaps were not analyzed and appended (-10 points)'}),
    ('bad-settings.log', {
        'Combined read/write offset cannot be verified (-5 points)',
        'C2 pointers were used (-20 points)',
        'EAC 0.95 log or older (-30 points)',
        'EAC <1.0 (no checksum)',
        'Gaps were not analyzed and appended (-10 points)'}),
    ('read-mode.log', {
        'Audio cache not defeated (-10 points)',
        'EAC 0.95 log or older (-30 points)',
        'EAC <1.0 (no checksum)',
        'Gaps were not analyzed and appended (-10 points)'}),
]


@pytest.mark.parametrize(
    'filename, deductions', LOGS)
def test_scoring(filename, deductions):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'EAC95', filename)
    log_file = Path(log_path)
    log = score_log(log_file)
    assert deductions == {d[0] for d in log['deductions']}
