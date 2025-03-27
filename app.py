import streamlit as st
from agents import generate_itinerary
import json

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
</style>
""", unsafe_allow_html=True)

# Main App
def main():
    st.title("🌍 AI Travel Companion")
    st.markdown("Generate personalized travel itineraries with AI-powered insights!")

    # Travel Request Form
    with st.form("travel_request"):
        col1, col2 = st.columns(2)
        
        with col1:
            destination = st.text_input("Destination", placeholder="Where are you traveling?")
            budget = st.slider("Budget (USD)", 100, 20000, 1000, step=100)
            duration = st.slider("Trip Duration (Days)", 1, 30, 5)
        
        with col2:
            interests = st.multiselect(
                "Travel Interests", 
                [
                    "Adventure", "Culture", "History", "Beach", 
                    "Food", "Nature", "Shopping", "Relaxation"
                ]
            )
            accommodation = st.selectbox(
                "Accommodation Preference", 
                ["Budget", "Mid-range", "Luxury", "Hostel", "Airbnb"]
            )
            dietary = st.text_input("Dietary Restrictions", placeholder="Optional")

        submitted = st.form_submit_button("Generate Itinerary")

    # Itinerary Generation
    if submitted:
        if not destination or not interests:
            st.warning("Please provide destination and interests!")
        else:
            with st.spinner("Crafting your personalized travel experience..."):
                travel_request = {
                    "destination": destination,
                    "budget": budget,
                    "duration": duration,
                    "interests": interests,
                    "accommodation": accommodation,
                    "dietary": dietary or "No restrictions"
                }

                try:
                    result = generate_itinerary(travel_request)
                    
                    # Display Results
                    st.success(f"🎉 Itinerary for {destination} Generated!")
                    
                    # AI Generated Itinerary
                    st.subheader("🤖 AI Generated Itinerary")
                    st.markdown(result.get('ai_generated_itinerary', 'No itinerary generated'), 
                                unsafe_allow_html=True)
                    
                    # Web Search Context
                    st.subheader("🌐 Web Search Insights")
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