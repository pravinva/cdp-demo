# Email & SMS Testing Alternatives

This document describes multiple options for testing email and SMS integrations without production API keys.

## Configuration

Set these in your `.env` file or environment variables:

```bash
# Email Testing Mode
EMAIL_TEST_MODE=console  # Options: console, mailtrap, mailhog, sendgrid, ses

# SMS Testing Mode  
SMS_TEST_MODE=console  # Options: console, twilio_test, twilio, mocksms
```

## Email Testing Options

### 1. **Console Mode** (Default - No Setup Required)
**Best for:** Quick local testing

```bash
EMAIL_TEST_MODE=console
```

- Prints emails to console/logs
- No external dependencies
- Perfect for development and debugging
- **No setup needed**

### 2. **Mailtrap** (Recommended for Testing)
**Best for:** Email testing with real email rendering

**Setup:**
1. Sign up at https://mailtrap.io (free tier available)
2. Get API token from dashboard
3. Configure:

```bash
EMAIL_TEST_MODE=mailtrap
MAILTRAP_API_TOKEN=your_api_token_here
```

**Benefits:**
- View emails in web interface
- Check spam scores
- Test HTML rendering
- Free tier: 500 emails/month

### 3. **MailHog** (Local Email Server)
**Best for:** Local development with email preview

**Setup:**
```bash
# Run MailHog via Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Configure
EMAIL_TEST_MODE=mailhog
MAILHOG_HOST=localhost
MAILHOG_PORT=1025
```

**Benefits:**
- View emails at http://localhost:8025
- No external dependencies
- Works offline
- Great for local development

### 4. **SendGrid** (Production)
**Best for:** Production email delivery

```bash
EMAIL_TEST_MODE=sendgrid
SENDGRID_API_KEY=your_api_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

### 5. **AWS SES** (Production)
**Best for:** Production email delivery on AWS

```bash
EMAIL_TEST_MODE=ses
# AWS credentials via AWS CLI or environment variables
```

## SMS Testing Options

### 1. **Console Mode** (Default - No Setup Required)
**Best for:** Quick local testing

```bash
SMS_TEST_MODE=console
```

- Prints SMS to console/logs
- No external dependencies
- Perfect for development

### 2. **Twilio Test Credentials** (Recommended for Testing)
**Best for:** Testing with real Twilio API (no charges)

**Setup:**
1. Sign up at https://www.twilio.com (free account)
2. Get Test Credentials from Twilio Console
3. Configure:

```bash
SMS_TEST_MODE=twilio_test
TWILIO_TEST_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_TEST_AUTH_TOKEN=your_test_auth_token
```

**Benefits:**
- Uses real Twilio API
- **No charges** (test credentials)
- Test delivery, webhooks, etc.
- Free tier available

**Test Phone Numbers:**
- Use Twilio test numbers: `+15005550006`, `+15005550007`, etc.
- Or use your verified phone number

### 3. **Twilio Production** (Production)
**Best for:** Production SMS delivery

```bash
SMS_TEST_MODE=twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
```

### 4. **MockSMS** (Alternative Testing Service)
**Best for:** Testing without Twilio account

```bash
SMS_TEST_MODE=mocksms
```

## Quick Start Examples

### Example 1: Console Mode (Simplest)
```bash
# .env file
EMAIL_TEST_MODE=console
SMS_TEST_MODE=console
```

**Output:**
```
📧 EMAIL (Console Mode)
================================================================================
From: noreply@cdp-platform.com
To: customer@example.com
Subject: Welcome!
--------------------------------------------------------------------------------
Hi there, welcome to our platform!
================================================================================
```

### Example 2: Mailtrap + Twilio Test
```bash
# .env file
EMAIL_TEST_MODE=mailtrap
MAILTRAP_API_TOKEN=your_token

SMS_TEST_MODE=twilio_test
TWILIO_TEST_ACCOUNT_SID=ACxxxxx
TWILIO_TEST_AUTH_TOKEN=your_token
```

### Example 3: MailHog (Local)
```bash
# Start MailHog
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# .env file
EMAIL_TEST_MODE=mailhog
MAILHOG_HOST=localhost
MAILHOG_PORT=1025

SMS_TEST_MODE=console
```

Then view emails at: http://localhost:8025

## Comparison

| Option | Setup Difficulty | Cost | Best For |
|--------|-----------------|------|----------|
| **Console** | ⭐ Easy | Free | Quick testing |
| **Mailtrap** | ⭐⭐ Medium | Free tier | Email testing |
| **MailHog** | ⭐⭐ Medium | Free | Local development |
| **Twilio Test** | ⭐⭐ Medium | Free | SMS testing |
| **SendGrid** | ⭐⭐ Medium | Paid | Production |
| **Twilio** | ⭐⭐ Medium | Paid | Production |

## Recommended Setup

**For Development:**
```bash
EMAIL_TEST_MODE=console
SMS_TEST_MODE=console
```

**For Testing:**
```bash
EMAIL_TEST_MODE=mailtrap
MAILTRAP_API_TOKEN=your_token

SMS_TEST_MODE=twilio_test
TWILIO_TEST_ACCOUNT_SID=ACxxxxx
TWILIO_TEST_AUTH_TOKEN=your_token
```

**For Production:**
```bash
EMAIL_TEST_MODE=sendgrid
SENDGRID_API_KEY=your_key

SMS_TEST_MODE=twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890
```

## Testing Workflow

1. **Start with Console Mode** - Verify code works
2. **Switch to Mailtrap/Twilio Test** - Test with real services
3. **Use Production** - When ready to go live

The system automatically falls back to console mode if configured providers fail.

