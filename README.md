# Pomodoro Timer with Notion Integration

A desktop app that combines the Pomodoro time management technique with task tracking and Notion integration. Stay focused, track your time, and sync your tasks and completed sessions with Notion.

![Pomodoro Timer with Notion Integration](https://github.com/user/Pomodoro-Timer-Task-Tracker/raw/main/PomodoroNotion/screenshots/app_screenshot.png)

## Features

- **Pomodoro Timer**: 25-minute work intervals followed by 5-minute short breaks and 15-minute long breaks
- **Task Management**: Create and organize tasks by project
- **Session Tracking**: Record and view your work sessions with detailed statistics
- **Notion Integration**: Sync tasks and session logs with your Notion workspace
- **Export Reports**: Generate CSV reports of your productivity data
- **Modern UI**: Clean, intuitive interface with customizable themes

## Requirements

- Python 3.6+
- Tkinter (included with most Python installations)
- Pillow (PIL Fork)
- Requests
- ttkthemes (optional, for enhanced UI)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/user/Pomodoro-Timer-Task-Tracker.git
   cd Pomodoro-Timer-Task-Tracker/PomodoroNotion
   ```

2. Install dependencies:
   ```
   pip install pillow requests ttkthemes
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage

### Basic Pomodoro Timer

1. Set up your tasks by selecting or creating a project and task
2. Click "Start" to begin a 25-minute Pomodoro session
3. Work until the timer completes
4. Take a short break (5 minutes) or a long break (15 minutes) after every 4 Pomodoros
5. Repeat the cycle

### Task Management

- Create new projects and tasks using the "Add" buttons
- Delete projects and tasks using the "Delete" buttons
- Track your completed sessions in the Session History section

### Notion Integration

1. Click "Notion Sync" in the settings area
2. Enter your Notion API token
3. Select databases for tasks and session logs
4. Choose to import/export tasks or log sessions to Notion
5. Enable auto-sync for seamless integration

## Getting a Notion API Token

1. Go to [Notion Developers](https://www.notion.so/my-integrations)
2. Create a new integration
3. Set appropriate permissions (read/write for databases you want to access)
4. Copy the token and use it in the app's Notion Sync settings

## File Structure

- `main.py`: Application entry point
- `pomodoro_timer.py`: Core timer and task tracking functionality
- `notion_integration.py`: Notion API integration features
- `pomodoro_data.json`: Local storage for tasks and session data
- `notion_config.json`: Configuration for Notion integration


