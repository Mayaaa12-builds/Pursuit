Personal Habit & Mood Linker
Project Pitch
"Tired of guessing what truly affects your mood? Our Personal Habit & Mood Linker helps you uncover the hidden connections between your daily habits—like sleep and exercise—and your well-being. By simply logging your day, you'll gain personalized insights to cultivate more positive days."

Problem & Solution Statement
Individuals often lack a simple, personalized tool to understand how their daily habits specifically correlate with their mood, making it difficult to identify actionable strategies for improved well-being.

The Personal Habit & Mood Linker solves this by providing an easy-to-use platform for daily logging that then generates personalized insights, revealing the direct relationships between a user's routines and their emotional state.

Features
Daily Logging: A simple interface for users to manually input their mood rating and the status of various habits (e.g., exercise, sleep, social interaction) on a daily basis. The system now also captures additional contextual data such as sleep hours, stress levels, and weather.

Data Storage: All user data is now stored securely and efficiently in a local SQLite database, moving away from a simple CSV file. This allows for more robust data management and complex queries.

Personalized Insights & Analytics: The tool analyzes the stored data to provide correlations between habits, mood, and contextual factors, offering actionable feedback and deeper analytical insights.

Data-Driven Feedback Loop: The tool creates a direct feedback loop for self-improvement, allowing users to see the impact of their choices and proactively cultivate more positive routines.

Installation & Setup
Prerequisites
Python 3.6 or higher installed.

The sqlite3 library (typically comes pre-installed with Python).

Steps
Create a Project Directory:

mkdir personal_habit_tracker
cd personal_habit_tracker

Set Up a Virtual Environment:

python -m venv venv

Activate the Virtual Environment:

On Windows:

.\venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

Create Project Structure:

Create the main Python script file, main.py.

The SQLite database file (habit_tracker.db) will be created automatically when you run the application.

touch main.py

Run the Application:
Once your code is complete, you can run the application from your terminal:

python main.py
