"""
Workflow Automation Service
Manages automated workflows for video processing, content moderation, and system operations
"""

import os
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import asyncio
import threading
import time
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class WorkflowPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class WorkflowEngine:
    """
    Centralized workflow automation engine for spiritual content processing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workflows = {}
        self.active_jobs = {}
        self.job_queue = []
        self.workflow_history = []
        self.is_running = False
        self.engine_thread = None
        
        # Initialize built-in workflow templates
        self.workflow_templates = self._initialize_workflow_templates()
        
        # Performance tracking
        self.performance_metrics = {
            'total_workflows_executed': 0,
            'successful_workflows': 0,
            'failed_workflows': 0,
            'average_execution_time': 0,
            'last_execution_times': []
        }
    
    def _initialize_workflow_templates(self) -> Dict:
        """Initialize predefined workflow templates"""
        return {
            'video_processing_complete': {
                'name': 'Complete Video Processing Pipeline',
                'description': 'Full automated video processing with quality assessment, moderation, and thumbnail generation',
                'steps': [
                    {
                        'name': 'video_quality_assessment',
                        'service': 'video_quality_service',
                        'function': 'assess_video_quality',
                        'retry_count': 2,
                        'timeout': 300
                    },
                    {
                        'name': 'content_moderation',
                        'service': 'content_moderation_service',
                        'function': 'moderate_video_content',
                        'retry_count': 1,
                        'timeout': 120,
                        'depends_on': ['video_quality_assessment']
                    },
                    {
                        'name': 'thumbnail_generation',
                        'service': 'thumbnail_generation_service',
                        'function': 'generate_thumbnail',
                        'retry_count': 2,
                        'timeout': 180,
                        'depends_on': ['content_moderation']
                    },
                    {
                        'name': 'finalization',
                        'service': 'workflow_automation_service',
                        'function': 'finalize_video_processing',
                        'retry_count': 1,
                        'timeout': 60,
                        'depends_on': ['thumbnail_generation']
                    }
                ],
                'notification_settings': {
                    'on_completion': True,
                    'on_failure': True,
                    'on_step_failure': True
                }
            },
            'content_moderation_pipeline': {
                'name': 'Content Moderation Pipeline',
                'description': 'Automated content moderation with escalation for spiritual content',
                'steps': [
                    {
                        'name': 'initial_screening',
                        'service': 'content_moderation_service',
                        'function': 'moderate_content',
                        'retry_count': 1,
                        'timeout': 60
                    },
                    {
                        'name': 'spiritual_alignment_check',
                        'service': 'content_moderation_service',
                        'function': 'assess_spiritual_alignment',
                        'retry_count': 1,
                        'timeout': 90,
                        'depends_on': ['initial_screening']
                    },
                    {
                        'name': 'quality_enhancement_suggestions',
                        'service': 'content_moderation_service',
                        'function': 'generate_improvement_suggestions',
                        'retry_count': 1,
                        'timeout': 120,
                        'depends_on': ['spiritual_alignment_check']
                    }
                ]
            },
            'scheduled_quality_assessment': {
                'name': 'Scheduled Quality Assessment',
                'description': 'Regular quality assessment of existing content',
                'schedule': 'daily',
                'steps': [
                    {
                        'name': 'gather_content_list',
                        'service': 'workflow_automation_service',
                        'function': 'get_content_for_assessment',
                        'retry_count': 1,
                        'timeout': 60
                    },
                    {
                        'name': 'batch_quality_assessment',
                        'service': 'video_quality_service',
                        'function': 'batch_assess_videos',
                        'retry_count': 2,
                        'timeout': 600,
                        'depends_on': ['gather_content_list']
                    },
                    {
                        'name': 'generate_quality_report',
                        'service': 'video_quality_service',
                        'function': 'generate_quality_report',
                        'retry_count': 1,
                        'timeout': 120,
                        'depends_on': ['batch_quality_assessment']
                    }
                ]
            },
            'performance_optimization': {
                'name': 'Performance Optimization Workflow',
                'description': 'Automated performance testing and optimization',
                'schedule': 'weekly',
                'steps': [
                    {
                        'name': 'performance_baseline',
                        'service': 'performance_testing_service',
                        'function': 'establish_baseline',
                        'retry_count': 1,
                        'timeout': 300
                    },
                    {
                        'name': 'load_testing',
                        'service': 'performance_testing_service',
                        'function': 'run_load_tests',
                        'retry_count': 2,
                        'timeout': 600,
                        'depends_on': ['performance_baseline']
                    },
                    {
                        'name': 'optimization_recommendations',
                        'service': 'performance_testing_service',
                        'function': 'generate_optimization_recommendations',
                        'retry_count': 1,
                        'timeout': 180,
                        'depends_on': ['load_testing']
                    }
                ]
            }
        }
    
    def start_engine(self):
        """Start the workflow engine"""
        if not self.is_running:
            self.is_running = True
            self.engine_thread = threading.Thread(target=self._engine_loop, daemon=True)
            self.engine_thread.start()
            self.logger.info("Workflow engine started")
    
    def stop_engine(self):
        """Stop the workflow engine"""
        self.is_running = False
        if self.engine_thread:
            self.engine_thread.join(timeout=10)
        self.logger.info("Workflow engine stopped")
    
    def _engine_loop(self):
        """Main engine loop for processing workflows"""
        while self.is_running:
            try:
                self._process_job_queue()
                self._monitor_active_jobs()
                self._cleanup_completed_jobs()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                self.logger.error(f"Error in workflow engine loop: {str(e)}")
                time.sleep(10)  # Wait longer on error
    
    def create_workflow(self, workflow_config: Dict) -> str:
        """
        Create a new workflow from configuration
        
        Args:
            workflow_config: Workflow configuration dict
            
        Returns:
            Workflow ID
        """
        try:
            workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.workflows)}"
            
            workflow = {
                'id': workflow_id,
                'name': workflow_config.get('name', 'Unnamed Workflow'),
                'description': workflow_config.get('description', ''),
                'steps': workflow_config.get('steps', []),
                'status': WorkflowStatus.PENDING,
                'priority': WorkflowPriority(workflow_config.get('priority', 2)),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'metadata': workflow_config.get('metadata', {}),
                'notification_settings': workflow_config.get('notification_settings', {}),
                'schedule': workflow_config.get('schedule'),
                'execution_history': [],
                'current_step': 0,
                'step_results': {},
                'error_details': None
            }
            
            self.workflows[workflow_id] = workflow
            self.logger.info(f"Created workflow: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Error creating workflow: {str(e)}")
            raise
    
    def schedule_workflow(self, workflow_id: str, schedule_time: datetime = None, 
                         input_data: Dict = None) -> str:
        """
        Schedule a workflow for execution
        
        Args:
            workflow_id: ID of workflow to schedule
            schedule_time: When to run (None for immediate)
            input_data: Input data for the workflow
            
        Returns:
            Job ID
        """
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.job_queue)}"
            
            job = {
                'id': job_id,
                'workflow_id': workflow_id,
                'status': WorkflowStatus.PENDING,
                'scheduled_time': schedule_time or datetime.now(),
                'input_data': input_data or {},
                'created_at': datetime.now().isoformat(),
                'started_at': None,
                'completed_at': None,
                'execution_time': None,
                'step_results': {},
                'error_details': None
            }
            
            # Insert job in queue based on priority and schedule time
            self._insert_job_in_queue(job)
            
            self.logger.info(f"Scheduled workflow {workflow_id} as job {job_id}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Error scheduling workflow: {str(e)}")
            raise
    
    def _insert_job_in_queue(self, job: Dict):
        """Insert job in queue based on priority and schedule time"""
        workflow = self.workflows[job['workflow_id']]
        job_priority = workflow['priority'].value
        job_schedule = job['scheduled_time']
        
        # Find insertion point
        insertion_index = len(self.job_queue)
        for i, queued_job in enumerate(self.job_queue):
            queued_workflow = self.workflows[queued_job['workflow_id']]
            queued_priority = queued_workflow['priority'].value
            queued_schedule = queued_job['scheduled_time']
            
            # Higher priority jobs go first, then by schedule time
            if (job_priority > queued_priority or 
                (job_priority == queued_priority and job_schedule < queued_schedule)):
                insertion_index = i
                break
        
        self.job_queue.insert(insertion_index, job)
    
    def _process_job_queue(self):
        """Process jobs in the queue"""
        current_time = datetime.now()
        
        while self.job_queue:
            job = self.job_queue[0]
            
            # Check if job is ready to run
            if job['scheduled_time'] > current_time:
                break  # Jobs are ordered by schedule time
            
            # Check if we have capacity (limit active jobs)
            if len(self.active_jobs) >= 5:  # Max 5 concurrent workflows
                break
            
            # Remove from queue and start execution
            job = self.job_queue.pop(0)
            self._start_job_execution(job)
    
    def _start_job_execution(self, job: Dict):
        """Start executing a job"""
        try:
            job_id = job['id']
            job['status'] = WorkflowStatus.RUNNING
            job['started_at'] = datetime.now().isoformat()
            
            self.active_jobs[job_id] = job
            
            # Start job execution in a separate thread
            execution_thread = threading.Thread(
                target=self._execute_workflow_job,
                args=(job,),
                daemon=True
            )
            execution_thread.start()
            
            self.logger.info(f"Started execution of job {job_id}")
            
        except Exception as e:
            self.logger.error(f"Error starting job execution: {str(e)}")
            job['status'] = WorkflowStatus.FAILED
            job['error_details'] = str(e)
    
    def _execute_workflow_job(self, job: Dict):
        """Execute a workflow job"""
        job_id = job['id']
        workflow_id = job['workflow_id']
        workflow = self.workflows[workflow_id]
        
        try:
            start_time = datetime.now()
            
            # Execute workflow steps
            for step_index, step in enumerate(workflow['steps']):
                step_result = self._execute_workflow_step(job, step, step_index)
                job['step_results'][step['name']] = step_result
                
                if not step_result.get('success', False):
                    raise Exception(f"Step {step['name']} failed: {step_result.get('error', 'Unknown error')}")
            
            # Mark job as completed
            job['status'] = WorkflowStatus.COMPLETED
            job['completed_at'] = datetime.now().isoformat()
            job['execution_time'] = (datetime.now() - start_time).total_seconds()
            
            # Update performance metrics
            self._update_performance_metrics(job)
            
            # Send notifications if configured
            self._send_workflow_notifications(job, 'completion')
            
            self.logger.info(f"Workflow job {job_id} completed successfully")
            
        except Exception as e:
            job['status'] = WorkflowStatus.FAILED
            job['error_details'] = str(e)
            job['completed_at'] = datetime.now().isoformat()
            
            self._send_workflow_notifications(job, 'failure')
            self.logger.error(f"Workflow job {job_id} failed: {str(e)}")
        
        finally:
            # Move to history
            self.workflow_history.append(job.copy())
            # Keep only last 1000 history entries
            if len(self.workflow_history) > 1000:
                self.workflow_history = self.workflow_history[-1000:]
    
    def _execute_workflow_step(self, job: Dict, step: Dict, step_index: int) -> Dict:
        """Execute a single workflow step"""
        step_name = step['name']
        service_name = step['service']
        function_name = step['function']
        retry_count = step.get('retry_count', 0)
        timeout = step.get('timeout', 300)
        
        self.logger.info(f"Executing step {step_name} for job {job['id']}")
        
        # Check dependencies
        depends_on = step.get('depends_on', [])
        for dependency in depends_on:
            if dependency not in job['step_results']:
                return {
                    'success': False,
                    'error': f"Dependency {dependency} not found",
                    'timestamp': datetime.now().isoformat()
                }
            
            if not job['step_results'][dependency].get('success', False):
                return {
                    'success': False,
                    'error': f"Dependency {dependency} failed",
                    'timestamp': datetime.now().isoformat()
                }
        
        # Execute step with retries
        last_error = None
        for attempt in range(retry_count + 1):
            try:
                # Simulate step execution (would call actual service functions)
                result = self._simulate_step_execution(step, job['input_data'], job['step_results'])
                
                if result.get('success', False):
                    return {
                        'success': True,
                        'result': result,
                        'attempt': attempt + 1,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    last_error = result.get('error', 'Step execution failed')
                    
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Step {step_name} attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < retry_count:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return {
            'success': False,
            'error': last_error,
            'attempts': retry_count + 1,
            'timestamp': datetime.now().isoformat()
        }
    
    def _simulate_step_execution(self, step: Dict, input_data: Dict, previous_results: Dict) -> Dict:
        """Simulate step execution (would call actual service functions in real implementation)"""
        step_name = step['name']
        service_name = step['service']
        function_name = step['function']
        
        # Simulate processing time
        time.sleep(1)
        
        # Simulate different step types
        if 'quality_assessment' in step_name:
            return {
                'success': True,
                'quality_score': 85,
                'issues_found': ['minor_audio_quality'],
                'recommendations': ['improve_microphone_setup']
            }
        elif 'moderation' in step_name:
            return {
                'success': True,
                'approved': True,
                'confidence': 0.92,
                'flags': []
            }
        elif 'thumbnail' in step_name:
            return {
                'success': True,
                'thumbnail_path': '/tmp/generated_thumbnail.jpg',
                'quality_score': 88
            }
        elif 'performance' in step_name:
            return {
                'success': True,
                'response_time': 150,
                'throughput': 1200,
                'resource_usage': 65
            }
        else:
            return {
                'success': True,
                'message': f'{step_name} completed successfully'
            }
    
    def _monitor_active_jobs(self):
        """Monitor active jobs for timeouts and issues"""
        current_time = datetime.now()
        
        for job_id, job in list(self.active_jobs.items()):
            if job['status'] == WorkflowStatus.RUNNING:
                started_time = datetime.fromisoformat(job['started_at'])
                elapsed_time = (current_time - started_time).total_seconds()
                
                # Check for global timeout (30 minutes default)
                if elapsed_time > 1800:  # 30 minutes
                    job['status'] = WorkflowStatus.FAILED
                    job['error_details'] = "Workflow timeout exceeded"
                    job['completed_at'] = current_time.isoformat()
                    
                    self.logger.error(f"Job {job_id} timed out after {elapsed_time} seconds")
    
    def _cleanup_completed_jobs(self):
        """Clean up completed or failed jobs from active jobs"""
        completed_jobs = []
        
        for job_id, job in self.active_jobs.items():
            if job['status'] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                completed_jobs.append(job_id)
        
        for job_id in completed_jobs:
            del self.active_jobs[job_id]
    
    def _update_performance_metrics(self, job: Dict):
        """Update performance metrics based on completed job"""
        self.performance_metrics['total_workflows_executed'] += 1
        
        if job['status'] == WorkflowStatus.COMPLETED:
            self.performance_metrics['successful_workflows'] += 1
        else:
            self.performance_metrics['failed_workflows'] += 1
        
        # Track execution times
        if job.get('execution_time'):
            execution_times = self.performance_metrics['last_execution_times']
            execution_times.append(job['execution_time'])
            
            # Keep only last 100 execution times
            if len(execution_times) > 100:
                execution_times = execution_times[-100:]
                self.performance_metrics['last_execution_times'] = execution_times
            
            # Update average
            self.performance_metrics['average_execution_time'] = sum(execution_times) / len(execution_times)
    
    def _send_workflow_notifications(self, job: Dict, event_type: str):
        """Send notifications for workflow events"""
        workflow_id = job['workflow_id']
        workflow = self.workflows[workflow_id]
        notification_settings = workflow.get('notification_settings', {})
        
        if not notification_settings.get(f'on_{event_type}', False):
            return
        
        # Simulate notification (would integrate with actual notification systems)
        notification = {
            'type': event_type,
            'job_id': job['id'],
            'workflow_name': workflow['name'],
            'timestamp': datetime.now().isoformat(),
            'status': job['status'].value,
            'execution_time': job.get('execution_time'),
            'error_details': job.get('error_details')
        }
        
        self.logger.info(f"Notification sent for job {job['id']}: {event_type}")
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get current status of a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        # Find recent executions
        recent_executions = [
            job for job in self.workflow_history 
            if job['workflow_id'] == workflow_id
        ][-10:]  # Last 10 executions
        
        # Find active jobs
        active_jobs = [
            job for job in self.active_jobs.values()
            if job['workflow_id'] == workflow_id
        ]
        
        return {
            'workflow': workflow,
            'recent_executions': recent_executions,
            'active_jobs': active_jobs,
            'total_executions': len([j for j in self.workflow_history if j['workflow_id'] == workflow_id])
        }
    
    def get_system_metrics(self) -> Dict:
        """Get workflow engine performance metrics"""
        return {
            'engine_status': 'running' if self.is_running else 'stopped',
            'active_jobs_count': len(self.active_jobs),
            'queued_jobs_count': len(self.job_queue),
            'total_workflows': len(self.workflows),
            'performance_metrics': self.performance_metrics,
            'uptime': datetime.now().isoformat()
        }
    
    def create_workflow_from_template(self, template_name: str, custom_config: Dict = None) -> str:
        """Create workflow from predefined template"""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Template {template_name} not found")
        
        template = self.workflow_templates[template_name].copy()
        
        # Apply custom configuration if provided
        if custom_config:
            template.update(custom_config)
        
        return self.create_workflow(template)
    
    def get_available_templates(self) -> List[str]:
        """Get list of available workflow templates"""
        return list(self.workflow_templates.keys())


# Convenience functions
def create_automation_workflow(workflow_config: Dict) -> str:
    """Create a new automation workflow"""
    engine = WorkflowEngine()
    return engine.create_workflow(workflow_config)

def schedule_video_processing(video_path: str, content_type: str = "spiritual") -> str:
    """Schedule complete video processing workflow"""
    engine = WorkflowEngine()
    workflow_id = engine.create_workflow_from_template('video_processing_complete')
    
    input_data = {
        'video_path': video_path,
        'content_type': content_type
    }
    
    return engine.schedule_workflow(workflow_id, input_data=input_data)

def schedule_daily_quality_assessment() -> str:
    """Schedule daily quality assessment workflow"""
    engine = WorkflowEngine()
    workflow_id = engine.create_workflow_from_template('scheduled_quality_assessment')
    
    # Schedule for next day at 2 AM
    tomorrow_2am = datetime.now().replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    return engine.schedule_workflow(workflow_id, schedule_time=tomorrow_2am)

def get_workflow_engine_status() -> Dict:
    """Get current workflow engine status"""
    engine = WorkflowEngine()
    return engine.get_system_metrics()