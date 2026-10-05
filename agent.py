# ============================================================
# CAREBED AI - BED ALLOCATION AGENT
# ============================================================

from database import get_available_beds


# ------------------------------------------------------------
# PRIORITY SCORES
# ------------------------------------------------------------

PRIORITY_SCORE = {
    "Emergency": 100,
    "ICU": 90,
    "High": 75,
    "Medium": 50,
    "Low": 25
}


# ------------------------------------------------------------
# BED TYPE COMPATIBILITY
# ------------------------------------------------------------

def get_required_bed_type(department, priority):

    if priority == "Emergency":
        return "Emergency"

    if department == "ICU":
        return "ICU"

    if department == "Pediatrics":
        return "Pediatric"

    if department == "Cardiology":
        return "Cardiac"

    return "Normal"


# ------------------------------------------------------------
# CALCULATE BED SUITABILITY SCORE
# ------------------------------------------------------------

def calculate_bed_score(
    department,
    priority,
    required_bed_type,
    bed
):

    bed_id = bed[0]
    bed_number = bed[1]
    bed_department = bed[2]
    bed_type = bed[3]
    floor = bed[4]
    status = bed[5]

    score = 0

    reasons = []

    # --------------------------------------------------------
    # Department Match
    # --------------------------------------------------------

    if bed_department.lower() == department.lower():

        score += 50

        reasons.append(
            "Department matches patient requirement"
        )

    else:

        score -= 20

        reasons.append(
            "Department does not exactly match"
        )

    # --------------------------------------------------------
    # Bed Type Match
    # --------------------------------------------------------

    if bed_type.lower() == required_bed_type.lower():

        score += 30

        reasons.append(
            "Bed type is suitable"
        )

    else:

        score -= 10

        reasons.append(
            "Bed type is not an exact match"
        )

    # --------------------------------------------------------
    # Availability
    # --------------------------------------------------------

    if status == "Available":

        score += 10

        reasons.append(
            "Bed is currently available"
        )

    # --------------------------------------------------------
    # Priority
    # --------------------------------------------------------

    patient_priority_score = PRIORITY_SCORE.get(
        priority,
        25
    )

    score += patient_priority_score * 0.1

    reasons.append(
        f"Patient priority: {priority}"
    )

    # --------------------------------------------------------
    # Floor Preference
    # --------------------------------------------------------

    if priority in ["Emergency", "ICU"]:

        if floor <= 3:

            score += 10

            reasons.append(
                "Lower floor is preferred for urgent cases"
            )

    return round(score, 2), reasons


# ------------------------------------------------------------
# FIND BEST BED
# ------------------------------------------------------------

def recommend_bed(
    department,
    priority
):

    available_beds = get_available_beds()

    if not available_beds:

        return {
            "success": False,
            "message": "No beds are currently available.",
            "recommendation": None,
            "alternatives": []
        }

    required_bed_type = get_required_bed_type(
        department,
        priority
    )

    recommendations = []

    for bed in available_beds:

        score, reasons = calculate_bed_score(
            department,
            priority,
            required_bed_type,
            bed
        )

        recommendation = {

            "bed_id": bed[0],

            "bed_number": bed[1],

            "department": bed[2],

            "bed_type": bed[3],

            "floor": bed[4],

            "status": bed[5],

            "score": score,

            "reasons": reasons
        }

        recommendations.append(
            recommendation
        )

    # Sort highest score first
    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    best_bed = recommendations[0]

    alternatives = recommendations[1:4]

    return {

        "success": True,

        "message": "Suitable bed found.",

        "required_bed_type": required_bed_type,

        "recommendation": best_bed,

        "alternatives": alternatives
    }


# ------------------------------------------------------------
# GENERATE HUMAN-READABLE EXPLANATION
# ------------------------------------------------------------

def generate_explanation(
    patient_name,
    department,
    priority,
    recommendation
):

    if recommendation is None:

        return "No suitable bed recommendation available."

    bed_number = recommendation["bed_number"]

    bed_department = recommendation["department"]

    bed_type = recommendation["bed_type"]

    floor = recommendation["floor"]

    score = recommendation["score"]

    explanation = f"""
Patient: {patient_name}

Priority: {priority}

Requested Department: {department}

Recommended Bed: {bed_number}

Bed Department: {bed_department}

Bed Type: {bed_type}

Floor: {floor}

Suitability Score: {score}

Why this bed was selected:
"""

    for reason in recommendation["reasons"]:

        explanation += f"\n✓ {reason}"

    explanation += """

IMPORTANT:
This is an AI-assisted recommendation.
Final allocation should be approved by authorized
hospital staff.
"""

    return explanation


# ------------------------------------------------------------
# ALLOCATION DECISION SUMMARY
# ------------------------------------------------------------

def get_agent_decision(
    patient_name,
    department,
    priority
):

    result = recommend_bed(
        department,
        priority
    )

    if not result["success"]:

        return {

            "status": "NO_BED",

            "message": result["message"],

            "explanation":
                f"No suitable bed is currently available "
                f"for {patient_name}."
        }

    best_bed = result["recommendation"]

    explanation = generate_explanation(
        patient_name,
        department,
        priority,
        best_bed
    )

    return {

        "status": "RECOMMENDED",

        "message":
            f"Bed {best_bed['bed_number']} "
            f"is recommended.",

        "recommendation":
            best_bed,

        "alternatives":
            result["alternatives"],

        "explanation":
            explanation
    }


# ------------------------------------------------------------
# TEST THE AGENT
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)

    print("CAREBED AI - BED ALLOCATION AGENT")

    print("=" * 60)

    patient_name = "Rahul Das"

    department = "General Medicine"

    priority = "High"

    result = get_agent_decision(
        patient_name,
        department,
        priority
    )

    print("\nAGENT RESULT")
    print("-" * 60)

    print(result["message"])

    print("\n")

    print(result["explanation"])

    if result["alternatives"]:

        print("\nALTERNATIVE BEDS")
        print("-" * 60)

        for bed in result["alternatives"]:

            print(
                f"{bed['bed_number']} | "
                f"{bed['department']} | "
                f"{bed['bed_type']} | "
                f"Score: {bed['score']}"
            )