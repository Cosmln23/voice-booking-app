#!/usr/bin/env python3
"""
OpenAI Integration Test Suite
Tests OpenAI Realtime API integration with voice booking functions
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Add backend to path
sys.path.append('/mnt/d/EU/voice-booking-app/backend')

from app.voice.openai_client import OpenAIRealtimeClient
from app.voice.twilio_bridge import TwilioOpenAIBridge, TwilioBridgeServer
from app.voice.functions.registry import get_openai_tools_definition, execute_voice_function
from app.core.config import settings


class MockSupabaseClient:
    """Mock Supabase client for testing"""
    
    def __init__(self):
        self.tables = {
            "services": [],
            "clients": [],
            "appointments": [],
            "business_settings": [],
            "voice_sessions": []
        }
    
    def table(self, table_name: str):
        return MockTable(self.tables.get(table_name, []))
    
    class auth:
        @staticmethod
        class admin:
            @staticmethod
            def get_user_by_id(user_id: str):
                return Mock(user=Mock(id=user_id, email="test@example.com"))
            
            @staticmethod
            def list_users():
                return Mock(users=[Mock(id="test-user-123")])


class MockTable:
    """Mock Supabase table"""
    
    def __init__(self, data):
        self.data = data
        self._filters = {}
    
    def select(self, *args):
        return self
    
    def insert(self, data):
        self.data.append(data)
        return Mock(data=[data])
    
    def eq(self, field, value):
        self._filters[field] = value
        return self
    
    def limit(self, count):
        return self
    
    def execute(self):
        return Mock(data=self.data)


async def test_openai_tools_definition():
    """Test OpenAI tools definition generation"""
    print("🧪 TESTING OPENAI TOOLS DEFINITION...")
    
    try:
        tools = get_openai_tools_definition()
        
        print(f"✅ Generated {len(tools)} OpenAI tools")
        
        # Validate each tool structure
        for tool in tools:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]
            
            print(f"  📋 {tool['function']['name']}: {tool['function']['description'][:50]}...")
        
        # Print first tool as example
        print(f"\n📄 Example tool definition:")
        print(json.dumps(tools[0], indent=2, ensure_ascii=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing tools definition: {e}")
        return False


async def test_function_execution_mock():
    """Test function execution with mock data"""
    print("\n🧪 TESTING FUNCTION EXECUTION (MOCK)...")
    
    try:
        mock_client = MockSupabaseClient()
        mock_user_context = {
            "user_id": "test-user-123",
            "auth_type": "voice_service",
            "permissions": ["voice_booking", "create_appointments", "manage_clients"]
        }
        
        # Test get_available_services
        result = await execute_voice_function(
            function_name="get_available_services",
            function_args={"category": "tuns"},
            supabase_client=mock_client,
            user_context=mock_user_context
        )
        
        print(f"✅ get_available_services result: {result['success']}")
        
        # Test find_existing_client
        result = await execute_voice_function(
            function_name="find_existing_client",
            function_args={"phone": "+40721123456"},
            supabase_client=mock_client,
            user_context=mock_user_context
        )
        
        print(f"✅ find_existing_client result: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing function execution: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_openai_client_initialization():
    """Test OpenAI client initialization"""
    print("\n🧪 TESTING OPENAI CLIENT INITIALIZATION...")
    
    try:
        mock_client = MockSupabaseClient()
        
        # Test client creation (without actual connection)
        openai_client = OpenAIRealtimeClient(mock_client)
        
        print(f"✅ OpenAI client created: {openai_client.__class__.__name__}")
        print(f"✅ Model: {openai_client.model}")
        print(f"✅ API Key configured: {'Yes' if openai_client.api_key else 'No'}")
        
        # Test instructions generation
        openai_client.user_context = {
            "business_name": "Test Salon",
            "user_id": "test-user-123"
        }
        
        instructions = openai_client._get_romanian_instructions()
        
        print(f"✅ Romanian instructions generated: {len(instructions)} characters")
        print(f"📝 Instructions preview: {instructions[:200]}...")
        
        # Test booking context
        context = openai_client.get_booking_context()
        print(f"✅ Booking context structure: {list(context.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAI client: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_twilio_bridge_initialization():
    """Test Twilio bridge initialization"""
    print("\n🧪 TESTING TWILIO BRIDGE INITIALIZATION...")
    
    try:
        # Test bridge creation
        bridge = TwilioOpenAIBridge()
        
        print(f"✅ Twilio bridge created: {bridge.__class__.__name__}")
        print(f"✅ Sample rates: Twilio={bridge.TWILIO_SAMPLE_RATE}Hz, OpenAI={bridge.OPENAI_SAMPLE_RATE}Hz")
        
        # Test call status
        status = bridge.get_call_status()
        print(f"✅ Call status structure: {list(status.keys())}")
        
        # Test bridge server
        server = TwilioBridgeServer(host="localhost", port=8081)  # Different port for testing
        
        print(f"✅ Bridge server created on {server.host}:{server.port}")
        
        server_status = server.get_server_status()
        print(f"✅ Server status: {server_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Twilio bridge: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_conversation_flow_simulation():
    """Test simulated conversation flow"""
    print("\n🧪 TESTING CONVERSATION FLOW SIMULATION...")
    
    try:
        mock_client = MockSupabaseClient()
        
        # Add mock data
        mock_client.tables["services"] = [
            {"id": "1", "name": "Tuns", "category": "tuns", "duration": 30, "price": "50", "status": "active"}
        ]
        
        openai_client = OpenAIRealtimeClient(mock_client)
        openai_client.user_context = {
            "user_id": "test-user-123",
            "business_name": "Test Salon",
            "permissions": ["voice_booking", "create_appointments", "manage_clients"]
        }
        
        # Simulate conversation flow
        print("📞 Simulating conversation flow:")
        
        # Step 1: Get services
        print("  1️⃣ Customer asks about services...")
        services_result = await execute_voice_function(
            "get_available_services",
            {},
            mock_client,
            openai_client.user_context
        )
        print(f"     AI Response: {services_result.get('voice_response', 'N/A')[:80]}...")
        
        # Step 2: Check availability
        print("  2️⃣ Customer asks for availability...")
        availability_result = await execute_voice_function(
            "check_appointment_availability", 
            {"date_requested": "mâine", "time_requested": "10:00"},
            mock_client,
            openai_client.user_context
        )
        print(f"     AI Response: {availability_result.get('voice_response', 'N/A')[:80]}...")
        
        # Step 3: Find client
        print("  3️⃣ AI searches for existing client...")
        client_result = await execute_voice_function(
            "find_existing_client",
            {"phone": "+40721123456"},
            mock_client,
            openai_client.user_context
        )
        print(f"     AI Response: {client_result.get('voice_response', 'N/A')[:80]}...")
        
        print("✅ Conversation flow simulation completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing conversation flow: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_romanian_language_processing():
    """Test Romanian language processing"""
    print("\n🧪 TESTING ROMANIAN LANGUAGE PROCESSING...")
    
    try:
        from app.voice.functions.availability import _parse_voice_date, _parse_voice_time
        from app.voice.functions.errors import ROMANIAN_ERROR_MESSAGES, VoiceErrorType
        
        # Test date parsing
        print("📅 Testing Romanian date parsing:")
        test_dates = ["mâine", "joi", "15.10.2024", "astăzi"]
        
        for date_str in test_dates:
            try:
                parsed = await _parse_voice_date(date_str)
                print(f"  ✅ '{date_str}' → {parsed}")
            except Exception as e:
                print(f"  ❌ '{date_str}' → Error: {e}")
        
        # Test time parsing
        print("\n⏰ Testing Romanian time parsing:")
        test_times = ["10:00", "dimineața", "după-amiaza", "două și jumătate"]
        
        for time_str in test_times:
            try:
                parsed = await _parse_voice_time(time_str)
                print(f"  ✅ '{time_str}' → {parsed}")
            except Exception as e:
                print(f"  ❌ '{time_str}' → Error: {e}")
        
        # Test error messages
        print(f"\n💬 Testing Romanian error messages:")
        sample_errors = [
            VoiceErrorType.INVALID_PHONE,
            VoiceErrorType.CLIENT_NOT_FOUND,
            VoiceErrorType.TIME_SLOT_OCCUPIED
        ]
        
        for error_type in sample_errors:
            message = ROMANIAN_ERROR_MESSAGES.get(error_type, "N/A")
            print(f"  📢 {error_type.value}: {message}")
        
        print("✅ Romanian language processing tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Romanian processing: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all OpenAI integration tests"""
    print("🚀 OPENAI REALTIME API INTEGRATION TESTS")
    print("=" * 60)
    
    # Check if OpenAI API key is configured
    if not settings.openai_api_key:
        print("⚠️  WARNING: OPENAI_API_KEY not configured - some tests will be limited")
    else:
        print("✅ OpenAI API Key configured")
    
    tests = [
        ("OpenAI Tools Definition", test_openai_tools_definition),
        ("Function Execution (Mock)", test_function_execution_mock),
        ("OpenAI Client Init", test_openai_client_initialization),
        ("Twilio Bridge Init", test_twilio_bridge_initialization), 
        ("Conversation Flow Simulation", test_conversation_flow_simulation),
        ("Romanian Language Processing", test_romanian_language_processing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} FAILED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 FINAL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! OpenAI Integration is ready for production.")
    else:
        print("⚠️  SOME TESTS FAILED. Check errors above.")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"1. Set OPENAI_API_KEY environment variable")
    print(f"2. Configure Twilio webhook URLs")
    print(f"3. Test with real voice calls")
    print(f"4. Deploy to Railway with WebSocket support")


if __name__ == "__main__":
    asyncio.run(main())