from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Optional, Union, Any
from agents import generate_itinerary, WebSearchAgent

# Initialize FastAPI app with enhanced configuration
app = FastAPI(
    title="AI Travel Companion API",
    description="Advanced AI-powered travel itinerary generation platform",
    version="1.1.0",
    docs_url="/documentation",
    redoc_url="/redoc"
)

# Add comprehensive CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Enhanced Request Models
class TravelRequestModel(BaseModel):
    destination: str = Field(..., min_length=2, max_length=100, description="Travel destination")
    budget: int = Field(default=1000, ge=100, le=50000, description="Total trip budget in USD")
    duration: int = Field(default=5, ge=1, le=45, description="Trip duration in days")
    interests: List[str] = Field(
        default_factory=list, 
        description="List of traveler's interests",
        min_items=1,
        max_items=10
    )
    accommodation: str = Field(
        default="Budget", 
        pattern="^(Budget|Mid-range|Luxury|Hostel|Airbnb)$", 
        description="Preferred accommodation type"
    )
    dietary: Optional[str] = Field(
        default=None, 
        max_length=200, 
        description="Dietary restrictions or preferences"
    )

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: Optional[Dict[str, Any]] = None

# Global error handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation Error",
            "details": exc.errors()
        }
    )

# Comprehensive Itinerary Generation Endpoint
@app.post(
    "/generate_itinerary", 
    response_model=Dict[str, Any], 
    responses={
        200: {"description": "Successful Itinerary Generation"},
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def create_itinerary(request: TravelRequestModel):
    try:
        # Convert Pydantic model to dictionary
        travel_request = request.dict()
        
        # Add some input preprocessing
        travel_request['interests'] = [
            interest.strip().capitalize() 
            for interest in travel_request['interests']
        ]
        
        # Generate comprehensive itinerary
        itinerary = generate_itinerary(travel_request)
        
        # Enhanced response structure
        return {
            "status": "success",
            "destination": travel_request['destination'],
            "itinerary": {
                "ai_generated": itinerary.get('ai_generated_itinerary', 'No detailed itinerary available'),
                "web_context": itinerary.get('web_search_context', [])
            },
            "metadata": {
                "budget": travel_request['budget'],
                "duration": travel_request['duration'],
                "interests": travel_request['interests']
            }
        }
    
    except Exception as e:
        # Structured error response
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": "Itinerary generation failed",
                "details": str(e)
            }
        )

# Destination Search Endpoint
@app.post("/destination_insights")
async def destination_insights(destination: str, interests: Optional[List[str]] = None):
    try:
        search_agent = WebSearchAgent()
        
        # Perform web search
        search_query = f"Best travel guide for {destination} " + \
                       (f"with {' '.join(interests)}" if interests else "")
        
        search_results = search_agent.perform_web_search(search_query)
        
        return {
            "status": "success",
            "destination": destination,
            "insights": search_results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": "Destination insights retrieval failed",
                "details": str(e)
            }
        )

# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Travel Companion",
        "version": "1.1.0"
    }

# Optional: Comprehensive Travel Query Endpoint
@app.post("/travel_query")
async def process_travel_query(query: str):
    """
    Process advanced travel-related queries.
    Future expansion point for more sophisticated query handling.
    """
    try:
        search_agent = WebSearchAgent()
        
        # Use Gemini to process the query
        response = search_agent.model.generate_content(
            f"Provide a comprehensive response to the travel query: {query}"
        )
        
        return {
            "status": "success",
            "query": query,
            "response": response.text
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": "Query processing failed",
                "details": str(e)
            }
        )
