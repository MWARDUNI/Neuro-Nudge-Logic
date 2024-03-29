import datetime
from icalendar import Calendar, Event


# from nn_01_parser import parse_assignments
# from nn_02_categorizer import categorize_assignments
from nn_03_prioritizer import calculate_impact, prioritize_assignments
# from nn_03_1_5day_study import create_study_plans_for_tests
# from nn_04_time_blocker import find_time_blocks

from nn_01_parser import *
from nn_02_categorizer import *
from nn_03_prioritizer import *
from nn_03_1_5day_study import *
from nn_04_time_blocker import *


def create_study_plan(prioritized_assignments, start_date=datetime.datetime.now()):
    
    chunks = ["A", "B", "C", "D"]

    # the study plan
    study_plan = [
        ("Day 1", [("Prepare Chunk A", 120)]),
        ("Day 2", [("Prepare Chunk B", 120), ("Review Chunk A", 30)]),
        ("Day 3", [("Prepare Chunk C", 90), ("Review Chunk B", 30), ("Review Chunk A", 15)]),
        ("Day 4", [("Prepare Chunk D", 60), ("Review Chunk C", 30), ("Review Chunk B", 15), ("Review Chunk A", 15)]),
        ("Day 5", [("Review Chunk D", 25), ("Review Chunk C", 15), ("Review Chunk B", 10), ("Review Chunk A", 10), ("Self-test on A, B, C, D", 60)])
    ]

    cal = Calendar()
    cal.add('prodid', '-//My Study Plan//example.com//')
    cal.add('version', '2.0')


    high_priority_test = next((a for a in prioritized_assignments if a['type'] == 'final'), None)
    if high_priority_test:
        event_name = high_priority_test['description']
        event_due_date = datetime.datetime.strptime(high_priority_test['due_date'], '%Y-%m-%d')
        study_plan_start = event_due_date - datetime.timedelta(days=5)

        for day, activities in enumerate(study_plan, start=1):
            day_name, tasks = activities

            day_start = study_plan_start + datetime.timedelta(days=day - 1)
            for task_name, duration_mins in tasks:
                event = Event()
                event.add('summary', f'{day_name}: {task_name}')
                event.add('dtstart', day_start)
                event.add('dtend', day_start + datetime.timedelta(minutes=duration_mins))
                cal.add_component(event)


    with open('study_plan.ics', 'wb') as f:
        f.write(cal.to_ical())







