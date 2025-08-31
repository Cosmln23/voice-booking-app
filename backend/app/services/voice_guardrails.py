"""
Voice Processing Guardrails and Security System
Implements safety checks and validation for voice interactions
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class GuardrailViolation(str, Enum):
    """Types of guardrail violations"""
    PERSONAL_DATA = "personal_data"
    INAPPROPRIATE_LANGUAGE = "inappropriate_language"
    SECURITY_RISK = "security_risk"
    RATE_LIMIT = "rate_limit"
    INVALID_REQUEST = "invalid_request"
    SPAM_DETECTION = "spam_detection"


class VoiceGuardrailsManager:
    """Manages security and safety guardrails for voice processing"""
    
    def __init__(self):
        self.rate_limit_cache: Dict[str, List[datetime]] = {}
        self.blocked_patterns = self._load_blocked_patterns()
        self.personal_data_patterns = self._load_personal_data_patterns()
        
        # Configuration
        self.max_requests_per_minute = 30
        self.max_requests_per_hour = 200
        self.max_text_length = 1000
        self.min_text_length = 3
        
    def _load_blocked_patterns(self) -> List[str]:
        """Load patterns that should be blocked"""
        return [
            r"(?i)(password|parol[aă])",
            r"(?i)(credit.*card|num[aă]r.*card)",
            r"(?i)(cnp|cod.*numeric.*personal)",
            r"(?i)(buletin|c[aă]rte.*identitate)",
            r"(?i)(cont.*bancar|iban)",
            r"(?i)(pin.*cod|cod.*secret)",
            # Inappropriate language (Romanian)
            r"(?i)(prost|idiot|tâmpit)",
            r"(?i)(du-te.*dracu|la naiba)",
            # System manipulation attempts
            r"(?i)(ignore.*previous.*instruction)",
            r"(?i)(system.*prompt|admin.*access)",
            r"(?i)(bypass.*security|override.*setting)",
        ]
    
    def _load_personal_data_patterns(self) -> List[str]:
        """Load patterns that might contain personal data requiring special handling"""
        return [
            r"\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b",  # Credit card pattern
            r"\b\d{13}\b",  # CNP pattern
            r"\b[A-Z]{2}\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b",  # IBAN pattern
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN-like pattern
            r"\b\d{10,12}\b",  # Long number sequences (potential IDs)
        ]
    
    async def validate_input(self, text: str, session_id: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Validate input text against all guardrails
        Returns validation result with any violations
        """
        try:
            violations = []
            warnings = []
            
            # 1. Basic text validation
            basic_result = self._validate_basic_text(text)
            if not basic_result["valid"]:
                violations.extend(basic_result["violations"])
            
            # 2. Rate limiting
            rate_result = self._check_rate_limits(session_id)
            if not rate_result["valid"]:
                violations.extend(rate_result["violations"])
            
            # 3. Content filtering
            content_result = self._filter_content(text)
            violations.extend(content_result["violations"])
            warnings.extend(content_result["warnings"])
            
            # 4. Personal data detection
            pii_result = self._detect_personal_data(text)
            warnings.extend(pii_result["warnings"])
            
            # 5. Security checks
            security_result = self._security_checks(text)
            violations.extend(security_result["violations"])
            
            # 6. Spam/abuse detection
            spam_result = self._detect_spam(text, session_id)
            if not spam_result["valid"]:
                violations.extend(spam_result["violations"])
            
            # Determine overall validation result
            is_valid = len(violations) == 0
            
            result = {
                "valid": is_valid,
                "violations": violations,
                "warnings": warnings,
                "sanitized_text": self._sanitize_text(text) if is_valid else None,
                "risk_score": self._calculate_risk_score(violations, warnings),
                "timestamp": datetime.now().isoformat()
            }
            
            # Log validation result
            if violations:
                logger.warning(
                    f"Guardrail violations detected for session {session_id}",
                    extra={
                        "violations": violations,
                        "text_preview": text[:50] + "..." if len(text) > 50 else text,
                        "risk_score": result["risk_score"]
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Guardrail validation error: {e}", exc_info=True)
            return {
                "valid": False,
                "violations": [{"type": "system_error", "message": "Validation system error"}],
                "warnings": [],
                "sanitized_text": None,
                "risk_score": 100,
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_basic_text(self, text: str) -> Dict[str, Any]:
        """Basic text validation (length, encoding, etc.)"""
        violations = []
        
        if not text or not isinstance(text, str):
            violations.append({
                "type": GuardrailViolation.INVALID_REQUEST,
                "message": "Text input is required and must be a string"
            })
        
        elif len(text.strip()) < self.min_text_length:
            violations.append({
                "type": GuardrailViolation.INVALID_REQUEST,
                "message": f"Text too short (minimum {self.min_text_length} characters)"
            })
        
        elif len(text) > self.max_text_length:
            violations.append({
                "type": GuardrailViolation.INVALID_REQUEST,
                "message": f"Text too long (maximum {self.max_text_length} characters)"
            })
        
        # Check for valid UTF-8 and printable characters
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            violations.append({
                "type": GuardrailViolation.INVALID_REQUEST,
                "message": "Text contains invalid characters"
            })
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    def _check_rate_limits(self, session_id: str) -> Dict[str, Any]:
        """Check rate limiting for the session"""
        violations = []
        now = datetime.now()
        
        # Initialize session tracking
        if session_id not in self.rate_limit_cache:
            self.rate_limit_cache[session_id] = []
        
        # Clean old entries
        cutoff_minute = now - timedelta(minutes=1)
        cutoff_hour = now - timedelta(hours=1)
        
        self.rate_limit_cache[session_id] = [
            timestamp for timestamp in self.rate_limit_cache[session_id]
            if timestamp > cutoff_hour
        ]
        
        # Count recent requests
        recent_minute = [
            timestamp for timestamp in self.rate_limit_cache[session_id]
            if timestamp > cutoff_minute
        ]
        
        recent_hour = self.rate_limit_cache[session_id]
        
        # Check limits
        if len(recent_minute) >= self.max_requests_per_minute:
            violations.append({
                "type": GuardrailViolation.RATE_LIMIT,
                "message": f"Too many requests per minute (max {self.max_requests_per_minute})"
            })
        
        elif len(recent_hour) >= self.max_requests_per_hour:
            violations.append({
                "type": GuardrailViolation.RATE_LIMIT,
                "message": f"Too many requests per hour (max {self.max_requests_per_hour})"
            })
        
        else:
            # Add current request to cache
            self.rate_limit_cache[session_id].append(now)
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    def _filter_content(self, text: str) -> Dict[str, Any]:
        """Filter for inappropriate content and blocked patterns"""
        violations = []
        warnings = []
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, text):
                violations.append({
                    "type": GuardrailViolation.INAPPROPRIATE_LANGUAGE,
                    "message": "Text contains blocked content"
                })
                break  # Don't need to check further patterns
        
        return {
            "violations": violations,
            "warnings": warnings
        }
    
    def _detect_personal_data(self, text: str) -> Dict[str, Any]:
        """Detect potential personal data in text"""
        warnings = []
        
        for pattern in self.personal_data_patterns:
            if re.search(pattern, text):
                warnings.append({
                    "type": GuardrailViolation.PERSONAL_DATA,
                    "message": "Text may contain personal data - handle with care"
                })
                break  # One warning is enough
        
        return {
            "warnings": warnings
        }
    
    def _security_checks(self, text: str) -> Dict[str, Any]:
        """Check for security-related issues"""
        violations = []
        
        # Check for prompt injection attempts
        injection_patterns = [
            r"(?i)ignore.*previous.*instruction",
            r"(?i)system.*you.*are.*now",
            r"(?i)forget.*everything.*before",
            r"(?i)new.*instruction.*override",
            r"(?i)admin.*mode.*enabled",
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, text):
                violations.append({
                    "type": GuardrailViolation.SECURITY_RISK,
                    "message": "Potential prompt injection attempt detected"
                })
                break
        
        return {
            "violations": violations
        }
    
    def _detect_spam(self, text: str, session_id: str) -> Dict[str, Any]:
        """Detect spam or abusive patterns"""
        violations = []
        
        # Check for excessive repetition
        words = text.lower().split()
        if len(words) > 5:
            word_count = {}
            for word in words:
                word_count[word] = word_count.get(word, 0) + 1
            
            # If any word appears more than 50% of the time, it might be spam
            max_repetition = max(word_count.values())
            if max_repetition / len(words) > 0.5:
                violations.append({
                    "type": GuardrailViolation.SPAM_DETECTION,
                    "message": "Excessive word repetition detected"
                })
        
        # Check for excessive special characters
        special_char_count = len([c for c in text if not c.isalnum() and not c.isspace()])
        if special_char_count / len(text) > 0.3:  # More than 30% special chars
            violations.append({
                "type": GuardrailViolation.SPAM_DETECTION,
                "message": "Excessive special characters detected"
            })
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text for safe processing"""
        # Remove potential HTML/script tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove control characters except newline and tab
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        return text
    
    def _calculate_risk_score(self, violations: List[Dict], warnings: List[Dict]) -> int:
        """Calculate risk score (0-100) based on violations and warnings"""
        score = 0
        
        # Violations add significant risk
        for violation in violations:
            violation_type = violation.get("type", "")
            if violation_type == GuardrailViolation.SECURITY_RISK:
                score += 50
            elif violation_type == GuardrailViolation.INAPPROPRIATE_LANGUAGE:
                score += 30
            elif violation_type == GuardrailViolation.RATE_LIMIT:
                score += 25
            elif violation_type == GuardrailViolation.SPAM_DETECTION:
                score += 20
            else:
                score += 15
        
        # Warnings add moderate risk
        for warning in warnings:
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    async def validate_conversation_response(self, response_text: str, context: Dict) -> Dict[str, Any]:
        """Validate AI-generated response before sending to user"""
        try:
            violations = []
            warnings = []
            
            # Check response doesn't contain blocked patterns
            content_result = self._filter_content(response_text)
            violations.extend(content_result["violations"])
            
            # Check for potential data leakage
            if self._contains_sensitive_patterns(response_text):
                warnings.append({
                    "type": GuardrailViolation.PERSONAL_DATA,
                    "message": "Response may contain sensitive information"
                })
            
            # Validate response is appropriate for booking context
            if not self._is_appropriate_booking_response(response_text):
                violations.append({
                    "type": GuardrailViolation.INVALID_REQUEST,
                    "message": "Response not appropriate for booking context"
                })
            
            is_valid = len(violations) == 0
            
            return {
                "valid": is_valid,
                "violations": violations,
                "warnings": warnings,
                "sanitized_response": self._sanitize_text(response_text) if is_valid else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Response validation error: {e}", exc_info=True)
            return {
                "valid": False,
                "violations": [{"type": "system_error", "message": "Response validation failed"}],
                "warnings": [],
                "sanitized_response": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def _contains_sensitive_patterns(self, text: str) -> bool:
        """Check if text contains potentially sensitive information"""
        sensitive_patterns = [
            r"\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b",  # Card numbers
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email addresses
            r"\b\d{3}-?\d{2}-?\d{4}\b",  # SSN-like
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _is_appropriate_booking_response(self, text: str) -> bool:
        """Check if response is appropriate for booking context"""
        # Should contain booking-related terms in Romanian
        booking_keywords = [
            "programare", "consultație", "tratament", "serviciu", 
            "data", "ora", "nume", "telefon", "confirmare"
        ]
        
        # Should not contain inappropriate topics
        inappropriate_topics = [
            "politică", "religie", "sex", "droguri", "violență"
        ]
        
        text_lower = text.lower()
        
        # Check for inappropriate topics
        for topic in inappropriate_topics:
            if topic in text_lower:
                return False
        
        # For booking responses, should contain relevant keywords
        # (This is lenient - we don't require keywords for all responses)
        return True
    
    def get_guardrails_status(self) -> Dict[str, Any]:
        """Get current guardrails system status"""
        return {
            "active": True,
            "configuration": {
                "max_requests_per_minute": self.max_requests_per_minute,
                "max_requests_per_hour": self.max_requests_per_hour,
                "max_text_length": self.max_text_length,
                "min_text_length": self.min_text_length
            },
            "active_sessions": len(self.rate_limit_cache),
            "blocked_patterns_count": len(self.blocked_patterns),
            "personal_data_patterns_count": len(self.personal_data_patterns),
            "timestamp": datetime.now().isoformat()
        }


# Global guardrails manager instance
voice_guardrails_manager = VoiceGuardrailsManager()


def get_voice_guardrails_manager() -> VoiceGuardrailsManager:
    """Get the global voice guardrails manager instance"""
    return voice_guardrails_manager