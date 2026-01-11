#!/usr/bin/env python3
"""
Set environment variables for an existing Railway service.

Usage:
    python set_env_vars.py <service_id> [env1=value1] [env2=value2]
    
    Or load from .env file:
    python set_env_vars.py <service_id>
"""

import os
import sys
from railway_deploy import RailwayClient

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except ImportError:
    pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python set_env_vars.py <service_id> [env1=value1] [env2=value2]")
        print("\nExample:")
        print("  python set_env_vars.py 12f42d41-0842-45e1-a423-74c64973d925")
        print("  python set_env_vars.py 12f42d41-0842-45e1-a423-74c64973d925 STREAM_KEY=d13z-2397-59gt-21d9-8sez YouTube_ID=4UTdZpN26Bs")
        sys.exit(1)
    
    service_id = sys.argv[1]
    
    # Get API token
    api_token = os.getenv("RAILWAY_TOKEN")
    if not api_token:
        print("❌ Error: RAILWAY_TOKEN environment variable not set")
        print("Please set it in your .env file or as an environment variable")
        sys.exit(1)
    
    # Collect environment variables
    env_vars = {}
    
    # Load from .env file
    stream_key = os.getenv("STREAM_KEY")
    youtube_id = os.getenv("YouTube_ID") or os.getenv("YOUTUBE_ID")
    
    if stream_key:
        env_vars["STREAM_KEY"] = stream_key
    if youtube_id:
        env_vars["YouTube_ID"] = youtube_id
    
    # Override with command line arguments
    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            env_vars[key] = value
    
    if not env_vars:
        print("❌ No environment variables to set")
        print("Set them in .env file or pass as arguments: KEY=value")
        sys.exit(1)
    
    print(f"Setting environment variables for service: {service_id}")
    print(f"   Variables to set: {', '.join(env_vars.keys())}")
    
    try:
        client = RailwayClient(api_token)
        success = client.set_environment_variables(
            service_id=service_id,
            environment_variables=env_vars
        )
        
        if success:
            print("\n[OK] Environment variables set successfully!")
            print("[Note] Service will automatically redeploy with new variables.")
        else:
            print("\n[ERROR] Failed to set environment variables")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

