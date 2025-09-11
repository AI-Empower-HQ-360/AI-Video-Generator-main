"""
Enhanced Multilingual Engine for Workflow Automation
===================================================

Extended multilingual capabilities for workflow-based content translation
and localization automation.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TranslationRequest:
    """Data structure for translation requests"""
    content: str
    source_language: str
    target_language: str
    content_type: str = 'text'  # text, html, markdown
    context: Optional[str] = None
    priority: int = 1  # 1=high, 2=medium, 3=low


@dataclass
class TranslationResult:
    """Data structure for translation results"""
    translated_content: str
    source_language: str
    target_language: str
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any]


class WorkflowMultilingualEngine:
    """
    Enhanced multilingual engine with workflow automation capabilities
    """
    
    def __init__(self):
        # Supported languages with their metadata
        self.supported_languages = {
            'en': {'name': 'English', 'direction': 'ltr', 'family': 'germanic'},
            'es': {'name': 'Spanish', 'direction': 'ltr', 'family': 'romance'},
            'fr': {'name': 'French', 'direction': 'ltr', 'family': 'romance'},
            'de': {'name': 'German', 'direction': 'ltr', 'family': 'germanic'},
            'hi': {'name': 'Hindi', 'direction': 'ltr', 'family': 'indo-aryan'},
            'zh': {'name': 'Chinese', 'direction': 'ltr', 'family': 'sino-tibetan'},
            'ar': {'name': 'Arabic', 'direction': 'rtl', 'family': 'semitic'},
            'ja': {'name': 'Japanese', 'direction': 'ltr', 'family': 'japonic'},
            'ko': {'name': 'Korean', 'direction': 'ltr', 'family': 'koreanic'},
            'pt': {'name': 'Portuguese', 'direction': 'ltr', 'family': 'romance'},
            'ru': {'name': 'Russian', 'direction': 'ltr', 'family': 'slavic'},
            'it': {'name': 'Italian', 'direction': 'ltr', 'family': 'romance'},
            'th': {'name': 'Thai', 'direction': 'ltr', 'family': 'tai-kadai'},
            'vi': {'name': 'Vietnamese', 'direction': 'ltr', 'family': 'austroasiatic'},
            'tr': {'name': 'Turkish', 'direction': 'ltr', 'family': 'turkic'}
        }
        
        # Spiritual terminology mappings for accurate translations
        self.spiritual_terminology = {
            'dharma': {
                'en': 'dharma',
                'es': 'dharma',
                'fr': 'dharma',
                'de': 'Dharma',
                'hi': 'धर्म',
                'zh': '法',
                'ar': 'دارما',
                'ja': '法',
                'ko': '법'
            },
            'karma': {
                'en': 'karma',
                'es': 'karma',
                'fr': 'karma',
                'de': 'Karma',
                'hi': 'कर्म',
                'zh': '业',
                'ar': 'كارما',
                'ja': '業',
                'ko': '업'
            },
            'meditation': {
                'en': 'meditation',
                'es': 'meditación',
                'fr': 'méditation',
                'de': 'Meditation',
                'hi': 'ध्यान',
                'zh': '冥想',
                'ar': 'التأمل',
                'ja': '瞑想',
                'ko': '명상'
            },
            'enlightenment': {
                'en': 'enlightenment',
                'es': 'iluminación',
                'fr': 'illumination',
                'de': 'Erleuchtung',
                'hi': 'बोध',
                'zh': '开悟',
                'ar': 'التنوير',
                'ja': '悟り',
                'ko': '깨달음'
            }
        }
        
        # Quality thresholds for different content types
        self.quality_thresholds = {
            'spiritual_content': 0.9,
            'general_content': 0.8,
            'technical_content': 0.85,
            'marketing_content': 0.75
        }
    
    async def translate_content(self, request: TranslationRequest) -> TranslationResult:
        """
        Translate content with spiritual context awareness
        """
        start_time = datetime.now()
        
        try:
            # Validate languages
            if request.source_language not in self.supported_languages:
                raise ValueError(f"Unsupported source language: {request.source_language}")
            
            if request.target_language not in self.supported_languages:
                raise ValueError(f"Unsupported target language: {request.target_language}")
            
            # Skip translation if source and target are the same
            if request.source_language == request.target_language:
                return TranslationResult(
                    translated_content=request.content,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    confidence_score=1.0,
                    processing_time=0.0,
                    metadata={'skipped': True, 'reason': 'same_language'}
                )
            
            # Pre-process content
            preprocessed_content = self._preprocess_content(request.content, request.content_type)
            
            # Apply spiritual terminology preservation
            terminology_map = self._extract_spiritual_terms(preprocessed_content)
            
            # Perform translation (simulated - in production, use actual translation API)
            translated_content = await self._perform_translation(
                preprocessed_content, 
                request.source_language, 
                request.target_language,
                request.context
            )
            
            # Post-process and apply terminology
            final_content = self._postprocess_content(
                translated_content, 
                terminology_map, 
                request.target_language,
                request.content_type
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(
                request.content, 
                final_content, 
                request.source_language, 
                request.target_language
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return TranslationResult(
                translated_content=final_content,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=confidence_score,
                processing_time=processing_time,
                metadata={
                    'content_type': request.content_type,
                    'context': request.context,
                    'terminology_preserved': len(terminology_map),
                    'language_family_match': self._check_language_family_match(
                        request.source_language, 
                        request.target_language
                    )
                }
            )
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise
    
    async def translate_batch(self, requests: List[TranslationRequest]) -> List[TranslationResult]:
        """
        Translate multiple content pieces in batch
        """
        results = []
        
        # Sort by priority
        sorted_requests = sorted(requests, key=lambda x: x.priority)
        
        for request in sorted_requests:
            try:
                result = await self.translate_content(request)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch translation failed for item: {e}")
                # Create error result
                error_result = TranslationResult(
                    translated_content=request.content,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    confidence_score=0.0,
                    processing_time=0.0,
                    metadata={'error': str(e)}
                )
                results.append(error_result)
        
        return results
    
    def detect_language(self, content: str) -> Tuple[str, float]:
        """
        Detect the language of given content
        """
        # Simplified language detection (in production, use proper language detection library)
        
        # Check for specific script patterns
        if any('\u0900' <= char <= '\u097F' for char in content):  # Devanagari script
            return 'hi', 0.9
        elif any('\u4e00' <= char <= '\u9fff' for char in content):  # Chinese characters
            return 'zh', 0.85
        elif any('\u0600' <= char <= '\u06FF' for char in content):  # Arabic script
            return 'ar', 0.9
        elif any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' for char in content):  # Japanese
            return 'ja', 0.9
        elif any('\uAC00' <= char <= '\uD7AF' for char in content):  # Korean
            return 'ko', 0.9
        
        # Check for specific words/patterns
        spiritual_keywords = {
            'en': ['dharma', 'karma', 'meditation', 'enlightenment', 'spiritual'],
            'es': ['dharma', 'karma', 'meditación', 'iluminación', 'espiritual'],
            'fr': ['dharma', 'karma', 'méditation', 'illumination', 'spirituel'],
            'de': ['Dharma', 'Karma', 'Meditation', 'Erleuchtung', 'spirituell'],
            'hi': ['धर्म', 'कर्म', 'ध्यान', 'बोध', 'आध्यात्मिक'],
            'zh': ['法', '业', '冥想', '开悟', '精神'],
            'ar': ['دارما', 'كارما', 'التأمل', 'التنوير', 'روحي']
        }
        
        content_lower = content.lower()
        language_scores = {}
        
        for lang, keywords in spiritual_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in content_lower)
            if score > 0:
                language_scores[lang] = score / len(keywords)
        
        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            confidence = min(language_scores[detected_lang], 0.95)
            return detected_lang, confidence
        
        # Default to English with low confidence
        return 'en', 0.6
    
    def create_localization_workflow_template(self, content_languages: List[str], 
                                            content_type: str = 'spiritual') -> Dict[str, Any]:
        """
        Create a workflow template for automated localization
        """
        nodes = []
        connections = []
        
        # Start node
        start_node = {
            'node_type': 'start',
            'name': 'Begin Localization',
            'description': 'Start the localization workflow',
            'position_x': 100,
            'position_y': 200
        }
        nodes.append(start_node)
        
        # Language detection node
        detection_node = {
            'node_type': 'action',
            'name': 'Detect Language',
            'description': 'Automatically detect source language',
            'action_type': 'language_detection',
            'action_config': {
                'confidence_threshold': 0.8
            },
            'position_x': 300,
            'position_y': 200
        }
        nodes.append(detection_node)
        
        # Translation nodes for each target language
        x_offset = 500
        y_offset = 100
        
        for i, lang in enumerate(content_languages):
            if lang == 'en':  # Skip source language
                continue
            
            translation_node = {
                'node_type': 'localization',
                'name': f'Translate to {self.supported_languages[lang]["name"]}',
                'description': f'Translate content to {lang}',
                'localization_enabled': True,
                'target_languages': [lang],
                'config': {
                    'preserve_spiritual_terms': True,
                    'content_type': content_type,
                    'quality_threshold': self.quality_thresholds.get(f'{content_type}_content', 0.8)
                },
                'position_x': x_offset,
                'position_y': y_offset + (i * 100)
            }
            nodes.append(translation_node)
            
            # Connect detection node to translation node
            connection = {
                'from_node': 1,  # Detection node
                'to_node': len(nodes) - 1,
                'condition': 'success'
            }
            connections.append(connection)
        
        # Quality check node
        quality_node = {
            'node_type': 'action',
            'name': 'Quality Review',
            'description': 'Review translation quality',
            'action_type': 'quality_check',
            'action_config': {
                'check_spiritual_terms': True,
                'check_cultural_sensitivity': True,
                'auto_approve_threshold': 0.9
            },
            'position_x': x_offset + 200,
            'position_y': 200
        }
        nodes.append(quality_node)
        
        # Connect all translation nodes to quality check
        for i in range(2, len(nodes) - 1):
            connection = {
                'from_node': i,
                'to_node': len(nodes) - 1,
                'condition': 'success'
            }
            connections.append(connection)
        
        # Publishing node
        publish_node = {
            'node_type': 'action',
            'name': 'Publish Localized Content',
            'description': 'Publish content in all languages',
            'action_type': 'multi_publish',
            'action_config': {
                'platforms': ['website', 'app', 'social_media'],
                'schedule_publication': True
            },
            'position_x': x_offset + 400,
            'position_y': 200
        }
        nodes.append(publish_node)
        
        # End node
        end_node = {
            'node_type': 'end',
            'name': 'Localization Complete',
            'description': 'All content localized and published',
            'position_x': x_offset + 600,
            'position_y': 200
        }
        nodes.append(end_node)
        
        # Connect quality check to publish
        connections.append({
            'from_node': len(nodes) - 3,  # Quality node
            'to_node': len(nodes) - 2,    # Publish node
            'condition': 'approved'
        })
        
        # Connect publish to end
        connections.append({
            'from_node': len(nodes) - 2,  # Publish node
            'to_node': len(nodes) - 1,    # End node
            'condition': 'success'
        })
        
        return {
            'name': f'Multi-Language Localization - {content_type.title()}',
            'description': f'Automated localization workflow for {content_type} content',
            'category': 'localization',
            'is_template': True,
            'template_category': 'localization',
            'nodes': nodes,
            'connections': connections,
            'config': {
                'supported_languages': content_languages,
                'content_type': content_type,
                'auto_quality_check': True,
                'preserve_formatting': True
            }
        }
    
    def _preprocess_content(self, content: str, content_type: str) -> str:
        """
        Preprocess content before translation
        """
        if content_type == 'html':
            # Extract and preserve HTML tags
            # This is simplified - in production, use proper HTML parsing
            return content
        elif content_type == 'markdown':
            # Preserve markdown formatting
            return content
        else:
            # Clean and normalize text
            return content.strip()
    
    def _extract_spiritual_terms(self, content: str) -> Dict[str, str]:
        """
        Extract spiritual terminology that should be preserved
        """
        content_lower = content.lower()
        found_terms = {}
        
        for term, translations in self.spiritual_terminology.items():
            if term in content_lower:
                found_terms[term] = term
        
        return found_terms
    
    async def _perform_translation(self, content: str, source_lang: str, 
                                 target_lang: str, context: Optional[str] = None) -> str:
        """
        Perform the actual translation (simulated)
        """
        # In production, this would call actual translation APIs like:
        # - Google Translate API
        # - Azure Translator
        # - AWS Translate
        # - OpenAI GPT for context-aware translation
        
        # For spiritual content, we'd use specialized prompts
        if context and 'spiritual' in context.lower():
            # Use spiritual-aware translation
            prompt = f"""
            Translate the following spiritual content from {source_lang} to {target_lang}.
            Preserve the spiritual meaning and cultural context.
            Keep Sanskrit terms like 'dharma', 'karma', 'moksha' in their original form.
            
            Content: {content}
            """
            # This would be sent to a translation API
            
        # Simplified simulation
        lang_name = self.supported_languages[target_lang]['name']
        return f"[{lang_name} translation of: {content}]"
    
    def _postprocess_content(self, translated_content: str, terminology_map: Dict[str, str],
                           target_lang: str, content_type: str) -> str:
        """
        Post-process translated content
        """
        # Apply preserved terminology
        for original_term, preserved_term in terminology_map.items():
            if target_lang in self.spiritual_terminology.get(original_term, {}):
                correct_translation = self.spiritual_terminology[original_term][target_lang]
                translated_content = translated_content.replace(
                    preserved_term, 
                    correct_translation
                )
        
        # Apply language-specific formatting
        if self.supported_languages[target_lang]['direction'] == 'rtl':
            # Apply RTL formatting for Arabic, Hebrew, etc.
            translated_content = f"‏{translated_content}‎"
        
        return translated_content
    
    def _calculate_confidence(self, original: str, translated: str, 
                            source_lang: str, target_lang: str) -> float:
        """
        Calculate translation confidence score
        """
        # Simplified confidence calculation
        # In production, this would use more sophisticated metrics
        
        base_confidence = 0.8
        
        # Boost confidence for related language families
        if self._check_language_family_match(source_lang, target_lang):
            base_confidence += 0.1
        
        # Penalize for very short or very long content
        length_ratio = len(translated) / len(original) if len(original) > 0 else 0
        if 0.5 <= length_ratio <= 2.0:
            base_confidence += 0.05
        else:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _check_language_family_match(self, lang1: str, lang2: str) -> bool:
        """
        Check if two languages belong to the same language family
        """
        family1 = self.supported_languages.get(lang1, {}).get('family')
        family2 = self.supported_languages.get(lang2, {}).get('family')
        
        return family1 and family2 and family1 == family2
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of supported languages with metadata
        """
        return self.supported_languages
    
    def get_language_pairs_quality(self) -> Dict[str, Dict[str, float]]:
        """
        Get quality scores for different language pairs
        """
        # Simplified quality matrix
        quality_matrix = {}
        
        for source in self.supported_languages:
            quality_matrix[source] = {}
            for target in self.supported_languages:
                if source == target:
                    quality_matrix[source][target] = 1.0
                elif self._check_language_family_match(source, target):
                    quality_matrix[source][target] = 0.9
                else:
                    quality_matrix[source][target] = 0.8
        
        return quality_matrix
    
    def validate_translation_quality(self, result: TranslationResult, 
                                   content_type: str = 'general_content') -> bool:
        """
        Validate if translation meets quality threshold
        """
        threshold = self.quality_thresholds.get(content_type, 0.8)
        return result.confidence_score >= threshold


# Global multilingual engine instance
multilingual_engine = WorkflowMultilingualEngine()


# Convenience functions for workflow integration
async def translate_for_workflow(content: str, source_lang: str, target_languages: List[str],
                               content_type: str = 'text', context: str = None) -> Dict[str, TranslationResult]:
    """
    Translate content for workflow automation
    """
    results = {}
    
    for target_lang in target_languages:
        if target_lang != source_lang:
            request = TranslationRequest(
                content=content,
                source_language=source_lang,
                target_language=target_lang,
                content_type=content_type,
                context=context
            )
            
            result = await multilingual_engine.translate_content(request)
            results[target_lang] = result
    
    return results


def create_localization_workflow(target_languages: List[str], content_type: str = 'spiritual') -> Dict[str, Any]:
    """
    Create a localization workflow template
    """
    return multilingual_engine.create_localization_workflow_template(target_languages, content_type)


def get_language_suggestions(content: str) -> List[Tuple[str, str, float]]:
    """
    Get language suggestions based on content
    """
    detected_lang, confidence = multilingual_engine.detect_language(content)
    
    suggestions = [(detected_lang, multilingual_engine.supported_languages[detected_lang]['name'], confidence)]
    
    # Add related language suggestions
    detected_family = multilingual_engine.supported_languages[detected_lang]['family']
    
    for lang_code, lang_info in multilingual_engine.supported_languages.items():
        if lang_code != detected_lang and lang_info['family'] == detected_family:
            suggestions.append((lang_code, lang_info['name'], 0.7))
    
    return suggestions[:5]  # Return top 5 suggestions