import tkinter as tk
from tkinter import ttk
import sys
from pomodoro_timer import PomodoroTimer
from notion_integration import add_notion_integration

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set app icon if available
    try:
        if sys.platform == 'win32':
            root.iconbitmap("tomato.ico")
    except:
        pass
        
    # Set window title with emoji for supported platforms
    root.title("🍅 Pomodoro Timer with Notion Sync")
    
    # Apply a themed style if available
    try:
        from ttkthemes import ThemedTk, ThemedStyle
        if isinstance(root, tk.Tk):
            style = ThemedStyle(root)
            style.set_theme("arc")  # You can choose: 'arc', 'plastik', 'clearlooks', etc.
    except ImportError:
        # ttkthemes not available, use default styling
        pass
        
    # Create the main app
    app = PomodoroTimer(root)
    
    # Add Notion integration
    notion_integration = add_notion_integration(app)
    
    # Start the application
    root.mainloop()
