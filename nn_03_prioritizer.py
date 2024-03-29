
from datetime import datetime


# from nn_01_parser import parse_assignments
from nn_02_categorizer import categorize_assignments
# from nn_03_prioritizer import calculate_impact, prioritize_assignments
# from nn_03_1_5day_study import create_study_plans_for_tests
# from nn_04_time_blocker import find_time_blocks

from nn_01_parser import *
from nn_02_categorizer import *
from nn_03_prioritizer import *
from nn_03_1_5day_study import *
from nn_04_time_blocker import *


def calculate_impact(assignments, grading_info):
    for class_name, types in assignments.items():
        for assignment_type, assignment_list in types.items():
            for assignment in assignment_list:
                impact = grading_info.get(class_name, {}).get(assignment_type, 0)
                assignment['impact'] = impact
    return assignments

def prioritize_assignments(assignments):
    today = datetime.today().date()
    assignments_flat = [item for sublist in assignments.values() for subsublist in sublist.values() for item in subsublist]
    assignments_flat.sort(key=lambda x: (datetime.strptime(x['due_date'], '%Y-%m-%d').date() - today, -x.get('impact', 0)))
    return assignments_flat

# impacts on final grade for each assignment type
grading_info = {
    # Theory
    'CSCI 4034': {'homework': 20, 'project': 30, 'final': 50},
    # Network Programming
    'CSCI 3762': {'homework': 15, 'project': 35, 'final': 50},
    # Security
    'CSCI 4743': {'lab': 25, 'project': 35, 'final': 40},
    # Embedded Systems
    'CSCI 4287': {'homework': 20, 'project': 30, 'final': 50}
}


assignments_with_impact = calculate_impact(categorize_assignments.categorized_with_grading, grading_info)


prioritized_assignments = prioritize_assignments(assignments_with_impact)

print(prioritized_assignments)


