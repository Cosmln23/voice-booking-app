"""
Test Suite for Romanian Language Processing
Comprehensive testing for all Romanian language processing modules
"""

import pytest
from datetime import datetime, date, time, timedelta
from typing import Dict, Any

# Import processing modules
from app.voice.processing.name_utils import normalize_name_from_voice, validate_name_format
from app.voice.processing.phone_utils import normalize_phone_from_voice, validate_romanian_phone
from app.voice.processing.service_mapper import map_service_from_voice
from app.voice.processing.datetime_parser import parse_datetime_from_voice
from app.voice.processing.vocabulary import classify_user_intent


class TestRomanianNameProcessing:
    """Test Romanian name processing functionality"""
    
    def test_normalize_simple_name(self):
        """Test simple name normalization"""
        result = normalize_name_from_voice("ion popescu")
        assert result["success"] is True
        assert result["normalized"] == "Ion Popescu"
        assert result["is_romanian"] is True
    
    def test_normalize_name_with_diacritics(self):
        """Test name normalization with Romanian diacritics"""
        result = normalize_name_from_voice("ștefan ionuț")
        assert result["success"] is True
        assert result["normalized"] == "Ștefan Ionuț"
        assert result["has_diacritics"] is True
    
    def test_normalize_complex_name(self):
        """Test complex name with voice variations"""
        result = normalize_name_from_voice("aleksandra maria popesc")
        assert result["success"] is True
        # Should normalize alexandra spelling and add -u ending
        assert "Alexandra" in result["normalized"]
        assert result["confidence"] > 0.7
    
    def test_validate_complete_name(self):
        """Test name validation"""
        result = validate_name_format("Ion Popescu")
        assert result["valid"] is True
        assert result["parts_count"] == 2
    
    def test_validate_incomplete_name(self):
        """Test validation of incomplete name"""
        result = validate_name_format("Ion")
        assert result["valid"] is False
        assert "incomplete" in result["message"].lower()


class TestRomanianPhoneProcessing:
    """Test Romanian phone number processing"""
    
    def test_normalize_mobile_with_country_code(self):
        """Test mobile number with country code - converts to national format"""
        result = normalize_phone_from_voice("+40721123456")
        assert result == "0721123456"  # Should convert to national format
        assert validate_romanian_phone(result) is True
    
    def test_normalize_mobile_without_country_code(self):
        """Test mobile number without country code - keeps national format"""
        result = normalize_phone_from_voice("0721123456")
        assert result == "0721123456"  # Should keep national format
        assert validate_romanian_phone(result) is True
    
    def test_normalize_spelled_digits(self):
        """Test spelled out phone number"""
        result = normalize_phone_from_voice("zero șapte doi unu doi trei patru cinci șase")
        assert result is not None
        assert result.startswith("07")  # Should be in national format
        assert validate_romanian_phone(result) is True
    
    def test_normalize_mixed_format(self):
        """Test mixed format phone number"""
        result = normalize_phone_from_voice("patruzeci 721 123 456")
        assert result == "0721123456"  # Should convert to national format
        assert validate_romanian_phone(result) is True
    
    def test_invalid_phone_number(self):
        """Test invalid phone number"""
        result = normalize_phone_from_voice("123")
        assert result is None
        assert validate_romanian_phone("123") is False


class TestServiceMapping:
    """Test Romanian service name mapping"""
    
    def test_exact_service_match(self):
        """Test exact service name match"""
        result = map_service_from_voice("tuns")
        assert result["success"] is True
        assert result["canonical_name"] == "Tunsoare Clasică"
        assert result["category"] == "tuns"
        assert result["confidence"] >= 0.9
    
    def test_fuzzy_service_match(self):
        """Test fuzzy service matching"""
        result = map_service_from_voice("vreau să mă tund")
        assert result["success"] is True
        assert result["canonical_name"] == "Tunsoare Clasică"
        assert result["confidence"] >= 0.6
    
    def test_variation_service_match(self):
        """Test service variation matching"""
        result = map_service_from_voice("tunsoare clasică")
        assert result["success"] is True
        assert result["canonical_name"] == "Tunsoare Clasică"
    
    def test_beard_service_match(self):
        """Test beard service matching"""
        result = map_service_from_voice("bărbierit")
        assert result["success"] is True
        assert result["canonical_name"] == "Bărbierit Complet"
        assert result["category"] == "barba"
    
    def test_unknown_service(self):
        """Test unknown service handling"""
        result = map_service_from_voice("serviciu inexistent")
        assert result["success"] is False
        assert "suggestions" in result


class TestDateTimeProcessing:
    """Test Romanian date/time processing"""
    
    def test_parse_relative_date(self):
        """Test relative date parsing"""
        result = parse_datetime_from_voice("mâine la 10:00")
        assert result["success"] is True
        assert result["parsed_date"] == (date.today() + timedelta(days=1))
        assert result["parsed_time"] == time(10, 0)
    
    def test_parse_weekday_reference(self):
        """Test weekday reference parsing"""
        result = parse_datetime_from_voice("joi la 14:30")
        assert result["success"] is True
        assert result["parsed_time"] == time(14, 30)
        # Should be next Thursday
        assert result["parsed_date"].weekday() == 3  # Thursday = 3
    
    def test_parse_specific_date(self):
        """Test specific date parsing"""
        result = parse_datetime_from_voice("15 septembrie la ora 16:00")
        assert result["success"] is True
        assert result["parsed_date"].day == 15
        assert result["parsed_date"].month == 9
        assert result["parsed_time"] == time(16, 0)
    
    def test_parse_time_of_day(self):
        """Test time of day parsing"""
        result = parse_datetime_from_voice("mâine dimineața")
        assert result["success"] is True
        assert result["parsed_time"] >= time(9, 0)  # Morning time
        assert result["parsed_time"] <= time(12, 0)
    
    def test_invalid_datetime(self):
        """Test invalid date/time input"""
        result = parse_datetime_from_voice("data inexistentă")
        assert result["success"] is False


class TestVocabularyProcessing:
    """Test Romanian vocabulary and intent classification"""
    
    def test_booking_intent(self):
        """Test booking intent classification"""
        result = classify_user_intent("vreau să mă programez pentru un tuns")
        assert result["success"] is True
        assert result["primary_intent"] == "doresc_programare"
        assert result["confidence"] >= 0.8
    
    def test_service_inquiry_intent(self):
        """Test service inquiry intent"""
        result = classify_user_intent("ce servicii aveți disponibile")
        assert result["success"] is True
        assert result["primary_intent"] == "intrebare_servicii"
    
    def test_schedule_inquiry_intent(self):
        """Test schedule inquiry intent"""
        result = classify_user_intent("la ce ore sunteți deschisi")
        assert result["success"] is True
        assert result["primary_intent"] == "intrebare_program"
    
    def test_price_inquiry_intent(self):
        """Test price inquiry intent"""
        result = classify_user_intent("cât costă o tunsoare")
        assert result["success"] is True
        assert result["primary_intent"] == "intrebare_pret"
    
    def test_confirmation_intent(self):
        """Test confirmation intent"""
        result = classify_user_intent("da, perfect, vreau să confirm")
        assert result["success"] is True
        assert result["primary_intent"] == "confirmare_pozitiva"
    
    def test_mixed_intent(self):
        """Test mixed vocabulary input"""
        result = classify_user_intent("bună ziua, vreau să mă tund mâine dimineața")
        assert result["success"] is True
        assert len(result["vocabulary_terms"]) >= 2
        assert len(result["matched_expressions"]) >= 1


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple processors"""
    
    def test_complete_appointment_request(self):
        """Test complete appointment request processing"""
        voice_input = "Bună ziua, sunt Ion Popescu, numărul meu este zero șapte doi unu doi trei patru cinci șase, vreau să mă programez pentru un tuns mâine la ora zece"
        
        # Extract and process different components
        intent_result = classify_user_intent(voice_input)
        assert intent_result["primary_intent"] == "doresc_programare"
        
        # Extract name (would need more sophisticated extraction in real scenario)
        name_result = normalize_name_from_voice("Ion Popescu")
        assert name_result["success"] is True
        
        # Extract and normalize phone
        phone_result = normalize_phone_from_voice("zero șapte doi unu doi trei patru cinci șase")
        assert phone_result is not None
        assert phone_result.startswith("07")  # Should be in national format
        assert validate_romanian_phone(phone_result) is True
        
        # Extract service
        service_result = map_service_from_voice("tuns")
        assert service_result["success"] is True
        
        # Extract datetime
        datetime_result = parse_datetime_from_voice("mâine la ora zece")
        assert datetime_result["success"] is True
    
    def test_appointment_modification_request(self):
        """Test appointment modification request"""
        voice_input = "Vreau să modific programarea de mâine, să o mut pe joi la 15:00"
        
        intent_result = classify_user_intent(voice_input)
        # This would be a modification intent (not implemented in basic version)
        assert intent_result["success"] is True
        
        datetime_result = parse_datetime_from_voice("joi la 15:00")
        assert datetime_result["success"] is True
        assert datetime_result["parsed_time"] == time(15, 0)
    
    def test_complex_service_request(self):
        """Test complex service request with multiple services"""
        voice_input = "Doresc și tuns și bărbierit pentru sâmbătă dimineața"
        
        # Check for both services
        tuns_result = map_service_from_voice("tuns")
        barbierit_result = map_service_from_voice("bărbierit")
        
        assert tuns_result["success"] is True
        assert barbierit_result["success"] is True
        
        datetime_result = parse_datetime_from_voice("sâmbătă dimineața")
        assert datetime_result["success"] is True


# Test data for edge cases
EDGE_CASE_NAMES = [
    "Maria-Elena Popescu-Ionescu",
    "Ștefan Ionuț Mănescu",
    "Ana Mărioara Gheorghiu",
    "Ion-Cristian de la Constanța"
]

EDGE_CASE_PHONES = [
    "zero zero patruzeci șapte doi unu",
    "plus patruzeci opt unul doi trei",
    "07 21 12 34 56",
    "+40-721-123-456"
]

EDGE_CASE_SERVICES = [
    "vreau să îmi fac părul frumos",
    "am nevoie de o coafură pentru nuntă",
    "să mă bărbieresc frumos",
    "tunsoare scurtă și modernă"
]

EDGE_CASE_DATETIMES = [
    "săptămâna viitoare joi după-amiaza",
    "peste două săptămâni vineri dimineața",
    "luna viitoare pe 15 la ora 17:30",
    "mâine după masa târziu"
]


class TestEdgeCases:
    """Test edge cases and complex scenarios"""
    
    @pytest.mark.parametrize("name", EDGE_CASE_NAMES)
    def test_complex_names(self, name):
        """Test complex Romanian names"""
        result = normalize_name_from_voice(name.lower())
        assert result["success"] is True
        # Should have proper capitalization
        assert result["normalized"][0].isupper()
    
    @pytest.mark.parametrize("phone", EDGE_CASE_PHONES)
    def test_complex_phones(self, phone):
        """Test complex phone number formats"""
        result = normalize_phone_from_voice(phone)
        if result:  # Some edge cases might not be parseable
            assert validate_romanian_phone(result) is True
    
    @pytest.mark.parametrize("service", EDGE_CASE_SERVICES)
    def test_complex_services(self, service):
        """Test complex service descriptions"""
        result = map_service_from_voice(service)
        # Should at least provide suggestions if not exact match
        assert result["success"] is True or "suggestions" in result
    
    @pytest.mark.parametrize("datetime_str", EDGE_CASE_DATETIMES)
    def test_complex_datetimes(self, datetime_str):
        """Test complex date/time expressions"""
        result = parse_datetime_from_voice(datetime_str)
        # Complex expressions might not all be parseable in basic version
        # but should not crash
        assert isinstance(result, dict)
        assert "success" in result


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])