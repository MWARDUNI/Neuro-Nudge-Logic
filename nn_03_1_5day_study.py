from datetime import datetime, timedelta
from icalendar import Calendar, Event
from supabase import Client, create_client
import uuid

# References:
# Blerkom, D. L. (2012). Orientation to college learning (7 edition). Boston: Engage
# Blerkom, D. L. and Mulcahy-Ernt, P. I. (2004). College reading and study strategies. Boston: Cengage.
# Texas A&M University Academic Success Center (n.d.). 5 day study plan. https://asc.tamu.edu/study-learning-handouts/5-day-study-plan



def create_study_plan(supabase: Client, start_date=None):
    
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

    try:
        # get all midterm and final assignments
        response = supabase.table("assignments").select("*").in_("type", ["final", "midterm"]).order("due").execute()

        prioritized_assignments = response.data
        

        print("\n")
        print("============================================================\n")
        print("STUDY PLAN:\n")

        # by class and type of test
        assignments_by_class_type = {}
        for assignment in prioritized_assignments:
            class_name = assignment['class']
            assignment_type = assignment['type']
            if class_name not in assignments_by_class_type:
                assignments_by_class_type[class_name] = {}
            if assignment_type not in assignments_by_class_type[class_name]:
                assignments_by_class_type[class_name][assignment_type] = []
            assignments_by_class_type[class_name][assignment_type].append(assignment)

        # create study plans for each class and type of test (midterm, final)
        study_plan_events = []
        for class_name, assignments_by_type in assignments_by_class_type.items():
            for assignment_type, assignments in assignments_by_type.items():
                print(f"Study Plan for {class_name} - {assignment_type}:\n")
                for assignment in assignments:
                    event_name = assignment['description']
                    event_due_date = datetime.fromisoformat(assignment['due'])
                    study_plan_start = event_due_date - timedelta(days=5)

                    for day, activities in enumerate(study_plan, start=1):
                        day_name, tasks = activities

                        day_start = study_plan_start + timedelta(days=day - 1)
                        last_time = day_start
                        for task_name, duration_mins in tasks:
                            event = Event()
                            event.add('summary', f'{day_name}: {task_name} - {class_name} - {assignment_type}')
                            event.add('dtstart', day_start)
                            event.add('dtend', day_start + timedelta(minutes=duration_mins))
                            cal.add_component(event)
                            
                            next_time = (last_time + timedelta(minutes=duration_mins))
                            # add study plan event to the list
                            study_plan_events.append({
                                'uid': str(uuid.uuid4()),
                                'summary': class_name,
                                'description': f'{day_name}: {task_name} - {assignment_type}',
                                'start_time': last_time.isoformat(),
                                'end_time': next_time.isoformat(),
                                'impact': assignment['impact']
                            })
                            last_time = next_time

                        print(f"{day_name}: {tasks} on {day_start} to {day_start + timedelta(days=1)}\n")

        # sort study plan events by impact in descending order
        study_plan_events.sort(key=lambda x: x['impact'], reverse=True)
        # print(study_plan_events)
        supabase.table("events").upsert(study_plan_events).execute()


    except Exception as e:
        print(f"Error: {str(e)}")
        
        
if __name__ == "__main__":
    # Initialize the Supabase client
    url = "https://fgocfoakntmlhgtftrzh.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnb2Nmb2FrbnRtbGhndGZ0cnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTE2ODkyMTUsImV4cCI6MjAyNzI2NTIxNX0.s5dAWy-DSa1EBfKjhpGOOcax6S7QUsh7xCHPFgKlBn8"
    supabase: Client = create_client(url, key)
    create_study_plan(supabase)




# Prepare Strategies:
# Develop study sheets or study guides
# Make flash cards
# Outline/summarize material
# Develop concept maps or charts (make sure you use use linking terms)
# List the steps in a complex process or develop a flow chart
# Make a list of 20 topics that could be on the exam. Be able to explain why you think they might be on the test.
# Predict (and answer!) practice test/essay questions
# Answer questions at the end of the chapter (that weren’t assigned as HW)
# Prepare material for a study group


# Review Strategies:
# Explain concepts to others
# Use your quizlets or flash cards
# Work problems (no looking at answer keys!)
# Take self-tests (try to mimic test conditions if you can)
# Recite from memory (better yet, tell your cat or favorite pillow) your list of 20 topics that could be on the exam.
# Work the problems that you missed on quizzes, HW, or questions at the end of the chapter
# Outline answers to essay questions from memory
# Write a full sample essay
# Explain material to group members or study partners

