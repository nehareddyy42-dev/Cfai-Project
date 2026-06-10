"""
Hybrid Explainable AI-Based Smart Exam Seating System
======================================================
Covers: Agent Model, A*, CSP (MRV/LCV/Backtracking),
        Utility Functions, Bayesian Risk, Explainable AI

Course: Computational Foundations for AI
"""

import csv
import time
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional


# ==============================================================
# CO1 - AGENT MODEL & DATA STRUCTURES
# ==============================================================

@dataclass(frozen=True)
class Student:
    sid: int
    name: str
    branch: str
    gpa: float
    trust_score: int
    malpractice_count: int


@dataclass(frozen=True)
class Hall:
    room_no: str
    rows: int
    cols: int


@dataclass(frozen=True)
class Seat:
    room: str
    row: int
    col: int

    def is_adjacent(self, other: "Seat") -> bool:
        return (
            self.room == other.room
            and abs(self.row - other.row) <= 1
            and abs(self.col - other.col) <= 1
        )


# Type alias for readability
Assignment = dict[Student, Seat]


# ==============================================================
# PROBLEM DATA
# ==============================================================

STUDENTS: list[Student] = [
    Student(1, "Harshith", "CSE",  9.5, 95, 0),
    Student(2, "Rahul",    "ECE",  5.5, 30, 2),
    Student(3, "Kiran",    "AIDS", 8.8, 90, 0),
    Student(4, "Arjun",    "CSE",  6.0, 45, 1),
    Student(5, "Varun",    "ECE",  9.2, 92, 0),
    Student(6, "Sai",      "MECH", 5.2, 25, 3),
    Student(7, "Teja",     "AIDS", 7.8, 80, 0),
    Student(8, "Manoj",    "CSE",  4.9, 20, 4),
]


HALLS: list[Hall] = [
    Hall("A101", 4, 4),
    Hall("A102", 4, 4),
]

ALL_SEATS: list[Seat] = [
    Seat(hall.room_no, r, c)
    for hall in HALLS
    for r in range(hall.rows)
    for c in range(hall.cols)
]


# ==============================================================
# CO4 - UTILITY & CO5 - BAYESIAN RISK
# ==============================================================

def utility_score(student: Student) -> float:
    """
    Composite utility: reward high trust and GPA,
    penalise prior malpractice.
    """
    return (
        student.trust_score
        + student.gpa * 10
        - student.malpractice_count * 20
    )


def cheating_probability(student: Student) -> float:
    """
    Naive Bayes estimate of cheating risk.
    Prior: 10 %. Each risk factor multiplies the evidence weight.
    """
    PRIOR = 0.10
    evidence = 0.50

    if student.trust_score < 40:
        evidence += 0.30
    if student.gpa < 6.0:
        evidence += 0.20
    if student.malpractice_count > 0:
        evidence += 0.40

    return min(PRIOR * evidence * 2, 1.0)


# ==============================================================
# CO2 - HEURISTIC (used by A* evaluation & LCV)
# ==============================================================

def placement_risk(student: Student, seat: Seat, assignments: Assignment) -> int:
    """
    Estimates risk of placing `student` at `seat` given existing
    assignments. Used as the h(n) component of A*.

    Higher score = riskier placement (A* minimises f = g + h).
    """
    risk = 0
    for neighbour, neighbour_seat in assignments.items():
        if not seat.is_adjacent(neighbour_seat):
            continue
        if abs(student.gpa - neighbour.gpa) > 2:
            risk += 15
        if student.trust_score < 40:
            risk += 20
    return risk


def a_star_cost(student: Student, seat: Seat, assignments: Assignment) -> int:
    """f(n) = g(n) + h(n)  where g = depth, h = placement_risk."""
    g = len(assignments)
    h = placement_risk(student, seat, assignments)
    return g + h


# ==============================================================
# CO3 - CSP: CONSTRAINT CHECKING
# ==============================================================

class ConstraintViolation(Exception):
    """Raised when a placement violates a hard constraint."""


def _check_constraints(student: Student, seat: Seat, assignments: Assignment) -> None:
    """
    Raises ConstraintViolation with a human-readable reason if any
    hard constraint is broken. Returns None if the placement is valid.

    Constraints enforced:
        1. No two students share a seat.
        2. GPA gap > 2 -> students must not be adjacent (anti-cheating).
        3. Trust score < 40 -> student must not be adjacent to anyone.
    """
    occupied = assignments.values()

    if seat in occupied:
        raise ConstraintViolation(f"Seat {seat} is already taken.")

    for other, other_seat in assignments.items():
        adjacent = seat.is_adjacent(other_seat)

        if not adjacent:
            continue

        if abs(student.gpa - other.gpa) > 2:
            raise ConstraintViolation(
                f"GPA gap too large: {student.name} (GPA {student.gpa}) "
                f"cannot sit adjacent to {other.name} (GPA {other.gpa})."
            )

        if student.trust_score < 40:
            raise ConstraintViolation(
                f"Low trust: {student.name} (score {student.trust_score}) "
                f"requires isolated monitored seating."
            )




def is_valid(student: Student, seat: Seat, assignments: Assignment) -> bool:
    """Returns True iff placing student at seat satisfies all constraints."""
    try:
        _check_constraints(student, seat, assignments)
        return True
    except ConstraintViolation:
        return False


# ==============================================================
# CO3 - CSP: MRV & LCV HEURISTICS
# ==============================================================

def _count_valid_seats(student: Student, assignments: Assignment) -> int:
    """Number of seats still legally available for this student."""
    taken = set(assignments.values())
    return sum(
        1 for seat in ALL_SEATS
        if seat not in taken and is_valid(student, seat, assignments)
    )


def select_by_mrv(assignments: Assignment) -> Optional[Student]:
    """
    Minimum Remaining Values: pick the unassigned student with the
    fewest valid seat options (most constrained first).
    """
    unassigned = [s for s in STUDENTS if s not in assignments]
    if not unassigned:
        return None
    return min(unassigned, key=lambda s: _count_valid_seats(s, assignments))


def order_by_lcv(student: Student, assignments: Assignment) -> list[Seat]:
    """
    Least Constraining Value: order available seats by how little
    they restrict future students (lowest risk score first).
    """
    taken = set(assignments.values())
    candidates = [s for s in ALL_SEATS if s not in taken]
    return sorted(candidates, key=lambda seat: placement_risk(student, seat, assignments))


# ==============================================================
# CO3 - BACKTRACKING SEARCH
# ==============================================================

class Solver:
    """
    CSP solver using backtracking with MRV + LCV + A* ordering.
    Tracks node expansions for performance analysis.
    """

    def __init__(self) -> None:
        self.node_expansions: int = 0
        self._violation_log: list[str] = []

    def solve(self, assignments: Optional[Assignment] = None) -> Optional[Assignment]:
        if assignments is None:
            assignments = {}

        self.node_expansions += 1

        if len(assignments) == len(STUDENTS):
            return assignments

        student = select_by_mrv(assignments)
        if student is None:
            return None

        for seat in order_by_lcv(student, assignments):
            try:
                _check_constraints(student, seat, assignments)
            except ConstraintViolation as exc:
                self._violation_log.append(str(exc))
                continue

            assignments[student] = seat
            result = self.solve(assignments)
            if result is not None:
                return result
            del assignments[student]

        return None

    @property
    def violations_summary(self) -> str:
        counts: dict[str, int] = defaultdict(int)
        for msg in self._violation_log:
            kind = msg.split(":")[0]
            counts[kind] += 1
        lines = [f"  {k}: {v} pruned branches" for k, v in counts.items()]
        return "\n".join(lines) if lines else "  (none)"


# ==============================================================
# CO6 - EXPLAINABLE AI
# ==============================================================

def explain_placement(student: Student, seat: Seat, assignments: Assignment) -> str:
    """
    Returns a plain-language explanation of why a student was
    placed at a given seat.
    """
    risk = cheating_probability(student)
    reasons: list[str] = []

    if student.trust_score < 40:
        reasons.append("low trust score -> monitored/isolated zone required")
    if student.gpa < 6.0:
        reasons.append("GPA below threshold -> elevated cheating risk factor")
    if student.malpractice_count > 0:
        reasons.append(
            f"{student.malpractice_count} prior malpractice record(s) on file"
        )
    if not reasons:
        reasons.append("no special risk factors; standard placement")

    lines = [
        f"  Student  : {student.name} (ID {student.sid}, {student.branch})",
        f"  Seat     : {seat.room} - row {seat.row}, col {seat.col}",
        f"  GPA      : {student.gpa:.1f}   Trust: {student.trust_score}   "
        f"Utility: {utility_score(student):.1f}",
        f"  Risk     : {risk:.0%} estimated cheating probability",
        f"  Rationale: {'; '.join(reasons)}",
    ]
    return "\n".join(lines)


# ==============================================================
# VISUALISATION
# ==============================================================

def visualize_seating(solution: Assignment) -> None:
    """
    Prints a grid for each hall.

    Legend:
        T  - top student (GPA > 9.0)
        R  - high-risk student (trust score < 40)
        *  - standard assignment
        .  - empty seat
    """
    hall_map: dict[str, list[tuple[Student, Seat]]] = defaultdict(list)
    for student, seat in solution.items():
        hall_map[seat.room].append((student, seat))

    for hall in HALLS:
        print(f"\n  Hall {hall.room_no}  ({hall.rows}x{hall.cols})")
        print("  " + "-" * (hall.cols * 6 - 1))

        grid: list[list[str]] = [
            ["  .  " for _ in range(hall.cols)] for _ in range(hall.rows)
        ]

        for student, seat in hall_map[hall.room_no]:
            if student.gpa > 9.0:
                label = f"[T:{student.name[:3]}]"
            elif student.trust_score < 40:
                label = f"[R:{student.name[:3]}]"
            else:
                label = f"[ {student.name[:3]} ]"
            grid[seat.row][seat.col] = label

        for row in grid:
            print("  " + " ".join(f"{cell:^8}" for cell in row))

        print("  " + "-" * (hall.cols * 6 - 1))
        print("  Legend: [T:xxx] top GPA  [R:xxx] high-risk  [ xxx ] standard")


# ==============================================================
# MAIN
# ==============================================================

def main() -> None:
    print("=" * 60)
    print("  HYBRID XAI EXAM SEATING SYSTEM")
    print("=" * 60)

    print(f"\n  Students : {len(STUDENTS)}")
    print(f"  Halls    : {len(HALLS)}  ({len(ALL_SEATS)} total seats)")

    solver = Solver()
    t0 = time.perf_counter()
    solution = solver.solve()
    elapsed = time.perf_counter() - t0

    print("\n" + "=" * 60)
    print("  SEATING ASSIGNMENTS + XAI EXPLANATIONS")
    print("=" * 60)

    if solution is None:
        print("\n  ERROR: No valid seating arrangement could be found.")
        print("  Check that enough seats exist and constraints are satisfiable.")
        return

    for student, seat in sorted(solution.items(), key=lambda x: x[0].sid):
        print()
        print(explain_placement(student, seat, solution))

    visualize_seating(solution)

    print("\n" + "=" * 60)
    print("  PERFORMANCE PROFILE")
    print("=" * 60)
    print(f"  Runtime          : {elapsed:.4f} s")
    print(f"  Node expansions  : {solver.node_expansions}")
    print(f"\n  Constraint violations pruned:\n{solver.violations_summary}")

    print("\n" + "=" * 60)
    print("  ETHICS & LIMITATIONS")
    print("=" * 60)
    notes = [
        "Low GPA is a risk proxy, not proof of dishonesty.",
        "Trust scores may carry historical or demographic bias.",
        "Bayesian estimates are probabilistic - not determinations.",
        "All automated placements must be reviewed by a human invigilator.",
        "System is designed to support, not replace, human judgment.",
    ]
    for i, note in enumerate(notes, 1):
        print(f"  {i}. {note}")

    print("\n  System completed successfully.\n")


if __name__ == "__main__":
    main()