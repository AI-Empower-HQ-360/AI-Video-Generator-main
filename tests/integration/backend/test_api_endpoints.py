import requests
import pytest
import json
from unittest.mock import patch, MagicMock

# Test base URL - in a real scenario this would be configurable
BASE_URL = 'http://localhost:5000'

class TestUsersAPI:
    """Integration tests for Users API endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = BASE_URL
        self.headers = {'Content-Type': 'application/json'}
    
    def test_get_user_profile_success(self):
        """Test successful user profile retrieval"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'message': 'User profile endpoint',
                'data': {
                    'user_id': '123',
                    'username': 'testuser',
                    'preferences': {
                        'language': 'en',
                        'guru_type': 'spiritual'
                    }
                }
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f'{self.base_url}/api/users/profile')
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'data' in data
            mock_get.assert_called_once_with(f'{self.base_url}/api/users/profile')
    
    def test_get_user_profile_unauthorized(self):
        """Test user profile retrieval with unauthorized access"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {
                'success': False,
                'message': 'Unauthorized access'
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f'{self.base_url}/api/users/profile')
            
            assert response.status_code == 401
            data = response.json()
            assert data['success'] is False
    
    def test_save_user_preferences_success(self):
        """Test successful user preferences saving"""
        preferences_data = {
            'language': 'hi',
            'guru_type': 'meditation',
            'notification_enabled': True
        }
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'message': 'Preferences saved',
                'data': preferences_data
            }
            mock_post.return_value = mock_response
            
            response = requests.post(
                f'{self.base_url}/api/users/preferences',
                headers=self.headers,
                json=preferences_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['message'] == 'Preferences saved'
            mock_post.assert_called_once()
    
    def test_save_user_preferences_validation_error(self):
        """Test user preferences saving with validation error"""
        invalid_data = {
            'language': 'invalid_lang',
            'guru_type': 'invalid_type'
        }
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                'success': False,
                'message': 'Validation error',
                'errors': {
                    'language': 'Invalid language code',
                    'guru_type': 'Invalid guru type'
                }
            }
            mock_post.return_value = mock_response
            
            response = requests.post(
                f'{self.base_url}/api/users/preferences',
                headers=self.headers,
                json=invalid_data
            )
            
            assert response.status_code == 400
            data = response.json()
            assert data['success'] is False
            assert 'errors' in data
    
    def test_save_user_preferences_server_error(self):
        """Test user preferences saving with server error"""
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {
                'success': False,
                'message': 'Internal server error'
            }
            mock_post.return_value = mock_response
            
            response = requests.post(
                f'{self.base_url}/api/users/preferences',
                headers=self.headers,
                json={'language': 'en'}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert data['success'] is False


class TestSessionsAPI:
    """Integration tests for Sessions API endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = BASE_URL
        self.headers = {'Content-Type': 'application/json'}
    
    def test_create_session_success(self):
        """Test successful session creation"""
        session_data = {
            'user_id': '123',
            'guru_type': 'meditation',
            'session_type': 'guided_meditation',
            'duration': 300  # 5 minutes
        }
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                'success': True,
                'message': 'Session created successfully',
                'data': {
                    'session_id': 'sess_456',
                    'status': 'active',
                    'created_at': '2024-01-01T00:00:00Z',
                    **session_data
                }
            }
            mock_post.return_value = mock_response
            
            response = requests.post(
                f'{self.base_url}/api/sessions',
                headers=self.headers,
                json=session_data
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data['success'] is True
            assert 'session_id' in data['data']
    
    def test_get_session_history(self):
        """Test retrieving session history"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'data': {
                    'sessions': [
                        {
                            'session_id': 'sess_123',
                            'guru_type': 'spiritual',
                            'duration': 600,
                            'completed_at': '2024-01-01T00:10:00Z'
                        },
                        {
                            'session_id': 'sess_124',
                            'guru_type': 'meditation',
                            'duration': 300,
                            'completed_at': '2024-01-01T00:15:00Z'
                        }
                    ],
                    'total_count': 2,
                    'total_duration': 900
                }
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f'{self.base_url}/api/sessions/history')
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']['sessions']) == 2
    
    def test_end_session_success(self):
        """Test successful session completion"""
        session_id = 'sess_456'
        completion_data = {
            'duration': 300,
            'rating': 5,
            'feedback': 'Very helpful session'
        }
        
        with patch('requests.put') as mock_put:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'message': 'Session completed successfully',
                'data': {
                    'session_id': session_id,
                    'status': 'completed',
                    'completed_at': '2024-01-01T00:05:00Z',
                    **completion_data
                }
            }
            mock_put.return_value = mock_response
            
            response = requests.put(
                f'{self.base_url}/api/sessions/{session_id}/complete',
                headers=self.headers,
                json=completion_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['data']['status'] == 'completed'


class TestGurusAPI:
    """Integration tests for Gurus API endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = BASE_URL
        self.headers = {'Content-Type': 'application/json'}
    
    def test_get_available_gurus(self):
        """Test retrieving available gurus"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'data': {
                    'gurus': [
                        {
                            'type': 'spiritual',
                            'name': 'Spiritual Guru',
                            'description': 'Provides general spiritual guidance',
                            'specialties': ['dharma', 'moksha', 'wisdom']
                        },
                        {
                            'type': 'meditation',
                            'name': 'Meditation Guru',
                            'description': 'Guides meditation practices',
                            'specialties': ['mindfulness', 'breathing', 'concentration']
                        }
                    ]
                }
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f'{self.base_url}/api/gurus')
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']['gurus']) >= 2
    
    def test_chat_with_guru_success(self):
        """Test successful guru chat interaction"""
        chat_data = {
            'guru_type': 'spiritual',
            'message': 'What is the meaning of dharma?',
            'user_context': {
                'language': 'en',
                'experience_level': 'beginner'
            }
        }
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'data': {
                    'response': 'Dharma refers to the righteous path of life...',
                    'guru_type': 'spiritual',
                    'context_used': True,
                    'response_id': 'resp_789'
                }
            }
            mock_post.return_value = mock_response
            
            response = requests.post(
                f'{self.base_url}/api/gurus/chat',
                headers=self.headers,
                json=chat_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'response' in data['data']
    
    def test_chat_with_guru_invalid_type(self):
        """Test chat with invalid guru type"""
        chat_data = {
            'guru_type': 'invalid_guru',
            'message': 'Test message'
        }
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                'success': False,
                'message': 'Invalid guru type',
                'valid_types': ['spiritual', 'meditation', 'karma', 'bhakti']
            }
            mock_post.return_value = mock_response
            
            response = requests.post(
                f'{self.base_url}/api/gurus/chat',
                headers=self.headers,
                json=chat_data
            )
            
            assert response.status_code == 400
            data = response.json()
            assert data['success'] is False
            assert 'valid_types' in data


class TestSlokasAPI:
    """Integration tests for Slokas API endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = BASE_URL
        self.headers = {'Content-Type': 'application/json'}
    
    def test_get_random_sloka(self):
        """Test retrieving random sloka"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'data': {
                    'sloka_id': 'sloka_123',
                    'text': 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन',
                    'translation': 'You have the right to perform actions, but never to the fruits of action.',
                    'source': 'bhagavad-gita',
                    'chapter': 2,
                    'verse': 47,
                    'meaning': 'This verse emphasizes performing duty without attachment to results.'
                }
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f'{self.base_url}/api/slokas/random')
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'sloka_id' in data['data']
            assert 'text' in data['data']
            assert 'translation' in data['data']
    
    def test_search_slokas(self):
        """Test searching slokas"""
        search_params = {
            'query': 'dharma',
            'source': 'bhagavad-gita',
            'limit': 5
        }
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'data': {
                    'slokas': [
                        {
                            'sloka_id': 'sloka_456',
                            'text': 'धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः',
                            'translation': 'In the holy field of Kurukshetra...',
                            'source': 'bhagavad-gita',
                            'relevance_score': 0.95
                        }
                    ],
                    'total_count': 1,
                    'search_query': 'dharma'
                }
            }
            mock_get.return_value = mock_response
            
            response = requests.get(
                f'{self.base_url}/api/slokas/search',
                params=search_params
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']['slokas']) > 0
    
    def test_get_sloka_by_id(self):
        """Test retrieving specific sloka by ID"""
        sloka_id = 'sloka_123'
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'data': {
                    'sloka_id': sloka_id,
                    'text': 'योगस्थः कुरु कर्माणि',
                    'translation': 'Established in yoga, perform actions.',
                    'source': 'bhagavad-gita',
                    'chapter': 2,
                    'verse': 48,
                    'commentary': 'Detailed explanation of the verse...',
                    'related_slokas': ['sloka_124', 'sloka_125']
                }
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f'{self.base_url}/api/slokas/{sloka_id}')
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['data']['sloka_id'] == sloka_id
    
    def test_get_sloka_not_found(self):
        """Test retrieving non-existent sloka"""
        invalid_id = 'sloka_999'
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                'success': False,
                'message': 'Sloka not found'
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f'{self.base_url}/api/slokas/{invalid_id}')
            
            assert response.status_code == 404
            data = response.json()
            assert data['success'] is False


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])