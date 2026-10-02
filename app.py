import customtkinter as ctk
from tkinter import messagebox
import database as db

# Application configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class StaffTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        db.init_db()
        db.seed_sample_employees()

        self.title("Daily Staff Tracker & Activity Workboard")
        self.geometry("900x700")

        # Top Control Bar - Staff Selector
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=15, pady=10)

        self.lbl_select = ctk.CTkLabel(self.top_frame, text="Select Employee:", font=("Arial", 14, "bold"))
        self.lbl_select.pack(side="left", padx=10, pady=10)

        self.staff_list = db.get_all_employees()
        self.selected_staff = ctk.StringVar(value=self.staff_list[0] if self.staff_list else "")
        self.combo_staff = ctk.CTkOptionMenu(self.top_frame, variable=self.selected_staff, values=self.staff_list, command=self.on_staff_change)
        self.combo_staff.pack(side="left", padx=10, pady=10)

        # Check-in / Check-out Action Panel
        self.attn_frame = ctk.CTkFrame(self)
        self.attn_frame.pack(fill="x", padx=15, pady=5)

        self.btn_checkin = ctk.CTkButton(self.attn_frame, text="Morning Check-In", fg_color="green", command=self.check_in_action)
        self.btn_checkin.pack(side="left", padx=15, pady=10)

        self.btn_checkout = ctk.CTkButton(self.attn_frame, text="Evening Check-Out", fg_color="darkred", command=self.check_out_action)
        self.btn_checkout.pack(side="left", padx=15, pady=10)

        self.lbl_status_msg = ctk.CTkLabel(self.attn_frame, text="Ready", font=("Arial", 12, "italic"))
        self.lbl_status_msg.pack(side="right", padx=15, pady=10)

        # Activity & Task Entry Section
        self.task_entry_frame = ctk.CTkFrame(self)
        self.task_entry_frame.pack(fill="x", padx=15, pady=10)

        # Activity Type Selection
        self.lbl_activity = ctk.CTkLabel(self.task_entry_frame, text="Activity:", font=("Arial", 12, "bold"))
        self.lbl_activity.pack(side="left", padx=(10, 2), pady=10)

        self.activity_var = ctk.StringVar(value="Production")
        self.combo_activity = ctk.CTkOptionMenu(
            self.task_entry_frame, 
            variable=self.activity_var, 
            values=["Production", "Out of Office", "No Work", "Planned Leave", "Others"], 
            width=130
        )
        self.combo_activity.pack(side="left", padx=5, pady=10)

        # Task/Comment Entry Box
        self.entry_task = ctk.CTkEntry(self.task_entry_frame, placeholder_text="Enter task description or comment/reason...", width=320)
        self.entry_task.pack(side="left", padx=5, pady=10)

        # Priority Selection
        self.priority_var = ctk.StringVar(value="Medium")
        self.combo_priority = ctk.CTkOptionMenu(self.task_entry_frame, variable=self.priority_var, values=["High", "Medium", "Low"], width=90)
        self.combo_priority.pack(side="left", padx=5, pady=10)

        # Add Button
        self.btn_add_task = ctk.CTkButton(self.task_entry_frame, text="+ Add Entry", width=90, command=self.add_task_action)
        self.btn_add_task.pack(side="left", padx=10, pady=10)

        # Task Display Section
        self.lbl_task_header = ctk.CTkLabel(self, text="Today's Work Board", font=("Arial", 16, "bold"))
        self.lbl_task_header.pack(anchor="w", padx=20, pady=(10, 0))

        self.task_list_frame = ctk.CTkScrollableFrame(self, height=350)
        self.task_list_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.refresh_tasks()

    def check_in_action(self):
        emp = self.selected_staff.get()
        msg = db.log_check_in(emp)
        self.lbl_status_msg.configure(text=msg)
        messagebox.showinfo("Attendance Notice", msg)

    def check_out_action(self):
        emp = self.selected_staff.get()
        msg = db.log_check_out(emp)
        self.lbl_status_msg.configure(text=msg)
        messagebox.showinfo("Attendance Notice", msg)

    def add_task_action(self):
        emp = self.selected_staff.get()
        activity = self.activity_var.get()
        desc = self.entry_task.get().strip()
        priority = self.priority_var.get()

        if not desc and activity == "Others":
            messagebox.showwarning("Warning", "Please enter a manual comment/description for 'Others'!")
            return

        final_desc = desc if desc else f"Status: {activity}"

        db.add_task(emp, activity, final_desc, priority)
        self.entry_task.delete(0, 'end')
        self.refresh_tasks()

    def on_staff_change(self, choice):
        self.refresh_tasks()
        self.lbl_status_msg.configure(text="Ready")

    def refresh_tasks(self):
        # Clear existing task widgets
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        emp = self.selected_staff.get()
        tasks = db.get_today_tasks(emp)

        if not tasks:
            ctk.CTkLabel(self.task_list_frame, text="No activities logged yet for today.", font=("Arial", 12, "italic")).pack(pady=20)
            return

        for task_id, activity, desc, priority, status in tasks:
            row_frame = ctk.CTkFrame(self.task_list_frame)
            row_frame.pack(fill="x", padx=5, pady=5)

            # Priority Tag
            color_map = {"High": "red", "Medium": "orange", "Low": "gray"}
            p_label = ctk.CTkLabel(row_frame, text=f"[{priority}]", text_color=color_map.get(priority, "white"), font=("Arial", 12, "bold"), width=55)
            p_label.pack(side="left", padx=5)

            # Activity Tag
            act_label = ctk.CTkLabel(row_frame, text=f"<{activity}>", font=("Arial", 12, "bold"), text_color="#1F6AA5", width=110)
            act_label.pack(side="left", padx=5)

            # Description / Manual Comment
            desc_label = ctk.CTkLabel(row_frame, text=desc, anchor="w", font=("Arial", 13))
            desc_label.pack(side="left", fill="x", expand=True, padx=10)

            # Status Dropdown
            status_var = ctk.StringVar(value=status)
            status_dropdown = ctk.CTkOptionMenu(
                row_frame,
                variable=status_var,
                values=["Pending", "In Progress", "Completed", "Blocked"],
                width=110,
                command=lambda new_stat, tid=task_id: db.update_task_status(tid, new_stat)
            )
            status_dropdown.pack(side="right", padx=10)

if __name__ == "__main__":
    app = StaffTrackerApp()
    app.mainloop()