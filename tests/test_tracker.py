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
