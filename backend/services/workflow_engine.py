"""
Workflow Execution Engine
========================

This module handles the execution of workflows with conditional logic,
branching, and multi-step automation processes.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from models.database import (
    db, Workflow, WorkflowNode, WorkflowConnection, WorkflowExecution,
    WorkflowExecutionLog, WorkflowApproval
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """Context data passed between workflow nodes"""
    workflow_id: str
    execution_id: str
    current_node_id: str
    input_data: Dict[str, Any]
    runtime_data: Dict[str, Any]
    user_id: Optional[str] = None


class WorkflowExecutionEngine:
    """
    Core engine for executing workflows with conditional logic and branching
    """
    
    def __init__(self):
        self.node_processors = {
            'start': self._process_start_node,
            'action': self._process_action_node,
            'condition': self._process_condition_node,
            'approval': self._process_approval_node,
            'localization': self._process_localization_node,
            'schedule': self._process_schedule_node,
            'end': self._process_end_node
        }
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any], 
                             user_id: Optional[str] = None, trigger_type: str = 'manual') -> str:
        """
        Execute a workflow and return the execution ID
        """
        # Get workflow
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if workflow.status != 'active':
            raise ValueError(f"Workflow {workflow_id} is not active")
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            triggered_by=user_id,
            trigger_type=trigger_type,
            input_data=input_data,
            context_data={}
        )
        
        db.session.add(execution)
        db.session.commit()
        
        # Log execution start
        await self._log_execution(execution.id, None, 'info', 
                                f'Workflow execution started by {trigger_type}', 
                                {'input_data': input_data})
        
        try:
            # Find start node
            start_node = WorkflowNode.query.filter_by(
                workflow_id=workflow_id, 
                node_type='start'
            ).first()
            
            if not start_node:
                raise ValueError(f"No start node found for workflow {workflow_id}")
            
            # Create execution context
            context = ExecutionContext(
                workflow_id=workflow_id,
                execution_id=execution.id,
                current_node_id=start_node.id,
                input_data=input_data,
                runtime_data={},
                user_id=user_id
            )
            
            # Execute workflow starting from start node
            await self._execute_from_node(context, start_node)
            
            # Update execution status
            execution.status = 'completed'
            execution.completed_at = datetime.utcnow()
            execution.output_data = context.runtime_data.get('output', {})
            
        except Exception as e:
            # Log error and update execution status
            await self._log_execution(execution.id, None, 'error', 
                                    f'Workflow execution failed: {str(e)}')
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            logger.error(f"Workflow execution {execution.id} failed: {e}")
            
        finally:
            db.session.commit()
        
        return execution.id
    
    async def _execute_from_node(self, context: ExecutionContext, node: WorkflowNode):
        """
        Execute workflow starting from a specific node
        """
        current_node = node
        
        while current_node and current_node.node_type != 'end':
            # Update current node in execution
            execution = WorkflowExecution.query.get(context.execution_id)
            execution.current_node_id = current_node.id
            execution.context_data = context.runtime_data
            db.session.commit()
            
            # Log node execution
            await self._log_execution(context.execution_id, current_node.id, 'info', 
                                    f'Executing node: {current_node.name}')
            
            # Process current node
            processor = self.node_processors.get(current_node.node_type)
            if not processor:
                raise ValueError(f"Unknown node type: {current_node.node_type}")
            
            result = await processor(context, current_node)
            
            # Handle node result and get next node
            next_node = await self._get_next_node(context, current_node, result)
            current_node = next_node
        
        # Process end node if reached
        if current_node and current_node.node_type == 'end':
            await self._process_end_node(context, current_node)
    
    async def _process_start_node(self, context: ExecutionContext, node: WorkflowNode) -> Dict[str, Any]:
        """Process start node"""
        await self._log_execution(context.execution_id, node.id, 'info', 
                                f'Workflow started with input: {context.input_data}')
        
        # Initialize runtime data with input data
        context.runtime_data.update(context.input_data)
        
        return {'status': 'success'}
    
    async def _process_action_node(self, context: ExecutionContext, node: WorkflowNode) -> Dict[str, Any]:
        """Process action node"""
        action_type = node.action_type
        action_config = node.action_config or {}
        
        await self._log_execution(context.execution_id, node.id, 'info', 
                                f'Executing action: {action_type}')
        
        try:
            if action_type == 'content_generation':
                result = await self._execute_content_generation(context, action_config)
            elif action_type == 'api_call':
                result = await self._execute_api_call(context, action_config)
            elif action_type == 'data_transformation':
                result = await self._execute_data_transformation(context, action_config)
            elif action_type == 'notification':
                result = await self._execute_notification(context, action_config)
            else:
                result = await self._execute_custom_action(context, action_type, action_config)
            
            # Store result in runtime data
            context.runtime_data[f'action_{node.id}_result'] = result
            
            await self._log_execution(context.execution_id, node.id, 'info', 
                                    f'Action completed successfully', {'result': result})
            
            return {'status': 'success', 'result': result}
            
        except Exception as e:
            await self._log_execution(context.execution_id, node.id, 'error', 
                                    f'Action failed: {str(e)}')
            return {'status': 'failure', 'error': str(e)}
    
    async def _process_condition_node(self, context: ExecutionContext, node: WorkflowNode) -> Dict[str, Any]:
        """Process condition node with branching logic"""
        condition_expression = node.condition_expression
        
        if not condition_expression:
            return {'status': 'success', 'condition_result': True}
        
        try:
            # Evaluate condition expression
            condition_result = await self._evaluate_condition(context, condition_expression)
            
            await self._log_execution(context.execution_id, node.id, 'info', 
                                    f'Condition evaluated to: {condition_result}', 
                                    {'expression': condition_expression})
            
            return {'status': 'success', 'condition_result': condition_result}
            
        except Exception as e:
            await self._log_execution(context.execution_id, node.id, 'error', 
                                    f'Condition evaluation failed: {str(e)}')
            return {'status': 'failure', 'error': str(e)}
    
    async def _process_approval_node(self, context: ExecutionContext, node: WorkflowNode) -> Dict[str, Any]:
        """Process approval node"""
        approval_required_from = node.approval_required_from or []
        timeout_hours = node.approval_timeout_hours or 24
        
        if not approval_required_from:
            await self._log_execution(context.execution_id, node.id, 'warning', 
                                    'No approvers specified, auto-approving')
            return {'status': 'success', 'approved': True}
        
        # Create approval requests
        for approver_id in approval_required_from:
            approval = WorkflowApproval(
                execution_id=context.execution_id,
                node_id=node.id,
                required_from=approver_id,
                subject=f'Approval Required: {node.name}',
                content=node.description or 'Please review and approve this workflow step',
                approval_data=context.runtime_data,
                expires_at=datetime.utcnow() + timedelta(hours=timeout_hours)
            )
            db.session.add(approval)
        
        db.session.commit()
        
        await self._log_execution(context.execution_id, node.id, 'info', 
                                f'Approval requests sent to {len(approval_required_from)} approvers')
        
        # For now, return pending - in a real implementation, 
        # this would wait for approvals or be resumed later
        return {'status': 'pending', 'waiting_for_approval': True}
    
    async def _process_localization_node(self, context: ExecutionContext, node: WorkflowNode) -> Dict[str, Any]:
        """Process localization node for multi-language workflows"""
        if not node.localization_enabled:
            return {'status': 'success', 'message': 'Localization not enabled'}
        
        target_languages = node.target_languages or ['en']
        content_to_translate = context.runtime_data.get('content', '')
        
        try:
            # Simulate translation (in real implementation, use translation service)
            translations = {}
            for lang in target_languages:
                if lang != 'en':  # Don't translate English to English
                    translations[lang] = await self._translate_content(content_to_translate, lang)
                else:
                    translations[lang] = content_to_translate
            
            context.runtime_data['translations'] = translations
            
            await self._log_execution(context.execution_id, node.id, 'info', 
                                    f'Content localized to {len(target_languages)} languages')
            
            return {'status': 'success', 'translations': translations}
            
        except Exception as e:
            await self._log_execution(context.execution_id, node.id, 'error', 
                                    f'Localization failed: {str(e)}')
            return {'status': 'failure', 'error': str(e)}
    
    async def _process_schedule_node(self, context: ExecutionContext, node: WorkflowNode) -> Dict[str, Any]:
        """Process schedule node for delayed execution"""
        schedule_config = node.action_config or {}
        delay_minutes = schedule_config.get('delay_minutes', 0)
        
        if delay_minutes > 0:
            await self._log_execution(context.execution_id, node.id, 'info', 
                                    f'Scheduling delay of {delay_minutes} minutes')
            
            # In a real implementation, this would schedule the continuation
            # For now, we'll just log it
            context.runtime_data['scheduled_for'] = (
                datetime.utcnow() + timedelta(minutes=delay_minutes)
            ).isoformat()
        
        return {'status': 'success', 'scheduled': delay_minutes > 0}
    
    async def _process_end_node(self, context: ExecutionContext, node: WorkflowNode) -> Dict[str, Any]:
        """Process end node"""
        await self._log_execution(context.execution_id, node.id, 'info', 
                                'Workflow execution completed')
        
        # Set final output
        context.runtime_data['output'] = context.runtime_data.get('output', {
            'status': 'completed',
            'final_data': context.runtime_data
        })
        
        return {'status': 'success'}
    
    async def _get_next_node(self, context: ExecutionContext, current_node: WorkflowNode, 
                           result: Dict[str, Any]) -> Optional[WorkflowNode]:
        """Determine the next node based on current node result"""
        connections = WorkflowConnection.query.filter_by(from_node_id=current_node.id).all()
        
        if not connections:
            return None
        
        # For condition nodes, choose path based on condition result
        if current_node.node_type == 'condition':
            condition_result = result.get('condition_result', True)
            target_condition = 'true' if condition_result else 'false'
            
            for connection in connections:
                if connection.condition == target_condition:
                    return WorkflowNode.query.get(connection.to_node_id)
        
        # For approval nodes, choose path based on approval status
        elif current_node.node_type == 'approval':
            if result.get('status') == 'pending':
                # In real implementation, workflow would be paused here
                return None
            
            approved = result.get('approved', False)
            target_condition = 'approved' if approved else 'rejected'
            
            for connection in connections:
                if connection.condition == target_condition:
                    return WorkflowNode.query.get(connection.to_node_id)
        
        # For other nodes, choose path based on result status
        else:
            status = result.get('status', 'success')
            
            for connection in connections:
                if connection.condition == status or connection.condition is None:
                    return WorkflowNode.query.get(connection.to_node_id)
        
        # Default to first connection if no condition matches
        if connections:
            return WorkflowNode.query.get(connections[0].to_node_id)
        
        return None
    
    async def _evaluate_condition(self, context: ExecutionContext, expression: str) -> bool:
        """
        Safely evaluate condition expressions
        """
        # Simple expression evaluator - in production, use a proper expression parser
        try:
            # Replace variable references with actual values
            runtime_data = context.runtime_data
            
            # Basic variable substitution (simplified)
            for key, value in runtime_data.items():
                expression = expression.replace(f'${key}', str(value))
            
            # Basic condition evaluation
            if 'equals' in expression:
                parts = expression.split('equals')
                if len(parts) == 2:
                    left = parts[0].strip().strip('"\'')
                    right = parts[1].strip().strip('"\'')
                    return left == right
            elif 'contains' in expression:
                parts = expression.split('contains')
                if len(parts) == 2:
                    left = parts[0].strip().strip('"\'')
                    right = parts[1].strip().strip('"\'')
                    return right in left
            elif 'greater_than' in expression:
                parts = expression.split('greater_than')
                if len(parts) == 2:
                    try:
                        left = float(parts[0].strip())
                        right = float(parts[1].strip())
                        return left > right
                    except ValueError:
                        return False
            
            # Default to True for simple expressions
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            return False
    
    async def _execute_content_generation(self, context: ExecutionContext, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content generation action"""
        prompt = config.get('prompt', '')
        guru_type = config.get('guru_type', 'spiritual')
        
        # Substitute variables in prompt
        for key, value in context.runtime_data.items():
            prompt = prompt.replace(f'${key}', str(value))
        
        # Simulate content generation (integrate with existing guru system)
        generated_content = f"Generated content for prompt: {prompt[:100]}..."
        
        return {
            'generated_content': generated_content,
            'guru_type': guru_type,
            'prompt_used': prompt
        }
    
    async def _execute_api_call(self, context: ExecutionContext, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call action"""
        url = config.get('url', '')
        method = config.get('method', 'GET')
        headers = config.get('headers', {})
        payload = config.get('payload', {})
        
        # Substitute variables in URL and payload
        for key, value in context.runtime_data.items():
            url = url.replace(f'${key}', str(value))
            payload = json.loads(json.dumps(payload).replace(f'${key}', str(value)))
        
        # Simulate API call
        return {
            'status_code': 200,
            'response': {'message': 'API call simulated successfully'},
            'url': url,
            'method': method
        }
    
    async def _execute_data_transformation(self, context: ExecutionContext, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data transformation action"""
        transformation_type = config.get('type', 'identity')
        source_field = config.get('source_field', '')
        target_field = config.get('target_field', '')
        
        source_value = context.runtime_data.get(source_field, '')
        
        if transformation_type == 'uppercase':
            transformed_value = str(source_value).upper()
        elif transformation_type == 'lowercase':
            transformed_value = str(source_value).lower()
        elif transformation_type == 'extract_keywords':
            # Simple keyword extraction
            words = str(source_value).split()
            transformed_value = [word for word in words if len(word) > 4]
        else:
            transformed_value = source_value
        
        # Store transformed value
        if target_field:
            context.runtime_data[target_field] = transformed_value
        
        return {
            'source_field': source_field,
            'target_field': target_field,
            'transformation_type': transformation_type,
            'transformed_value': transformed_value
        }
    
    async def _execute_notification(self, context: ExecutionContext, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification action"""
        notification_type = config.get('type', 'email')
        recipients = config.get('recipients', [])
        subject = config.get('subject', 'Workflow Notification')
        message = config.get('message', '')
        
        # Substitute variables
        for key, value in context.runtime_data.items():
            subject = subject.replace(f'${key}', str(value))
            message = message.replace(f'${key}', str(value))
        
        # Simulate notification sending
        return {
            'notification_type': notification_type,
            'recipients': recipients,
            'subject': subject,
            'message': message,
            'sent': True
        }
    
    async def _execute_custom_action(self, context: ExecutionContext, action_type: str, 
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom action types"""
        # Placeholder for custom action implementations
        return {
            'action_type': action_type,
            'config': config,
            'status': 'executed',
            'message': f'Custom action {action_type} executed'
        }
    
    async def _translate_content(self, content: str, target_language: str) -> str:
        """
        Translate content to target language
        """
        # Simulate translation - in real implementation, use translation API
        language_names = {
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'hi': 'Hindi',
            'zh': 'Chinese',
            'ar': 'Arabic'
        }
        
        lang_name = language_names.get(target_language, target_language)
        return f"[{lang_name} translation]: {content}"
    
    async def _log_execution(self, execution_id: str, node_id: Optional[str], 
                           level: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log workflow execution details"""
        log_entry = WorkflowExecutionLog(
            execution_id=execution_id,
            node_id=node_id,
            level=level,
            message=message,
            details=details
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        # Also log to application logger
        log_method = getattr(logger, level, logger.info)
        log_method(f"Execution {execution_id}: {message}")


# Workflow Template Functions
class WorkflowTemplateService:
    """
    Service for managing workflow templates and marketplace
    """
    
    @staticmethod
    def create_content_creation_template() -> Dict[str, Any]:
        """Create a content creation workflow template"""
        return {
            'name': 'AI Content Creation Workflow',
            'description': 'Automated content generation with approval and publishing',
            'category': 'content_creation',
            'is_template': True,
            'template_category': 'content',
            'nodes': [
                {
                    'node_type': 'start',
                    'name': 'Start Content Creation',
                    'position_x': 100,
                    'position_y': 100
                },
                {
                    'node_type': 'action',
                    'name': 'Generate Content',
                    'action_type': 'content_generation',
                    'action_config': {
                        'prompt': 'Create spiritual content about: ${topic}',
                        'guru_type': '${guru_type}'
                    },
                    'position_x': 300,
                    'position_y': 100
                },
                {
                    'node_type': 'approval',
                    'name': 'Content Review',
                    'approval_required_from': ['${approver_id}'],
                    'approval_timeout_hours': 24,
                    'position_x': 500,
                    'position_y': 100
                },
                {
                    'node_type': 'localization',
                    'name': 'Translate Content',
                    'localization_enabled': True,
                    'target_languages': ['en', 'es', 'hi'],
                    'position_x': 700,
                    'position_y': 100
                },
                {
                    'node_type': 'action',
                    'name': 'Publish Content',
                    'action_type': 'api_call',
                    'action_config': {
                        'url': '${publish_url}',
                        'method': 'POST',
                        'payload': {'content': '${generated_content}'}
                    },
                    'position_x': 900,
                    'position_y': 100
                },
                {
                    'node_type': 'end',
                    'name': 'Content Published',
                    'position_x': 1100,
                    'position_y': 100
                }
            ],
            'connections': [
                {'from_node': 0, 'to_node': 1, 'condition': 'success'},
                {'from_node': 1, 'to_node': 2, 'condition': 'success'},
                {'from_node': 2, 'to_node': 3, 'condition': 'approved'},
                {'from_node': 3, 'to_node': 4, 'condition': 'success'},
                {'from_node': 4, 'to_node': 5, 'condition': 'success'}
            ]
        }
    
    @staticmethod
    def create_approval_workflow_template() -> Dict[str, Any]:
        """Create an approval chain workflow template"""
        return {
            'name': 'Multi-Level Approval Workflow',
            'description': 'Hierarchical approval process with escalation',
            'category': 'approval',
            'is_template': True,
            'template_category': 'approval',
            'nodes': [
                {
                    'node_type': 'start',
                    'name': 'Start Approval Process',
                    'position_x': 100,
                    'position_y': 200
                },
                {
                    'node_type': 'approval',
                    'name': 'First Level Approval',
                    'approval_required_from': ['${level1_approver}'],
                    'approval_timeout_hours': 24,
                    'position_x': 300,
                    'position_y': 200
                },
                {
                    'node_type': 'condition',
                    'name': 'Check Amount',
                    'condition_expression': '${amount} greater_than 1000',
                    'position_x': 500,
                    'position_y': 200
                },
                {
                    'node_type': 'approval',
                    'name': 'Second Level Approval',
                    'approval_required_from': ['${level2_approver}'],
                    'approval_timeout_hours': 48,
                    'position_x': 700,
                    'position_y': 100
                },
                {
                    'node_type': 'action',
                    'name': 'Final Processing',
                    'action_type': 'notification',
                    'action_config': {
                        'type': 'email',
                        'recipients': ['${requester_email}'],
                        'subject': 'Request Approved',
                        'message': 'Your request has been approved and processed.'
                    },
                    'position_x': 900,
                    'position_y': 200
                },
                {
                    'node_type': 'end',
                    'name': 'Process Complete',
                    'position_x': 1100,
                    'position_y': 200
                }
            ],
            'connections': [
                {'from_node': 0, 'to_node': 1, 'condition': 'success'},
                {'from_node': 1, 'to_node': 2, 'condition': 'approved'},
                {'from_node': 2, 'to_node': 3, 'condition': 'true'},
                {'from_node': 2, 'to_node': 4, 'condition': 'false'},
                {'from_node': 3, 'to_node': 4, 'condition': 'approved'},
                {'from_node': 4, 'to_node': 5, 'condition': 'success'}
            ]
        }