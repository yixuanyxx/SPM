#!/usr/bin/env python3
"""
Test script for the deadline reminder scheduler.

This script allows you to test the scheduler without waiting for the scheduled time.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deadline_reminder_scheduler import (
    test_scheduler_connection,
    process_deadline_reminders,
    get_tasks_with_upcoming_deadlines,
    calculate_days_until_due,
    send_deadline_reminder
)

def main():
    """Run tests for the scheduler."""
    print("=" * 80)
    print("Testing Deadline Reminder Scheduler")
    print("=" * 80)
    print()
    
    # Test 1: Connection tests
    print("1.Testing connections...")
    if test_scheduler_connection():
        print("    All connections successful\n")
    else:
        print("   Connection tests failed\n")
        print("   Make sure:")
        print("      - The notification service is running (python app.py)")
        print("      - Environment variables are set correctly")
        print("      - Supabase credentials are valid")
        return
    
    # Test 2: Get tasks
    print("2.  Fetching tasks with upcoming deadlines...")
    tasks = get_tasks_with_upcoming_deadlines(max_days_ahead=7)
    print(f"   Found {len(tasks)} tasks with upcoming deadlines\n")
    
    if tasks:
        print("   Task details:")
        for task in tasks:
            task_id = task.get("id")
            task_name = task.get("task_name", "Unknown")
            due_date = task.get("due_date")
            status = task.get("status")
            reminder_intervals = task.get("reminder_intervals", [7, 3, 1])
            
            days_until = calculate_days_until_due(due_date)
            
            print(f"   - Task {task_id}: '{task_name}'")
            print(f"     Status: {status}")
            print(f"     Due: {due_date}")
            print(f"     Days until due: {days_until}")
            print(f"     Reminder intervals: {reminder_intervals}")
            
            # Check if reminder should be sent
            should_send = days_until in reminder_intervals
            print(f"     Should send reminder today: {'YES' if should_send else 'NO'}")
            print()
    else:
        print("   No tasks found. This is normal if:")
        print("      - No tasks have due dates in the next 7 days")
        print("      - All tasks with upcoming due dates are completed")
        print()
    
    # Test 3: Ask if user wants to run the full process
    print("3. Process all deadline reminders?")
    response = input("   Run the full reminder process? (y/n): ").lower().strip()
    
    if response == 'y':
        print()
        print("=" * 80)
        process_deadline_reminders()
        print("=" * 80)
    else:
        print("   Skipped\n")
    
    # Test 4: Manual reminder test
    print("4. Send a test reminder manually?")
    response = input("   Send a manual test reminder? (y/n): ").lower().strip()
    
    if response == 'y':
        try:
            task_id = int(input("   Enter task ID: "))
            reminder_days = int(input("   Enter reminder days (e.g., 3): "))
            
            print(f"\n   Sending reminder for task {task_id} ({reminder_days} days)...")
            success = send_deadline_reminder(task_id, reminder_days)
            
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
    print("Testing complete!")
    print("=" * 80)
    print()
    print("To run the scheduler normally:")
    print("   python utils/deadline_reminder_scheduler.py")
    print()


if __name__ == "__main__":
    main()


