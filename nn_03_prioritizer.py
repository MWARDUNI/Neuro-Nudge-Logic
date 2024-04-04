
from datetime import datetime


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


def calculate_impact(categorized_assignments, grade_impact_key):
    for class_name, assignment_types in categorized_assignments.items():
        class_impact = grade_impact_key.get(class_name, {})
        for assignment_type, assignments in assignment_types.items():
            impact = class_impact.get(assignment_type, 0)
            for assignment in assignments:
                # add the impact
                assignment['impact'] = impact
                # set status to required "VTODO" property
                assignment['status'] = 'NEEDS-ACTION'
    return categorized_assignments


exams = {}



# def extract_exams(categorized_assignments):
#     for course, tasks in categorized_assignments.items():
#         for task_type, details in list(tasks.items()):
#             if task_type in ["midterm", "final"]:
#                 if course not in exams:
#                     exams[course] = {}
#                 exams[course][task_type] = details
#                 del categorized_assignments[course][task_type]
#     return exams



# def prioritize_assignments(assignments):

#     today = datetime.today().date()

#     assignments_flat = [item for sublist in assignments.values() for subsublist in sublist.values() for item in subsublist]

#     # if 'due_date' is a datetime object and use it directly
#     assignments_flat.sort(key=lambda x: (x['due'].date() - today, -x.get('impact', 0)))

#     return assignments_flat

