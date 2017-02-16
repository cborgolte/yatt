#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

import yatt.serializer
from yatt import parser


def test_parse_task():
    context = {
    }
    parser.set_day(datetime.date(2016, 12, 31), context)
    entry = dict(line=(" 09:00 - 11.33 \t"
                       "MyCustomer:  Ticket-1234 Debugging Workflow Engine"))
    entry = parser.parse_task(entry, context)
    assert entry['start'] == datetime.datetime(2016, 12, 31, 9)
    assert entry['stop'] == datetime.datetime(2016, 12, 31, 11, 33)
    assert entry['customer'] == 'MyCustomer'
    assert entry['task'] == 'Ticket-1234 Debugging Workflow Engine'
    assert entry['type'] == 'task'


def test_parse_task_with_hour():
    context = {
    }
    parser.set_day(datetime.date(2016, 12, 31), context)
    line = '    + 1 h         Another Customer: relative time entry'
    entry = dict(line=line)
    entry = parser.parse_task(entry, context)
    assert entry['start'] == datetime.datetime(2016, 12, 31, 9)
    assert entry['stop'] == datetime.datetime(2016, 12, 31, 10)
    assert entry['customer'] == 'Another Customer'
    assert entry['task'] == 'relative time entry'
    assert entry['type'] == 'task'


def test_parse_date():
    context = {
    }
    parser.set_day(datetime.date(2016, 1, 1), context)
    line = "Thursday, 26.10."
    entry = dict(line=line)
    entry = parser.parse_new_date(entry, context)
    assert context['day'] == datetime.date(2016, 10, 26)
    assert entry['type'] == 'new_date'

    line = "Mo., 27.10."
    entry = dict(line=line)
    entry = parser.parse_new_date(entry, context)
    assert context['day'] == datetime.date(2016, 10, 27)
    assert entry['type'] == 'new_date'

    line = "Mo., 25.10.2015"
    entry = dict(line=line)
    entry = parser.parse_new_date(entry, context)
    assert context['day'] == datetime.date(2015, 10, 25)
    assert entry['type'] == 'new_date'

    line = "di 23.10."
    entry = dict(line=line)
    entry = parser.parse_new_date(entry, context)
    assert context['day'] == datetime.date(2016, 10, 23)
    assert entry['type'] == 'new_date'

    line = "Mo, 2010-10-22"
    entry = dict(line=line)
    entry = parser.parse_new_date(entry, context)
    assert context['day'] == datetime.date(2010, 10, 22)
    assert entry['type'] == 'new_date'

    line = "2010-10-21"
    entry = dict(line=line)
    entry = parser.parse_new_date(entry, context)
    assert context['day'] == datetime.date(2010, 10, 21)
    assert entry['type'] == 'new_date'

    line = "2017-02-10"
    entry = dict(line=line)
    entry = parser.parse_new_date(entry, context)
    assert context['day'] == datetime.date(2017, 2, 10)
    assert entry['type'] == 'new_date'

    line = "Do. 12.01."
    entry = dict(line=line)
    entry = parser.parse_new_date(entry, context)
    assert context['day'] == datetime.date(2016, 1, 12)
    assert entry['type'] == 'new_date'


def test_parse_and_format_block():
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
    lines = block.splitlines()
    entries = list(parser.parse(lines))
    block_formatted = '\n'.join(yatt.serializer.serialize_entries(entries))
    assert block_expected == block_formatted

    # assert that tracker can read it's own output!
    lines = block_expected.splitlines()
    block_formatted = '\n'.join(yatt.serializer.serialize_entries(entries))
    assert block_expected == block_formatted
