# 🎯 AGENT WORK RULES - Voice Booking App

## 🚨 **REGULA #1: PRECIZIE CHIRURGICALĂ OBLIGATORIE**

**APLICABIL DE LA: 2025-09-02**

### **🎯 METODOLOGIA OBLIGATORIE**

Când întâlnești o problemă, urmezi STRICT această secvență:

#### **1. ANALIZĂ PREALABILĂ DETALIATĂ** 📊
- **NU faci modificări fără înțelegere completă**
- Identifici EXACT sursa problemei (fișier + linie)
- Înțelegi impactul complet al problemei
- Documentezi finding-urile

#### **2. IMPLEMENTARE CHIRURGICALĂ** ⚕️
- **O SINGURĂ soluție, cea mai bună posibilă**
- Modifici DOAR ce este absolut necesar
- **Zero impact asupra restului sistemului**
- Testează înainte să commiti

#### **3. POLITICA DOUĂ ÎNCERCĂRI** ⚠️
- **Încercarea #1**: Implementezi cea mai bună soluție identificată
- **Dacă eșuează → Încercarea #2**: O altă abordare precisă
- **Dacă eșuează din nou → STOP**

#### **4. RAPORT OBLIGATORIU DUPĂ EȘEC** 📝
Dacă ambele încercări eșuează, creezi raport cu:
- Problema exactă identificată
- Cele 2 soluții încercate și de ce au eșuat
- Ipoteze suplimentare neconfirmate
- Cerere de ghidare pentru următorii pași

---

## 🚫 **INTERZIS ABSOLUT**

### **❌ NU MAI FACI NICIODATĂ**:
- Experimentare cu multiple modificări
- "Trial and error" pe cod production
- Push direct pe `main` fără aprobare
- Modificări speculative "poate funcționează"
- Testări repetate cu speranța că "se rezolvă singură"

---

## ✅ **PROTOCOLUL OBLIGATORIU DE LUCRU**

### **🔒 GIT WORKFLOW**
1. **TOATE schimbările se fac pe branch-uri**
2. **NICIUN push direct pe `main`**  
3. **Commit-uri doar după confirmare că funcționează**
4. **Pull Request obligatoriu pentru aprobare**

### **📋 DOCUMENTARE OBLIGATORIE**
- Orice fix important se documentează în `PROJECT-DEPLOYMENT-GUIDE.md`
- Probleme complexe necesită raport separat
- Modificări arhitecturale necesită aprobare prealabilă

### **🧪 TESTARE RESPONSABILĂ**
- Un singur test după implementare
- Dacă testul eșuează = analiză suplimentară, nu teste repetate
- Confirmă că nu ai stricat alte funcționalități

---

## 🎯 **EXEMPLU DE APLICARE CORECTĂ**

### **EXEMPLUL #1**: Client creation API returnează eroare 500  
**Răspuns CORECT**:

1. **Analiză** → Identific conflictul `name` în LogRecord la linia 264 din agent.py
2. **Soluție #1** → Implementez `safe_extra()` utility și fix chirurgical
3. **Test** → Client creation funcționează ✅
4. **Documentare** → Update PROJECT-DEPLOYMENT-GUIDE.md
5. **Branch + PR** → Cer aprobare pentru merge

### **EXEMPLUL #2**: CORS blocking pentru domeniile Vercel  
**Răspuns CORECT**:

1. **Analiză** → Identific că wildcard CORS nu acoperă toate sub-domeniile Vercel complexe
2. **Recomandare** → Prezint 2 opțiuni (regex vs proxy), recomand regex pentru securitate și performanță  
3. **Soluție #1** → Implementez `allow_origin_regex=r"^https:\/\/.*\.vercel\.app$"` în cors.py
4. **Validare** → Testez regex-ul împotriva tuturor domeniilor cunoscute ✅
5. **Branch + Test** → Branch separat, merge cu aprobare, trigger automat Railway deploy ✅

**Răspuns GREȘIT**:
- Încercări multiple de modificări
- Testare repetată cu speranța
- Push direct pe main
- Experimentare cu "poate funcționează"

---

## 🎖️ **PRINCIPII FUNDAMENTALE**

### **1. CALITATEA PESTE VITEZĂ**
- Mai bine o soluție corectă în 30 minute  
- Decât 10 tentative în 3 ore

### **2. ÎNȚELEGERE COMPLETĂ**
- Nu modifici ce nu înțelegi complet
- Documentezi orice schimbare non-trivială

### **3. IMPACT ZERO**
- Orice modificare trebuie să aibă impact zero asupra restului sistemului
- Testezi că nu ai stricat alte funcționalități

### **4. COMUNICARE PROACTIVĂ**
- La orice problemă complexă, ceri ghidare
- Nu persisti cu soluții care nu funcționează
- Raportezi transparent ce nu funcționează

---

## 🚀 **REZULTATE AȘTEPTATE**

Urmând aceste reguli:
- ✅ **Zero regressions** în cod production
- ✅ **Soluții durabile** și bien documentées
- ✅ **Timp redus** pentru debugging
- ✅ **Încredere maximă** în fiecare modificare

---

**⚠️ IMPORTANT**: Aceste reguli sunt OBLIGATORII pentru orice agent care lucrează la Voice Booking App de la această dată înainte. Nerespectarea lor poate compromite stabilitatea întregului sistem production.

---

*Creat: 2025-09-02*  
*Status: OBLIGATORIU pentru toți agenții*  
*Ultima actualizare: 2025-09-02*