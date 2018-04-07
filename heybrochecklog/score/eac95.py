"""This module contains the EAC Version <=0.95 Log Checker."""

import re
from heybrochecklog.markup import markup
from heybrochecklog.score.logchecker import LogChecker
from heybrochecklog import UnrecognizedException
from heybrochecklog.score.modules import combined, drives, parsers, validation


class EAC95Checker(LogChecker):
    """This class analyzes <=0.95 EAC Log Files."""

    def check(self, main_log):
        """Checks the EAC logs."""
        logs = combined.split_combined(main_log)
        for log in logs:
            if len(log.concat_contents) < 12:
                raise UnrecognizedException('Cannot parse log file; log file too short')

            log.version = 'EAC <=0.95'
            log.album = log.concat_contents[1]
            log.drive = self.check_drive(log)

            self.index_log(log)
            self.evaluate_settings(log)
            self.check_tracks(log)
            markup(log, self.patterns, self.translation)

        main_log = combined.defragment(logs, eac95=True)
        validation.validate_track_settings(main_log)
        self.deduct_and_score(main_log)

        return main_log

    def check_drive(self, log):
        """Check the drive of the log and verify it is an allowed drive."""
        regex = r' ?: (.*) Adapter:[ 0-9]+ID:[ 0-9]+$'
        return self.get_drive(regex, log.concat_contents[2])

    def all_range_index(self, log, line):
        """Match the Range Rip line in the log file."""
        if log.index_tracks is None and re.match(self.patterns['range'], line):
            return True
        return False

    def all_range_index_action(self, log, line_num):
        """Action to take when the range rip line is matched."""
        log.track_indices.append(line_num)
        log.range = True

    def evaluate_settings(self, log):
        """Evaluate the log for usage of proper rip settings.
        Overwriting the base class for different 0.95 behavior.
        """
        psettings = self.patterns['95 settings']
        full_psettings = self.patterns['95 full line settings']
        offset_settings = self.patterns['95 offset settings']
        proper_settings = self.patterns['proper settings']

        # Compile regex beforehand
        settings, full_settings, off_settings = {}, {}, {}
        for key, regex in psettings.items():
            settings[key] = re.compile(regex)
        for key, regex in full_psettings.items():
            full_settings[key] = re.compile(regex + ' : (.*)')
        for key, regex in offset_settings.items():
            off_settings[key] = re.compile(regex + ' : (.*)')

        # Iterate through line in the settings, and verify each setting in `settings` dict
        offset_match = False
        for line in log.contents[log.index_settings:log.index_tracks]:
            for key, setting in list(settings.items()):
                result = setting.search(line)
                if result:
                    del settings[key]
            for key, setting in list(full_settings.items()):
                result = setting.search(line)
                if result:
                    if not re.search(proper_settings[key], result.group(1)):
                        log.add_deduction(key)
                    del full_settings[key]
                    break
            if not offset_match:
                offset_match = self.check_offset(log, line, off_settings)

            self.check_bad_settings(log, line)

        self.evaluate_unmatched_settings(log, settings)

        # Drive offsets aren't in the match/no match string algorithm
        if not offset_match:
            log.add_deduction('Drive offset')

    def check_offset(self, log, line, off_settings):
        """Check a log file line for proper offset."""
        found = False
        for key, setting in off_settings.items():
            result = setting.search(line)
            if result:
                if key == 'Combined offset':
                    log.add_deduction('Combined offset')
                else:
                    drives.eval_offset(log, result.group(1))
                found = True

        return found

    def check_bad_settings(self, log, line):
        """Evaluate the instant -100 point deductions
        (destructive normalization and compression offset)."""
        bad_settings = self.patterns['bad settings']
        for sett, pattern in bad_settings.items():
            if pattern in line:
                log.add_deduction(sett)

    def evaluate_unmatched_settings(self, log, settings):
        """Evaluate all unmatched settings and deduct for them.
        <=0.95 is using a match/no match string algorithm, so it's a deduction if no match."""
        for key in settings:
            if log.range and key == 'Gap handling':
                log.deductions.append('Could not verify gap handling')
            elif key == 'Gap handling':
                log.deductions.append('Gap handling')
            else:
                log.add_deduction(key)

    def check_tracks(self, log):
        """Get track data for each track and check for errors."""
        tsettings = self.patterns['track settings']
        track_settings = {
            'filename': re.compile(r' ' + tsettings['filename'] + r' (.*)'),
            'pregap': re.compile(r' ' + tsettings['pregap'] + r' ([0-9:\.]+)'),
            'peak': re.compile(r' ' + tsettings['peak'] + r' ([0-9\.]+) %'),
            'test crc': re.compile(r' ' + tsettings['test crc'] + r' ([A-Z0-9]{8})'),
            'copy crc': re.compile(r' ' + tsettings['copy crc'] + r' ([A-Z0-9]{8})')
        }

        self.analyze_tracks(log, track_settings, parsers.parse_errors_eac, accuraterip=False)

    def evaluate_tracks(self, log):
        """Evaluate the analyzed track data for deficiencies."""
        # Deduct for a Range Rip
        if log.range:
            log.add_deduction('Range rip')

    def deduct_and_score(self, log):
        """Process the accumulated deductions and score the log file."""
        # EAC <=0.95 mandatory deductions.
        log.add_deduction('EAC 0.95')
        log.add_deduction('EAC <1.0 (no checksum)')
        if not log.range:
            log.add_deduction('Gap handling')

        # Deduct for all the per-track accumulated deductions.
        for error in log.track_errors:
            if log.track_errors[error]:
                log.add_deduction(error, len(log.track_errors[error]))

        super().deduct_and_score(log)
