import requests
import json
from datetime import datetime

class WeatherService:
    def __init__(self, api_key=None):
        # Using OpenWeatherMap API (free tier available)
        self.api_key = api_key or "your_api_key_here"
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    def get_current_weather(self, city="London", lat=None, lon=None):
        """Get current weather data"""
        params = {
            'appid': self.api_key,
            'units': 'metric'  # Celsius
        }
        
        if lat and lon:
            params['lat'] = lat
            params['lon'] = lon
        else:
            params['q'] = city
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Weather API error: {e}")
            return None
    
    def calculate_weather_mood_score(self, weather_data):
        """Calculate weather impact on mood (0-10 scale, 5 = neutral)"""
        if not weather_data:
            return 5.0, []
        
        score = 5.0  # Start neutral
        factors = []
        
        # Temperature impact
        temp = weather_data['main']['temp']
        if 18 <= temp <= 25:  # Ideal temperature range
            score += 1.5
            factors.append(f"Comfortable temperature ({temp}°C)")
        elif 15 <= temp < 18 or 25 < temp <= 28:
            score += 0.5
            factors.append(f"Pleasant temperature ({temp}°C)")
        elif temp < 5 or temp > 35:
            score -= 2.0
            factors.append(f"Extreme temperature ({temp}°C)")
        elif temp < 15 or temp > 28:
            score -= 1.0
            factors.append(f"Uncomfortable temperature ({temp}°C)")
        
        # Humidity impact
        humidity = weather_data['main']['humidity']
        if 40 <= humidity <= 60:  # Ideal humidity
            score += 0.5
            factors.append(f"Comfortable humidity ({humidity}%)")
        elif humidity > 80:
            score -= 1.5
            factors.append(f"High humidity ({humidity}%)")
        elif humidity < 30:
            score -= 0.5
            factors.append(f"Low humidity ({humidity}%)")
        
        # Weather condition impact
        condition = weather_data['weather'][0]['main'].lower()
        if condition in ['clear', 'sunny']:
            score += 2.0
            factors.append("Clear/sunny weather")
        elif condition in ['clouds']:
            cloud_cover = weather_data.get('clouds', {}).get('all', 0)
            if cloud_cover < 30:
                score += 1.0
                factors.append("Partly cloudy")
            elif cloud_cover > 80:
                score -= 1.0
                factors.append("Overcast")
        elif condition in ['rain', 'drizzle']:
            score -= 1.5
            factors.append("Rainy weather")
        elif condition in ['thunderstorm']:
            score -= 2.0
            factors.append("Thunderstorm")
        elif condition in ['snow']:
            score -= 1.0
            factors.append("Snowy weather")
        elif condition in ['mist', 'fog']:
            score -= 0.5
            factors.append("Misty/foggy")
        
        # Wind impact
        wind_speed = weather_data.get('wind', {}).get('speed', 0)
        if wind_speed > 10:  # m/s
            score -= 1.0
            factors.append(f"Strong winds ({wind_speed} m/s)")
        elif 2 <= wind_speed <= 5:
            score += 0.3
            factors.append("Gentle breeze")
        
        # Air pressure impact (if available)
        pressure = weather_data['main'].get('pressure')
        if pressure:
            if pressure < 1000:  # Low pressure
                score -= 0.8
                factors.append(f"Low air pressure ({pressure} hPa)")
            elif pressure > 1020:  # High pressure
                score += 0.5
                factors.append(f"High air pressure ({pressure} hPa)")
        
        # Ensure score stays within bounds
        score = max(0, min(10, score))
        
        return round(score, 1), factors
    
    def get_weather_mood_prediction(self, weather_data, user_patterns=None):
        """Predict mood impact based on weather and user patterns"""
        base_score, factors = self.calculate_weather_mood_score(weather_data)
        
        # If we have user-specific patterns, adjust the score
        if user_patterns:
            # This would use machine learning in a full implementation
            # For now, we'll use simple pattern matching
            temp = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            condition = weather_data['weather'][0]['main']
            
            # Find matching patterns and adjust score
            for pattern in user_patterns:
                if self._matches_pattern(temp, humidity, condition, pattern):
                    adjustment = pattern['avg_mood_impact'] - 5.0  # Convert to adjustment
                    base_score += adjustment * 0.3  # Weight user patterns
                    factors.append(f"Personal pattern: {pattern['weather_condition']}")
                    break
        
        return {
            'mood_score': round(base_score, 1),
            'impact_factors': factors,
            'recommendation': self._get_weather_recommendation(base_score, factors)
        }
    
    def _matches_pattern(self, temp, humidity, condition, pattern):
        """Check if current weather matches a stored pattern"""
        # Simple pattern matching - could be more sophisticated
        return pattern['weather_condition'].lower() == condition.lower()
    
    def _get_weather_recommendation(self, score, factors):
        """Generate recommendations based on weather impact"""
        if score >= 7:
            return "Perfect weather for outdoor activities! Consider exercising outside."
        elif score >= 5.5:
            return "Good weather conditions. Great day for a walk or outdoor time."
        elif score >= 4:
            return "Weather might affect your mood slightly. Consider indoor activities."
        else:
            return "Weather conditions may negatively impact mood. Focus on indoor comfort and self-care."