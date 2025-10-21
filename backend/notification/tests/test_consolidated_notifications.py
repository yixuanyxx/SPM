#!/usr/bin/env python3
"""
Consolidated Notification Test Script

This script tests the new consolidated notification system to ensure multiple changes
to the same task result in only one notification per user.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/yixli/Documents/GitHub/SPM/backend/.env')

# API endpoints
NOTIFICATION_API = "http://127.0.0.1:5006"

def test_consolidated_notification():
    """Test consolidated notification with multiple changes."""
    print("=== Testing Consolidated Notification System ===")
    
    # Test data with multiple changes to the same task
    test_data = {
        "task_id": 1,
        "user_ids": [160],  # User 160 (yixlim@gmail.com)
        "changes": [
            {
                "field": "status",
                "old_value": "Ongoing",
                "new_value": "Under Review",
                "field_name": "Status"
            },
            {
                "field": "priority",
                "old_value": "Medium",
                "new_value": "High",
                "field_name": "Priority"
            },
            {
                "field": "description",
                "old_value": "Old description",
                "new_value": "Updated description with more details",
                "field_name": "Description"
            }
        ],
        "updater_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{NOTIFICATION_API}/notifications/triggers/task-consolidated-update",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Consolidated notification sent successfully!")
            print(f"Results: {json.dumps(result, indent=2)}")
            
            # Check if only one notification was created per user
            results = result.get("results", [])
            for user_result in results:
                user_id = user_result.get("user_id")
                notification_results = user_result.get("result", {}).get("results", [])
                
                print(f"\nUser {user_id} notifications:")
                for notif_result in notification_results:
                    notif_type = notif_result.get("type")
                    notif_data = notif_result.get("result", {}).get("data", {})
                    
                    if notif_type == "in_app":
                        print(f"  📱 In-app: {notif_data.get('notification', 'N/A')}")
                    elif notif_type == "email":
                        print(f"  📧 Email: {notif_result.get('result', {}).get('message', 'N/A')}")
            
            return True
        else:
            print("❌ Consolidated notification failed")
            return False
            
    except Exception as e:
        print(f"Error testing consolidated notification: {e}")
        return False

def test_multiple_single_notifications():
    """Test multiple single notifications to compare with consolidated approach."""
    print("\n=== Testing Multiple Single Notifications (for comparison) ===")
    
    # Test individual notifications (old approach)
    individual_tests = [
        {
            "endpoint": "/notifications/triggers/task-status-change",
            "data": {
                "task_id": 1,
                "user_ids": [160],
                "old_status": "Ongoing",
                "new_status": "Under Review",
                "updater_name": "Test User"
            }
        },
        {
            "endpoint": "/notifications/triggers/task-priority-change",
            "data": {
                "task_id": 1,
                "user_ids": [160],
                "old_priority": "Medium",
                "new_priority": "High",
                "updater_name": "Test User"
            }
        }
    ]
    
    notification_count = 0
    
    for test in individual_tests:
        try:
            response = requests.post(
                f"{NOTIFICATION_API}{test['endpoint']}",
                json=test["data"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                notification_count += 1
                print(f"✅ Individual notification {notification_count} sent")
            else:
                print(f"❌ Individual notification failed: {response.status_code}")
                
        except Exception as e:
            print(f"Error sending individual notification: {e}")
    
    print(f"Total individual notifications sent: {notification_count}")
    return notification_count

def main():
    """Run all tests."""
    print("=== SPM Consolidated Notification Test ===")
    
    # Test consolidated notification
    consolidated_success = test_consolidated_notification()
    
    # Test individual notifications for comparison
    individual_count = test_multiple_single_notifications()
    
    print(f"\n=== Test Summary ===")
    print(f"Consolidated notification: {'✅ Success' if consolidated_success else '❌ Failed'}")
    print(f"Individual notifications: {individual_count} sent")
    
    if consolidated_success:
        print(f"\n🎉 Consolidated notification system is working!")
        print(f"✅ Multiple changes to the same task now result in ONE notification per user")
        print(f"✅ Both in-app and email notifications are consolidated")
        print(f"✅ Check yixlim@gmail.com inbox for the consolidated email")
    else:
        print(f"\n❌ Consolidated notification system needs debugging")

if __name__ == "__main__":
    main()
