import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import requests
from datetime import datetime, timedelta

class NotionClient:
    """Class to handle Notion API interactions"""
    
    def __init__(self, token=None):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"  # Using a stable API version
        } if token else None
        self.base_url = "https://api.notion.com/v1"
        self.logger = None  # Will be set by NotionIntegration
        
    def set_token(self, token):
        """Set or update the API token"""
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
    def test_connection(self):
        """Test if the connection to Notion API works"""
        if not self.token:
            return False
            
        try:
            response = requests.get(f"{self.base_url}/users/me", headers=self.headers)
            return response.status_code == 200
        except Exception:
            return False
            
    def get_databases(self):
        """Get list of databases the integration has access to"""
        if not self.token:
            return []
            
        try:
            # First try with the filter approach
            response = requests.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json={"filter": {"value": "database", "property": "object"}}
            )
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                if self.logger:
                    self.logger.info(f"Found {len(results)} databases with filter method")
                return results
            else:
                # Log the error
                if self.logger:
                    self.logger.error(f"Database search failed: {response.status_code} - {response.text}")
                
                # Try alternative approach without filter
                response = requests.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={}  # No filter, search all objects
                )
                
                if response.status_code == 200:
                    # Filter for databases manually
                    all_results = response.json().get("results", [])
                    database_results = [r for r in all_results if r.get("object") == "database"]
                    if self.logger:
                        self.logger.info(f"Found {len(database_results)} databases with alternative method")
                    return database_results
                else:
                    if self.logger:
                        self.logger.error(f"Alternative search failed: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            if self.logger:
                self.logger.error(f"Exception getting databases: {str(e)}")
            return []
            
    def get_database_tasks(self, database_id):
        """Get tasks from a specific database"""
        if not self.token or not database_id:
            return []
            
        try:
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/query",
                headers=self.headers,
                json={}
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                return []
        except Exception:
            return []
            
    def create_task(self, database_id, task_name, project_name=None):
        """Create a new task in a Notion database"""
        if not self.token or not database_id:
            return None
            
        # Default properties for a task
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": task_name
                        }
                    }
                ]
            }
        }
        
        # Add project name as a tag if provided
        if project_name:
            properties["Tags"] = {
                "multi_select": [
                    {
                        "name": project_name
                    }
                ]
            }
            
        try:
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json={
                    "parent": {"database_id": database_id},
                    "properties": properties
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                if self.logger:
                    self.logger.error(f"Failed to create task in Notion: {response.text}")
                return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Exception creating task in Notion: {str(e)}")
            return None
    
    def log_simple_session(self, database_id, project, task, start_time, end_time, duration_seconds):
        """Simplified session logger with explicit focus on correct property types"""
        if not self.token or not database_id:
            return None
            
        # Format duration for display
        duration_minutes = float(duration_seconds) / 60.0  # Explicitly convert to float
        
        # Format the date and time strings for Notion
        date_str = start_time.split('T')[0]  # Extract YYYY-MM-DD
        start_time_obj = datetime.fromisoformat(start_time.replace('Z', '+00:00') if 'Z' in start_time else start_time)
        end_time_obj = datetime.fromisoformat(end_time.replace('Z', '+00:00') if 'Z' in end_time else end_time)
        
        start_time_str = start_time_obj.strftime("%H:%M")
        end_time_str = end_time_obj.strftime("%H:%M")
        
        # Create a simple properties object with correct property types
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": f"Session: {task}"
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": date_str
                }
            },
            "Project": {  
                "select": {  # Changed from rich_text to select
                    "name": project
                }
            },
            "Task": {
                "rich_text": [
                    {
                        "text": {
                            "content": task
                        }
                    }
                ]
            },
            "Start Time": {
                "rich_text": [
                    {
                        "text": {
                            "content": start_time_str
                        }
                    }
                ]
            },
            "End Time": {
                "rich_text": [
                    {
                        "text": {
                            "content": end_time_str
                        }
                    }
                ]
            },
            "Duration": {  
                "rich_text": [  # Changed from number to rich_text
                    {
                        "text": {
                            "content": f"{int(duration_minutes)} min" 
                        }
                    }
                ]
            }
        }
        
        try:
            # Log the request for debugging
            if self.logger:
                self.logger.info(f"Logging session with duration: {duration_minutes} minutes ({type(duration_minutes).__name__})")
                
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json={
                    "parent": {"database_id": database_id},
                    "properties": properties
                }
            )
            
            if response.status_code == 200:
                if self.logger:
                    self.logger.info(f"Successfully logged session to Notion: {project} - {task}")
                return response.json()
            else:
                if self.logger:
                    self.logger.error(f"Failed to log session to Notion: {response.text}")
                return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Exception logging session to Notion: {str(e)}")
            return None
            
    def log_session(self, database_id, project, task, start_time, end_time, duration_seconds):
        """Log a completed Pomodoro session to a Notion database"""
        if not self.token or not database_id:
            return None
            
        # Format duration for display
        duration_minutes = duration_seconds / 60
        duration_formatted = f"{int(duration_minutes)} min"
        
        # Format the date and time strings for Notion
        date_str = start_time.split('T')[0]  # Extract YYYY-MM-DD
        start_time_obj = datetime.fromisoformat(start_time.replace('Z', '+00:00') if 'Z' in start_time else start_time)
        end_time_obj = datetime.fromisoformat(end_time.replace('Z', '+00:00') if 'Z' in end_time else end_time)
        
        start_time_str = start_time_obj.strftime("%H:%M")
        end_time_str = end_time_obj.strftime("%H:%M")
        
        # Create properties for the log entry
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": f"Session: {task}"
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": date_str
                }
            },
            "Project": {
                "select": {  # Updated to use select instead of rich_text
                    "name": project
                }
            },
            "Task": {
                "rich_text": [
                    {
                        "text": {
                            "content": task
                        }
                    }
                ]
            },
            "Start Time": {
                "rich_text": [
                    {
                        "text": {
                            "content": start_time_str
                        }
                    }
                ]
            },
            "End Time": {
                "rich_text": [
                    {
                        "text": {
                            "content": end_time_str
                        }
                    }
                ]
            },
            "Duration": {
                "rich_text": [  # Updated to use rich_text instead of number
                    {
                        "text": {
                            "content": duration_formatted
                        }
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json={
                    "parent": {"database_id": database_id},
                    "properties": properties
                }
            )
            
            if response.status_code == 200:
                if self.logger:
                    self.logger.info(f"Successfully logged session to Notion: {project} - {task}")
                return response.json()
            else:
                if self.logger:
                    self.logger.error(f"Failed to log session to Notion: {response.text}")
                return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Exception logging session to Notion: {str(e)}")
            return None

class NotionIntegration:
    """Class to handle Notion integration with the Pomodoro app"""
    
    def __init__(self, parent, pomodoro_app):
        self.parent = parent
        self.pomodoro_app = pomodoro_app
        self.config_file = "notion_config.json"
        self.client = NotionClient()
        self.client.logger = pomodoro_app.logger  # Pass logger to client
        self.selected_database = None
        self.log_database = None  # Database for session logs
        self.databases = []
        self.auto_log_sessions = tk.BooleanVar(value=False)  # Control auto-logging
        
        # Load existing configuration
        self.load_config()
        
        # Create integration window
        self.window = tk.Toplevel(parent)
        self.window.title("Notion Integration")
        self.window.geometry("650x650")  # Increased height to accommodate log settings
        self.window.resizable(True, True)
        self.window.withdraw()  # Hidden initially
        
        # Apply same theme as parent
        self.window.configure(bg=pomodoro_app.colors["bg_main"])
        
        # Create the UI
        self.create_widgets()
        
    def load_config(self):
        """Load Notion configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as file:
                    config = json.load(file)
                    token = config.get("token")
                    if token:
                        self.client.set_token(token)
                    self.selected_database = config.get("selected_database")
                    self.log_database = config.get("log_database")
                    
                    # Load auto-log preference
                    if "auto_log" in config:
                        self.auto_log_sessions.set(config.get("auto_log"))
            except:
                # If file exists but can't be read, initialize with empty config
                self.save_config()
        else:
            # Initialize config file if it doesn't exist
            self.save_config()
            
    def save_config(self):
        """Save Notion configuration to file"""
        config = {
            "token": self.client.token,
            "selected_database": self.selected_database,
            "log_database": self.log_database,
            "auto_log": self.auto_log_sessions.get()
        }
        
        with open(self.config_file, "w") as file:
            json.dump(config, file)
            
    def create_widgets(self):
        """Create the UI elements for Notion integration"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection section
        conn_frame = ttk.LabelFrame(main_frame, text="NOTION CONNECTION", padding="15")
        conn_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.connection_status = ttk.Label(conn_frame, text="Not connected", foreground="red")
        self.connection_status.pack(pady=5)
        
        token_frame = ttk.Frame(conn_frame)
        token_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(token_frame, text="API Token:").pack(side=tk.LEFT, padx=5)
        
        # Show a masked token or prompt text
        token_text = "••••••••••••••••" if self.client.token else "No token set"
        self.token_label = ttk.Label(token_frame, text=token_text)
        self.token_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        ttk.Button(token_frame, text="Set Token", command=self.set_token).pack(side=tk.RIGHT, padx=5)
        ttk.Button(token_frame, text="Test Connection", command=self.test_connection).pack(side=tk.RIGHT, padx=5)
        
        # Database selection section
        db_frame = ttk.LabelFrame(main_frame, text="TASK DATABASE SELECTION", padding="15")
        db_frame.pack(fill=tk.X, padx=5, pady=10)
        
        db_buttons_frame = ttk.Frame(db_frame)
        db_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(db_buttons_frame, text="Refresh Databases", command=self.refresh_databases).pack(side=tk.LEFT, padx=5)
        
        # Database list
        list_frame = ttk.Frame(db_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create scrollable listbox for databases
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.db_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=5)
        self.db_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.config(command=self.db_listbox.yview)
        
        # Bind selection event
        self.db_listbox.bind('<<ListboxSelect>>', self.on_database_select)
        
        # Label to show selected database
        self.selected_db_label = ttk.Label(db_frame, text="No database selected for tasks")
        self.selected_db_label.pack(fill=tk.X, pady=5)
        
        # Log database selection section
        log_db_frame = ttk.LabelFrame(main_frame, text="SESSION LOG DATABASE", padding="15")
        log_db_frame.pack(fill=tk.X, padx=5, pady=10)
        
        log_db_desc = ttk.Label(log_db_frame, 
                               text="Select a database to store completed Pomodoro session logs.\n"
                                    "This database should have Date, Project, Task, Duration fields.")
        log_db_desc.pack(fill=tk.X, pady=5)
        
        # Database list for logs
        log_list_frame = ttk.Frame(log_db_frame)
        log_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create scrollable listbox for log databases
        log_scrollbar = ttk.Scrollbar(log_list_frame)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_db_listbox = tk.Listbox(log_list_frame, yscrollcommand=log_scrollbar.set, height=5)
        self.log_db_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        log_scrollbar.config(command=self.log_db_listbox.yview)
        
        # Bind selection event
        self.log_db_listbox.bind('<<ListboxSelect>>', self.on_log_database_select)
        
        # Label to show selected log database
        self.log_db_label = ttk.Label(log_db_frame, text="No database selected for session logs")
        self.log_db_label.pack(fill=tk.X, pady=5)
        
        # Auto-log checkbox
        log_options_frame = ttk.Frame(log_db_frame)
        log_options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(
            log_options_frame, 
            text="Automatically log completed Pomodoro sessions to Notion", 
            variable=self.auto_log_sessions
        ).pack(anchor=tk.W, padx=5)
        
        # Manual log button
        ttk.Button(
            log_options_frame, 
            text="Log Recent Sessions to Notion", 
            command=self.log_recent_sessions,
            width=25
        ).pack(anchor=tk.W, padx=5, pady=5)
        
        # Task synchronization section
        sync_frame = ttk.LabelFrame(main_frame, text="TASK SYNCHRONIZATION", padding="15")
        sync_frame.pack(fill=tk.X, padx=5, pady=10)
        
        sync_buttons = ttk.Frame(sync_frame)
        sync_buttons.pack(fill=tk.X, pady=10)
        
        ttk.Button(sync_buttons, text="Import Tasks from Notion", command=self.import_tasks, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(sync_buttons, text="Export Tasks to Notion", command=self.export_tasks, width=25).pack(side=tk.LEFT, padx=5)
        
        # Auto-sync options
        auto_sync_frame = ttk.Frame(sync_frame)
        auto_sync_frame.pack(fill=tk.X, pady=5)
        
        self.auto_sync_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(auto_sync_frame, text="Auto-sync new tasks to Notion", variable=self.auto_sync_var).pack(anchor=tk.W, padx=5)
        
        # Close button at bottom
        ttk.Button(main_frame, text="Close", command=self.window.withdraw).pack(pady=10)
        
        # Update UI based on current state
        self.update_connection_status()
        self.populate_database_list()
        
    def show(self):
        """Show the Notion integration window"""
        self.window.deiconify()
        self.window.lift()
        
    def set_token(self):
        """Prompt for and set the Notion API token"""
        token = simpledialog.askstring("Notion API Token", 
                                     "Enter your Notion integration token:",
                                     parent=self.window)
        
        if token:
            self.client.set_token(token)
            self.token_label.config(text="••••••••••••••••")
            self.save_config()
            self.update_connection_status()
            
    def test_connection(self):
        """Test the connection to Notion API"""
        if not self.client.token:
            messagebox.showwarning("No Token", "Please set a Notion API token first.")
            return
            
        if self.client.test_connection():
            messagebox.showinfo("Connection Successful", "Successfully connected to Notion API!")
            self.update_connection_status(True)
        else:
            messagebox.showerror("Connection Failed", "Could not connect to Notion API. Please check your token.")
            self.update_connection_status(False)
            
    def update_connection_status(self, force_status=None):
        """Update the connection status display"""
        if force_status is not None:
            is_connected = force_status
        else:
            is_connected = self.client.test_connection() if self.client.token else False
            
        if is_connected:
            self.connection_status.config(text="Connected to Notion", foreground="green")
        else:
            self.connection_status.config(text="Not connected", foreground="red")
            
    def refresh_databases(self):
        """Refresh the list of available Notion databases"""
        if not self.client.token:
            messagebox.showwarning("No Token", "Please set a Notion API token first.")
            return
            
        # Show a wait cursor
        self.window.config(cursor="wait")
        self.window.update()
        
        try:
            # Get databases from Notion
            self.databases = self.client.get_databases()
            
            # Populate the listboxes
            self.populate_database_list()
            
            # Provide feedback about the result
            if not self.databases:
                messagebox.showinfo("No Databases Found", 
                                  "No databases were found. Make sure you have:\n\n"
                                  "1. Created at least one database in Notion\n"
                                  "2. Shared the database with your integration\n"
                                  "3. Given the integration the correct permissions")
        finally:
            # Restore normal cursor
            self.window.config(cursor="")
        
    def populate_database_list(self):
        """Populate the listbox with available databases"""
        self.db_listbox.delete(0, tk.END)
        self.log_db_listbox.delete(0, tk.END)
        
        for db in self.databases:
            title = self.get_database_title(db)
            
            # Add to both listboxes
            self.db_listbox.insert(tk.END, title)
            self.log_db_listbox.insert(tk.END, title)
            
            # If this is the previously selected task database, select it
            if db.get("id") == self.selected_database:
                index = self.databases.index(db)
                self.db_listbox.selection_set(index)
                self.selected_db_label.config(text=f"Selected for tasks: {title}")
                
            # If this is the previously selected log database, select it
            if db.get("id") == self.log_database:
                index = self.databases.index(db)
                self.log_db_listbox.selection_set(index)
                self.log_db_label.config(text=f"Selected for logs: {title}")
                
    def get_database_title(self, db):
        """Extract the title from a database object"""
        try:
            title = db.get("title", [{}])[0].get("plain_text", "Untitled Database")
            return title
        except (IndexError, KeyError, AttributeError):
            try:
                # Try alternative way of getting title
                title = db.get("properties", {}).get("title", {}).get("title", {}).get("name", "Untitled Database")
                return title
            except (IndexError, KeyError, AttributeError):
                return "Untitled Database"
            
    def on_database_select(self, event):
        """Handle task database selection from the listbox"""
        selection = self.db_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.databases):
            selected_db = self.databases[index]
            self.selected_database = selected_db.get("id")
            title = self.get_database_title(selected_db)
            self.selected_db_label.config(text=f"Selected for tasks: {title}")
            self.save_config()
            
    def on_log_database_select(self, event):
        """Handle log database selection from the listbox"""
        selection = self.log_db_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.databases):
            selected_db = self.databases[index]
            self.log_database = selected_db.get("id")
            title = self.get_database_title(selected_db)
            self.log_db_label.config(text=f"Selected for logs: {title}")
            self.save_config()
            
    def import_tasks(self):
        """Import tasks from selected Notion database"""
        if not self.client.token:
            messagebox.showwarning("No Token", "Please connect to Notion first.")
            return
            
        if not self.selected_database:
            messagebox.showwarning("No Database", "Please select a Notion database first.")
            return
            
        # Get tasks from the selected database
        notion_tasks = self.client.get_database_tasks(self.selected_database)
        if not notion_tasks:
            messagebox.showinfo("No Tasks", "No tasks found in the selected database.")
            return
            
        # Count how many new tasks were imported
        imported_count = 0
        
        # Process each task
        for task in notion_tasks:
            # Extract task properties
            try:
                task_name = self.extract_task_name(task)
                project_name = self.extract_project_name(task)
                
                if task_name and project_name:
                    # Format as "Project: Task" to match app's format
                    task_key = f"{project_name}: {task_name}"
                    
                    # Add to projects if needed
                    if project_name not in self.pomodoro_app.projects:
                        self.pomodoro_app.projects.append(project_name)
                        
                    # Add to tasks if not already present
                    if task_key not in self.pomodoro_app.tasks:
                        self.pomodoro_app.tasks.append(task_key)
                        imported_count += 1
            except:
                # Skip tasks that can't be processed
                continue
                
        # Update the UI
        if imported_count > 0:
            self.pomodoro_app.project_combo['values'] = self.pomodoro_app.projects
            self.pomodoro_app.task_combo['values'] = self.pomodoro_app.tasks
            self.pomodoro_app.save_data()
            messagebox.showinfo("Import Complete", f"Successfully imported {imported_count} tasks from Notion.")
        else:
            messagebox.showinfo("No New Tasks", "No new tasks were imported from Notion.")
            
    def extract_task_name(self, task):
        """Extract the task name from a Notion task object"""
        try:
            # Try to get name from title property
            name_prop = task.get("properties", {}).get("Name", {}) or task.get("properties", {}).get("name", {}) or task.get("properties", {}).get("Title", {})
            
            if "title" in name_prop:
                title_content = name_prop.get("title", [])
                if title_content and len(title_content) > 0:
                    return title_content[0].get("plain_text", "")
        except:
            pass
            
        return None
        
    def extract_project_name(self, task):
        """Extract the project name from a Notion task object"""
        try:
            # Try to get project from multi_select property (Tags)
            tags_prop = task.get("properties", {}).get("Tags", {}) or task.get("properties", {}).get("Project", {})
            
            if "multi_select" in tags_prop:
                tags = tags_prop.get("multi_select", [])
                if tags and len(tags) > 0:
                    return tags[0].get("name", "Default Project")
            
            # If no tags found, return default project
            return "Default Project"
        except:
            return "Default Project"
            
    def export_tasks(self):
        """Export tasks from app to Notion database"""
        if not self.client.token:
            messagebox.showwarning("No Token", "Please connect to Notion first.")
            return
            
        if not self.selected_database:
            messagebox.showwarning("No Database", "Please select a Notion database first.")
            return
            
        # Ask which tasks to export
        export_options = ["All Tasks", "Selected Project Tasks"]
        choice = simpledialog.askstring("Export Tasks", 
                                      "Export options:\n1. All Tasks\n2. Selected Project Tasks\n\nEnter choice (1 or 2):",
                                      parent=self.window)
        
        if not choice or choice not in ["1", "2"]:
            return
            
        tasks_to_export = []
        if choice == "1":  # All Tasks
            tasks_to_export = self.pomodoro_app.tasks
        else:  # Selected Project Tasks
            selected_project = self.pomodoro_app.project_combo.get()
            if not selected_project:
                messagebox.showwarning("No Project Selected", "Please select a project first.")
                return
                
            # Filter tasks by the selected project
            tasks_to_export = [task for task in self.pomodoro_app.tasks if task.startswith(f"{selected_project}:")]
            
        if not tasks_to_export:
            messagebox.showinfo("No Tasks", "No tasks to export.")
            return
            
        # Export tasks to Notion
        exported_count = 0
        for task_key in tasks_to_export:
            # Split into project and task name
            parts = task_key.split(": ", 1)
            if len(parts) == 2:
                project_name, task_name = parts
                
                # Create task in Notion
                result = self.client.create_task(self.selected_database, task_name, project_name)
                if result:
                    exported_count += 1
                    
        if exported_count > 0:
            messagebox.showinfo("Export Complete", f"Successfully exported {exported_count} tasks to Notion.")
        else:
            messagebox.showinfo("Export Failed", "Failed to export tasks to Notion.")
            
    def add_task_to_notion(self, project, task):
        """Add a single task to Notion (called when auto-sync is enabled)"""
        if not self.auto_sync_var.get() or not self.client.token or not self.selected_database:
            return False
            
        result = self.client.create_task(self.selected_database, task, project)
        return result is not None
        
    def log_session_to_notion(self, session):
        """Log a completed session to Notion"""
        if not self.client.token or not self.log_database:
            return False
            
        # Extract session details
        project = session.get("project")
        task = session.get("task")
        start_time = session.get("start_time")
        end_time = session.get("end_time")
        duration_seconds = session.get("duration_seconds")
        
        if not all([project, task, start_time, end_time, duration_seconds]):
            return False
            
        # Log to Notion using the simplified method with better error handling
        result = self.client.log_simple_session(
            self.log_database,
            project,
            task,
            start_time,
            end_time,
            duration_seconds
        )
        
        return result is not None
    
    def log_recent_sessions(self):
        """Manually log recent sessions to Notion with duplicate prevention"""
        if not self.client.token:
            messagebox.showwarning("No Token", "Please connect to Notion first.")
            return
            
        if not self.log_database:
            messagebox.showwarning("No Log Database", "Please select a database for session logs first.")
            return
            
        # Ask how many recent sessions to log
        date_options = ["Today's Sessions", "Yesterday's Sessions", "Last 7 Days", "All Sessions"]
        choice = simpledialog.askstring("Log Sessions", 
                                      "Which sessions would you like to log to Notion?\n\n"
                                      "1. Today's Sessions\n"
                                      "2. Yesterday's Sessions\n"
                                      "3. Last 7 Days\n"
                                      "4. All Sessions\n\n"
                                      "Enter choice (1-4):",
                                      parent=self.window)
        
        if not choice or choice not in ["1", "2", "3", "4"]:
            return
            
        # Determine date range
        today = datetime.now().date()
        if choice == "1":  # Today
            start_date = today
            date_desc = "today"
        elif choice == "2":  # Yesterday
            start_date = today - timedelta(days=1)
            end_date = start_date
            date_desc = "yesterday"
        elif choice == "3":  # Last 7 days
            start_date = today - timedelta(days=6)
            date_desc = "the last 7 days"
        else:  # All sessions
            start_date = None
            date_desc = "all time"
            
        # Filter sessions
        sessions_to_log = []
        for session in self.pomodoro_app.task_sessions:
            # Skip sessions that are already logged to Notion
            if session.get("notion_logged", False):
                continue
                
            if not start_date:  # All sessions
                sessions_to_log.append(session)
            else:
                session_date = datetime.fromisoformat(session["start_time"]).date()
                if choice in ["1", "3"]:  # Today or Last 7 days
                    if start_date <= session_date <= today:
                        sessions_to_log.append(session)
                elif choice == "2":  # Yesterday
                    if session_date == start_date:
                        sessions_to_log.append(session)
                    
        if not sessions_to_log:
            messagebox.showinfo("No Sessions", f"No new sessions found for {date_desc} to log.")
            return
            
        # Confirm with user
        if not messagebox.askyesno("Confirm", 
                                  f"This will log {len(sessions_to_log)} new sessions from {date_desc} to Notion.\n\n"
                                  f"Continue?"):
            return
            
        # Log sessions
        successful = 0
        for session in sessions_to_log:
            if self.log_session_to_notion(session):
                # Mark session as logged to prevent duplicates
                session["notion_logged"] = True
                successful += 1
        
        # Save the updated session data
        self.pomodoro_app.save_data()
                
        # Show results
        if successful > 0:
            messagebox.showinfo("Logging Complete", 
                               f"Successfully logged {successful} of {len(sessions_to_log)} sessions to Notion.")
        else:
            messagebox.showwarning("Logging Failed", 
                                 f"Failed to log sessions to Notion. Please check your database configuration.")


# Function to integrate Notion with the Pomodoro Timer class
def add_notion_integration(pomodoro_timer):
    """Add Notion integration to the Pomodoro Timer application"""
    
    # Create the Notion integration
    notion_integration = NotionIntegration(pomodoro_timer.root, pomodoro_timer)
    
    # Find a suitable settings frame using a more flexible approach
    settings_frame = None
    
    # First, try to find settings frames by looking through the widget hierarchy
    try:
        # Look for frames that might contain settings
        for frame in pomodoro_timer.root.winfo_children():
            if isinstance(frame, ttk.Frame) or isinstance(frame, tk.Frame):
                for child in frame.winfo_children():
                    if isinstance(child, ttk.LabelFrame):
                        # Check if this is likely a settings frame
                        child_str = str(child).lower()
                        if "settings" in child_str or "control" in child_str or "option" in child_str:
                            settings_frame = child
                            break
                if settings_frame:
                    break
                    
        # If no settings frame found, try to find the last LabelFrame as fallback
        if not settings_frame:
            main_frame = None
            for widget in pomodoro_timer.root.winfo_children():
                if isinstance(widget, ttk.Frame) or isinstance(widget, tk.Frame):
                    main_frame = widget
                    break
                    
            if main_frame:
                last_frame = None
                for child in main_frame.winfo_children():
                    if isinstance(child, ttk.LabelFrame):
                        last_frame = child
                        
                if last_frame:
                    settings_frame = last_frame
    except Exception as e:
        print(f"Error finding settings frame: {e}")
    
    # If still no settings frame found, create a new one
    if not settings_frame:
        try:
            main_container = pomodoro_timer.root.winfo_children()[0]  # Assume first child is main container
            settings_frame = ttk.LabelFrame(main_container, text="SETTINGS")
            settings_frame.pack(fill=tk.X, padx=5, pady=10)
        except Exception as e:
            print(f"Error creating settings frame: {e}")
            # Last resort - use the root as the parent
            settings_frame = ttk.LabelFrame(pomodoro_timer.root, text="SETTINGS")
            settings_frame.pack(fill=tk.X, padx=5, pady=10)
    
    # Add Notion button to the settings frame
    notion_button = ttk.Button(settings_frame, text="🔄 Notion Sync", 
                              command=notion_integration.show, width=15)
    notion_button.pack(side=tk.RIGHT, padx=10)
    
    # Override the add_task method to support auto-sync
    original_add_task = pomodoro_timer.add_task
    
    def new_add_task(event=None):
        # Call the original method first
        original_add_task(event)
        
        # If auto-sync is enabled, sync the new task to Notion
        project = pomodoro_timer.project_combo.get()
        task = pomodoro_timer.task_combo.get().replace(f"{project}: ", "") if project in pomodoro_timer.task_combo.get() else pomodoro_timer.task_combo.get()
        
        if notion_integration.auto_sync_var.get() and project and task:
            # Try to add to Notion
            if notion_integration.add_task_to_notion(project, task):
                print(f"Task '{task}' auto-synced to Notion")
    
    # Replace the add_task method
    pomodoro_timer.add_task = new_add_task
    
    # Override the record_task_session method to support auto-logging
    original_record_session = pomodoro_timer.record_task_session
    
    def new_record_task_session():
        # Call the original method first
        original_record_session()
        
        # If auto-logging is enabled, log the session to Notion
        if notion_integration.auto_log_sessions.get() and notion_integration.log_database:
            # Get the most recently added session
            if pomodoro_timer.task_sessions:
                latest_session = pomodoro_timer.task_sessions[-1]
                
                # Skip if already logged to Notion
                if latest_session.get("notion_logged", False):
                    return
                    
                # Try to log to Notion
                if notion_integration.log_session_to_notion(latest_session):
                    # Mark as logged to prevent duplicates
                    latest_session["notion_logged"] = True
                    pomodoro_timer.save_data()
                    print(f"Session logged to Notion: {latest_session['project']} - {latest_session['task']}")
    
    # Replace the record_task_session method
    pomodoro_timer.record_task_session = new_record_task_session
    
    return notion_integration
