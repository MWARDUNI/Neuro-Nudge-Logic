# nn_logic
This is the python implementation for the backend logic for neuro-nudge.

```icalendar

`RELATED-TO` via `UID`

`VEVENT`: `DTSTART`, `DTEND`
  `RRULE`: lectures, actual class, quiz, test (timebound events)
  `STATUS`: CONFIRMED (default), TENTATIVE, CANCELLED
  
`VTODO`: `DUE`, `STATUS`
  homework, labs, projects
  `STATUS`: NEEDS-ACTION (default), IN-PROCESS, COMPLETED, CANCELLED
  
`CATEGORIES`
  allow for filtering or organizing events and tasks by subject, course, or other classifications

`VALARM`: "NUDGE"
  BEGIN:VALARM
  TRIGGER: -PT30M
  ACTION: DISPLAY
  DESCRIPTION: Nudge: Day 1 of 5 for study plan
  END: VALARM
  
`CLASS`
  FOR VEVENT || VTODO
    public, private, confidential

```
### nn_00: Driver Code
- **Contains Steps**: 1 - 4

### nn_01: Parse the iCalendar Data
- **Read the .ics File**: extract events and details (start time, end time, description, and summary).

- **Event Types**: In details, find class schedules and various assignments (homework, projects, midterms, labs, finals, quizzes).

- **Extract Metadata**: For each assignment, extract relevant metadata: due date, assignment type, and associated class.

- **Standardize Data Format**: UTC, all dates and times are in a consistent format to facilitate comparison and scheduling.

### nn_02: Categorize Assignments
- **Categorizes by Type and Class**: Organize assignments by type and class they belong to.

- **Grading Criteria**: This is the "syllabus" weight and impact on the grade.

### nn_03: Prioritize Assignments
- **Calculate Impact on Final Grade**: Uses grading criteria to calculate the impact of each assignment on the final grade. To be tweaked.

- **Due Dates**: Factor in the due dates to prioritize assignments. Assignments with a high impact on the final grade and an approaching due date should be prioritized.

### nn_03.1: 5 Day Study Blocker
- **Study Plan**: If event is 'test', 'final', 'midterm' create a 5-day study plan to prepare for such by creating block events for each day leading up to the test in digestible "chunks".


# TODO
### nn_04: Time Blocker
- **Personal Schedule/Availability**: Integrate class schedules and personal commitments to find time blocks for completing assignments. Prioritizes assignments based on their impact and urgency.
(This needs work for sure. Personal schedule is not yet integrated. timeblock as well.)

### nn_05: Nudge Generator
- **Nudge**: Generate nudges for upcoming assignments and study plans. Nudges are reminders to complete assignments or study for tests.

### nn_06: Dynamic Scheduler