from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class Program(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    title: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProgramSelection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    program_id: str
    program_name: str
    selected_at: datetime = Field(default_factory=datetime.utcnow)
    user_session: Optional[str] = None

class ProgramSelectionCreate(BaseModel):
    program_id: str
    program_name: str
    user_session: Optional[str] = None

# Initialize programs data
async def initialize_programs():
    """Initialize the 15 programs in the database"""
    # Clear existing programs to reinitialize with new names
    await db.programs.delete_many({})
    
    program_names = [
        "CSV-to-blacklist",
        "csv-to-enduser", 
        "csv-to-functional",
        "csv-to-newenduser",
        "csv-to-newfunctional",
        "csv-to-silentuser",
        "csv-to-swapalias",
        "csv-to-antispoofing",
        "csv-to-globalalias",
        "csv-to-autoblockattachment",
        "csv-to-block-by-body-content",
        "csv-to-blocklist",
        "Archive tools",
        "autoblockHeader",
        "autorelay"
    ]
    
    programs_data = []
    for i, name in enumerate(program_names, 1):
        program = Program(
            name=name,
            title=f"Program {i}",
            description="This is a testing program and soon it will be a program to execute to complete a specific functionality. To be determined soon...."
        )
        programs_data.append(program.dict())
    
    await db.programs.insert_many(programs_data)
    logger.info(f"Initialized {len(programs_data)} programs in database with new names")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Program Selection API"}

@api_router.get("/programs", response_model=List[Program])
async def get_programs():
    """Get all available programs"""
    programs = await db.programs.find().sort("name", 1).to_list(1000)
    return [Program(**program) for program in programs]

@api_router.get("/programs/{program_id}", response_model=Program)
async def get_program(program_id: str):
    """Get a specific program by ID"""
    program = await db.programs.find_one({"id": program_id})
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return Program(**program)

@api_router.post("/select-program", response_model=ProgramSelection)
async def select_program(selection: ProgramSelectionCreate):
    """Record a program selection"""
    # Verify program exists
    program = await db.programs.find_one({"id": selection.program_id})
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    selection_obj = ProgramSelection(**selection.dict())
    await db.program_selections.insert_one(selection_obj.dict())
    return selection_obj

@api_router.get("/selections", response_model=List[ProgramSelection])
async def get_selections():
    """Get all program selections"""
    selections = await db.program_selections.find().sort("selected_at", -1).to_list(1000)
    return [ProgramSelection(**selection) for selection in selections]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    await initialize_programs()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
