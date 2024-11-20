
from datetime import datetime
from typing import List, Dict, Tuple
import copy 

# Impacts on final grade for EACH assignment type
grade_impact_key = {
    # Theory
    'CSCI 4034': {'hw': 11, 'midterm': 33, 'final': 33}, # 3 homeworks 11% each
    # Network Programming
    'CSCI 3762': {'lab': 10}, # 10 labs 10% each (NEED TO ADJUST THE CALENDAR FILE)
    # Security
    'CSCI 4743': {'hw': 6, 'quiz': 10, 'midterm': 20, 'final': 20}, # 5 homeworks 6% each, 3 quizzes 10% each
    # Embedded Systems
    'CSCI 4287': {'hw': 5, 'midterm': 20, 'final': 20, 'project': 40} # 4 labs 5% each, midterm 20%, final 20%, project 40%
}


def add_impact(categorized_assignments, grade_impact_key):
    for class_name, assignment_types in categorized_assignments.items():
        class_impact = grade_impact_key.get(class_name, {})
        for assignment_type, assignments in assignment_types.items():
            impact = class_impact.get(assignment_type, 0)
            for assignment in assignments:
                # add the impact
                assignment['impact'] = impact
    return categorized_assignments



exams = {}

def extract_exams(categorized_assignments, exams):
    for course, tasks in categorized_assignments.items():
        for task_type, details in list(tasks.items()):
            if task_type in ["midterm", "final"]:
                if course not in exams:
                    exams[course] = {}
                exams[course][task_type] = details
                del categorized_assignments[course][task_type]
    return exams, categorized_assignments



prioritize_assignments = {}

def assign_priority(categorized_assignments, prioritize_assignments):
    today = datetime.today().date()
    for class_name, assignment_types in categorized_assignments.items():
        for assignment_type, assignments in assignment_types.items():
            for assignment in assignments:
                # calculate the number of days between today and the due date
                due_date = assignment['due'].date()
                days_until_due = (due_date - today).days
                # print(f"\ndays_until_due: {days_until_due}\n")
                # normalize the number of days to a value between 1 and 9
                normalized_days = 9 - min(max((days_until_due // 7), 1), 9)

                # normalize the impact to a value between 1 and 9
                impact = assignment['impact']
                normalized_impact = 9 - min(max((impact // 11), 1), 9)

                # calculate the priority as the average of the normalized values
                priority = (normalized_days + normalized_impact) // 2

                # assign the priority to the assignment
                assignment['priority'] = priority

    prioritize_assignments = copy.deepcopy(categorized_assignments)

    return prioritize_assignments # now have priority



def sort_prioritized_assignments(input_assignments):
    today = datetime.today().date()
    # Deep copy the input to avoid modifying the original data
    assignments_copy = copy.deepcopy(input_assignments)
    for category, subcategories in assignments_copy.items():
        for subcategory, assignment_list in subcategories.items():
            # Sort in place each list of assignments within their respective subcategory
            assignment_list.sort(key=lambda x: (x['due'].date() - today, -x.get('priority', 0), -x.get('impact', 0)))
    return assignments_copy

