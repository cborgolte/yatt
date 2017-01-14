#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime
import dateparser


### class Parser(object):
###
###     def __init__(self):
###         self.lineno = 0
###         self.day = None
###         self.relative_base = datetime.datetime.now()
###         self.entries = []
###
###     def set_day(self, date):
###         self.day = date
###         # start working day at 9:00 h
###         self.set_relative_base(datetime.datetime.combine(date, datetime.time(9, 0)))
###
###     def set_relative_base(self, relative_base):
###         self.relative_base = relative_base


def set_day(date, context):
    context['day'] = date
    # start working day at 9:00 h
    context['relative_base'] = datetime.datetime.combine(date,
                                                         datetime.time(9, 0))


def create_datetime(timestr, context):
    h, m = None, None
    try:
        h, m = timestr.strip().split(':')
    except:
        h, m = timestr.strip().split('.')
    time = datetime.time(int(h), int(m))
    retval = datetime.datetime.combine(context['day'], time)
    context['relative_base'] = retval
    return retval


def parse_new_date(entry, context):
    line = entry['line']
    token = line.strip().split()
    if len(token) == 1:
        datestr, = token
    else:
        weekday, datestr  = token
    date = dateparser.parse(datestr,
                            settings={'RELATIVE_BASE': context['relative_base']})
    context['day'] = date.date()
    # TODO: check weekday w/ real date
    entry['type'] = 'new_date'
    entry['date'] = date.date()
    return entry


def _parse_duration_str(duration_str):
    try:
        h, m = (int(val.strip()) for val in duration_str.split(':', 1))
        duration = datetime.timedelta(hours=h, minutes=m)
        return duration
    except:
        h = int(duration_str.strip())
        duration = datetime.timedelta(hours=h)
        return duration


def parse_task(entry, context):
    line = entry['line'].strip()

    try:  # to parse 'from - to' time entries
        start, part = line.split('-', 1)
        stop, part = part.strip().split(' ', 1)
        starttime = create_datetime(start, context)
        stoptime = create_datetime(stop, context)
        duration = stoptime - starttime
    except:  # fall back to duration entry
        # + 1:00 h
        # 4 h
        if line.startswith('+'):
            line = line[1:]
        # split at marker for hour
        duration_str, part = line.split(' h ', 1)
        starttime = context['relative_base']
        duration = _parse_duration_str(duration_str)
        stoptime = starttime + duration

    customer = ''
    try:  # to fetch the customer name
        customer, part = part.strip().split(':', 1)
    except:
        # TODO: logging -> missing customer name
        pass

    task = part.strip()
    entry['type'] = 'task'
    entry['start'] = starttime
    entry['stop'] = stoptime
    entry['duration'] = duration
    entry['customer'] = customer
    entry['task'] = task
    return entry


def parse_default(entry, context):
    line = entry['line']
    entry['type'] = 'default'
    # parse whole day entry (Krank, Urlaub)
    tags = {'krank': 'Krank',
            'urlaub': 'Urlaub'}
    if line.strip().lower() in tags:
        entry['type'] = 'whole_day'
        entry['customer'] = 'Intern'
        entry['task'] = tags[line.strip().lower()]
        starttime = create_datetime('9:00', context)
        duration = datetime.timedelta(hours=8)
        stoptime = starttime + duration
        entry['start'] = starttime
        entry['stop'] = stoptime
        entry['duration'] = duration
    return entry


def parse_line(line, context):
    entry = {
        'lineno': context['lineno'],
        'line': line,
        'day': context['day']
    }

    line = line.strip()
    if not line:
        entry['type'] = 'break'
        context['day'] = None
        return entry

    if line.startswith('#'):
        entry['type'] = 'comment'
        entry['comment'] = line
        return entry

    # parse date entry
    try:
        return parse_new_date(entry, context)
    except:
        pass

    # parse time entry
    try:
        return parse_task(entry, context)
    except:
        pass

    return parse_default(entry, context)


def parse(lines):
    context = {
        'day': None,
        'relative_base': datetime.datetime.now()
    }
    for lineno, line in enumerate(lines, 1):
        context['line'] = line
        context['lineno'] = lineno
        entry = parse_line(line, context)
        yield entry
