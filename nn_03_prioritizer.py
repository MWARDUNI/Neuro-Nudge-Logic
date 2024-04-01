
from datetime import datetime


# adds impact value to each assignment based on assignment type and 
def calculate_impact(categorized_assignments, grade_impact_key):
    for class_name, assignment_types in categorized_assignments.items():
        for assignment_type, assignments in assignment_types.items():
            for assignment in assignments:
                # Now correctly fetching impact value
                impact = grade_impact_key.get(class_name, {}).get(assignment_type, 0)
                assignment['impact'] = impact
    return categorized_assignments


# def calculate_impact(assignments, grade_impact_key):
#     # Iterate through the list of assignment dictionaries
#     for assignment in assignments:
#         class_name = assignment['class']
#         assignment_type = assignment['type']
#         # Fetch the impact value from the grading_info based on class_name and assignment_type
#         impact = grade_impact_key.get(class_name, {}).get(assignment_type, 0)
#         # Update the assignment dict with the impact value
#         assignment['impact'] = impact
#     return assignments


def prioritize_assignments(assignments):
    today = datetime.today().date()
    assignments_flat = [item for sublist in assignments.values() for subsublist in sublist.values() for item in subsublist]
    # if 'due_date' is a datetime object and use it directly
    assignments_flat.sort(key=lambda x: (x['due'].date() - today, -x.get('impact', 0)))
    return assignments_flat


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


