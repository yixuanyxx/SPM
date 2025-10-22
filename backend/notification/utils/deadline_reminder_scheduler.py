#!/usr/bin/env python3
"""
Deadline Reminder Scheduler

This script runs daily to check for tasks with upcoming deadlines and sends
reminder notifications to collaborators based on their reminder intervals.

Features:
- Sends reminders at customizable intervals (default: 7, 3, 1 days before due date)
- Respects user notification preferences (in-app/email)
- Skips completed tasks
- Tracks sent reminders to avoid duplicates
- Runs daily at 9:00 AM (configurable)
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deadline_reminders.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
NOTIFICATION_API_URL = os.getenv("NOTIFICATION_API_URL", "http://localhost:5006")
TASKS_API_URL = os.getenv("TASKS_API_URL", "http://localhost:5002")
SCHEDULER_TIME = os.getenv("SCHEDULER_TIME", "09:00")  # Default: 9:00 AM


def get_tasks_with_upcoming_deadlines(max_days_ahead: int = 7) -> List[Dict[str, Any]]:
    """
    Query tasks microservice for tasks with upcoming deadlines.
    
    Args:
        max_days_ahead: Maximum number of days to look ahead for deadlines
    
    Returns:
        List of tasks with due dates in the next max_days_ahead days
    """
    try:
        # Calculate date range for logging
        today = datetime.now().date()
        end_date = today + timedelta(days=max_days_ahead)
        
        logger.info(f"Querying tasks with due dates between {today} and {end_date}")
        
        # Call the tasks microservice endpoint
        tasks_api_url = f"{TASKS_API_URL}/tasks/upcoming-deadlines"
        params = {"max_days_ahead": max_days_ahead}
        
        response = requests.get(tasks_api_url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            tasks = result.get("data", [])
            logger.info(f"Found {len(tasks)} tasks with upcoming deadlines")
            return tasks
        elif response.status_code == 404:
            # No tasks found - this is not an error
            logger.info("No tasks with upcoming deadlines found")
            return []
        else:
            logger.error(f"Tasks API returned status {response.status_code}: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching tasks: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        return []


def calculate_days_until_due(due_date_str: str) -> int:
    """
    Calculate the number of days until a task is due.
    
    Args:
        due_date_str: ISO format date string
    
    Returns:
        Number of days until due date (0 if due today, negative if overdue)
    """
    try:
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
        today = datetime.now().date()
        delta = (due_date - today).days
        return delta
    except Exception as e:
        logger.error(f"Error parsing due date {due_date_str}: {str(e)}")
        return -999  # Return invalid value on error


def check_if_reminder_already_sent(task_id: int, reminder_days: int) -> bool:
    """
    Check if a reminder has already been sent for this task and interval.
    
    Args:
        task_id: ID of the task
        reminder_days: Reminder interval (e.g., 7, 3, 1)
    
    Returns:
        True if reminder was already sent today, False otherwise
    """
    try:
        today = datetime.now().date().isoformat()
        
        # Check if there's a notification of type 'due_date_reminder' created today
        # that contains this task_id and reminder_days info
        # Use the notification API to get notifications for the task
        response = requests.get(f"{NOTIFICATION_API_URL}/notifications/task/{task_id}", timeout=5)
        
        if response.status_code == 200:
            notifications = response.json().get("data", [])
            
            # Check if any notification contains the specific reminder_days in the content
            for notification in notifications:
                notification_type = notification.get("notification_type", "")
                created_at = notification.get("created_at", "")
                notification_text = notification.get("notification", "")
                
                # Check if it's a due_date_reminder created today with the right reminder_days
                if (notification_type == "due_date_reminder" and 
                    created_at.startswith(today) and 
                    f"{reminder_days} day" in notification_text):
                    logger.info(f"Reminder already sent for task {task_id} ({reminder_days} days)")
                    return True
        
        return False
    except Exception as e:
        logger.error(f"Error checking reminder status: {str(e)}")
        # On error, assume not sent to avoid missing reminders
        return False


def send_deadline_reminder(task_id: int, reminder_days: int) -> bool:
    """
    Send deadline reminder notification for a task.
    
    Args:
        task_id: ID of the task
        reminder_days: Number of days before due date
    
    Returns:
        True if notification sent successfully, False otherwise
    """
    try:
        url = f"{NOTIFICATION_API_URL}/notifications/triggers/deadline-reminder"
        payload = {
            "task_id": task_id,
            "reminder_days": reminder_days
        }
        
        logger.info(f"Sending reminder for task {task_id} ({reminder_days} days before due)")
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Reminder sent successfully for task {task_id}: {result.get('message')}")
            return True
        else:
            logger.error(f"Failed to send reminder for task {task_id}: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error sending reminder for task {task_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending reminder for task {task_id}: {str(e)}")
        return False


def process_deadline_reminders():
    """
    Main function to process all deadline reminders.
    This function is called by the scheduler.
    """
    logger.info("=" * 80)
    logger.info("Starting deadline reminder processing")
    logger.info("=" * 80)
    
    try:
        # Get all tasks with upcoming deadlines
        tasks = get_tasks_with_upcoming_deadlines(max_days_ahead=7)
        
        if not tasks:
            logger.info("No tasks with upcoming deadlines found")
            return
        
        sent_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process each task
        for task in tasks:
            task_id = task.get("id")
            task_name = task.get("task_name", "Unknown")
            due_date = task.get("due_date")
            reminder_intervals = task.get("reminder_intervals", [7, 3, 1])
            
            if not due_date:
                logger.warning(f"Task {task_id} has no due date, skipping")
                skipped_count += 1
                continue
            
            # Calculate days until due
            days_until_due = calculate_days_until_due(due_date)
            
            if days_until_due < 0:
                logger.warning(f"Task {task_id} is overdue ({abs(days_until_due)} days), skipping")
                skipped_count += 1
                continue
            
            logger.info(f"Processing task {task_id} ('{task_name}'): {days_until_due} days until due")
            
            # Check if we should send a reminder for any interval
            for reminder_days in reminder_intervals:
                if days_until_due == reminder_days:
                    # Check if reminder already sent today
                    if check_if_reminder_already_sent(task_id, reminder_days):
                        logger.info(f"Skipping: Reminder already sent for task {task_id} ({reminder_days} days)")
                        skipped_count += 1
                        continue
                    
                    # Send the reminder
                    if send_deadline_reminder(task_id, reminder_days):
                        sent_count += 1
                    else:
                        error_count += 1
        
        logger.info("=" * 80)
        logger.info(f"Deadline reminder processing complete")
        logger.info(f"Reminders sent: {sent_count}")
        logger.info(f"Reminders skipped: {skipped_count}")
        logger.info(f"Errors: {error_count}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Fatal error in deadline reminder processing: {str(e)}")
        raise


def test_scheduler_connection():
    """Test connection to notification API and tasks API before starting scheduler."""
    logger.info("Testing connections...")
    
    # Test tasks API connection
    try:
        response = requests.get(f"{TASKS_API_URL}/tasks/upcoming-deadlines", timeout=5)
        if response.status_code in [200, 404]:  # 404 is OK (no tasks found)
            logger.info(f"Tasks API connection successful (status: {response.status_code})")
        else:
            logger.error(f"Tasks API returned unexpected status: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Tasks API connection failed: {str(e)}")
        logger.warning("Make sure the tasks service is running on port 5002")
        return False
    
    # Test notification API connection
    try:
        response = requests.get(f"{NOTIFICATION_API_URL}/notifications/user/1", timeout=5)
        logger.info(f"Notification API connection successful (status: {response.status_code})")
    except Exception as e:
        logger.error(f"Notification API connection failed: {str(e)}")
        logger.warning("Make sure the notification service is running on port 5006")
        return False
    
    return True


def main():
    """Main function to start the scheduler."""
    logger.info("Deadline Reminder Scheduler Starting...")
    logger.info(f"Notification API URL: {NOTIFICATION_API_URL}")
    logger.info(f"Scheduled to run daily at: {SCHEDULER_TIME}")
    
    # Test connections
    if not test_scheduler_connection():
        logger.error("Connection tests failed. Exiting...")
        sys.exit(1)
    
    # Create scheduler
    scheduler = BlockingScheduler()
    
    # Parse scheduler time (format: "HH:MM")
    try:
        hour, minute = map(int, SCHEDULER_TIME.split(":"))
    except ValueError:
        logger.error(f"Invalid SCHEDULER_TIME format: {SCHEDULER_TIME}. Using default 09:00")
        hour, minute = 9, 0
    
    # Schedule the job to run daily at specified time
    scheduler.add_job(
        process_deadline_reminders,
        trigger=CronTrigger(hour=hour, minute=minute),
        id='deadline_reminder_job',
        name='Process Deadline Reminders',
        replace_existing=True
    )
    
    logger.info(f"Scheduler configured successfully")
    logger.info(f"Next run scheduled for: {scheduler.get_jobs()[0].next_run_time}")
    logger.info("Press Ctrl+C to exit")
    
    # Optionally run immediately for testing
    if os.getenv("RUN_ON_STARTUP", "false").lower() == "true":
        logger.info("Running deadline reminders immediately (RUN_ON_STARTUP=true)")
        process_deadline_reminders()
    
    try:
        # Start the scheduler
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n👋 Scheduler stopped by user")
        scheduler.shutdown()


if __name__ == "__main__":
    main()

