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

def deploy_workflows():
    """Deploy all workflows to Databricks"""
    w = WorkspaceClient()
    
    workflows = [
        {
            "name": "journey_orchestrator",
            "description": "Process customer journey states and advance customers through journeys",
            "schedule": "0 */5 * * * ?",  # Every 5 minutes
            "notebook_path": "/Workspace/Repos/cdp-demo/backend/scripts/workflows/journey_orchestrator",
            "timeout": 3600,
            "task_key": "process_journey_states",
            "base_parameters": {"tenant_id": "demo_tenant"}
        },
        {
            "name": "identity_resolution",
            "description": "Process clickstream events and create match groups for identity resolution",
            "schedule": "0 0 */4 * * ?",  # Every 4 hours
            "notebook_path": "/Workspace/Repos/cdp-demo/backend/scripts/workflows/identity_resolution",
            "timeout": 3600,
            "task_key": "run_identity_resolution",
            "base_parameters": {"tenant_id": "demo_tenant"}
        },
        {
            "name": "scheduled_deliveries",
            "description": "Process scheduled message deliveries and send them",
            "schedule": "0 */5 * * * ?",  # Every 5 minutes
            "notebook_path": "/Workspace/Repos/cdp-demo/backend/scripts/workflows/scheduled_deliveries",
            "timeout": 1800,
            "task_key": "process_scheduled_deliveries",
            "base_parameters": {"tenant_id": "demo_tenant"}
        },
        {
            "name": "feature_sync",
            "description": "Sync customer features for ML serving",
            "schedule": "0 */15 * * * ?",  # Every 15 minutes
            "notebook_path": "/Workspace/Repos/cdp-demo/backend/scripts/workflows/feature_sync",
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
    print("\n📋 Deployed workflows:")
    for workflow in workflows:
        print(f"   • {workflow['name']} - {workflow['description']}")
        print(f"     Schedule: {workflow['schedule']}")

if __name__ == "__main__":
    deploy_workflows()

