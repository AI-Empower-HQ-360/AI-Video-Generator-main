"""
Workflow Scheduler Service
=========================

Handles scheduled execution of workflows using APScheduler.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio
from threading import Thread

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.jobstores.memory import MemoryJobStore
    from apscheduler.executors.pool import ThreadPoolExecutor
except ImportError:
    raise ImportError(
        "APScheduler is required for workflow scheduling. "
        "Install it with 'pip install APScheduler'."
    )

from models.database import db, WorkflowSchedule, WorkflowExecution
from services.workflow_engine import WorkflowExecutionEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowSchedulerService:
    """
    Service for scheduling and managing automated workflow executions
    """
    
    def __init__(self):
        # Configure APScheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        self.workflow_engine = WorkflowExecutionEngine()
        self.is_running = False
    
    def start(self):
        """Start the scheduler service"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Workflow scheduler service started")
            
            # Load and schedule existing schedules
            self._load_existing_schedules()
    
    def stop(self):
        """Stop the scheduler service"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Workflow scheduler service stopped")
    
    def create_schedule(self, schedule_data: Dict[str, Any]) -> str:
        """
        Create a new workflow schedule
        """
        try:
            # Create schedule record in database
            schedule = WorkflowSchedule(
                workflow_id=schedule_data['workflow_id'],
                name=schedule_data.get('name', 'Unnamed Schedule'),
                cron_expression=schedule_data.get('cron_expression'),
                timezone=schedule_data.get('timezone', 'UTC'),
                input_data=schedule_data.get('input_data', {}),
                max_runs=schedule_data.get('max_runs'),
                created_by=schedule_data.get('created_by')
            )
            
            db.session.add(schedule)
            db.session.flush()
            
            # Add job to scheduler
            job_id = f"workflow_schedule_{schedule.id}"
            
            if schedule.cron_expression:
                # Parse cron expression
                try:
                    trigger = CronTrigger.from_crontab(
                        schedule.cron_expression, 
                        timezone=schedule.timezone
                    )
                    
                    self.scheduler.add_job(
                        func=self._execute_scheduled_workflow,
                        trigger=trigger,
                        args=[schedule.id],
                        id=job_id,
                        name=f"Scheduled: {schedule.name}",
                        misfire_grace_time=300  # 5 minutes grace time
                    )
                    
                    # Calculate next run time
                    next_run = self.scheduler.get_job(job_id).next_run_time
                    schedule.next_run_at = next_run
                    
                except Exception as e:
                    logger.error(f"Invalid cron expression: {schedule.cron_expression} - {e}")
                    raise ValueError(f"Invalid cron expression: {e}")
            
            db.session.commit()
            
            logger.info(f"Created workflow schedule: {schedule.name} (ID: {schedule.id})")
            return schedule.id
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create workflow schedule: {e}")
            raise
    
    def update_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing workflow schedule
        """
        try:
            schedule = WorkflowSchedule.query.get(schedule_id)
            if not schedule:
                return False
            
            # Update schedule properties
            for key, value in updates.items():
                if hasattr(schedule, key):
                    setattr(schedule, key, value)
            
            # Update scheduler job if cron expression changed
            if 'cron_expression' in updates or 'timezone' in updates:
                job_id = f"workflow_schedule_{schedule_id}"
                
                # Remove existing job
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)
                
                # Add updated job
                if schedule.is_active and schedule.cron_expression:
                    trigger = CronTrigger.from_crontab(
                        schedule.cron_expression,
                        timezone=schedule.timezone
                    )
                    
                    self.scheduler.add_job(
                        func=self._execute_scheduled_workflow,
                        trigger=trigger,
                        args=[schedule_id],
                        id=job_id,
                        name=f"Scheduled: {schedule.name}"
                    )
                    
                    # Update next run time
                    next_run = self.scheduler.get_job(job_id).next_run_time
                    schedule.next_run_at = next_run
            
            # Handle activation/deactivation
            if 'is_active' in updates:
                job_id = f"workflow_schedule_{schedule_id}"
                
                if not schedule.is_active and self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)
                    schedule.next_run_at = None
                elif schedule.is_active and not self.scheduler.get_job(job_id) and schedule.cron_expression:
                    trigger = CronTrigger.from_crontab(
                        schedule.cron_expression,
                        timezone=schedule.timezone
                    )
                    
                    self.scheduler.add_job(
                        func=self._execute_scheduled_workflow,
                        trigger=trigger,
                        args=[schedule_id],
                        id=job_id,
                        name=f"Scheduled: {schedule.name}"
                    )
                    
                    next_run = self.scheduler.get_job(job_id).next_run_time
                    schedule.next_run_at = next_run
            
            db.session.commit()
            
            logger.info(f"Updated workflow schedule: {schedule_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update workflow schedule {schedule_id}: {e}")
            return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """
        Delete a workflow schedule
        """
        try:
            schedule = WorkflowSchedule.query.get(schedule_id)
            if not schedule:
                return False
            
            # Remove job from scheduler
            job_id = f"workflow_schedule_{schedule_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Delete from database
            db.session.delete(schedule)
            db.session.commit()
            
            logger.info(f"Deleted workflow schedule: {schedule_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete workflow schedule {schedule_id}: {e}")
            return False
    
    def schedule_one_time_execution(self, workflow_id: str, run_at: datetime, 
                                  input_data: Dict[str, Any] = None, 
                                  created_by: str = None) -> str:
        """
        Schedule a one-time workflow execution
        """
        try:
            # Create temporary schedule record
            schedule = WorkflowSchedule(
                workflow_id=workflow_id,
                name=f"One-time execution at {run_at.isoformat()}",
                timezone='UTC',
                input_data=input_data or {},
                max_runs=1,
                created_by=created_by,
                is_active=True
            )
            
            db.session.add(schedule)
            db.session.flush()
            
            # Schedule one-time job
            job_id = f"workflow_onetime_{schedule.id}"
            
            self.scheduler.add_job(
                func=self._execute_scheduled_workflow,
                trigger=DateTrigger(run_date=run_at, timezone='UTC'),
                args=[schedule.id],
                id=job_id,
                name=f"One-time: {workflow_id}"
            )
            
            schedule.next_run_at = run_at
            db.session.commit()
            
            logger.info(f"Scheduled one-time workflow execution: {workflow_id} at {run_at}")
            return schedule.id
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to schedule one-time execution: {e}")
            raise
    
    def get_schedule_status(self, schedule_id: str) -> Dict[str, Any]:
        """
        Get status information for a schedule
        """
        schedule = WorkflowSchedule.query.get(schedule_id)
        if not schedule:
            return {}
        
        job_id = f"workflow_schedule_{schedule_id}"
        job = self.scheduler.get_job(job_id)
        
        return {
            'schedule': schedule.to_dict(),
            'job_active': job is not None,
            'next_run_time': job.next_run_time.isoformat() if job and job.next_run_time else None,
            'job_status': 'active' if job else 'inactive'
        }
    
    def _load_existing_schedules(self):
        """
        Load and schedule existing active schedules from database
        """
        try:
            active_schedules = WorkflowSchedule.query.filter_by(is_active=True).all()
            
            for schedule in active_schedules:
                if schedule.cron_expression:
                    try:
                        job_id = f"workflow_schedule_{schedule.id}"
                        
                        # Skip if max runs reached
                        if schedule.max_runs and schedule.run_count >= schedule.max_runs:
                            schedule.is_active = False
                            continue
                        
                        trigger = CronTrigger.from_crontab(
                            schedule.cron_expression,
                            timezone=schedule.timezone
                        )
                        
                        self.scheduler.add_job(
                            func=self._execute_scheduled_workflow,
                            trigger=trigger,
                            args=[schedule.id],
                            id=job_id,
                            name=f"Scheduled: {schedule.name}"
                        )
                        
                        # Update next run time
                        next_run = self.scheduler.get_job(job_id).next_run_time
                        schedule.next_run_at = next_run
                        
                        logger.info(f"Loaded workflow schedule: {schedule.name}")
                        
                    except Exception as e:
                        logger.error(f"Failed to load schedule {schedule.id}: {e}")
                        schedule.is_active = False
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to load existing schedules: {e}")
    
    def _execute_scheduled_workflow(self, schedule_id: str):
        """
        Execute a scheduled workflow
        """
        try:
            schedule = WorkflowSchedule.query.get(schedule_id)
            if not schedule:
                logger.error(f"Schedule {schedule_id} not found")
                return
            
            logger.info(f"Executing scheduled workflow: {schedule.name}")
            
            # Execute workflow in a new thread to avoid blocking the scheduler
            def run_workflow():
                try:
                    # Create new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Execute workflow
                    execution_id = loop.run_until_complete(
                        self.workflow_engine.execute_workflow(
                            workflow_id=schedule.workflow_id,
                            input_data=schedule.input_data,
                            user_id=schedule.created_by,
                            trigger_type='scheduled'
                        )
                    )
                    
                    # Update schedule statistics
                    schedule.last_run_at = datetime.utcnow()
                    schedule.last_run_status = 'success'
                    schedule.run_count += 1
                    
                    # Check if max runs reached
                    if schedule.max_runs and schedule.run_count >= schedule.max_runs:
                        schedule.is_active = False
                        
                        # Remove job from scheduler
                        job_id = f"workflow_schedule_{schedule_id}"
                        if self.scheduler.get_job(job_id):
                            self.scheduler.remove_job(job_id)
                        
                        logger.info(f"Schedule {schedule.name} completed max runs ({schedule.max_runs})")
                    
                    db.session.commit()
                    
                    logger.info(f"Scheduled workflow execution completed: {execution_id}")
                    
                except Exception as e:
                    # Update schedule with failure status
                    schedule.last_run_at = datetime.utcnow()
                    schedule.last_run_status = 'failed'
                    db.session.commit()
                    
                    logger.error(f"Scheduled workflow execution failed: {e}")
                
                finally:
                    loop.close()
            
            # Run in separate thread
            thread = Thread(target=run_workflow)
            thread.start()
            
        except Exception as e:
            logger.error(f"Failed to execute scheduled workflow {schedule_id}: {e}")
    
    def get_running_jobs(self) -> list:
        """
        Get list of currently running scheduled jobs
        """
        if not self.is_running:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return jobs
    
    def pause_schedule(self, schedule_id: str) -> bool:
        """
        Pause a schedule temporarily
        """
        try:
            job_id = f"workflow_schedule_{schedule_id}"
            job = self.scheduler.get_job(job_id)
            
            if job:
                self.scheduler.pause_job(job_id)
                
                # Update schedule in database
                schedule = WorkflowSchedule.query.get(schedule_id)
                if schedule:
                    schedule.is_active = False
                    db.session.commit()
                
                logger.info(f"Paused workflow schedule: {schedule_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to pause schedule {schedule_id}: {e}")
            return False
    
    def resume_schedule(self, schedule_id: str) -> bool:
        """
        Resume a paused schedule
        """
        try:
            job_id = f"workflow_schedule_{schedule_id}"
            job = self.scheduler.get_job(job_id)
            
            if job:
                self.scheduler.resume_job(job_id)
                
                # Update schedule in database
                schedule = WorkflowSchedule.query.get(schedule_id)
                if schedule:
                    schedule.is_active = True
                    db.session.commit()
                
                logger.info(f"Resumed workflow schedule: {schedule_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resume schedule {schedule_id}: {e}")
            return False


# Global scheduler instance
workflow_scheduler = WorkflowSchedulerService()


def start_scheduler():
    """Start the global workflow scheduler"""
    workflow_scheduler.start()


def stop_scheduler():
    """Stop the global workflow scheduler"""
    workflow_scheduler.stop()


# Scheduler management functions
def create_cron_schedule(workflow_id: str, cron_expression: str, 
                        name: str = None, input_data: Dict[str, Any] = None,
                        timezone: str = 'UTC', max_runs: int = None,
                        created_by: str = None) -> str:
    """
    Convenience function to create a cron-based schedule
    """
    schedule_data = {
        'workflow_id': workflow_id,
        'name': name or f'Cron schedule for {workflow_id}',
        'cron_expression': cron_expression,
        'timezone': timezone,
        'input_data': input_data or {},
        'max_runs': max_runs,
        'created_by': created_by
    }
    
    return workflow_scheduler.create_schedule(schedule_data)


def create_interval_schedule(workflow_id: str, interval_seconds: int,
                           name: str = None, input_data: Dict[str, Any] = None,
                           max_runs: int = None, created_by: str = None) -> str:
    """
    Create an interval-based schedule (every X seconds)
    """
    # Convert to cron expression (simplified)
    if interval_seconds >= 3600:  # 1 hour or more
        hours = interval_seconds // 3600
        cron_expression = f"0 */{hours} * * *"
    elif interval_seconds >= 60:  # 1 minute or more
        minutes = interval_seconds // 60
        cron_expression = f"*/{minutes} * * * *"
    else:
        # For very short intervals, use every minute (minimum practical interval)
        cron_expression = "* * * * *"
    
    return create_cron_schedule(
        workflow_id=workflow_id,
        cron_expression=cron_expression,
        name=name or f'Interval schedule for {workflow_id}',
        input_data=input_data,
        max_runs=max_runs,
        created_by=created_by
    )


def create_daily_schedule(workflow_id: str, hour: int = 9, minute: int = 0,
                         name: str = None, input_data: Dict[str, Any] = None,
                         created_by: str = None) -> str:
    """
    Create a daily schedule at specified time
    """
    cron_expression = f"{minute} {hour} * * *"
    
    return create_cron_schedule(
        workflow_id=workflow_id,
        cron_expression=cron_expression,
        name=name or f'Daily schedule for {workflow_id}',
        input_data=input_data,
        created_by=created_by
    )


def create_weekly_schedule(workflow_id: str, day_of_week: int = 1, 
                          hour: int = 9, minute: int = 0,
                          name: str = None, input_data: Dict[str, Any] = None,
                          created_by: str = None) -> str:
    """
    Create a weekly schedule (0=Sunday, 6=Saturday)
    """
    cron_expression = f"{minute} {hour} * * {day_of_week}"
    
    return create_cron_schedule(
        workflow_id=workflow_id,
        cron_expression=cron_expression,
        name=name or f'Weekly schedule for {workflow_id}',
        input_data=input_data,
        created_by=created_by
    )