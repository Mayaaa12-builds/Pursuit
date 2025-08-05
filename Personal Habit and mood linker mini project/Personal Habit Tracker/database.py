import sqlite3
import os
import csv
import json
from datetime import datetime

class HabitDatabase:
    def __init__(self, db_path='habit_tracker.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with weather-enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subscription_tier TEXT DEFAULT 'free'
            )
        ''')
        
        # Habits table for better normalization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                target_frequency INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Habit completions for detailed tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habit_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                date DATE NOT NULL,
                completed BOOLEAN DEFAULT TRUE,
                notes TEXT,
                FOREIGN KEY (habit_id) REFERENCES habits(id),
                UNIQUE(habit_id, date)
            )
        ''')
        
        # Enhanced daily_logs table with weather data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                log_date DATE NOT NULL,
                mood_rating INTEGER NOT NULL CHECK (mood_rating >= 1 AND mood_rating <= 5),
                had_exercise BOOLEAN NOT NULL,
                got_enough_sleep BOOLEAN NOT NULL,
                had_social_interaction BOOLEAN NOT NULL,
                ate_healthy BOOLEAN NOT NULL,
                notes TEXT,
                
                -- Weather data
                temperature REAL,
                humidity INTEGER,
                weather_condition TEXT,
                precipitation REAL DEFAULT 0,
                cloud_cover INTEGER,
                wind_speed REAL,
                air_pressure REAL,
                uv_index INTEGER,
                
                -- Calculated weather impact
                weather_mood_score REAL,
                weather_impact_factors TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, log_date)
            )
        ''')
        
        # Weather mood patterns table for learning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_mood_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                temperature_range TEXT,
                humidity_range TEXT,
                weather_condition TEXT,
                avg_mood_impact REAL,
                sample_count INTEGER DEFAULT 1,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    
    def migrate_csv_data(self, csv_file_path):
        """Migrate existing CSV data to SQLite"""
        if not os.path.exists(csv_file_path):
            print(f"CSV file not found: {csv_file_path}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                migrated_count = 0
                
                for row in reader:
                    # Convert string booleans to actual booleans
                    had_exercise = row['HadExercise'].lower() == 'true'
                    got_enough_sleep = row['GotEnoughSleep'].lower() == 'true'
                    had_social_interaction = row['HadSocialInteraction'].lower() == 'true'
                    ate_healthy = row['AteHealthy'].lower() == 'true'
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO daily_logs 
                        (user_id, log_date, mood_rating, had_exercise, got_enough_sleep, 
                         had_social_interaction, ate_healthy, notes)
                        VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['LogDate'],
                        int(row['MoodRating']),
                        had_exercise,
                        got_enough_sleep,
                        had_social_interaction,
                        ate_healthy,
                        row['Notes']
                    ))
                    migrated_count += 1
                
                conn.commit()
                print(f"Successfully migrated {migrated_count} records from CSV to SQLite!")
                return True
                
        except Exception as e:
            conn.rollback()
            print(f"Error during migration: {e}")
            return False
        finally:
            conn.close()
    
    def save_daily_log(self, log_entry, user_id=1):
        """Save daily log entry to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_logs 
                (user_id, log_date, mood_rating, had_exercise, got_enough_sleep, 
                 had_social_interaction, ate_healthy, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                log_entry['LogDate'],
                log_entry['MoodRating'],
                log_entry['HadExercise'],
                log_entry['GotEnoughSleep'],
                log_entry['HadSocialInteraction'],
                log_entry['AteHealthy'],
                log_entry['Notes']
            ))
            conn.commit()
            print(f"Log for {log_entry['LogDate']} saved successfully to database!")
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving log: {e}")
            return False
        finally:
            conn.close()
    
    def save_daily_log_with_weather(self, log_entry, weather_data=None, user_id=1):
        """Save daily log entry with weather data to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if weather_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_logs 
                    (user_id, log_date, mood_rating, had_exercise, got_enough_sleep, 
                     had_social_interaction, ate_healthy, notes, temperature, humidity,
                     weather_condition, precipitation, cloud_cover, wind_speed, 
                     air_pressure, uv_index, weather_mood_score, weather_impact_factors)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    log_entry['LogDate'],
                    log_entry['MoodRating'],
                    log_entry['HadExercise'],
                    log_entry['GotEnoughSleep'],
                    log_entry['HadSocialInteraction'],
                    log_entry['AteHealthy'],
                    log_entry['Notes'],
                    weather_data.get('temperature'),
                    weather_data.get('humidity'),
                    weather_data.get('condition'),
                    weather_data.get('precipitation', 0),
                    weather_data.get('cloud_cover'),
                    weather_data.get('wind_speed'),
                    weather_data.get('air_pressure'),
                    weather_data.get('uv_index'),
                    weather_data.get('mood_score'),
                    json.dumps(weather_data.get('impact_factors', {}))
                ))
            else:
                # Fallback to regular save without weather
                return self.save_daily_log(log_entry, user_id)
            
            conn.commit()
            print(f"Log for {log_entry['LogDate']} saved with weather data!")
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving log with weather: {e}")
            return False
        finally:
            conn.close()
    
    def load_all_logs(self, user_id=1):
        """Load all logs for a user from SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT log_date, mood_rating, had_exercise, got_enough_sleep, 
                   had_social_interaction, ate_healthy, notes, temperature,
                   humidity, weather_condition, weather_mood_score
            FROM daily_logs 
            WHERE user_id = ?
            ORDER BY log_date DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries matching original format
        logs = []
        for row in results:
            log_entry = {
                'LogDate': row[0],
                'MoodRating': row[1],
                'HadExercise': row[2],
                'GotEnoughSleep': row[3],
                'HadSocialInteraction': row[4],
                'AteHealthy': row[5],
                'Notes': row[6]
            }
            
            # Add weather data if available
            if row[7] is not None:
                log_entry['Weather'] = {
                    'temperature': row[7],
                    'humidity': row[8],
                    'condition': row[9],
                    'mood_score': row[10]
                }
            
            logs.append(log_entry)
        
        return logs
    
    def get_weather_mood_patterns(self, user_id=1):
        """Get weather mood patterns for analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT temperature_range, humidity_range, weather_condition, 
                   avg_mood_impact, sample_count
            FROM weather_mood_patterns 
            WHERE user_id = ?
            ORDER BY sample_count DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in results:
            patterns.append({
                'temperature_range': row[0],
                'humidity_range': row[1],
                'weather_condition': row[2],
                'avg_mood_impact': row[3],
                'sample_count': row[4]
            })
        
        return patterns
    
    def update_weather_pattern(self, user_id, weather_data, mood_impact):
        """Update weather mood patterns for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create temperature and humidity ranges
            temp = weather_data.get('temperature', 0)
            humidity = weather_data.get('humidity', 0)
            condition = weather_data.get('condition', 'unknown')
            
            temp_range = f"{int(temp//5)*5}-{int(temp//5)*5+5}"
            humidity_range = f"{int(humidity//10)*10}-{int(humidity//10)*10+10}"
            
            # Check if pattern exists
            cursor.execute('''
                SELECT id, avg_mood_impact, sample_count 
                FROM weather_mood_patterns 
                WHERE user_id = ? AND temperature_range = ? AND humidity_range = ? AND weather_condition = ?
            ''', (user_id, temp_range, humidity_range, condition))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pattern
                pattern_id, current_avg, current_count = existing
                new_avg = ((current_avg * current_count) + mood_impact) / (current_count + 1)
                new_count = current_count + 1
                
                cursor.execute('''
                    UPDATE weather_mood_patterns 
                    SET avg_mood_impact = ?, sample_count = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_avg, new_count, pattern_id))
            else:
                # Create new pattern
                cursor.execute('''
                    INSERT INTO weather_mood_patterns 
                    (user_id, temperature_range, humidity_range, weather_condition, avg_mood_impact)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, temp_range, humidity_range, condition, mood_impact))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating weather pattern: {e}")
            return False
        finally:
            conn.close()