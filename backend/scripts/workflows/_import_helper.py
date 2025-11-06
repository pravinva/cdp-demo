"""
Common import helper for Databricks workflow notebooks
Handles finding the backend code whether running from repo or workspace
"""

import sys
import os

def setup_imports():
    """Setup Python path to find backend app code"""
    # Try multiple approaches to find backend code
    
    # Approach 1: If running from repo (dbutils available)
    try:
        import dbutils
        repo_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
        if '/Repos/' in repo_path:
            # Extract repo root: /Repos/user/repo-name
            parts = repo_path.split('/Repos/')[1].split('/')
            if len(parts) >= 2:
                repo_root = f'/Workspace/Repos/{parts[0]}/{parts[1]}'
                backend_path = os.path.join(repo_root, 'backend')
                if os.path.exists(backend_path):
                    sys.path.insert(0, backend_path)
                    print(f"✓ Found backend at: {backend_path}")
                    return
        elif '/Users/' in repo_path:
            # Extract user folder path: /Users/user@domain.com/repo-name
            parts = repo_path.split('/Users/')[1].split('/')
            if len(parts) >= 2:
                user_repo_path = f'/Workspace/Users/{parts[0]}/{parts[1]}'
                backend_path = os.path.join(user_repo_path, 'backend')
                if os.path.exists(backend_path):
                    sys.path.insert(0, backend_path)
                    print(f"✓ Found backend at: {backend_path}")
                    return
    except:
        pass
    
    # Approach 2: Try common workspace paths
    common_paths = [
        '/Workspace/Users/pravin.varma@databricks.com/cdp-demo/backend',
        '/Workspace/Repos/cdp-demo/backend',
        '/Workspace/cdp-demo/backend',
        '/Workspace/cdp-workflows/../backend',
        os.path.join(os.path.dirname(__file__), '../../backend') if '__file__' in globals() else None
    ]
    
    for path in common_paths:
        if path and os.path.exists(path):
            abs_path = os.path.abspath(path)
            sys.path.insert(0, abs_path)
            print(f"✓ Found backend at: {abs_path}")
            return
    
    # Approach 3: If backend is installed as package
    try:
        import app
        print("✓ Backend available as installed package")
        return
    except ImportError:
        pass
    
    print("⚠️  Warning: Could not find backend code. Some imports may fail.")
    print("   Make sure backend code is accessible or install as package.")

# Auto-setup on import
setup_imports()

