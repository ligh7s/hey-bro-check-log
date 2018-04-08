import os
import pytest
from pathlib import Path
from heybrochecklog.score import score_log

"""Lazy person not going to do full unit testing."""

LOGS = [
    ('abort.log', {'Combined log'}),
    ('badcombo.log', {'Gaps were not analyzed and appended (-10 points)',
                      'Combined log'}),
    ('eac-95-had-decoding-issues.log', {'EAC 0.95 log or older (-30 points)',
                                        'EAC <1.0 (no checksum)',
                                        'Gaps were not analyzed and appended (-10 points)'}),
    ('eac-13-good.log', set()),
    ('eac-95-also-bad.log', {'Combined read/write offset cannot be verified (-5 points)',
                             'Test & Copy was not used (-20 points)',
                             'EAC 0.95 log or older (-30 points)',
                             'EAC <1.0 (no checksum)',
                             'Gaps were not analyzed and appended (-10 points)'}),
    ('eac-95-bad-settings.log', {'Combined read/write offset cannot be verified (-5 points)',
                                 'C2 pointers were used (-20 points)',
                                 'EAC 0.95 log or older (-30 points)',
                                 'EAC <1.0 (no checksum)',
                                 'Gaps were not analyzed and appended (-10 points)'}),
    ('eac-95-read-mode.log', {'Audio cache not defeated (-10 points)',
                              'EAC 0.95 log or older (-30 points)',
                              'EAC <1.0 (no checksum)',
                              'Gaps were not analyzed and appended (-10 points)'}),
    ('eac-99-good.log', {'EAC <1.0 (no checksum)'}),
    ('hella-aborted.log', {'Audio cache not defeated (-10 points)',
                           'Gaps were not analyzed and appended (-10 points)',
                           'Could not verify usage of null samples',
                           'EAC <1.0 (no checksum)',
                           'Could not verify presence of ID3 tags',
                           'Combined log',
                           'Test & Copy was not used (-20 points)'}),
    ('bad-htoa.log', {'Could not verify presence of ID3 tags',
                      'HTOA was improperly extracted (-10 points)',
                      'HTOA was not ripped twice (-10 points)',
                      'Combined log'}),
    ('range-rip.log', {'Could not verify gap handling',
                       'Range rip detected (-20 points)'}),
    ('htoa-not-ripped-twice.log', {'HTOA extracted',
                                   'HTOA was not ripped twice (-10 points)'}),
    ('shitty-eac.log', {'Suspicious position (3 occurrences) (-60 points)',
                        'CRC mismatch (3 occurrences) (-90 points)'}),
    ('xld32p.log', {'Ripper mode was not XLD Secure Ripper (-100 points)',
                    'C2 pointers were used (-20 points)',
                    'Gaps were not analyzed and appended (-10 points)',
                    'XLD pre-142.2 (no checksum)',
                    'Track gain was not turned on (-1 points)'}),
    ('xld-crc-mismatch.log', {'CRC mismatch (-30 points)'}),
    ('xld-htoa.log', {'CD-R detected; not a pressed CD',
                      'HTOA extracted'}),
    ('xld-ripping-error.log', {'Track 16: Damaged sector (724 occurrences) (-10 points)',
                               'CRC mismatch (-30 points)'}),
    ('xldrr-vbox.log', {'Range rip detected (-20 points)'}),
    ('inconsistent-accuraterip.log', {'AccurateRip discrepancies; rip may contain silent errors'}),
    ('perf-hunid.log', set()),
]


@pytest.mark.parametrize(
    'filename, deductions', LOGS)
def test_scoring(filename, deductions):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', filename)
    log_file = Path(log_path)
    log = score_log(log_file)
    assert deductions == {d[0] for d in log['deductions']}
