#!/usr/bin/env python
# -*- coding: utf-8 -*-

import difflib
from .serializer import serialize_entry


def validate_break(entry):
    return []

def validate_default(entry):
    fnc = serialize_entry(entry)
    a = fnc(entry)
    b = entry['line']
    sm = difflib.SequenceMatcher(None, a, b)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        return ['{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'
                .format(tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2])]

def validate_whole_day(entry):
    return []

def validate_task(entry):
    msg = []
    if not entry['customer']:
        msg.append('missing customer')
    return msg

def validate_entry(entry):
    fnc = locals().get('validate_' + entry['type'], validate_default)
    validation_msgs = fnc(entry)
    if validation_msgs:
        print('{}: {}'.format(entry['lineno'],
                                '; '.join(validation_msgs)))

def validate_entries(entries):
    for entry in entries:
        validate_entry(entry)
