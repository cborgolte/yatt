# -*- coding: utf-8 -*-

import datetime
from collections import defaultdict
from typing import Dict, List, NamedTuple, Set

import click
from yatt import parser


class Task(NamedTuple):
    project: str
    name: str
    duration: datetime.timedelta


class ProjectData:
    def __init__(self,
                 project: str,
                 duration: datetime.timedelta = datetime.timedelta(0),
                 tasks: Set[str] = None):
        self.project = project
        self.duration = duration
        if tasks is None:
            tasks = set([])
        self.tasks = tasks


class DayData(NamedTuple):
    day: datetime.date
    duration_total: datetime.timedelta
    overtime: datetime.timedelta
    projects: List[ProjectData]


def collect_tasks(entries):
    entries_per_date = defaultdict(list)
    for entry in entries:
        date = entry['day']
        if entry['type'] == 'task':
            task = Task(entry['customer'], entry['task'], entry['duration'])
            entries_per_date[date].append(task)
    return entries_per_date


def get_cumulated_hours(entries_per_date: Dict[datetime.datetime, List[Task]]):
    result = {}
    keys = entries_per_date.keys()
    working_hours = datetime.timedelta(hours=8)
    # for every day, aggregate tasks per project
    for day in sorted(keys):
        prj_based_data = {}
        duration_at_day = datetime.timedelta(0)
        for task in entries_per_date[day]:
            project = task.project
            project_data = prj_based_data.setdefault(project, ProjectData(project))
            duration_at_day += task.duration
            project_data.tasks.add(task.name)
            project_data.duration += task.duration
        overtime = duration_at_day - working_hours
        projects = prj_based_data.values()
        day_data = DayData(day, duration_at_day, overtime, projects)
        result[day] = day_data
    return result


def print_cumulated_hours(cumulated_hours):
    overtime_total = datetime.timedelta(0)
    for day, day_data in sorted(cumulated_hours.items()):
        print(day)
        for project in day_data.projects:
            td = project.duration
            tasks = '; '.join(sorted(project.tasks))
            hours = datetime.datetime.combine(day, datetime.time()) + td
            print('    {}: {} ({:3.2f}) h - {}'
                  .format(project.project,
                          hours.strftime('%H:%M'),
                          hours.hour + hours.minute / 60.,
                          tasks))
        overtime = day_data.overtime
        overtime_total += overtime
        if overtime.days >= 0:
            overtime_hours = datetime.datetime.combine(day, datetime.time()) + overtime
            overtime_str = overtime_hours.strftime('%H:%M')
        else:
            overtime_hours = datetime.datetime.combine(day, datetime.time()) - overtime
            overtime_str = '-{}'.format(overtime_hours.strftime('%H:%M'))
        overtime_total_hours = datetime.datetime.combine(day, datetime.time()) + overtime_total
        overtime_total_str = overtime_total_hours.strftime('%H:%M')
        duration_hours = datetime.datetime.combine(day, datetime.time()) + day_data.duration_total
        duration_str = duration_hours.strftime('%H:%M')
        print('Total duration: {}\tOvertime: {}\n Overtime total: {}'
              .format(duration_str, overtime_str, overtime_total_str))


@click.command()
@click.argument('filename', nargs=-1)
def main(filename):
    """Console script for yatt"""
    # click.echo("See click documentation at http://click.pocoo.org/")
    def entries():
        for fname in filename:
            with open(fname) as infile:
                for entry in parser.parse(infile.readlines()):
                    yield entry

    entries_per_date = collect_tasks(entries())
    cumulated_hours = get_cumulated_hours(dict(entries_per_date))
    print_cumulated_hours(cumulated_hours)


if __name__ == "__main__":
    main()
