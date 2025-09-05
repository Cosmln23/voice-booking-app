"""
Romanian Name Validation and Processing
Advanced processing for Romanian names with diacritics support
"""

import re
import unicodedata
from typing import Optional, Dict, List, Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)

# Romanian specific characters and their alternatives
ROMANIAN_DIACRITICS = {
    'ă': ['a', 'ã'], 'â': ['a', 'i'], 'î': ['i'], 'ș': ['s', 'sh'], 'ț': ['t', 'th'],
    'Ă': ['A', 'Ã'], 'Â': ['A', 'I'], 'Î': ['I'], 'Ș': ['S', 'SH'], 'Ț': ['T', 'TH']
}

# Common Romanian first names with variants
ROMANIAN_FIRST_NAMES = {
    # Male names
    'alexandru': ['alex', 'alexe', 'sandu', 'alexandro'],
    'andrei': ['andre', 'andi'],
    'adrian': ['adi'],
    'bogdan': ['bogdi'],
    'cristian': ['cristi', 'chris'],
    'daniel': ['dan', 'dani'],
    'dumitru': ['dumi', 'mitru'],
    'florin': ['flori'],
    'george': ['gigi', 'george'],
    'ion': ['ioni', 'nelu'],
    'ionuț': ['ionut', 'ionel'],
    'lucian': ['luci'],
    'marian': ['mari'],
    'mihai': ['mihaita', 'mișu', 'misu'],
    'nicolae': ['nicu', 'nico'],
    'octavian': ['tavi'],
    'paul': ['pavel'],
    'radu': ['radule'],
    'robert': ['robi'],
    'ștefan': ['stefan', 'stefi'],
    'vasile': ['vasi'],
    'victor': ['vicu'],
    'vlad': ['vladut'],
    
    # Female names
    'alexandra': ['alexa', 'sanda'],
    'ana': ['ana', 'anca', 'anica'],
    'andreea': ['andi', 'andre'],
    'cristina': ['cristi', 'tina'],
    'diana': ['diana'],
    'elena': ['lena', 'eli'],
    'gabriela': ['gabi'],
    'ioana': ['ioana', 'oana'],
    'larisa': ['lari'],
    'maria': ['maria', 'mari', 'mărioara', 'marioara'],
    'mihaela': ['miha', 'ela'],
    'monica': ['moni'],
    'oana': ['oana'],
    'paula': ['pauli'],
    'raluca': ['ralu'],
    'roxana': ['roxi'],
    'simona': ['simo'],
    'ștefania': ['stefania', 'stefi']
}

# Common Romanian surnames with variants
ROMANIAN_SURNAMES = {
    'popescu': ['popesc'],
    'ionescu': ['ionesc'],
    'popa': ['popă'],
    'stan': ['stan'],
    'dumitrescu': ['dumitresc'],
    'gheorghiu': ['gheorghiu'],
    'constantinescu': ['constantinesc'],
    'marin': ['marin'],
    'tudor': ['tudor'],
    'florea': ['florea'],
    'dobre': ['dobre'],
    'ene': ['ene'],
    'barbu': ['barbu'],
    'nicolae': ['nicolae'],
    'radu': ['radu']
}

# Voice recognition common errors for Romanian names
NAME_VOICE_FIXES = {
    'alexandra': ['aleksandra', 'alexandera'],
    'andreea': ['andrea', 'andria'],
    'cristian': ['christian', 'kristian'],
    'ștefan': ['stefan', 'stephane'],
    'mihai': ['mihai', 'mihaj'],
    'bogdan': ['bogdan', 'bordan'],
    'ionuț': ['ionut', 'jonut'],
    'răducu': ['raducu', 'raduku']
}


class RomanianNameProcessor:
    """Advanced Romanian name processing with diacritics support"""
    
    def __init__(self):
        self.logger = logger
        self.first_names = ROMANIAN_FIRST_NAMES
        self.surnames = ROMANIAN_SURNAMES
        self.voice_fixes = NAME_VOICE_FIXES
        
        # Build reverse lookup indices
        self._build_name_indices()
    
    def _build_name_indices(self):
        """Build indices for faster name matching"""
        self.first_name_variants = {}
        self.surname_variants = {}
        
        # Build first name variants index
        for canonical, variants in self.first_names.items():
            self.first_name_variants[canonical] = canonical
            for variant in variants:
                self.first_name_variants[variant.lower()] = canonical
        
        # Build surname variants index
        for canonical, variants in self.surnames.items():
            self.surname_variants[canonical] = canonical
            for variant in variants:
                self.surname_variants[variant.lower()] = canonical
    
    def normalize_name_from_voice(self, voice_input: str) -> Dict:
        """
        Normalize name from voice input
        
        Args:
            voice_input: Raw voice input (e.g., "Alexandru Popescu")
            
        Returns:
            Dict with normalized name information
        """
        try:
            if not voice_input or not isinstance(voice_input, str):
                return {
                    "success": False,
                    "message": "Input vid sau invalid"
                }
            
            # Clean and normalize input
            clean_name = self._clean_name_input(voice_input)
            
            if not clean_name:
                return {
                    "success": False,
                    "message": "Numele nu poate fi procesat"
                }
            
            # Apply voice recognition fixes
            fixed_name = self._apply_voice_fixes(clean_name)
            
            # Parse name components
            name_parts = self._parse_name_parts(fixed_name)
            
            # Validate and normalize each part
            normalized_parts = []
            confidence_scores = []
            
            for part in name_parts:
                normalized_part, confidence = self._normalize_name_part(part)
                normalized_parts.append(normalized_part)
                confidence_scores.append(confidence)
            
            # Calculate overall confidence
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # Format final name
            formatted_name = self._format_name(' '.join(normalized_parts))
            
            return {
                "success": True,
                "original": voice_input,
                "normalized": formatted_name,
                "parts": normalized_parts,
                "confidence": overall_confidence,
                "has_diacritics": self._has_diacritics(formatted_name),
                "is_romanian": self._is_likely_romanian(normalized_parts)
            }
            
        except Exception as e:
            self.logger.error(f"Error normalizing name: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _clean_name_input(self, name: str) -> str:
        """Clean and normalize name input"""
        if not name:
            return ""
        
        # Remove extra whitespace and normalize case
        clean = name.strip()
        
        # Remove common prefixes/suffixes
        prefixes = ["domnul", "doamna", "dl", "dna", "d-na"]
        for prefix in prefixes:
            clean = re.sub(rf'^{prefix}\s+', '', clean, flags=re.IGNORECASE)
        
        # Remove numbers and special characters except diacritics
        clean = re.sub(r'[0-9\-_\(\)\[\]{}]', '', clean)
        
        # Normalize whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _apply_voice_fixes(self, name: str) -> str:
        """Apply common voice recognition fixes"""
        fixed = name.lower()
        
        for correct, variants in self.voice_fixes.items():
            for variant in variants:
                fixed = fixed.replace(variant, correct)
        
        return fixed
    
    def _parse_name_parts(self, name: str) -> List[str]:
        """Parse name into components"""
        # Split by whitespace
        parts = name.split()
        
        # Filter out very short parts (likely noise)
        valid_parts = []
        for part in parts:
            if len(part) >= 2:  # Minimum 2 characters
                valid_parts.append(part)
        
        return valid_parts
    
    def _normalize_name_part(self, name_part: str) -> Tuple[str, float]:
        """
        Normalize a single name part
        
        Returns:
            Tuple of (normalized_name, confidence_score)
        """
        name_lower = name_part.lower()
        
        # Check first names
        if name_lower in self.first_name_variants:
            canonical = self.first_name_variants[name_lower]
            confidence = 1.0 if name_lower == canonical else 0.9
            return self._title_case_with_diacritics(canonical), confidence
        
        # Check surnames
        if name_lower in self.surname_variants:
            canonical = self.surname_variants[name_lower]
            confidence = 1.0 if name_lower == canonical else 0.9
            return self._title_case_with_diacritics(canonical), confidence
        
        # Fuzzy matching for similar names
        fuzzy_match = self._fuzzy_match_name(name_lower)
        if fuzzy_match:
            return self._title_case_with_diacritics(fuzzy_match), 0.7
        
        # If no match found, apply basic normalization
        normalized = self._basic_normalize(name_part)
        return normalized, 0.5
    
    def _fuzzy_match_name(self, name: str) -> Optional[str]:
        """Fuzzy match against known names"""
        from difflib import get_close_matches
        
        # Try first names
        first_matches = get_close_matches(name, self.first_name_variants.keys(), n=1, cutoff=0.8)
        if first_matches:
            return self.first_name_variants[first_matches[0]]
        
        # Try surnames
        surname_matches = get_close_matches(name, self.surname_variants.keys(), n=1, cutoff=0.8)
        if surname_matches:
            return self.surname_variants[surname_matches[0]]
        
        return None
    
    def _basic_normalize(self, name: str) -> str:
        """Apply basic normalization to unknown names"""
        # Title case
        normalized = name.title()
        
        # Try to add common diacritics based on patterns
        normalized = self._add_likely_diacritics(normalized)
        
        return normalized
    
    def _add_likely_diacritics(self, name: str) -> str:
        """Add likely diacritics based on Romanian patterns"""
        # Common patterns where diacritics are likely
        patterns = [
            (r'([Ss])t([aeiou])', r'\1ț\2'),    # st -> ț
            (r'([Ss])([aeiou])', r'Ș\2'),       # S at start -> Ș
            (r'([aA])n([^aeiou])', r'ăn\2'),    # an + consonant -> ăn
            (r'([iI])n([^aeiou])', r'în\2'),    # in + consonant -> în
        ]
        
        result = name
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        
        return result
    
    def _title_case_with_diacritics(self, name: str) -> str:
        """Apply title case while preserving diacritics"""
        if not name:
            return name
        
        # Simple title case that preserves diacritics
        return name[0].upper() + name[1:].lower()
    
    def _format_name(self, name: str) -> str:
        """Format complete name properly"""
        parts = name.split()
        formatted_parts = []
        
        for part in parts:
            formatted_parts.append(self._title_case_with_diacritics(part))
        
        return ' '.join(formatted_parts)
    
    def _has_diacritics(self, text: str) -> bool:
        """Check if text contains Romanian diacritics"""
        romanian_chars = 'ăâîșțĂÂÎȘȚ'
        return any(char in text for char in romanian_chars)
    
    def _is_likely_romanian(self, name_parts: List[str]) -> bool:
        """Determine if name is likely Romanian"""
        romanian_count = 0
        
        for part in name_parts:
            part_lower = part.lower()
            
            # Check if it's a known Romanian name
            if (part_lower in self.first_name_variants or 
                part_lower in self.surname_variants):
                romanian_count += 1
            
            # Check for Romanian-specific patterns
            elif self._has_romanian_patterns(part_lower):
                romanian_count += 0.5
        
        # Consider it Romanian if more than half the parts seem Romanian
        return romanian_count >= len(name_parts) * 0.5
    
    def _has_romanian_patterns(self, text: str) -> bool:
        """Check for Romanian-specific patterns"""
        patterns = [
            r'escu$',     # -escu ending
            r'eanu$',     # -eanu ending  
            r'[ăâîșț]',   # Contains Romanian diacritics
            r'^ion',      # Ion- prefix
            r'oiu$',      # -oiu ending
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def validate_name_format(self, name: str) -> Dict:
        """
        Validate name format and completeness
        
        Args:
            name: Full name string
            
        Returns:
            Dict with validation results
        """
        try:
            if not name or not isinstance(name, str):
                return {
                    "valid": False,
                    "message": "Nume invalid sau vid"
                }
            
            clean_name = name.strip()
            parts = clean_name.split()
            
            # Check minimum requirements
            if len(parts) < 2:
                return {
                    "valid": False,
                    "message": "Nume incomplete - vă rog să specificați prenume și nume",
                    "suggestion": "Exemplu: Ion Popescu"
                }
            
            if len(parts) > 4:
                return {
                    "valid": False,
                    "message": "Prea multe părți în nume",
                    "suggestion": "Vă rog să specificați doar prenume și nume"
                }
            
            # Check individual part validity
            invalid_parts = []
            for part in parts:
                if not self._is_valid_name_part(part):
                    invalid_parts.append(part)
            
            if invalid_parts:
                return {
                    "valid": False,
                    "message": f"Părți invalide în nume: {', '.join(invalid_parts)}",
                    "invalid_parts": invalid_parts
                }
            
            return {
                "valid": True,
                "parts_count": len(parts),
                "has_diacritics": self._has_diacritics(clean_name),
                "likely_romanian": self._is_likely_romanian(parts)
            }
            
        except Exception as e:
            self.logger.error(f"Error validating name: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _is_valid_name_part(self, part: str) -> bool:
        """Check if a name part is valid"""
        if not part or len(part) < 2:
            return False
        
        # Should contain only letters and diacritics
        if not re.match(r'^[a-zA-ZăâîșțĂÂÎȘȚ]+$', part):
            return False
        
        # Should not be all uppercase or all lowercase (except single letter)
        if len(part) > 1 and (part.isupper() or part.islower()):
            return False
        
        return True
    
    def format_for_voice_response(self, name: str) -> str:
        """Format name for voice response"""
        try:
            # Normalize the name first
            result = self.normalize_name_from_voice(name)
            
            if result.get("success"):
                return result["normalized"]
            else:
                # Fallback to basic formatting
                return self._format_name(name)
                
        except Exception:
            return name
    
    def get_name_suggestions(self, partial_name: str) -> List[str]:
        """Get name suggestions for partial input"""
        suggestions = []
        partial_lower = partial_name.lower()
        
        # Search in first names
        for name in self.first_name_variants.keys():
            if name.startswith(partial_lower):
                canonical = self.first_name_variants[name]
                formatted = self._title_case_with_diacritics(canonical)
                if formatted not in suggestions:
                    suggestions.append(formatted)
        
        # Search in surnames
        for name in self.surname_variants.keys():
            if name.startswith(partial_lower):
                canonical = self.surname_variants[name]
                formatted = self._title_case_with_diacritics(canonical)
                if formatted not in suggestions:
                    suggestions.append(formatted)
        
        return suggestions[:5]  # Limit to top 5 suggestions


# Global instance
name_processor = RomanianNameProcessor()


# Convenience functions
def normalize_name_from_voice(voice_input: str) -> Dict:
    """Normalize name from voice input"""
    return name_processor.normalize_name_from_voice(voice_input)


def validate_name_format(name: str) -> Dict:
    """Validate name format"""
    return name_processor.validate_name_format(name)


def format_name_for_voice(name: str) -> str:
    """Format name for voice response"""
    return name_processor.format_for_voice_response(name)


def get_name_suggestions(partial_name: str) -> List[str]:
    """Get name suggestions"""
    return name_processor.get_name_suggestions(partial_name)