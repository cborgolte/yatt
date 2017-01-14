# -*- coding: utf-8 -*-

import datetime
import click
from collections import defaultdict
from yatt import parser


def collect(entry, entries_per_date):
    date = entry['day']
    entries_per_date[date].append(entry)


def get_cumulated_hours(entries_per_date):
    keys = entries_per_date.keys()
    for day in sorted(keys, reverse=True):
        task_entries_of_day = [entry for entry in entries_per_date[day]
                               if entry['type'] == 'task']
        duration_total = datetime.timedelta(0)
        for entry in task_entries_of_day:
            duration_total += entry['duration']
        print('{} -> {}'.format(day, duration_total))


@click.command()
@click.argument('filename', nargs=-1)
def main(filename):
    """Console script for yatt"""
    entries_per_date = defaultdict(list)
    # click.echo("See click documentation at http://click.pocoo.org/")
    for fname in filename:
        with open(fname) as infile:
            for entry in parser.parse(infile.readlines()):
                collect(entry, entries_per_date)

    import pprint
    pprint.pprint(entries_per_date)
    #pprint.pprint(list(entries_per_date.keys()))
    get_cumulated_hours(entries_per_date)

if __name__ == "__main__":
    main()
