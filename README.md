Personal Habit & Mood Linker
Project Pitch
"Tired of guessing what truly affects your mood? Our Personal Habit & Mood Linker helps you uncover the hidden connections between your daily habits—like sleep and exercise—and your well-being. By simply logging your day, you'll gain personalized insights to cultivate more positive days."

Problem & Solution Statement
Individuals often lack a simple, personalized tool to understand how their daily habits specifically correlate with their mood, making it difficult to identify actionable strategies for improved well-being.

The Personal Habit & Mood Linker solves this by providing an easy-to-use platform for daily logging that then generates personalized insights, revealing the direct relationships between a user's routines and their emotional state.

Features
Daily Logging: A simple interface for users to manually input their mood rating and the status of various habits (e.g., exercise, sleep, social interaction) on a daily basis.

Data Storage: All user data is stored locally in a CSV file, ensuring privacy and ease of use for beginners.

Personalized Insights: The tool analyzes the stored data to provide correlations between habits and mood, offering actionable feedback such as:

"Your average mood on days you exercised was 4.2/5, compared to 3.1/5 on days you didn't."

"You typically report a mood of 4.5/5 when you get 7+ hours of sleep."

Data-Driven Feedback Loop: The tool creates a direct feedback loop for self-improvement, allowing users to see the impact of their choices and proactively cultivate more positive routines.

Installation & Setup
Prerequisites
Python 3.6 or higher installed.

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

Create a data directory to store your data file.

Create the main Python script file, main.py.

mkdir data
touch main.py

Run the Application:
Once your code is complete, you can run the application from your terminal:

python main.py
