#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from yatt import tracker


def test_parse_task():
    line = (
        " 09:00 - 11.33 \tMyCustomer:  Ticket-1234 Debugging Workflow Engine")
    trk = tracker.Tracker()
    trk.set_day(datetime.date(2016, 12, 31))
    entry = trk.parse_task(line)
    assert entry['start'] == datetime.datetime(2016, 12, 31, 9)
    assert entry['stop'] == datetime.datetime(2016, 12, 31, 11, 33)
    assert entry['customer'] == 'MyCustomer'
    assert entry['task'] == 'Ticket-1234 Debugging Workflow Engine'


def test_parse_date():
    line = "Thursday, 26.10."  # TODO: thursday need's to be validated as wrong
    trk = tracker.Tracker()
    entry = trk.parse_new_date(line)
    assert trk.day == datetime.date(2016, 10, 26)
    assert entry['type'] == 'new_date'

    line = "Mo., 26.10."
    trk = tracker.Tracker()
    entry = trk.parse_new_date(line)
    assert trk.day == datetime.date(2016, 10, 26)
    assert entry['type'] == 'new_date'

    line = "Mo., 26.10.2015"
    trk = tracker.Tracker()
    entry = trk.parse_new_date(line)
    assert trk.day == datetime.date(2015, 10, 26)
    assert entry['type'] == 'new_date'

    line = "di 26.10."
    trk = tracker.Tracker()
    entry = trk.parse_new_date(line)
    assert trk.day == datetime.date(2016, 10, 26)
    assert entry['type'] == 'new_date'


def test_parse_block():
    block = """Mo. 26.8.2010
    9:10 -  11:55 task w/o a customer entry
    10:00 - 14:20 A Customer: But Time is overlapping
    # a comment on line 4
    + 1 h         Another Customer: relative time entry
    """
    block_expected = """Do, 2010-08-26
09:10 - 11:55 task w/o a customer entry
10:00 - 14:20 A Customer: But Time is overlapping
# a comment on line 4
14:20 - 15:20 Another Customer: relative time entry
"""
    trk = tracker.Tracker()
    lines = block.splitlines()
    trk.parse(lines)
    trk.entries
    block_formatted = '\n'.join(trk.serialize())
    assert block_expected == block_formatted

