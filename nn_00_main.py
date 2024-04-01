from icalendar import Calendar, Event
import datetime
from dateutil.rrule import *
from dateutil.parser import parse
import pytz
import copy 


def main():
    # nn_01_parser.py
    from nn_01_parser import parse_ics
    events, assignments = parse_ics('nn_all_events.ics')


    if all(isinstance(assignment, dict) for assignment in assignments):
        from nn_02_categorizer import categorize_assignments
        categorized_assignments = categorize_assignments(assignments)
    else:
        print("Error: One or more assignments are not in dictionary format.")


    # # Impacts on final grade for TOTAL assignment type
    # grading_info = {
    #     # Theory
    #     'CSCI 4034': {'homework': 33, 'midterm': 33, 'final': 33}, # 3 homeworks 11% each
    #     # Network Programming
    #     'CSCI 3762': {'lab': 100}, # 10 labs 10% each
    #     # Embedded Systems
    #     'CSCI 4287': {'homework': 30, 'quiz': 30, 'final': 40}, # 5 homeworks 6% each, 3 quizzes 10% each, final 40%
    #     # Security
    #     'CSCI 4743': {'lab': 25, 'project': 35, 'final': 40} # 
    # }

    # Impacts on final grade for EACH assignment type
    grade_impact_key = {
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
    assignments_with_impact = calculate_impact(categorized_assignments, grade_impact_key)

    assignments_copy =  assignments_with_impact.copy()

    print("\n========== COPY ASSIGNMENTS w/ IMPACT ==================================================\n")
    for class_name, assignment_types in assignments_copy.items():
        for assignment_type, assignments in assignment_types.items():
            for assignment in assignments:
                print(assignment)
    
    print("\n")
    print(len(assignments_copy)) # 3
    print("\n")

    print("============================================================\n")
    print("Assignments with Impact:\n")
    for class_name, assignment_types in assignments_with_impact.items():
        print(f"\n\n{class_name}:")
        for assignment_type, assignments in assignment_types.items():
            print(f"\n\t{assignment_type}:")
            for assignment in assignments:
                print(f"\n\t\t{assignment}")
    # print(assignments_with_impact)


    # nn_03_prioritizer.py
    prioritized_assignments = prioritize_assignments(assignments_with_impact)
    print(type(prioritized_assignments))


    # nn_04_time_blocker.py
    # this will eventually be the unavailable time slots for the user to study
    personal_schedule = []



if __name__ == '__main__':
    main()
