# Railway Automation

Automatically deploy Docker containers to Railway with environment variables configured.

## Prerequisites

- Python 3.7+
- Railway account ([Sign up here](https://railway.app))
- Railway workspace-level API token

## Installation

1. **Clone this repository:**
   ```bash
   git clone <repository-url>
   cd railway-automation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Setup

### Step 1: Get Your Variables

#### 1. Railway Token (Required)
- Go to [Railway Account Tokens](https://railway.app/account/tokens)
- Click **"New Token"**
- Enter a name (e.g., "Automation Script")
- Select workspace scope
- Click **"Create"**
- Copy the token immediately (you'll only see it once)
- This is your `RAILWAY_TOKEN`

#### 2. Project Name (Optional)
- Choose any name for your Railway project
- Default: "Live Stream"
- This is your `RAILWAY_PROJECT_NAME`

#### 3. Docker Image (Required)
- Use any public Docker image from Docker Hub
- Example: `imvickykumar999/stream-downloader`
- Alternative: `imvickykumar999/youtube-stream`
- This is your `RAILWAY_DOCKER_IMAGE`

#### 4. Stream Key (Optional - for streaming services)
- Go to [YouTube Studio Livestreaming](https://studio.youtube.com/channel/UC/livestreaming)
- Create a stream or get your existing stream key
- Copy the stream key
- This is your `STREAM_KEY`

#### 5. YouTube ID (Optional - for YouTube streaming)
- From any YouTube video URL: `https://www.youtube.com/watch?v=VIDEO_ID`
- Extract the `VIDEO_ID` part (e.g., `4UTdZpN26Bs` from `https://www.youtube.com/watch?v=4UTdZpN26Bs`)
- This is your `YouTube_ID`

### Step 2: Create `.env` File

1. **Copy the example file:**
   ```bash
   cp example.env .env
   ```

2. **Edit `.env` file and fill in your values:**
   ```env
   RAILWAY_TOKEN=your-token-here
   RAILWAY_PROJECT_NAME=Live Stream
   RAILWAY_DOCKER_IMAGE=imvickykumar999/stream-downloader
   STREAM_KEY=your-stream-key-here
   YouTube_ID=4UTdZpN26Bs
   ```

## Usage

### Deploy a New Project with Docker Container

**Basic command:**
```bash
python railway_deploy.py
```

This will:
- Create a new Railway project (name from `.env`)
- Deploy the Docker image (from `.env`)
- Set environment variables (STREAM_KEY, YouTube_ID from `.env`)

**Custom project and image:**
```bash
python railway_deploy.py "My Project" "nginx:latest"
```

**Full customization:**
```bash
python railway_deploy.py "My Project" "nginx:latest" "my-service"
```

### Set Environment Variables on Existing Service

If you need to update environment variables on an existing service:

1. **Find your service ID:**
   ```bash
   python list_services.py <project_id>
   ```

2. **Set environment variables:**
   ```bash
   python set_env_vars.py <service_id>
   ```

   Or with specific values:
   ```bash
   python set_env_vars.py <service_id> STREAM_KEY=value YouTube_ID=value
   ```

## Example Workflow

1. **Get your Railway token:**
   - Visit: https://railway.app/account/tokens
   - Create a new token and copy it

2. **Setup `.env` file:**
   ```bash
   cp example.env .env
   # Edit .env and add your RAILWAY_TOKEN
   ```

3. **Deploy:**
   ```bash
   python railway_deploy.py
   ```

4. **Check your deployment:**
   - Visit: https://railway.app
   - Check your project dashboard

## Troubleshooting

**Error: "RAILWAY_TOKEN environment variable not set"**
- Make sure you created a `.env` file
- Verify the token is set in `.env`
- Check for typos in variable names

**Error: "Free plan resource provision limit exceeded"**
- You've reached Railway's free tier limit
- Wait 30 seconds between project creations
- Or upgrade your Railway plan

**Error: "Not Authorized"**
- Check that your token is a workspace-level token
- Verify the token hasn't been revoked
- Recreate the token if needed

**Service not starting:**
- Check that required environment variables are set
- Use `set_env_vars.py` to add missing variables
- Check Railway dashboard logs for errors

## Files

- `railway_deploy.py` - Main deployment script
- `set_env_vars.py` - Set environment variables on existing service
- `list_services.py` - List all services in a project
- `example.env` - Example environment file (copy to `.env`)
- `requirements.txt` - Python dependencies

## Support

- Railway Docs: https://docs.railway.app
- Railway API: https://docs.railway.app/reference/api

