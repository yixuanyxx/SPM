#!/usr/bin/env python3
"""
Simple SendGrid Test Script

This script tests the SendGrid API key using the working example format.
"""

import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/yixli/Documents/GitHub/SPM/backend/.env')

def test_sendgrid_simple():
    """Test SendGrid with the working example format."""
    print("=== Testing SendGrid API Key ===")
    
    # Get API key and sender email
    api_key = os.environ.get("SENDGRID_API_KEY")
    from_email = os.environ.get("SENDGRID_FROM_EMAIL")
    
    print(f"API Key: {api_key[:10]}..." if api_key else "Not set")
    print(f"From Email: {from_email}")
    
    if not api_key or not from_email:
        print("❌ Missing SendGrid configuration")
        return False
    
    try:
        # Create SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        
        # Create email using the working format
        from_email_obj = Email(from_email)
        to_email_obj = To("yixlim@gmail.com")  # User 160's email
        subject_obj = "SPM Test - SendGrid API Key Test"
        content_obj = Content("text/html", "Hello <b>yixuan!</b><br><br>This is a test email to verify your SendGrid API key is working correctly.")
        
        # Create mail object
        mail = Mail(from_email_obj, to_email_obj, subject_obj, content_obj)
        
        # Get mail as JSON
        mail_json = mail.get()
        
        # Send email
        print("Sending test email...")
        response = sg.client.mail.send.post(request_body=mail_json)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        
        if response.status_code in [200, 201, 202]:
            print("✅ SendGrid API key is working!")
            print("Check yixlim@gmail.com inbox for the test email.")
            return True
        else:
            print(f"❌ SendGrid error: {response.status_code}")
            print(f"Response body: {response.body}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SendGrid: {e}")
        return False

if __name__ == "__main__":
    test_sendgrid_simple()
