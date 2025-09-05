"""
Romanian Business Vocabulary for Salon Services
Comprehensive vocabulary mapping for salon/beauty business terminology
"""

import re
from typing import Dict, List, Set, Optional, Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)

# Professional salon terminology in Romanian
SALON_VOCABULARY = {
    "servicii": {
        "canonical": "servicii",
        "variations": [
            "servicii", "serviciul", "serviciile", "tratamente", "tratament",
            "proceduri", "procedura", "oferte", "prestari", "lucrari",
            "activitati", "operatiuni", "interventii"
        ],
        "context": ["salon", "frizerie", "beauty", "infrumusetare"]
    },
    
    "programare": {
        "canonical": "programare", 
        "variations": [
            "programare", "rezervare", "programez", "rezerv", "appointment",
            "intalnire", "sedinta", "consultatie", "randul", "termin",
            "stabilesc", "fixez", "aranjez"
        ],
        "context": ["data", "ora", "timp", "program", "disponibil"]
    },
    
    "coafor": {
        "canonical": "coafor",
        "variations": [
            "coafor", "coafeza", "frizer", "frizerie", "salon de infrumusetare",
            "salon de coafura", "beauty salon", "hair salon", "stilist",
            "specialist par", "artist par"
        ],
        "context": ["par", "coafura", "tuns", "vopsit", "styling"]
    },
    
    "par": {
        "canonical": "păr",
        "variations": [
            "păr", "par", "parul", "peri", "fire de par", "coama",
            "par lung", "par scurt", "par mediu", "par blond", "par saten"
        ],
        "context": ["tuns", "vopsit", "spalat", "coafat", "aranjat"]
    },
    
    "ora": {
        "canonical": "ora",
        "variations": [
            "ora", "orele", "timpul", "momentul", "ceasul", "programul",
            "intervalul", "perioada", "durata", "minute", "secunde"
        ],
        "context": ["dimineata", "amiaza", "seara", "noaptea", "program"]
    },
    
    "disponibil": {
        "canonical": "disponibil",
        "variations": [
            "disponibil", "disponibila", "liber", "libera", "vacant", "vacanta",
            "deschis", "deschisa", "accesibil", "accesibila", "posibil"
        ],
        "context": ["programare", "rezervare", "ora", "data", "termin"]
    },
    
    "pret": {
        "canonical": "preț",
        "variations": [
            "pret", "preț", "pretul", "prețul", "cost", "costul", "tarif",
            "taxa", "suma", "bani", "plata", "factura", "cheltuiala"
        ],
        "context": ["lei", "ron", "euro", "plata", "card", "cash", "numerar"]
    },
    
    "client": {
        "canonical": "client",
        "variations": [
            "client", "clienta", "clientul", "clienta", "customer", "cumparator",
            "utilizator", "persoana", "domn", "doamna", "domnisoara"
        ],
        "context": ["nume", "prenume", "telefon", "contact", "adresa"]
    }
}

# Salon-specific expressions and phrases
SALON_EXPRESSIONS = {
    "greeting": {
        "patterns": [
            r"salut", r"bună", r"servus", r"hei", r"alo", r"hello",
            r"bună ziua", r"bună dimineața", r"bună seara"
        ],
        "responses": [
            "Bună ziua! Cu ce vă pot ajuta?",
            "Salut! Doriți să faceți o programare?",
            "Bună! La ce serviciu sunteți interesat?"
        ]
    },
    
    "booking_intent": {
        "patterns": [
            r"vreau să mă.*?tund", r"doresc.*?programare", r"pot să fac.*?rezervare",
            r"am nevoie de.*?tuns", r"caut.*?coafor", r"vreau.*?styling",
            r"mă.*?programez", r"rezerv.*?un loc", r"fac.*?o programare"
        ],
        "canonical": "doresc_programare",
        "confidence": 0.9
    },
    
    "service_inquiry": {
        "patterns": [
            r"ce servicii.*?aveți", r"ce.*?faceți", r"cu ce.*?ajutați",
            r"ce.*?proceduri", r"ce.*?tratamente", r"lista.*?servicii"
        ],
        "canonical": "intrebare_servicii",
        "confidence": 0.8
    },
    
    "time_inquiry": {
        "patterns": [
            r"când.*?disponibil", r"ce.*?program.*?aveți", r"la ce ore",
            r"sunteți.*?liberi", r"aveți.*?loc", r"când pot.*?veni"
        ],
        "canonical": "intrebare_program", 
        "confidence": 0.8
    },
    
    "price_inquiry": {
        "patterns": [
            r"cât.*?costă", r"ce.*?preț", r"care.*?tarif", r"cât.*?plătesc",
            r"care.*?cost", r"prețul.*?pentru", r"tariful.*?la"
        ],
        "canonical": "intrebare_pret",
        "confidence": 0.8
    },
    
    "confirmation": {
        "patterns": [
            r"da\b", r"sigur", r"perfect", r"ok", r"bine", r"de acord",
            r"confirm", r"da, vă rog", r"exact", r"corect"
        ],
        "canonical": "confirmare_pozitiva",
        "confidence": 0.9
    },
    
    "negation": {
        "patterns": [
            r"nu\b", r"nicidecum", r"negativ", r"nu, mersi", r"nu mulțumesc",
            r"pass", r"nu vreau", r"nu doresc", r"altceva"
        ],
        "canonical": "negare",
        "confidence": 0.9
    },
    
    "politeness": {
        "patterns": [
            r"vă rog", r"mulțumesc", r"mersi", r"cu plăcere", r"îmi pare rău",
            r"scuzați", r"pardon", r"iertați-mă", r"vă mulțumesc frumos"
        ],
        "canonical": "politete",
        "confidence": 0.7
    }
}

# Time-related vocabulary specific to salon context
SALON_TIME_VOCABULARY = {
    "working_hours": {
        "patterns": [
            r"program.*?lucru", r"ore.*?funcționare", r"când.*?deschis",
            r"la ce ore.*?lucrați", r"programul.*?salonului"
        ],
        "standard_response": "Programul nostru este de luni până vineri 9-18, sâmbătă 9-16."
    },
    
    "busy_times": {
        "morning": ["dimineața", "în dimineața", "pe dimineață", "dimineața devreme"],
        "afternoon": ["după-amiaza", "la amiază", "prin amiază", "după masa"],
        "evening": ["seara", "către seară", "în seară", "seara târziu"],
        "weekend": ["weekend", "sâmbătă", "duminică", "în weekend"]
    }
}

# Common voice recognition errors in salon context
SALON_VOICE_CORRECTIONS = {
    "tuns": ["tons", "tunz", "tunsz"],
    "bărbierit": ["barbierit", "barberit", "bărberi"],
    "coafură": ["coafura", "goafura", "coafeura"],
    "programare": ["proglamare", "programale", "progamare"],
    "disponibil": ["disponibi", "disponibil", "disponibl"],
    "sâmbătă": ["sambata", "sambăta", "sambaata"],
    "duminică": ["duminica", "duminca", "dominca"]
}


class SalonVocabularyProcessor:
    """Advanced salon vocabulary processing for Romanian voice system"""
    
    def __init__(self):
        self.logger = logger
        self.vocabulary = SALON_VOCABULARY
        self.expressions = SALON_EXPRESSIONS
        self.time_vocab = SALON_TIME_VOCABULARY
        self.corrections = SALON_VOICE_CORRECTIONS
        
        # Build search indices
        self._build_search_indices()
    
    def _build_search_indices(self):
        """Build search indices for faster vocabulary matching"""
        self.term_index = {}  # term -> vocabulary_key
        self.pattern_index = {}  # compiled_pattern -> expression_key
        
        # Build vocabulary term index
        for vocab_key, vocab_data in self.vocabulary.items():
            for variation in vocab_data["variations"]:
                self.term_index[variation.lower()] = vocab_key
        
        # Build expression pattern index  
        for expr_key, expr_data in self.expressions.items():
            if "patterns" in expr_data:
                for pattern in expr_data["patterns"]:
                    compiled_pattern = re.compile(pattern, re.IGNORECASE)
                    self.pattern_index[compiled_pattern] = expr_key
    
    def classify_user_intent(self, voice_input: str) -> Dict:
        """
        Classify user intent from voice input
        
        Args:
            voice_input: Raw voice input from user
            
        Returns:
            Dict with classification results
        """
        try:
            # Clean and normalize input
            clean_input = self._clean_voice_input(voice_input)
            
            if not clean_input:
                return {
                    "success": False,
                    "message": "Input vid sau invalid"
                }
            
            # Apply voice corrections
            corrected_input = self._apply_voice_corrections(clean_input)
            
            # Try to match expressions
            matched_expressions = []
            for pattern, expr_key in self.pattern_index.items():
                if pattern.search(corrected_input):
                    expr_data = self.expressions[expr_key]
                    matched_expressions.append({
                        "expression": expr_key,
                        "canonical": expr_data.get("canonical", expr_key),
                        "confidence": expr_data.get("confidence", 0.5)
                    })
            
            # Find vocabulary terms
            found_terms = self._extract_vocabulary_terms(corrected_input)
            
            # Determine primary intent
            primary_intent = self._determine_primary_intent(matched_expressions, found_terms)
            
            return {
                "success": True,
                "original_input": voice_input,
                "cleaned_input": corrected_input,
                "primary_intent": primary_intent,
                "matched_expressions": matched_expressions,
                "vocabulary_terms": found_terms,
                "confidence": self._calculate_confidence(primary_intent, matched_expressions, found_terms)
            }
            
        except Exception as e:
            self.logger.error(f"Error classifying user intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _clean_voice_input(self, text: str) -> str:
        """Clean voice input for processing"""
        if not text:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        clean = text.lower().strip()
        
        # Remove punctuation except Romanian diacritics
        clean = re.sub(r'[^\w\săâîșțĂÂÎȘȚ\s]', ' ', clean)
        
        # Normalize whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _apply_voice_corrections(self, text: str) -> str:
        """Apply common voice recognition corrections"""
        corrected = text
        
        for correct, variants in self.corrections.items():
            for variant in variants:
                corrected = corrected.replace(variant, correct)
        
        return corrected
    
    def _extract_vocabulary_terms(self, text: str) -> List[Dict]:
        """Extract vocabulary terms from text"""
        found_terms = []
        words = text.split()
        
        # Check individual words and phrases
        for i, word in enumerate(words):
            if word in self.term_index:
                vocab_key = self.term_index[word]
                found_terms.append({
                    "term": word,
                    "vocabulary_key": vocab_key,
                    "canonical": self.vocabulary[vocab_key]["canonical"],
                    "position": i
                })
            
            # Check two-word phrases
            if i < len(words) - 1:
                phrase = f"{word} {words[i+1]}"
                if phrase in self.term_index:
                    vocab_key = self.term_index[phrase]
                    found_terms.append({
                        "term": phrase,
                        "vocabulary_key": vocab_key,
                        "canonical": self.vocabulary[vocab_key]["canonical"],
                        "position": i
                    })
        
        return found_terms
    
    def _determine_primary_intent(self, expressions: List[Dict], terms: List[Dict]) -> Optional[str]:
        """Determine the primary user intent"""
        if not expressions and not terms:
            return None
        
        # Priority-based intent determination
        intent_priorities = {
            "doresc_programare": 10,
            "intrebare_servicii": 8,
            "intrebare_program": 7,
            "intrebare_pret": 6,
            "confirmare_pozitiva": 5,
            "negare": 5,
            "politete": 2
        }
        
        best_intent = None
        best_score = 0
        
        for expr in expressions:
            canonical = expr.get("canonical")
            if canonical in intent_priorities:
                score = intent_priorities[canonical] * expr.get("confidence", 0.5)
                if score > best_score:
                    best_intent = canonical
                    best_score = score
        
        # If no expression intent, infer from vocabulary terms
        if not best_intent and terms:
            vocab_keys = [term["vocabulary_key"] for term in terms]
            
            if "programare" in vocab_keys or "servicii" in vocab_keys:
                best_intent = "doresc_programare"
            elif "pret" in vocab_keys:
                best_intent = "intrebare_pret"
            elif "ora" in vocab_keys or "disponibil" in vocab_keys:
                best_intent = "intrebare_program"
        
        return best_intent
    
    def _calculate_confidence(self, intent: Optional[str], expressions: List[Dict], terms: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not intent:
            return 0.0
        
        # Base confidence from expressions
        expr_confidence = 0.0
        if expressions:
            expr_confidence = max(expr.get("confidence", 0.0) for expr in expressions)
        
        # Boost confidence based on vocabulary terms
        term_boost = min(len(terms) * 0.1, 0.3)
        
        # Final confidence
        confidence = min(expr_confidence + term_boost, 1.0)
        
        return confidence
    
    def generate_contextual_response(self, intent: str, terms: List[str] = None) -> str:
        """Generate contextual response based on intent and terms"""
        try:
            responses = {
                "doresc_programare": [
                    "Perfect! Pentru ce serviciu doriți să vă programez?",
                    "Cu plăcere! Ce tratament vă interesează?",
                    "Excelent! Ce serviciu ați dori să rezervați?"
                ],
                "intrebare_servicii": [
                    "Oferim tunsori, bărbierit, styling, spălare și tratamente speciale.",
                    "Avem servicii complete de coafură și îngrijire pentru bărbați și femei.",
                    "Serviciile noastre includ tuns, coafat, vopsit și multe altele."
                ],
                "intrebare_program": [
                    "Suntem deschisi de luni până vineri 9-18, sâmbătă 9-16.",
                    "Programul nostru: L-V 9:00-18:00, Sâmbătă 9:00-16:00.",
                    "Lucrăm zilnic până la 18:00, sâmbăta până la 16:00."
                ],
                "intrebare_pret": [
                    "Prețurile variază în funcție de serviciu. Ce vă interesează?",
                    "Tarifele depind de tratament. Pentru ce serviciu întrebați?",
                    "Prețurile sunt diferite pentru fiecare serviciu. Care vă interesează?"
                ],
                "confirmare_pozitiva": [
                    "Perfect! Continuăm cu programarea.",
                    "Excelent! Să vedem următorul pas.",
                    "Minunat! Urmează să confirmăm detaliile."
                ],
                "negare": [
                    "Înțeleg. Poate altceva?",
                    "În regulă. Ce altceva vă pot ajuta?",
                    "Fără problemă. Cum vă pot fi util?"
                ]
            }
            
            if intent in responses:
                import random
                return random.choice(responses[intent])
            else:
                return "Cum vă pot ajuta cu programarea dumneavoastră?"
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "Cum vă pot ajuta?"
    
    def extract_salon_entities(self, text: str) -> Dict:
        """Extract salon-specific entities from text"""
        try:
            entities = {
                "services": [],
                "times": [],
                "persons": [],
                "prices": [],
                "locations": []
            }
            
            # Service extraction
            service_patterns = [
                r"tuns\w*", r"bărbierit\w*", r"coafur\w*", r"styling\w*",
                r"spălat\w*", r"vopsit\w*", r"tratament\w*"
            ]
            
            for pattern in service_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["services"].extend(matches)
            
            # Time extraction
            time_patterns = [
                r"\d{1,2}:\d{2}", r"\d{1,2}\s*o'?clock", r"dimineața", r"după-amiaza", 
                r"seara", r"mâine", r"azi", r"sâmbătă", r"duminică"
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["times"].extend(matches)
            
            # Price extraction
            price_patterns = [
                r"\d+\s*lei", r"\d+\s*ron", r"\d+\s*euro"
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["prices"].extend(matches)
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Error extracting entities: {e}")
            return {"services": [], "times": [], "persons": [], "prices": [], "locations": []}


# Global instance
vocabulary_processor = SalonVocabularyProcessor()


# Convenience functions
def classify_user_intent(voice_input: str) -> Dict:
    """Classify user intent from voice input"""
    return vocabulary_processor.classify_user_intent(voice_input)


def generate_contextual_response(intent: str, terms: List[str] = None) -> str:
    """Generate contextual response"""
    return vocabulary_processor.generate_contextual_response(intent, terms)


def extract_salon_entities(text: str) -> Dict:
    """Extract salon entities from text"""
    return vocabulary_processor.extract_salon_entities(text)