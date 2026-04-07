import os
import logging
import requests
from flask import Flask, render_template_string, request, flash, redirect, url_for
from typing import Optional, Dict, Any

# --- Environment Loading ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Secret key for session/flash messages
app.secret_key = os.getenv("FLASK_SECRET", "railway-deploy-secret-god-mode-99")

# --- Railway API Client ---

class RailwayClient:
    """Client for interacting with Railway's GraphQL API."""
    
    API_ENDPOINT = "https://backboard.railway.app/graphql/v2"
    
    def __init__(self, api_token: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        })

    def _execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"query": query, "variables": variables or {}}
        try:
            response = self.session.post(self.API_ENDPOINT, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
                logger.error(f"GraphQL Error: {error_msg}")
                raise ValueError(error_msg)
            
            return data.get("data", {})
        except requests.exceptions.RequestException as e:
            logger.error(f"Network Error: {str(e)}")
            raise ConnectionError(f"Failed to connect to Railway API: {str(e)}")

    def create_project(self, name: str) -> str:
        mutation = """
        mutation CreateProject($input: ProjectCreateInput!) {
            projectCreate(input: $input) { id }
        }
        """
        result = self._execute(mutation, {"input": {"name": name}})
        return result["projectCreate"]["id"]

    def create_service(self, project_id: str, name: str, image: str) -> str:
        mutation = """
        mutation CreateService($input: ServiceCreateInput!) {
            serviceCreate(input: $input) { id }
        }
        """
        result = self._execute(mutation, {
            "input": {
                "projectId": project_id, 
                "name": name,
                "source": {"image": image}
            }
        })
        return result["serviceCreate"]["id"]

# --- God Level UI Template ---

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Deployer | Enterprise</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(circle at top left, #1e293b, #0f172a);
            color: #f8fafc;
            min-height: 100vh;
        }
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .input-glow:focus {
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
            border-color: #3b82f6;
        }
        .gradient-button {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .gradient-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
        }
        .loading-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.9);
            z-index: 50;
            backdrop-filter: blur(8px);
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body class="flex items-center justify-center p-4">

    <!-- Global Loading State -->
    <div id="loadingOverlay" class="loading-overlay">
        <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500 mb-6"></div>
        <h2 class="text-2xl font-bold tracking-tight text-white mb-2">Executing Deployment</h2>
        <p class="text-slate-400 text-sm max-w-xs">Provisioning infrastructure and establishing service connection...</p>
    </div>

    <div class="max-w-2xl w-full glass-card rounded-3xl overflow-hidden transition-all duration-500">
        <!-- Header -->
        <div class="px-8 py-10 border-b border-white/5 bg-white/5">
            <div class="flex items-center space-x-3 mb-2">
                <div class="p-2 bg-blue-500/20 rounded-xl">
                    <i data-lucide="rocket" class="w-6 h-6 text-blue-400"></i>
                </div>
                <h1 class="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                    Railway Deployer
                </h1>
            </div>
            <p class="text-slate-400 text-sm font-medium">Automated Enterprise Deployment Engine</p>
        </div>

        <form method="POST" action="/deploy" class="p-8 space-y-8" id="deployForm">
            <!-- Token Section -->
            <div class="space-y-2">
                <div class="flex items-center justify-between">
                    <label class="flex items-center space-x-2 text-xs font-bold uppercase tracking-widest text-blue-400">
                        <i data-lucide="shield-check" class="w-3 h-3"></i>
                        <span>Railway API Token</span>
                    </label>
                </div>
                <div class="relative">
                    <input type="password" name="railway_token" required placeholder="Paste your Workspace Token"
                           value="{{ default_token }}"
                           class="w-full bg-slate-900/50 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:outline-none input-glow transition-all duration-200">
                </div>
            </div>

            <!-- Project Details Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                    <label class="text-xs font-bold uppercase tracking-widest text-slate-400 px-1">Project Identifier</label>
                    <input type="text" name="project_name" required placeholder="Blog Forge" value="Blog Forge"
                           class="w-full bg-slate-900/50 border border-white/10 rounded-xl p-4 text-white focus:outline-none input-glow transition-all">
                </div>
                <div class="space-y-2">
                    <label class="text-xs font-bold uppercase tracking-widest text-slate-400 px-1">Registry Image</label>
                    <input type="text" name="docker_image" required value="imvickykumar999/blogforge"
                           class="w-full bg-slate-900/50 border border-white/10 rounded-xl p-4 text-white focus:outline-none input-glow transition-all">
                </div>
            </div>

            <!-- Service Details -->
            <div class="space-y-2 pb-4">
                <label class="text-xs font-bold uppercase tracking-widest text-slate-400 px-1">Service Label</label>
                <input type="text" name="service_name" placeholder="blogforge" value="blogforge"
                       class="w-full bg-slate-900/50 border border-white/10 rounded-xl p-4 text-white focus:outline-none input-glow transition-all">
            </div>

            <!-- Notifications -->
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                {% for category, message in messages %}
                  <div class="flex items-start p-4 rounded-xl text-sm leading-relaxed
                      {{ 'bg-red-500/10 text-red-400 border border-red-500/20' if category == 'error' else 'bg-green-500/10 text-green-400 border border-green-500/20' }}">
                    <i data-lucide="{{ 'alert-circle' if category == 'error' else 'check-circle' }}" class="w-4 h-4 mr-3 mt-0.5 shrink-0"></i>
                    <span>{{ message }}</span>
                  </div>
                {% endfor %}
              {% endif %}
            {% endwith %}

            <!-- Submit -->
            <button type="submit" id="submitBtn"
                    class="w-full gradient-button text-white font-bold py-5 rounded-2xl flex items-center justify-center space-x-3 text-lg shadow-xl">
                <span>Execute Launch Sequence</span>
                <i data-lucide="chevron-right" class="w-5 h-5"></i>
            </button>
        </form>
    </div>

    <script>
        lucide.createIcons();

        document.getElementById('deployForm').onsubmit = function() {
            document.getElementById('loadingOverlay').style.display = 'flex';
            const btn = document.getElementById('submitBtn');
            btn.disabled = true;
            btn.classList.add('opacity-50');
        };
    </script>
</body>
</html>
"""

# --- Routes ---

@app.route('/')
def index():
    default_token = os.getenv("RAILWAY_TOKEN", "")
    return render_template_string(INDEX_TEMPLATE, default_token=default_token)

@app.route('/deploy', methods=['POST'])
def deploy_action():
    token = request.form.get('railway_token') or os.getenv("RAILWAY_TOKEN")
    
    if not token:
        flash("Authorization failed: Token required.", "error")
        return redirect(url_for('index'))

    proj_name = request.form.get('project_name')
    image = request.form.get('docker_image')
    svc_name = request.form.get('service_name') or "web-service"

    try:
        client = RailwayClient(token)
        
        logger.info(f"Initiating project: {proj_name}")
        project_id = client.create_project(proj_name)
        
        logger.info(f"Mounting service: {svc_name}")
        client.create_service(project_id, svc_name, image)
        
        # Immediate redirect to the same tab
        return render_template_string("""
            <script>
                window.location.href = 'https://railway.app/project/{{ pid }}';
            </script>
        """, pid=project_id)

    except Exception as e:
        logger.exception("Deploy Failed")
        flash(str(e), "error")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
