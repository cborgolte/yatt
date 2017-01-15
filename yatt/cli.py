# -*- coding: utf-8 -*-

import datetime
import click
from collections import defaultdict
from yatt import parser


def collect(entry, entries_per_date):
    date = entry['day']
    entries_per_date[date].append(entry)


def get_cumulated_hours(entries_per_date):
    result = {}
    keys = entries_per_date.keys()
    for day in sorted(keys, reverse=True):
        task_entries_of_day = [entry for entry in entries_per_date[day]
                               if entry['type'] == 'task']
        durations_per_project = defaultdict(datetime.timedelta)
        for entry in task_entries_of_day:
            project = entry['customer']
            durations_per_project[project] += entry['duration']
        result[day] = dict(durations_per_project)
    return result


def print_cumulated_hours(cumulated_hours):
    for day, entries in sorted(cumulated_hours.items()):
        print(day)
        for customer, td in entries.items():
            hours = datetime.datetime.combine(day, datetime.time()) + td
            print('\t{}: {} h'.format(customer, hours.strftime('%H:%M')))
        print()


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

    cumulated_hours = get_cumulated_hours(entries_per_date)
    print_cumulated_hours(cumulated_hours)

if __name__ == "__main__":
    main()
