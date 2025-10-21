#!/usr/bin/env python3
"""
Email Notification Test Script for User 160

This script retrieves user 160's email from Supabase and tests the email notification system.
"""

import requests
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv('/Users/yixli/Documents/GitHub/SPM/backend/.env')

# API endpoints
NOTIFICATION_API = "http://127.0.0.1:5006"
USER_API = "http://127.0.0.1:5003"

def get_supabase_client():
    """Create Supabase client."""
    try:
        SUPABASE_URL = os.environ["SUPABASE_URL"]
        SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        return None

def get_user_160_email():
    """Get user 160's email from Supabase."""
    print("=== Retrieving User 160's Email from Supabase ===")
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Query the user table for userid 160
        res = client.table("user").select("*").eq("userid", 160).single().execute()
        
        if res.data:
            user_data = res.data
            email = user_data.get("email")
            name = user_data.get("name", "Unknown")
            
            print(f"✅ Found user 160:")
            print(f"   Name: {name}")
            print(f"   Email: {email}")
            print(f"   User ID: {user_data.get('userid')}")
            
            # Check notification preferences
            notification_preferences = user_data.get("notification_preferences", {})
            print(f"   Notification Preferences: {notification_preferences}")
            
            return email
        else:
            print("❌ User 160 not found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error retrieving user 160: {e}")
        return None

def test_sendgrid_config():
    """Test SendGrid configuration."""
    print("\n=== Testing SendGrid Configuration ===")
    
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

def test_direct_email(user_email):
    """Test sending email directly to user 160."""
    print(f"\n=== Testing Direct Email to User 160 ({user_email}) ===")
    
    test_data = {
        "user_email": user_email,
        "subject": "SPM Test Notification - User 160",
        "message": """
        <h2>Test Email Notification for User 160</h2>
        <p>Hello! This is a test email from your SPM notification system.</p>
        <p>If you receive this email, your SendGrid integration is working correctly!</p>
        <hr>
        <p><strong>Test Details:</strong></p>
        <ul>
            <li>Recipient: User 160</li>
            <li>Email: """ + user_email + """</li>
            <li>Test Type: Direct Email Test</li>
            <li>Timestamp: """ + str(os.popen('date').read().strip()) + """</li>
        </ul>
        <hr>
        <p><small>This is a test message from the SPM notification system.</small></p>
        """
    }
    
    try:
        response = requests.post(
            f"{NOTIFICATION_API}/notifications/test-email",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Test email sent successfully!")
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print("❌ Test email failed")
            
    except Exception as e:
        print(f"Error testing direct email: {e}")

def test_user_notification():
    """Test notification trigger for user 160."""
    print(f"\n=== Testing Notification Trigger for User 160 ===")
    
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
            print("✅ Notification triggered successfully!")
            print(f"Results: {json.dumps(result, indent=2)}")
        else:
            print("❌ Notification trigger failed")
            
    except Exception as e:
        print(f"Error testing user notification: {e}")

def test_user_service_api():
    """Test getting user 160 data via the user service API."""
    print(f"\n=== Testing User Service API for User 160 ===")
    
    try:
        response = requests.get(f"{USER_API}/users/160")
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ User service API working!")
            print(f"User data: {json.dumps(user_data, indent=2)}")
            
            # Extract email and preferences
            data = user_data.get("data", {})
            email = data.get("email")
            preferences = data.get("notification_preferences", {})
            
            print(f"\nEmail: {email}")
            print(f"Notification Preferences: {preferences}")
            
            return email
        else:
            print(f"❌ User service API failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error testing user service API: {e}")
        return None

def main():
    """Run all tests."""
    print("=== SPM Email Notification Test for User 160 ===")
    
    # Test SendGrid configuration
    if not test_sendgrid_config():
        print("\n❌ SendGrid not properly configured. Please check your .env file.")
        return
    
    print("\n✅ SendGrid configuration looks good!")
    
    # Get user 160's email from Supabase
    user_email = get_user_160_email()
    
    if not user_email:
        print("\n❌ Could not retrieve user 160's email from Supabase.")
        print("Trying alternative method via User Service API...")
        
        # Try alternative method via User Service API
        user_email = test_user_service_api()
        
        if not user_email:
            print("\n❌ Could not retrieve user 160's email from any source.")
            return
    
    print(f"\n✅ Successfully retrieved user 160's email: {user_email}")
    
    # Test direct email
    test_direct_email(user_email)
    
    # Test user notification
    test_user_notification()
    
    print(f"\n=== Test Complete ===")
    print(f"Check {user_email} inbox for test messages.")
    print("If you don't receive emails, check the notification service logs for DEBUG messages.")
    print("\nNext steps:")
    print("1. Check your email inbox")
    print("2. Check spam folder")
    print("3. Check notification service logs")
    print("4. Verify SendGrid account status and sender authentication")

if __name__ == "__main__":
    main()
