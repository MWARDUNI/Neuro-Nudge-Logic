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
