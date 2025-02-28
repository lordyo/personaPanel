"""
Backend server for the Persona Panel application.
Provides API endpoints for persona generation using DSPy and Claude.
"""
import os
import json
import traceback
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import dspy
from pydantic import BaseModel

# Import the persona framework components
from persona_framework.modules.dimension import DimensionRegistry, Dimension
from persona_framework.modules.generator import PersonaGeneratorWithValidation
from persona_framework.modules.persona import Persona, PersonaLibrary

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Persona Panel API", description="API for generating personas using DSPy and Claude")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DSPy with Claude
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")

lm = dspy.LM('anthropic/claude-3-sonnet-20240229', api_key=api_key)
dspy.configure(lm=lm)

# Initialize dimension registry and persona library
dimension_registry = DimensionRegistry()
persona_library = PersonaLibrary()

# Define request/response models
class GenerationSettings(BaseModel):
    dimensions: List[Dict[str, Any]]
    num_personas: int
    diversity_level: str = "medium"
    selected_dimensions: Optional[List[str]] = None

class PersonaResponse(BaseModel):
    id: str
    name: str
    traits: List[Dict[str, Any]]
    backstory: str

class SavePersonaRequest(BaseModel):
    persona: Dict[str, Any]

class DimensionResponse(BaseModel):
    name: str
    description: str
    type: str
    importance: str
    constraints: Optional[Dict[str, Any]] = None

class StatsResponse(BaseModel):
    persona_count: int
    dimension_count: int

@app.on_event("startup")
async def startup_event():
    """Initialize the dimension registry on startup."""
    print("Initializing dimension registry...")
    # This would typically load from a config file or database
    # For now, we'll use hardcoded dimensions for testing

@app.get("/")
async def root():
    """Root endpoint to check if the server is running."""
    return {"message": "Persona Panel API is running"}

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get statistics about personas and dimensions."""
    try:
        return {
            "persona_count": len(persona_library.list_personas()),
            "dimension_count": len(dimension_registry.list_dimensions())
        }
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/api/dimensions", response_model=List[DimensionResponse])
async def get_dimensions():
    """Get all registered dimensions."""
    try:
        dimensions = []
        for dim_name in dimension_registry.list_dimensions():
            dim = dimension_registry.get(dim_name)
            if dim:
                dimensions.append(dim.to_dict())
        return dimensions
    except Exception as e:
        print(f"Error getting dimensions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting dimensions: {str(e)}")

@app.post("/api/personas/generate", response_model=List[PersonaResponse])
async def generate_personas(settings: GenerationSettings = Body(...)):
    """
    Generate personas using DSPy and Claude based on the provided settings.
    """
    try:
        print(f"Generating {settings.num_personas} personas with diversity level: {settings.diversity_level}")
        print(f"Number of dimensions provided: {len(settings.dimensions)}")
        
        # Clear existing dimensions and register new ones from the request
        dimension_registry.clear()
        for dim_data in settings.dimensions:
            try:
                dim = Dimension.from_dict(dim_data)
                dimension_registry.register(dim)
                print(f"Registered dimension: {dim.name}")
            except Exception as e:
                print(f"Error registering dimension {dim_data.get('name', 'unknown')}: {str(e)}")
        
        # Filter dimensions if selected_dimensions is provided
        if settings.selected_dimensions:
            print(f"Filtering dimensions to: {settings.selected_dimensions}")
            filtered_dimensions = [
                dim for dim in dimension_registry.list_dimensions() 
                if dim in settings.selected_dimensions
            ]
            # Create a temporary registry with only the selected dimensions
            temp_registry = DimensionRegistry()
            for dim_name in filtered_dimensions:
                dim = dimension_registry.get(dim_name)
                if dim:
                    temp_registry.register(dim)
                    print(f"Using dimension: {dim_name}")
            
            generator = PersonaGeneratorWithValidation(temp_registry)
        else:
            generator = PersonaGeneratorWithValidation(dimension_registry)
        
        # Log the number of registered dimensions
        print(f"Number of dimensions for generation: {len(dimension_registry.list_dimensions())}")
        
        # Generate personas
        personas = generator.generate(
            num_personas=settings.num_personas,
            diversity_level=settings.diversity_level
        )
        
        print(f"Generated {len(personas)} personas")
        
        # Convert to response format
        response_personas = []
        for i, persona in enumerate(personas):
            persona_dict = persona.to_dict()
            
            # Validate required fields instead of using fallbacks
            if not persona_dict.get("id"):
                raise ValueError(f"Generated persona missing ID field")
                
            if not persona_dict.get("name"):
                raise ValueError(f"Generated persona missing name field")
                
            if not persona_dict.get("backstory"):
                raise ValueError(f"Generated persona '{persona_dict.get('name', 'unknown')}' missing backstory field")
            
            response_personas.append(persona_dict)
        
        return response_personas
    
    except Exception as e:
        traceback.print_exc()
        print(f"Error generating personas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating personas: {str(e)}")

@app.post("/api/personas/save", response_model=PersonaResponse)
async def save_persona(request: SavePersonaRequest = Body(...)):
    """
    Save a persona to the library.
    """
    try:
        persona_data = request.persona
        
        # Check required fields instead of using fallbacks
        if not persona_data.get("name"):
            raise HTTPException(status_code=400, detail="Persona must have a name")
        
        if not persona_data.get("backstory"):
            raise HTTPException(status_code=400, detail=f"Persona '{persona_data['name']}' must have a backstory")
            
        # Create persona object
        persona = Persona.from_dict(persona_data)
        
        # Add to library
        persona_library.add(persona)
        
        print(f"Saved persona: {persona.name} (ID: {persona.id})")
        
        return persona.to_dict()
    
    except Exception as e:
        print(f"Error saving persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving persona: {str(e)}")

@app.get("/api/personas", response_model=List[PersonaResponse])
async def get_personas():
    """
    Get all personas from the library.
    """
    try:
        personas = persona_library.list_personas()
        return [p.to_dict() for p in personas]
    
    except Exception as e:
        print(f"Error getting personas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting personas: {str(e)}")

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port) 