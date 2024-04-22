from icalendar import Calendar, Event
from datetime import datetime
from dateutil.rrule import *
from dateutil.parser import parse
import pytz
import copy 
import pandas as pd
from supabase import create_client, Client



def nn_main():
    
    from nn_01_parser import parse_ics
    from nn_02_categorizer import categorize_assignments
    from nn_03_prioritizer import add_impact, extract_exams, assign_priority, sort_prioritized_assignments, exams, prioritize_assignments
    from nn_03_1_5day_study import create_study_plan

    # nn_01_parser.py
    events, assignments = parse_ics('all_in_one.ics')
    
    # Init supabase client
    url = "https://fgocfoakntmlhgtftrzh.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
    
    supabase: Client = create_client(url, key)

    # nn_02_categorizer.py
    if all(isinstance(assignment, dict) for assignment in assignments):
        categorized_assignments = categorize_assignments(assignments)
    else:
        print("Error: One or more assignments are not in dictionary format.")

    # print("\n========== CATEGORIZED ASSIGNMENTS ==================================================\n")
    # for class_name, assignment_types in categorized_assignments.items():
    #     print(f"\n{class_name}:")
    #     for assignment_type, assignments in assignment_types.items():
    #         print(f"\n\t{assignment_type}:")
    #         for assignment in assignments:
    #             print(f"\n\t\t{assignment}")
                
    # supabase.table("assignments").upsert(assignments).execute()
    # supabase.table("events").upsert(events).execute()


    # df = pd.DataFrame(events)
    # df.to_csv('events.csv')
    # df = pd.DataFrame(assignments)
    # df.to_csv('assignments.csv')    

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

    assignments_with_impact = add_impact(categorized_assignments, grade_impact_key)
    # print("\n========== ASSIGNMENTS WITH IMPACT ==================================================\n")
    # for class_name, assignment_types in assignments_with_impact.items():
    #     print(f"\n{class_name}:")
    #     for assignment_type, assignments in assignment_types.items():
    #         print(f"\n\t{assignment_type}:")
    #         for assignment in assignments:
    #             print(f"\n\t\timpact: {assignment['impact']}")


    exams = {}
    exams = extract_exams(assignments_with_impact, exams)

    # data structure to hold the prioritize_assignments @param
    prioritized_assignments = {}
    # 
    prioritized_assignments = assign_priority(categorized_assignments, prioritize_assignments)

    # print("\n========== EXAMS ==================================================\n")
    # for class_name, exam_types in exams.items():
    #     print(f"\n{class_name}:")
    #     for exam_type, exams in exam_types.items():
    #         print(f"\n\t{exam_type}:")
    #         for exam in exams:
    #             print(f"\n\t\t{exam}")


    # print("\n========== PRIORITIZED ASSIGNMENTS ==================================================\n")
    # for class_name, assignment_types in prioritized_assignments.items():
    #     print(f"\n{class_name}:")
    #     for assignment_type, assignments in assignment_types.items():
    #         print(f"\n\t{assignment_type}:")
    #         for assignment in assignments:
    #             print(f"\n\tassignment: {assignment}\tpriority: {assignment['priority']}")


    sorted_assignments = {}
    sorted_assignments = sort_prioritized_assignments(prioritized_assignments)



    # print("\n========== SORTED ASSIGNMENTS ==================================================\n")
    # for class_name, assignment_types in sorted_assignments.items():
    #     # print class name
    #     print(f"\n{class_name}:")
    #     # print assignment type, due date, priority, and impact
    #     for assignment_type, assignments in assignment_types.items():
    #         print(f"\n\t{assignment_type}:")
    #         for assignment in assignments:
    #             print(f"\n\t\tassignment: {assignment}\tdue: {assignment['due']}\tpriority: {assignment['priority']}\timpact: {assignment['impact']}")
                
    print("\n\n\n\n")  
    # assignments = prioritized_assignments
    # print(sorted_assignments)
    # print(events)
    for assignment in assignments:
        # print(assignment)
        assignment['due'] = assignment['due'].isoformat()
    for event in events:
        # print(event)
        event['start_time'] = event['start_time'].isoformat()
        event['end_time'] = event['end_time'].isoformat()
    supabase.table("assignments").upsert(assignments).execute()
    supabase.table("events").upsert(events).execute()
    
    create_study_plan(supabase, "2024-01-01")
    


if __name__ == '__nn_main__':
    nn_main()
