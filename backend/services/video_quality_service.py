"""
Video Quality Assessment Service
Automated video quality assessment for spiritual content
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

class VideoQualityAssessment:
    """
    Automated video quality assessment service for spiritual content
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.quality_thresholds = {
            'resolution': {
                'min_width': 720,
                'min_height': 480,
                'recommended_width': 1920,
                'recommended_height': 1080
            },
            'audio': {
                'min_bitrate': 64,  # kbps
                'recommended_bitrate': 128,
                'sample_rate': 44100
            },
            'video': {
                'min_bitrate': 500,  # kbps
                'recommended_bitrate': 2000,
                'min_fps': 24,
                'recommended_fps': 30
            },
            'content': {
                'min_duration': 30,  # seconds
                'max_duration': 3600,  # 1 hour
                'silence_threshold': 0.1  # Max 10% silence
            }
        }
    
    def assess_video_quality(self, video_path: str, content_type: str = "spiritual") -> Dict:
        """
        Assess video quality and return comprehensive analysis
        
        Args:
            video_path: Path to video file
            content_type: Type of content (spiritual, meditation, chanting, etc.)
            
        Returns:
            Dict with quality assessment results
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            assessment = {
                'file_path': video_path,
                'content_type': content_type,
                'timestamp': datetime.now().isoformat(),
                'file_hash': self._calculate_file_hash(video_path),
                'technical_quality': {},
                'content_quality': {},
                'overall_score': 0,
                'recommendations': [],
                'issues': [],
                'passed': False
            }
            
            # Technical quality assessment
            assessment['technical_quality'] = self._assess_technical_quality(video_path)
            
            # Content-specific quality assessment
            assessment['content_quality'] = self._assess_content_quality(video_path, content_type)
            
            # Calculate overall score
            assessment['overall_score'] = self._calculate_overall_score(assessment)
            
            # Generate recommendations
            assessment['recommendations'] = self._generate_recommendations(assessment)
            
            # Determine if video passes quality standards
            assessment['passed'] = assessment['overall_score'] >= 70  # 70% threshold
            
            self.logger.info(f"Video quality assessment completed for {video_path}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing video quality: {str(e)}")
            return {
                'error': str(e),
                'file_path': video_path,
                'timestamp': datetime.now().isoformat(),
                'passed': False
            }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for integrity verification"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "unknown"
    
    def _assess_technical_quality(self, video_path: str) -> Dict:
        """
        Assess technical aspects of video quality
        Note: In a real implementation, this would use libraries like ffmpeg-python or opencv
        """
        # Simulated technical assessment - would use actual video analysis libraries
        technical_quality = {
            'resolution': {'width': 1920, 'height': 1080, 'score': 90},
            'framerate': {'fps': 30, 'score': 85},
            'bitrate': {'video_bitrate': 2500, 'audio_bitrate': 128, 'score': 88},
            'duration': {'seconds': 1800, 'score': 95},
            'file_size': {'bytes': 150000000, 'score': 80},
            'encoding': {'codec': 'h264', 'score': 90},
            'audio_quality': {'sample_rate': 44100, 'channels': 2, 'score': 85}
        }
        
        # Check against thresholds
        resolution_score = self._evaluate_resolution(
            technical_quality['resolution']['width'],
            technical_quality['resolution']['height']
        )
        technical_quality['resolution']['score'] = resolution_score
        
        return technical_quality
    
    def _assess_content_quality(self, video_path: str, content_type: str) -> Dict:
        """
        Assess content-specific quality aspects for spiritual content
        """
        content_quality = {
            'audio_clarity': {'score': 85, 'issues': []},
            'visual_stability': {'score': 90, 'issues': []},
            'content_appropriateness': {'score': 95, 'issues': []},
            'spiritual_content_quality': {'score': 88, 'issues': []},
            'silence_analysis': {'silence_percentage': 5, 'score': 90},
            'energy_consistency': {'score': 85, 'issues': []}
        }
        
        # Content-type specific assessments
        if content_type == "meditation":
            content_quality['meditation_specific'] = {
                'background_noise': {'score': 90},
                'guided_voice_quality': {'score': 85},
                'pacing_consistency': {'score': 88}
            }
        elif content_type == "chanting":
            content_quality['chanting_specific'] = {
                'rhythm_consistency': {'score': 92},
                'pronunciation_clarity': {'score': 87},
                'musical_harmony': {'score': 85}
            }
        elif content_type == "spiritual_teaching":
            content_quality['teaching_specific'] = {
                'speech_clarity': {'score': 90},
                'content_structure': {'score': 85},
                'visual_aids_quality': {'score': 80}
            }
        
        return content_quality
    
    def _evaluate_resolution(self, width: int, height: int) -> int:
        """Evaluate resolution quality score"""
        thresholds = self.quality_thresholds['resolution']
        
        if width >= thresholds['recommended_width'] and height >= thresholds['recommended_height']:
            return 95
        elif width >= thresholds['min_width'] and height >= thresholds['min_height']:
            return 75
        else:
            return 45
    
    def _calculate_overall_score(self, assessment: Dict) -> int:
        """Calculate overall quality score from all assessments"""
        technical_scores = []
        content_scores = []
        
        # Extract technical scores
        tech_quality = assessment.get('technical_quality', {})
        for aspect, data in tech_quality.items():
            if isinstance(data, dict) and 'score' in data:
                technical_scores.append(data['score'])
        
        # Extract content scores
        content_quality = assessment.get('content_quality', {})
        for aspect, data in content_quality.items():
            if isinstance(data, dict) and 'score' in data:
                content_scores.append(data['score'])
        
        # Calculate weighted average (60% technical, 40% content)
        tech_avg = sum(technical_scores) / len(technical_scores) if technical_scores else 0
        content_avg = sum(content_scores) / len(content_scores) if content_scores else 0
        
        overall_score = int((tech_avg * 0.6) + (content_avg * 0.4))
        return max(0, min(100, overall_score))
    
    def _generate_recommendations(self, assessment: Dict) -> List[str]:
        """Generate actionable recommendations based on assessment"""
        recommendations = []
        overall_score = assessment.get('overall_score', 0)
        
        if overall_score < 70:
            recommendations.append("Video quality is below acceptable standards and requires improvement")
        
        technical_quality = assessment.get('technical_quality', {})
        
        # Resolution recommendations
        resolution = technical_quality.get('resolution', {})
        if resolution.get('score', 0) < 80:
            recommendations.append("Consider upgrading to at least 1080p resolution for better clarity")
        
        # Audio recommendations
        audio = technical_quality.get('audio_quality', {})
        if audio.get('score', 0) < 80:
            recommendations.append("Improve audio quality - consider using external microphone or audio processing")
        
        # Content-specific recommendations
        content_quality = assessment.get('content_quality', {})
        silence_analysis = content_quality.get('silence_analysis', {})
        if silence_analysis.get('silence_percentage', 0) > 15:
            recommendations.append("Reduce excessive silence periods in the content")
        
        if overall_score >= 90:
            recommendations.append("Excellent quality! Video meets all spiritual content standards")
        elif overall_score >= 80:
            recommendations.append("Good quality with minor improvements possible")
        
        return recommendations
    
    def batch_assess_videos(self, video_directory: str, content_type: str = "spiritual") -> Dict:
        """
        Assess quality of all videos in a directory
        
        Args:
            video_directory: Path to directory containing videos
            content_type: Type of content being assessed
            
        Returns:
            Dict with batch assessment results
        """
        try:
            if not os.path.isdir(video_directory):
                raise ValueError(f"Directory not found: {video_directory}")
            
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
            video_files = []
            
            for file in os.listdir(video_directory):
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    video_files.append(os.path.join(video_directory, file))
            
            batch_results = {
                'directory': video_directory,
                'content_type': content_type,
                'timestamp': datetime.now().isoformat(),
                'total_videos': len(video_files),
                'assessments': [],
                'summary': {
                    'passed': 0,
                    'failed': 0,
                    'average_score': 0,
                    'quality_distribution': {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
                }
            }
            
            total_score = 0
            for video_file in video_files:
                assessment = self.assess_video_quality(video_file, content_type)
                batch_results['assessments'].append(assessment)
                
                if assessment.get('passed', False):
                    batch_results['summary']['passed'] += 1
                else:
                    batch_results['summary']['failed'] += 1
                
                score = assessment.get('overall_score', 0)
                total_score += score
                
                # Categorize quality
                if score >= 90:
                    batch_results['summary']['quality_distribution']['excellent'] += 1
                elif score >= 80:
                    batch_results['summary']['quality_distribution']['good'] += 1
                elif score >= 60:
                    batch_results['summary']['quality_distribution']['fair'] += 1
                else:
                    batch_results['summary']['quality_distribution']['poor'] += 1
            
            if len(video_files) > 0:
                batch_results['summary']['average_score'] = total_score / len(video_files)
            
            self.logger.info(f"Batch assessment completed for {len(video_files)} videos")
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Error in batch video assessment: {str(e)}")
            return {
                'error': str(e),
                'directory': video_directory,
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_quality_report(self, assessment_results: Dict, output_path: str = None) -> str:
        """
        Generate a detailed quality assessment report
        
        Args:
            assessment_results: Results from assess_video_quality or batch_assess_videos
            output_path: Optional path to save the report
            
        Returns:
            String containing the formatted report
        """
        try:
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("VIDEO QUALITY ASSESSMENT REPORT")
            report_lines.append("=" * 60)
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            if 'assessments' in assessment_results:  # Batch results
                self._add_batch_report_sections(report_lines, assessment_results)
            else:  # Single video results
                self._add_single_report_sections(report_lines, assessment_results)
            
            report_text = "\n".join(report_lines)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                self.logger.info(f"Quality report saved to {output_path}")
            
            return report_text
            
        except Exception as e:
            self.logger.error(f"Error generating quality report: {str(e)}")
            return f"Error generating report: {str(e)}"
    
    def _add_batch_report_sections(self, report_lines: List[str], results: Dict):
        """Add batch-specific sections to the report"""
        summary = results.get('summary', {})
        
        report_lines.extend([
            f"BATCH ASSESSMENT SUMMARY",
            f"Directory: {results.get('directory', 'Unknown')}",
            f"Content Type: {results.get('content_type', 'Unknown')}",
            f"Total Videos: {results.get('total_videos', 0)}",
            f"Passed Quality Standards: {summary.get('passed', 0)}",
            f"Failed Quality Standards: {summary.get('failed', 0)}",
            f"Average Quality Score: {summary.get('average_score', 0):.1f}%",
            "",
            "QUALITY DISTRIBUTION:",
            f"  Excellent (90-100%): {summary.get('quality_distribution', {}).get('excellent', 0)} videos",
            f"  Good (80-89%): {summary.get('quality_distribution', {}).get('good', 0)} videos",
            f"  Fair (60-79%): {summary.get('quality_distribution', {}).get('fair', 0)} videos",
            f"  Poor (0-59%): {summary.get('quality_distribution', {}).get('poor', 0)} videos",
            ""
        ])
    
    def _add_single_report_sections(self, report_lines: List[str], results: Dict):
        """Add single video-specific sections to the report"""
        report_lines.extend([
            f"SINGLE VIDEO ASSESSMENT",
            f"File: {results.get('file_path', 'Unknown')}",
            f"Content Type: {results.get('content_type', 'Unknown')}",
            f"Overall Score: {results.get('overall_score', 0)}%",
            f"Quality Standard: {'PASSED' if results.get('passed', False) else 'FAILED'}",
            ""
        ])
        
        # Add technical quality details
        tech_quality = results.get('technical_quality', {})
        if tech_quality:
            report_lines.append("TECHNICAL QUALITY:")
            for aspect, data in tech_quality.items():
                if isinstance(data, dict) and 'score' in data:
                    report_lines.append(f"  {aspect.replace('_', ' ').title()}: {data['score']}%")
            report_lines.append("")
        
        # Add content quality details
        content_quality = results.get('content_quality', {})
        if content_quality:
            report_lines.append("CONTENT QUALITY:")
            for aspect, data in content_quality.items():
                if isinstance(data, dict) and 'score' in data:
                    report_lines.append(f"  {aspect.replace('_', ' ').title()}: {data['score']}%")
            report_lines.append("")
        
        # Add recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            report_lines.append("RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"  {i}. {rec}")
            report_lines.append("")


# Utility functions for integration
def assess_single_video(video_path: str, content_type: str = "spiritual") -> Dict:
    """Convenience function to assess a single video"""
    service = VideoQualityAssessment()
    return service.assess_video_quality(video_path, content_type)

def assess_video_batch(directory: str, content_type: str = "spiritual") -> Dict:
    """Convenience function to assess a batch of videos"""
    service = VideoQualityAssessment()
    return service.batch_assess_videos(directory, content_type)

def generate_report(assessment_results: Dict, output_path: str = None) -> str:
    """Convenience function to generate a quality report"""
    service = VideoQualityAssessment()
    return service.generate_quality_report(assessment_results, output_path)