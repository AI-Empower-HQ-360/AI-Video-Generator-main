"""
Test suite for interactive video features
"""

import json
from unittest.mock import Mock, patch
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.interactive_endpoints import interactive_bp

class TestInteractiveFeatures:
    """Test class for interactive video features"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_user_id = "test_user_123"
        self.test_scene_id = "test_scene_meditation"
    
    def test_user_progress_creation(self):
        """Test creating user progress data"""
        from api.interactive_endpoints import user_progress
        
        # Initially empty
        assert self.test_user_id not in user_progress
        
        # Simulate progress update
        test_progress = {
            'achievements': ['first_interaction'],
            'decisions': [{'scene': 'intro', 'choice': 'meditation'}],
            'completedScenes': ['intro'],
            'interactions': [{'type': 'hotspot_click', 'data': 'wisdom_orb'}],
            'totalWatchTime': 300,
            'level': 1,
            'experience': 25
        }
        
        user_progress[self.test_user_id] = test_progress
        
        assert user_progress[self.test_user_id]['level'] == 1
        assert len(user_progress[self.test_user_id]['achievements']) == 1
        print("✅ User progress creation test passed")
    
    def test_achievement_checking(self):
        """Test achievement checking logic"""
        from api.interactive_endpoints import check_achievements
        
        test_progress = {
            'achievements': [],
            'decisions': [],
            'completedScenes': [],
            'interactions': [
                {'type': 'hotspot_click', 'data': 'test1'},
                {'type': 'hotspot_click', 'data': 'test2'}
            ],
            'totalWatchTime': 100,
            'level': 1,
            'experience': 0
        }
        
        new_achievements = check_achievements(self.test_user_id, test_progress)
        
        # Should get first_interaction achievement
        assert 'first_interaction' in new_achievements
        assert test_progress['experience'] > 0
        print("✅ Achievement checking test passed")
    
    def test_hotspot_management(self):
        """Test hotspot management functionality"""
        from api.interactive_endpoints import hotspot_data
        
        # Add hotspot
        test_hotspot = {
            'timeStart': 10.0,
            'timeEnd': 15.0,
            'x': 50,
            'y': 30,
            'content': 'Test wisdom insight',
            'action': 'show_quote'
        }
        
        if self.test_scene_id not in hotspot_data:
            hotspot_data[self.test_scene_id] = []
        
        hotspot_data[self.test_scene_id].append(test_hotspot)
        
        assert len(hotspot_data[self.test_scene_id]) == 1
        assert hotspot_data[self.test_scene_id][0]['content'] == 'Test wisdom insight'
        print("✅ Hotspot management test passed")
    
    def test_branching_data(self):
        """Test branching narrative data structure"""
        from api.interactive_endpoints import branching_data
        
        test_branch_data = {
            'branches': [
                {
                    'time': 30.0,
                    'question': 'What path calls to you?',
                    'options': [
                        {'text': 'Meditation', 'nextScene': 'meditation'},
                        {'text': 'Wisdom', 'nextScene': 'wisdom'}
                    ]
                }
            ],
            'hotspots': [],
            'metadata': {'difficulty': 'beginner'}
        }
        
        branching_data[self.test_scene_id] = test_branch_data
        
        assert len(branching_data[self.test_scene_id]['branches']) == 1
        assert len(branching_data[self.test_scene_id]['branches'][0]['options']) == 2
        print("✅ Branching data test passed")
    
    def test_live_session_management(self):
        """Test live streaming session management"""
        from api.interactive_endpoints import live_sessions
        
        test_session_id = "test_live_session"
        test_session_data = {
            'viewers': [],
            'is_live': True,
            'stream_url': 'https://example.com/stream',
            'instructor': 'Test Guru'
        }
        
        live_sessions[test_session_id] = test_session_data
        
        assert live_sessions[test_session_id]['is_live'] == True
        assert live_sessions[test_session_id]['instructor'] == 'Test Guru'
        print("✅ Live session management test passed")
    
    def test_chat_message_structure(self):
        """Test chat message data structure"""
        from api.interactive_endpoints import chat_messages
        
        test_session_id = "test_chat_session"
        test_message = {
            'id': 'msg_123',
            'userId': self.test_user_id,
            'username': 'TestUser',
            'message': 'This is a test message',
            'timestamp': '2024-01-01T12:00:00Z',
            'type': 'user'
        }
        
        if test_session_id not in chat_messages:
            chat_messages[test_session_id] = []
        
        chat_messages[test_session_id].append(test_message)
        
        assert len(chat_messages[test_session_id]) == 1
        assert chat_messages[test_session_id][0]['message'] == 'This is a test message'
        print("✅ Chat message structure test passed")
    
    def test_level_calculation(self):
        """Test level calculation based on experience"""
        from api.interactive_endpoints import calculate_level
        
        # Test different experience levels
        assert calculate_level(0) == 1
        assert calculate_level(100) == 2
        assert calculate_level(400) == 3
        assert calculate_level(900) == 4
        
        print("✅ Level calculation test passed")
    
    def test_achievement_points(self):
        """Test achievement point system"""
        from api.interactive_endpoints import get_achievement_points
        
        # Test different achievement point values
        assert get_achievement_points('first_interaction') == 10
        assert get_achievement_points('wisdom_seeker') == 100
        assert get_achievement_points('unknown_achievement') == 10  # default
        
        print("✅ Achievement points test passed")

class TestInteractiveEndpoints:
    """Test interactive API endpoints"""
    
    def setup_method(self):
        """Setup Flask test client"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
        
        from app import app
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.test_user_id = "test_user_api"
    
    def test_get_achievements_endpoint(self):
        """Test GET /api/interactive/achievements"""
        response = self.client.get('/api/interactive/achievements')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'achievements' in data
        assert len(data['achievements']) > 0
        
        print("✅ Get achievements endpoint test passed")
    
    def test_user_progress_endpoint(self):
        """Test user progress endpoints"""
        # Test GET user progress (should create default)
        response = self.client.get(f'/api/interactive/progress/{self.test_user_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'progress' in data
        
        # Test POST user progress update
        update_data = {
            'achievements': ['first_interaction'],
            'level': 2,
            'experience': 150
        }
        
        response = self.client.post(
            f'/api/interactive/progress/{self.test_user_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        print("✅ User progress endpoint test passed")
    
    def test_hotspot_endpoints(self):
        """Test hotspot management endpoints"""
        scene_id = "test_scene_api"
        
        # Test adding a hotspot
        hotspot_data = {
            'timeStart': 5.0,
            'timeEnd': 10.0,
            'x': 25,
            'y': 75,
            'content': 'API test hotspot',
            'action': 'test_action'
        }
        
        response = self.client.post(
            f'/api/interactive/hotspots/{scene_id}',
            data=json.dumps(hotspot_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'hotspot' in data
        assert data['hotspot']['content'] == 'API test hotspot'
        
        # Test getting hotspots
        response = self.client.get(f'/api/interactive/hotspots/{scene_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['hotspots']) >= 1
        
        print("✅ Hotspot endpoints test passed")
    
    def test_vr_content_endpoint(self):
        """Test VR content endpoint"""
        response = self.client.get('/api/interactive/vr-content')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'content' in data
        assert 'environments' in data['content']
        
        print("✅ VR content endpoint test passed")
    
    def test_voice_commands_endpoint(self):
        """Test voice commands endpoint"""
        response = self.client.get('/api/interactive/voice-commands')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'commands' in data
        assert 'video_controls' in data['commands']
        
        print("✅ Voice commands endpoint test passed")

def run_all_tests():
    """Run all interactive feature tests"""
    print("🧪 Running Interactive Video Features Tests...\n")
    
    # Test core functionality
    test_features = TestInteractiveFeatures()
    test_features.setup_method()
    
    try:
        test_features.test_user_progress_creation()
        test_features.test_achievement_checking()
        test_features.test_hotspot_management()
        test_features.test_branching_data()
        test_features.test_live_session_management()
        test_features.test_chat_message_structure()
        test_features.test_level_calculation()
        test_features.test_achievement_points()
        
        print("\n✅ All core functionality tests passed!")
        
    except Exception as e:
        print(f"\n❌ Core functionality test failed: {e}")
        return False
    
    # Test API endpoints
    test_endpoints = TestInteractiveEndpoints()
    test_endpoints.setup_method()
    
    try:
        test_endpoints.test_get_achievements_endpoint()
        test_endpoints.test_user_progress_endpoint()
        test_endpoints.test_hotspot_endpoints()
        test_endpoints.test_vr_content_endpoint()
        test_endpoints.test_voice_commands_endpoint()
        
        print("\n✅ All API endpoint tests passed!")
        
    except Exception as e:
        print(f"\n❌ API endpoint test failed: {e}")
        return False
    
    print("\n🎉 All Interactive Video Features tests completed successfully!")
    return True

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)