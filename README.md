# Railway Automation

Automate Railway deployments and manage your Railway account programmatically using Railway API tokens.

## What is a Railway API Token?

A Railway API token is an authentication credential that allows you to programmatically access and manage your Railway account without using the web interface. It enables you to:

- Deploy applications and Docker containers
- Manage projects and services
- Access Railway's REST API
- Automate deployments and infrastructure management
- Integrate Railway with CI/CD pipelines
- Run automated scripts and tools

## Obtaining an API Token

1. **Via Mobile App** (as shown in the image):
   - Open the Railway mobile app
   - Navigate to the **Tokens** section (purple key icon)
   - Tap **"New Token"** to generate a new token
   - Copy the token immediately (you'll only see it once)
   - Store it securely

2. **Via Web Interface**:
   - Log in to [railway.app](https://railway.app)
   - Go to your account settings
   - Navigate to the API tokens section
   - Create a new token with a descriptive name (e.g., "Automate App", "CI/CD Pipeline")
   - Copy and securely store the token

## Using the Token

### Environment Variable
Set the token as an environment variable:
```bash
export RAILWAY_TOKEN="your-token-here"
```

### In Scripts
```bash
# Using curl
curl -H "Authorization: Bearer $RAILWAY_TOKEN" \
     https://api.railway.app/v1/your-endpoint

# Using Railway CLI
railway login --token $RAILWAY_TOKEN
railway up
```

### Example: Deploy Docker Container
```bash
# Set your token
export RAILWAY_TOKEN="your-token-here"

# Deploy using Railway CLI
railway login --token $RAILWAY_TOKEN
railway link  # Link to your project
railway up    # Deploy your Docker container
```

## Security Best Practices

1. **Never commit tokens to version control** - Use environment variables or secret managers
2. **Use descriptive token names** - Name tokens based on their purpose (e.g., "CI/CD", "Local Dev", "Automation Script")
3. **Rotate tokens regularly** - Delete old tokens and create new ones periodically
4. **Limit token scope** - Use tokens only for their intended purpose
5. **Store securely** - Use password managers or secret management tools (e.g., GitHub Secrets, AWS Secrets Manager)
6. **Revoke compromised tokens** - If a token is exposed, delete it immediately and create a new one

## Token Format

Railway API tokens typically follow this format:
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Example: `f60a8bb1-4b21-47b1-9653-4cf518d2b...`

## Managing Tokens

- **View existing tokens**: List all tokens in your Railway account (names are visible, tokens are masked)
- **Delete tokens**: Use the trash icon next to any token to revoke access
- **Token visibility**: You can only see the full token value once when it's created

## Railway API Documentation

For more information on using Railway's API:
- [Railway API Documentation](https://docs.railway.app/reference/api)
- [Railway CLI Documentation](https://docs.railway.app/cli)

## Project Purpose

This project automates Railway deployments, particularly for running Docker containers using API tokens for authentication and management.
