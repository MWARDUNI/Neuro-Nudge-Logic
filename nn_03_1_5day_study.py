from datetime import datetime, timedelta
from icalendar import Calendar, Event



def create_study_plan(prioritized_assignments, start_date=None):
    if start_date is None:
        start_date = datetime.now()
    
    chunks = ["A", "B", "C", "D"]

    # the study plan
    study_plan = [
        ("Day 1", [("Prepare Chunk A", 120)]),
        ("Day 2", [("Prepare Chunk B", 120), ("Review Chunk A", 30)]),
        ("Day 3", [("Prepare Chunk C", 90), ("Review Chunk B", 30), ("Review Chunk A", 15)]),
        ("Day 4", [("Prepare Chunk D", 60), ("Review Chunk C", 30), ("Review Chunk B", 15), ("Review Chunk A", 15)]),
        ("Day 5", [("Review Chunk D", 25), ("Review Chunk C", 15), ("Review Chunk B", 10), ("Review Chunk A", 10), ("Self-test on A, B, C, D", 60)])
    ]

    cal = Calendar()
    cal.add('prodid', '-//My Study Plan//example.com//')
    cal.add('version', '2.0')

    print("\n")
    print("============================================================\n")
    print("STUDY PLAN:\n")
    high_priority_test = next((a for a in prioritized_assignments if a['type'] == 'final'), None)
    if high_priority_test:
        event_name = high_priority_test['description']
        event_due_date = high_priority_test['due_date']
        study_plan_start = event_due_date - timedelta(days=5)

        for day, activities in enumerate(study_plan, start=1):
            day_name, tasks = activities

            day_start = study_plan_start + timedelta(days=day - 1)
            for task_name, duration_mins in tasks:
                event = Event()
                event.add('summary', f'{day_name}: {task_name}')
                event.add('dtstart', day_start)
                event.add('dtend', day_start + timedelta(minutes=duration_mins))
                cal.add_component(event)



            print(f"{day_name}: {tasks} on {day_start} to {day_start + timedelta(days=1)}\n")




    with open('study_plan.ics', 'wb') as f:
        f.write(cal.to_ical())




