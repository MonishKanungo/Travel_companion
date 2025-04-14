import os
import json
import requests
from typing import Dict, List, Any
import google.generativeai as genai
from dotenv import load_dotenv
from weather_service import WeatherService

class WebSearchAgent:
    def __init__(self):
        # Load API keys from environment
        load_dotenv()
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        self.genai_key = os.getenv('GENAI_API_KEY')
        
        # Configure Gemini AI
        genai.configure(api_key=self.genai_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Initialize weather service
        self.weather_service = WeatherService()
    
    def validate_location(self, location: str) -> bool:
        """
        Validate the location using the weather service.
        
        Args:
            location: Location to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            validation_result = self.weather_service.validate_location(location)
            return validation_result.get("valid", False)
        except Exception:
            return False

    def perform_web_search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Perform web search using SerpAPI with comprehensive error handling.
        """
        if not self.serpapi_key:
            raise ValueError("SerpAPI key is required for web search")
        
        params = {
            'engine': 'google',
            'q': query,
            'api_key': self.serpapi_key,
            'num': num_results
        }
        
        try:
            response = requests.get('https://serpapi.com/search', params=params)
            response.raise_for_status()
            results = response.json().get('organic_results', [])
            
            # Extract key information from search results
            processed_results = [
                {
                    'title': result.get('title', ''),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', ''),
                    'source': result.get('source', '')
                }
                for result in results
            ]
            
            return processed_results
        except requests.RequestException as e:
            print(f"Web search error: {e}")
            return []
    
    def get_weather_data(self, destination: str, duration: int) -> Dict:
        """
        Get weather forecast for the destination.
        
        Args:
            destination: Travel destination
            duration: Trip duration in days
            
        Returns:
            Formatted weather summary
        """
        try:
            # Fetch raw weather data
            forecast = self.weather_service.get_weather_forecast(destination, duration)
            
            # Check for errors
            if "error" in forecast:
                return {"error": forecast.get("error", "Failed to fetch weather data")}
            
            # Format weather data into a user-friendly summary
            return self.weather_service.format_weather_summary(forecast, duration)
        except Exception as e:
            return {"error": f"Weather data retrieval failed: {str(e)}"}
    
    def get_transport_options(self, source: str, destination: str) -> List[Dict]:
        """
        Get transportation options between source and destination.
        
        Args:
            source: Starting location
            destination: Travel destination
            
        Returns:
            List of transportation options
        """
        try:
            # Search for transportation options
            search_query = f"How to travel from {source} to {destination} transportation options"
            transport_results = self.perform_web_search(search_query, num_results=3)
            
            return transport_results
        except Exception as e:
            print(f"Transport search error: {e}")
            return []
    
    def generate_comprehensive_itinerary(self, travel_request: Dict) -> Dict:
        """
        Generate a comprehensive travel itinerary using web search, weather data, and AI insights.
        """
        # Validate locations first
        source = travel_request.get('source', '')
        destination = travel_request['destination']
        
        # Validate destination
        if not self.validate_location(destination):
            return {
                'error': 'Invalid destination',
                'details': f"'{destination}' does not appear to be a valid location"
            }
        
        # Validate source if provided
        if source and not self.validate_location(source):
            return {
                'error': 'Invalid source location',
                'details': f"'{source}' does not appear to be a valid location"
            }
        
        # Perform web search for destination insights
        search_query = f"Best travel guide for {travel_request['destination']} {' '.join(travel_request['interests'])}"
        web_results = self.perform_web_search(search_query)
        
        # Get transportation options if source is provided
        transport_options = []
        if source:
            transport_options = self.get_transport_options(source, destination)
        
        # Get weather forecast for the destination
        weather_data = self.get_weather_data(
            travel_request['destination'], 
            travel_request['duration']
        )
        
        # Prepare AI prompt for itinerary generation with weather information
        source_info = f"Starting from {source}" if source else "No specific starting location provided"
        
        itinerary_prompt = f"""
        Create a comprehensive {travel_request['duration']}-day travel plan for {travel_request['destination']}

        Travel Context:
        - Source Location: {source_info}
        - Budget: ₹{travel_request['budget']}
        - Duration: {travel_request['duration']} days
        - Interests: {', '.join(travel_request['interests'])}
        - Accommodation: {travel_request['accommodation']}
        - Dietary Needs: {travel_request['dietary']}

        Weather Forecast:
        {json.dumps(weather_data, indent=2)}

        Web Search Insights:
        {json.dumps(web_results, indent=2)}
        
        {f"Transportation Options from {source} to {destination}:" if source else ""}
        {json.dumps(transport_options, indent=2) if source else ""}

        Itinerary Requirements:
        1. Personalized day-by-day breakdown that accounts for the weather forecast
        2. Activities matching specific interests, prioritizing outdoor activities on good weather days 
        3. Budget-conscious recommendations
        4. Detailed accommodation suggestions
        5. Dining options considering dietary needs
        6. Transportation logistics{f" including journey from {source} to {destination}" if source else ""}
        7. Cultural insights and local experiences
        8. Clothing recommendations based on weather
        9. Alternative indoor activities for days with poor weather

        Provide a structured response with:
        - Overall trip overview including weather summary
        {f"- Transportation details from {source} to {destination}" if source else ""}
        - Detailed day-by-day itinerary with weather-appropriate activities
        - Packing list based on weather conditions
        - Budget breakdown in INR (₹)
        - Travel tips and local recommendations
        """
        
        try:
            # Generate AI-powered itinerary
            response = self.model.generate_content(itinerary_prompt)
            
            # Parse and structure the response
            return {
                'ai_generated_itinerary': response.text,
                'web_search_context': web_results,
                'weather_data': weather_data,
                'transport_options': transport_options if source else []
            }
        
        except Exception as e:
            return {
                'error': 'Itinerary generation failed',
                'details': str(e)
            }

def generate_itinerary(travel_request: Dict) -> Dict:
    """
    Main function to generate travel itinerary using WebSearchAgent.
    """
    agent = WebSearchAgent()
    return agent.generate_comprehensive_itinerary(travel_request)