import os
import csv
from datetime import datetime

# --- Configuration ---
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'daily_log.csv')
HEADERS = ['LogDate', 'MoodRating', 'HadExercise', 'GotEnoughSleep', 'HadSocialInteraction', 'AteHealthy', 'Notes']

# --- Helper Functions ---

def ensure_data_directory_exists():
    """Ensures the 'data' directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created data directory: {DATA_DIR}")

def initialize_data_file():
    """
    Checks if the CSV data file exists and creates it with headers if not.
    """
    ensure_data_directory_exists()
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
        print(f"Created new data file with headers: {DATA_FILE}")

def save_daily_log(log_entry):
    """
    Saves a single daily log entry to the CSV file.
    log_entry should be a dictionary matching the HEADERS.
    """
    initialize_data_file() # Ensure file exists before writing
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(log_entry)
    print(f"Log for {log_entry['LogDate']} saved successfully!")

def load_all_logs():
    """
    Loads all historical daily log entries from the CSV file.
    Returns a list of dictionaries.
    """
    if not os.path.exists(DATA_FILE):
        return [] # Return empty list if file doesn't exist yet

    logs = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            logs.append(row)
    return logs

# --- Main Application Logic (Placeholder for now) ---

def get_user_input(prompt, type_func=str, valid_options=None):
    """Helper to get validated user input."""
    while True:
        user_input = input(prompt).strip()
        try:
            value = type_func(user_input)
            if valid_options and value not in valid_options:
                print(f"Invalid input. Please choose from {valid_options}.")
                continue
            return value
        except ValueError:
            print("Invalid input type. Please try again.")

def record_daily_entry():
    """Guides the user through recording a daily log entry."""
    print("\n--- Record Your Daily Log ---")
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"Logging for today: {today_str}")

    # Check if a log for today already exists
    existing_logs = load_all_logs()
    if any(log['LogDate'] == today_str for log in existing_logs):
        print("You've already logged for today. Please run analysis or try again tomorrow.")
        return

    mood = get_user_input("Mood (1=Bad, 5=Great): ", type_func=int, valid_options=range(1, 6))
    exercise = get_user_input("Did you exercise today? (y/n): ", type_func=str.lower, valid_options=['y', 'n']) == 'y'
    sleep = get_user_input("Did you get 7+ hours of sleep? (y/n): ", type_func=str.lower, valid_options=['y', 'n']) == 'y'
    social = get_user_input("Did you socialize today? (y/n): ", type_func=str.lower, valid_options=['y', 'n']) == 'y'
    healthy_eating = get_user_input("Did you eat healthy meals today? (y/n): ", type_func=str.lower, valid_options=['y', 'n']) == 'y'
    notes = input("Any significant notes/events today (optional)? ").strip()

    new_log = {
        'LogDate': today_str,
        'MoodRating': mood,
        'HadExercise': exercise,
        'GotEnoughSleep': sleep,
        'HadSocialInteraction': social,
        'AteHealthy': healthy_eating,
        'Notes': notes
    }
    save_daily_log(new_log)

def main_menu():
    """Displays the main menu and handles user choices."""
    while True:
        print("\n--- Personal Habit & Mood Linker ---")
        print("1. Record Daily Log")
        print("2. View All Logs (Raw Data)")
        print("3. Exit") # Placeholder for now, analysis will go here later
        
        choice = get_user_input("Enter your choice: ", type_func=int, valid_options=[1, 2, 3])

        if choice == 1:
            record_daily_entry()
        elif choice == 2:
            all_logs = load_all_logs()
            if not all_logs:
                print("No logs recorded yet.")
            else:
                print("\n--- All Recorded Logs ---")
                for log in all_logs:
                    print(log) # Simple print for now
        elif choice == 3:
            print("Exiting. Keep tracking your well-being!")
            break

if __name__ == "__main__":
    main_menu()
