import os
import json
import requests
from typing import Dict, List, Any
import google.generativeai as genai
from dotenv import load_dotenv

class WebSearchAgent:
    def __init__(self):
        # Load API keys from environment
        load_dotenv()
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        self.genai_key = os.getenv('GENAI_API_KEY')
        
        # Configure Gemini AI
        genai.configure(api_key=self.genai_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

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

    def generate_comprehensive_itinerary(self, travel_request: Dict) -> Dict:
        """
        Generate a comprehensive travel itinerary using web search and AI insights.
        """
        # Perform web search for destination insights
        search_query = f"Best travel guide for {travel_request['destination']} {' '.join(travel_request['interests'])}"
        web_results = self.perform_web_search(search_query)
        
        # Prepare AI prompt for itinerary generation
        itinerary_prompt = f"""
        Create a comprehensive {travel_request['duration']}-day travel plan for {travel_request['destination']}

        Travel Context:
        - Budget: ${travel_request['budget']}
        - Duration: {travel_request['duration']} days
        - Interests: {', '.join(travel_request['interests'])}
        - Accommodation: {travel_request['accommodation']}
        - Dietary Needs: {travel_request['dietary']}

        Web Search Insights:
        {json.dumps(web_results, indent=2)}

        Itinerary Requirements:
        1. Personalized day-by-day breakdown
        2. Activities matching specific interests
        3. Budget-conscious recommendations
        4. Detailed accommodation suggestions
        5. Dining options considering dietary needs
        6. Transportation logistics
        7. Cultural insights and local experiences

        Provide a structured response with:
        - Overall trip overview
        - Detailed day-by-day itinerary
        - Budget breakdown
        - Travel tips and local recommendations
        """
        
        try:
            # Generate AI-powered itinerary
            response = self.model.generate_content(itinerary_prompt)
            
            # Parse and structure the response
            return {
                'ai_generated_itinerary': response.text,
                'web_search_context': web_results
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