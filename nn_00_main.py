from icalendar import Calendar, Event
import datetime
from dateutil.rrule import *
from dateutil.parser import parse
import pytz


def main():
    # nn_01_parser.py
    from nn_01_parser import parse_ics
    events, assignments = parse_ics('testcal.ics')

    if all(isinstance(assignment, dict) for assignment in assignments):
        from nn_02_categorizer import categorize_assignments
        categorized_assignments = categorize_assignments(assignments)
    else:
        print("Error: One or more assignments are not in dictionary format.")


    # Impacts on final grade for TOTAL assignment type
    grading_info = {
        # Theory
        'CSCI 4034': {'homework': 33, 'midterm': 33, 'final': 33}, # 3 homeworks 11% each
        # Network Programming
        'CSCI 3762': {'lab': 100}, # 10 labs 10% each
        # Embedded Systems
        'CSCI 4287': {'homework': 30, 'quiz': 30, 'final': 40}, # 5 homeworks 6% each, 3 quizzes 10% each, final 40%
        # Security
        'CSCI 4743': {'lab': 25, 'project': 35, 'final': 40} # 
    }

    # Impacts on final grade for EACH assignment type
    grade_impact_individually = {
        # Theory
        'CSCI 4034': {'homework': 11, 'midterm': 33, 'final': 33}, # 3 homeworks 11% each
        # Network Programming
        'CSCI 3762': {'lab': 10}, # 10 labs 10% each (NEED TO ADJUST THE CALENDAR FILE)
        # Security
        'CSCI 4743': {'homework': 6, 'quiz': 10, 'midterm': 20, 'final': 20}, # 5 homeworks 6% each, 3 quizzes 10% each
        # Embedded Systems
        'CSCI 4287': {'labs': 5, 'midterm': 20, 'final': 20, 'project': 40} # 4 labs 5% each, midterm 20%, final 20%, project 40%
    }

    # nn_03_prioritizer.py
    from nn_03_prioritizer import calculate_impact, prioritize_assignments
    # assignments_with_impact = calculate_impact(categorized_assignments, grading_info)
    assignments_with_impact = calculate_impact(categorized_assignments, grade_impact_individually)

    # nn_03_prioritizer.py
    prioritized_assignments = prioritize_assignments(assignments_with_impact)

    print("============================================================\n")
    print("Prioritized Assignments:\n")
    print(prioritized_assignments)

    # nn_03_1_5day_study.py
    from nn_03_1_5day_study import create_study_plan
    create_study_plan(prioritized_assignments)

    # nn_04_time_blocker.py
    personal_schedule = [
        
        ('2023-04-10', '2023-04-11'),
        ('2023-04-15', '2023-04-16'),

    ]

    # suitable_assignments = find_time_blocks(prioritized_assignments, personal_schedule)

    # print(suitable_assignments)

if __name__ == '__main__':
    main()
