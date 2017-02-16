#!/usr/bin/env python
# -*- coding: utf-8 -*-


WEEKDAYS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']


def serialize_break(entry):
    # noop
    return ''


def serialize_task(entry):
    line = '{} - {} '.format(entry['start'].strftime('%H:%M'),
                             entry['stop'].strftime('%H:%M'))
    if (entry['customer']):
        line += '{}: '.format(entry['customer'])
    line += entry['task']
    return line


def serialize_new_date(entry):
    dte = entry['day']
    weekday = WEEKDAYS[dte.weekday()]
    line = '{}, {}'.format(weekday, dte)
    return line


def serialize_whole_day(entry):
    return serialize_task(entry)


def serialize_comment(entry):
    return entry['comment']


def serialize_default(entry):
    return 'not implemented: {} -> {}'.format(entry['type'], entry['line'])


def serialize_entry(entry):
    fnc = globals().get('serialize_' + entry['type'], serialize_default)
    line = fnc(entry)
    return line


def serialize_entries(entries):
    for entry in entries:
        yield serialize_entry(entry)
