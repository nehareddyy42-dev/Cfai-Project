# CO1 - Intelligent Agent Based Examination Seating Arrangement System

# Concepts Used:
# Agent Model (PEAS)
# State Representation
# Knowledge Representation
# Dataclass
# Lists, Dictionaries, Sets
# Trace Logging

from dataclasses import dataclass

print("INTELLIGENT AGENT BASED EXAMINATION SEATING ARRANGEMENT\n")

# PEAS Model
print("PEAS MODEL")
print("Performance Measure : Allocate seats without exceeding room capacity")
print("Environment         : Examination Hall")
print("Actuators           : Display Seating Arrangement")
print("Sensors             : Student Count and Room Information\n")

# State Representation
@dataclass
class ExamState:
    students: int


# Knowledge Representation
rooms = [

    {
        "room": "A101",
        "capacity": 30
    },

    {
        "room": "A102",
        "capacity": 40
    },

    {
        "room": "A103",
        "capacity": 50
    },

    {
        "room": "A104",
        "capacity": 60
    }

]

# User Input
students = int(input("Enter Number of Students: "))

# Initial State
state = ExamState(students)

print("\nSTATE CREATED")
print(state)

print("\nAGENT REASONING PROCESS\n")

allocated = []

visited = set()

remaining = students

for room in rooms:

    print("Checking:", room["room"])

    action = "Allocate Room"

    if remaining > 0:

        allocated.append(room)
        visited.add(room["room"])

        remaining -= room["capacity"]

        print("Action:", action)
        print("Result : Room Accepted\n")

    else:

        print("Action:", action)
        print("Result : Room Rejected\n")

# Goal Test
print("FINAL SEATING ARRANGEMENT\n")

for room in allocated:

    print("Room :", room["room"])
    print("Capacity :", room["capacity"])
    print()

print("VISITED STATES")
print(visited)