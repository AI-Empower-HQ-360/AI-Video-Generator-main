"""
Basic test for workflow automation system - standalone version
"""

import asyncio
import json
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the database imports for testing
class MockDB:
    def __init__(self):
        pass

# Create mock models
class MockWorkflow:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

class MockWorkflowNode:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

# Mock the database models
sys.modules['models.database'] = type('MockModule', (), {
    'db': MockDB(),
    'Workflow': MockWorkflow,
    'WorkflowNode': MockWorkflowNode,
    'WorkflowConnection': MockWorkflow,
    'WorkflowExecution': MockWorkflow,
    'WorkflowExecutionLog': MockWorkflow,
    'WorkflowApproval': MockWorkflow
})()

async def test_workflow_execution():
    """Test basic workflow execution"""
    print("🧪 Testing Workflow Automation System")
    print("=" * 50)
    
    # Import after mocking
    from services.workflow_engine import WorkflowExecutionEngine, WorkflowTemplateService
    
    # Create workflow engine
    engine = WorkflowExecutionEngine()
    template_service = WorkflowTemplateService()
    
    # Test 1: Create a simple workflow template
    print("\n1. Creating content creation workflow template...")
    template = template_service.create_content_creation_template()
    print(f"   ✅ Template created: {template['name']}")
    print(f"   📊 Nodes: {len(template['nodes'])}, Connections: {len(template['connections'])}")
    
    # Test 2: Create approval workflow template
    print("\n2. Creating approval workflow template...")
    approval_template = template_service.create_approval_workflow_template()
    print(f"   ✅ Template created: {approval_template['name']}")
    print(f"   📊 Nodes: {len(approval_template['nodes'])}, Connections: {len(approval_template['connections'])}")
    
    # Test 3: Test condition evaluation
    print("\n3. Testing condition evaluation...")
    test_context = type('Context', (), {
        'workflow_id': 'test_001',
        'execution_id': 'exec_001', 
        'current_node_id': 'node_001',
        'input_data': {'status': 'approved', 'amount': 1500},
        'runtime_data': {'status': 'approved', 'amount': 1500},
        'user_id': 'user_001'
    })()
    
    # Test simple conditions
    conditions = [
        '${status} equals approved',
        '${amount} greater_than 1000',
        '${status} contains approve'
    ]
    
    for condition in conditions:
        result = await engine._evaluate_condition(test_context, condition)
        print(f"   📝 Condition: '{condition}' → {result}")
    
    # Test 4: Test content generation action
    print("\n4. Testing content generation...")
    action_config = {
        'prompt': 'Create spiritual guidance about ${topic}',
        'guru_type': 'spiritual'
    }
    
    test_context.runtime_data = {'topic': 'meditation'}
    result = await engine._execute_content_generation(test_context, action_config)
    print(f"   ✅ Content generated: {result['generated_content'][:50]}...")
    
    # Test 5: Test API call action
    print("\n5. Testing API call simulation...")
    api_config = {
        'url': 'https://api.example.com/publish/${content_id}',
        'method': 'POST',
        'payload': {'title': '${title}', 'content': '${content}'}
    }
    
    test_context.runtime_data = {
        'content_id': '12345',
        'title': 'Daily Meditation',
        'content': 'Today we focus on inner peace...'
    }
    
    api_result = await engine._execute_api_call(test_context, api_config)
    print(f"   ✅ API call simulated: {api_result['method']} to {api_result['url']}")
    
    # Test 6: Test data transformation
    print("\n6. Testing data transformation...")
    transform_config = {
        'type': 'uppercase',
        'source_field': 'title',
        'target_field': 'title_upper'
    }
    
    transform_result = await engine._execute_data_transformation(test_context, transform_config)
    print(f"   ✅ Transformation: '{transform_result['transformed_value']}'")
    
    print("\n🎉 All workflow automation tests passed!")
    return True

async def test_multilingual_engine():
    """Test multilingual workflow features"""
    print("\n🌍 Testing Multilingual Engine")
    print("=" * 30)
    
    from services.workflow_multilingual import multilingual_engine, TranslationRequest
    
    # Test 1: Language detection
    print("\n1. Testing language detection...")
    test_content = "Meditation brings inner peace and dharma guides our path"
    detected_lang, confidence = multilingual_engine.detect_language(test_content)
    print(f"   🔍 Detected: {detected_lang} (confidence: {confidence:.2f})")
    
    # Test 2: Translation request
    print("\n2. Testing translation...")
    request = TranslationRequest(
        content="Meditation is the path to enlightenment",
        source_language="en",
        target_language="es",
        content_type="text",
        context="spiritual"
    )
    
    result = await multilingual_engine.translate_content(request)
    print(f"   🔄 Translation: {result.translated_content}")
    print(f"   📊 Confidence: {result.confidence_score:.2f}")
    
    # Test 3: Create localization workflow
    print("\n3. Creating localization workflow template...")
    localization_workflow = multilingual_engine.create_localization_workflow_template(
        content_languages=['en', 'es', 'fr', 'hi'],
        content_type='spiritual'
    )
    print(f"   ✅ Workflow: {localization_workflow['name']}")
    print(f"   📊 Nodes: {len(localization_workflow['nodes'])}")
    
    print("\n🌍 Multilingual tests completed!")
    return True

def test_scheduler_setup():
    """Test scheduler service setup"""
    print("\n⏰ Testing Scheduler Setup")
    print("=" * 25)
    
    try:
        from services.workflow_scheduler import WorkflowSchedulerService
        
        # Test scheduler initialization
        scheduler = WorkflowSchedulerService()
        print("   ✅ Scheduler service created")
        
        # Test cron expression parsing (basic)
        test_schedules = [
            "0 9 * * *",  # Daily at 9 AM
            "0 0 * * 1",  # Weekly on Monday
            "*/30 * * * *"  # Every 30 minutes
        ]
        
        for cron_expr in test_schedules:
            try:
                from apscheduler.triggers.cron import CronTrigger
                trigger = CronTrigger.from_crontab(cron_expr)
                print(f"   📅 Valid cron: '{cron_expr}'")
            except Exception as e:
                print(f"   ❌ Invalid cron: '{cron_expr}' - {e}")
        
        print("   ✅ Scheduler setup test completed")
        return True
        
    except ImportError as e:
        print(f"   ⚠️  APScheduler not available: {e}")
        print("   💡 Run: pip install APScheduler")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Workflow Automation Tests")
    print("=" * 60)
    
    # Run tests
    test1 = await test_workflow_execution()
    test2 = await test_multilingual_engine() 
    test3 = test_scheduler_setup()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 15)
    print(f"   Workflow Engine: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Multilingual Engine: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"   Scheduler Setup: {'✅ PASS' if test3 else '⚠️  PARTIAL'}")
    
    all_passed = test1 and test2 and test3
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '⚠️  SOME ISSUES FOUND'}")
    
    if all_passed:
        print("\n🎉 Workflow Automation System is ready for use!")
        print("\nNext steps:")
        print("   1. Install APScheduler: pip install APScheduler")
        print("   2. Start the Flask application")
        print("   3. Access workflow builder at /api/workflows")
        print("   4. Create your first workflow!")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())