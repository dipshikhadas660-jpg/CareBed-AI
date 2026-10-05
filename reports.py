# ============================================================
# CAREBED AI - REPORTS AND ANALYTICS
# ============================================================

from database import (
    get_connection,
    get_statistics,
    get_all_beds,
    get_all_patients,
    get_active_allocations
)


# ------------------------------------------------------------
# BED OCCUPANCY PERCENTAGE
# ------------------------------------------------------------

def get_occupancy_percentage():

    stats = get_statistics()

    total = stats["total_beds"]

    occupied = stats["occupied_beds"]

    if total == 0:
        return 0

    percentage = (occupied / total) * 100

    return round(percentage, 2)


# ------------------------------------------------------------
# AVAILABLE BED PERCENTAGE
# ------------------------------------------------------------

def get_available_percentage():

    stats = get_statistics()

    total = stats["total_beds"]

    available = stats["available_beds"]

    if total == 0:
        return 0

    percentage = (available / total) * 100

    return round(percentage, 2)


# ------------------------------------------------------------
# DEPARTMENT-WISE BED COUNT
# ------------------------------------------------------------

def get_department_bed_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            department,
            COUNT(*) AS total_beds,
            SUM(
                CASE
                    WHEN status = 'Available'
                    THEN 1
                    ELSE 0
                END
            ) AS available_beds,
            SUM(
                CASE
                    WHEN status = 'Occupied'
                    THEN 1
                    ELSE 0
                END
            ) AS occupied_beds
        FROM beds
        GROUP BY department
        ORDER BY department
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# ------------------------------------------------------------
# BED TYPE STATISTICS
# ------------------------------------------------------------

def get_bed_type_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            bed_type,
            COUNT(*) AS total,
            SUM(
                CASE
                    WHEN status = 'Available'
                    THEN 1
                    ELSE 0
                END
            ) AS available,
            SUM(
                CASE
                    WHEN status = 'Occupied'
                    THEN 1
                    ELSE 0
                END
            ) AS occupied
        FROM beds
        GROUP BY bed_type
        ORDER BY bed_type
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# ------------------------------------------------------------
# PATIENT PRIORITY STATISTICS
# ------------------------------------------------------------

def get_priority_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            priority,
            COUNT(*) AS total
        FROM patients
        GROUP BY priority
        ORDER BY
            CASE priority
                WHEN 'Emergency' THEN 1
                WHEN 'ICU' THEN 2
                WHEN 'High' THEN 3
                WHEN 'Medium' THEN 4
                WHEN 'Low' THEN 5
                ELSE 6
            END
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# ------------------------------------------------------------
# PATIENT STATUS STATISTICS
# ------------------------------------------------------------

def get_patient_status_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            status,
            COUNT(*) AS total
        FROM patients
        GROUP BY status
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# ------------------------------------------------------------
# DEPARTMENT-WISE PATIENT COUNT
# ------------------------------------------------------------

def get_department_patient_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            department,
            COUNT(*) AS total_patients
        FROM patients
        GROUP BY department
        ORDER BY total_patients DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# ------------------------------------------------------------
# RECENT PATIENTS
# ------------------------------------------------------------

def get_recent_patients(limit=10):

    patients = get_all_patients()

    return patients[:limit]


# ------------------------------------------------------------
# RECENT ALLOCATIONS
# ------------------------------------------------------------

def get_recent_allocations(limit=10):

    allocations = get_active_allocations()

    return allocations[:limit]


# ------------------------------------------------------------
# COMPLETE DASHBOARD SUMMARY
# ------------------------------------------------------------

def get_dashboard_summary():

    stats = get_statistics()

    occupancy = get_occupancy_percentage()

    available_percentage = get_available_percentage()

    return {

        "total_beds":
            stats["total_beds"],

        "available_beds":
            stats["available_beds"],

        "occupied_beds":
            stats["occupied_beds"],

        "maintenance_beds":
            stats["maintenance_beds"],

        "waiting_patients":
            stats["waiting_patients"],

        "admitted_patients":
            stats["admitted_patients"],

        "occupancy_percentage":
            occupancy,

        "available_percentage":
            available_percentage
    }


# ------------------------------------------------------------
# DEPARTMENT REPORT
# ------------------------------------------------------------

def get_department_report():

    data = get_department_bed_statistics()

    report = []

    for row in data:

        department = row[0]

        total = row[1]

        available = row[2] or 0

        occupied = row[3] or 0

        if total > 0:

            occupancy = round(
                (occupied / total) * 100,
                2
            )

        else:

            occupancy = 0

        report.append({

            "department":
                department,

            "total_beds":
                total,

            "available_beds":
                available,

            "occupied_beds":
                occupied,

            "occupancy":
                occupancy
        })

    return report


# ------------------------------------------------------------
# GENERATE TEXT REPORT
# ------------------------------------------------------------

def generate_text_report():

    summary = get_dashboard_summary()

    department_report = get_department_report()

    report = ""

    report += "=" * 60
    report += "\n"
    report += "CAREBED AI - HOSPITAL BED REPORT"
    report += "\n"
    report += "=" * 60
    report += "\n\n"

    report += "OVERALL STATISTICS\n"
    report += "-" * 60
    report += "\n"

    report += (
        f"Total Beds       : "
        f"{summary['total_beds']}\n"
    )

    report += (
        f"Available Beds   : "
        f"{summary['available_beds']}\n"
    )

    report += (
        f"Occupied Beds    : "
        f"{summary['occupied_beds']}\n"
    )

    report += (
        f"Maintenance Beds : "
        f"{summary['maintenance_beds']}\n"
    )

    report += (
        f"Waiting Patients : "
        f"{summary['waiting_patients']}\n"
    )

    report += (
        f"Admitted Patients: "
        f"{summary['admitted_patients']}\n"
    )

    report += (
        f"Occupancy Rate   : "
        f"{summary['occupancy_percentage']}%\n"
    )

    report += "\n"

    report += "DEPARTMENT-WISE REPORT\n"
    report += "-" * 60
    report += "\n"

    for department in department_report:

        report += (
            f"\nDepartment: "
            f"{department['department']}\n"
        )

        report += (
            f"Total Beds: "
            f"{department['total_beds']}\n"
        )

        report += (
            f"Available: "
            f"{department['available_beds']}\n"
        )

        report += (
            f"Occupied: "
            f"{department['occupied_beds']}\n"
        )

        report += (
            f"Occupancy: "
            f"{department['occupancy']}%\n"
        )

    report += "\n"
    report += "=" * 60
    report += "\n"

    return report


# ------------------------------------------------------------
# TEST REPORT MODULE
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)

    print("CAREBED AI - REPORT SYSTEM")

    print("=" * 60)

    print("\nDASHBOARD SUMMARY")
    print("-" * 60)

    summary = get_dashboard_summary()

    for key, value in summary.items():

        print(
            f"{key}: {value}"
        )

    print("\n")

    print(generate_text_report())