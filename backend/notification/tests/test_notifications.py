#!/usr/bin/env python3
"""
Notification System Test Script

This script helps test the notification system to debug issues with email notifications.
Run this script to test specific scenarios with users 160 and 676.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoints
NOTIFICATION_API = "http://127.0.0.1:5006"
USER_API = "http://127.0.0.1:5003"
TASK_API = "http://localhost:5002"

def test_user_details(user_id):
    """Test getting user details and preferences."""
    print(f"\n=== Testing User {user_id} Details ===")
    try:
        response = requests.get(f"{USER_API}/users/{user_id}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"User {user_id} data: {json.dumps(user_data, indent=2)}")
            
            # Check notification preferences
            preferences = user_data.get("data", {}).get("notification_preferences", {})
            email = user_data.get("data", {}).get("email")
            
            print(f"Notification preferences: {preferences}")
            print(f"Email address: {email}")
            
            return user_data
        else:
            print(f"Failed to get user {user_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting user {user_id}: {e}")
        return None

def test_sendgrid_config():
    """Test SendGrid configuration."""
    print(f"\n=== Testing SendGrid Configuration ===")
    
    api_key = os.environ.get("SENDGRID_API_KEY")
    from_email = os.environ.get("SENDGRID_FROM_EMAIL")
    
    print(f"SENDGRID_API_KEY: {'Set' if api_key else 'Not set'}")
    print(f"SENDGRID_FROM_EMAIL: {from_email if from_email else 'Not set'}")
    
    if not api_key:
        print("ERROR: SENDGRID_API_KEY not configured!")
        return False
    
    if not from_email:
        print("ERROR: SENDGRID_FROM_EMAIL not configured!")
        return False
    
    return True

def test_notification_endpoint():
    """Test the notification trigger endpoint directly."""
    print(f"\n=== Testing Notification Trigger Endpoint ===")
    
    # Test data for user 160
    test_data = {
        "task_id": 1,
        "user_ids": [160],
        "old_status": "Ongoing",
        "new_status": "Under Review",
        "updater_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{NOTIFICATION_API}/notifications/triggers/task-status-change",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Notification results: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error testing notification endpoint: {e}")

def test_email_notification_direct():
    """Test sending email notification directly."""
    print(f"\n=== Testing Direct Email Notification ===")
    
    # Get user 160's email
    user_data = test_user_details(160)
    if not user_data:
        return
    
    user_email = user_data.get("data", {}).get("email")
    if not user_email:
        print("ERROR: User 160 has no email address!")
        return
    
    # Test direct email sending
    test_data = {
        "user_email": user_email,
        "subject": "Test Notification - SPM",
        "message": "<p>This is a test email notification.</p>"
    }
    
    try:
        response = requests.post(
            f"{NOTIFICATION_API}/notifications/test-email",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Direct email test response: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error testing direct email: {e}")

def main():
    """Run all tests."""
    print("=== SPM Notification System Test ===")
    
    # Test SendGrid configuration
    if not test_sendgrid_config():
        print("\nERROR: SendGrid not properly configured. Please check your .env file.")
        return
    
    # Test user details
    test_user_details(160)
    test_user_details(676)
    
    # Test notification endpoint
    test_notification_endpoint()
    
    # Test direct email (if endpoint exists)
    test_email_notification_direct()
    
    print(f"\n=== Test Complete ===")
    print("Check the notification service logs for DEBUG messages.")
    print("If email notifications are still not working, check:")
    print("1. SendGrid account status and quota")
    print("2. Sender email verification")
    print("3. API key permissions")

if __name__ == "__main__":
    main()
