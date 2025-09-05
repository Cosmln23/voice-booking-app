"""
Romanian Service Name Mapping
Advanced fuzzy matching for salon services in Romanian
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from difflib import SequenceMatcher
from app.core.logging import get_logger

logger = get_logger(__name__)

# Romanian service mappings with variations and synonyms
ROMANIAN_SERVICE_MAPPINGS = {
    "tuns": {
        "canonical": "Tunsoare Clasică",
        "category": "tuns",
        "variations": [
            "tuns", "tunsoare", "tunseuri", "tuns clasic", "tunsoare clasică",
            "tăiere", "tăiat părul", "scurtare", "scurtat părul",
            "coafură", "coafat", "aranjat părul", "dat cu foarfeca"
        ],
        "phonetic": ["tuns", "tunz", "tunsoare", "coafură", "tăiere"],
        "keywords": ["păr", "foarfeca", "scurt", "tăiat", "aranjat"]
    },
    
    "barba": {
        "canonical": "Bărbierit Complet",
        "category": "barba", 
        "variations": [
            "barbă", "bărbierit", "ras", "bărbat", "mustață",
            "tuns barbă", "aranjat barba", "modelat barba",
            "bărbierit complet", "bărbierit clasic", "ras traditional"
        ],
        "phonetic": ["barbă", "barba", "bărbierit", "ras"],
        "keywords": ["barbă", "mustață", "ras", "bărbierit", "bărbat"]
    },
    
    "styling": {
        "canonical": "Styling & Aranjare", 
        "category": "styling",
        "variations": [
            "styling", "aranjare", "coafură", "modelare",
            "pus în formă", "aranjat părul", "stilizare",
            "coafat profesional", "aranjament par", "stil nou"
        ],
        "phonetic": ["styling", "stilaj", "coafură", "aranjare"],
        "keywords": ["stil", "formă", "aranjat", "modelare", "coafură"]
    },
    
    "spalat": {
        "canonical": "Spălare & Tratament",
        "category": "spalat",
        "variations": [
            "spălat", "spălare", "șamponat", "șampon",
            "tratament păr", "îngrijire păr", "hidratare",
            "spălat cu șampon", "curățare păr", "îngrijit părul"
        ],
        "phonetic": ["spălat", "spalat", "șamponat", "samponat"],
        "keywords": ["șampon", "spălat", "curățat", "tratament", "îngrijire"]
    },
    
    "coafat": {
        "canonical": "Coafură Specială",
        "category": "coafat", 
        "variations": [
            "coafat", "coafură", "coafură specială", "aranjament special",
            "coafură de seară", "coafură de nuntă", "coafură elegantă",
            "aranjament păr", "păr aranjat festiv", "coafură pentru eveniment"
        ],
        "phonetic": ["coafat", "coafură", "aranjament"],
        "keywords": ["coafură", "elegant", "special", "eveniment", "nuntă"]
    }
}

# Common Romanian words that might be confused or misheard
ROMANIAN_HOMOPHONES = {
    "tuns": ["tunz", "tons", "tuns"],
    "barbă": ["barba", "bărba"],  
    "spălat": ["spalat", "șpălat"],
    "coafat": ["coatat", "goafat"]
}

# Voice recognition common errors for Romanian
VOICE_RECOGNITION_FIXES = {
    "tons": "tuns",
    "tunz": "tuns", 
    "barba": "barbă",
    "spalat": "spălat",
    "sampon": "șampon",
    "goafat": "coafat",
    "coatat": "coafat"
}


class RomanianServiceMapper:
    """Advanced Romanian service name mapping with fuzzy matching"""
    
    def __init__(self):
        self.logger = logger
        self.service_mappings = ROMANIAN_SERVICE_MAPPINGS
        self.homophones = ROMANIAN_HOMOPHONES
        self.voice_fixes = VOICE_RECOGNITION_FIXES
        
        # Build search indices
        self._build_search_indices()
    
    def _build_search_indices(self):
        """Build search indices for faster matching"""
        self.all_variations = {}  # variation -> service_key
        self.keyword_index = {}   # keyword -> [service_keys]
        
        for service_key, service_data in self.service_mappings.items():
            # Index variations
            for variation in service_data["variations"]:
                self.all_variations[variation.lower()] = service_key
                
            # Index phonetic variations
            for phonetic in service_data["phonetic"]:
                self.all_variations[phonetic.lower()] = service_key
            
            # Index keywords
            for keyword in service_data["keywords"]:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = []
                self.keyword_index[keyword].append(service_key)
    
    def map_service_from_voice(self, voice_input: str, confidence_threshold: float = 0.6) -> Dict:
        """
        Map voice input to canonical service name
        
        Args:
            voice_input: Raw voice input (e.g., "vreau să mă tund")
            confidence_threshold: Minimum confidence score (0.0-1.0)
            
        Returns:
            Dict with service mapping results
        """
        try:
            # Clean and normalize input
            clean_input = self._clean_voice_input(voice_input)
            
            if not clean_input:
                return {
                    "success": False,
                    "confidence": 0.0,
                    "message": "Input vid sau invalid"
                }
            
            # Try different matching strategies
            strategies = [
                ("exact_match", self._exact_match),
                ("variation_match", self._variation_match),
                ("fuzzy_match", self._fuzzy_match),
                ("keyword_match", self._keyword_match),
                ("phonetic_match", self._phonetic_match)
            ]
            
            best_result = None
            best_confidence = 0.0
            
            for strategy_name, strategy_func in strategies:
                result = strategy_func(clean_input)
                
                if result and result.get("confidence", 0) > best_confidence:
                    best_result = result
                    best_confidence = result.get("confidence", 0)
                    best_result["strategy"] = strategy_name
            
            if best_result and best_confidence >= confidence_threshold:
                self.logger.info(f"Service mapped: '{voice_input}' → {best_result['service_key']} ({best_confidence:.2f})")
                return {
                    "success": True,
                    "service_key": best_result["service_key"],
                    "canonical_name": best_result["canonical_name"],
                    "category": best_result["category"],
                    "confidence": best_confidence,
                    "strategy": best_result["strategy"],
                    "original_input": voice_input
                }
            
            # No good match found
            return {
                "success": False,
                "confidence": best_confidence if best_result else 0.0,
                "message": f"Nu am găsit serviciul '{voice_input}'",
                "suggestions": self._get_suggestions(clean_input),
                "original_input": voice_input
            }
            
        except Exception as e:
            self.logger.error(f"Error mapping service from voice: {e}")
            return {
                "success": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _clean_voice_input(self, text: str) -> str:
        """Clean and normalize voice input"""
        if not text:
            return ""
        
        # Convert to lowercase
        clean = text.lower().strip()
        
        # Apply voice recognition fixes
        for wrong, correct in self.voice_fixes.items():
            clean = clean.replace(wrong, correct)
        
        # Remove common filler phrases
        filler_phrases = [
            "vreau să", "doresc să", "aș vrea să", "pot să",
            "să mă", "să îmi", "pentru", "cu", "la",
            "un", "o", "m-", "îmi", "am nevoie de"
        ]
        
        for phrase in filler_phrases:
            clean = clean.replace(phrase, " ")
        
        # Normalize whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _exact_match(self, text: str) -> Optional[Dict]:
        """Try exact match with service keys"""
        for service_key in self.service_mappings:
            if service_key in text:
                return {
                    "service_key": service_key,
                    "canonical_name": self.service_mappings[service_key]["canonical"],
                    "category": self.service_mappings[service_key]["category"],
                    "confidence": 1.0
                }
        return None
    
    def _variation_match(self, text: str) -> Optional[Dict]:
        """Try matching with known variations"""
        best_match = None
        best_confidence = 0.0
        
        for variation, service_key in self.all_variations.items():
            if variation in text:
                confidence = len(variation) / len(text)  # Longer matches = higher confidence
                
                if confidence > best_confidence:
                    best_match = {
                        "service_key": service_key,
                        "canonical_name": self.service_mappings[service_key]["canonical"],
                        "category": self.service_mappings[service_key]["category"],
                        "confidence": min(confidence, 0.95)  # Cap at 95% for variations
                    }
                    best_confidence = confidence
        
        return best_match
    
    def _fuzzy_match(self, text: str) -> Optional[Dict]:
        """Fuzzy string matching"""
        best_match = None
        best_confidence = 0.0
        
        # Check against all variations
        for variation, service_key in self.all_variations.items():
            similarity = SequenceMatcher(None, text, variation).ratio()
            
            if similarity > best_confidence and similarity > 0.6:
                best_match = {
                    "service_key": service_key,
                    "canonical_name": self.service_mappings[service_key]["canonical"],
                    "category": self.service_mappings[service_key]["category"], 
                    "confidence": similarity * 0.9  # Slightly lower confidence for fuzzy
                }
                best_confidence = similarity
        
        return best_match
    
    def _keyword_match(self, text: str) -> Optional[Dict]:
        """Match based on keywords"""
        keyword_scores = {}
        
        words = text.split()
        
        for word in words:
            for keyword, service_keys in self.keyword_index.items():
                if keyword in word or word in keyword:
                    for service_key in service_keys:
                        if service_key not in keyword_scores:
                            keyword_scores[service_key] = 0
                        keyword_scores[service_key] += 1
        
        if keyword_scores:
            best_service = max(keyword_scores, key=keyword_scores.get)
            confidence = min(keyword_scores[best_service] / len(words), 0.8)
            
            return {
                "service_key": best_service,
                "canonical_name": self.service_mappings[best_service]["canonical"],
                "category": self.service_mappings[best_service]["category"],
                "confidence": confidence
            }
        
        return None
    
    def _phonetic_match(self, text: str) -> Optional[Dict]:
        """Match using phonetic variations"""
        best_match = None
        best_confidence = 0.0
        
        for service_key, service_data in self.service_mappings.items():
            for phonetic in service_data["phonetic"]:
                if phonetic in text:
                    confidence = len(phonetic) / len(text) * 0.7  # Lower confidence for phonetic
                    
                    if confidence > best_confidence:
                        best_match = {
                            "service_key": service_key,
                            "canonical_name": service_data["canonical"],
                            "category": service_data["category"],
                            "confidence": confidence
                        }
                        best_confidence = confidence
        
        return best_match
    
    def _get_suggestions(self, text: str) -> List[str]:
        """Get service suggestions for unclear input"""
        suggestions = []
        
        # Get top 3 fuzzy matches even if below threshold
        matches = []
        for variation, service_key in self.all_variations.items():
            similarity = SequenceMatcher(None, text, variation).ratio()
            if similarity > 0.3:  # Lower threshold for suggestions
                canonical = self.service_mappings[service_key]["canonical"]
                if canonical not in suggestions:
                    matches.append((similarity, canonical))
        
        # Sort by similarity and take top 3
        matches.sort(reverse=True, key=lambda x: x[0])
        suggestions = [match[1] for match in matches[:3]]
        
        # Add default services if no suggestions
        if not suggestions:
            suggestions = [
                "Tunsoare Clasică",
                "Bărbierit Complet", 
                "Styling & Aranjare"
            ]
        
        return suggestions
    
    def get_all_services(self) -> List[Dict]:
        """Get all available services"""
        services = []
        
        for service_key, service_data in self.service_mappings.items():
            services.append({
                "key": service_key,
                "canonical": service_data["canonical"],
                "category": service_data["category"],
                "variations": service_data["variations"]
            })
        
        return services
    
    def get_service_by_category(self, category: str) -> List[Dict]:
        """Get services by category"""
        services = []
        
        for service_key, service_data in self.service_mappings.items():
            if service_data["category"] == category:
                services.append({
                    "key": service_key,
                    "canonical": service_data["canonical"],
                    "category": service_data["category"]
                })
        
        return services
    
    def format_service_for_voice(self, service_key: str) -> str:
        """Format service name for voice response"""
        if service_key in self.service_mappings:
            return self.service_mappings[service_key]["canonical"]
        return service_key.title()


# Global instance
service_mapper = RomanianServiceMapper()


# Convenience functions
def map_service_from_voice(voice_input: str, confidence_threshold: float = 0.6) -> Dict:
    """Map service from voice input"""
    return service_mapper.map_service_from_voice(voice_input, confidence_threshold)


def get_all_services() -> List[Dict]:
    """Get all available services"""
    return service_mapper.get_all_services()


def format_service_for_voice(service_key: str) -> str:
    """Format service for voice response"""
    return service_mapper.format_service_for_voice(service_key)