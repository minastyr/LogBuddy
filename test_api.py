"""
TesBASE_URL = "http://localhost:8002" script to demonstrate LogBuddy functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_logbuddy():
    print("🚀 Testing LogBuddy Application")
    print("="*50)
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Server not running. Start with: python main.py")
        return
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Response: {response.json()}")
    
    # Create some test log entries
    print("\n3. Creating test log entries...")
    test_logs = [
        {
            "level": "INFO",
            "message": "Application started successfully",
            "source": "app-startup",
            "user_id": "system",
            "extra_data": {"version": "1.0.0", "environment": "test"}
        },
        {
            "level": "WARNING",
            "message": "High memory usage detected",
            "source": "monitoring",
            "user_id": "admin",
            "extra_data": {"memory_usage": "85%", "threshold": "80%"}
        },
        {
            "level": "ERROR",
            "message": "Database connection failed",
            "source": "database",
            "user_id": "db-service",
            "extra_data": {"error_code": "CONN_001", "retry_count": 3}
        }
    ]
    
    created_logs = []
    for log_data in test_logs:
        response = requests.post(f"{BASE_URL}/logs", json=log_data)
        if response.status_code == 200:
            created_log = response.json()
            created_logs.append(created_log)
            print(f"   ✅ Created log: {created_log['level']} - {created_log['message'][:30]}...")
        else:
            print(f"   ❌ Failed to create log: {response.status_code}")
    
    # Test retrieving logs
    print("\n4. Retrieving logs...")
    response = requests.get(f"{BASE_URL}/logs")
    logs = response.json()
    print(f"   Retrieved {len(logs)} logs")
    
    # Test filtering by level
    print("\n5. Testing log filtering...")
    response = requests.get(f"{BASE_URL}/logs?level=ERROR")
    error_logs = response.json()
    print(f"   Found {len(error_logs)} ERROR logs")
    
    # Test analytics
    print("\n6. Testing analytics...")
    response = requests.get(f"{BASE_URL}/analytics")
    analytics = response.json()
    print(f"   Total logs: {analytics['total_logs']}")
    print(f"   Logs by level: {analytics['logs_by_level']}")
    print(f"   Logs by source: {analytics['logs_by_source']}")
    
    # Test external API (weather)
    print("\n7. Testing external weather API...")
    response = requests.get(f"{BASE_URL}/external-api/weather?city=London")
    if response.status_code == 200:
        try:
            weather_data = response.json()
            if weather_data['success']:
                print(f"   ✅ Weather data retrieved for London")
                print(f"   Data: {weather_data['data']}")
            else:
                print(f"   ❌ Weather API failed: {weather_data['error']}")
        except requests.exceptions.JSONDecodeError:
            print(f"   ❌ Invalid JSON response from weather API")
    else:
        print(f"   ❌ Weather API returned status {response.status_code}")
    
    # Test webhook
    print("\n8. Testing webhook...")
    webhook_data = {
        "type": "user_action",
        "action": "login",
        "user_id": "test_user_123",
        "timestamp": time.time()
    }
    response = requests.post(f"{BASE_URL}/external-api/webhook", json=webhook_data)
    print(f"   Webhook response: {response.json()}")
    
    # Test CSV export
    print("\n9. Testing CSV export...")
    response = requests.get(f"{BASE_URL}/export/csv")
    export_result = response.json()
    print(f"   Export result: {export_result}")
    
    print("\n🎉 All tests completed!")
    print("Visit http://localhost:8002/docs for interactive API documentation")

if __name__ == "__main__":
    test_logbuddy()
