#!/usr/bin/env python3
"""
Deploy Databricks Workflows
Creates or updates workflows in Databricks workspace
"""

import sys
import os
from pathlib import Path
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import (
    Task,
    NotebookTask,
    JobEmailNotifications,
    CronSchedule,
    JobSettings
)

# Import config to get workflow schedule
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.config import get_settings

def deploy_workflows():
    """Deploy all workflows to Databricks"""
    w = WorkspaceClient()
    settings = get_settings()
    
    # Get schedule from config (default: once per day at midnight UTC)
    workflow_schedule = settings.WORKFLOW_SCHEDULE_CRON
    
    workflows = [
        {
            "name": "journey_orchestrator",
            "description": "Process customer journey states and advance customers through journeys",
            "schedule": workflow_schedule,  # Configurable via WORKFLOW_SCHEDULE_CRON
            "notebook_path": "/Workspace/Users/pravin.varma@databricks.com/cdp-demo/backend/scripts/workflows/journey_orchestrator",
            "timeout": 3600,
            "task_key": "process_journey_states",
            "base_parameters": {"tenant_id": "demo_tenant"}
        },
        {
            "name": "identity_resolution",
            "description": "Process clickstream events and create match groups for identity resolution",
            "schedule": workflow_schedule,  # Configurable via WORKFLOW_SCHEDULE_CRON
            "notebook_path": "/Workspace/Users/pravin.varma@databricks.com/cdp-demo/backend/scripts/workflows/identity_resolution",
            "timeout": 3600,
            "task_key": "run_identity_resolution",
            "base_parameters": {"tenant_id": "demo_tenant"}
        },
        {
            "name": "scheduled_deliveries",
            "description": "Process scheduled message deliveries and send them",
            "schedule": workflow_schedule,  # Configurable via WORKFLOW_SCHEDULE_CRON
            "notebook_path": "/Workspace/Users/pravin.varma@databricks.com/cdp-demo/backend/scripts/workflows/scheduled_deliveries",
            "timeout": 1800,
            "task_key": "process_scheduled_deliveries",
            "base_parameters": {"tenant_id": "demo_tenant"}
        },
        {
            "name": "feature_sync",
            "description": "Sync customer features for ML serving",
            "schedule": workflow_schedule,  # Configurable via WORKFLOW_SCHEDULE_CRON
            "notebook_path": "/Workspace/Users/pravin.varma@databricks.com/cdp-demo/backend/scripts/workflows/feature_sync",
            "timeout": 3600,
            "task_key": "sync_customer_features",
            "base_parameters": {"tenant_id": "demo_tenant"}
        }
    ]
    
    for workflow in workflows:
        try:
            # Check if job exists
            existing_jobs = [j for j in w.jobs.list() if j.settings and j.settings.name == workflow["name"]]
            
            notebook_task = NotebookTask(
                notebook_path=workflow["notebook_path"],
                base_parameters=workflow.get("base_parameters", {})
            )
            
            job_settings = JobSettings(
                name=workflow["name"],
                description=workflow["description"],
                tasks=[
                    Task(
                        task_key=workflow["task_key"],
                        notebook_task=notebook_task,
                        timeout_seconds=workflow["timeout"],
                        max_retries=2
                    )
                ],
                schedule=CronSchedule(
                    quartz_cron_expression=workflow["schedule"],
                    timezone_id="UTC"
                ),
                email_notifications=JobEmailNotifications(
                    on_failure=["${workflow.owner}"],
                    on_success=["${workflow.owner}"]
                ),
                max_concurrent_runs=1
            )
            
            if existing_jobs:
                # Update existing job
                job_id = existing_jobs[0].job_id
                print(f"📝 Updating workflow: {workflow['name']} (ID: {job_id})")
                w.jobs.update(job_id=job_id, new_settings=job_settings)
                print(f"   ✅ Updated successfully")
            else:
                # Create new job - pass JobSettings fields as individual keyword arguments
                print(f"🆕 Creating workflow: {workflow['name']}")
                job = w.jobs.create(
                    name=job_settings.name,
                    description=job_settings.description,
                    tasks=job_settings.tasks,
                    schedule=job_settings.schedule,
                    email_notifications=job_settings.email_notifications,
                    max_concurrent_runs=job_settings.max_concurrent_runs
                )
                print(f"   ✅ Created with ID: {job.job_id}")
        
        except Exception as e:
            print(f"❌ Error deploying {workflow['name']}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✅ Workflow deployment complete!")
    print(f"\n📅 Schedule: {workflow_schedule} (configurable via WORKFLOW_SCHEDULE_CRON)")
    print("\n📋 Deployed workflows:")
    for workflow in workflows:
        print(f"   • {workflow['name']} - {workflow['description']}")
        print(f"     Schedule: {workflow['schedule']}")

if __name__ == "__main__":
    deploy_workflows()

