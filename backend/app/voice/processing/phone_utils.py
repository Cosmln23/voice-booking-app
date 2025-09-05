"""
Romanian Phone Number Processing
Advanced phone number validation and normalization for Romanian format
"""

import re
from typing import Optional, Dict, Tuple, List
from app.core.logging import get_logger

logger = get_logger(__name__)

# Romanian mobile network prefixes
ROMANIAN_MOBILE_PREFIXES = {
    # Orange
    "740", "741", "742", "743", "744", "745", "746", "747", "748", "749",
    # Vodafone  
    "750", "751", "752", "753", "754", "755", "756", "757", "758", "759",
    # Telekom
    "760", "761", "762", "763", "764", "765", "766", "767", "768", "769",
    # Digi
    "770", "771", "772", "773", "774", "775", "776", "777", "778", "779",
    # RCS&RDS
    "780", "781", "782", "783", "784", "785", "786", "787", "788", "789",
    # Test prefixes (for development/testing)
    "720", "721", "722", "723", "724", "725", "726", "727", "728", "729"
}

# Common voice input patterns for Romanian phone numbers
VOICE_NUMBER_PATTERNS = [
    # "zero șapte doi unu unu doi trei patru cinci șase"
    r"zero\s+șapte\s+(doi|trei|patru|cinci|șase|șapte|opt|nouă)\s+",
    # "plus patruzeci șapte doi unu"
    r"plus\s+patruzeci\s+șapte\s+",
    # "patruzeci șapte doi unu"  
    r"patruzeci\s+șapte\s+",
]

# Number word mappings
ROMANIAN_DIGIT_WORDS = {
    "zero": "0", "unu": "1", "doi": "2", "trei": "3", "patru": "4",
    "cinci": "5", "șase": "6", "șapte": "7", "opt": "8", "nouă": "9",
    "patruzeci": "40", "plus": "+", "minus": "-"
}


class RomanianPhoneProcessor:
    """Advanced Romanian phone number processing"""
    
    def __init__(self):
        self.logger = logger
    
    def normalize_phone_from_voice(self, voice_input: str) -> Optional[str]:
        """
        Normalize phone number from voice input
        
        Args:
            voice_input: Raw voice input (e.g., "zero șapte doi unu doi trei")
            
        Returns:
            Normalized phone number or None if invalid
        """
        try:
            # Convert voice input to lowercase and clean
            clean_input = voice_input.lower().strip()
            
            # Remove common filler words
            clean_input = self._remove_filler_words(clean_input)
            
            # Try different parsing strategies
            strategies = [
                self._parse_spelled_digits,
                self._parse_mixed_format,
                self._parse_direct_digits,
                self._parse_segmented_format
            ]
            
            for strategy in strategies:
                result = strategy(clean_input)
                if result and self.validate_romanian_phone(result):
                    self.logger.info(f"Successfully parsed phone: '{voice_input}' → {result}")
                    return result
            
            self.logger.warning(f"Could not parse phone number: {voice_input}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing phone from voice: {e}")
            return None
    
    def _remove_filler_words(self, text: str) -> str:
        """Remove common filler words from voice input"""
        filler_words = [
            "este", "numărul", "meu", "de", "telefon", "la", 
            "contactul", "să", "mă", "sunați", "pe", "cum", "spun"
        ]
        
        for word in filler_words:
            text = re.sub(rf"\b{word}\b", "", text)
        
        return re.sub(r'\s+', ' ', text).strip()
    
    def _parse_spelled_digits(self, text: str) -> Optional[str]:
        """Parse fully spelled out digits"""
        try:
            # "zero șapte doi unu doi trei patru cinci șase"
            words = text.split()
            digits = []
            
            for word in words:
                if word in ROMANIAN_DIGIT_WORDS:
                    digit_value = ROMANIAN_DIGIT_WORDS[word]
                    if digit_value == "40":  # "patruzeci" = country code
                        digits.append("+40")
                    elif digit_value in "0123456789":
                        digits.append(digit_value)
            
            if len(digits) >= 9:  # Minimum for valid Romanian number
                number_str = "".join(digits)
                # If we have exactly 9 digits and starts with 07, it means we're missing a digit
                if len(number_str) == 9 and number_str.startswith('07'):
                    # Likely missing a digit - this shouldn't be valid
                    return None
                return self._normalize_format(number_str)
            
            return None
            
        except Exception:
            return None
    
    def _parse_mixed_format(self, text: str) -> Optional[str]:
        """Parse mixed format (words + digits)"""
        try:
            # "patruzeci 721 123 456" or "plus patruzeci 07 21 12 34 56"
            # Replace known words with digits
            processed = text
            for word, digit in ROMANIAN_DIGIT_WORDS.items():
                processed = processed.replace(word, digit)
            
            # Extract digits and format
            digits = re.findall(r'\d+', processed)
            if digits:
                number_str = "".join(digits)
                return self._normalize_format(number_str)
            
            return None
            
        except Exception:
            return None
    
    def _parse_direct_digits(self, text: str) -> Optional[str]:
        """Parse direct digit sequences including international format"""
        try:
            # Handle international format with + sign first
            if text.startswith('+40'):
                # Extract digits after +40
                digits = re.findall(r'\d+', text)
                if digits:
                    number_str = "".join(digits)
                    # Should be 40XXXXXXXXX, convert to national format
                    if len(number_str) >= 11 and number_str.startswith('407'):
                        return '0' + number_str[2:]  # +407XXXXXXXX -> 07XXXXXXXX
            
            # Extract all digit sequences for other formats
            digits = re.findall(r'\d+', text)
            
            if not digits:
                return None
            
            # Join all digits
            number_str = "".join(digits)
            
            # Handle common formats - normalize to national 07... format
            if len(number_str) == 10 and number_str.startswith('07'):
                return number_str  # Already in correct national format
            elif len(number_str) == 12 and number_str.startswith('4007'):
                return '0' + number_str[2:]  # Convert 407XXXXXXXX to 07XXXXXXXX
            elif len(number_str) >= 9:
                return self._normalize_format(number_str)
            
            return None
            
        except Exception:
            return None
    
    def _parse_segmented_format(self, text: str) -> Optional[str]:
        """Parse segmented format like '07 21 12 34 56'"""
        try:
            # Look for digit groups separated by spaces/punctuation
            segments = re.findall(r'\d{2,4}', text)
            
            if len(segments) >= 3:  # At least prefix + some digits
                number_str = "".join(segments)
                return self._normalize_format(number_str)
            
            return None
            
        except Exception:
            return None
    
    def _normalize_format(self, number_str: str) -> Optional[str]:
        """
        Normalize phone number to standard format
        Supports both +40 international format and 07 national format
        Most Romanians say just '07...' so prioritize that format
        """
        try:
            # Remove any non-digits except +
            clean_number = re.sub(r'[^\d+]', '', number_str)
            
            # Handle different input formats - prioritize Romanian national format
            if clean_number.startswith('07') and len(clean_number) == 10:
                # Most common: Romanian national mobile format 07XXXXXXXX
                # Keep in national format as this is what people expect
                return clean_number
            elif clean_number.startswith('+40') and len(clean_number) == 13:
                # International format +407XXXXXXXX 
                # Convert to national format 07XXXXXXXX for consistency
                return '0' + clean_number[3:]
            elif clean_number.startswith('0040'):
                # Replace 0040 with 07
                return '07' + clean_number[6:]
            elif clean_number.startswith('40') and len(clean_number) == 12:
                # 407XXXXXXXX format - convert to national
                return '0' + clean_number[2:]
            elif len(clean_number) == 9 and clean_number.startswith('7'):
                # Missing leading 0: 7XXXXXXXX -> 07XXXXXXXX
                return '0' + clean_number
            elif len(clean_number) >= 9 and len(clean_number) <= 10:
                # Try to standardize to 07 format
                if clean_number.startswith('7'):
                    return '0' + clean_number
                elif clean_number.startswith('07'):
                    return clean_number
                else:
                    # Unknown format, try adding 07 prefix if it makes sense
                    if len(clean_number) == 8:
                        return '07' + clean_number
            
            return None
            
        except Exception:
            return None
    
    def validate_romanian_phone(self, phone: str) -> bool:
        """
        Validate Romanian phone number
        Supports both national (07...) and international (+40...) formats
        
        Args:
            phone: Phone number in national (07...) or international (+40...) format
            
        Returns:
            True if valid Romanian phone number
        """
        try:
            if not phone or not isinstance(phone, str):
                return False
            
            # Clean the phone number
            clean_phone = re.sub(r'[^\d+]', '', phone)
            
            # Handle international format (+40...)
            if clean_phone.startswith('+40'):
                # Extract number part after +40
                number_part = clean_phone[3:]
                
                # Must be exactly 9 digits after +40
                if not number_part.isdigit() or len(number_part) != 9:
                    return False
                
                # Must start with 7 (mobile) or 2/3 (landline)
                first_digit = number_part[0]
                if first_digit not in ['7', '2', '3']:
                    return False
                
                # For mobile numbers (7XXXXXXXX), check network prefix
                if first_digit == '7':
                    prefix = number_part[:3]
                    return prefix in ROMANIAN_MOBILE_PREFIXES
                
                return True
            
            # Handle national format (07...)
            elif clean_phone.startswith('07'):
                # Must be exactly 10 digits (07XXXXXXXX)
                if not clean_phone.isdigit() or len(clean_phone) != 10:
                    return False
                
                # Check mobile network prefix (first 3 digits after 0)
                prefix = clean_phone[1:4]  # Skip the '0', take next 3 digits
                return prefix in ROMANIAN_MOBILE_PREFIXES
            
            # Handle landline national format (02... or 03...)
            elif clean_phone.startswith('02') or clean_phone.startswith('03'):
                # Romanian landlines: 02X XXX XXXX or 03X XXX XXXX
                if not clean_phone.isdigit() or len(clean_phone) != 10:
                    return False
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error validating phone {phone}: {e}")
            return False
    
    def get_phone_info(self, phone: str) -> Dict[str, str]:
        """
        Get information about Romanian phone number
        Supports both national and international formats
        
        Args:
            phone: Phone number in 07... or +40... format
            
        Returns:
            Dict with phone information
        """
        try:
            info = {
                "original": phone,
                "country": "Romania", 
                "type": "unknown",
                "network": "unknown",
                "formatted": phone,
                "national_format": "",
                "international_format": ""
            }
            
            if not self.validate_romanian_phone(phone):
                info["valid"] = False
                return info
            
            info["valid"] = True
            clean_phone = re.sub(r'[^\d+]', '', phone)
            
            # Handle international format (+40...)
            if clean_phone.startswith('+40'):
                number_part = clean_phone[3:]  # Remove +40
                national_format = '0' + number_part
                international_format = clean_phone
            # Handle national format (07...)
            elif clean_phone.startswith('07'):
                number_part = clean_phone[1:]  # Remove leading 0
                national_format = clean_phone
                international_format = '+40' + number_part
            else:
                # Handle other formats
                if clean_phone.startswith('02') or clean_phone.startswith('03'):
                    number_part = clean_phone[1:]
                    national_format = clean_phone
                    international_format = '+40' + number_part
                else:
                    return info
            
            info["national_format"] = national_format
            info["international_format"] = international_format
            
            # Determine type and network for mobile numbers
            if national_format.startswith('07'):
                info["type"] = "mobile"
                prefix = national_format[1:4]  # Get 7XX prefix
                
                # Determine network based on prefix
                if prefix.startswith('74'):
                    info["network"] = "Orange"
                elif prefix.startswith('75'):
                    info["network"] = "Vodafone"
                elif prefix.startswith('76'):
                    info["network"] = "Telekom"
                elif prefix.startswith('77'):
                    info["network"] = "Digi"
                elif prefix.startswith('78'):
                    info["network"] = "RCS&RDS"
                elif prefix.startswith('72'):
                    info["network"] = "Test Network"
                
                # Format for display: 07XX XXX XXX (national) or +40 7XX XXX XXX (international)
                info["formatted"] = f"{national_format[:4]} {national_format[4:7]} {national_format[7:]}"
                
            elif national_format.startswith('02') or national_format.startswith('03'):
                info["type"] = "landline"
                # Format for display: 0XX XXX XXXX
                info["formatted"] = f"{national_format[:3]} {national_format[3:6]} {national_format[6:]}"
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting phone info: {e}")
            return {"original": phone, "valid": False, "error": str(e)}
    
    def format_for_voice_response(self, phone: str) -> str:
        """
        Format phone number for voice response
        Handles both national and international formats
        
        Args:
            phone: Phone number in 07... or +40... format
            
        Returns:
            Voice-friendly format
        """
        try:
            if not self.validate_romanian_phone(phone):
                return phone
            
            clean_phone = re.sub(r'[^\d+]', '', phone)
            
            # Get the actual digits to pronounce
            if clean_phone.startswith('+40'):
                # International format - pronounce without country code
                digits_to_pronounce = clean_phone[3:]  # Skip +40
                digits_to_pronounce = '0' + digits_to_pronounce  # Add leading 0 for pronunciation
            elif clean_phone.startswith('07'):
                # National format - pronounce as is
                digits_to_pronounce = clean_phone
            else:
                # Other formats (landline)
                digits_to_pronounce = clean_phone
            
            # Romanian digit words
            digit_words = {
                '0': 'zero', '1': 'unu', '2': 'doi', '3': 'trei', '4': 'patru',
                '5': 'cinci', '6': 'șase', '7': 'șapte', '8': 'opt', '9': 'nouă'
            }
            
            # Group digits for better pronunciation
            if len(digits_to_pronounce) == 10:  # Standard Romanian mobile: 07XXXXXXXX
                groups = [
                    digits_to_pronounce[:2],   # "07"
                    digits_to_pronounce[2:4],  # Next 2 digits
                    digits_to_pronounce[4:7],  # Next 3 digits
                    digits_to_pronounce[7:]    # Last 3 digits
                ]
                
                voice_groups = []
                for group in groups:
                    voice_digits = [digit_words.get(d, d) for d in group]
                    voice_groups.append(' '.join(voice_digits))
                
                return ', '.join(voice_groups)
            
            # Fallback: just convert each digit with grouping
            voice_digits = [digit_words.get(d, d) for d in digits_to_pronounce]
            
            # Group in threes for easier pronunciation
            grouped_digits = []
            for i in range(0, len(voice_digits), 3):
                group = voice_digits[i:i+3]
                grouped_digits.append(' '.join(group))
            
            return ', '.join(grouped_digits)
            
        except Exception:
            return phone


# Global instance
phone_processor = RomanianPhoneProcessor()


# Convenience functions
def normalize_phone_from_voice(voice_input: str) -> Optional[str]:
    """Normalize phone number from voice input"""
    return phone_processor.normalize_phone_from_voice(voice_input)


def validate_romanian_phone(phone: str) -> bool:
    """Validate Romanian phone number"""
    return phone_processor.validate_romanian_phone(phone)


def get_phone_info(phone: str) -> Dict[str, str]:
    """Get phone number information"""
    return phone_processor.get_phone_info(phone)


def format_for_voice(phone: str) -> str:
    """Format phone number for voice response"""
    return phone_processor.format_for_voice_response(phone)