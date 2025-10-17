#!/usr/bin/env python3
"""
Email Notification Test Script

This script tests the email notification system to help debug SendGrid integration issues.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoints
NOTIFICATION_API = "http://127.0.0.1:5006"

def test_sendgrid_config():
    """Test SendGrid configuration."""
    print("=== Testing SendGrid Configuration ===")
    
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

def test_direct_email():
    """Test sending email directly through the notification service."""
    print("\n=== Testing Direct Email Notification ===")
    
    # Replace with your actual email address for testing
    test_email = input("Enter your email address for testing: ").strip()
    
    if not test_email:
        print("No email provided, skipping test")
        return
    
    test_data = {
        "user_email": test_email,
        "subject": "SPM Test Notification",
        "message": """
        <h2>Test Email Notification</h2>
        <p>This is a test email from your SPM notification system.</p>
        <p>If you receive this email, your SendGrid integration is working correctly!</p>
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
        else:
            print("❌ Test email failed")
            
    except Exception as e:
        print(f"Error testing direct email: {e}")

def test_user_notification():
    """Test notification for a specific user."""
    print("\n=== Testing User Notification ===")
    
    user_id = input("Enter user ID to test (e.g., 160): ").strip()
    
    if not user_id:
        print("No user ID provided, skipping test")
        return
    
    try:
        user_id = int(user_id)
    except ValueError:
        print("Invalid user ID")
        return
    
    test_data = {
        "task_id": 1,
        "user_ids": [user_id],
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

def main():
    """Run all tests."""
    print("=== SPM Email Notification Test ===")
    
    # Test SendGrid configuration
    if not test_sendgrid_config():
        print("\n❌ SendGrid not properly configured. Please check your .env file.")
        return
    
    print("\n✅ SendGrid configuration looks good!")
    
    # Test direct email
    test_direct_email()
    
    # Test user notification
    test_user_notification()
    
    print(f"\n=== Test Complete ===")
    print("Check your email inbox for test messages.")
    print("If you don't receive emails, check the notification service logs for DEBUG messages.")

if __name__ == "__main__":
    main()
