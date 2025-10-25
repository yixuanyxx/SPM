#!/usr/bin/env python3
"""
Test script for the deadline reminder scheduler using minutes instead of days.

This script allows you to test the scheduler with minute-based intervals
for faster testing without waiting for actual deadlines.
"""

import os
import sys
from datetime import datetime, timedelta
import pytz
import requests
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deadline_reminder_scheduler import (
    test_scheduler_connection,
    send_deadline_reminder
)

def calculate_minutes_until_due(due_date_str):
    """Calculate minutes until due date."""
    try:
        # Handle Singapore timezone input
        if 'T' in due_date_str and '+' not in due_date_str and 'Z' not in due_date_str:
            # Assume Singapore timezone if no timezone specified
            sg_tz = pytz.timezone('Asia/Singapore')
            due_date = datetime.fromisoformat(due_date_str)
            due_date = sg_tz.localize(due_date)
        else:
            # Handle ISO format with timezone
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        
        now = datetime.now(due_date.tzinfo)
        time_diff = due_date - now
        return int(time_diff.total_seconds() / 60)
    except Exception as e:
        print(f"Error calculating minutes until due: {e}")
        return None

def get_task_by_id(task_id):
    """Get a specific task by ID using HTTP API."""
    try:
        response = requests.get(f"http://127.0.0.1:5002/tasks/{task_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching task: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching task: {e}")
        return None

def process_minute_reminders(task_id, custom_due_date, reminder_minutes=[5, 2, 1]):
    """Process reminders for a specific task with minute-based intervals."""
    print(f"Processing minute-based reminders for task {task_id}")
    print(f"Custom due date: {custom_due_date}")
    print(f"Reminder intervals: {reminder_minutes} minutes")
    print()
    
    # Get the task
    task = get_task_by_id(task_id)
    if not task:
        print(f"Task {task_id} not found!")
        return
    
    print(f"Task found: '{task.get('task_name', 'Unknown')}'")
    print(f"Original due date: {task.get('due_date')}")
    print()
    
    # Calculate minutes until the custom due date
    minutes_until = calculate_minutes_until_due(custom_due_date)
    if minutes_until is None:
        print("Invalid due date format!")
        return
    
    print(f"Minutes until custom due date: {minutes_until}")
    print()
    
    # Check which reminders should be sent
    reminders_to_send = []
    for minutes in reminder_minutes:
        if minutes_until <= minutes and minutes_until > 0:
            reminders_to_send.append(minutes)
    
    if not reminders_to_send:
        print("No reminders should be sent at this time.")
        if minutes_until <= 0:
            print("Task is already overdue!")
        else:
            print(f"Next reminder will be sent in {min(reminder_minutes) - minutes_until} minutes")
        return
    
    print(f"Reminders to send: {reminders_to_send}")
    print()
    
    # Send the reminders
    for minutes in reminders_to_send:
        # Use minutes directly as reminder_days (the system expects positive integers)
        # This is a workaround for testing - in production, use actual days
        print(f"Sending {minutes}-minute reminder for task {task_id}...")
        print(f"  (Using {minutes} as reminder_days for testing)")
        success = send_deadline_reminder(task_id, minutes)
        
        if success:
            print(f"{minutes}-minute reminder sent successfully!")
        else:
            print(f"Failed to send {minutes}-minute reminder")
        print()

def monitor_reminders(task_id, custom_due_date, reminder_minutes=[5, 2, 1], check_interval=30):
    """Continuously monitor and send reminders at appropriate times."""
    print(f"Starting continuous monitoring for task {task_id}")
    print(f"Due date: {custom_due_date}")
    print(f"Reminder intervals: {reminder_minutes} minutes")
    print(f"Checking every {check_interval} seconds")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)
    
    sent_reminders = set()  # Track which reminders have been sent
    
    try:
        while True:
            current_time = datetime.now()
            print(f"\n[{current_time.strftime('%H:%M:%S')}] Checking reminders...")
            
            # Calculate minutes until due
            minutes_until = calculate_minutes_until_due(custom_due_date)
            
            if minutes_until is None:
                print("Invalid due date format!")
                break
            
            print(f"Minutes until due: {minutes_until}")
            
            # Check which reminders should be sent
            for minutes in reminder_minutes:
                reminder_key = f"{minutes}min"
                
                # Check if reminder should be sent and hasn't been sent yet
                if minutes_until <= minutes and minutes_until > 0 and reminder_key not in sent_reminders:
                    # Use minutes directly as reminder_days (the system expects positive integers)
                    # This is a workaround for testing - in production, use actual days
                    print(f" Sending {minutes}-minute reminder...")
                    print(f"  (Using {minutes} as reminder_days for testing)")
                    success = send_deadline_reminder(task_id, minutes)
                    
                    if success:
                        print(f"{minutes}-minute reminder sent successfully!")
                        sent_reminders.add(reminder_key)
                    else:
                        print(f"Failed to send {minutes}-minute reminder")
                elif reminder_key in sent_reminders:
                    print(f"{minutes}-minute reminder already sent")
            
            # Check if all reminders sent or task overdue
            if minutes_until <= 0:
                print("Task is now overdue!")
                break
            
            if len(sent_reminders) == len(reminder_minutes):
                print("All reminders have been sent!")
                break
            
            # Wait before next check
            print(f"Waiting {check_interval} seconds before next check...")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"Error during monitoring: {e}")

def main():
    """Run minute-based tests for the scheduler."""
    print("=" * 80)
    print("Testing Deadline Reminder Scheduler (Minute-based)")
    print("=" * 80)
    print()
    
    # Test 1: Connection tests
    print("1. Testing connections...")
    if test_scheduler_connection():
        print("    All connections successful\n")
    else:
        print("   Connection tests failed\n")
        print("   Make sure:")
        print("      - The notification service is running (python app.py)")
        print("      - Environment variables are set correctly")
        print("      - Supabase credentials are valid")
        return
    
    # Test 2: Get task ID and custom due date
    print("2. Task Configuration")
    try:
        task_id = int(input("   Enter task ID: "))
    except ValueError:
        print("   Invalid task ID")
        return
    
    print("\n   Enter custom due date:")
    print("   - Singapore time: 2024-01-15T14:30:00")
    print("   - ISO with timezone: 2024-01-15T14:30:00+08:00")
    print("   - UTC: 2024-01-15T06:30:00Z")
    custom_due_date = input("   Due date: ").strip()
    
    if not custom_due_date:
        print("   No due date provided, using Singapore time + 10 minutes")
        sg_tz = pytz.timezone('Asia/Singapore')
        now_sg = datetime.now(sg_tz)
        custom_due_date = (now_sg + timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S')
    
    print(f"\n   Using due date: {custom_due_date}")
    
    # Test 3: Set reminder intervals
    print("\n3. Reminder Configuration")
    print("   Default reminder intervals: [5, 2, 1] minutes")
    custom_intervals = input("   Use custom intervals? (y/n): ").lower().strip()
    
    reminder_minutes = [5, 2, 1]  # Default
    if custom_intervals == 'y':
        try:
            intervals_input = input("   Enter intervals (comma-separated, e.g., 10,5,1): ").strip()
            reminder_minutes = [int(x.strip()) for x in intervals_input.split(',')]
            reminder_minutes.sort(reverse=True)  # Sort in descending order
            print(f"   Using custom intervals: {reminder_minutes}")
        except ValueError:
            print("   Invalid input, using default intervals")
    
    print()
    
    # Test 4: Choose monitoring mode
    print("4. Monitoring Mode")
    print("   a) One-time check (immediate)")
    print("   b) Continuous monitoring (real-time)")
    mode = input("   Choose mode (a/b): ").lower().strip()
    
    if mode == 'a':
        print("\n4. Processing Minute-based Reminders (One-time)")
        print("=" * 50)
        process_minute_reminders(task_id, custom_due_date, reminder_minutes)
        print("=" * 50)
    elif mode == 'b':
        print("\n4. Starting Continuous Monitoring")
        print("=" * 50)
        monitor_reminders(task_id, custom_due_date, reminder_minutes)
        print("=" * 50)
    else:
        print("   Invalid choice, using one-time check")
        print("\n4. Processing Minute-based Reminders (One-time)")
        print("=" * 50)
        process_minute_reminders(task_id, custom_due_date, reminder_minutes)
        print("=" * 50)
    
    # Test 5: Manual reminder test
    print("\n5. Manual Reminder Test")
    response = input("   Send a manual test reminder? (y/n): ").lower().strip()
    
    if response == 'y':
        try:
            reminder_minutes_input = int(input("   Enter reminder minutes (e.g., 3): "))
            
            print(f"\n   Sending reminder for task {task_id} ({reminder_minutes_input} minutes)...")
            success = send_deadline_reminder(task_id, reminder_minutes_input)
            
            if success:
                print("    Test reminder sent successfully!")
            else:
                print("    Failed to send test reminder")
        except ValueError:
            print("    Invalid input")
        except Exception as e:
            print(f"    Error: {str(e)}")
    else:
        print("   Skipped\n")
    
    print()
    print("=" * 80)
    print("Minute-based testing complete!")
    print("=" * 80)
    print()
    print("Tips for testing:")
    print("   - Set due date to current time + 10 minutes for immediate testing")
    print("   - Use intervals like [10, 5, 1] for gradual testing")
    print("   - Run the script multiple times to test different scenarios")
    print()

if __name__ == "__main__":
    main()
