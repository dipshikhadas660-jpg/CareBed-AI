import sqlite3
from datetime import datetime

DB_NAME = "hospital.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_NAME)


# --------------------------------------------------
# CREATE DATABASE TABLES
# --------------------------------------------------

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Patient table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            disease TEXT,
            department TEXT,
            doctor TEXT,
            priority TEXT,
            admission_date TEXT,
            status TEXT DEFAULT 'Waiting'
        )
    """)

    # Bed table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beds (
            bed_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bed_number TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            bed_type TEXT NOT NULL,
            floor INTEGER,
            status TEXT DEFAULT 'Available',
            patient_id INTEGER
        )
    """)

    # Allocation table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allocations (
            allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            bed_id INTEGER,
            allocation_date TEXT,
            discharge_date TEXT,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY(bed_id) REFERENCES beds(bed_id)
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# ADD PATIENT
# --------------------------------------------------

def add_patient(
    name,
    age,
    gender,
    disease,
    department,
    doctor,
    priority
):

    conn = get_connection()
    cursor = conn.cursor()

    admission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO patients
        (
            name,
            age,
            gender,
            disease,
            department,
            doctor,
            priority,
            admission_date,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        gender,
        disease,
        department,
        doctor,
        priority,
        admission_date,
        "Waiting"
    ))

    patient_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return patient_id


# --------------------------------------------------
# GET ALL PATIENTS
# --------------------------------------------------

def get_all_patients():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            patient_id,
            name,
            age,
            gender,
            disease,
            department,
            doctor,
            priority,
            admission_date,
            status
        FROM patients
        ORDER BY patient_id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# --------------------------------------------------
# GET PATIENT BY ID
# --------------------------------------------------

def get_patient(patient_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE patient_id = ?
    """, (patient_id,))

    patient = cursor.fetchone()

    conn.close()

    return patient


# --------------------------------------------------
# ADD BED
# --------------------------------------------------

def add_bed(
    bed_number,
    department,
    bed_type,
    floor
):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO beds
            (
                bed_number,
                department,
                bed_type,
                floor,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            bed_number,
            department,
            bed_type,
            floor,
            "Available"
        ))

        conn.commit()

        result = True

    except sqlite3.IntegrityError:

        result = False

    conn.close()

    return result


# --------------------------------------------------
# GET ALL BEDS
# --------------------------------------------------

def get_all_beds():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            bed_id,
            bed_number,
            department,
            bed_type,
            floor,
            status,
            patient_id
        FROM beds
        ORDER BY bed_id
    """)

    beds = cursor.fetchall()

    conn.close()

    return beds


# --------------------------------------------------
# GET AVAILABLE BEDS
# --------------------------------------------------

def get_available_beds():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            bed_id,
            bed_number,
            department,
            bed_type,
            floor,
            status
        FROM beds
        WHERE status = 'Available'
    """)

    beds = cursor.fetchall()

    conn.close()

    return beds


# --------------------------------------------------
# GET AVAILABLE BEDS BY DEPARTMENT
# --------------------------------------------------

def get_available_beds_by_department(department):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            bed_id,
            bed_number,
            department,
            bed_type,
            floor,
            status
        FROM beds
        WHERE department = ?
        AND status = 'Available'
    """, (department,))

    beds = cursor.fetchall()

    conn.close()

    return beds


# --------------------------------------------------
# ALLOCATE BED
# --------------------------------------------------

def allocate_bed(patient_id, bed_id):

    conn = get_connection()

    cursor = conn.cursor()

    allocation_date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Update bed
    cursor.execute("""
        UPDATE beds
        SET
            status = 'Occupied',
            patient_id = ?
        WHERE bed_id = ?
        AND status = 'Available'
    """, (
        patient_id,
        bed_id
    ))

    # Check whether update happened
    if cursor.rowcount == 0:

        conn.close()

        return False

    # Create allocation record
    cursor.execute("""
        INSERT INTO allocations
        (
            patient_id,
            bed_id,
            allocation_date,
            status
        )
        VALUES (?, ?, ?, ?)
    """, (
        patient_id,
        bed_id,
        allocation_date,
        "Active"
    ))

    # Update patient status
    cursor.execute("""
        UPDATE patients
        SET status = 'Admitted'
        WHERE patient_id = ?
    """, (patient_id,))

    conn.commit()

    conn.close()

    return True


# --------------------------------------------------
# DISCHARGE PATIENT
# --------------------------------------------------

def discharge_patient(patient_id):

    conn = get_connection()

    cursor = conn.cursor()

    discharge_date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Find active allocation
    cursor.execute("""
        SELECT bed_id
        FROM allocations
        WHERE patient_id = ?
        AND status = 'Active'
    """, (patient_id,))

    result = cursor.fetchone()

    if result is None:

        conn.close()

        return False

    bed_id = result[0]

    # Make bed available
    cursor.execute("""
        UPDATE beds
        SET
            status = 'Available',
            patient_id = NULL
        WHERE bed_id = ?
    """, (bed_id,))

    # Close allocation
    cursor.execute("""
        UPDATE allocations
        SET
            discharge_date = ?,
            status = 'Completed'
        WHERE patient_id = ?
        AND status = 'Active'
    """, (
        discharge_date,
        patient_id
    ))

    # Update patient
    cursor.execute("""
        UPDATE patients
        SET status = 'Discharged'
        WHERE patient_id = ?
    """, (patient_id,))

    conn.commit()

    conn.close()

    return True


# --------------------------------------------------
# GET ACTIVE ALLOCATIONS
# --------------------------------------------------

def get_active_allocations():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.allocation_id,
            p.patient_id,
            p.name,
            p.department,
            p.priority,
            b.bed_number,
            b.bed_type,
            b.floor,
            a.allocation_date
        FROM allocations a

        JOIN patients p
        ON a.patient_id = p.patient_id

        JOIN beds b
        ON a.bed_id = b.bed_id

        WHERE a.status = 'Active'

        ORDER BY a.allocation_date DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# --------------------------------------------------
# DATABASE STATISTICS
# --------------------------------------------------

def get_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM beds
    """)

    total_beds = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM beds
        WHERE status = 'Available'
    """)

    available_beds = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM beds
        WHERE status = 'Occupied'
    """)

    occupied_beds = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM beds
        WHERE status = 'Maintenance'
    """)

    maintenance_beds = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE status = 'Waiting'
    """)

    waiting_patients = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE status = 'Admitted'
    """)

    admitted_patients = cursor.fetchone()[0]

    conn.close()

    return {
        "total_beds": total_beds,
        "available_beds": available_beds,
        "occupied_beds": occupied_beds,
        "maintenance_beds": maintenance_beds,
        "waiting_patients": waiting_patients,
        "admitted_patients": admitted_patients
    }


# --------------------------------------------------
# SAMPLE BED DATA
# --------------------------------------------------

# --------------------------------------------------
# SAMPLE BED DATA
# --------------------------------------------------

def create_sample_beds():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM beds
    """)

    count = cursor.fetchone()[0]

    # Do not create duplicate sample data
    if count > 0:
        conn.close()
        return

    sample_beds = [

        ("GEN-101", "General Medicine", "Normal", 1),
        ("GEN-102", "General Medicine", "Normal", 1),
        ("GEN-103", "General Medicine", "Normal", 1),
        ("GEN-104", "General Medicine", "Normal", 1),

        ("ICU-201", "ICU", "ICU", 2),
        ("ICU-202", "ICU", "ICU", 2),
        ("ICU-203", "ICU", "ICU", 2),

        ("EMG-301", "Emergency", "Emergency", 3),
        ("EMG-302", "Emergency", "Emergency", 3),

        ("PED-401", "Pediatrics", "Pediatric", 4),
        ("PED-402", "Pediatrics", "Pediatric", 4),

        ("CAR-501", "Cardiology", "Cardiac", 5),
        ("CAR-502", "Cardiology", "Cardiac", 5)
    ]

    cursor.executemany("""
        INSERT INTO beds
        (
            bed_number,
            department,
            bed_type,
            floor
        )
        VALUES (?, ?, ?, ?)
    """, sample_beds)

    conn.commit()
    conn.close()


# --------------------------------------------------
# INITIALIZE DATABASE WHEN FILE IS RUN
# --------------------------------------------------

if __name__ == "__main__":

    initialize_database()

    create_sample_beds()

    print("Database initialized successfully.")

    print("Sample beds created successfully.")

    print("\nAvailable Beds:")

    for bed in get_available_beds():

        print(bed)

    print("\nStatistics:")

    print(get_statistics())