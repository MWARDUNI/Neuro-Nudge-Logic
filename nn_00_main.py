
from nn_01_parser import parse_assignments
from nn_02_categorizer import categorize_assignments
from nn_03_prioritizer import calculate_impact, prioritize_assignments
from nn_03_1_5day_study import create_study_plans_for_tests
from nn_04_time_blocker import find_time_blocks

from nn_01_parser import *
from nn_02_categorizer import *
from nn_03_prioritizer import *
from nn_03_1_5day_study import *
from nn_04_time_blocker import *


def main():
    # nn_01_parser.py
    assignments = parse_assignments('assignments_data_source.txt')  # Example file name

    # nn_02_categorizer.py
    categorized_assignments = categorize_assignments(assignments)

    # Impacts on final grade for each assignment type
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

    # nn_03_prioritizer.py
    assignments_with_impact = calculate_impact(categorized_assignments, grading_info)

    # nn_03_prioritizer.py
    prioritized_assignments = prioritize_assignments(assignments_with_impact)

    # nn_03_1_5day_study.py
    create_study_plans_for_tests(prioritized_assignments)

    # nn_04_time_blocker.py
    personal_schedule = [
        
        ('2023-04-10', '2023-04-11'),
        ('2023-04-15', '2023-04-16'),

    ]

    suitable_assignments = find_time_blocks(prioritized_assignments, personal_schedule)

    print(suitable_assignments)

if __name__ == '__main__':
    main()
