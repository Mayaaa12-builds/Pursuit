import csv
import sqlite3
from database import HabitDatabase

def migrate_csv_data():
    db = HabitDatabase()
    
    # Create a default user for existing data
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, email, password_hash) 
        VALUES (1, 'default@user.com', 'temp_hash')
    ''')
    
    # Read existing CSV data
    with open('data/daily_log.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT OR IGNORE INTO daily_logs 
                (user_id, date, mood_score, habits)
                VALUES (1, ?, ?, ?)
            ''', (row['date'], row['mood'], row['habits']))
    
    conn.commit()
    conn.close()
    print("Migration completed!")

if __name__ == "__main__":
    migrate_csv_data()