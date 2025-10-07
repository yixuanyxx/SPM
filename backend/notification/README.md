# Notification Microservice

This microservice handles all notification functionality for the SPM (Software Project Management) system, including in-app notifications and email notifications via Twilio SendGrid.

## Features

- **In-app notifications**: Store and manage notifications in the database
- **Email notifications**: Send emails via Twilio SendGrid API
- **User preferences**: Respect user notification preferences (in-app, email, or both)
- **Task-related notifications**: Automatic notifications for task assignments and updates
- **Read/unread status**: Track notification read status
- **RESTful API**: Complete CRUD operations for notifications

## Setup

### Environment Variables

Create a `.env` file in the notification directory with the following variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Database Schema

The notification system uses a `notification` table in Supabase with the following schema:

```sql
CREATE TABLE notification (
    id BIGSERIAL PRIMARY KEY,
    userid INTEGER NOT NULL REFERENCES "user"(userid),
    notification TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_read BOOLEAN DEFAULT FALSE,
    notification_type TEXT DEFAULT 'general',
    related_task_id INTEGER
);
```

### User Notification Preferences

The user table should include a `notification_preferences` JSONB field:

```sql
ALTER TABLE "user" ADD COLUMN notification_preferences JSONB DEFAULT '{"in_app": true, "email": true}';
```

## API Endpoints

### Basic Notification Operations

- `POST /notifications/create` - Create a new notification
- `GET /notifications/user/{user_id}` - Get all notifications for a user
- `GET /notifications/{notification_id}` - Get a specific notification
- `PUT /notifications/{notification_id}/read` - Mark notification as read
- `PUT /notifications/{notification_id}/unread` - Mark notification as unread
- `GET /notifications/user/{user_id}/unread-count` - Get unread count for user
- `GET /notifications/user/{user_id}/unread` - Get unread notifications for user
- `DELETE /notifications/{notification_id}` - Delete a notification

### Notification Triggers

These endpoints are designed to be called by other microservices:

- `POST /notifications/triggers/task-assignment` - Trigger notification for task assignment
- `POST /notifications/triggers/task-status-change` - Trigger notification for task status change
- `POST /notifications/triggers/task-due-date-change` - Trigger notification for due date change
- `POST /notifications/triggers/task-description-change` - Trigger notification for description change

### User Preferences

Update user notification preferences via the user microservice:

- `PUT /users/{userid}/notification-preferences` - Update notification preferences

## Usage Examples

### Creating a Notification

```bash
curl -X POST http://localhost:5005/notifications/create \
  -H "Content-Type: application/json" \
  -d '{
    "userid": 123,
    "notification": "Your task has been updated",
    "notification_type": "task_updated",
    "related_task_id": 456
  }'
```

### Triggering Task Assignment Notification

```bash
curl -X POST http://localhost:5005/notifications/triggers/task-assignment \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 456,
    "assigned_user_id": 123,
    "assigner_name": "John Doe"
  }'
```

### Updating User Notification Preferences

```bash
curl -X PUT http://localhost:5003/users/123/notification-preferences \
  -H "Content-Type: application/json" \
  -d '{
    "in_app": true,
    "email": false
  }'
```

## Integration with Other Microservices

### Task Microservice Integration

When tasks are assigned or updated, the task microservice should call the notification trigger endpoints:

```python
import requests

# When assigning a task
requests.post("http://localhost:5005/notifications/triggers/task-assignment", json={
    "task_id": task_id,
    "assigned_user_id": user_id,
    "assigner_name": current_user_name
})

# When updating task status
requests.post("http://localhost:5005/notifications/triggers/task-status-change", json={
    "task_id": task_id,
    "user_ids": collaborator_ids,
    "old_status": old_status,
    "new_status": new_status,
    "updater_name": current_user_name
})
```

## Running the Service

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env` file

3. Run the service:
```bash
python app.py
```

The service will run on port 5005 by default.

## User Stories Implementation

This notification system implements the following user stories:

1. **Customise notification preferences in Account Settings page**
   - Users can update preferences via `/users/{userid}/notification-preferences`
   - Preferences are stored in the user table and respected by all notifications

2. **Receive notification when a new task/subtasks is assigned to user**
   - Implemented via `/notifications/triggers/task-assignment` endpoint
   - Respects user preferences for in-app and/or email notifications

3. **Task update notifications**
   - Status changes: `/notifications/triggers/task-status-change`
   - Due date changes: `/notifications/triggers/task-due-date-change`
   - Description changes: `/notifications/triggers/task-description-change`
   - All include old/new values and respect user preferences

4. **View all notifications in home page**
   - Get all notifications: `/notifications/user/{user_id}`
   - Get unread count: `/notifications/user/{user_id}/unread-count`
   - Mark as read/unread: `/notifications/{id}/read` or `/notifications/{id}/unread`
   - Notifications ordered by created_at descending

