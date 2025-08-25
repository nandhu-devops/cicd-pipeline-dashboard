#!/usr/bin/env python3
"""
Startup script for CI/CD Health Dashboard
"""

import sys
import os
from pathlib import Path

# Get the current working directory
current_dir = Path.cwd()
print(f"Current working directory: {current_dir}")

# Add the backend directory to Python path
backend_dir = current_dir / "backend"
sys.path.insert(0, str(backend_dir))

# Add the app directory to Python path
app_dir = backend_dir / "app"
sys.path.insert(0, str(app_dir))

print(f"Backend directory: {backend_dir}")
print(f"App directory: {app_dir}")
print(f"Python path: {sys.path[:3]}")

if __name__ == "__main__":
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
        
        print("🚀 Starting CI/CD Health Dashboard...")
        
        # Start the server from the current directory (not changing to backend)
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[str(backend_dir)]
        )
    except ImportError as e:
        print(f"❌ Failed to import uvicorn: {e}")
        print("Please install uvicorn: pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
