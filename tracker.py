#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime
import glob
import difflib

class Tracker(object):

    WEEKDAYS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

    def __init__(self):
        self.lineno = 0
        self.day = None
        self.year = 2016
        self.entries = []

    def get_year_from_filename(self, filename):
        # TODO implement
        return 2016

    def set_day(self, day, month, year=None):
        if not year:
            year = self.year
        self.day = datetime.date(int(year), int(month), int(day))

    def create_datetime(self, timestr):
        h, m = timestr.strip().split(':')
        retval = datetime.datetime.combine(self.day, datetime.time(int(h), int(m)))
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
        weekday, date = line.split()
        day, month, *_ = date.split('.')
        self.set_day(day.strip(), month.strip())
        print("---> {0}".format(self.day))
        #todo: check weekday w/ real date
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

    def parse_task(self, line):
        entry = self._create_entry(line)
        start, part = line.split('-', 1)
        stop, part = part.strip().split(' ', 1)
        starttime = self.create_datetime(start)
        stoptime = self.create_datetime(stop)
        customer = ''
        try:
            customer, part = part.strip().split(':', 1)
        except:
            # TODO: logging
            pass
        task = part
        print("duration: {0} on task '{1}'".format(stoptime - starttime, part))
        entry['type'] = 'task'
        entry['start'] = starttime
        entry['stop'] = stoptime
        entry['duration'] = stoptime - starttime
        entry['customer'] = customer
        entry['task'] = task
        return entry

    def parse(self, lines):
        for self.lineno, line in enumerate(lines, 1):
            entry = self.parse_line(line)
            self.entries.append(entry)

    def serialize_break(self, entry):
        # noop
        return ''

    def serialize_task(self, entry):
        line = '{} - {} '.format(entry['start'].strftime('%H:%m'),
                                entry['stop'].strftime('%H:%m'))
        if (entry['customer']):
            line += ' {}: '.format(entry['customer'])
        line += entry['task']
        line += '\n'
        return line

    def serialize_new_date(self, entry):
        line = '\n'
        dte = entry['date']
        weekday = self.WEEKDAYS[dte.weekday()]
        line += '{}, {}\n'.format(weekday, dte)
        return line

    def serialize_whole_day(self, entry):
        return self.serialize_task(entry)

    def serialize_default(self, entry):
        return 'not implemented: {} -> {}\n'.format(entry['type'], entry['line'])

    def persist(self, filename):
        with open(filename, 'w') as outfile:
            for entry in self.entries:
                fnc = getattr(self, 'serialize_' + entry['type'], self.serialize_default)
                line = fnc(entry)
                outfile.write(line)

    def validate_break(self, entry):
        return []

    def validate_default(self, entry):
        fnc = getattr(self, 'serialize_' + entry['type'], self.serialize_default)
        a = fnc(entry)
        b = entry['line']
        sm = difflib.SequenceMatcher(None, a, b)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                continue
            return ['{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'
                    .format(tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2])]

    def validate_whole_day(self, entry):
        return []

    def validate_task(self, entry):
        msg = []
        if not entry['customer']:
            msg.append('missing customer')
        return msg

    def validate(self):
        for entry in self.entries:
            fnc = getattr(self, 'validate_' + entry['type'], self.validate_default)
            validation_msgs = fnc(entry)
            if validation_msgs:
                print('{}: {}'.format(entry['lineno'],
                                      '; '.join(validation_msgs)))


for filename in glob.glob('timesheet*.txt'):
    print(filename)
    tracker = Tracker()
    with open(filename) as fle:
        tracker.parse(fle.readlines())
    tracker.persist('/tmp/' + filename)
    tracker.validate()

tracker = Tracker()
tracker.parse_new_date('Do. 22.12.')
tracker.parse_task("7:00 - 7:20 Intern: Fahrtkostenaufstellung")

