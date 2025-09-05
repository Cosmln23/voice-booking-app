# 🧪 Voice Functions - Ghid de Testare

## Verificare Implementare FAZA 1

### 1. Verificare Structură Fișiere

```bash
# Verifică că toate fișierele există
find backend/app/voice -type f -name "*.py" | sort
```

**Expected Output:**
```
backend/app/voice/__init__.py
backend/app/voice/functions/__init__.py
backend/app/voice/functions/appointments.py
backend/app/voice/functions/auth.py
backend/app/voice/functions/availability.py
backend/app/voice/functions/clients.py
backend/app/voice/functions/errors.py
backend/app/voice/functions/registry.py
backend/app/voice/functions/services.py
```

### 2. Test de Import și Sintaxă

```bash
# Din directorul backend/
python test_voice_functions.py
```

**Expected Result:** Toate testele trebuie să treacă (6/6)

### 3. Verificare OpenAI Tools Definition

```python
from app.voice.functions.registry import get_openai_tools_definition

tools = get_openai_tools_definition()
print(f"Tools disponibile: {len(tools)}")

# Afișează structura pentru OpenAI API
import json
print(json.dumps(tools[0], indent=2))
```

### 4. Test Funcții Individual

#### 4.1 Test Services Function

```python
# Mock test fără baza de date
from app.voice.functions.services import get_available_services

# Această funcție va eșua fără Supabase client real
# Dar poți vedea structura și validarea argumentelor
```

#### 4.2 Test Romanian Date/Time Parsing

```python
from app.voice.functions.availability import _parse_voice_date, _parse_voice_time
import asyncio

async def test_parsing():
    # Test date românești
    dates = ["mâine", "joi", "2024-09-05", "15.10.2024"]
    for date_str in dates:
        result = await _parse_voice_date(date_str)
        print(f"'{date_str}' -> {result}")
    
    # Test ore românești  
    times = ["10:00", "dimineața", "seara", "două și jumătate"]
    for time_str in times:
        try:
            result = await _parse_voice_time(time_str)
            print(f"'{time_str}' -> {result}")
        except:
            print(f"'{time_str}' -> Nu s-a putut procesa")

asyncio.run(test_parsing())
```

#### 4.3 Test Error Messages

```python
from app.voice.functions.errors import VoiceErrorType, ROMANIAN_ERROR_MESSAGES

# Verifică mesajele în română
error_types = [
    VoiceErrorType.INVALID_PHONE,
    VoiceErrorType.PAST_DATE, 
    VoiceErrorType.CLIENT_NOT_FOUND,
    VoiceErrorType.TIME_SLOT_OCCUPIED
]

for error_type in error_types:
    message = ROMANIAN_ERROR_MESSAGES[error_type]
    print(f"{error_type.value}: {message}")
```

### 5. Test cu Mock Supabase Client

Pentru testare completă cu baza de date, ai nevoie de:

```python
# Mock Supabase client pentru testare
class MockSupabaseClient:
    def table(self, table_name):
        return MockTable()

class MockTable:
    def select(self, *args):
        return self
    def eq(self, field, value):
        return self
    def execute(self):
        return MockResponse()

class MockResponse:
    def __init__(self):
        self.data = []  # Mock data

# Test cu mock client
mock_client = MockSupabaseClient()

# Acum poți testa funcțiile care necesită client
```

### 6. Verificare Integrare Backend

```python
# Verifică că voice functions pot utiliza CRUD-urile existente
from app.database.user_crud_appointments import UserAppointmentCRUD
from app.database.user_crud_clients import UserClientCRUD
from app.models.appointment import AppointmentCreate

print("✅ Voice functions pot utiliza infrastructura existentă")
```

### 7. Test pentru Production

Pentru testare în production environment:

1. **Setup Environment Variables:**
   ```bash
   export VOICE_BUSINESS_OWNER_ID="your-user-uuid"
   ```

2. **Test cu Supabase real:**
   ```python
   from app.database import get_database
   from app.voice.functions.services import get_available_services
   
   # Necesită client Supabase real și user autentificat
   ```

3. **Test cu OpenAI Realtime API:**
   - Configurează OpenAI API key
   - Testează tool calling cu funcțiile definite

## Rezultate Așteptate

### ✅ Success Indicators:

- **Syntax Check**: Toate fișierele se compilează fără erori
- **Import Test**: Toate importurile funcționează  
- **Tools Definition**: 5 tools OpenAI corect definite
- **Romanian Errors**: 23+ mesaje de eroare în română
- **Date/Time Parsing**: Procesează corect expresii românești
- **Registry**: 7 funcții în registry functional

### ❌ Common Issues:

1. **Import Errors**: Verifică PYTHONPATH și structura package-urilor
2. **Missing Dependencies**: Instalează toate requirements
3. **Type Errors**: Verifică type hints și import-urile typing

## Next Steps După Testare

Odată ce toate testele trec:

1. **Integrare cu OpenAI Realtime API**
2. **Setup Twilio Bridge pentru apeluri**  
3. **Test E2E cu apeluri vocale reale**
4. **Monitoring și logging în production**

---

**Status:** FAZA 1 completă ✅  
**Ready for:** OpenAI Realtime API integration și Twilio bridge