#!/usr/bin/env python3
"""
Upload workflow notebooks to Databricks Workspace
Uploads Python scripts as notebooks to /Workspace/cdp-workflows/
"""

import os
from pathlib import Path
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ImportFormat

def upload_notebooks():
    """Upload workflow notebooks to Databricks Workspace"""
    w = WorkspaceClient()
    
    # Source directory
    source_dir = Path(__file__).parent / "workflows"
    
    # Target directory in Workspace
    target_dir = "/Workspace/cdp-workflows"
    
    # Create target directory if it doesn't exist
    try:
        w.workspace.mkdirs(path=target_dir)
        print(f"✓ Created directory: {target_dir}")
    except Exception as e:
        if "already exists" not in str(e).lower():
            print(f"Directory exists or error: {e}")
    
    # Notebooks to upload (including helper)
    notebooks = [
        "_import_helper.py",
        "journey_orchestrator.py",
        "identity_resolution.py",
        "scheduled_deliveries.py",
        "feature_sync.py"
    ]
    
    uploaded = []
    for notebook_file in notebooks:
        source_path = source_dir / notebook_file
        # Remove .py extension for notebook name
        notebook_name = notebook_file.replace('.py', '')
        target_path = f"{target_dir}/{notebook_name}"
        
        if not source_path.exists():
            print(f"⚠️  Skipping {notebook_file} - file not found")
            continue
        
        try:
            # Read Python file content
            with open(source_path, 'r') as f:
                content = f.read()
            
            # Upload as Python notebook (SOURCE format)
            w.workspace.import_(
                path=target_path,
                content=content.encode('utf-8'),
                format=ImportFormat.SOURCE,
                language="PYTHON",
                overwrite=True
            )
            
            print(f"✓ Uploaded: {target_path}")
            uploaded.append(target_path)
        except Exception as e:
            print(f"❌ Error uploading {notebook_file}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Uploaded {len(uploaded)} notebooks to: {target_dir}")
    print("\n📋 Uploaded notebooks:")
    for path in uploaded:
        print(f"   • {path}")
    
    print("\n💡 Next steps:")
    print("   1. Verify notebooks exist in Databricks Workspace")
    print("   2. Run: python backend/scripts/deploy_workflows.py")
    print("   3. Workflows will use /Workspace/cdp-workflows/* paths")

if __name__ == "__main__":
    upload_notebooks()

