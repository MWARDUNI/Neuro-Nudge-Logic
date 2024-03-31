
from datetime import datetime


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
    # Check if 'due_date' is a datetime object and use it directly
    assignments_flat.sort(key=lambda x: (x['due_date'].date() - today, -x.get('impact', 0)))
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
from nn_02_categorizer import categorize_assignments, add_grading_criteria
# assignments_with_impact = calculate_impact(categorized_with_grading, grading_info)
# assignments_with_impact = calculate_impact(categorize_assignments, grade_impact_individually)

# prioritized_assignments = prioritize_assignments(assignments_with_impact)

# print(prioritized_assignments)


