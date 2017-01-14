#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime
import dateparser
import yatt.serializer
import yatt.parser


class Tracker(object):

    WEEKDAYS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

    def __init__(self):
        self.lineno = 0
        self.day = None
        self.relative_base = datetime.datetime.now()
        self.entries = []

    def set_day(self, date):
        self.day = date
        # start working day at 9:00 h
        self.set_relative_base(datetime.datetime.combine(date, datetime.time(9, 0)))

    def set_relative_base(self, relative_base):
        self.relative_base = relative_base

    def create_datetime(self, timestr):
        h, m = None, None
        try:
            h, m = timestr.strip().split(':')
        except:
            h, m = timestr.strip().split('.')
        time = datetime.time(int(h), int(m))
        retval = datetime.datetime.combine(self.day, time)
        self.set_relative_base(retval)
        return retval

    def parse_line(self, line):
        entry = {'lineno': self.lineno, 'line': line}
        if self.day:
            entry['date'] = self.day

        line = line.strip()
        if not line:
            entry['type'] = 'break'
            self.day = None
            return entry

        if line.startswith('#'):
            entry['type'] = 'comment'
            entry['comment'] = line
            return entry

        # parse date entry
        try:
            return self.parse_new_date(line)
        except:
            pass

        # parse time entry
        try:
            return self.parse_task(line)
        except:
            pass

        return self.parse_default(line)

    def _create_entry(self, line):
        return {'lineno': self.lineno, 'line': line}

    def parse_new_date(self, line):
        entry = self._create_entry(line)
        token = line.strip().split()
        if len(token) == 1:
            datestr, = token
        else:
            weekday, datestr  = token
        date = dateparser.parse(datestr, settings={'RELATIVE_BASE':
                                                   self.relative_base})
        self.set_day(date.date())
        # TODO: check weekday w/ real date
        entry['type'] = 'new_date'
        entry['date'] = self.day
        return entry

    def parse_default(self, line):
        entry = self._create_entry(line)
        entry['type'] = 'default'
        # parse whole day entry (Krank, Urlaub)
        tags = {'krank': 'Krank',
                'urlaub': 'Urlaub'}
        if line.strip().lower() in tags:
            entry['type'] = 'whole_day'
            entry['customer'] = 'Intern'
            entry['task'] = tags[line.strip().lower()]
            starttime = self.create_datetime('9:00')
            duration = datetime.timedelta(hours=8)
            stoptime = starttime + duration
            entry['start'] = starttime
            entry['stop'] = stoptime
            entry['duration'] = duration
        return entry

    def _parse_duration_str(self, duration_str):
        try:
            h, m = (int(val.strip()) for val in duration_str.split(':', 1))
            duration = datetime.timedelta(hours=h, minutes=m)
            return duration
        except:
            h = int(duration_str.strip())
            duration = datetime.timedelta(hours=h)
            return duration

    def parse_task(self, line):
        entry = self._create_entry(line)

        try:  # to parse 'from - to' time entries
            start, part = line.split('-', 1)
            stop, part = part.strip().split(' ', 1)
            starttime = self.create_datetime(start)
            stoptime = self.create_datetime(stop)
            duration = stoptime - starttime
        except:  # fall back to duration entry
            # + 1:00 h
            # 4 h
            if line.startswith('+'):
                line = line[1:]
            # split at marker for hour
            duration_str, part = line.split(' h ', 1)
            starttime = self.relative_base
            duration = self._parse_duration_str(duration_str)
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

    def parse(self, lines):
        for self.lineno, line in enumerate(lines, 1):
            entry = self.parse_line(line)
            self.entries.append(entry)

    def persist(self, filename):
        with open(filename, 'w') as outfile:
            for line in yatt.serializer.serialize_entries(self.entries):
                outfile.write(line)
