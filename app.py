# ============================================================
# CAREBED AI
# Human-in-the-Loop Hospital Bed Allocation Agent
# ============================================================

import streamlit as st
import pandas as pd

from database import (
    initialize_database,
    create_sample_beds,
    add_patient,
    get_all_patients,
    get_patient,
    get_all_beds,
    get_available_beds,
    allocate_bed,
    discharge_patient,
    get_active_allocations,
    get_statistics
)

from agent import get_agent_decision

from reports import (
    get_dashboard_summary,
    get_department_report,
    get_bed_type_statistics,
    get_priority_statistics,
    get_patient_status_statistics,
    get_department_patient_statistics,
    generate_text_report
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CareBed AI",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_database()
create_sample_beds()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 38px;
    font-weight: bold;
}

.subtitle {
    font-size: 18px;
    color: #666666;
}

.metric-box {
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🏥 CareBed AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Human-in-the-Loop Intelligent Hospital Bed Allocation Agent'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏥 CareBed AI")

st.sidebar.markdown(
    "### Navigation"
)

page = st.sidebar.radio(
    "Select Module",
    [
        "📊 Dashboard",
        "👤 Patient Registration",
        "🛏️ Bed Management",
        "🤖 AI Bed Allocation",
        "📋 Active Allocations",
        "🚪 Discharge Patient",
        "📈 Reports"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    """
    CareBed AI assists hospital staff by recommending
    suitable beds based on patient priority,
    department, bed type and availability.

    Final allocation remains under human control.
    """
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.header("📊 Hospital Dashboard")

    summary = get_dashboard_summary()

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Beds",
            summary["total_beds"]
        )

    with col2:

        st.metric(
            "Available Beds",
            summary["available_beds"]
        )

    with col3:

        st.metric(
            "Occupied Beds",
            summary["occupied_beds"]
        )

    with col4:

        st.metric(
            "Occupancy",
            f"{summary['occupancy_percentage']}%"
        )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Waiting Patients",
            summary["waiting_patients"]
        )

    with col2:

        st.metric(
            "Admitted Patients",
            summary["admitted_patients"]
        )

    with col3:

        st.metric(
            "Maintenance Beds",
            summary["maintenance_beds"]
        )

    st.divider()

    # --------------------------------------------------------
    # BED STATUS
    # --------------------------------------------------------

    st.subheader("🛏️ Bed Status")

    beds = get_all_beds()

    if beds:

        bed_data = []

        for bed in beds:

            bed_data.append({

                "Bed Number": bed[1],

                "Department": bed[2],

                "Bed Type": bed[3],

                "Floor": bed[4],

                "Status": bed[5]

            })

        df_beds = pd.DataFrame(
            bed_data
        )

        st.dataframe(
            df_beds,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No beds found."
        )


# ============================================================
# PATIENT REGISTRATION
# ============================================================

elif page == "👤 Patient Registration":

    st.header("👤 Patient Registration")

    st.write(
        "Register a new patient before requesting bed allocation."
    )

    with st.form("patient_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Patient Name *"
            )

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=30
            )

            gender = st.selectbox(
                "Gender",
                [
                    "Male",
                    "Female",
                    "Other"
                ]
            )

            disease = st.text_input(
                "Disease / Condition"
            )

        with col2:

            department = st.selectbox(
                "Department",
                [
                    "General Medicine",
                    "ICU",
                    "Emergency",
                    "Pediatrics",
                    "Cardiology"
                ]
            )

            doctor = st.text_input(
                "Doctor Name"
            )

            priority = st.selectbox(
                "Patient Priority",
                [
                    "Emergency",
                    "ICU",
                    "High",
                    "Medium",
                    "Low"
                ]
            )

        submit = st.form_submit_button(
            "➕ Register Patient"
        )

        if submit:

            if not name.strip():

                st.error(
                    "Please enter the patient name."
                )

            else:

                patient_id = add_patient(
                    name=name,
                    age=age,
                    gender=gender,
                    disease=disease,
                    department=department,
                    doctor=doctor,
                    priority=priority
                )

                st.success(
                    f"Patient registered successfully. "
                    f"Patient ID: {patient_id}"
                )


# ============================================================
# BED MANAGEMENT
# ============================================================

elif page == "🛏️ Bed Management":

    st.header("🛏️ Bed Management")

    st.subheader("Current Bed Availability")

    beds = get_all_beds()

    if beds:

        data = []

        for bed in beds:

            status = bed[5]

            if status == "Available":

                display_status = "🟢 Available"

            elif status == "Occupied":

                display_status = "🔴 Occupied"

            else:

                display_status = "🟡 Maintenance"

            data.append({

                "Bed": bed[1],

                "Department": bed[2],

                "Type": bed[3],

                "Floor": bed[4],

                "Status": display_status

            })

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # --------------------------------------------------------
    # ADD NEW BED
    # --------------------------------------------------------

    st.subheader("➕ Add New Bed")

    with st.form("bed_form"):

        col1, col2 = st.columns(2)

        with col1:

            bed_number = st.text_input(
                "Bed Number",
                placeholder="GEN-105"
            )

            department = st.selectbox(
                "Department",
                [
                    "General Medicine",
                    "ICU",
                    "Emergency",
                    "Pediatrics",
                    "Cardiology"
                ],
                key="bed_department"
            )

        with col2:

            bed_type = st.selectbox(
                "Bed Type",
                [
                    "Normal",
                    "ICU",
                    "Emergency",
                    "Pediatric",
                    "Cardiac"
                ]
            )

            floor = st.number_input(
                "Floor",
                min_value=0,
                max_value=50,
                value=1
            )

        add_bed_button = st.form_submit_button(
            "Add Bed"
        )

        if add_bed_button:

            if not bed_number.strip():

                st.error(
                    "Enter a bed number."
                )

            else:

                from database import add_bed

                success = add_bed(
                    bed_number,
                    department,
                    bed_type,
                    floor
                )

                if success:

                    st.success(
                        f"Bed {bed_number} added successfully."
                    )

                else:

                    st.error(
                        "Bed number already exists."
                    )


# ============================================================
# AI BED ALLOCATION
# ============================================================

elif page == "🤖 AI Bed Allocation":

    st.header("🤖 AI Bed Allocation Agent")

    st.write(
        "The agent analyzes patient requirements and "
        "available beds to recommend the most suitable bed."
    )

    st.info(
        "⚠️ The AI provides a recommendation. "
        "Final allocation must be approved by authorized staff."
    )

    patients = get_all_patients()

    waiting_patients = [
        p for p in patients
        if p[9] == "Waiting"
    ]

    if not waiting_patients:

        st.warning(
            "No waiting patients available."
        )

    else:

        patient_options = {}

        for patient in waiting_patients:

            label = (
                f"#{patient[0]} - "
                f"{patient[1]} | "
                f"{patient[7]} | "
                f"{patient[5]}"
            )

            patient_options[label] = patient

        selected_label = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        selected_patient = patient_options[
            selected_label
        ]

        patient_id = selected_patient[0]
        patient_name = selected_patient[1]
        department = selected_patient[5]
        priority = selected_patient[7]

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Patient",
                patient_name
            )

        with col2:

            st.metric(
                "Department",
                department
            )

        with col3:

            st.metric(
                "Priority",
                priority
            )

        st.divider()

        if st.button(
            "🤖 Find Best Bed",
            type="primary"
        ):

            result = get_agent_decision(
                patient_name,
                department,
                priority
            )

            st.session_state[
                "agent_result"
            ] = result

            st.session_state[
                "selected_patient_id"
            ] = patient_id

        # ----------------------------------------------------
        # SHOW AGENT RESULT
        # ----------------------------------------------------

        if "agent_result" in st.session_state:

            result = st.session_state[
                "agent_result"
            ]

            if result["status"] == "NO_BED":

                st.error(
                    result["message"]
                )

            else:

                recommendation = result[
                    "recommendation"
                ]

                st.success(
                    result["message"]
                )

                st.subheader(
                    "🎯 Recommended Bed"
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Bed",
                        recommendation[
                            "bed_number"
                        ]
                    )

                with col2:

                    st.metric(
                        "Department",
                        recommendation[
                            "department"
                        ]
                    )

                with col3:

                    st.metric(
                        "Bed Type",
                        recommendation[
                            "bed_type"
                        ]
                    )

                with col4:

                    st.metric(
                        "Score",
                        recommendation[
                            "score"
                        ]
                    )

                st.subheader(
                    "🧠 Agent Explanation"
                )

                st.text(
                    result["explanation"]
                )

                # ------------------------------------------------
                # HUMAN APPROVAL
                # ------------------------------------------------

                st.divider()

                st.subheader(
                    "👨‍⚕️ Human Approval"
                )

                st.warning(
                    "Review the recommendation before allocation."
                )

                approve = st.checkbox(
                    "I approve this bed allocation."
                )

                if approve:

                    if st.button(
                        "✅ Confirm Bed Allocation",
                        type="primary"
                    ):

                        success = allocate_bed(
                            st.session_state[
                                "selected_patient_id"
                            ],
                            recommendation[
                                "bed_id"
                            ]
                        )

                        if success:

                            st.success(
                                f"Bed "
                                f"{recommendation['bed_number']} "
                                f"allocated successfully."
                            )

                            # Clear previous result
                            del st.session_state[
                                "agent_result"
                            ]

                            st.rerun()

                        else:

                            st.error(
                                "Allocation failed. "
                                "The bed may no longer be available."
                            )

                # ------------------------------------------------
                # ALTERNATIVE BEDS
                # ------------------------------------------------

                alternatives = result.get(
                    "alternatives",
                    []
                )

                if alternatives:

                    st.divider()

                    st.subheader(
                        "🔄 Alternative Beds"
                    )

                    alternative_data = []

                    for bed in alternatives:

                        alternative_data.append({

                            "Bed":
                                bed["bed_number"],

                            "Department":
                                bed["department"],

                            "Type":
                                bed["bed_type"],

                            "Floor":
                                bed["floor"],

                            "Score":
                                bed["score"]

                        })

                    st.dataframe(
                        pd.DataFrame(
                            alternative_data
                        ),
                        use_container_width=True,
                        hide_index=True
                    )


# ============================================================
# ACTIVE ALLOCATIONS
# ============================================================

elif page == "📋 Active Allocations":

    st.header("📋 Active Bed Allocations")

    allocations = get_active_allocations()

    if allocations:

        data = []

        for row in allocations:

            data.append({

                "Allocation ID": row[0],

                "Patient ID": row[1],

                "Patient": row[2],

                "Department": row[3],

                "Priority": row[4],

                "Bed": row[5],

                "Bed Type": row[6],

                "Floor": row[7],

                "Allocation Time": row[8]

            })

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "There are currently no active allocations."
        )


# ============================================================
# DISCHARGE PATIENT
# ============================================================

elif page == "🚪 Discharge Patient":

    st.header("🚪 Discharge Patient")

    allocations = get_active_allocations()

    if not allocations:

        st.info(
            "No currently admitted patients."
        )

    else:

        options = {}

        for row in allocations:

            label = (
                f"Patient #{row[1]} - "
                f"{row[2]} - "
                f"Bed {row[5]}"
            )

            options[label] = row

        selected = st.selectbox(
            "Select Patient",
            list(options.keys())
        )

        allocation = options[selected]

        patient_id = allocation[1]

        st.write(
            f"**Patient:** {allocation[2]}"
        )

        st.write(
            f"**Bed:** {allocation[5]}"
        )

        st.write(
            f"**Department:** {allocation[3]}"
        )

        st.write(
            f"**Priority:** {allocation[4]}"
        )

        if st.button(
            "🚪 Confirm Discharge",
            type="primary"
        ):

            success = discharge_patient(
                patient_id
            )

            if success:

                st.success(
                    "Patient discharged successfully. "
                    "The bed is now available."
                )

                st.rerun()

            else:

                st.error(
                    "Unable to discharge patient."
                )


# ============================================================
# REPORTS
# ============================================================

elif page == "📈 Reports":

    st.header("📈 Hospital Reports & Analytics")

    summary = get_dashboard_summary()

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    st.subheader(
        "Hospital Summary"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Beds",
            summary["total_beds"]
        )

    with col2:

        st.metric(
            "Available",
            summary["available_beds"]
        )

    with col3:

        st.metric(
            "Occupied",
            summary["occupied_beds"]
        )

    with col4:

        st.metric(
            "Occupancy",
            f"{summary['occupancy_percentage']}%"
        )

    st.divider()

    # --------------------------------------------------------
    # DEPARTMENT REPORT
    # --------------------------------------------------------

    st.subheader(
        "🏥 Department-wise Bed Report"
    )

    department_report = get_department_report()

    if department_report:

        df_department = pd.DataFrame(
            department_report
        )

        df_department.columns = [
            "Department",
            "Total Beds",
            "Available Beds",
            "Occupied Beds",
            "Occupancy %"
        ]

        st.dataframe(
            df_department,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            df_department.set_index(
                "Department"
            )["Available Beds"]
        )

    # --------------------------------------------------------
    # BED TYPE REPORT
    # --------------------------------------------------------

    st.subheader(
        "🛏️ Bed Type Statistics"
    )

    bed_types = get_bed_type_statistics()

    if bed_types:

        bed_type_data = []

        for row in bed_types:

            bed_type_data.append({

                "Bed Type": row[0],

                "Total": row[1],

                "Available": row[2] or 0,

                "Occupied": row[3] or 0

            })

        df_types = pd.DataFrame(
            bed_type_data
        )

        st.dataframe(
            df_types,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # PATIENT PRIORITY
    # --------------------------------------------------------

    st.subheader(
        "🚨 Patient Priority Distribution"
    )

    priorities = get_priority_statistics()

    if priorities:

        priority_data = []

        for row in priorities:

            priority_data.append({

                "Priority": row[0],

                "Patients": row[1]

            })

        df_priority = pd.DataFrame(
            priority_data
        )

        st.bar_chart(
            df_priority.set_index(
                "Priority"
            )
        )

    # --------------------------------------------------------
    # PATIENT STATUS
    # --------------------------------------------------------

    st.subheader(
        "👤 Patient Status"
    )

    statuses = get_patient_status_statistics()

    if statuses:

        status_data = []

        for row in statuses:

            status_data.append({

                "Status": row[0],

                "Patients": row[1]

            })

        df_status = pd.DataFrame(
            status_data
        )

        st.dataframe(
            df_status,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # DOWNLOAD REPORT
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📄 Download Hospital Report"
    )

    report_text = generate_text_report()

    st.download_button(
        label="⬇️ Download Text Report",
        data=report_text,
        file_name="carebed_hospital_report.txt",
        mime="text/plain"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "CareBed AI | Human-in-the-Loop Hospital Bed Allocation "
    "Agent | ELITRIX"
)