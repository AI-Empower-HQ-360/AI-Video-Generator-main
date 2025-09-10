"""
AI-Powered Content Moderation Service
Automated content moderation specifically designed for spiritual content
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import hashlib

class SpiritualContentModerator:
    """
    AI-powered content moderation service specialized for spiritual content
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Spiritual content guidelines
        self.spiritual_keywords = {
            'positive': {
                'meditation', 'mindfulness', 'peace', 'love', 'compassion', 'wisdom',
                'enlightenment', 'spiritual', 'divine', 'sacred', 'prayer', 'blessing',
                'dharma', 'karma', 'moksha', 'nirvana', 'yoga', 'mantra', 'chanting',
                'devotion', 'surrender', 'gratitude', 'forgiveness', 'healing',
                'consciousness', 'awareness', 'presence', 'tranquility', 'serenity'
            },
            'neutral': {
                'practice', 'teaching', 'learning', 'guidance', 'study', 'reading',
                'reflection', 'contemplation', 'discussion', 'sharing', 'community',
                'tradition', 'culture', 'philosophy', 'psychology', 'science',
                'nature', 'universe', 'cosmos', 'energy', 'vibration', 'frequency'
            },
            'concerning': {
                'hatred', 'violence', 'anger', 'fear', 'discrimination', 'prejudice',
                'extremism', 'fanaticism', 'superiority', 'inferiority', 'judgment',
                'condemnation', 'punishment', 'revenge', 'manipulation', 'exploitation'
            }
        }
        
        # Content quality indicators
        self.quality_indicators = {
            'high_quality': [
                'authentic teaching', 'genuine experience', 'practical wisdom',
                'compassionate guidance', 'inclusive message', 'peaceful approach',
                'balanced perspective', 'respectful dialogue', 'ethical principles'
            ],
            'low_quality': [
                'unsupported claims', 'fear-based messaging', 'exclusive doctrine',
                'commercialization', 'personality cult', 'dogmatic statements',
                'intolerant views', 'misleading information', 'harmful practices'
            ]
        }
        
        # Moderation thresholds
        self.thresholds = {
            'content_appropriateness': 80,  # Minimum score for approval
            'spiritual_alignment': 75,      # Minimum spiritual content alignment
            'quality_score': 70,            # Minimum quality threshold
            'safety_score': 85,             # Minimum safety threshold
            'authenticity_score': 70        # Minimum authenticity threshold
        }
    
    def moderate_content(self, content: str, content_type: str = "text", 
                        metadata: Dict = None) -> Dict:
        """
        Moderate content for spiritual appropriateness and quality
        
        Args:
            content: Text content to moderate (transcript, description, etc.)
            content_type: Type of content (text, audio_transcript, video_description)
            metadata: Additional metadata about the content
            
        Returns:
            Dict with moderation results
        """
        try:
            moderation_result = {
                'content_hash': hashlib.sha256(content.encode()).hexdigest()[:16],
                'content_type': content_type,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {},
                'moderation_scores': {},
                'flags': [],
                'recommendations': [],
                'approved': False,
                'confidence': 0,
                'detailed_analysis': {}
            }
            
            # Core moderation checks
            moderation_result['moderation_scores'] = self._analyze_content_scores(content)
            moderation_result['flags'] = self._identify_content_flags(content)
            moderation_result['detailed_analysis'] = self._detailed_content_analysis(content)
            
            # Calculate overall confidence and approval
            moderation_result['confidence'] = self._calculate_confidence(moderation_result)
            moderation_result['approved'] = self._determine_approval(moderation_result)
            moderation_result['recommendations'] = self._generate_moderation_recommendations(moderation_result)
            
            self.logger.info(f"Content moderation completed - Approved: {moderation_result['approved']}")
            return moderation_result
            
        except Exception as e:
            self.logger.error(f"Error in content moderation: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'approved': False,
                'confidence': 0
            }
    
    def _analyze_content_scores(self, content: str) -> Dict:
        """Analyze various aspects of content quality and appropriateness"""
        content_lower = content.lower()
        words = re.findall(r'\b\w+\b', content_lower)
        total_words = len(words)
        
        if total_words == 0:
            return {
                'spiritual_alignment': 0,
                'content_appropriateness': 0,
                'quality_score': 0,
                'safety_score': 0,
                'authenticity_score': 0
            }
        
        # Spiritual alignment score
        spiritual_positive = sum(1 for word in words if word in self.spiritual_keywords['positive'])
        spiritual_concerning = sum(1 for word in words if word in self.spiritual_keywords['concerning'])
        spiritual_alignment = max(0, min(100, 
            ((spiritual_positive * 10) - (spiritual_concerning * 15)) / max(1, total_words * 0.1) * 10
        ))
        
        # Content appropriateness
        appropriateness = self._calculate_appropriateness_score(content, words)
        
        # Quality score
        quality_score = self._calculate_quality_score(content, words)
        
        # Safety score
        safety_score = self._calculate_safety_score(content, words)
        
        # Authenticity score
        authenticity_score = self._calculate_authenticity_score(content, words)
        
        return {
            'spiritual_alignment': round(spiritual_alignment, 2),
            'content_appropriateness': round(appropriateness, 2),
            'quality_score': round(quality_score, 2),
            'safety_score': round(safety_score, 2),
            'authenticity_score': round(authenticity_score, 2)
        }
    
    def _calculate_appropriateness_score(self, content: str, words: List[str]) -> float:
        """Calculate content appropriateness for spiritual context"""
        base_score = 75  # Start with neutral score
        
        # Positive indicators
        positive_count = sum(1 for word in words if word in self.spiritual_keywords['positive'])
        base_score += min(25, positive_count * 2)
        
        # Negative indicators
        concerning_count = sum(1 for word in words if word in self.spiritual_keywords['concerning'])
        base_score -= concerning_count * 10
        
        # Check for inappropriate patterns
        inappropriate_patterns = [
            r'\b(hate|hatred|violence|war|fight|attack|destroy)\b',
            r'\b(superior|inferior|better than|worse than)\b',
            r'\b(only way|one truth|false|wrong|evil)\b'
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                base_score -= 15
        
        # Check for inclusive language
        inclusive_patterns = [
            r'\b(all beings|everyone|universal|inclusive|unity|together)\b',
            r'\b(respect|honor|appreciate|understand|accept)\b'
        ]
        
        for pattern in inclusive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                base_score += 5
        
        return max(0, min(100, base_score))
    
    def _calculate_quality_score(self, content: str, words: List[str]) -> float:
        """Calculate content quality score"""
        base_score = 70
        
        # Length considerations
        word_count = len(words)
        if word_count < 10:
            base_score -= 20
        elif word_count > 50:
            base_score += 10
        
        # Quality indicators
        high_quality_count = sum(1 for phrase in self.quality_indicators['high_quality'] 
                                if phrase in content.lower())
        low_quality_count = sum(1 for phrase in self.quality_indicators['low_quality'] 
                               if phrase in content.lower())
        
        base_score += high_quality_count * 8
        base_score -= low_quality_count * 12
        
        # Check for educational content
        educational_patterns = [
            r'\b(learn|understand|practice|develop|grow|improve)\b',
            r'\b(technique|method|approach|way|path|journey)\b'
        ]
        
        for pattern in educational_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                base_score += 3
        
        return max(0, min(100, base_score))
    
    def _calculate_safety_score(self, content: str, words: List[str]) -> float:
        """Calculate safety score to ensure content doesn't promote harmful practices"""
        base_score = 90  # Start high, reduce for safety concerns
        
        # Dangerous practice indicators
        dangerous_patterns = [
            r'\b(extreme|dangerous|risky|harmful|unsafe)\b',
            r'\b(without guidance|unsupervised|alone|secret)\b',
            r'\b(force|push|strain|pain|suffering)\b'
        ]
        
        for pattern in dangerous_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            base_score -= matches * 15
        
        # Safe practice indicators
        safe_patterns = [
            r'\b(safe|gentle|gradual|guided|supervised)\b',
            r'\b(listen to your body|at your own pace|comfort)\b',
            r'\b(qualified teacher|experienced guide|proper instruction)\b'
        ]
        
        for pattern in safe_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                base_score += 5
        
        return max(0, min(100, base_score))
    
    def _calculate_authenticity_score(self, content: str, words: List[str]) -> float:
        """Calculate authenticity score based on genuine spiritual expression"""
        base_score = 75
        
        # Authentic expression indicators
        authentic_patterns = [
            r'\b(experience|personal|journey|practice|learning)\b',
            r'\b(humbly|grateful|thankful|blessed|honored)\b',
            r'\b(share|offer|suggest|invite|welcome)\b'
        ]
        
        for pattern in authentic_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            base_score += matches * 3
        
        # Inauthentic indicators
        inauthentic_patterns = [
            r'\b(guaranteed|promised|secret|exclusive|special)\b',
            r'\b(must|should|have to|need to|required)\b',
            r'\b(only|best|perfect|ultimate|supreme)\b'
        ]
        
        for pattern in inauthentic_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            base_score -= matches * 8
        
        return max(0, min(100, base_score))
    
    def _identify_content_flags(self, content: str) -> List[Dict]:
        """Identify specific content flags and concerns"""
        flags = []
        content_lower = content.lower()
        
        # Check for concerning spiritual claims
        concerning_claims = [
            (r'\b(only true|one way|false religion|wrong path)\b', 'religious_exclusivity', 'high'),
            (r'\b(pay|money|donation|purchase|buy)\b', 'commercialization', 'medium'),
            (r'\b(guru|master|supreme|ultimate|perfect)\b', 'personality_cult_risk', 'medium'),
            (r'\b(fear|punishment|hell|damnation|curse)\b', 'fear_based_messaging', 'high'),
            (r'\b(secret|hidden|exclusive|chosen|special)\b', 'exclusivity_claims', 'medium')
        ]
        
        for pattern, flag_type, severity in concerning_claims:
            if re.search(pattern, content_lower):
                flags.append({
                    'type': flag_type,
                    'severity': severity,
                    'description': f"Content contains {flag_type.replace('_', ' ')}",
                    'pattern_matched': pattern
                })
        
        # Check for positive indicators
        positive_indicators = [
            (r'\b(love|compassion|kindness|peace|unity)\b', 'positive_values', 'positive'),
            (r'\b(inclusive|universal|all beings|everyone)\b', 'inclusive_messaging', 'positive'),
            (r'\b(practice|learn|grow|develop|journey)\b', 'growth_oriented', 'positive')
        ]
        
        for pattern, flag_type, severity in positive_indicators:
            if re.search(pattern, content_lower):
                flags.append({
                    'type': flag_type,
                    'severity': severity,
                    'description': f"Content demonstrates {flag_type.replace('_', ' ')}",
                    'pattern_matched': pattern
                })
        
        return flags
    
    def _detailed_content_analysis(self, content: str) -> Dict:
        """Provide detailed analysis of content characteristics"""
        words = re.findall(r'\b\w+\b', content.lower())
        sentences = re.split(r'[.!?]+', content)
        
        analysis = {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'avg_sentence_length': len(words) / max(1, len(sentences)),
            'spiritual_keyword_density': 0,
            'sentiment_indicators': {},
            'content_themes': [],
            'language_style': 'neutral'
        }
        
        # Calculate spiritual keyword density
        spiritual_words = sum(1 for word in words 
                            if word in self.spiritual_keywords['positive'] or 
                               word in self.spiritual_keywords['neutral'])
        analysis['spiritual_keyword_density'] = spiritual_words / max(1, len(words)) * 100
        
        # Sentiment indicators
        positive_sentiment = sum(1 for word in words if word in {
            'love', 'peace', 'joy', 'gratitude', 'blessing', 'beautiful', 'wonderful'
        })
        negative_sentiment = sum(1 for word in words if word in {
            'fear', 'anger', 'hate', 'suffering', 'pain', 'bad', 'wrong'
        })
        
        analysis['sentiment_indicators'] = {
            'positive_count': positive_sentiment,
            'negative_count': negative_sentiment,
            'overall_tone': 'positive' if positive_sentiment > negative_sentiment else 
                           'negative' if negative_sentiment > positive_sentiment else 'neutral'
        }
        
        # Identify content themes
        theme_keywords = {
            'meditation': ['meditation', 'mindfulness', 'awareness', 'presence'],
            'devotion': ['devotion', 'prayer', 'worship', 'surrender'],
            'wisdom': ['wisdom', 'knowledge', 'understanding', 'insight'],
            'practice': ['practice', 'discipline', 'training', 'exercise'],
            'community': ['community', 'together', 'sharing', 'fellowship']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content.lower() for keyword in keywords):
                analysis['content_themes'].append(theme)
        
        # Determine language style
        if any(word in content.lower() for word in ['thou', 'thee', 'sacred', 'divine']):
            analysis['language_style'] = 'formal_spiritual'
        elif any(word in content.lower() for word in ['hey', 'guys', 'awesome', 'cool']):
            analysis['language_style'] = 'casual'
        elif any(word in content.lower() for word in ['practice', 'technique', 'method']):
            analysis['language_style'] = 'instructional'
        
        return analysis
    
    def _calculate_confidence(self, moderation_result: Dict) -> float:
        """Calculate confidence in the moderation decision"""
        scores = moderation_result.get('moderation_scores', {})
        flags = moderation_result.get('flags', [])
        
        # Base confidence from score consistency
        score_values = list(scores.values())
        if not score_values:
            return 0.5
        
        score_avg = sum(score_values) / len(score_values)
        score_variance = sum((score - score_avg) ** 2 for score in score_values) / len(score_values)
        
        # Lower variance = higher confidence
        base_confidence = max(0.5, 1.0 - (score_variance / 1000))
        
        # Adjust based on flags
        high_severity_flags = sum(1 for flag in flags if flag.get('severity') == 'high')
        positive_flags = sum(1 for flag in flags if flag.get('severity') == 'positive')
        
        confidence_adjustment = (positive_flags * 0.1) - (high_severity_flags * 0.2)
        final_confidence = max(0.1, min(1.0, base_confidence + confidence_adjustment))
        
        return round(final_confidence, 3)
    
    def _determine_approval(self, moderation_result: Dict) -> bool:
        """Determine if content should be approved based on all factors"""
        scores = moderation_result.get('moderation_scores', {})
        flags = moderation_result.get('flags', [])
        confidence = moderation_result.get('confidence', 0)
        
        # Check if all scores meet minimum thresholds
        score_checks = []
        for score_type, threshold in self.thresholds.items():
            if score_type in scores:
                score_checks.append(scores[score_type] >= threshold)
        
        # Must pass all score checks
        passes_scores = all(score_checks) if score_checks else False
        
        # Check for blocking flags
        high_severity_flags = [f for f in flags if f.get('severity') == 'high']
        has_blocking_flags = len(high_severity_flags) > 0
        
        # Require minimum confidence
        sufficient_confidence = confidence >= 0.6
        
        # Final approval decision
        approved = passes_scores and not has_blocking_flags and sufficient_confidence
        
        return approved
    
    def _generate_moderation_recommendations(self, moderation_result: Dict) -> List[str]:
        """Generate actionable recommendations based on moderation results"""
        recommendations = []
        scores = moderation_result.get('moderation_scores', {})
        flags = moderation_result.get('flags', [])
        approved = moderation_result.get('approved', False)
        
        if approved:
            recommendations.append("Content approved for publication - meets spiritual content standards")
        else:
            recommendations.append("Content requires revision before publication")
        
        # Score-based recommendations
        for score_type, score in scores.items():
            threshold = self.thresholds.get(score_type, 70)
            if score < threshold:
                if score_type == 'spiritual_alignment':
                    recommendations.append("Increase spiritual content relevance and positive messaging")
                elif score_type == 'content_appropriateness':
                    recommendations.append("Review content for spiritual appropriateness and inclusivity")
                elif score_type == 'quality_score':
                    recommendations.append("Improve content quality with more educational or inspirational elements")
                elif score_type == 'safety_score':
                    recommendations.append("Address safety concerns and ensure responsible guidance")
                elif score_type == 'authenticity_score':
                    recommendations.append("Focus on authentic expression and genuine spiritual sharing")
        
        # Flag-based recommendations
        high_flags = [f for f in flags if f.get('severity') == 'high']
        for flag in high_flags:
            flag_type = flag.get('type', '')
            if flag_type == 'religious_exclusivity':
                recommendations.append("Remove exclusive religious claims and promote inclusive spirituality")
            elif flag_type == 'fear_based_messaging':
                recommendations.append("Replace fear-based messaging with love-based spiritual guidance")
            elif flag_type == 'commercialization':
                recommendations.append("Reduce commercial elements to maintain spiritual focus")
        
        return recommendations
    
    def moderate_batch_content(self, content_list: List[Dict]) -> Dict:
        """
        Moderate multiple pieces of content in batch
        
        Args:
            content_list: List of dicts with 'content', 'content_type', and optional 'metadata'
            
        Returns:
            Dict with batch moderation results
        """
        try:
            batch_results = {
                'timestamp': datetime.now().isoformat(),
                'total_items': len(content_list),
                'results': [],
                'summary': {
                    'approved': 0,
                    'rejected': 0,
                    'average_confidence': 0,
                    'common_issues': {}
                }
            }
            
            total_confidence = 0
            issue_counts = {}
            
            for i, item in enumerate(content_list):
                content = item.get('content', '')
                content_type = item.get('content_type', 'text')
                metadata = item.get('metadata', {})
                
                result = self.moderate_content(content, content_type, metadata)
                result['item_index'] = i
                batch_results['results'].append(result)
                
                # Update summary statistics
                if result.get('approved', False):
                    batch_results['summary']['approved'] += 1
                else:
                    batch_results['summary']['rejected'] += 1
                
                total_confidence += result.get('confidence', 0)
                
                # Track common issues
                for flag in result.get('flags', []):
                    flag_type = flag.get('type', 'unknown')
                    issue_counts[flag_type] = issue_counts.get(flag_type, 0) + 1
            
            # Calculate summary statistics
            if len(content_list) > 0:
                batch_results['summary']['average_confidence'] = total_confidence / len(content_list)
            
            # Identify most common issues
            batch_results['summary']['common_issues'] = dict(
                sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            )
            
            self.logger.info(f"Batch moderation completed for {len(content_list)} items")
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Error in batch content moderation: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'total_items': len(content_list) if content_list else 0
            }


# Utility functions for integration
def moderate_text_content(content: str, content_type: str = "text") -> Dict:
    """Convenience function to moderate text content"""
    moderator = SpiritualContentModerator()
    return moderator.moderate_content(content, content_type)

def moderate_content_batch(content_list: List[Dict]) -> Dict:
    """Convenience function to moderate content in batch"""
    moderator = SpiritualContentModerator()
    return moderator.moderate_batch_content(content_list)

def get_moderation_summary(moderation_result: Dict) -> str:
    """Generate a brief summary of moderation results"""
    if moderation_result.get('error'):
        return f"Moderation Error: {moderation_result['error']}"
    
    approved = moderation_result.get('approved', False)
    confidence = moderation_result.get('confidence', 0)
    scores = moderation_result.get('moderation_scores', {})
    
    status = "APPROVED" if approved else "REQUIRES REVIEW"
    avg_score = sum(scores.values()) / len(scores) if scores else 0
    
    return f"Status: {status} | Confidence: {confidence:.1%} | Avg Score: {avg_score:.1f}/100"