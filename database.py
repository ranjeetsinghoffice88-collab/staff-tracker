import sqlite3
from datetime import datetime

DB_NAME = "staff_tracker.db"

def init_db():
    """Initializes SQLite database tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL
        )
    ''')
    
    # Attendance log table
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
    
    # Daily tasks table
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
    
    # Migration check for existing database without activity_type
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]
    if "activity_type" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN activity_type TEXT DEFAULT 'Production'")

    conn.commit()
    conn.close()

def seed_sample_employees():
    """Seeds actual employee names if table is empty or missing them."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    actual_staff = [("Diya", "Operations"), ("Shailesh", "Operations"), ("Gaurav", "Operations")]
    
    for name, dept in actual_staff:
        cursor.execute("INSERT OR IGNORE INTO employees (name, department) VALUES (?, ?)", (name, dept))
        
    conn.commit()
    conn.close()

def log_check_in(emp_name):
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%I:%M %p")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO attendance (emp_name, date, check_in) VALUES (?, ?, ?)", (emp_name, today, now_time))
        conn.commit()
        return f"Check-in logged successfully at {now_time}"
    except sqlite3.IntegrityError:
        return f"Already checked in today ({today})!"
    finally:
        conn.close()

def log_check_out(emp_name):
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%I:%M %p")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE attendance SET check_out = ? WHERE emp_name = ? AND date = ?", (now_time, emp_name, today))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return f"Check-out logged at {now_time}" if updated else "No check-in record found for today!"

def add_task(emp_name, activity_type, desc, priority):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (emp_name, date, activity_type, task_desc, priority) VALUES (?, ?, ?, ?, ?)", 
                   (emp_name, today, activity_type, desc, priority))
    conn.commit()
    conn.close()

def get_today_tasks(emp_name):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, activity_type, task_desc, priority, status FROM tasks WHERE emp_name = ? AND date = ?", (emp_name, today))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_task_status(task_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE task_id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

def get_all_employees():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM employees")
    rows = [r[0] for r in cursor.fetchall()]
    conn.close()
    return rows