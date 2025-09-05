"""
Advanced Romanian Date/Time Parser
Natural language processing for Romanian date and time expressions
"""

import re
from datetime import datetime, date, time, timedelta
from typing import Optional, Dict, Tuple, List, Union
from app.core.logging import get_logger

logger = get_logger(__name__)

# Romanian weekday names
ROMANIAN_WEEKDAYS = {
    "luni": 0, "luni": 0,
    "marți": 1, "marti": 1, "martea": 1,
    "miercuri": 2, "miercuri": 2,
    "joi": 3, "joia": 3,
    "vineri": 4, "vinerea": 4,
    "sâmbătă": 5, "sambata": 5, "simbata": 5, "sâmbăta": 5,
    "duminică": 6, "duminica": 6, "duminica": 6
}

# Romanian month names
ROMANIAN_MONTHS = {
    "ianuarie": 1, "jan": 1,
    "februarie": 2, "feb": 2,
    "martie": 3, "mar": 3,
    "aprilie": 4, "apr": 4,
    "mai": 5,
    "iunie": 6, "iun": 6,
    "iulie": 7, "iul": 7,
    "august": 8, "aug": 8,
    "septembrie": 9, "sep": 9, "sept": 9,
    "octombrie": 10, "oct": 10,
    "noiembrie": 11, "nov": 11,
    "decembrie": 12, "dec": 12
}

# Time-related expressions
TIME_EXPRESSIONS = {
    # Specific times
    "dimineața": time(9, 0),
    "dimineata": time(9, 0),
    "dis-de-dimineață": time(8, 0),
    "devreme": time(8, 0),
    
    "prânz": time(12, 0),
    "prinz": time(12, 0),
    "amiaza": time(12, 0),
    "la amiază": time(12, 0),
    
    "după-amiaza": time(15, 0),
    "dupa-amiaza": time(15, 0),
    "după-masa": time(15, 0),
    "dupamasa": time(15, 0),
    
    "seara": time(18, 0),
    "către seară": time(17, 30),
    "pe seară": time(18, 0),
    
    "noaptea": time(20, 0),
    "târziu": time(19, 0),
    "tarziu": time(19, 0)
}

# Relative date expressions
RELATIVE_DATE_EXPRESSIONS = {
    # Immediate
    "astăzi": 0,
    "azi": 0,
    "astazi": 0,
    "în ziua de astăzi": 0,
    
    "mâine": 1,
    "maine": 1,
    "ziua de mâine": 1,
    
    "poimâine": 2,
    "poimaine": 2,
    "după mâine": 2,
    "peste o zi": 2,
    
    # Week-based
    "săptămâna asta": 0,  # This week - will be processed specially
    "săptămâna aceasta": 0,
    "saptamana asta": 0,
    
    "săptămâna viitoare": 7,
    "saptamana viitoare": 7,
    "săptămâna următoare": 7,
    
    "săptămâna trecută": -7,
    "saptamana trecuta": -7,
    
    # Month-based  
    "luna asta": 0,      # This month - will be processed specially
    "luna aceasta": 0,
    "luna viitoare": 30,
    "luna următoare": 30,
    "luna trecută": -30
}

# Number words in Romanian
ROMANIAN_NUMBERS = {
    "unu": 1, "una": 1, "primul": 1, "prima": 1,
    "doi": 2, "două": 2, "doilea": 2, "a doua": 2,
    "trei": 3, "treilea": 3, "a treia": 3,
    "patru": 4, "al patrulea": 4, "a patra": 4,
    "cinci": 5, "al cincilea": 5, "a cincea": 5,
    "șase": 6, "sase": 6, "al șaselea": 6,
    "șapte": 7, "sapte": 7, "al șaptelea": 7,
    "opt": 8, "al optulea": 8,
    "nouă": 9, "noua": 9, "al nouălea": 9,
    "zece": 10, "al zecelea": 10,
    
    # Teens
    "unsprezece": 11, "doisprezece": 12, "treisprezece": 13,
    "paisprezece": 14, "cincisprezece": 15, "șaisprezece": 16,
    "șaptesprezece": 17, "optsprezece": 18, "nouăsprezece": 19,
    
    # Twenties
    "douăzeci": 20, "douazeci": 20,
    "treizeci": 30, "patruzeci": 40
}

# Hour patterns for voice input
HOUR_PATTERNS = {
    "și jumătate": 30,      # "zece și jumătate" = 10:30
    "si jumatate": 30,
    "și un sfert": 15,      # "zece și un sfert" = 10:15
    "si un sfert": 15,
    "și trei sferturi": 45, # "zece și trei sferturi" = 10:45
    "si trei sferturi": 45,
    "fix": 0,               # "zece fix" = 10:00
    "în punct": 0           # "zece în punct" = 10:00
}


class RomanianDateTimeParser:
    """Advanced Romanian date and time parser"""
    
    def __init__(self):
        self.logger = logger
        
    def parse_datetime_from_voice(self, voice_input: str) -> Dict:
        """
        Parse both date and time from voice input
        
        Args:
            voice_input: Voice input containing date/time info
            
        Returns:
            Dict with parsed date and time
        """
        try:
            # Split input to try to find both date and time
            words = voice_input.lower().split()
            
            # Try to parse date
            parsed_date = self.parse_date_from_voice(voice_input)
            parsed_time = self.parse_time_from_voice(voice_input)
            
            if not parsed_date and not parsed_time:
                return {
                    "success": False,
                    "message": "Nu am putut interpreta data sau ora"
                }
            
            # Use defaults if missing
            if not parsed_date:
                parsed_date = date.today()
            if not parsed_time:
                parsed_time = time(10, 0)  # Default to 10:00 AM
            
            return {
                "success": True,
                "parsed_date": parsed_date,
                "parsed_time": parsed_time,
                "original_input": voice_input
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing datetime: {e}")
            return {
                "success": False,
                "message": f"Eroare la parsarea datei/orei: {str(e)}"
            }
    
    def parse_date_from_voice(self, voice_input: str) -> Optional[date]:
        """
        Parse date from Romanian voice input
        
        Args:
            voice_input: Voice input like "săptămâna viitoare joi", "15 martie"
            
        Returns:
            Parsed date object or None
        """
        try:
            clean_input = self._clean_input(voice_input)
            
            if not clean_input:
                return None
            
            # Try different parsing strategies
            strategies = [
                self._parse_relative_dates,
                self._parse_weekday_references,
                self._parse_specific_dates,
                self._parse_date_expressions,
                self._parse_numeric_dates
            ]
            
            for strategy in strategies:
                result = strategy(clean_input)
                if result:
                    self.logger.info(f"Date parsed: '{voice_input}' → {result}")
                    return result
            
            self.logger.warning(f"Could not parse date: {voice_input}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing date: {e}")
            return None
    
    def parse_time_from_voice(self, voice_input: str) -> Optional[time]:
        """
        Parse time from Romanian voice input
        
        Args:
            voice_input: Voice input like "zece și jumătate", "după-amiaza"
            
        Returns:
            Parsed time object or None
        """
        try:
            clean_input = self._clean_input(voice_input)
            
            if not clean_input:
                return None
            
            # Try different parsing strategies
            strategies = [
                self._parse_time_expressions,
                self._parse_specific_times,
                self._parse_relative_times,
                self._parse_numeric_times
            ]
            
            for strategy in strategies:
                result = strategy(clean_input)
                if result:
                    self.logger.info(f"Time parsed: '{voice_input}' → {result}")
                    return result
            
            self.logger.warning(f"Could not parse time: {voice_input}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing time: {e}")
            return None
    
    def parse_datetime_range(self, voice_input: str) -> Optional[Tuple[datetime, datetime]]:
        """
        Parse date/time range from voice input
        
        Args:
            voice_input: "între 9 și 12", "de luni până vineri"
            
        Returns:
            Tuple of (start_datetime, end_datetime) or None
        """
        try:
            clean_input = self._clean_input(voice_input)
            
            # Look for range indicators
            range_indicators = [
                (r"între\s+(.+?)\s+și\s+(.+)", "between"),
                (r"de\s+la\s+(.+?)\s+până\s+la\s+(.+)", "from_to"),
                (r"din\s+(.+?)\s+în\s+(.+)", "from_to"),
                (r"(.+?)\s*-\s*(.+)", "dash")
            ]
            
            for pattern, range_type in range_indicators:
                match = re.search(pattern, clean_input, re.IGNORECASE)
                if match:
                    start_str, end_str = match.groups()
                    
                    # Parse start and end
                    start_time = self.parse_time_from_voice(start_str)
                    end_time = self.parse_time_from_voice(end_str)
                    
                    if start_time and end_time:
                        today = date.today()
                        start_dt = datetime.combine(today, start_time)
                        end_dt = datetime.combine(today, end_time)
                        
                        return (start_dt, end_dt)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing datetime range: {e}")
            return None
    
    def _clean_input(self, text: str) -> str:
        """Clean and normalize input"""
        if not text:
            return ""
        
        clean = text.lower().strip()
        
        # Remove common filler words
        fillers = [
            "pe", "în", "la", "pentru", "de", "din", "cu",
            "ziua de", "ora de", "vremea de"
        ]
        
        for filler in fillers:
            clean = clean.replace(filler, " ")
        
        # Normalize whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _parse_relative_dates(self, text: str) -> Optional[date]:
        """Parse relative date expressions"""
        today = date.today()
        
        for expression, days_offset in RELATIVE_DATE_EXPRESSIONS.items():
            if expression in text:
                if days_offset == 0:  # Special handling for "this week/month"
                    if "săptămână" in expression:
                        # Return start of this week (Monday)
                        days_since_monday = today.weekday()
                        return today - timedelta(days=days_since_monday)
                    elif "lună" in expression:
                        # Return start of this month
                        return today.replace(day=1)
                
                return today + timedelta(days=days_offset)
        
        return None
    
    def _parse_weekday_references(self, text: str) -> Optional[date]:
        """Parse weekday references like 'joi viitor', 'luni aceasta'"""
        today = date.today()
        current_weekday = today.weekday()
        
        # Find weekday in text
        target_weekday = None
        for weekday_name, weekday_num in ROMANIAN_WEEKDAYS.items():
            if weekday_name in text:
                target_weekday = weekday_num
                break
        
        if target_weekday is None:
            return None
        
        # Determine which week
        if any(word in text for word in ["viitor", "viitoare", "următor", "următoare"]):
            # Next week
            days_ahead = target_weekday - current_weekday + 7
        elif any(word in text for word in ["trecut", "trecută", "precedent"]):
            # Last week  
            days_ahead = target_weekday - current_weekday - 7
        else:
            # This week or next occurrence
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:  # If day already passed this week
                days_ahead += 7
        
        return today + timedelta(days=days_ahead)
    
    def _parse_specific_dates(self, text: str) -> Optional[date]:
        """Parse specific dates like '15 martie', '23 decembrie 2024'"""
        today = date.today()
        
        # Pattern: day month [year]
        patterns = [
            r'(\d{1,2})\s+(\w+)(?:\s+(\d{4}))?',        # "15 martie 2024"
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',           # "15.03.2024"
            r'(\d{1,2})/(\d{1,2})/(\d{4})',            # "15/03/2024"
            r'(\d{1,2})-(\d{1,2})-(\d{4})'             # "15-03-2024"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                
                if len(groups) == 3 and groups[1].isdigit():
                    # Numeric format
                    day, month, year = map(int, groups)
                    try:
                        return date(year, month, day)
                    except ValueError:
                        continue
                        
                elif len(groups) >= 2:
                    # Text format with month name
                    day = int(groups[0])
                    month_name = groups[1].lower()
                    year = int(groups[2]) if len(groups) > 2 and groups[2] else today.year
                    
                    month = ROMANIAN_MONTHS.get(month_name)
                    if month:
                        try:
                            return date(year, month, day)
                        except ValueError:
                            continue
        
        return None
    
    def _parse_date_expressions(self, text: str) -> Optional[date]:
        """Parse complex date expressions"""
        today = date.today()
        
        # "peste X zile"
        match = re.search(r'peste\s+(\w+)\s+zil[eă]', text)
        if match:
            number_word = match.group(1)
            days = ROMANIAN_NUMBERS.get(number_word)
            if days:
                return today + timedelta(days=days)
        
        # "în X zile"
        match = re.search(r'în\s+(\w+)\s+zil[eă]', text)
        if match:
            number_word = match.group(1)
            days = ROMANIAN_NUMBERS.get(number_word)
            if days:
                return today + timedelta(days=days)
        
        # "acum X zile" (past)
        match = re.search(r'acum\s+(\w+)\s+zil[eă]', text)
        if match:
            number_word = match.group(1)
            days = ROMANIAN_NUMBERS.get(number_word)
            if days:
                return today - timedelta(days=days)
        
        return None
    
    def _parse_numeric_dates(self, text: str) -> Optional[date]:
        """Parse numeric date patterns"""
        today = date.today()
        
        # Extract numbers
        numbers = re.findall(r'\d+', text)
        
        if len(numbers) >= 2:
            day = int(numbers[0])
            month = int(numbers[1])
            year = int(numbers[2]) if len(numbers) > 2 else today.year
            
            # Validate and create date
            if 1 <= day <= 31 and 1 <= month <= 12:
                try:
                    return date(year, month, day)
                except ValueError:
                    pass
        
        return None
    
    def _parse_time_expressions(self, text: str) -> Optional[time]:
        """Parse common time expressions"""
        for expression, time_obj in TIME_EXPRESSIONS.items():
            if expression in text:
                return time_obj
        
        return None
    
    def _parse_specific_times(self, text: str) -> Optional[time]:
        """Parse specific time formats"""
        # "zece și jumătate", "nouă fix"
        for hour_word, hour_num in ROMANIAN_NUMBERS.items():
            if hour_word in text and hour_num <= 24:
                # Look for minute modifiers
                minute = 0
                
                for pattern, min_value in HOUR_PATTERNS.items():
                    if pattern in text:
                        minute = min_value
                        break
                
                try:
                    return time(hour_num, minute)
                except ValueError:
                    continue
        
        return None
    
    def _parse_relative_times(self, text: str) -> Optional[time]:
        """Parse relative time expressions"""
        now = datetime.now().time()
        
        if "peste" in text and ("minut" in text or "oră" in text):
            # "peste 30 de minute", "peste o oră"
            numbers = re.findall(r'\d+', text)
            if numbers:
                offset_minutes = int(numbers[0])
                if "oră" in text or "ore" in text:
                    offset_minutes *= 60
                
                # Add to current time
                current_dt = datetime.combine(date.today(), now)
                future_dt = current_dt + timedelta(minutes=offset_minutes)
                return future_dt.time()
        
        return None
    
    def _parse_numeric_times(self, text: str) -> Optional[time]:
        """Parse numeric time patterns"""
        # HH:MM format
        time_pattern = r'(\d{1,2}):(\d{2})'
        match = re.search(time_pattern, text)
        if match:
            hour, minute = map(int, match.groups())
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return time(hour, minute)
        
        # H MM format (space separated)
        space_pattern = r'(\d{1,2})\s+(\d{2})'
        match = re.search(space_pattern, text)
        if match:
            hour, minute = map(int, match.groups())
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return time(hour, minute)
        
        # Just hour
        hour_pattern = r'\b(\d{1,2})\b'
        match = re.search(hour_pattern, text)
        if match:
            hour = int(match.group(1))
            if 0 <= hour <= 23:
                return time(hour, 0)
        
        return None
    
    def format_date_for_voice(self, date_obj: date) -> str:
        """Format date for voice response"""
        try:
            today = date.today()
            
            # Calculate difference
            diff = (date_obj - today).days
            
            if diff == 0:
                return "astăzi"
            elif diff == 1:
                return "mâine"
            elif diff == 2:
                return "poimâine"
            elif diff == -1:
                return "ieri"
            elif diff == -2:
                return "alaltăieri"
            else:
                # Format as weekday and date
                weekday_names = ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]
                month_names = [
                    "ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
                    "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"
                ]
                
                weekday = weekday_names[date_obj.weekday()]
                month = month_names[date_obj.month - 1]
                
                return f"{weekday}, {date_obj.day} {month}"
                
        except Exception as e:
            self.logger.error(f"Error formatting date for voice: {e}")
            return str(date_obj)
    
    def format_time_for_voice(self, time_obj: time) -> str:
        """Format time for voice response"""
        try:
            hour = time_obj.hour
            minute = time_obj.minute
            
            if minute == 0:
                if hour == 0:
                    return "miezul nopții"
                elif hour == 12:
                    return "amiaza"
                else:
                    return f"ora {hour}"
            elif minute == 15:
                return f"ora {hour} și un sfert"
            elif minute == 30:
                return f"ora {hour} și jumătate"
            elif minute == 45:
                return f"ora {hour} și trei sferturi"
            else:
                return f"ora {hour} și {minute}"
                
        except Exception as e:
            self.logger.error(f"Error formatting time for voice: {e}")
            return str(time_obj)
    
    def format_datetime_for_voice(self, date_obj: date, time_obj: time) -> str:
        """Format both date and time for voice response"""
        try:
            date_str = self.format_date_for_voice(date_obj)
            time_str = self.format_time_for_voice(time_obj)
            return f"{date_str} la {time_str}"
        except Exception as e:
            self.logger.error(f"Error formatting datetime for voice: {e}")
            return f"{date_obj} {time_obj}"
    
    def get_available_time_slots(self, target_date: date) -> List[str]:
        """Get available time slots for a given date"""
        try:
            # Standard business hours: 9:00 - 18:00
            slots = []
            current_time = time(9, 0)
            end_time = time(18, 0)
            
            # Generate 30-minute slots
            while current_time <= end_time:
                slot_str = self.format_time_for_voice(current_time)
                slots.append(slot_str)
                
                # Add 30 minutes
                current_datetime = datetime.combine(target_date, current_time) + timedelta(minutes=30)
                current_time = current_datetime.time()
                
                if current_time > end_time:
                    break
            
            return slots
        except Exception as e:
            self.logger.error(f"Error getting time slots: {e}")
            return ["ora 10", "ora 14", "ora 16"]  # Fallback slots


# Global instance
datetime_parser = RomanianDateTimeParser()


# Convenience functions
def parse_datetime_from_voice(voice_input: str) -> Dict:
    """Parse both date and time from voice input"""
    return datetime_parser.parse_datetime_from_voice(voice_input)


def parse_date_from_voice(voice_input: str) -> Optional[date]:
    """Parse date from voice input"""
    return datetime_parser.parse_date_from_voice(voice_input)


def parse_time_from_voice(voice_input: str) -> Optional[time]:
    """Parse time from voice input"""  
    return datetime_parser.parse_time_from_voice(voice_input)


def format_datetime_for_voice(date_obj: date, time_obj: time) -> str:
    """Format date and time for voice response"""
    return datetime_parser.format_datetime_for_voice(date_obj, time_obj)


def format_date_for_voice(date_obj: date) -> str:
    """Format date for voice response"""
    return datetime_parser.format_date_for_voice(date_obj)


def format_time_for_voice(time_obj: time) -> str:
    """Format time for voice response"""
    return datetime_parser.format_time_for_voice(time_obj)


def get_available_time_slots(target_date: date) -> List[str]:
    """Get available time slots for a given date"""
    return datetime_parser.get_available_time_slots(target_date)