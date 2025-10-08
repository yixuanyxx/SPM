#!/usr/bin/env python3
"""
Notification System Testing Script
This script helps test both in-app and email notifications
"""

import requests
import json
import time
from datetime import datetime

# API Endpoints
NOTIFICATION_API = "http://127.0.0.1:5006"
USER_API = "http://127.0.0.1:5003"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n[STEP {step}] {description}")
    print("-" * 50)

def test_create_notification():
    """Test creating a basic notification"""
    print_step(1, "Testing Basic Notification Creation")
    
    # Test data
    test_notification = {
        "userid": 1,  # Change this to a valid user ID in your system
        "notification": "This is a test notification created via API",
        "notification_type": "test",
        "related_task_id": None
    }
    
    try:
        response = requests.post(
            f"{NOTIFICATION_API}/notifications/create",
            json=test_notification,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Notification created successfully!")
            return response.json().get("data", {}).get("id")
        else:
            print("❌ Failed to create notification")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_get_user_notifications(user_id):
    """Test retrieving user notifications"""
    print_step(2, f"Testing Get Notifications for User {user_id}")
    
    try:
        response = requests.get(f"{NOTIFICATION_API}/notifications/user/{user_id}")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            notifications = response.json().get("data", [])
            print(f"✅ Found {len(notifications)} notifications")
            return notifications
        else:
            print("❌ Failed to get notifications")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return []

def test_unread_count(user_id):
    """Test getting unread notification count"""
    print_step(3, f"Testing Unread Count for User {user_id}")
    
    try:
        response = requests.get(f"{NOTIFICATION_API}/notifications/user/{user_id}/unread-count")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            count = response.json().get("data", {}).get("unread_count", 0)
            print(f"✅ Unread count: {count}")
            return count
        else:
            print("❌ Failed to get unread count")
            return 0
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return 0

def test_mark_as_read(notification_id):
    """Test marking notification as read"""
    print_step(4, f"Testing Mark as Read for Notification {notification_id}")
    
    if not notification_id:
        print("❌ No notification ID provided")
        return False
    
    try:
        response = requests.put(f"{NOTIFICATION_API}/notifications/{notification_id}/read")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Notification marked as read!")
            return True
        else:
            print("❌ Failed to mark as read")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_task_assignment_notification():
    """Test task assignment notification trigger"""
    print_step(5, "Testing Task Assignment Notification")
    
    # Test data - adjust these values for your system
    assignment_data = {
        "task_id": 1,  # Change to a valid task ID
        "assigned_user_id": 1,  # Change to a valid user ID
        "assigner_name": "Test Manager"
    }
    
    try:
        response = requests.post(
            f"{NOTIFICATION_API}/notifications/triggers/task-assignment",
            json=assignment_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Task assignment notification sent!")
            return True
        else:
            print("❌ Failed to send task assignment notification")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_task_status_change_notification():
    """Test task status change notification trigger"""
    print_step(6, "Testing Task Status Change Notification")
    
    # Test data - adjust these values for your system
    status_change_data = {
        "task_id": 1,  # Change to a valid task ID
        "user_ids": [1, 2],  # Change to valid user IDs (collaborators)
        "old_status": "Ongoing",
        "new_status": "Completed",
        "updater_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{NOTIFICATION_API}/notifications/triggers/task-status-change",
            json=status_change_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Task status change notification sent!")
            return True
        else:
            print("❌ Failed to send task status change notification")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_user_preferences(user_id):
    """Test getting user notification preferences"""
    print_step(7, f"Testing User Preferences for User {user_id}")
    
    try:
        response = requests.get(f"{USER_API}/users/{user_id}")
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json().get("data", {})
            preferences = user_data.get("notification_preferences", {})
            print(f"User Preferences: {json.dumps(preferences, indent=2)}")
            print(f"✅ User preferences retrieved!")
            return preferences
        else:
            print("❌ Failed to get user preferences")
            return {}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {}

def main():
    """Run all notification tests"""
    print_header("NOTIFICATION SYSTEM TESTING")
    print(f"Test started at: {datetime.now()}")
    
    # Configuration - CHANGE THESE VALUES FOR YOUR SYSTEM
    TEST_USER_ID = 676  # Change to a valid user ID in your database
    
    print(f"\n🔧 Configuration:")
    print(f"   - Test User ID: {TEST_USER_ID}")
    print(f"   - Notification API: {NOTIFICATION_API}")
    print(f"   - User API: {USER_API}")
    
    # Test sequence
    print_header("RUNNING TESTS")
    
    # 1. Test basic notification creation
    notification_id = test_create_notification()
    
    # 2. Test getting user notifications
    notifications = test_get_user_notifications(TEST_USER_ID)
    
    # 3. Test unread count
    unread_count = test_unread_count(TEST_USER_ID)
    
    # 4. Test marking as read (if we have a notification)
    if notification_id:
        test_mark_as_read(notification_id)
    
    # 5. Test task assignment notification
    test_task_assignment_notification()
    
    # 6. Test task status change notification
    test_task_status_change_notification()
    
    # 7. Test user preferences
    test_user_preferences(TEST_USER_ID)
    
    print_header("TEST SUMMARY")
    print("✅ All tests completed!")
    print("\n📝 Next Steps:")
    print("   1. Check your frontend for in-app notifications")
    print("   2. Check your email for email notifications")
    print("   3. Verify notification preferences in Account Settings")
    print("   4. Test the notification bell icon and dropdown")

if __name__ == "__main__":
    main()
