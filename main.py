"""
LogBuddy - A comprehensive logging and analytics service
Using FastAPI, pandas, loguru, requests, and SQLAlchemy
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import pandas as pd
import requests
from loguru import logger
import json
import os

# Configure Loguru logger
logger.add("logs/app.log", rotation="1 MB", retention="10 days", level="INFO")
logger.add("logs/error.log", rotation="1 MB", retention="10 days", level="ERROR")

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./logbuddy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String(20))
    message = Column(Text)
    source = Column(String(100))
    user_id = Column(String(50), nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON string

class APICall(Base):
    __tablename__ = "api_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    endpoint = Column(String(200))
    method = Column(String(10))
    status_code = Column(Integer)
    response_time = Column(Float)
    user_agent = Column(String(200), nullable=True)

# Pydantic models
class LogEntryCreate(BaseModel):
    level: str
    message: str
    source: str
    user_id: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class LogEntryResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str
    message: str
    source: str
    user_id: Optional[str]
    extra_data: Optional[str]

class AnalyticsResponse(BaseModel):
    total_logs: int
    logs_by_level: Dict[str, int]
    logs_by_source: Dict[str, int]
    recent_activity: List[Dict[str, Any]]

class ExternalAPIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="LogBuddy",
    description="A comprehensive logging and analytics service",
    version="1.0.0"
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("LogBuddy application starting up...")
    os.makedirs("logs", exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("LogBuddy application shutting down...")

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to LogBuddy - Your logging companion!"}

@app.post("/logs", response_model=LogEntryResponse)
async def create_log_entry(log_entry: LogEntryCreate, db: Session = Depends(get_db)):
    """Create a new log entry"""
    try:
        # Log the incoming request
        logger.info(f"Creating log entry: {log_entry.level} - {log_entry.message}")
        
        # Create database entry
        db_log = LogEntry(
            level=log_entry.level,
            message=log_entry.message,
            source=log_entry.source,
            user_id=log_entry.user_id,
            extra_data=json.dumps(log_entry.extra_data) if log_entry.extra_data else None
        )
        
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        
        logger.success(f"Log entry created with ID: {db_log.id}")
        return db_log
        
    except Exception as e:
        logger.error(f"Error creating log entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create log entry")

@app.get("/logs", response_model=List[LogEntryResponse])
async def get_logs(
    skip: int = 0,
    limit: int = 100,
    level: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve log entries with optional filtering"""
    try:
        query = db.query(LogEntry)
        
        if level:
            query = query.filter(LogEntry.level == level)
        if source:
            query = query.filter(LogEntry.source == source)
            
        logs = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(logs)} log entries")
        return logs
        
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")

@app.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(db: Session = Depends(get_db)):
    """Get analytics using pandas for data analysis"""
    try:
        logger.info("Generating analytics report...")
        
        # Fetch all logs into a pandas DataFrame
        logs = db.query(LogEntry).all()
        
        if not logs:
            return AnalyticsResponse(
                total_logs=0,
                logs_by_level={},
                logs_by_source={},
                recent_activity=[]
            )
        
        # Convert to pandas DataFrame for analysis
        df = pd.DataFrame([{
            'id': log.id,
            'timestamp': log.timestamp,
            'level': log.level,
            'source': log.source,
            'message': log.message
        } for log in logs])
        
        # Analyze data using pandas
        total_logs = len(df)
        logs_by_level = df['level'].value_counts().to_dict()
        logs_by_source = df['source'].value_counts().to_dict()
        
        # Get recent activity (last 24 hours)
        recent_df = df[df['timestamp'] >= datetime.utcnow() - timedelta(hours=24)]
        recent_activity = recent_df.tail(10).to_dict('records')
        
        # Convert timestamps to strings for JSON serialization
        for activity in recent_activity:
            activity['timestamp'] = activity['timestamp'].isoformat()
        
        logger.success("Analytics report generated successfully")
        
        return AnalyticsResponse(
            total_logs=total_logs,
            logs_by_level=logs_by_level,
            logs_by_source=logs_by_source,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate analytics")

@app.get("/external-api/weather")
async def get_weather_data(city: str = "London") -> ExternalAPIResponse:
    """Fetch weather data from external API using requests"""
    try:
        logger.info(f"Fetching weather data for {city}")
        
        # Using OpenWeatherMap API (free tier)
        # Note: In production, you would use an actual API key
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": "demo_key",  # Replace with actual API key
            "units": "metric"
        }
        
        # Make request using requests library
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.success(f"Weather data retrieved for {city}")
                return ExternalAPIResponse(success=True, data=data)
            except ValueError:
                # JSON parsing failed, fall back to mock data
                pass
        
        # For demo purposes, return mock data when API key is invalid or response fails
        mock_data = {
            "city": city,
            "temperature": 20.5,
            "description": "Partly cloudy",
            "humidity": 65,
            "note": "This is mock data - replace with actual API key for real data"
        }
        logger.warning(f"Using mock weather data for {city} (API response: {response.status_code})")
        return ExternalAPIResponse(success=True, data=mock_data)
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching weather data for {city}")
        return ExternalAPIResponse(success=False, error="Request timeout")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return ExternalAPIResponse(success=False, error="Request failed")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return ExternalAPIResponse(success=False, error="Internal server error")

@app.post("/external-api/webhook")
async def handle_webhook(data: Dict[str, Any], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Handle incoming webhook data"""
    try:
        logger.info("Received webhook data")
        
        # Process webhook in background
        background_tasks.add_task(process_webhook_data, data, db)
        
        return {"status": "accepted", "message": "Webhook data will be processed"}
        
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")

async def process_webhook_data(data: Dict[str, Any], db: Session):
    """Background task to process webhook data"""
    try:
        logger.info("Processing webhook data in background...")
        
        # Create log entry for webhook
        log_entry = LogEntry(
            level="INFO",
            message=f"Webhook processed: {data.get('type', 'unknown')}",
            source="webhook",
            extra_data=json.dumps(data)
        )
        
        db.add(log_entry)
        db.commit()
        
        logger.success("Webhook data processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing webhook data: {str(e)}")

@app.get("/export/csv")
async def export_logs_csv(db: Session = Depends(get_db)):
    """Export logs to CSV using pandas"""
    try:
        logger.info("Exporting logs to CSV...")
        
        # Fetch logs
        logs = db.query(LogEntry).all()
        
        # Convert to pandas DataFrame
        df = pd.DataFrame([{
            'id': log.id,
            'timestamp': log.timestamp,
            'level': log.level,
            'message': log.message,
            'source': log.source,
            'user_id': log.user_id
        } for log in logs])
        
        # Export to CSV
        csv_filename = f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_filename, index=False)
        
        logger.success(f"Logs exported to {csv_filename}")
        
        return {
            "message": "Export completed",
            "filename": csv_filename,
            "records_exported": len(df)
        }
        
    except Exception as e:
        logger.error(f"Error exporting logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export logs")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting LogBuddy server...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")