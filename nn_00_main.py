from icalendar import Calendar, Event
import datetime
from dateutil.rrule import *
from dateutil.parser import parse
import pytz
import copy 
import pandas as pd
from supabase import create_client, Client

def main():
    # nn_01_parser.py
    from nn_01_parser import parse_ics
    events, assignments = parse_ics('class_cal.ics')
    
    # Initialize the Supabase client
    url = "https://fgocfoakntmlhgtftrzh.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
    supabase: Client = create_client(url, key)

    # nn_02_categorizer.py
    if all(isinstance(assignment, dict) for assignment in assignments):
        from nn_02_categorizer import categorize_assignments
        categorized_assignments = categorize_assignments(assignments)
    else:
        print("Error: One or more assignments are not in dictionary format.")

    df = pd.DataFrame(events)
    df.to_csv('events.csv')
    df = pd.DataFrame(assignments)
    df.to_csv('assignments.csv')    
    # Impacts on final grade for EACH assignment type
    grade_impact_key = {
        # Theory of Computation
        'CSCI 4034': {'hw': 11, 'midterm': 33, 'final': 33}, # 3 homeworks 11% each
        # Network Programming
        'CSCI 3762': {'lab': 10}, # 10 labs 10% each (NEED TO ADJUST THE CALENDAR FILE)
        # Cyber Security 
        'CSCI 4743': {'hw': 6, 'quiz': 10, 'midterm': 20, 'final': 20}, # 5 homeworks 6% each, 3 quizzes 10% each
        # Embedded Systems
        'CSCI 4287': {'hw': 5, 'midterm': 20, 'final': 20, 'project': 40} # 4 labs 5% each, midterm 20%, final 20%, project 40%
    }

    # nn_03_prioritizer.py
    from nn_03_prioritizer import calculate_impact
    assignments_with_impact = calculate_impact(categorized_assignments, grade_impact_key)

    assignments_copy =  assignments_with_impact.copy()

    print("\n========== COPY ASSIGNMENTS w/ IMPACT ==================================================\n")
    for class_name, assignment_types in assignments_copy.items():
        for assignment_type, assignments in assignment_types.items():
            for assignment in assignments:
                print(assignment)
    

    print("============================================================\n")
    print("Assignments with Impact:\n")
    for class_name, assignment_types in assignments_with_impact.items():
        print(f"\n\n{class_name}:")
        for assignment_type, assignments in assignment_types.items():
            print(f"\n\t{assignment_type}:")
            for assignment in assignments:
                print(f"\n\t\t{assignment}")


    # nn_03_prioritizer.py
    # extract exams from categorized_assignments
    # exams = {}
    # for course, tasks in assignments_with_impact.items():
    #     for task_type, details in list(tasks.items()):
    #         if task_type in ["midterm", "final"]:
    #             if course not in exams:
    #                 exams[course] = {}
    #             exams[course][task_type] = details
    #             del assignments_with_impact[course][task_type]

    # nn_04_time_blocker.py
    # this will eventually be the unavailable time slots for the user to study
    personal_schedule = []


if __name__ == '__main__':
    main()
