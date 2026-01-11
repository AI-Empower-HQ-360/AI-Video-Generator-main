"""
Automated Video Thumbnail Generation Service
Generates appropriate thumbnails for spiritual video content
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import base64

class VideoThumbnailGenerator:
    """
    Automated thumbnail generation service for spiritual video content
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Thumbnail generation settings
        self.thumbnail_settings = {
            'dimensions': {
                'youtube': {'width': 1280, 'height': 720},
                'instagram': {'width': 1080, 'height': 1080},
                'facebook': {'width': 1200, 'height': 630},
                'twitter': {'width': 1200, 'height': 675},
                'standard': {'width': 1920, 'height': 1080}
            },
            'quality': 85,
            'formats': ['jpg', 'png', 'webp'],
            'frame_selection': {
                'method': 'intelligent',  # 'intelligent', 'time_based', 'key_frames'
                'avoid_transitions': True,
                'prefer_stable_frames': True,
                'face_detection': True
            }
        }
        
        # Spiritual content overlay templates
        self.overlay_templates = {
            'meditation': {
                'background_color': '#1a1a2e',
                'text_color': '#eee6ce',
                'accent_color': '#16213e',
                'font_style': 'peaceful',
                'decorative_elements': ['lotus', 'mandala', 'zen_circle']
            },
            'chanting': {
                'background_color': '#2c1810',
                'text_color': '#f4e4bc',
                'accent_color': '#8b4513',
                'font_style': 'traditional',
                'decorative_elements': ['om_symbol', 'sanskrit', 'sound_waves']
            },
            'spiritual_teaching': {
                'background_color': '#0f2027',
                'text_color': '#ffffff',
                'accent_color': '#2c5364',
                'font_style': 'elegant',
                'decorative_elements': ['wisdom_symbols', 'light_rays', 'sacred_geometry']
            },
            'yoga': {
                'background_color': '#1a3b3a',
                'text_color': '#f0f8e8',
                'accent_color': '#4a7c59',
                'font_style': 'natural',
                'decorative_elements': ['nature_elements', 'balance_symbols', 'energy_flow']
            }
        }
    
    def generate_thumbnail(self, video_path: str, content_type: str = "spiritual", 
                          platform: str = "standard", custom_settings: Dict = None) -> Dict:
        """
        Generate thumbnail for a video file
        
        Args:
            video_path: Path to the video file
            content_type: Type of spiritual content
            platform: Target platform for thumbnail
            custom_settings: Override default settings
            
        Returns:
            Dict with generation results and thumbnail paths
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            settings = custom_settings or {}
            platform_settings = self.thumbnail_settings['dimensions'].get(platform, 
                                                                         self.thumbnail_settings['dimensions']['standard'])
            
            result = {
                'video_path': video_path,
                'content_type': content_type,
                'platform': platform,
                'timestamp': datetime.now().isoformat(),
                'settings_used': platform_settings,
                'thumbnails_generated': [],
                'selected_thumbnail': None,
                'generation_metadata': {},
                'success': False
            }
            
            # Analyze video for optimal frame selection
            frame_analysis = self._analyze_video_frames(video_path, content_type)
            result['generation_metadata']['frame_analysis'] = frame_analysis
            
            # Generate multiple thumbnail candidates
            thumbnail_candidates = self._generate_thumbnail_candidates(
                video_path, content_type, platform_settings, frame_analysis
            )
            
            # Apply content-appropriate overlays and styling
            styled_thumbnails = self._apply_spiritual_styling(
                thumbnail_candidates, content_type, platform
            )
            
            # Select best thumbnail using AI-powered assessment
            best_thumbnail = self._select_optimal_thumbnail(
                styled_thumbnails, content_type, platform
            )
            
            result['thumbnails_generated'] = styled_thumbnails
            result['selected_thumbnail'] = best_thumbnail
            result['success'] = True
            
            self.logger.info(f"Thumbnail generation completed for {video_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating thumbnail: {str(e)}")
            return {
                'error': str(e),
                'video_path': video_path,
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    def _analyze_video_frames(self, video_path: str, content_type: str) -> Dict:
        """
        Analyze video frames to identify optimal thumbnail candidates
        Note: In real implementation, would use libraries like opencv-python or ffmpeg
        """
        # Simulated frame analysis - would use actual video processing libraries
        analysis = {
            'total_frames': 7200,  # 30 fps * 240 seconds
            'duration_seconds': 240,
            'fps': 30,
            'resolution': {'width': 1920, 'height': 1080},
            'optimal_frame_timestamps': [],
            'scene_changes': [],
            'stability_scores': {},
            'content_characteristics': {}
        }
        
        # Identify key timestamps for thumbnail extraction
        if content_type == "meditation":
            # For meditation, prefer calm, centered moments
            analysis['optimal_frame_timestamps'] = [30, 60, 120, 180]  # seconds
            analysis['content_characteristics'] = {
                'preferred_composition': 'centered',
                'avoid_movement': True,
                'prefer_calm_expressions': True
            }
        elif content_type == "chanting":
            # For chanting, capture moments of expression
            analysis['optimal_frame_timestamps'] = [45, 90, 135, 200]
            analysis['content_characteristics'] = {
                'preferred_composition': 'close_up',
                'capture_expression': True,
                'show_instruments': True
            }
        elif content_type == "spiritual_teaching":
            # For teaching, show clear speaker visibility
            analysis['optimal_frame_timestamps'] = [60, 120, 180, 220]
            analysis['content_characteristics'] = {
                'preferred_composition': 'medium_shot',
                'clear_speaker_visibility': True,
                'show_gestures': True
            }
        elif content_type == "yoga":
            # For yoga, show poses and positions
            analysis['optimal_frame_timestamps'] = [40, 80, 160, 200]
            analysis['content_characteristics'] = {
                'preferred_composition': 'full_body',
                'show_pose_clarity': True,
                'demonstrate_alignment': True
            }
        else:
            # Default spiritual content
            analysis['optimal_frame_timestamps'] = [50, 100, 150, 200]
            analysis['content_characteristics'] = {
                'preferred_composition': 'balanced',
                'spiritual_symbolism': True,
                'peaceful_imagery': True
            }
        
        # Simulate stability analysis
        for timestamp in analysis['optimal_frame_timestamps']:
            analysis['stability_scores'][str(timestamp)] = 85 + (timestamp % 15)  # Simulated score
        
        return analysis
    
    def _generate_thumbnail_candidates(self, video_path: str, content_type: str, 
                                     dimensions: Dict, frame_analysis: Dict) -> List[Dict]:
        """Generate multiple thumbnail candidates from optimal frames"""
        candidates = []
        
        for i, timestamp in enumerate(frame_analysis['optimal_frame_timestamps']):
            # Simulated thumbnail generation - would extract actual frames
            candidate = {
                'candidate_id': i + 1,
                'timestamp': timestamp,
                'dimensions': dimensions,
                'file_path': f"/tmp/thumbnail_{i+1}_{timestamp}s.jpg",  # Simulated path
                'extraction_method': 'key_frame',
                'quality_score': frame_analysis['stability_scores'].get(str(timestamp), 80),
                'composition_analysis': {
                    'focal_point': 'center',
                    'lighting_quality': 85,
                    'clarity_score': 88,
                    'aesthetic_appeal': 82
                },
                'base64_preview': self._generate_sample_thumbnail_data(content_type, i)
            }
            candidates.append(candidate)
        
        return candidates
    
    def _generate_sample_thumbnail_data(self, content_type: str, index: int) -> str:
        """Generate sample base64 thumbnail data for demonstration"""
        # This would contain actual image data in a real implementation
        sample_data = f"thumbnail_{content_type}_{index}_placeholder_data"
        return base64.b64encode(sample_data.encode()).decode()
    
    def _apply_spiritual_styling(self, candidates: List[Dict], content_type: str, 
                               platform: str) -> List[Dict]:
        """Apply spiritual content-appropriate styling to thumbnails"""
        styled_thumbnails = []
        template = self.overlay_templates.get(content_type, 
                                            self.overlay_templates['spiritual_teaching'])
        
        for candidate in candidates:
            styled_candidate = candidate.copy()
            
            # Apply styling metadata (would apply actual image processing)
            styling = {
                'overlay_template': template,
                'text_overlay': self._generate_text_overlay(content_type, platform),
                'color_adjustments': {
                    'saturation': 1.1,
                    'brightness': 1.05,
                    'contrast': 1.15,
                    'warmth': 1.08
                },
                'decorative_elements': template['decorative_elements'],
                'border_style': {
                    'type': 'subtle_gradient',
                    'width': 2,
                    'color': template['accent_color']
                }
            }
            
            styled_candidate['styling_applied'] = styling
            styled_candidate['final_path'] = f"/tmp/styled_thumbnail_{candidate['candidate_id']}.jpg"
            
            # Recalculate quality score with styling
            base_score = candidate.get('quality_score', 80)
            styling_bonus = self._calculate_styling_bonus(content_type, platform)
            styled_candidate['final_quality_score'] = min(100, base_score + styling_bonus)
            
            styled_thumbnails.append(styled_candidate)
        
        return styled_thumbnails
    
    def _generate_text_overlay(self, content_type: str, platform: str) -> Dict:
        """Generate appropriate text overlay for the thumbnail"""
        text_overlays = {
            'meditation': {
                'title_style': 'peaceful',
                'subtitle_style': 'minimal',
                'font_size_ratio': 0.08,  # Relative to image height
                'position': 'bottom_center',
                'sample_text': 'Guided Meditation'
            },
            'chanting': {
                'title_style': 'traditional',
                'subtitle_style': 'ornate',
                'font_size_ratio': 0.09,
                'position': 'top_center',
                'sample_text': 'Sacred Chanting'
            },
            'spiritual_teaching': {
                'title_style': 'elegant',
                'subtitle_style': 'clean',
                'font_size_ratio': 0.07,
                'position': 'bottom_left',
                'sample_text': 'Spiritual Wisdom'
            },
            'yoga': {
                'title_style': 'natural',
                'subtitle_style': 'flowing',
                'font_size_ratio': 0.08,
                'position': 'top_right',
                'sample_text': 'Yoga Practice'
            }
        }
        
        return text_overlays.get(content_type, text_overlays['spiritual_teaching'])
    
    def _calculate_styling_bonus(self, content_type: str, platform: str) -> int:
        """Calculate quality bonus from applied styling"""
        base_bonus = 10
        
        # Platform-specific bonuses
        platform_bonuses = {
            'youtube': 5,    # YouTube favors bold, clear thumbnails
            'instagram': 3,  # Instagram prefers aesthetic consistency
            'facebook': 4,   # Facebook values engagement-friendly designs
            'twitter': 2,    # Twitter prefers simpler designs
            'standard': 0
        }
        
        # Content-type bonuses for appropriate styling
        content_bonuses = {
            'meditation': 8,        # Calm, centered styling
            'chanting': 6,          # Traditional, expressive styling
            'spiritual_teaching': 7, # Professional, clear styling
            'yoga': 5               # Natural, flowing styling
        }
        
        total_bonus = (base_bonus + 
                      platform_bonuses.get(platform, 0) + 
                      content_bonuses.get(content_type, 0))
        
        return total_bonus
    
    def _select_optimal_thumbnail(self, styled_thumbnails: List[Dict], 
                                content_type: str, platform: str) -> Dict:
        """Select the best thumbnail using AI-powered assessment"""
        if not styled_thumbnails:
            return None
        
        # Score each thumbnail based on multiple criteria
        scored_thumbnails = []
        
        for thumbnail in styled_thumbnails:
            score_components = {
                'quality_score': thumbnail.get('final_quality_score', 0) * 0.3,
                'composition_score': self._assess_composition(thumbnail, content_type) * 0.25,
                'platform_optimization': self._assess_platform_fit(thumbnail, platform) * 0.25,
                'spiritual_appropriateness': self._assess_spiritual_appropriateness(thumbnail, content_type) * 0.2
            }
            
            total_score = sum(score_components.values())
            
            scored_thumbnail = thumbnail.copy()
            scored_thumbnail['selection_scores'] = score_components
            scored_thumbnail['final_selection_score'] = total_score
            
            scored_thumbnails.append(scored_thumbnail)
        
        # Select thumbnail with highest score
        best_thumbnail = max(scored_thumbnails, key=lambda x: x['final_selection_score'])
        
        # Add selection reasoning
        best_thumbnail['selection_reasoning'] = self._generate_selection_reasoning(
            best_thumbnail, content_type, platform
        )
        
        return best_thumbnail
    
    def _assess_composition(self, thumbnail: Dict, content_type: str) -> float:
        """Assess thumbnail composition quality"""
        composition = thumbnail.get('composition_analysis', {})
        
        # Base composition scores
        clarity = composition.get('clarity_score', 80)
        lighting = composition.get('lighting_quality', 80)
        aesthetic = composition.get('aesthetic_appeal', 80)
        
        # Content-type specific adjustments
        content_adjustments = {
            'meditation': {'focal_point_center': 10, 'calm_composition': 8},
            'chanting': {'expressive_elements': 8, 'traditional_framing': 6},
            'spiritual_teaching': {'clear_subject': 10, 'professional_framing': 7},
            'yoga': {'body_positioning': 9, 'space_utilization': 6}
        }
        
        base_score = (clarity + lighting + aesthetic) / 3
        adjustment = sum(content_adjustments.get(content_type, {}).values())
        
        return min(100, base_score + adjustment)
    
    def _assess_platform_fit(self, thumbnail: Dict, platform: str) -> float:
        """Assess how well thumbnail fits platform requirements"""
        dimensions = thumbnail.get('dimensions', {})
        styling = thumbnail.get('styling_applied', {})
        
        platform_preferences = {
            'youtube': {
                'bold_text': 20,
                'high_contrast': 15,
                'clear_focus': 20,
                'engagement_elements': 10
            },
            'instagram': {
                'aesthetic_consistency': 25,
                'visual_appeal': 20,
                'color_harmony': 15,
                'minimal_text': 10
            },
            'facebook': {
                'readable_text': 20,
                'social_engagement': 15,
                'clear_messaging': 20,
                'emotional_appeal': 15
            },
            'twitter': {
                'simple_design': 25,
                'quick_recognition': 20,
                'minimal_elements': 15,
                'clear_branding': 10
            },
            'standard': {
                'balanced_design': 20,
                'versatile_styling': 15,
                'clear_content': 20,
                'professional_quality': 15
            }
        }
        
        preferences = platform_preferences.get(platform, platform_preferences['standard'])
        return sum(preferences.values()) * 0.8  # Base platform fit score
    
    def _assess_spiritual_appropriateness(self, thumbnail: Dict, content_type: str) -> float:
        """Assess spiritual appropriateness of thumbnail"""
        styling = thumbnail.get('styling_applied', {})
        template = styling.get('overlay_template', {})
        
        appropriateness_score = 75  # Base score
        
        # Check color scheme appropriateness
        if template.get('background_color') in ['#1a1a2e', '#2c1810', '#0f2027', '#1a3b3a']:
            appropriateness_score += 10  # Appropriate spiritual colors
        
        # Check decorative elements
        decorative = template.get('decorative_elements', [])
        spiritual_elements = {'lotus', 'mandala', 'om_symbol', 'zen_circle', 'sacred_geometry'}
        if any(elem in spiritual_elements for elem in decorative):
            appropriateness_score += 15
        
        # Content-type specific checks
        if content_type == "meditation" and 'peaceful' in template.get('font_style', ''):
            appropriateness_score += 10
        elif content_type == "chanting" and 'traditional' in template.get('font_style', ''):
            appropriateness_score += 10
        
        return min(100, appropriateness_score)
    
    def _generate_selection_reasoning(self, thumbnail: Dict, content_type: str, platform: str) -> str:
        """Generate human-readable reasoning for thumbnail selection"""
        scores = thumbnail.get('selection_scores', {})
        total_score = thumbnail.get('final_selection_score', 0)
        
        reasoning_parts = []
        reasoning_parts.append(f"Selected with overall score of {total_score:.1f}/100")
        
        # Identify strongest aspects
        score_items = list(scores.items())
        score_items.sort(key=lambda x: x[1], reverse=True)
        
        top_aspect = score_items[0]
        reasoning_parts.append(f"Strongest in {top_aspect[0].replace('_', ' ')} ({top_aspect[1]:.1f}/100)")
        
        # Content-specific reasoning
        content_reasons = {
            'meditation': "Promotes peaceful, centered energy suitable for meditation content",
            'chanting': "Captures expressive, traditional elements appropriate for chanting",
            'spiritual_teaching': "Provides clear, professional presentation for educational content",
            'yoga': "Shows natural, flowing composition ideal for yoga practice"
        }
        
        if content_type in content_reasons:
            reasoning_parts.append(content_reasons[content_type])
        
        # Platform-specific reasoning
        platform_reasons = {
            'youtube': "Optimized for YouTube engagement with bold, clear design",
            'instagram': "Aesthetically pleasing for Instagram feed integration",
            'facebook': "Designed for Facebook social sharing and engagement",
            'twitter': "Simple, recognizable design perfect for Twitter",
            'standard': "Versatile design suitable for multiple platforms"
        }
        
        if platform in platform_reasons:
            reasoning_parts.append(platform_reasons[platform])
        
        return ". ".join(reasoning_parts)
    
    def generate_batch_thumbnails(self, video_list: List[Dict], 
                                 default_platform: str = "standard") -> Dict:
        """
        Generate thumbnails for multiple videos in batch
        
        Args:
            video_list: List of dicts with 'video_path', 'content_type', 'platform' (optional)
            default_platform: Default platform if not specified per video
            
        Returns:
            Dict with batch generation results
        """
        try:
            batch_results = {
                'timestamp': datetime.now().isoformat(),
                'total_videos': len(video_list),
                'results': [],
                'summary': {
                    'successful': 0,
                    'failed': 0,
                    'average_quality_score': 0,
                    'platform_distribution': {},
                    'content_type_distribution': {}
                }
            }
            
            total_quality_score = 0
            platform_counts = {}
            content_type_counts = {}
            
            for i, video_info in enumerate(video_list):
                video_path = video_info.get('video_path', '')
                content_type = video_info.get('content_type', 'spiritual')
                platform = video_info.get('platform', default_platform)
                custom_settings = video_info.get('custom_settings')
                
                result = self.generate_thumbnail(video_path, content_type, platform, custom_settings)
                result['batch_index'] = i
                batch_results['results'].append(result)
                
                # Update summary statistics
                if result.get('success', False):
                    batch_results['summary']['successful'] += 1
                    selected = result.get('selected_thumbnail', {})
                    if selected:
                        quality_score = selected.get('final_selection_score', 0)
                        total_quality_score += quality_score
                else:
                    batch_results['summary']['failed'] += 1
                
                # Track distributions
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
            
            # Calculate summary statistics
            successful_count = batch_results['summary']['successful']
            if successful_count > 0:
                batch_results['summary']['average_quality_score'] = total_quality_score / successful_count
            
            batch_results['summary']['platform_distribution'] = platform_counts
            batch_results['summary']['content_type_distribution'] = content_type_counts
            
            self.logger.info(f"Batch thumbnail generation completed: {successful_count}/{len(video_list)} successful")
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Error in batch thumbnail generation: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'total_videos': len(video_list) if video_list else 0
            }
    
    def get_thumbnail_templates(self) -> Dict:
        """Get available thumbnail templates and their configurations"""
        return {
            'overlay_templates': self.overlay_templates,
            'dimension_presets': self.thumbnail_settings['dimensions'],
            'supported_formats': self.thumbnail_settings['formats'],
            'generation_methods': ['intelligent', 'time_based', 'key_frames']
        }


# Utility functions for integration
def generate_video_thumbnail(video_path: str, content_type: str = "spiritual", 
                           platform: str = "standard") -> Dict:
    """Convenience function to generate a single video thumbnail"""
    generator = VideoThumbnailGenerator()
    return generator.generate_thumbnail(video_path, content_type, platform)

def generate_thumbnails_batch(video_list: List[Dict], platform: str = "standard") -> Dict:
    """Convenience function to generate thumbnails in batch"""
    generator = VideoThumbnailGenerator()
    return generator.generate_batch_thumbnails(video_list, platform)

def get_available_templates() -> Dict:
    """Get available thumbnail templates"""
    generator = VideoThumbnailGenerator()
    return generator.get_thumbnail_templates()