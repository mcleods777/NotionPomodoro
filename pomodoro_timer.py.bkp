import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import time
from datetime import datetime, timedelta
import webbrowser
import csv
from PIL import Image, ImageTk  # For handling images
import sys
from tkinter import font as tkfont  # For custom fonts

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer with Task Tracking")
        # Further increased window size to better accommodate the session list
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Set application theme and style
        self.set_theme()
        
        # Create custom fonts
        self.timer_font = tkfont.Font(family="Helvetica", size=56, weight="bold")
        self.heading_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.button_font = tkfont.Font(family="Helvetica", size=10)
        
        # Configure logging
        import logging
        logging.basicConfig(
            filename='pomodoro_app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('pomodoro')
        
        # Add console handler to show logs in console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        self.logger.info("Application started")
        
        # Define colors
        self.colors = {
            "bg_main": "#f5f5f5",
            "bg_frame": "#ffffff",
            "accent": "#ff6347",  # Tomato red for Pomodoro
            "short_break": "#4682B4",  # Steel Blue for short breaks
            "long_break": "#6A5ACD",  # Slate Blue for long breaks
            "text": "#333333",
            "text_light": "#777777",
            "button_bg": "#f0f0f0",
            "button_active": "#e0e0e0"
        }
        
        # Set initial background color based on mode
        self.update_color_scheme("Pomodoro")
        
        # Timer settings
        self.pomodoro_time = 25 * 60  # 25 minutes in seconds
        self.short_break_time = 5 * 60  # 5 minutes
        self.long_break_time = 15 * 60  # 15 minutes
        self.current_time = self.pomodoro_time
        self.timer_running = False
        self.current_mode = "Pomodoro"
        self.completed_pomodoros = 0
        
        # Sound settings
        self.enable_sounds = tk.BooleanVar(value=False)  # Disabled sounds by default
        
        # Task tracking
        self.data_file = "pomodoro_data.json"
        self.projects = []
        self.tasks = []
        self.current_task = None
        self.current_project = None
        self.task_start_time = None
        self.task_sessions = []
        
        # Load existing data
        self.load_data()
        self.logger.info(f"Loaded {len(self.projects)} projects and {len(self.tasks)} tasks")
        self.logger.info(f"Loaded {len(self.task_sessions)} previous sessions")
        
        # Create the interface
        self.create_widgets()
        self.update_timer_display()
    
    def set_theme(self):
        """Set up a modern theme for the application"""
        style = ttk.Style()
        
        if 'vista' in style.theme_names():
            style.theme_use('vista')
        elif 'clam' in style.theme_names():
            style.theme_use('clam')
        
        # Configure frame styles
        style.configure('TFrame', background='#ffffff')
        style.configure('TLabelframe', background='#ffffff', borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label', background='#ffffff', foreground='#555555', font=('Helvetica', 11, 'bold'))
        
        # Configure button styles
        style.configure('TButton', padding=6, font=('Helvetica', 10))
        style.configure('Accent.TButton', background='#ff6347')
        
        # Configure label styles
        style.configure('TLabel', background='#ffffff', foreground='#333333')
        style.configure('Mode.TLabel', font=('Helvetica', 12), foreground='#555555')
        style.configure('Large.TLabel', font=('Helvetica', 48, 'bold'))
        
        # Configure combobox styles
        style.configure('TCombobox', padding=5)
        
        # Configure treeview
        style.configure('Treeview', rowheight=25, font=('Helvetica', 10))
        style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
    
    def create_widgets(self):
        # Configure root background
        self.root.configure(bg=self.colors["bg_main"])
        
        # Main container frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Timer section
        timer_frame = ttk.LabelFrame(main_frame, text="FOCUS TIMER", padding="20")
        timer_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Progress indicator (circular or bar)
        progress_frame = ttk.Frame(timer_frame)
        progress_frame.pack(pady=10)
        
        # Timer display with large font
        self.timer_label = ttk.Label(timer_frame, text="25:00", font=self.timer_font, foreground=self.colors["accent"])
        self.timer_label.pack(pady=15)
        
        self.mode_label = ttk.Label(timer_frame, text="Pomodoro Mode", style="Mode.TLabel")
        self.mode_label.pack(pady=5)
        
        # Improved timer buttons with better spacing and styling
        timer_buttons_frame = ttk.Frame(timer_frame)
        timer_buttons_frame.pack(pady=15)
        
        # Custom styled buttons
        self.start_button = ttk.Button(timer_buttons_frame, text="▶ Start", command=self.start_timer, width=12, style="Accent.TButton")
        self.start_button.grid(row=0, column=0, padx=8)
        
        self.pause_button = ttk.Button(timer_buttons_frame, text="⏸ Pause", command=self.pause_timer, state=tk.DISABLED, width=12)
        self.pause_button.grid(row=0, column=1, padx=8)
        
        self.reset_button = ttk.Button(timer_buttons_frame, text="↺ Reset", command=self.reset_timer, width=12)
        self.reset_button.grid(row=0, column=2, padx=8)
        
        # Add Skip Break button with increased width to prevent text cutoff
        self.skip_button = ttk.Button(timer_buttons_frame, text="⏭ Skip Break", command=self.skip_break, state=tk.DISABLED, width=15)
        self.skip_button.grid(row=0, column=3, padx=8)
        
        # Task input section with improved styling
        task_frame = ttk.LabelFrame(main_frame, text="TASK INFORMATION", padding="15")
        task_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Project row with improved layout
        project_row = ttk.Frame(task_frame)
        project_row.pack(fill=tk.X, pady=8)
        
        ttk.Label(project_row, text="Project:", font=self.button_font).pack(side=tk.LEFT, padx=5)
        
        self.project_combo = ttk.Combobox(project_row, width=30, font=self.button_font)
        self.project_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.project_combo['values'] = self.projects
        self.project_combo.bind('<Return>', self.add_project)
        
        project_buttons = ttk.Frame(project_row)
        project_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(project_buttons, text="+ Add", command=self.add_project, width=8).pack(side=tk.LEFT, padx=3)
        ttk.Button(project_buttons, text="- Delete", command=self.delete_project, width=8).pack(side=tk.LEFT, padx=3)
        
        # Task row with improved layout
        task_row = ttk.Frame(task_frame)
        task_row.pack(fill=tk.X, pady=8)
        
        ttk.Label(task_row, text="Task:", font=self.button_font).pack(side=tk.LEFT, padx=5)
        
        self.task_combo = ttk.Combobox(task_row, width=30, font=self.button_font)
        self.task_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.task_combo['values'] = self.tasks
        self.task_combo.bind('<Return>', self.add_task)
        
        task_buttons = ttk.Frame(task_row)
        task_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(task_buttons, text="+ Add", command=self.add_task, width=8).pack(side=tk.LEFT, padx=3)
        ttk.Button(task_buttons, text="- Delete", command=self.delete_task, width=8).pack(side=tk.LEFT, padx=3)
        
        # Task sessions section with modern styling
        sessions_frame = ttk.LabelFrame(main_frame, text="SESSION HISTORY", padding="15")
        sessions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        # Set a minimum height for the sessions frame to ensure visibility
        sessions_frame.pack_propagate(False)  # Prevent the frame from shrinking
        sessions_frame.configure(height=350)  # Increased height from 250 to 350
        
        # Date selection with improved styling
        date_frame = ttk.Frame(sessions_frame)
        date_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(date_frame, text="View sessions for:", font=self.button_font).pack(side=tk.LEFT, padx=5)
        
        # Create date options with better styling
        self.date_var = tk.StringVar(value="Today")
        date_options = ["Today", "Yesterday", "Last 7 Days", "Last 30 Days", "All Time"]
        date_dropdown = ttk.Combobox(date_frame, textvariable=self.date_var, values=date_options, 
                                     width=15, state="readonly", font=self.button_font)
        date_dropdown.pack(side=tk.LEFT, padx=10)
        date_dropdown.bind("<<ComboboxSelected>>", lambda e: self.populate_sessions_tree())
        
        refresh_button = ttk.Button(date_frame, text="↻ Refresh", command=self.populate_sessions_tree, width=10)
        refresh_button.pack(side=tk.LEFT, padx=10)
        
        # Summary stats frame to show totals
        stats_frame = ttk.Frame(sessions_frame)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.total_time_label = ttk.Label(stats_frame, text="Total Time: 0:00", font=self.button_font)
        self.total_time_label.pack(side=tk.LEFT, padx=10)
        
        self.total_sessions_label = ttk.Label(stats_frame, text="Sessions: 0", font=self.button_font)
        self.total_sessions_label.pack(side=tk.LEFT, padx=10)
        
        # Create Treeview with better styling for session history
        tree_frame = ttk.Frame(sessions_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        # Set a minimum height for tree frame to ensure treeview visibility
        tree_frame.pack_propagate(False)  # Prevent the frame from shrinking
        tree_frame.configure(height=280)  # Increased height from 180 to 280
        
        columns = ("Date", "Time", "Project", "Task", "Duration")
        self.sessions_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Treeview")
        
        # Set column headings with better proportions
        self.sessions_tree.heading("Date", text="Date")
        self.sessions_tree.column("Date", width=100, anchor="center")
        
        self.sessions_tree.heading("Time", text="Time")
        self.sessions_tree.column("Time", width=80, anchor="center")
        
        self.sessions_tree.heading("Project", text="Project")
        self.sessions_tree.column("Project", width=150)
        
        self.sessions_tree.heading("Task", text="Task")
        self.sessions_tree.column("Task", width=200)
        
        self.sessions_tree.heading("Duration", text="Duration")
        self.sessions_tree.column("Duration", width=80, anchor="center")
        
        # Add horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.sessions_tree.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.sessions_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, pady=5, padx=5)
        self.sessions_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # Add vertical scrollbar with better styling
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sessions_tree.configure(yscrollcommand=y_scrollbar.set)
        
        # Reports and settings frame with better organization
        controls_frame = ttk.Frame(main_frame, padding="10")
        controls_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Report buttons with icons and better styling
        reports_frame = ttk.LabelFrame(controls_frame, text="REPORTS", padding="10")
        reports_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Button(reports_frame, text="📊 Daily Report", command=self.export_daily_report, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(reports_frame, text="📈 Weekly Report", command=self.export_weekly_report, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(reports_frame, text="🔍 View Data File", command=self.view_data_file, width=15).pack(side=tk.LEFT, padx=5)
        
        # Settings frame for app settings
        settings_frame = ttk.LabelFrame(controls_frame, text="SETTINGS", padding="10")
        settings_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Sound toggle with better styling
        sound_check = ttk.Checkbutton(settings_frame, text="🔊 Enable Sounds", variable=self.enable_sounds)
        sound_check.pack(side=tk.RIGHT, padx=10)
        
        # App info / version at bottom
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=5)
        
        version_label = ttk.Label(footer_frame, text="Pomodoro Timer v1.1", foreground=self.colors["text_light"])
        version_label.pack(side=tk.RIGHT, padx=10)
        
        # Populate the session tree
        self.populate_sessions_tree()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as file:
                    data = json.load(file)
                    self.projects = data.get("projects", [])
                    self.tasks = data.get("tasks", [])
                    self.task_sessions = data.get("sessions", [])
            except (json.JSONDecodeError, FileNotFoundError):
                self.projects = []
                self.tasks = []
                self.task_sessions = []
    
    def save_data(self):
        data = {
            "projects": self.projects,
            "tasks": self.tasks,
            "sessions": self.task_sessions
        }
        with open(self.data_file, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)
        
        self.logger.info(f"Saved data with {len(self.projects)} projects, {len(self.tasks)} tasks, and {len(self.task_sessions)} sessions")
    
    def add_project(self, event=None):
        project = self.project_combo.get().strip()
        if project and project not in self.projects:
            self.projects.append(project)
            self.project_combo['values'] = self.projects
            self.save_data()
    
    def delete_project(self):
        project = self.project_combo.get()
        if project and project in self.projects:
            if messagebox.askyesno("Confirm", f"Delete project '{project}'? This will remove all associated task records."):
                self.projects.remove(project)
                
                # Remove task sessions associated with the project
                self.task_sessions = [session for session in self.task_sessions 
                                      if session.get("project") != project]
                
                # Remove tasks associated with the project
                self.tasks = [task for task in self.tasks 
                              if not task.startswith(f"{project}:")]
                
                self.project_combo['values'] = self.projects
                self.project_combo.set('')
                self.task_combo['values'] = self.tasks
                self.populate_sessions_tree()
                self.save_data()
    
    def add_task(self, event=None):
        project = self.project_combo.get()
        task = self.task_combo.get().strip()
        
        if not project:
            messagebox.showwarning("Warning", "Please select or add a project first.")
            return
        
        if task:
            task_key = f"{project}: {task}"
            if task_key not in self.tasks:
                self.tasks.append(task_key)
                self.task_combo['values'] = self.tasks
                self.save_data()
    
    def delete_task(self):
        task_key = self.task_combo.get()
        if task_key and task_key in self.tasks:
            if messagebox.askyesno("Confirm", f"Delete task '{task_key}'? This will remove all associated records."):
                self.tasks.remove(task_key)
                
                # Remove task sessions associated with the task
                self.task_sessions = [session for session in self.task_sessions 
                                      if session.get("task_key") != task_key]
                
                self.task_combo['values'] = self.tasks
                self.task_combo.set('')
                self.populate_sessions_tree()
                self.save_data()
    
    def update_color_scheme(self, mode):
        """Update the color scheme based on the current timer mode"""
        if mode == "Pomodoro":
            self.current_color = self.colors["accent"]
        elif mode == "Short Break":
            self.current_color = self.colors["short_break"]
        else:  # Long Break
            self.current_color = self.colors["long_break"]
            
        # Update the timer label color
        if hasattr(self, 'timer_label'):
            self.timer_label.config(foreground=self.current_color)
    
    def update_timer_display(self):
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.config(text=time_string)
        
        # Update mode label and color scheme
        if self.current_mode == "Pomodoro":
            pomodoro_count = self.completed_pomodoros
            self.mode_label.config(text=f"Pomodoro Mode ({pomodoro_count}/4)")
            # Disable skip button during Pomodoro sessions
            self.skip_button.config(state=tk.DISABLED)
            # Update color scheme
            self.update_color_scheme("Pomodoro")
        elif self.current_mode == "Short Break":
            self.mode_label.config(text="Short Break")
            # Enable skip button during break sessions
            self.skip_button.config(state=tk.NORMAL)
            # Update color scheme
            self.update_color_scheme("Short Break")
        else:  # Long Break
            self.mode_label.config(text="Long Break")
            # Enable skip button during break sessions
            self.skip_button.config(state=tk.NORMAL)
            # Update color scheme
            self.update_color_scheme("Long Break")
    
    def start_timer(self):
        if not self.timer_running:
            # Validate task and project selection for Pomodoro mode
            if self.current_mode == "Pomodoro":
                self.current_task = self.task_combo.get()
                self.current_project = self.project_combo.get()
                
                if not self.current_project:
                    messagebox.showwarning("Warning", "Please select a project before starting the timer.")
                    return
                    
                if not self.current_task:
                    messagebox.showwarning("Warning", "Please select a task before starting the timer.")
                    return
            
            self.timer_running = True
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            
            # If we're starting a Pomodoro, record the start time
            if self.current_mode == "Pomodoro":
                self.task_start_time = datetime.now()
                print(f"Started session for {self.current_project}: {self.current_task} at {self.task_start_time}")
            
            self.tick()
    
    def play_sound(self, sound_type):
        """Play a sound based on the type of notification"""
        # Simply return if sounds are disabled
        if not self.enable_sounds.get():
            return
            
        # Log sound request but don't play any sounds
        self.logger.info(f"Sound requested: {sound_type} (sounds are disabled)")
            
    def tick(self):
        if self.timer_running and self.current_time > 0:
            self.current_time -= 1
            self.update_timer_display()
            self.root.after(1000, self.tick)
        elif self.timer_running and self.current_time <= 0:
            self.timer_running = False
            
            # Actions when timer completes
            if self.current_mode == "Pomodoro":
                # Record task session when Pomodoro completes
                if self.task_start_time and self.current_task:
                    print(f"Pomodoro completed for {self.current_project}: {self.current_task}")
                    self.record_task_session()
                
                self.completed_pomodoros += 1
                
                # Decide whether to take a short break or long break
                if self.completed_pomodoros % 4 == 0:
                    self.current_mode = "Long Break"
                    self.current_time = self.long_break_time
                else:
                    self.current_mode = "Short Break"
                    self.current_time = self.short_break_time
                
                messagebox.showinfo("Pomodoro Complete", "Time to take a break!")
            else:
                # Break is over, start a new Pomodoro
                self.current_mode = "Pomodoro"
                self.current_time = self.pomodoro_time
                messagebox.showinfo("Break Complete", "Time to focus!")
            
            self.update_timer_display()
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            
            # Reset task start time after completion
            self.task_start_time = None
    
    def skip_break(self):
        """Skip the current break and start a new Pomodoro session"""
        # Only allow skipping during break modes
        if self.current_mode not in ["Short Break", "Long Break"]:
            return
            
        self.logger.info(f"Skipping {self.current_mode}")
        
        # Stop the current timer if it's running
        self.timer_running = False
        
        # Change to Pomodoro mode and reset timer
        self.current_mode = "Pomodoro"
        self.current_time = self.pomodoro_time
        
        # Update display and color scheme
        self.update_timer_display()
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        
        # Log the skip action
        self.logger.info("Break skipped, ready for next Pomodoro")
        messagebox.showinfo("Break Skipped", "Break skipped. Ready to start next Pomodoro!")
    
    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            
            # If we're pausing a Pomodoro (not a break), record the session
            if self.current_mode == "Pomodoro" and self.task_start_time:
                self.record_task_session()
                # Reset task start time to prevent double-recording
                self.task_start_time = None
    
    def reset_timer(self):
        # If we're resetting a running Pomodoro, record the session
        if self.timer_running and self.current_mode == "Pomodoro" and self.task_start_time:
            self.record_task_session()
        
        self.timer_running = False
        
        # Only reset the time based on the current mode
        if self.current_mode == "Pomodoro":
            self.current_time = self.pomodoro_time
        elif self.current_mode == "Short Break":
            self.current_time = self.short_break_time
        else:
            self.current_time = self.long_break_time
        
        self.update_timer_display()
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        
        # Reset task start time
        self.task_start_time = None
    
    def record_task_session(self):
        # Only record if we have a valid start time and task
        if not self.task_start_time or not self.current_task or not self.current_project:
            return
            
        end_time = datetime.now()
        duration = end_time - self.task_start_time
        
        # Only record sessions that are at least 1 minute long
        if duration.total_seconds() < 60:
            return
            
        # Create session record
        session = {
            "start_time": self.task_start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "project": self.current_project,
            "task": self.current_task.replace(f"{self.current_project}: ", ""),
            "task_key": self.current_task,
            "duration_seconds": duration.total_seconds()
        }
        
        # Add to sessions and save
        self.task_sessions.append(session)
        self.save_data()
        
        # Update the sessions tree
        self.populate_sessions_tree()
        
        # Display confirmation message
        messagebox.showinfo("Session Recorded", 
                           f"Session recorded:\nProject: {self.current_project}\nTask: {session['task']}\nDuration: {self.format_duration(duration.total_seconds())}")
    
    def format_duration(self, seconds):
        """Format duration in seconds to mm:ss format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def format_duration_hours(self, seconds):
        """Format duration in seconds to hh:mm:ss format for longer durations"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"
    
    def populate_sessions_tree(self):
        """Populate the sessions tree with filtered sessions based on selected date range"""
        # Clear existing items
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
        
        # Determine date range based on selection
        today = datetime.now().date()
        date_filter = self.date_var.get()
        
        start_date = None
        if date_filter == "Today":
            start_date = today
        elif date_filter == "Yesterday":
            start_date = today - timedelta(days=1)
            end_date = start_date
        elif date_filter == "Last 7 Days":
            start_date = today - timedelta(days=6)
        elif date_filter == "Last 30 Days":
            start_date = today - timedelta(days=29)
        # All Time has no start date filter
        
        # Filter sessions based on date range
        filtered_sessions = []
        for session in self.task_sessions:
            session_date = datetime.fromisoformat(session["start_time"]).date()
            
            if date_filter == "Today" and session_date == today:
                filtered_sessions.append(session)
            elif date_filter == "Yesterday" and session_date == start_date:
                filtered_sessions.append(session)
            elif date_filter == "Last 7 Days" and start_date <= session_date <= today:
                filtered_sessions.append(session)
            elif date_filter == "Last 30 Days" and start_date <= session_date <= today:
                filtered_sessions.append(session)
            elif date_filter == "All Time":
                filtered_sessions.append(session)
        
        # Sort sessions by start time (most recent first)
        filtered_sessions.sort(key=lambda x: x["start_time"], reverse=True)
        
        # Add sessions to tree with alternating row colors for better readability
        for i, session in enumerate(filtered_sessions):
            start_time = datetime.fromisoformat(session["start_time"])
            date_str = start_time.strftime("%Y-%m-%d")
            time_str = start_time.strftime("%H:%M")
            project = session["project"]
            task = session["task"]
            duration = self.format_duration(session["duration_seconds"])
            
            # Insert with tags for alternating colors
            tag = "even" if i % 2 == 0 else "odd"
            self.sessions_tree.insert("", tk.END, values=(date_str, time_str, project, task, duration), tags=(tag,))
        
        # Configure tag colors
        self.sessions_tree.tag_configure("even", background="#ffffff")
        self.sessions_tree.tag_configure("odd", background="#f5f5f5")
        
        # Calculate and display statistics
        total_seconds = sum(session["duration_seconds"] for session in filtered_sessions)
        total_time = self.format_duration_hours(total_seconds)
        
        # Update the statistics labels
        self.total_time_label.config(text=f"Total Time: {total_time}")
        self.total_sessions_label.config(text=f"Sessions: {len(filtered_sessions)}")
        
        # Log the results
        count = len(filtered_sessions)
        range_text = date_filter
        if count == 0:
            self.logger.info(f"No sessions found for {range_text}")
        else:
            self.logger.info(f"Showing {count} sessions for {range_text}, total time: {total_time}")
    
    def export_daily_report(self):
        today = datetime.now().date()
        self.export_report(today, today, "daily")
    
    def export_weekly_report(self):
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        self.export_report(start_of_week, today, "weekly")
    
    def view_data_file(self):
        """Open the JSON data file in the default text editor"""
        try:
            # Check if file exists first
            if not os.path.exists(self.data_file):
                messagebox.showinfo("File Not Found", "The data file has not been created yet.")
                return
                
            # Open the JSON file in the default application
            webbrowser.open(self.data_file)
            self.logger.info(f"Opened data file for viewing: {self.data_file}")
        except Exception as e:
            self.logger.error(f"Error opening data file: {str(e)}")
            messagebox.showerror("Error", f"Could not open data file: {str(e)}")
            
    def export_report(self, start_date, end_date, report_type):
        # Filter sessions in the given date range
        filtered_sessions = []
        
        for session in self.task_sessions:
            session_date = datetime.fromisoformat(session["start_time"]).date()
            if start_date <= session_date <= end_date:
                filtered_sessions.append(session)
        
        if not filtered_sessions:
            messagebox.showinfo("No Data", f"No task sessions found for the {report_type} report period.")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"pomodoro_{report_type}_report_{start_date}.csv"
        )
        
        if not filename:
            return
        
        # Write to CSV
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Start Time', 'End Time', 'Project', 'Task', 'Duration (min)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for session in filtered_sessions:
                start_time = datetime.fromisoformat(session["start_time"])
                end_time = datetime.fromisoformat(session["end_time"])
                duration_min = session["duration_seconds"] / 60
                
                writer.writerow({
                    'Date': start_time.strftime("%Y-%m-%d"),
                    'Start Time': start_time.strftime("%H:%M:%S"),
                    'End Time': end_time.strftime("%H:%M:%S"),
                    'Project': session["project"],
                    'Task': session["task"],
                    'Duration (min)': f"{duration_min:.1f}"
                })
        
        messagebox.showinfo("Report Exported", f"The {report_type} report has been exported to {filename}")
        self.logger.info(f"Exported {report_type} report with {len(filtered_sessions)} sessions to {filename}")

def create_circular_progress(canvas, x, y, radius, progress, color, width=10):
    """Create a circular progress indicator on the canvas"""
    # Calculate angles for the progress arc
    start_angle = 90
    extent = -progress * 360
    
    # Draw background circle
    canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                      outline="#ddd", width=width)
    
    # Draw progress arc
    if progress > 0:
        canvas.create_arc(x-radius, y-radius, x+radius, y+radius, 
                         start=start_angle, extent=extent,
                         outline=color, style="arc", width=width)
