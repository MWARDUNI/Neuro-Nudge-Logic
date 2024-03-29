
# from nn_01_parser import parse_assignments
# from nn_02_categorizer import categorize_assignments
# from nn_03_prioritizer import calculate_impact, prioritize_assignments
# from nn_03_1_5day_study import create_study_plans_for_tests
# from nn_04_time_blocker import find_time_blocks

from nn_01_parser import *
from nn_02_categorizer import *
from nn_03_prioritizer import *
from nn_03_1_5day_study import *
from nn_04_time_blocker import *


def categorize_assignments(assignments):
    categorized = {}

    for assignment in assignments:
        class_name = assignment['class']
        assignment_type = assignment['type']

        if class_name not in categorized:
            categorized[class_name] = {}

        if assignment_type not in categorized[class_name]:
            categorized[class_name][assignment_type] = []

        categorized[class_name][assignment_type].append(assignment)

    return categorized

def add_grading_criteria(categorized_assignments, grading_info):

    for class_name, assignment_types in categorized_assignments.items():
        for assignment_type in assignment_types:
            if class_name in grading_info and assignment_type in grading_info[class_name]:
                impact = grading_info[class_name][assignment_type]
                for assignment in categorized_assignments[class_name][assignment_type]:
                    assignment['grade_impact'] = impact

    return categorized_assignments

# for testing, not from actual ics file
assignments = [
    {'due_date': '2023-04-10', 'type': 'homework', 'class': 'CSCI 4034', 'description': 'Finite Automata'},
    {'due_date': '2023-04-15', 'type': 'project', 'class': 'CSCI 3762', 'description': 'Socket Programming'},
    {'due_date': '2023-04-20', 'type': 'lab', 'class': 'CSCI 4743', 'description': 'Network Security Lab'},
    {'due_date': '2023-04-25', 'type': 'homework', 'class': 'CSCI 4287', 'description': 'Microcontroller Programming'},
    {'due_date': '2023-05-01', 'type': 'final', 'class': 'CSCI 4034', 'description': 'Comprehensive Exam'},
    {'due_date': '2023-05-05', 'type': 'final', 'class': 'CSCI 3762', 'description': 'Network Application Development'},
    {'due_date': '2023-05-10', 'type': 'project', 'class': 'CSCI 4743', 'description': 'Cyber Defense Strategy'},
    {'due_date': '2023-05-15', 'type': 'final', 'class': 'CSCI 4287', 'description': 'Embedded Systems Design'},
]

# TODO: logic for dividing up multiple assignments for proper impact
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

categorized = categorize_assignments(assignments)
categorized_with_grading = add_grading_criteria(categorized, grading_info)

print(categorized_with_grading)

categorized = categorize_assignments(assignments)
categorized_with_grading = add_grading_criteria(categorized, grading_info)

print(categorized_with_grading)
