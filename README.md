# Railway Automation

Automate Railway deployments and manage your Railway account programmatically using Railway API tokens.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your workspace token
export RAILWAY_TOKEN="your-workspace-token-here"

# Create project and deploy Docker container
python railway_deploy.py "My Project" "nginx:latest"
```

See the [Python Automation Script](#python-automation-script) section for detailed usage.

## What is a Railway API Token?

A Railway API token is an authentication credential that allows you to programmatically access and manage your Railway account without using the web interface. It enables you to:

- Deploy applications and Docker containers
- Manage projects and services
- Access Railway's REST API
- Automate deployments and infrastructure management
- Integrate Railway with CI/CD pipelines
- Run automated scripts and tools

## Token Types: Workspace vs Project Tokens

Railway offers two types of API tokens with different scopes and capabilities:

### Workspace-Based Tokens (Account-Level)

**Location**: Account Settings → Tokens (`railway.com/account/tokens`)

**Scope**: Workspace-wide or account-wide access

**Capabilities**:
- ✅ Access **all projects** within the specified workspace
- ✅ Manage multiple projects simultaneously
- ✅ Full workspace administration (projects, services, environments)
- ✅ Can create, delete, and modify projects
- ✅ Access workspace-level settings and configurations
- ✅ Manage workspace members and permissions (depending on your role)
- ✅ View usage and billing information for the workspace
- ✅ Can be scoped to "No workspace" for account-level access across all workspaces

**Use Cases**:
- CI/CD pipelines that deploy to multiple projects
- Automation tools managing multiple services
- Admin scripts that need broad access
- Workspace-level monitoring and management tools

**Security Consideration**: Higher risk - if compromised, can affect all projects in the workspace.

### Project-Based Tokens (Project-Level)

**Location**: Project Settings → Tokens (`railway.com/project/.../settings/tokens`)

**Scope**: Limited to a specific project and environment

**Capabilities**:
- ✅ Access **only the specific project** it was created for
- ✅ Access to **project environment variables** for the specified environment
- ✅ Deploy services within that project
- ✅ View logs and observability data for that project
- ✅ Limited to the selected environment (e.g., "production", "staging")
- ❌ Cannot access other projects
- ❌ Cannot modify project settings or workspace configurations
- ❌ Cannot manage workspace members or billing

**Use Cases**:
- Single-project deployments
- Environment-specific automation (production-only scripts)
- Third-party integrations for a specific project
- Limited-scope CI/CD pipelines
- Service monitoring for one project

**Security Consideration**: Lower risk - if compromised, only affects one project/environment.

### Key Differences Summary

| Feature | Workspace Token | Project Token |
|---------|----------------|---------------|
| **Access Scope** | All projects in workspace | Single project only |
| **Environment Access** | All environments | One specific environment |
| **Project Management** | Can create/delete projects | Cannot modify project settings |
| **Workspace Settings** | Full access | No access |
| **Environment Variables** | All projects/variables | Only project/environment variables |
| **Security Risk** | Higher (broader access) | Lower (limited scope) |
| **Best For** | Multi-project automation | Single-project deployments |

### Which Token Should You Use?

- **Use Workspace Tokens** when:
  - You need to manage multiple projects
  - Building automation that works across services
  - You require workspace-level administrative access
  - Running CI/CD for multiple projects

- **Use Project Tokens** when:
  - Working with a single project
  - You need least-privilege security (principle of least privilege)
  - Integrating third-party services for one project
  - Deploying to a specific environment only

## Obtaining an API Token

### Workspace-Based Token

1. **Via Web Interface**:
   - Log in to [railway.app](https://railway.app)
   - Click on your workspace name (top left)
   - Navigate to **Account** → **Tokens** (`railway.com/account/tokens`)
   - Enter a token name (e.g., "CI/CD Pipeline", "Automation Script")
   - Select the workspace scope (or "No workspace" for account-wide access)
   - Click **"Create"**
   - Copy the token immediately (you'll only see it once) and store it securely

### Project-Based Token

1. **Via Web Interface**:
   - Navigate to your project in Railway
   - Go to **Settings** → **Tokens** (`railway.com/project/.../settings/tokens`)
   - Enter a token name (e.g., "Production Deploy", "Staging Integration")
   - Select the target environment (e.g., "production", "staging")
   - Click **"Create"**
   - Copy the token immediately (you'll only see it once) and store it securely

### Via Mobile App

- Open the Railway mobile app
- Navigate to the **Tokens** section (purple key icon)
- Tap **"New Token"** to generate a new token
- Select the scope (workspace or project) if applicable
- Copy the token immediately (you'll only see it once)
- Store it securely

## Using the Token

> **Note**: Both workspace and project tokens are used the same way from a technical standpoint. The difference is in their access scope - workspace tokens can access multiple projects, while project tokens are limited to one project/environment.

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

1. **Use the least privilege principle** - Prefer project tokens over workspace tokens when possible. Only use workspace tokens when you need access to multiple projects.
2. **Never commit tokens to version control** - Use environment variables or secret managers
3. **Use descriptive token names** - Name tokens based on their purpose (e.g., "CI/CD", "Production Deploy", "Staging Integration")
4. **Rotate tokens regularly** - Delete old tokens and create new ones periodically
5. **Limit token scope** - Use tokens only for their intended purpose. For single-project deployments, use project tokens.
6. **Store securely** - Use password managers or secret management tools (e.g., GitHub Secrets, AWS Secrets Manager, environment variables)
7. **Revoke compromised tokens** - If a token is exposed, delete it immediately and create a new one
8. **Use environment-specific project tokens** - When using project tokens, scope them to specific environments (production, staging) for better security isolation

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

## Python Automation Script

This repository includes a Python script (`railway_deploy.py`) that uses a workspace-level token to create a Railway project and deploy a Docker container programmatically.

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your Railway workspace token**:
   
   **Linux/Mac:**
   ```bash
   export RAILWAY_TOKEN="your-workspace-token-here"
   ```
   
   **Windows (PowerShell):**
   ```powershell
   $env:RAILWAY_TOKEN="your-workspace-token-here"
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   set RAILWAY_TOKEN=your-workspace-token-here
   ```

### Usage

#### Basic Usage

Create a project and deploy a Docker container with default settings:
```bash
python railway_deploy.py
```

This will:
- Create a project named "My Docker Project"
- Deploy the `kennethreitz/httpbin` Docker image

#### Custom Project Name and Docker Image

```bash
python railway_deploy.py "My Custom Project" "nginx:latest"
```

#### Full Customization

```bash
python railway_deploy.py "My Project" "redis:alpine" "my-redis-service"
```

#### Using Environment Variables

You can also set default values via environment variables:
```bash
export RAILWAY_TOKEN="your-token"
export RAILWAY_PROJECT_NAME="My Project"
export RAILWAY_DOCKER_IMAGE="nginx:latest"
export RAILWAY_SERVICE_NAME="web-server"

python railway_deploy.py
```

### Example Docker Images

The script supports any Docker image from supported registries:
- `kennethreitz/httpbin` - Simple HTTP request testing service
- `nginx:latest` - Nginx web server
- `redis:alpine` - Redis cache
- `postgres:15` - PostgreSQL database
- `ghcr.io/username/repo:tag` - GitHub Container Registry
- `quay.io/username/repo:tag` - Quay.io registry
- `registry.gitlab.com/username/repo:tag` - GitLab registry

### Script Features

- ✅ **Create projects** programmatically using workspace-level tokens
- ✅ **Deploy Docker containers** from any supported registry
- ✅ **Error handling** with clear error messages
- ✅ **Environment variable support** for configuration
- ✅ **Command-line arguments** for flexibility
- ✅ **GraphQL API integration** with Railway's v2 API

### Code Structure

The `railway_deploy.py` script includes:

- **`RailwayClient` class**: Handles all Railway API interactions
  - `create_project()`: Creates a new Railway project
  - `deploy_docker_image()`: Deploys a Docker image as a service
  - `get_project()`: Retrieves project information

### Troubleshooting

**Error: "RAILWAY_TOKEN environment variable not set"**
- Make sure you've exported/set the `RAILWAY_TOKEN` environment variable
- Verify your token is a workspace-level token (created at `/account/tokens`)

**Error: "GraphQL errors: Unauthorized"**
- Check that your token is valid and has workspace-level permissions
- Ensure the token hasn't been revoked

**Error: "Failed to create project"**
- Verify you have permission to create projects in your workspace
- Check your workspace has available resources/credits

## Project Purpose

This project automates Railway deployments, particularly for running Docker containers using API tokens for authentication and management.
