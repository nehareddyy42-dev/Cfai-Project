# CO3 - Constraint Satisfaction Based Examination Seating Arrangement

# Concepts Used:
# CSP
# Constraints
# Filtering
# Final Decision Making

from co1 import rooms

print("FINAL EXAMINATION SEATING ARRANGEMENT SYSTEM\n")

# User Input
students = int(input("Enter Number of Students: "))

valid_rooms = []

print("\nAPPLYING CONSTRAINTS...\n")

# Constraint Satisfaction
for room in rooms:

    # Constraint checking
    if room["capacity"] >= students:

        valid_rooms.append(room)

        print(room["room"], "Accepted")
        print("Capacity:", room["capacity"])
        print()

    else:

        print(room["room"], "Rejected")
        print("Reason: Capacity Less Than Students")
        print()

# Final Recommendation
best_room = None
best_score = 9999

print("CALCULATING FINAL SELECTION...\n")

for room in valid_rooms:

    score = room["capacity"] - students

    print("Room:", room["room"])
    print("Seat Wastage:", score)
    print()

    if score < best_score:

        best_score = score
        best_room = room

print("FINAL RECOMMENDED ROOM\n")

print("Room Number:", best_room["room"])
print("Capacity:", best_room["capacity"])

print("\nReason:")

if best_room["capacity"] >= students:
    print("- Capacity satisfies constraint")

if best_score >= 0:
    print("- Minimum seat wastage")

print("- Suitable for Examination Seating")