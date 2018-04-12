"""This module handles the log scoring functionality of the heybrochecklog package."""

from heybrochecklog import UnrecognizedException
from heybrochecklog.analyze import analyze_log
from heybrochecklog.shared import get_log_contents, open_json
from heybrochecklog.logfile import LogFile
from heybrochecklog.score import eac, xld, eac95


def score_log(log_file):
    try:
        contents = get_log_contents(log_file)
        log = LogFile(contents)
        log = score_wrapper(log)
    except UnicodeDecodeError:
        log = LogFile('')
        log.unrecognized = 'Could not decode log file.'
    return log.to_dict()


def score_log_from_contents(contents):
    """Score a log file given its contents, instead of opening it from a file."""
    log = LogFile(contents.split('\n'))
    try:
        log = score_wrapper(log)
    except UnicodeDecodeError:
        log.unrecognized = 'Could not decode log file.'
    return log.to_dict()


def score_wrapper(log):
    """Determine the type of log file and passes the log to the appropriate logchecker."""

    try:
        analyze_log(log)
    except UnrecognizedException as exception:
        log.unrecognized = str(exception)
        return log

    if log.ripper == 'EAC':
        info_json = open_json('eac', '{}.json'.format(log.language))
        logchecker = eac.EACChecker(info_json['patterns'], info_json['translation'])
    elif log.ripper == 'XLD':
        patterns = open_json('xld.json')
        logchecker = xld.XLDChecker(patterns)
    elif log.ripper == 'EAC95':
        info_json = open_json('eac95', '{}.json'.format(log.language))
        logchecker = eac95.EAC95Checker(info_json['patterns'], info_json['translation'])

    try:
        log = logchecker.check(log)
    except UnrecognizedException as exception:
        log.unrecognized = str(exception)

    return log
