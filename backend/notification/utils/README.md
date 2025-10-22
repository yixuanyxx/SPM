# Deadline Reminder Scheduler

This directory contains the APScheduler script for sending automated deadline reminder notifications.

## Overview

The `deadline_reminder_scheduler.py` script runs as a standalone process that:
- Checks for tasks with upcoming deadlines daily
- Sends reminder notifications based on task `reminder_intervals` (default: 7, 3, 1 days before due date)
- Respects user notification preferences (in-app/email)
- Skips completed tasks automatically
- Prevents duplicate reminders on the same day

## Setup

### 1. Prerequisites

Make sure you have the following environment variables in your `.env` file:

```bash
# Supabase Configuration (required)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key

# SendGrid Configuration (required for email notifications)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_sender_email

# Optional Configuration
NOTIFICATION_API_URL=http://127.0.0.1:5006  # Default notification service URL
SCHEDULER_TIME=09:00  # Daily run time (24-hour format)
RUN_ON_STARTUP=false  # Set to 'true' to run immediately on startup (for testing)
```

### 2. Dependencies

All required dependencies are already included in `backend/notification/requirements.txt`:
- `apscheduler==3.10.4`
- `requests==2.31.0`
- `python-dotenv==1.1.1`
- `supabase==2.19.0`

## Running the Scheduler

### Method 1: Manual Execution (Development)

```bash
# Navigate to the notification directory
cd backend/notification

# Make sure the notification service is running first
python app.py

# In a new terminal, run the scheduler
python utils/deadline_reminder_scheduler.py
```

### Method 2: Background Process (Production)

#### On Linux/Mac:
```bash
# Using nohup
nohup python utils/deadline_reminder_scheduler.py > scheduler.log 2>&1 &

# Or using screen
screen -S deadline-scheduler
python utils/deadline_reminder_scheduler.py
# Press Ctrl+A then D to detach
```

#### On Windows:
```bash
# Run in a separate command prompt window
start /B python utils\deadline_reminder_scheduler.py
```

### Method 3: System Service (Production - Recommended)

#### Using systemd (Linux):

Create a service file `/etc/systemd/system/deadline-reminder.service`:

```ini
[Unit]
Description=Deadline Reminder Scheduler
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/SPM/backend/notification
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python utils/deadline_reminder_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable deadline-reminder
sudo systemctl start deadline-reminder
sudo systemctl status deadline-reminder
```

#### Using PM2 (Cross-platform):

```bash
npm install -g pm2
pm2 start utils/deadline_reminder_scheduler.py --name deadline-scheduler --interpreter python
pm2 save
pm2 startup
```

## Configuration

### Scheduler Time

By default, the scheduler runs at **9:00 AM** every day. To change this:

```bash
# In your .env file
SCHEDULER_TIME=14:30  # Run at 2:30 PM
```

### Testing Immediately

To run the scheduler immediately on startup (useful for testing):

```bash
# In your .env file
RUN_ON_STARTUP=true
```

### Custom Reminder Intervals

Users can customize reminder intervals per task by setting the `reminder_intervals` field:

```json
{
  "task_id": 123,
  "reminder_intervals": [10, 5, 2]  // Remind 10, 5, and 2 days before due date
}
```

Default intervals: `[7, 3, 1]` (7 days, 3 days, 1 day before due date)

## How It Works

### Daily Workflow:

1. **9:00 AM**: Scheduler wakes up
2. **Query Tasks**: Fetches all non-completed tasks with due dates in the next 7 days
3. **Calculate Days**: For each task, calculates days until due date
4. **Check Intervals**: Compares days until due with task's `reminder_intervals`
5. **Check Duplicates**: Ensures reminder wasn't already sent today
6. **Send Notifications**: Calls the `/notifications/triggers/deadline-reminder` endpoint
7. **Respects Preferences**: Notifications sent based on user preferences (in-app/email)
8. **Log Results**: Records sent, skipped, and error counts

### Example Scenario:

**Task Details:**
- Due Date: October 30, 2025
- Today: October 23, 2025 (7 days before due)
- Reminder Intervals: `[7, 3, 1]`
- Collaborators: User 100 (owner), User 101, User 102

**What Happens:**
1. Scheduler runs at 9:00 AM
2. Finds this task (7 days until due)
3. Matches the `7` in reminder intervals
4. Sends reminder to all 3 collaborators
5. Each user receives notification based on their preferences:
   - User 100: In-app only
   - User 101: Email only
   - User 102: Both in-app and email

**Next Reminders:**
- October 27 (3 days before): Second reminder sent
- October 29 (1 day before): Final "URGENT" reminder sent

## Monitoring

### Check Logs

The scheduler writes to both console and `deadline_reminders.log`:

```bash
# View logs in real-time
tail -f deadline_reminders.log

# Search for errors
grep "ERROR" deadline_reminders.log

# Count reminders sent today
grep "Reminder sent successfully" deadline_reminders.log | grep $(date +%Y-%m-%d) | wc -l
```

### Log Format

```
2025-10-22 09:00:00 - INFO - 🔔 Starting deadline reminder processing
2025-10-22 09:00:01 - INFO - Found 5 tasks with upcoming deadlines
2025-10-22 09:00:02 - INFO - Processing task 123 ('Website Redesign'): 3 days until due
2025-10-22 09:00:03 - INFO - ✅ Reminder sent successfully for task 123
2025-10-22 09:00:10 - INFO - ✅ Deadline reminder processing complete
2025-10-22 09:00:10 - INFO -    📤 Reminders sent: 4
2025-10-22 09:00:10 - INFO -    ⏭️  Reminders skipped: 1
2025-10-22 09:00:10 - INFO -    ❌ Errors: 0
```

## Troubleshooting

### Scheduler Won't Start

**Check connections:**
```bash
python utils/deadline_reminder_scheduler.py
```

Look for connection test results:
- ✅ Supabase connection successful
- ✅ Notification API connection successful

**Common issues:**
- Notification service not running → Start `app.py` first
- Wrong environment variables → Check `.env` file
- Port conflicts → Ensure port 5006 is available

### No Reminders Being Sent

**Check task conditions:**
1. Task has a `due_date` set
2. Task status is NOT "Completed"
3. Due date is within the next 7 days
4. Today matches one of the `reminder_intervals`

**Example query to check eligible tasks:**
```python
from datetime import datetime, timedelta
today = datetime.now().date()
end_date = today + timedelta(days=7)

# Tasks that should trigger reminders
tasks = supabase_client.table("task")\
    .select("*")\
    .gte("due_date", today.isoformat())\
    .lte("due_date", end_date.isoformat())\
    .neq("status", "Completed")\
    .execute()
```

### Duplicate Reminders

The scheduler checks if a reminder was already sent today by:
1. Querying notifications with `notification_type = "due_date_reminder"`
2. Filtering by `related_task_id`
3. Checking if created today
4. Matching reminder interval in message

If duplicates occur, check the `notification` table for multiple entries.

### Testing Without Waiting

```bash
# Set RUN_ON_STARTUP=true in .env, then:
python utils/deadline_reminder_scheduler.py

# Or manually call the function:
python -c "from utils.deadline_reminder_scheduler import process_deadline_reminders; process_deadline_reminders()"
```

## API Integration

The scheduler calls this endpoint for each reminder:

```
POST http://127.0.0.1:5006/notifications/triggers/deadline-reminder
Content-Type: application/json

{
    "task_id": 123,
    "reminder_days": 3
}
```

Response:
```json
{
    "message": "Deadline reminder notifications sent to all collaborators",
    "results": [
        {
            "user_id": 100,
            "result": {
                "status": 200,
                "message": "Notifications sent based on user preferences",
                "results": [...]
            }
        }
    ],
    "status": 200
}
```

## Support

For issues or questions:
1. Check the logs: `deadline_reminders.log`
2. Verify environment variables
3. Ensure notification service is running
4. Test the endpoint manually using curl/Postman

## License

Part of the SPM (Software Project Management) project.

