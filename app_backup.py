import streamlit as st
import pandas as pd
from datetime import date
from database import get_connection


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide"
)


# ==================================================
# TITLE
# ==================================================

# ==================================================
# SIDEBAR
# ==================================================

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


# ==================================================
# MAIN TITLE
# ==================================================

st.title("💼 Job Application Tracker")

st.write(
    "Track and manage all your job applications in one place."
)


# ==================================================
# LOAD APPLICATIONS FROM MYSQL
# ==================================================

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

        applications = cursor.fetchall()

        return applications

    except Exception as e:

        st.error(f"Error loading applications: {e}")
        return []

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==================================================
# ADD NEW JOB APPLICATION
# ==================================================

st.subheader("➕ Add New Job Application")

with st.form("job_application_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        company_name = st.text_input(
            "Company Name"
        )

    with col2:
        job_role = st.text_input(
            "Job Role"
        )

    with col3:
        location = st.text_input(
            "Location"
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        application_date = st.date_input(
            "Application Date",
            value=date.today()
        )

    with col5:
        status = st.selectbox(
            "Status",
            [
                "Applied",
                "Interview",
                "Selected",
                "Rejected"
            ]
        )

    with col6:
        job_type = st.selectbox(
            "Job Type",
            [
                "Full Time",
                "Part Time",
                "Internship",
                "Contract"
            ]
        )

    col7, col8 = st.columns(2)

    with col7:
        salary = st.text_input(
            "Salary",
            placeholder="Example: 5 LPA"
        )

    with col8:
        job_url = st.text_input(
            "Job URL",
            placeholder="https://example.com"
        )

    submitted = st.form_submit_button(
        "💾 Add Application",
        use_container_width=True
    )


# ==================================================
# INSERT APPLICATION INTO MYSQL
# ==================================================

if submitted:

    if company_name.strip() == "":
        st.warning("Please enter the company name.")

    elif job_role.strip() == "":
        st.warning("Please enter the job role.")

    elif location.strip() == "":
        st.warning("Please enter the location.")

    else:

        connection = None
        cursor = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            # ------------------------------------------
            # DUPLICATE CHECK
            # ------------------------------------------

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

                st.warning(
                    "⚠️ This application already exists "
                    "for the same company, role and date."
                )

            else:

                # --------------------------------------
                # INSERT
                # --------------------------------------

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
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
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

                st.success(
                    "✅ Job application added successfully!"
                )

                st.rerun()

        except Exception as e:

            st.error(
                f"Error adding application: {e}"
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


# ==================================================
# LOAD CURRENT DATA
# ==================================================

applications = load_applications()


# ==================================================
# CREATE DATAFRAME
# ==================================================

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


# ==================================================
# DASHBOARD COUNTS
# ==================================================

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


# ==================================================
# DASHBOARD
# ==================================================

st.divider()

st.subheader("📊 Application Dashboard")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "📊 Total",
        total_jobs
    )

with col2:
    st.metric(
        "📝 Applied",
        applied_count
    )

with col3:
    st.metric(
        "🎯 Interview",
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

# ==================================================
# INTERVIEW RATE
# ==================================================

if total_jobs > 0:
    interview_rate = (
        interview_count / total_jobs
    ) * 100
else:
    interview_rate = 0


with col6:
    st.metric(
        "📈 Interview Rate",
        f"{interview_rate:.1f}%"
    )


# ==================================================
# CHARTS
# ==================================================

if not df.empty:

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    # ----------------------------------------------
    # STATUS CHART
    # ----------------------------------------------

    with chart_col1:

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
            status_chart.set_index(
                "Status"
            )
        )


    # ----------------------------------------------
    # JOB ROLE CHART
    # ----------------------------------------------

    with chart_col2:

        st.subheader(
            "💼 Applications by Job Role"
        )

        role_chart = (
            df["Job Role"]
            .value_counts()
            .head(10)
        )

        st.bar_chart(
            role_chart
        )


    # ----------------------------------------------
    # COMPANY CHART
    # ----------------------------------------------

    st.subheader(
        "🏢 Applications by Company"
    )

    company_chart = (
        df["Company"]
        .value_counts()
        .head(10)
    )

    st.bar_chart(
        company_chart
    )


# ==================================================
# SEARCH AND FILTERS
# ==================================================

st.divider()

st.subheader(
    "🔎 Search & Filter Applications"
)

if not df.empty:

    # ----------------------------------------------
    # DATE RANGE
    # ----------------------------------------------

    st.write("### 📅 Date Range")

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


    # ----------------------------------------------
    # SEARCH
    # ----------------------------------------------

    st.write("### 🔍 Search")

    search_text = st.text_input(
        "Search by company, job role or location",
        placeholder="Example: Python, Infosys, Bangalore"
    )


    # ----------------------------------------------
    # DROPDOWN FILTERS
    # ----------------------------------------------

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


    # ==================================================
    # APPLY FILTERS
    # ==================================================

    filtered_df = df.copy()


    # ----------------------------------------------
    # DATE FILTER
    # ----------------------------------------------

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


    # ----------------------------------------------
    # SEARCH FILTER
    # ----------------------------------------------

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


    # ----------------------------------------------
    # COMPANY FILTER
    # ----------------------------------------------

    if company_filter != "All":

        filtered_df = filtered_df[
            filtered_df["Company"]
            == company_filter
        ]


    # ----------------------------------------------
    # STATUS FILTER
    # ----------------------------------------------

    if status_filter != "All":

        filtered_df = filtered_df[
            filtered_df["Status"]
            == status_filter
        ]


    # ----------------------------------------------
    # JOB ROLE FILTER
    # ----------------------------------------------

    if role_filter != "All":

        filtered_df = filtered_df[
            filtered_df["Job Role"]
            == role_filter
        ]


else:

    filtered_df = df


# ==================================================
# APPLICATION TABLE
# ==================================================

st.divider()

st.subheader(
    "📋 All Job Applications"
)

if not filtered_df.empty:

    st.info(
        f"Showing {len(filtered_df)} "
        f"of {len(df)} applications"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=False,
        column_config={
            "Job URL": st.column_config.LinkColumn(
                "Job URL",
                display_text="🔗 Open Job"
            )
        }
    )

else:

    st.info(
        "No applications match your search/filter."
    )


# ==================================================
# EDIT / DELETE APPLICATION
# ==================================================

st.divider()

st.subheader(
    "✏️ Manage Application"
)

if not df.empty:

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


    # ==================================================
    # UPDATE STATUS
    # ==================================================

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
                        selected_id
                    )
                )

                connection.commit()

                st.success(
                    "✅ Application status updated!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Error updating application: {e}"
                )

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()


    # ==================================================
    # DELETE APPLICATION
    # ==================================================

    with manage_col2:

        st.write("")

        confirm_delete = st.checkbox(
            "I understand this will permanently delete the application."
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
                        (selected_id,)
                    )

                    connection.commit()

                    st.success(
                        "✅ Application deleted successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Error deleting application: {e}"
                    )

                finally:

                    if cursor:
                        cursor.close()

                    if connection:
                        connection.close()


else:

    st.info(
        "No applications available to manage."
    )


# ==================================================
# RECENT APPLICATIONS
# ==================================================

if not df.empty:

    st.divider()

    st.subheader(
        "🕐 Recent Applications"
    )

    recent_df = df.head(5)

    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "💼 Job Application Tracker | "
    "Built with Python + Streamlit + MySQL"
)