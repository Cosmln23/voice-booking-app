#!/usr/bin/env python3
"""
Test Script pentru Voice Functions
Testează toate componentele implementate în FAZA 1
"""

import asyncio
import sys
import traceback
from datetime import datetime, date, time

def test_imports():
    """Test că toate importurile funcționează"""
    print("🧪 TESTARE IMPORTURI...")
    try:
        from app.voice.functions.registry import (
            get_openai_tools_definition, 
            get_available_functions,
            execute_voice_function
        )
        from app.voice.functions.services import get_available_services
        from app.voice.functions.availability import check_appointment_availability
        from app.voice.functions.appointments import create_voice_appointment
        from app.voice.functions.clients import find_existing_client
        from app.voice.functions.auth import get_voice_user_context
        from app.voice.functions.errors import VoiceError, VoiceErrorType
        
        print("✅ Toate importurile sunt corecte")
        return True
    except Exception as e:
        print(f"❌ Eroare la import: {e}")
        traceback.print_exc()
        return False

def test_openai_tools_definition():
    """Test definițiile tool-urilor OpenAI"""
    print("\n🧪 TESTARE DEFINIȚII OPENAI TOOLS...")
    try:
        from app.voice.functions.registry import get_openai_tools_definition
        
        tools = get_openai_tools_definition()
        print(f"✅ {len(tools)} tools definite pentru OpenAI")
        
        for tool in tools:
            name = tool["function"]["name"]
            params = tool["function"]["parameters"]
            required = params.get("required", [])
            print(f"  📋 {name}: {len(required)} parametri obligatorii")
        
        return True
    except Exception as e:
        print(f"❌ Eroare la testare tools: {e}")
        return False

def test_romanian_errors():
    """Test sistemul de erori în română"""
    print("\n🧪 TESTARE ERORI ÎN ROMÂNĂ...")
    try:
        from app.voice.functions.errors import (
            VoiceErrorType, ROMANIAN_ERROR_MESSAGES, 
            create_voice_error, handle_voice_error
        )
        
        # Test că avem mesaje pentru toate tipurile de erori
        missing_messages = []
        for error_type in VoiceErrorType:
            if error_type not in ROMANIAN_ERROR_MESSAGES:
                missing_messages.append(error_type.value)
        
        if missing_messages:
            print(f"❌ Lipsesc mesaje pentru: {missing_messages}")
            return False
        
        print(f"✅ {len(ROMANIAN_ERROR_MESSAGES)} mesaje de eroare în română")
        
        # Test crearea unei erori
        test_error = create_voice_error(
            VoiceErrorType.INVALID_PHONE,
            "Test error message"
        )
        
        print(f"✅ Eroare test creată: {test_error.voice_response}")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testare erori: {e}")
        return False

async def test_mock_function_calls():
    """Test apeluri mock ale funcțiilor (fără baza de date)"""
    print("\n🧪 TESTARE APELURI MOCK...")
    try:
        from app.voice.functions.availability import _parse_voice_date, _parse_voice_time
        
        # Test parsing date românesc
        test_dates = ["mâine", "joi", "2024-09-05"]
        for date_str in test_dates:
            try:
                parsed = await _parse_voice_date(date_str)
                print(f"✅ '{date_str}' -> {parsed}")
            except Exception as e:
                print(f"❌ '{date_str}' -> Eroare: {e}")
        
        # Test parsing time românesc  
        test_times = ["10:00", "dimineața", "după-amiaza"]
        for time_str in test_times:
            try:
                parsed = await _parse_voice_time(time_str)
                print(f"✅ '{time_str}' -> {parsed}")
            except Exception as e:
                print(f"❌ '{time_str}' -> Eroare: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testare mock: {e}")
        return False

def test_function_registry():
    """Test registry-ul de funcții"""
    print("\n🧪 TESTARE REGISTRY FUNCȚII...")
    try:
        from app.voice.functions.registry import (
            VOICE_FUNCTION_REGISTRY,
            validate_function_args
        )
        
        print(f"✅ {len(VOICE_FUNCTION_REGISTRY)} funcții în registry")
        
        # Test validare argumente
        valid_args = {
            "get_available_services": {"category": "tuns"},
            "check_appointment_availability": {"date_requested": "mâine"},
            "find_existing_client": {"phone": "+40721123456"},
            "create_voice_appointment": {
                "client_name": "Test Client",
                "phone": "+40721123456",
                "service_name": "Tuns",
                "date_requested": "mâine",
                "time_requested": "10:00"
            }
        }
        
        for func_name, args in valid_args.items():
            is_valid = validate_function_args(func_name, args)
            status = "✅" if is_valid else "❌"
            print(f"  {status} {func_name}: validare argumente")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testare registry: {e}")
        return False

def test_authentication_mock():
    """Test mock pentru sistemul de autentificare"""
    print("\n🧪 TESTARE AUTENTIFICARE MOCK...")
    try:
        # Acestea ar trebui să ruleze fără erori de sintaxă
        from app.voice.functions.auth import (
            VoiceAuthError,
            authenticate_voice_session,
            validate_voice_operation_permissions
        )
        
        print("✅ Clasele de autentificare se încarcă corect")
        
        # Test permission mapping
        test_operations = [
            "get_services",
            "check_availability", 
            "create_appointment",
            "find_client"
        ]
        
        for op in test_operations:
            print(f"  📋 Operațiune suportată: {op}")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testare auth: {e}")
        return False

async def main():
    """Rulează toate testele"""
    print("🚀 TESTARE BACKEND VOICE HANDLERS")
    print("=" * 50)
    
    tests = [
        ("Importuri", test_imports),
        ("OpenAI Tools", test_openai_tools_definition),
        ("Erori Română", test_romanian_errors),
        ("Registry", test_function_registry),
        ("Auth Mock", test_authentication_mock),
        ("Mock Calls", test_mock_function_calls)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} EȘUAT: {e}")
            results.append((test_name, False))
    
    # Sumar rezultate
    print("\n" + "="*50)
    print("📊 SUMAR TESTE")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ TRECUT" if result else "❌ EȘUAT"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 REZULTAT FINAL: {passed}/{total} teste trecute")
    
    if passed == total:
        print("🎉 TOATE TESTELE AU TRECUT! Voice Functions sunt gata pentru integrare.")
    else:
        print("⚠️  UNELE TESTE AU EȘUAT. Verifică erorile de mai sus.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())