# weather_service.py
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dotenv import load_dotenv

class WeatherService:
    def __init__(self):
        # Load API key from environment
        load_dotenv()
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "https://api.weatherapi.com/v1"
        
        if not self.api_key:
            raise ValueError("Weather API key is required")
    
    def get_basic_location_data(self, location: str) -> Dict:
        """
        Get basic location data to validate if a location exists.
        
        Args:
            location: City or location name
        
        Returns:
            Dictionary containing location data or error
        """
        endpoint = f"{self.base_url}/search.json"
        params = {
            'key': self.api_key,
            'q': location
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            results = response.json()
            
            # If the results array is empty, the location doesn't exist
            if not results:
                return {"error": f"Location '{location}' not found"}
            
            return {"location": results[0]}
        except requests.RequestException as e:
            return {"error": f"Location validation failed: {str(e)}"}
    
    def validate_location(self, location: str) -> Dict:
        """
        Check if a location exists by attempting to get its coordinates.
        
        Args:
            location: Location to validate
            
        Returns:
            Dict with validation result
        """
        try:
            result = self.get_basic_location_data(location)
            if "error" in result:
                return {"valid": False, "reason": result.get("error")}
            return {"valid": True}
        except Exception as e:
            return {"valid": False, "reason": str(e)}
    
    def get_weather_forecast(self, location: str, days: int = 10) -> Dict:
        """
        Fetch weather forecast for a specific location for up to 10 days.
        
        Args:
            location: City or location name
            days: Number of forecast days (max 10)
        
        Returns:
            Dictionary containing weather forecast data
        """
        # Ensure days is within valid range (1-10)
        days = min(max(days, 1), 10)
        
        # Build API request
        endpoint = f"{self.base_url}/forecast.json"
        params = {
            'key': self.api_key,
            'q': location,
            'days': days,
            'aqi': 'no',
            'alerts': 'yes'
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Weather forecast error: {e}")
            return {
                'error': 'Failed to fetch weather data',
                'details': str(e)
            }
    
    def get_clothing_recommendations(self, temp_c: float, condition: str) -> List[str]:
        """
        Generate clothing recommendations based on temperature and weather conditions.
        
        Args:
            temp_c: Temperature in Celsius
            condition: Weather condition description
        
        Returns:
            List of clothing recommendations
        """
        recommendations = []
        
        # Temperature-based recommendations
        if temp_c < 0:
            recommendations.extend([
                "Heavy winter coat", "Thermal underlayers", 
                "Winter hat", "Gloves", "Scarf", "Insulated boots"
            ])
        elif temp_c < 10:
            recommendations.extend([
                "Winter coat", "Sweater/layers", 
                "Light gloves", "Warm hat"
            ])
        elif temp_c < 20:
            recommendations.extend([
                "Light jacket or coat", "Long sleeves", 
                "Light scarf", "Closed-toe shoes"
            ])
        elif temp_c < 25:
            recommendations.extend([
                "Light layers", "Long or short sleeves",
                "Light pants or long shorts"
            ])
        else:
            recommendations.extend([
                "Light breathable clothing", "Short sleeves",
                "Shorts or light pants", "Sun hat"
            ])
        
        # Condition-based additions
        condition = condition.lower()
        if "rain" in condition or "drizzle" in condition or "shower" in condition:
            recommendations.extend(["Waterproof jacket", "Umbrella", "Waterproof shoes"])
        elif "snow" in condition:
            recommendations.extend(["Waterproof boots", "Snow-appropriate outerwear"])
        elif "sun" in condition or "clear" in condition:
            recommendations.extend(["Sunglasses", "Sunscreen", "Brimmed hat"])
        elif "wind" in condition:
            recommendations.append("Windbreaker")
        
        return recommendations
    
    def get_activity_recommendations(self, forecast_day: Dict) -> Dict[str, List[str]]:
        """
        Generate activity recommendations based on weather forecast.
        
        Args:
            forecast_day: Weather forecast for a specific day
        
        Returns:
            Dictionary with recommended and alternative activities
        """
        condition = forecast_day['day']['condition']['text'].lower()
        max_temp = forecast_day['day']['maxtemp_c']
        min_temp = forecast_day['day']['mintemp_c']
        avg_temp = (max_temp + min_temp) / 2
        precip_mm = forecast_day['day']['totalprecip_mm']
        
        outdoor_activities = []
        indoor_alternatives = [
            "Museum visits", "Indoor shopping", "Local food tour",
            "Cooking classes", "Spa treatments", "Art galleries",
            "Local theaters or performances", "Indoor markets"
        ]
        
        # Good weather activities
        if precip_mm < 5 and "rain" not in condition and "storm" not in condition:
            outdoor_activities.extend([
                "Sightseeing tours", "Walking tours", "Outdoor dining",
                "Parks and gardens", "Photography walks"
            ])
            
            # Temperature-specific activities
            if avg_temp > 20:
                outdoor_activities.extend([
                    "Beach activities", "Outdoor swimming", 
                    "Boat tours", "Outdoor cafes"
                ])
            elif avg_temp > 10:
                outdoor_activities.extend([
                    "Hiking", "Biking tours", "Outdoor markets",
                    "Wildlife watching", "Picnics"
                ])
            else:
                outdoor_activities.extend([
                    "Winter sports", "Scenic drives", 
                    "Hot springs (if available)"
                ])
        
        return {
            "recommended": outdoor_activities if outdoor_activities else indoor_alternatives,
            "alternatives": indoor_alternatives if outdoor_activities else []
        }
    
    def format_weather_summary(self, forecast: Dict, duration: int) -> Dict:
        """
        Format weather forecast data into a user-friendly summary.
        
        Args:
            forecast: Weather forecast data
            duration: Trip duration in days
            
        Returns:
            Dictionary with formatted weather summary and recommendations
        """
        # Limit to requested duration or available forecast (max 10 days)
        actual_days = min(duration, len(forecast.get('forecast', {}).get('forecastday', [])))
        
        daily_forecasts = []
        
        for i in range(actual_days):
            forecast_day = forecast['forecast']['forecastday'][i]
            date = forecast_day['date']
            condition = forecast_day['day']['condition']['text']
            max_temp = forecast_day['day']['maxtemp_c']
            min_temp = forecast_day['day']['mintemp_c']
            
            clothing = self.get_clothing_recommendations(
                (max_temp + min_temp) / 2, 
                condition
            )
            
            activities = self.get_activity_recommendations(forecast_day)
            
            daily_forecasts.append({
                "date": date,
                "condition": condition,
                "max_temp_c": max_temp,
                "min_temp_c": min_temp,
                "clothing_recommendations": clothing,
                "activity_recommendations": activities["recommended"],
                "alternative_activities": activities["alternatives"]
            })
        
        # Overall trip weather summary
        conditions = [day['condition'] for day in daily_forecasts]
        max_temps = [day['max_temp_c'] for day in daily_forecasts]
        min_temps = [day['min_temp_c'] for day in daily_forecasts]
        
        overall_summary = {
            "location": f"{forecast['location']['name']}, {forecast['location']['country']}",
            "forecast_days": actual_days,
            "avg_max_temp_c": sum(max_temps) / len(max_temps),
            "avg_min_temp_c": sum(min_temps) / len(min_temps),
            "conditions_summary": self._summarize_conditions(conditions),
            "daily_forecasts": daily_forecasts
        }
        
        return overall_summary
    
    def _summarize_conditions(self, conditions: List[str]) -> str:
        """
        Create a summary of weather conditions across multiple days.
        
        Args:
            conditions: List of daily weather conditions
            
        Returns:
            String summarizing overall weather patterns
        """
        # Count occurrences of each condition
        condition_counts = {}
        for condition in conditions:
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
        
        # Sort by frequency
        sorted_conditions = sorted(
            condition_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Create summary based on frequency
        total_days = len(conditions)
        
        if len(sorted_conditions) == 1:
            return f"Consistently {sorted_conditions[0][0]} throughout your trip"
        
        main_condition, main_count = sorted_conditions[0]
        if main_count / total_days >= 0.5:
            other_conditions = ", ".join([cond for cond, _ in sorted_conditions[1:]])
            return f"Mostly {main_condition} with some {other_conditions}"
        else:
            condition_text = ", ".join([f"{cond}" for cond, _ in sorted_conditions[:3]])
            return f"Variable conditions including {condition_text}"