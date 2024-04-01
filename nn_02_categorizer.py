

from nn_01_parser import events, assignments 

def categorize_assignments(assignments):
    if not assignments:  # Check if the list is empty
        return {}
    
    if not isinstance(assignments, list) or not all(isinstance(assignment, dict) for assignment in assignments):
        raise ValueError("assignments must be a list of dictionaries")
    
    categorized = {}
    for assignment in assignments:
        class_name = assignment.get('class', 'Unknown Class')
        assignment_type = assignment.get('type', 'Unknown Type')
        
        if class_name not in categorized:
            categorized[class_name] = {}
        
        if assignment_type not in categorized[class_name]:
            categorized[class_name][assignment_type] = []
        
        categorized[class_name][assignment_type].append(assignment)


    return categorized

