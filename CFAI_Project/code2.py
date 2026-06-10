# CO2 - Search Based Examination Seating Arrangement

# Concepts Used:
# Search
# Heuristic Selection
# State Evaluation

from co1 import rooms

print("SEARCHING BEST EXAMINATION HALL\n")

best_room = None
best_score = -1

# User Input
students = int(input("Enter Number of Students: "))

print("\nEvaluating Rooms...\n")

for room in rooms:

    # Heuristic score calculation
    score = room["capacity"] - abs(room["capacity"] - students)

    print("Checking:", room["room"])
    print("Capacity:", room["capacity"])
    print("Calculated Score:", score)
    print()

    # Best Room Selection
    if score > best_score:

        best_score = score
        best_room = room

print("BEST ROOM FOUND USING SEARCH\n")

print("Room Number:", best_room["room"])
print("Best Score:", best_score)