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
        prj_based_data = {}
        for entry in task_entries_of_day:
            project = entry['customer']
            project_data = prj_based_data.setdefault(project,
                                                     {'duration': datetime.timedelta(0),
                                                      'tasks': set()})
            project_data['duration'] += entry['duration']
            project_data['tasks'].add(entry['task'])
        result[day] = prj_based_data
    return result


def print_cumulated_hours(cumulated_hours):
    working_hours = datetime.timedelta(hours=8)
    overtime_total = datetime.timedelta(0)
    for day, entries in sorted(cumulated_hours.items()):
        print(day)
        duration_at_day = datetime.timedelta(0)
        for customer, project_data in entries.items():
            td = project_data['duration']
            duration_at_day += td
            tasks = '; '.join(project_data['tasks'])
            hours = datetime.datetime.combine(day, datetime.time()) + td
            print('    {}: {} ({:3.2f}) h - {}'.format(customer,
                                                  hours.strftime('%H:%M'),
                                                  hours.hour + hours.minute / 60.,
                                                  tasks))
        overtime = duration_at_day - working_hours
        overtime_total += overtime
        if overtime.days >= 0:
            overtime_hours = datetime.datetime.combine(day, datetime.time()) + overtime
            overtime_str = overtime_hours.strftime('%H:%M')
        else:
            overtime_hours = datetime.datetime.combine(day, datetime.time()) - overtime
            overtime_str = '-{}'.format(overtime_hours.strftime('%H:%M'))
        overtime_total_hours = datetime.datetime.combine(day, datetime.time()) + overtime_total
        overtime_total_str = overtime_total_hours.strftime('%H:%M')
        duration_hours = datetime.datetime.combine(day, datetime.time()) + duration_at_day
        duration_str = duration_hours.strftime('%H:%M')
        print('Total duration: {}\tOvertime: {}\n Overtime total: {}'
              .format(duration_str, overtime_str, overtime_total_str));


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
