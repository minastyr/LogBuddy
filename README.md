# LogBuddy

A comprehensive logging and analytics service built with FastAPI, pandas, loguru, requests, and SQLAlchemy.

## Features

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **SQLAlchemy**: Database ORM for persistent log storage
- **Pandas**: Data analysis and manipulation for log analytics
- **Loguru**: Advanced logging with structured output and file rotation
- **Requests**: HTTP library for external API integrations

## Libraries Demonstrated

### 1. FastAPI
- RESTful API endpoints with automatic OpenAPI documentation
- Pydantic models for request/response validation
- Dependency injection for database sessions
- Background tasks for asynchronous processing
- Exception handling and HTTP status codes

### 2. SQLAlchemy
- Database models and ORM operations
- Session management and connection pooling
- Query building with filtering capabilities
- Database table creation and migration

### 3. Pandas
- Data analysis and aggregation of log entries
- DataFrame operations for analytics
- CSV export functionality
- Time-based data filtering and grouping

### 4. Loguru
- Structured logging with different levels (INFO, ERROR, SUCCESS)
- File rotation and retention policies
- Contextual logging with metadata
- Automatic log file management

### 5. Requests
- External API integration (weather service example)
- HTTP request handling with timeouts
- Error handling for network operations
- Mock data fallback for demonstration

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python main.py
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Core Logging
- `POST /logs` - Create a new log entry
- `GET /logs` - Retrieve log entries with filtering options
- `GET /analytics` - Get log analytics using pandas

### External APIs
- `GET /external-api/weather?city={city}` - Fetch weather data
- `POST /external-api/webhook` - Handle webhook data

### Utilities
- `GET /export/csv` - Export logs to CSV using pandas
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint

## Example Usage

### Creating a log entry:
```bash
curl -X POST "http://localhost:8000/logs" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "INFO",
    "message": "User logged in successfully",
    "source": "authentication",
    "user_id": "user123",
    "metadata": {"ip": "192.168.1.1", "browser": "Chrome"}
  }'
```

### Getting analytics:
```bash
curl "http://localhost:8000/analytics"
```

### Fetching weather data:
```bash
curl "http://localhost:8000/external-api/weather?city=Paris"
```

## Project Structure

```
LogBuddy/
├── main.py              # Main application file with all implementations
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
├── logs/               # Log files (created automatically)
│   ├── app.log
│   └── error.log
└── logbuddy.db         # SQLite database (created automatically)
```

## Key Features Demonstrated

1. **Database Operations**: CRUD operations with SQLAlchemy ORM
2. **Data Analysis**: Using pandas for log analytics and CSV export
3. **Structured Logging**: Loguru for comprehensive application logging
4. **API Integration**: External service calls using requests
5. **Web Framework**: FastAPI for modern API development
6. **Background Processing**: Asynchronous webhook processing
7. **Data Validation**: Pydantic models for type safety
8. **Error Handling**: Comprehensive exception management

This project serves as a comprehensive example of how to integrate these popular Python libraries into a single, cohesive application.