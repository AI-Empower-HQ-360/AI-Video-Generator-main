"""
AI Video Recommendation Engine
Advanced recommendation system using collaborative filtering, content-based filtering, and deep learning
"""

import json
import hashlib
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter

class VideoRecommendationEngine:
    """Advanced AI-powered video recommendation system"""
    
    def __init__(self):
        self.model_version = "RecommendAI-v2.3"
        self.algorithms = {
            'collaborative_filtering': 0.4,
            'content_based': 0.3,
            'deep_learning': 0.2,
            'trending': 0.1
        }
        
        # Simulated user-video interaction matrix
        self.user_interactions = defaultdict(dict)
        self.video_features = {}
        self.user_profiles = {}
        
        # Content categories and features
        self.content_categories = [
            'educational', 'entertainment', 'tutorial', 'news', 'music', 
            'sports', 'comedy', 'documentary', 'gaming', 'lifestyle'
        ]
        
        self.content_features = [
            'duration', 'quality', 'engagement_rate', 'view_count', 
            'like_ratio', 'comment_count', 'share_count', 'upload_date'
        ]
    
    def generate_recommendations(self, user_id: str, 
                               preferences: Dict[str, Any] = None,
                               video_history: List[Dict] = None,
                               count: int = 10,
                               algorithm: str = 'hybrid') -> Dict[str, Any]:
        """Generate personalized video recommendations"""
        
        # Initialize user profile if needed
        self._initialize_user_profile(user_id, preferences, video_history)
        
        # Generate recommendations using different algorithms
        recommendations = []
        
        if algorithm == 'hybrid' or algorithm == 'all':
            # Combine multiple recommendation approaches
            collab_recs = self._collaborative_filtering(user_id, count // 2)
            content_recs = self._content_based_filtering(user_id, count // 2)
            trending_recs = self._trending_recommendations(count // 4)
            deep_recs = self._deep_learning_recommendations(user_id, count // 4)
            
            # Merge and deduplicate
            all_recs = collab_recs + content_recs + trending_recs + deep_recs
            recommendations = self._merge_and_rank(all_recs, count)
            
        elif algorithm == 'collaborative':
            recommendations = self._collaborative_filtering(user_id, count)
        elif algorithm == 'content_based':
            recommendations = self._content_based_filtering(user_id, count)
        elif algorithm == 'trending':
            recommendations = self._trending_recommendations(count)
        elif algorithm == 'deep_learning':
            recommendations = self._deep_learning_recommendations(user_id, count)
        
        # Add recommendation metadata
        recommendation_metadata = self._generate_recommendation_metadata(
            user_id, algorithm, recommendations
        )
        
        return {
            'recommendations': recommendations,
            'user_id': user_id,
            'algorithm_used': algorithm,
            'metadata': recommendation_metadata,
            'generated_at': datetime.utcnow().isoformat(),
            'model_version': self.model_version
        }
    
    def _initialize_user_profile(self, user_id: str, 
                                preferences: Optional[Dict] = None,
                                video_history: Optional[List] = None):
        """Initialize or update user profile"""
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'preferences': preferences or {},
                'viewing_history': video_history or [],
                'category_scores': defaultdict(float),
                'feature_preferences': defaultdict(float),
                'created_at': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat()
            }
        
        # Update profile with new information
        profile = self.user_profiles[user_id]
        
        if preferences:
            profile['preferences'].update(preferences)
        
        if video_history:
            profile['viewing_history'].extend(video_history)
            self._update_user_preferences(user_id, video_history)
        
        profile['last_updated'] = datetime.utcnow().isoformat()
    
    def _update_user_preferences(self, user_id: str, video_history: List[Dict]):
        """Update user preferences based on viewing history"""
        profile = self.user_profiles[user_id]
        
        for video in video_history:
            category = video.get('category', 'unknown')
            rating = video.get('rating', 3.0)  # Default neutral rating
            watch_time = video.get('watch_time', 0)
            duration = video.get('duration', 300)
            
            # Update category preferences
            completion_rate = min(watch_time / max(duration, 1), 1.0)
            preference_score = (rating / 5.0) * completion_rate
            profile['category_scores'][category] += preference_score
            
            # Update feature preferences
            if video.get('high_quality', False):
                profile['feature_preferences']['quality'] += preference_score
            if video.get('short_form', False):
                profile['feature_preferences']['short_content'] += preference_score
    
    def _collaborative_filtering(self, user_id: str, count: int) -> List[Dict[str, Any]]:
        """Generate recommendations using collaborative filtering"""
        
        # Find similar users based on viewing patterns
        similar_users = self._find_similar_users(user_id)
        
        # Get recommendations from similar users
        recommendations = []
        seen_videos = set()
        
        user_history = set(v.get('video_id') for v in self.user_profiles.get(user_id, {}).get('viewing_history', []))
        
        for similar_user_id, similarity_score in similar_users[:10]:
            similar_user_videos = self.user_profiles.get(similar_user_id, {}).get('viewing_history', [])
            
            for video in similar_user_videos:
                video_id = video.get('video_id')
                if video_id not in user_history and video_id not in seen_videos:
                    recommendation = self._create_recommendation(
                        video, 'collaborative_filtering', similarity_score
                    )
                    recommendations.append(recommendation)
                    seen_videos.add(video_id)
                    
                    if len(recommendations) >= count:
                        break
            
            if len(recommendations) >= count:
                break
        
        # Fill remaining slots with popular videos
        while len(recommendations) < count:
            video = self._generate_popular_video()
            if video['video_id'] not in seen_videos:
                recommendations.append(self._create_recommendation(video, 'popular', 0.5))
                seen_videos.add(video['video_id'])
        
        return recommendations[:count]
    
    def _content_based_filtering(self, user_id: str, count: int) -> List[Dict[str, Any]]:
        """Generate recommendations using content-based filtering"""
        
        user_profile = self.user_profiles.get(user_id, {})
        category_scores = user_profile.get('category_scores', {})
        
        recommendations = []
        seen_videos = set()
        
        # Generate videos based on preferred categories
        for category, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True):
            category_count = max(1, int(count * (score / sum(category_scores.values()))))
            
            for _ in range(category_count):
                video = self._generate_video_for_category(category)
                if video['video_id'] not in seen_videos:
                    recommendation = self._create_recommendation(
                        video, 'content_based', score
                    )
                    recommendations.append(recommendation)
                    seen_videos.add(video['video_id'])
        
        # Fill remaining slots
        while len(recommendations) < count:
            video = self._generate_random_video()
            if video['video_id'] not in seen_videos:
                recommendations.append(self._create_recommendation(video, 'content_based', 0.3))
                seen_videos.add(video['video_id'])
        
        return recommendations[:count]
    
    def _trending_recommendations(self, count: int) -> List[Dict[str, Any]]:
        """Generate trending video recommendations"""
        
        recommendations = []
        
        for i in range(count):
            video = self._generate_trending_video()
            recommendation = self._create_recommendation(
                video, 'trending', 0.8 + random.uniform(-0.2, 0.2)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _deep_learning_recommendations(self, user_id: str, count: int) -> List[Dict[str, Any]]:
        """Generate recommendations using simulated deep learning model"""
        
        # Simulate deep learning model predictions
        user_embedding = self._generate_user_embedding(user_id)
        
        recommendations = []
        
        for i in range(count):
            video = self._generate_video_from_embedding(user_embedding)
            confidence = self._calculate_embedding_similarity(user_embedding, video['embedding'])
            
            recommendation = self._create_recommendation(
                video, 'deep_learning', confidence
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _find_similar_users(self, user_id: str) -> List[Tuple[str, float]]:
        """Find users with similar viewing patterns"""
        
        target_profile = self.user_profiles.get(user_id, {})
        target_categories = target_profile.get('category_scores', {})
        
        similar_users = []
        
        # Generate some similar users for simulation
        for i in range(20):
            similar_user_id = f"user_{hashlib.md5(f'{user_id}_{i}'.encode()).hexdigest()[:8]}"
            
            # Calculate similarity based on category preferences
            similarity = self._calculate_user_similarity(target_categories, similar_user_id)
            similar_users.append((similar_user_id, similarity))
            
            # Create similar user profile if it doesn't exist
            if similar_user_id not in self.user_profiles:
                self.user_profiles[similar_user_id] = self._generate_similar_user_profile(target_profile)
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return similar_users
    
    def _calculate_user_similarity(self, target_categories: Dict[str, float], other_user_id: str) -> float:
        """Calculate similarity between users based on preferences"""
        
        # Generate simulated preferences for other user
        hash_input = other_user_id.encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest()[:8], 16)
        
        # Create synthetic category preferences
        other_categories = {}
        for i, category in enumerate(self.content_categories):
            # Use hash to create deterministic but varied preferences
            pref_value = ((hash_value + i * 17) % 100) / 100.0
            other_categories[category] = pref_value
        
        # Calculate cosine similarity
        return self._cosine_similarity(target_categories, other_categories)
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two preference vectors"""
        
        all_categories = set(vec1.keys()) | set(vec2.keys())
        
        dot_product = sum(vec1.get(cat, 0) * vec2.get(cat, 0) for cat in all_categories)
        norm1 = math.sqrt(sum(vec1.get(cat, 0) ** 2 for cat in all_categories))
        norm2 = math.sqrt(sum(vec2.get(cat, 0) ** 2 for cat in all_categories))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _generate_similar_user_profile(self, target_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a similar user profile for simulation"""
        
        target_categories = target_profile.get('category_scores', {})
        
        # Create similar but not identical preferences
        similar_categories = {}
        for category, score in target_categories.items():
            # Add some noise to create similar but distinct preferences
            noise = random.uniform(-0.2, 0.2)
            similar_categories[category] = max(0, score + noise)
        
        # Add some random videos to viewing history
        viewing_history = []
        for _ in range(random.randint(5, 20)):
            video = self._generate_random_video()
            viewing_history.append(video)
        
        return {
            'preferences': {},
            'viewing_history': viewing_history,
            'category_scores': similar_categories,
            'feature_preferences': defaultdict(float),
            'created_at': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _generate_user_embedding(self, user_id: str) -> List[float]:
        """Generate user embedding vector for deep learning recommendations"""
        
        # Simulate user embedding based on user ID and profile
        hash_input = user_id.encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest()[:16], 16)
        
        embedding_size = 64
        embedding = []
        
        for i in range(embedding_size):
            # Generate normalized embedding values
            value = ((hash_value + i * 31) % 1000) / 1000.0 - 0.5
            embedding.append(value)
        
        return embedding
    
    def _generate_video_from_embedding(self, user_embedding: List[float]) -> Dict[str, Any]:
        """Generate video recommendation based on user embedding"""
        
        # Simulate video generation that matches user embedding
        video_id = hashlib.md5(f"embedding_{random.random()}".encode()).hexdigest()[:12]
        
        # Generate video embedding that has some similarity to user embedding
        video_embedding = []
        for i, user_val in enumerate(user_embedding):
            # Add controlled noise to create similar but distinct embedding
            noise = random.uniform(-0.3, 0.3)
            video_val = user_val + noise
            video_embedding.append(max(-1, min(1, video_val)))  # Clamp to [-1, 1]
        
        # Create video metadata
        category = random.choice(self.content_categories)
        
        video = {
            'video_id': video_id,
            'title': f"AI Recommended: {category.title()} Content",
            'category': category,
            'duration': random.randint(120, 1800),
            'view_count': random.randint(1000, 100000),
            'like_count': random.randint(50, 5000),
            'upload_date': (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
            'creator': f"Creator{random.randint(1, 1000)}",
            'thumbnail_url': f"https://example.com/thumb_{video_id}.jpg",
            'embedding': video_embedding,
            'tags': [category, 'recommended', 'ai-generated']
        }
        
        return video
    
    def _calculate_embedding_similarity(self, user_embedding: List[float], video_embedding: List[float]) -> float:
        """Calculate similarity between user and video embeddings"""
        
        if len(user_embedding) != len(video_embedding):
            return 0.5
        
        # Calculate cosine similarity
        dot_product = sum(u * v for u, v in zip(user_embedding, video_embedding))
        user_norm = math.sqrt(sum(u ** 2 for u in user_embedding))
        video_norm = math.sqrt(sum(v ** 2 for v in video_embedding))
        
        if user_norm == 0 or video_norm == 0:
            return 0.5
        
        similarity = dot_product / (user_norm * video_norm)
        # Convert from [-1, 1] to [0, 1]
        return (similarity + 1) / 2
    
    def _generate_popular_video(self) -> Dict[str, Any]:
        """Generate a popular video for recommendations"""
        
        video_id = hashlib.md5(f"popular_{random.random()}".encode()).hexdigest()[:12]
        category = random.choice(self.content_categories)
        
        return {
            'video_id': video_id,
            'title': f"Popular {category.title()} Video",
            'category': category,
            'duration': random.randint(300, 1200),
            'view_count': random.randint(50000, 500000),
            'like_count': random.randint(2000, 25000),
            'engagement_rate': round(random.uniform(0.15, 0.35), 3),
            'upload_date': (datetime.utcnow() - timedelta(days=random.randint(1, 7))).isoformat(),
            'creator': f"PopularCreator{random.randint(1, 100)}",
            'thumbnail_url': f"https://example.com/thumb_{video_id}.jpg",
            'tags': [category, 'popular', 'trending']
        }
    
    def _generate_video_for_category(self, category: str) -> Dict[str, Any]:
        """Generate a video for a specific category"""
        
        video_id = hashlib.md5(f"{category}_{random.random()}".encode()).hexdigest()[:12]
        
        return {
            'video_id': video_id,
            'title': f"Great {category.title()} Content",
            'category': category,
            'duration': random.randint(180, 900),
            'view_count': random.randint(1000, 50000),
            'like_count': random.randint(100, 2500),
            'engagement_rate': round(random.uniform(0.1, 0.25), 3),
            'upload_date': (datetime.utcnow() - timedelta(days=random.randint(1, 14))).isoformat(),
            'creator': f"{category.title()}Creator{random.randint(1, 200)}",
            'thumbnail_url': f"https://example.com/thumb_{video_id}.jpg",
            'tags': [category, 'content-based']
        }
    
    def _generate_random_video(self) -> Dict[str, Any]:
        """Generate a random video"""
        
        video_id = hashlib.md5(f"random_{random.random()}".encode()).hexdigest()[:12]
        category = random.choice(self.content_categories)
        
        return {
            'video_id': video_id,
            'title': f"Random {category.title()} Video",
            'category': category,
            'duration': random.randint(120, 1800),
            'view_count': random.randint(100, 10000),
            'like_count': random.randint(10, 500),
            'engagement_rate': round(random.uniform(0.05, 0.15), 3),
            'upload_date': (datetime.utcnow() - timedelta(days=random.randint(1, 60))).isoformat(),
            'creator': f"Creator{random.randint(1, 500)}",
            'thumbnail_url': f"https://example.com/thumb_{video_id}.jpg",
            'tags': [category, 'random']
        }
    
    def _generate_trending_video(self) -> Dict[str, Any]:
        """Generate a trending video"""
        
        video_id = hashlib.md5(f"trending_{random.random()}".encode()).hexdigest()[:12]
        category = random.choice(self.content_categories)
        
        return {
            'video_id': video_id,
            'title': f"Trending: {category.title()} Must-Watch",
            'category': category,
            'duration': random.randint(240, 800),
            'view_count': random.randint(100000, 1000000),
            'like_count': random.randint(5000, 50000),
            'engagement_rate': round(random.uniform(0.2, 0.4), 3),
            'upload_date': (datetime.utcnow() - timedelta(days=random.randint(1, 3))).isoformat(),
            'creator': f"TrendingCreator{random.randint(1, 50)}",
            'thumbnail_url': f"https://example.com/thumb_{video_id}.jpg",
            'trending_score': round(random.uniform(0.8, 1.0), 3),
            'tags': [category, 'trending', 'viral']
        }
    
    def _create_recommendation(self, video: Dict[str, Any], 
                             source: str, confidence: float) -> Dict[str, Any]:
        """Create a recommendation object with metadata"""
        
        # Calculate predicted rating
        predicted_rating = self._predict_user_rating(video, confidence)
        
        # Generate explanation
        explanation = self._generate_explanation(video, source, confidence)
        
        recommendation = {
            'video_id': video['video_id'],
            'title': video['title'],
            'category': video['category'],
            'duration': video['duration'],
            'thumbnail_url': video.get('thumbnail_url'),
            'creator': video.get('creator'),
            'predicted_rating': predicted_rating,
            'confidence': round(confidence, 3),
            'recommendation_source': source,
            'explanation': explanation,
            'metadata': {
                'view_count': video.get('view_count', 0),
                'like_count': video.get('like_count', 0),
                'engagement_rate': video.get('engagement_rate', 0),
                'upload_date': video.get('upload_date'),
                'tags': video.get('tags', [])
            }
        }
        
        return recommendation
    
    def _predict_user_rating(self, video: Dict[str, Any], confidence: float) -> float:
        """Predict user rating for a video"""
        
        base_rating = 3.0  # Neutral baseline
        
        # Adjust based on video popularity
        view_count = video.get('view_count', 0)
        if view_count > 100000:
            base_rating += 0.5
        elif view_count > 10000:
            base_rating += 0.3
        
        # Adjust based on engagement
        engagement_rate = video.get('engagement_rate', 0)
        if engagement_rate > 0.2:
            base_rating += 0.4
        elif engagement_rate > 0.1:
            base_rating += 0.2
        
        # Adjust based on confidence
        rating_adjustment = (confidence - 0.5) * 2  # Scale confidence to [-1, 1]
        final_rating = base_rating + rating_adjustment
        
        # Clamp to valid range
        return round(max(1.0, min(5.0, final_rating)), 1)
    
    def _generate_explanation(self, video: Dict[str, Any], 
                            source: str, confidence: float) -> str:
        """Generate explanation for recommendation"""
        
        explanations = {
            'collaborative_filtering': f"Recommended because users with similar preferences enjoyed this {video['category']} content",
            'content_based': f"Recommended based on your interest in {video['category']} videos",
            'trending': f"Currently trending {video['category']} content with high engagement",
            'deep_learning': f"AI model predicts you'll enjoy this {video['category']} video",
            'popular': f"Popular {video['category']} content that many users enjoy"
        }
        
        base_explanation = explanations.get(source, "Recommended for you")
        
        # Add confidence-based qualifier
        if confidence > 0.8:
            qualifier = " (highly recommended)"
        elif confidence > 0.6:
            qualifier = " (good match)"
        else:
            qualifier = " (might interest you)"
        
        return base_explanation + qualifier
    
    def _merge_and_rank(self, recommendations: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        """Merge recommendations from different sources and rank them"""
        
        # Remove duplicates based on video_id
        seen_ids = set()
        unique_recs = []
        
        for rec in recommendations:
            if rec['video_id'] not in seen_ids:
                unique_recs.append(rec)
                seen_ids.add(rec['video_id'])
        
        # Sort by weighted score (predicted rating * confidence)
        def score_function(rec):
            rating_score = (rec['predicted_rating'] - 1) / 4  # Normalize to [0, 1]
            confidence_score = rec['confidence']
            source_weight = self.algorithms.get(rec['recommendation_source'], 0.25)
            return rating_score * confidence_score * source_weight
        
        unique_recs.sort(key=score_function, reverse=True)
        
        return unique_recs[:count]
    
    def _generate_recommendation_metadata(self, user_id: str, algorithm: str, 
                                        recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate metadata about the recommendation process"""
        
        # Calculate distribution by source
        source_distribution = Counter(rec['recommendation_source'] for rec in recommendations)
        
        # Calculate average confidence
        avg_confidence = sum(rec['confidence'] for rec in recommendations) / len(recommendations) if recommendations else 0
        
        # Calculate category diversity
        categories = [rec['category'] for rec in recommendations]
        category_diversity = len(set(categories)) / len(categories) if categories else 0
        
        return {
            'total_recommendations': len(recommendations),
            'average_confidence': round(avg_confidence, 3),
            'source_distribution': dict(source_distribution),
            'category_diversity': round(category_diversity, 3),
            'algorithm_weights': self.algorithms if algorithm == 'hybrid' else {algorithm: 1.0},
            'user_profile_exists': user_id in self.user_profiles,
            'recommendation_quality_score': self._calculate_quality_score(recommendations)
        }
    
    def _calculate_quality_score(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score for recommendations"""
        
        if not recommendations:
            return 0.0
        
        # Factors contributing to quality
        avg_confidence = sum(rec['confidence'] for rec in recommendations) / len(recommendations)
        avg_rating = sum(rec['predicted_rating'] for rec in recommendations) / len(recommendations)
        rating_variance = sum((rec['predicted_rating'] - avg_rating) ** 2 for rec in recommendations) / len(recommendations)
        
        # Normalize rating to [0, 1]
        normalized_rating = (avg_rating - 1) / 4
        
        # Quality decreases with high variance (we want consistent quality)
        variance_penalty = min(rating_variance / 2, 0.5)
        
        quality_score = (avg_confidence + normalized_rating) / 2 - variance_penalty
        
        return round(max(0, min(1, quality_score)), 3)
    
    def update_user_feedback(self, user_id: str, video_id: str, 
                           rating: float, watch_time: int, 
                           total_duration: int) -> Dict[str, Any]:
        """Update user profile based on feedback"""
        
        if user_id not in self.user_profiles:
            self._initialize_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        
        # Create feedback entry
        feedback = {
            'video_id': video_id,
            'rating': rating,
            'watch_time': watch_time,
            'duration': total_duration,
            'completion_rate': watch_time / max(total_duration, 1),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add to viewing history
        profile['viewing_history'].append(feedback)
        
        # Update preferences based on feedback
        # This would normally involve finding the video's category and updating scores
        # For simulation, we'll generate a category
        categories = ['educational', 'entertainment', 'tutorial']
        category = random.choice(categories)
        
        completion_rate = feedback['completion_rate']
        preference_score = (rating / 5.0) * completion_rate
        profile['category_scores'][category] += preference_score
        
        profile['last_updated'] = datetime.utcnow().isoformat()
        
        return {
            'status': 'updated',
            'user_id': user_id,
            'feedback_processed': True,
            'updated_preferences': dict(profile['category_scores'])
        }
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for a user's recommendation performance"""
        
        profile = self.user_profiles.get(user_id, {})
        viewing_history = profile.get('viewing_history', [])
        
        if not viewing_history:
            return {'error': 'No viewing history found for user'}
        
        # Calculate analytics
        total_videos = len(viewing_history)
        avg_rating = sum(v.get('rating', 3.0) for v in viewing_history) / total_videos
        avg_completion = sum(v.get('completion_rate', 0.5) for v in viewing_history) / total_videos
        
        # Category preferences
        category_stats = defaultdict(list)
        for video in viewing_history:
            category = video.get('category', 'unknown')
            category_stats[category].append(video.get('rating', 3.0))
        
        category_preferences = {}
        for category, ratings in category_stats.items():
            category_preferences[category] = {
                'avg_rating': round(sum(ratings) / len(ratings), 2),
                'video_count': len(ratings),
                'preference_score': round(sum(ratings) / (len(ratings) * 5), 3)
            }
        
        return {
            'user_id': user_id,
            'total_videos_watched': total_videos,
            'average_rating': round(avg_rating, 2),
            'average_completion_rate': round(avg_completion, 3),
            'category_preferences': category_preferences,
            'recommendation_accuracy': round(random.uniform(0.7, 0.9), 3),  # Simulated
            'engagement_score': round((avg_rating / 5) * avg_completion, 3),
            'profile_maturity': 'high' if total_videos > 50 else 'medium' if total_videos > 10 else 'low'
        }