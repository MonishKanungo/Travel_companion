import streamlit as st
from agents import generate_itinerary
import json
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="AI Travel Companion",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
}
.highlight {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 5px;
}
.weather-card {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    border-left: 5px solid #4e8df5;
}
.weather-day {
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 10px;
    margin-bottom: 10px;
}
.transport-card {
    background-color: #f0f8ff;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    border-left: 5px solid #4CAF50;
}
</style>
""", unsafe_allow_html=True)

# Weather icon mapping function
def get_weather_icon(condition):
    condition = condition.lower()
    if "sunny" in condition or "clear" in condition:
        return "☀️"
    elif "cloudy" in condition or "overcast" in condition:
        return "☁️"
    elif "rain" in condition or "drizzle" in condition or "shower" in condition:
        return "🌧️"
    elif "storm" in condition or "thunder" in condition:
        return "⛈️"
    elif "snow" in condition:
        return "❄️"
    elif "fog" in condition or "mist" in condition:
        return "🌫️"
    elif "wind" in condition:
        return "💨"
    else:
        return "🌤️"

# Transport icon mapping function
def get_transport_icon(transport_mode):
    transport_mode = transport_mode.lower()
    if "flight" in transport_mode or "plane" in transport_mode or "air" in transport_mode:
        return "✈️"
    elif "train" in transport_mode or "rail" in transport_mode:
        return "🚆"
    elif "bus" in transport_mode or "coach" in transport_mode:
        return "🚌"
    elif "car" in transport_mode or "taxi" in transport_mode or "uber" in transport_mode:
        return "🚗"
    elif "boat" in transport_mode or "ferry" in transport_mode or "cruise" in transport_mode:
        return "🚢"
    else:
        return "🚍"

# Main App
def main():
    st.title("🌍 AI Travel Companion")
    st.markdown("Generate personalized travel itineraries with AI-powered insights!")
    
    # Travel Request Form
    with st.form("travel_request"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            source = st.text_input("Starting Location", placeholder="Where are you traveling from?")
            destination = st.text_input("Destination", placeholder="Where are you traveling to?")
            budget = st.slider("Budget (Inr)", 3000, 15000, 50000, step=5000)
            
        with col2:
            duration = st.slider("Trip Duration (Days)", 1, 10, 5)
            # Add date selection for travel dates
            today = datetime.now().date()
            start_date = st.date_input(
                "Start Date",
                today + timedelta(days=30),
                min_value=today,
                max_value=today + timedelta(days=365)
            )
            accommodation = st.selectbox(
                "Accommodation Preference",
                ["Budget", "Mid-range", "Luxury", "Hostel", "Airbnb"]
            )
        
        with col3:
            interests = st.multiselect(
                "Travel Interests",
                [
                    "Adventure", "Culture", "History", "Beach", "Food", 
                    "Nature", "Shopping", "Relaxation"
                ]
            )
            dietary = st.text_input("Dietary Restrictions", placeholder="Optional")
            
            # Weather preference
            weather_pref = st.selectbox(
                "Weather Activity Preference",
                ["Balance indoor/outdoor activities", "Maximize outdoor activities", "Prefer indoor activities"]
            )
        
        submitted = st.form_submit_button("Generate Itinerary")
    
    # Itinerary Generation
    if submitted:
        if not destination or not interests:
            st.warning("Please provide destination and interests!")
        else:
            with st.spinner("Crafting your personalized travel experience..."):
                travel_request = {
                    "source": source,
                    "destination": destination,
                    "budget": budget,
                    "duration": duration,
                    "interests": interests,
                    "accommodation": accommodation,
                    "dietary": dietary or "No restrictions",
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "weather_preference": weather_pref
                }
                
                try:
                    result = generate_itinerary(travel_request)
                    
                    # Check for errors
                    if 'error' in result:
                        st.error(f"Error: {result['error']} - {result.get('details', '')}")
                        return
                    
                    # Display Results
                    st.success(f"🎉 Itinerary for {destination} Generated!")
                    
                    # Transportation Information (if source was provided)
                    if source and 'transport_options' in result and result['transport_options']:
                        st.subheader(f"🚆 Transportation from {source} to {destination}")
                        
                        for option in result['transport_options'][:3]:
                            icon = get_transport_icon(option.get('title', ''))
                            st.markdown(f"""
                            <div class="transport-card">
                                <h4>{icon} {option.get('title', 'Transportation Option')}</h4>
                                <p>{option.get('snippet', '')}</p>
                                <a href="{option.get('link', '#')}" target="_blank">More Information</a>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Weather Data Section
                    if 'weather_data' in result and 'error' not in result['weather_data']:
                        weather_data = result['weather_data']
                        
                        st.subheader("🌤️ Weather Forecast")
                        
                        # Weather Summary
                        st.markdown(f"""
                        <div class="highlight">
                            <h3>Weather Overview for {weather_data['location']}</h3>
                            <p><b>Conditions:</b> {weather_data['conditions_summary']}</p>
                            <p><b>Average Temperatures:</b> {weather_data['avg_min_temp_c']:.1f}°C to {weather_data['avg_max_temp_c']:.1f}°C</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Daily Weather Forecasts
                        st.markdown("### Daily Forecast")
                        cols = st.columns(min(3, len(weather_data['daily_forecasts'])))
                        
                        for i, day in enumerate(weather_data['daily_forecasts']):
                            col_idx = i % len(cols)
                            with cols[col_idx]:
                                icon = get_weather_icon(day['condition'])
                                
                                st.markdown(f"""
                                <div class="weather-card">
                                    <h4>{icon} {day['date']}</h4>
                                    <p><b>Condition:</b> {day['condition']}</p>
                                    <p><b>Temperature:</b> {day['min_temp_c']:.1f}°C to {day['max_temp_c']:.1f}°C</p>
                                    <p><b>What to Wear:</b></p>
                                    <ul>
                                        {"".join(f"<li>{item}</li>" for item in day['clothing_recommendations'][:3])}
                                    </ul>
                                    <p><b>Recommended Activities:</b></p>
                                    <ul>
                                        {"".join(f"<li>{item}</li>" for item in day['activity_recommendations'][:3])}
                                    </ul>
                                </div>
                                """, unsafe_allow_html=True)
                    elif 'weather_data' in result and 'error' in result['weather_data']:
                        st.warning(f"⚠️ Weather data not available: {result['weather_data']['error']}")
                    
                    # AI Generated Itinerary
                    st.subheader("🤖 AI Generated Itinerary")
                    st.markdown(result.get('ai_generated_itinerary', 'No itinerary generated'), unsafe_allow_html=True)
                    
                    # Web Search Context
                    with st.expander("🌐 Web Search Insights", expanded=False):
                        for result in result.get('web_search_context', []):
                            st.markdown(f"""
                            ### {result['title']}
                            **Link:** {result['link']}
                            
                            {result['snippet']}
                            """, unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error generating itinerary: {e}")

if __name__ == "__main__":
    main()