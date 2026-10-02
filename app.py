import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = "staff_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_name TEXT NOT NULL,
            date TEXT NOT NULL,
            check_in TEXT,
            check_out TEXT,
            UNIQUE(emp_name, date)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_name TEXT NOT NULL,
            date TEXT NOT NULL,
            activity_type TEXT NOT NULL DEFAULT 'Production',
            task_desc TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    
    actual_staff = [("Diya", "Operations"), ("Shailesh", "Operations"), ("Gaurav", "Operations")]
    for name, dept in actual_staff:
        cursor.execute("INSERT OR IGNORE INTO employees (name, department) VALUES (?, ?)", (name, dept))
        
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Daily Staff Tracker", layout="wide")

st.title("📋 Daily Staff Tracker & Workboard")

st.sidebar.header("Navigation")
staff_list = ["Diya", "Shailesh", "Gaurav"]
selected_emp = st.sidebar.selectbox("Select Employee", staff_list)

mode = st.sidebar.radio("View Mode", ["Staff Entry", "Admin Dashboard"])

today_str = datetime.now().strftime("%Y-%m-%d")

if mode == "Staff Entry":
    st.subheader(f"Welcome, {selected_emp} 👋")
    
    st.markdown("### ⏰ Daily Attendance")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🟢 Morning Check-In", use_container_width=True):
            now_time = datetime.now().strftime("%I:%M %p")
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO attendance (emp_name, date, check_in) VALUES (?, ?, ?)", (selected_emp, today_str, now_time))
                conn.commit()
                st.success(f"Checked in successfully at {now_time}")
            except sqlite3.IntegrityError:
                st.warning("Already checked in today!")
            finally:
                conn.close()

    with col2:
        if st.button("🔴 Evening Check-Out", use_container_width=True):
            now_time = datetime.now().strftime("%I:%M %p")
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("UPDATE attendance SET check_out = ? WHERE emp_name = ? AND date = ?", (now_time, selected_emp, today_str))
            conn.commit()
            if cursor.rowcount > 0:
                st.success(f"Checked out at {now_time}")
            else:
                st.warning("No check-in record found for today!")
            conn.close()

    st.divider()

    st.markdown("### 📝 Log Today's Activity / Task")
    with st.form("task_form", clear_on_submit=True):
        col_act, col_prio = st.columns([2, 1])
        with col_act:
            activity = st.selectbox("Activity Type", ["Production", "Out of Office", "No Work", "Planned Leave", "Others"])
        with col_prio:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
            
        desc = st.text_input("Description / Comment (Required for 'Others')", placeholder="Enter details here...")
        
        submitted = st.form_submit_button("Submit Entry")
        if submitted:
            if not desc.strip() and activity == "Others":
                st.error("Please add a description for 'Others'!")
            else:
                final_desc = desc.strip() if desc.strip() else f"Status: {activity}"
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO tasks (emp_name, date, activity_type, task_desc, priority) VALUES (?, ?, ?, ?, ?)",
                               (selected_emp, today_str, activity, final_desc, priority))
                conn.commit()
                conn.close()
                st.success("Activity logged successfully!")
                st.rerun()

    st.divider()
    st.markdown(f"### 📊 Today's Work Board for **{selected_emp}** ({today_str})")
    
    conn = sqlite3.connect(DB_NAME)
    df_tasks = pd.read_sql_query("SELECT task_id, activity_type, task_desc, priority, status FROM tasks WHERE emp_name = ? AND date = ?", 
                                conn, params=(selected_emp, today_str))
    conn.close()

    if not df_tasks.empty:
        st.dataframe(df_tasks, use_container_width=True, hide_index=True)
    else:
        st.info("No activities logged yet today.")

elif mode == "Admin Dashboard":
    st.subheader("🔒 Admin Dashboard (Read-Only Overview)")
    
    selected_date = st.date_input("Select Date", datetime.now())
    date_str = selected_date.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)

    st.markdown(f"#### 📅 Attendance Summary for {date_str}")
    df_attn = pd.read_sql_query("SELECT emp_name as Employee, check_in as 'Check In', check_out as 'Check Out' FROM attendance WHERE date = ?", conn, params=(date_str,))
    st.dataframe(df_attn, use_container_width=True, hide_index=True)

    st.markdown(f"#### 📝 All Staff Tasks for {date_str}")
    df_all_tasks = pd.read_sql_query("SELECT emp_name as Employee, activity_type as Activity, task_desc as Description, priority as Priority, status as Status FROM tasks WHERE date = ?", conn, params=(date_str,))
    st.dataframe(df_all_tasks, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 📥 Download Data Backup")
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        df_all_attn = pd.read_sql_query("SELECT * FROM attendance", conn)
        if not df_all_attn.empty:
            csv_attn = df_all_attn.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download All Attendance (CSV)",
                data=csv_attn,
                file_name=f"attendance_backup_{today_str}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No attendance records to download.")

    with col_d2:
        df_all_tasks_db = pd.read_sql_query("SELECT * FROM tasks", conn)
        if not df_all_tasks_db.empty:
            csv_tasks = df_all_tasks_db.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download All Tasks (CSV)",
                data=csv_tasks,
                file_name=f"tasks_backup_{today_str}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No task records to download.")

    conn.close()
