#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from yatt import tracker


def test_parse_task():
    line = (
        " 09:00 - 11.33 \tMyCustomer:  Ticket-1234 Debugging Workflow Engine")
    trk = tracker.Tracker()
    trk.day = datetime.date(2016, 12, 31)
    entry = trk.parse_task(line)
    assert entry['start'] == datetime.datetime(2016, 12, 31, 9)
    assert entry['stop'] == datetime.datetime(2016, 12, 31, 11, 33)
    assert entry['customer'] == 'MyCustomer'
    assert entry['task'] == 'Ticket-1234 Debugging Workflow Engine'
