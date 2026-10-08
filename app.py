import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# Page Configuration
st.set_page_config(page_title="Staff Daily Activity & Dress Code Tracker", page_icon="📋", layout="wide")

# Persistent File Path (Data automatically save rahega)
DATA_FILE = "staff_tracker_records.csv"

# Data load aur save karne ke functions
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Timestamp", "Date", "Employee Name", "Activity Type", "Activity Note", "Uniform Status", "Reason / Notes"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_records = load_data()

# Updated Staff List
STAFF_LIST = ["Sailesh", "Diya", "Gaurav", "Imtiyaz"]

# Sidebar Navigation
st.sidebar.title("Navigation")
selected_emp = st.sidebar.selectbox("Select Employee", STAFF_LIST)
view_mode = st.sidebar.radio("View Mode", ["Staff Entry", "Admin Dashboard & Past Records"])

# ----------------- VIEW 1: STAFF ENTRY -----------------
if view_mode == "Staff Entry":
    st.title("📋 Staff Entry Portal")
    st.write(f"Logged in as: **{selected_emp}**")

    st.divider()

    # Section 1: Daily Attendance & Activity Tracker
    st.subheader("⏰ Daily Attendance & Activity")
    attendance_status = st.selectbox(
        "Select Activity Status",
        ["Morning Check-In", "Evening Check-Out", "Production", "Break", "Meeting", "Other Activity"]
    )
    activity_notes = st.text_input("Activity Detail / Note (Optional)", placeholder="e.g. Working on production reports")

    st.divider()

    # Section 2: Dress Code Tracker
    st.subheader("👔 Daily Dress Code Check")
    dress_status = st.radio(
        "Are you in official uniform / proper dress code today?",
        ["Yes, Full Uniform 🟢", "No / Casual / Partial 🔴"],
        horizontal=True
    )
    dress_reason = ""
    if "No" in dress_status:
        dress_reason = st.text_input("Mention reason if not in uniform:")

    st.write("")
    if st.button("Submit Today's Entry", type="primary"):
        now_dt = datetime.now()
        current_timestamp = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        current_date = now_dt.strftime("%Y-%m-%d")

        is_uniform = "Yes" if "Yes" in dress_status else "No"
        combined_notes = f"Activity: {activity_notes} | Dress Reason: {dress_reason}".strip(" |")

        new_row = {
            "Timestamp": current_timestamp,
            "Date": current_date,
            "Employee Name": selected_emp,
            "Activity Type": attendance_status,
            "Activity Note": activity_notes if activity_notes else "-",
            "Uniform Status": is_uniform,
            "Reason / Notes": dress_reason if is_uniform == "No" else "-"
        }

        df_updated = pd.concat([df_records, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df_updated)
        st.success(f"Entry recorded successfully for **{selected_emp}**!")
        st.rerun()

# ----------------- VIEW 2: ADMIN DASHBOARD & PAST RECORDS -----------------
elif view_mode == "Admin Dashboard & Past Records":
    st.title("📊 Admin Dashboard & Historical Records")
    
    df_current = load_data()

    if df_current.empty:
        st.info("Abhi tak koi past records available nahi hain.")
    else:
        st.subheader("🔍 Search & Filter Past Records")
        
        # Convert Date column to datetime for proper filtering
        df_current["Date_Obj"] = pd.to_datetime(df_current["Date"]).dt.date
        min_date = df_current["Date_Obj"].min()
        max_date = df_current["Date_Obj"].max()

        # Date & Employee Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_emp = st.multiselect("Filter by Staff Name", STAFF_LIST, default=STAFF_LIST)
            
        with col2:
            start_date = st.date_input("From Date", value=min_date)
            
        with col3:
            end_date = st.date_input("To Date", value=max_date)

        # Filtering Data
        df_filtered = df_current[
            (df_current["Employee Name"].isin(filter_emp)) &
            (df_current["Date_Obj"] >= start_date) &
            (df_current["Date_Obj"] <= end_date)
        ]

        # Summary Metrics
        st.divider()
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Total Entries", len(df_filtered))
        m_col2.metric("In Uniform 🟢", len(df_filtered[df_filtered["Uniform Status"] == "Yes"]))
        m_col3.metric("Non-Uniform 🔴", len(df_filtered[df_filtered["Uniform Status"] == "No"]))

        st.write("### Records Log Table")
        display_df = df_filtered.drop(columns=["Date_Obj"])
        st.dataframe(display_df, use_container_width=True)

        # Optional CSV Download Button
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Selected Data as CSV",
            data=csv_data,
            file_name=f"staff_records_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )
