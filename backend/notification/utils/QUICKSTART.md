# Quick Start Guide: Deadline Reminder Scheduler

Get your deadline reminder system up and running in 5 minutes! ⚡

## Step 1: Prerequisites ✅

Make sure you have:
- [x] Python 3.8+ installed
- [x] All dependencies installed (`pip install -r ../requirements.txt`)
- [x] Environment variables configured in `.env` file
- [x] Notification service running

## Step 2: Configure Environment Variables 🔧

Add these to your `.env` file in the `backend` directory:

```bash
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_sender_email

# Optional (with defaults)
NOTIFICATION_API_URL=http://127.0.0.1:5006
SCHEDULER_TIME=09:00
RUN_ON_STARTUP=false
```

## Step 3: Start the Notification Service 🚀

```bash
# Terminal 1: Start the notification service
cd backend/notification
python app.py
```

You should see:
```
Notifications microservice running on port 5006
```

## Step 4: Test the Scheduler 🧪

```bash
# Terminal 2: Run the test script
cd backend/notification
python utils/test_scheduler.py
```

This will:
- ✅ Test connections to Supabase and the notification API
- ✅ Show you tasks with upcoming deadlines
- ✅ Let you send a test reminder manually

### Example Test Output:

```
🧪 Testing Deadline Reminder Scheduler
═══════════════════════════════════════════════════════════════

1️⃣  Testing connections...
   ✅ All connections successful

2️⃣  Fetching tasks with upcoming deadlines...
   Found 3 tasks with upcoming deadlines

   📋 Task details:
   - Task 123: 'Website Redesign'
     Status: Ongoing
     Due: 2025-10-29
     Days until due: 3
     Reminder intervals: [7, 3, 1]
     Should send reminder today: ✅ YES

3️⃣  Process all deadline reminders?
   Run the full reminder process? (y/n): y

═══════════════════════════════════════════════════════════════
🔔 Starting deadline reminder processing
═══════════════════════════════════════════════════════════════
Found 3 tasks with upcoming deadlines
Processing task 123 ('Website Redesign'): 3 days until due
✅ Reminder sent successfully for task 123
═══════════════════════════════════════════════════════════════
✅ Deadline reminder processing complete
   📤 Reminders sent: 1
   ⏭️  Reminders skipped: 2
   ❌ Errors: 0
═══════════════════════════════════════════════════════════════
```

## Step 5: Run the Scheduler 🕐

### For Development/Testing:

```bash
# Terminal 2: Run the scheduler
cd backend/notification
python utils/deadline_reminder_scheduler.py
```

You should see:
```
🚀 Deadline Reminder Scheduler Starting...
📍 Notification API URL: http://127.0.0.1:5006
⏰ Scheduled to run daily at: 09:00
✅ Scheduler configured successfully
📅 Next run scheduled for: 2025-10-23 09:00:00
🔄 Press Ctrl+C to exit
```

### For Production:

```bash
# Run in background with nohup
nohup python utils/deadline_reminder_scheduler.py > scheduler.log 2>&1 &

# Check if it's running
ps aux | grep deadline_reminder_scheduler

# View logs
tail -f scheduler.log
```

## Step 6: Verify It's Working ✅

### Check the logs:

```bash
tail -f deadline_reminders.log
```

### Manually trigger a reminder (for testing):

```bash
# Set environment variable to run on startup
export RUN_ON_STARTUP=true

# Then start the scheduler
python utils/deadline_reminder_scheduler.py
```

Or use the test script:
```bash
python utils/test_scheduler.py
# Choose option 4 to send a manual test reminder
```

### Check notifications in the database:

```python
# In Python shell
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# Get recent deadline reminders
notifications = client.table("notification")\
    .select("*")\
    .eq("notification_type", "due_date_reminder")\
    .order("created_at", desc=True)\
    .limit(10)\
    .execute()

for n in notifications.data:
    print(f"User {n['userid']}: {n['notification']}")
```

## Common Issues & Solutions 🔧

### Issue: "Notification API connection failed"

**Solution:**
```bash
# Make sure notification service is running
cd backend/notification
python app.py
```

### Issue: "Supabase connection failed"

**Solution:**
- Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
- Verify credentials are valid by testing in Python:
  ```python
  from supabase import create_client
  import os
  from dotenv import load_dotenv
  
  load_dotenv()
  client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
  print(client.table("task").select("id").limit(1).execute())
  ```

### Issue: "No tasks with upcoming deadlines found"

**Solution:**
- This is normal if no tasks have due dates in the next 7 days
- Create a test task with a due date 3 days from now:
  ```python
  from datetime import datetime, timedelta
  
  due_date = (datetime.now() + timedelta(days=3)).isoformat()
  # Create a task with this due_date
  ```

### Issue: "Reminders not being sent"

**Check:**
1. Task has a `due_date` set
2. Task status is not "Completed"
3. Today's date matches one of the task's `reminder_intervals`
4. Reminder wasn't already sent today

**Debug:**
```bash
python utils/test_scheduler.py
# This will show you exactly which tasks are eligible
```

## Next Steps 🎯

### 1. Customize Reminder Times

Edit `.env`:
```bash
SCHEDULER_TIME=14:30  # Run at 2:30 PM instead of 9:00 AM
```

### 2. Set Up as System Service

See [README.md](README.md#method-3-system-service-production-recommended) for instructions on running as a systemd service or with PM2.

### 3. Monitor Logs

```bash
# View all logs
cat deadline_reminders.log

# View today's reminders
grep $(date +%Y-%m-%d) deadline_reminders.log

# Count reminders sent today
grep "Reminder sent successfully" deadline_reminders.log | grep $(date +%Y-%m-%d) | wc -l
```

### 4. Customize Reminder Intervals

Users can customize per-task reminder intervals:
```json
{
  "task_id": 123,
  "reminder_intervals": [10, 5, 2, 1]  // 10, 5, 2, and 1 days before
}
```

## Need Help? 🆘

1. Check the [full README](README.md) for detailed documentation
2. Review the logs: `deadline_reminders.log`
3. Run the test script: `python utils/test_scheduler.py`
4. Verify the endpoint works manually:
   ```bash
   curl -X POST http://127.0.0.1:5006/notifications/triggers/deadline-reminder \
     -H "Content-Type: application/json" \
     -d '{"task_id": 123, "reminder_days": 3}'
   ```

## You're All Set! 🎉

Your deadline reminder system is now running! Users will automatically receive notifications based on their task reminder intervals and notification preferences.

**Remember:**
- Scheduler runs daily at the configured time (default 9:00 AM)
- Notifications are sent to task owner + all collaborators
- Users receive notifications based on their preferences (in-app/email/both)
- Completed tasks are automatically skipped
- No duplicate reminders on the same day


