import os
import csv
from datetime import datetime
from database import HabitDatabase
from weather_service import WeatherService

# --- Configuration ---
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'daily_log.csv')
HEADERS = ['LogDate', 'MoodRating', 'HadExercise', 'GotEnoughSleep', 'HadSocialInteraction', 'AteHealthy', 'Notes']

# Initialize services
db = HabitDatabase()
weather_service = WeatherService()

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

def save_enhanced_log(log_entry):
    """Save daily log with automatic weather analysis"""
    try:
        # Get current weather data automatically
        weather_data = weather_service.get_current_weather()
        
        if weather_data:
            # Calculate weather mood impact
            weather_score, factors = weather_service.calculate_weather_mood_score(weather_data)
            
            # Prepare weather data for database
            weather_info = {
                'temperature': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'condition': weather_data['weather'][0]['main'],
                'precipitation': weather_data.get('rain', {}).get('1h', 0),
                'cloud_cover': weather_data.get('clouds', {}).get('all', 0),
                'wind_speed': weather_data.get('wind', {}).get('speed', 0),
                'air_pressure': weather_data['main']['pressure'],
                'uv_index': weather_data.get('uvi', 0),
                'mood_score': weather_score,
                'impact_factors': factors
            }
            
            # Save to database with weather data
            success = db.save_daily_log_with_weather(log_entry, weather_info)
            
            if success:
                # Update weather patterns for learning
                db.update_weather_pattern(1, weather_info, log_entry['MoodRating'])
                print(f"✅ Log saved with weather analysis (Weather Impact: {weather_score:.1f}/10)")
            
        else:
            # Fallback to regular save if weather unavailable
            db.save_daily_log(log_entry)
            print("✅ Log saved (weather data unavailable)")
            
    except Exception as e:
        print(f"Error saving enhanced log: {e}")
        # Fallback to regular save
        db.save_daily_log(log_entry)

def record_daily_entry():
    """Guides the user through recording a daily log entry."""
    print("\n--- Record Your Daily Log ---")
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"Logging for today: {today_str}")

    # Check if a log for today already exists
    existing_logs = db.load_all_logs()
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
    
    # Save with automatic weather analysis
    save_enhanced_log(new_log)

def analyze_recent_trends():
    """Analyze trends from the last 5 days with weather factors"""
    logs = db.load_all_logs()
    
    if len(logs) < 2:
        print("Not enough data for analysis. Please log for a few more days.")
        return
    
    recent_logs = logs[:5]  # Last 5 days
    
    print("\n=== 5-Day Analysis with Weather Intelligence ===")
    print("\n📊 Daily Breakdown:")
    
    total_mood = 0
    weather_impacts = []
    
    for log in recent_logs:
        mood = int(log['MoodRating'])
        total_mood += mood
        
        # Display basic info
        print(f"\n📅 {log['LogDate']} - Mood: {mood}/5")
        print(f"   Exercise: {'✅' if log['HadExercise'] else '❌'} | "
              f"Sleep: {'✅' if log['GotEnoughSleep'] else '❌'} | "
              f"Social: {'✅' if log['HadSocialInteraction'] else '❌'} | "
              f"Healthy Eating: {'✅' if log['AteHealthy'] else '❌'}")
        
        # Display weather factors if available
        if 'Weather' in log and log['Weather']:
            weather = log['Weather']
            weather_score = weather.get('mood_score', 'N/A')
            weather_impacts.append(weather_score if weather_score != 'N/A' else 5.0)
            
            print(f"   🌤️ Weather Impact: {weather_score}/10 "
                  f"({weather.get('temperature', 'N/A')}°C, {weather.get('condition', 'N/A')})")
        else:
            print(f"   🌤️ Weather Impact: Not available")
        
        if log['Notes']:
            print(f"   📝 Notes: {log['Notes']}")
    
    # Summary analysis
    avg_mood = total_mood / len(recent_logs)
    print(f"\n📈 Average Mood: {avg_mood:.1f}/5")
    
    if weather_impacts:
        avg_weather_impact = sum(weather_impacts) / len(weather_impacts)
        print(f"🌤️ Average Weather Impact: {avg_weather_impact:.1f}/10")
        
        # Weather-mood correlation insight
        if avg_weather_impact > 6.5 and avg_mood > 3.5:
            print("\n💡 Insight: Good weather seems to correlate with better mood!")
        elif avg_weather_impact < 4.5 and avg_mood < 3.0:
            print("\n💡 Insight: Poor weather may be affecting your mood. Consider indoor activities.")
    
    # Get weather patterns for additional insights
    patterns = db.get_weather_mood_patterns()
    if patterns:
        print("\n🧠 Your Weather-Mood Learning:")
        for pattern in patterns[:3]:  # Top 3 patterns
            print(f"   • {pattern['weather_condition']} weather "
                  f"({pattern['temperature_range']}°C): "
                  f"Avg mood impact {pattern['avg_mood_impact']:.1f}/10 "
                  f"({pattern['sample_count']} samples)")

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
