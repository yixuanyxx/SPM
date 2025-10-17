# SendGrid Email Notification Setup

## Required Environment Variables

To enable email notifications, you need to set the following environment variables in your `.env` file:

```bash
# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=your_verified_sender_email@yourdomain.com
```

## SendGrid Setup Steps

1. **Create a SendGrid Account**
   - Go to [SendGrid](https://sendgrid.com/) and create an account
   - Verify your email address

2. **Create an API Key**
   - Log into your SendGrid dashboard
   - Go to Settings > API Keys
   - Click "Create API Key"
   - Choose "Restricted Access" and give it "Mail Send" permissions
   - Copy the generated API key

3. **Verify a Sender Email**
   - Go to Settings > Sender Authentication
   - Choose "Single Sender Verification"
   - Add your email address and verify it
   - This email will be used as the "from" address for notifications

4. **Add Environment Variables**
   - Create or update your `.env` file in the backend directory
   - Add the variables above with your actual values

## Testing Email Notifications

Once configured, email notifications will be automatically sent when:
- Task status changes
- Task due date changes  
- Task description changes
- Task/subtask assignments
- Task ownership transfers

The system respects user notification preferences (in-app vs email) configured in the user settings.

## Troubleshooting

- If emails are not being sent, check the notification service logs
- Ensure your SendGrid account has sufficient sending quota
- Verify that the sender email is properly authenticated
- Check that the API key has the correct permissions
