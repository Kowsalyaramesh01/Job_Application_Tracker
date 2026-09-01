import streamlit as st
import pandas as pd
from datetime import date
from database import get_connection


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide"
)


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def load_applications():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                company_name,
                job_role,
                location,
                application_date,
                status,
                job_type,
                salary,
                job_url
            FROM jobs
            ORDER BY application_date DESC, id DESC
        """)

        return cursor.fetchall()

    except Exception as e:
        st.error(f"Error loading applications: {e}")
        return []

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def add_application(
    company_name,
    job_role,
    location,
    application_date,
    status,
    job_type,
    salary,
    job_url
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Check duplicate
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM jobs
            WHERE LOWER(TRIM(company_name))
                  = LOWER(TRIM(%s))
            AND LOWER(TRIM(job_role))
                  = LOWER(TRIM(%s))
            AND application_date = %s
            """,
            (
                company_name,
                job_role,
                application_date
            )
        )

        duplicate_count = cursor.fetchone()[0]

        if duplicate_count > 0:
            return (
                False,
                "This application already exists "
                "for the same company, role and date."
            )

        cursor.execute(
            """
            INSERT INTO jobs
            (
                company_name,
                job_role,
                location,
                application_date,
                status,
                job_type,
                salary,
                job_url
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                company_name.strip(),
                job_role.strip(),
                location.strip(),
                application_date,
                status,
                job_type,
                salary.strip(),
                job_url.strip()
            )
        )

        connection.commit()

        return True, "Job application added successfully!"

    except Exception as e:
        return False, f"Error adding application: {e}"

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def update_status(application_id, new_status):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE jobs
            SET status = %s
            WHERE id = %s
            """,
            (
                new_status,
                application_id
            )
        )

        connection.commit()

        return True, "Application status updated successfully!"

    except Exception as e:
        return False, f"Error updating application: {e}"

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def delete_application(application_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM jobs
            WHERE id = %s
            """,
            (application_id,)
        )

        connection.commit()

        return True, "Application deleted successfully!"

    except Exception as e:
        return False, f"Error deleting application: {e}"

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOAD DATA
# =========================================================

applications = load_applications()


# =========================================================
# CREATE DATAFRAME
# =========================================================

if applications:

    df = pd.DataFrame(
        applications,
        columns=[
            "ID",
            "Company",
            "Job Role",
            "Location",
            "Application Date",
            "Status",
            "Job Type",
            "Salary",
            "Job URL"
        ]
    )

    df["Application Date"] = pd.to_datetime(
        df["Application Date"]
    ).dt.date

else:

    df = pd.DataFrame(
        columns=[
            "ID",
            "Company",
            "Job Role",
            "Location",
            "Application Date",
            "Status",
            "Job Type",
            "Salary",
            "Job URL"
        ]
    )


# =========================================================
# DASHBOARD COUNTS
# =========================================================

total_jobs = len(df)

applied_count = len(
    df[
        df["Status"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "applied"
    ]
)

interview_count = len(
    df[
        df["Status"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "interview"
    ]
)

selected_count = len(
    df[
        df["Status"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "selected"
    ]
)

rejected_count = len(
    df[
        df["Status"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "rejected"
    ]
)


# =========================================================
# INTERVIEW RATE
# =========================================================

if total_jobs > 0:
    interview_rate = (
        interview_count / total_jobs
    ) * 100
else:
    interview_rate = 0


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("💼 Job Tracker")

st.sidebar.write(
    "Manage your job applications"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "➕ Add Application",
        "📋 Applications",
        "📊 Analytics"
    ]
)

st.sidebar.divider()

st.sidebar.metric(
    "Total Applications",
    total_jobs
)

if st.sidebar.button(
    "🔄 Refresh Data",
    use_container_width=True
):
    st.rerun()

st.sidebar.divider()

st.sidebar.caption(
    "Built with Python • Streamlit • MySQL"
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.title("🏠 Job Application Dashboard")

    st.write(
        "Track and monitor your job applications."
    )

    st.divider()

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col4, col5, col6 = st.columns(3)

    with col1:

        st.metric(
            "📊 Total Applications",
            total_jobs
        )

    with col2:

        st.metric(
            "📝 Applied",
            applied_count
        )

    with col3:

        st.metric(
            "🎯 Interviews",
            interview_count
        )

    with col4:

        st.metric(
            "✅ Selected",
            selected_count
        )

    with col5:

        st.metric(
            "❌ Rejected",
            rejected_count
        )

    with col6:

        st.metric(
            "📈 Interview Rate",
            f"{interview_rate:.1f}%"
        )

    st.divider()

    # -----------------------------------------------------
    # STATUS CHART
    # -----------------------------------------------------

    st.subheader(
        "📈 Application Status"
    )

    status_chart = pd.DataFrame(
        {
            "Status": [
                "Applied",
                "Interview",
                "Selected",
                "Rejected"
            ],
            "Applications": [
                applied_count,
                interview_count,
                selected_count,
                rejected_count
            ]
        }
    )

    st.bar_chart(
        status_chart.set_index("Status")
    )

    st.divider()

    # -----------------------------------------------------
    # RECENT APPLICATIONS
    # -----------------------------------------------------

    st.subheader(
        "🕐 Recent Applications"
    )

    if not df.empty:

        recent_df = df.head(5)

        st.dataframe(
            recent_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Job URL": st.column_config.LinkColumn(
                    "Job URL",
                    display_text="🔗 Open Job"
                )
            }
        )

    else:

        st.info(
            "No applications available."
        )


# =========================================================
# ADD APPLICATION
# =========================================================

elif page == "➕ Add Application":

    st.title("➕ Add New Job Application")

    st.write(
        "Enter the details of the job you applied for."
    )

    st.divider()

    with st.form("add_application_form"):

        col1, col2 = st.columns(2)

        with col1:

            company_name = st.text_input(
                "Company Name"
            )

            job_role = st.text_input(
                "Job Role"
            )

            location = st.text_input(
                "Location"
            )

            application_date = st.date_input(
                "Application Date",
                value=date.today()
            )

        with col2:

            status = st.selectbox(
                "Status",
                [
                    "Applied",
                    "Interview",
                    "Selected",
                    "Rejected"
                ]
            )

            job_type = st.selectbox(
                "Job Type",
                [
                    "Full Time",
                    "Part Time",
                    "Internship",
                    "Contract"
                ]
            )

            salary = st.text_input(
                "Salary",
                placeholder="Example: 5 LPA"
            )

            job_url = st.text_input(
                "Job URL",
                placeholder="https://example.com"
            )

        submitted = st.form_submit_button(
            "💾 Add Application",
            use_container_width=True
        )

    if submitted:

        if not company_name.strip():

            st.warning(
                "Please enter the company name."
            )

        elif not job_role.strip():

            st.warning(
                "Please enter the job role."
            )

        elif not location.strip():

            st.warning(
                "Please enter the location."
            )

        else:

            success, message = add_application(
                company_name,
                job_role,
                location,
                application_date,
                status,
                job_type,
                salary,
                job_url
            )

            if success:

                st.success(
                    f"✅ {message}"
                )

                st.rerun()

            else:

                st.warning(
                    f"⚠️ {message}"
                )


# =========================================================
# APPLICATIONS
# =========================================================

elif page == "📋 Applications":

    st.title("📋 All Job Applications")

    st.write(
        "Search, filter and manage your applications."
    )

    st.divider()

    if df.empty:

        st.info(
            "No job applications found."
        )

    else:

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        st.subheader("🔍 Search")

        search_text = st.text_input(
            "Search by company, job role or location",
            placeholder="Example: Python, Infosys, Bangalore"
        )

        # -------------------------------------------------
        # DATE RANGE
        # -------------------------------------------------

        st.subheader("📅 Date Range")

        min_date = df["Application Date"].min()
        max_date = df["Application Date"].max()

        date_col1, date_col2 = st.columns(2)

        with date_col1:

            start_date = st.date_input(
                "From Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )

        with date_col2:

            end_date = st.date_input(
                "To Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date
            )

        # -------------------------------------------------
        # FILTERS
        # -------------------------------------------------

        st.subheader("🔎 Filters")

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:

            company_filter = st.selectbox(
                "Company",
                ["All"] +
                sorted(
                    df["Company"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

        with filter_col2:

            status_filter = st.selectbox(
                "Status",
                ["All"] +
                sorted(
                    df["Status"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

        with filter_col3:

            role_filter = st.selectbox(
                "Job Role",
                ["All"] +
                sorted(
                    df["Job Role"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

        # -------------------------------------------------
        # APPLY FILTERS
        # -------------------------------------------------

        filtered_df = df.copy()

        # Date filter
        if start_date <= end_date:

            filtered_df = filtered_df[
                (
                    filtered_df["Application Date"]
                    >= start_date
                )
                &
                (
                    filtered_df["Application Date"]
                    <= end_date
                )
            ]

        else:

            st.warning(
                "⚠️ From Date cannot be after To Date."
            )

        # Search filter
        if search_text.strip():

            search_value = (
                search_text
                .strip()
                .lower()
            )

            company_match = (
                filtered_df["Company"]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_value,
                    na=False
                )
            )

            role_match = (
                filtered_df["Job Role"]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_value,
                    na=False
                )
            )

            location_match = (
                filtered_df["Location"]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_value,
                    na=False
                )
            )

            filtered_df = filtered_df[
                company_match
                | role_match
                | location_match
            ]

        # Company filter
        if company_filter != "All":

            filtered_df = filtered_df[
                filtered_df["Company"]
                == company_filter
            ]

        # Status filter
        if status_filter != "All":

            filtered_df = filtered_df[
                filtered_df["Status"]
                == status_filter
            ]

        # Role filter
        if role_filter != "All":

            filtered_df = filtered_df[
                filtered_df["Job Role"]
                == role_filter
            ]

        # -------------------------------------------------
        # RESULT COUNT
        # -------------------------------------------------

        st.info(
            f"Showing {len(filtered_df)} "
            f"of {len(df)} applications"
        )

        # -------------------------------------------------
        # APPLICATION TABLE
        # -------------------------------------------------

        if not filtered_df.empty:

            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Job URL": st.column_config.LinkColumn(
                        "Job URL",
                        display_text="🔗 Open Job"
                    )
                }
            )

            # -------------------------------------------------
            # CSV DOWNLOAD
            # -------------------------------------------------

            st.subheader(
                "📥 Export Applications"
            )

            csv_data = filtered_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="📥 Download Applications as CSV",
                data=csv_data,
                file_name="job_applications.csv",
                mime="text/csv",
                use_container_width=True
            )

        else:

            st.warning(
                "No applications match your search/filter."
            )

        # -------------------------------------------------
        # MANAGE APPLICATION
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "✏️ Manage Application"
        )

        selected_id = st.selectbox(
            "Select Application ID",
            df["ID"].tolist()
        )

        selected_application = df[
            df["ID"] == selected_id
        ].iloc[0]

        st.write(
            f"**Company:** "
            f"{selected_application['Company']}"
        )

        st.write(
            f"**Job Role:** "
            f"{selected_application['Job Role']}"
        )

        st.write(
            f"**Current Status:** "
            f"{selected_application['Status']}"
        )

        manage_col1, manage_col2 = st.columns(2)

        # -------------------------------------------------
        # UPDATE STATUS
        # -------------------------------------------------

        with manage_col1:

            status_options = [
                "Applied",
                "Interview",
                "Selected",
                "Rejected"
            ]

            current_status = str(
                selected_application["Status"]
            ).strip()

            if current_status not in status_options:

                current_status = "Applied"

            new_status = st.selectbox(
                "Change Status",
                status_options,
                index=status_options.index(
                    current_status
                )
            )

            if st.button(
                "✏️ Update Status",
                use_container_width=True
            ):

                success, message = update_status(
                    selected_id,
                    new_status
                )

                if success:

                    st.success(
                        f"✅ {message}"
                    )

                    st.rerun()

                else:

                    st.error(message)

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        with manage_col2:

            st.write("")

            confirm_delete = st.checkbox(
                "Confirm permanent deletion"
            )

            if st.button(
                "🗑️ Delete Application",
                use_container_width=True
            ):

                if not confirm_delete:

                    st.warning(
                        "Please confirm deletion first."
                    )

                else:

                    success, message = delete_application(
                        selected_id
                    )

                    if success:

                        st.success(
                            f"✅ {message}"
                        )

                        st.rerun()

                    else:

                        st.error(message)


# =========================================================
# ANALYTICS
# =========================================================

elif page == "📊 Analytics":

    st.title("📊 Analytics")

    st.write(
        "Analyze your job application activity."
    )

    st.divider()

    if df.empty:

        st.info(
            "No data available for analytics."
        )

    else:

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        st.subheader(
            "📈 Application Status Analysis"
        )

        status_data = pd.DataFrame(
            {
                "Status": [
                    "Applied",
                    "Interview",
                    "Selected",
                    "Rejected"
                ],
                "Count": [
                    applied_count,
                    interview_count,
                    selected_count,
                    rejected_count
                ]
            }
        )

        st.bar_chart(
            status_data.set_index("Status")
        )

        st.divider()

        # -------------------------------------------------
        # COMPANY
        # -------------------------------------------------

        st.subheader(
            "🏢 Applications by Company"
        )

        company_data = (
            df["Company"]
            .value_counts()
            .head(10)
        )

        st.bar_chart(
            company_data
        )

        st.divider()

        # -------------------------------------------------
        # JOB ROLE
        # -------------------------------------------------

        st.subheader(
            "💼 Applications by Job Role"
        )

        role_data = (
            df["Job Role"]
            .value_counts()
            .head(10)
        )

        st.bar_chart(
            role_data
        )

        st.divider()

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        st.subheader(
            "📍 Applications by Location"
        )

        location_data = (
            df["Location"]
            .value_counts()
            .head(10)
        )

        st.bar_chart(
            location_data
        )

        st.divider()

        # -------------------------------------------------
        # PERFORMANCE
        # -------------------------------------------------

        st.subheader(
            "🎯 Interview Performance"
        )

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:

            st.metric(
                "Total Applications",
                total_jobs
            )

        with metric_col2:

            st.metric(
                "Interviews",
                interview_count
            )

        with metric_col3:

            st.metric(
                "Interview Rate",
                f"{interview_rate:.1f}%"
            )


# =========================================================
# END
# =========================================================

st.sidebar.divider()

st.sidebar.caption(
    "💼 Job Application Tracker"
)