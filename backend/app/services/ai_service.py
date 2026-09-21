"""AI Service - Handles all AI-powered features using OpenAI/LangChain."""
import json
from typing import Optional
from app.config import settings

# Mock AI responses when no API key is configured
MOCK_MODE = not settings.OPENAI_API_KEY


def _get_client():
    if MOCK_MODE:
        return None
    from openai import OpenAI
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _ai_call(system_prompt: str, user_prompt: str) -> str:
    """Make an AI API call or return mock response."""
    if MOCK_MODE:
        return _mock_response(system_prompt, user_prompt)
    
    client = _get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )
    return response.choices[0].message.content


def generate_fir(complaint_text: str, category: str = "") -> dict:
    """Generate a structured FIR from natural language complaint."""
    system_prompt = """You are a legal document generator for Indian Police FIR (First Information Report).
    Generate a properly formatted FIR from the given complaint. Return JSON with:
    - fir_text: The formal FIR document text
    - legal_sections: List of applicable IPC/BNS sections with descriptions
    - investigation_steps: List of recommended investigation steps
    - required_evidence: List of evidence that should be collected
    - priority: One of 'critical', 'high', 'medium', 'low'
    - priority_reasoning: Brief explanation of priority assignment
    - crime_category: The category of crime"""
    
    user_prompt = f"Complaint: {complaint_text}\nCategory: {category}"
    
    if MOCK_MODE:
        return {
            "fir_text": f"""FIRST INFORMATION REPORT (F.I.R.)
            
Under Section 154 Cr.P.C.

1. District: [To be filled] | P.S.: [To be filled] | Year: 2026 | FIR No.: [Auto-generated]
2. Date & Time of Occurrence: [As per complaint]
3. Type of Information: Written / Oral

COMPLAINT DETAILS:
{complaint_text}

This FIR is being registered based on the above complaint. The matter requires immediate investigation 
as per the applicable sections of the Indian Penal Code / Bharatiya Nyaya Sanhita.

Signature of the Complainant | Signature of the Officer""",
            "legal_sections": [
                {"section": "Section 420 IPC", "description": "Cheating and dishonestly inducing delivery of property"},
                {"section": "Section 406 IPC", "description": "Criminal breach of trust"},
                {"section": "Section 34 IPC", "description": "Common intention"}
            ],
            "investigation_steps": [
                "Record detailed statement of the complainant",
                "Collect all documentary evidence mentioned",
                "Identify and summon witnesses",
                "Obtain CCTV footage from relevant locations",
                "Send forensic evidence for examination",
                "Issue notice under Section 41A CrPC to suspects"
            ],
            "required_evidence": [
                "Written complaint with signature",
                "Identity proof of complainant",
                "Documentary evidence (receipts, messages, emails)",
                "CCTV footage",
                "Witness statements",
                "Digital forensic evidence"
            ],
            "priority": "high",
            "priority_reasoning": "Based on the nature of the complaint involving potential financial fraud and multiple victims, this case is classified as high priority requiring immediate investigation.",
            "crime_category": category or "fraud"
        }
    
    result = _ai_call(system_prompt, user_prompt)
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"fir_text": result, "legal_sections": [], "investigation_steps": [], 
                "required_evidence": [], "priority": "medium", "priority_reasoning": "Auto-classified",
                "crime_category": category}


def get_legal_suggestions(case_description: str, category: str) -> dict:
    """Get AI-powered legal section suggestions."""
    if MOCK_MODE:
        sections_map = {
            "cybercrime": [
                {"section": "Section 66 IT Act", "description": "Computer related offences", "penalty": "Up to 3 years imprisonment and/or fine up to ₹5 lakhs"},
                {"section": "Section 66C IT Act", "description": "Identity theft", "penalty": "Up to 3 years imprisonment and fine up to ₹1 lakh"},
                {"section": "Section 66D IT Act", "description": "Cheating by personation using computer resource", "penalty": "Up to 3 years imprisonment and fine up to ₹1 lakh"},
                {"section": "Section 43 IT Act", "description": "Penalty for damage to computer systems", "penalty": "Compensation up to ₹1 crore"}
            ],
            "theft": [
                {"section": "Section 378 IPC", "description": "Theft", "penalty": "Up to 3 years imprisonment and/or fine"},
                {"section": "Section 379 IPC", "description": "Punishment for theft", "penalty": "Up to 3 years imprisonment and/or fine"},
                {"section": "Section 411 IPC", "description": "Dishonestly receiving stolen property", "penalty": "Up to 3 years imprisonment and/or fine"}
            ],
            "fraud": [
                {"section": "Section 420 IPC", "description": "Cheating and dishonestly inducing delivery of property", "penalty": "Up to 7 years imprisonment and fine"},
                {"section": "Section 406 IPC", "description": "Criminal breach of trust", "penalty": "Up to 3 years imprisonment and/or fine"},
                {"section": "Section 467 IPC", "description": "Forgery of valuable security", "penalty": "Up to 10 years imprisonment and fine"}
            ],
            "assault": [
                {"section": "Section 323 IPC", "description": "Voluntarily causing hurt", "penalty": "Up to 1 year imprisonment and/or fine up to ₹1000"},
                {"section": "Section 325 IPC", "description": "Voluntarily causing grievous hurt", "penalty": "Up to 7 years imprisonment and fine"},
                {"section": "Section 307 IPC", "description": "Attempt to murder", "penalty": "Up to 10 years imprisonment and fine"}
            ]
        }
        return {
            "sections": sections_map.get(category, sections_map["fraud"]),
            "procedures": [
                "File FIR at nearest police station",
                "Collect and preserve all evidence",
                "Record statements of witnesses",
                "Obtain medical/forensic reports if applicable",
                "Apply for anticipatory bail if needed",
                "Follow up with investigating officer regularly"
            ]
        }
    
    system_prompt = """You are an Indian legal expert. Suggest applicable legal sections, penalties, 
    and investigation procedures for the given case. Return JSON with 'sections' (list of objects with 
    section, description, penalty) and 'procedures' (list of steps)."""
    
    result = _ai_call(system_prompt, f"Case: {case_description}\nCategory: {category}")
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"sections": [], "procedures": []}


def classify_priority(case_description: str, category: str) -> dict:
    """AI-powered case priority classification."""
    if MOCK_MODE:
        # Simple rule-based classification for demo
        critical_keywords = ["murder", "kidnap", "terrorism", "bomb", "hostage", "rape"]
        high_keywords = ["assault", "robbery", "extortion", "stalking", "threat"]
        
        desc_lower = case_description.lower()
        cat_lower = category.lower()
        
        if any(k in desc_lower or k in cat_lower for k in critical_keywords):
            return {"priority": "critical", "reasoning": "Case involves severe criminal activity requiring immediate action."}
        elif any(k in desc_lower or k in cat_lower for k in high_keywords):
            return {"priority": "high", "reasoning": "Case involves significant threat to person/property requiring urgent attention."}
        elif category in ["cybercrime", "fraud", "white_collar"]:
            return {"priority": "medium", "reasoning": "Financial/digital crime requiring systematic investigation."}
        else:
            return {"priority": "medium", "reasoning": "Standard case requiring regular investigation procedures."}
    
    system_prompt = """Classify the case priority as 'critical', 'high', 'medium', or 'low'.
    Return JSON with 'priority' and 'reasoning'."""
    result = _ai_call(system_prompt, f"Case: {case_description}\nCategory: {category}")
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"priority": "medium", "reasoning": "Auto-classified"}


def _match_topic(message: str, keywords: list) -> bool:
    """Check if message matches any keyword."""
    msg = message.lower()
    return any(k in msg for k in keywords)


# Knowledge base: each entry has keywords to match and the response text
_KNOWLEDGE_BASE = [
    {
        "keywords": ["file fir", "file an fir", "lodge fir", "register fir", "write fir", "fir process", "how to fir", "filing fir", "file a complaint", "lodge complaint", "register complaint", "file complaint"],
        "response": """📋 **How to File an FIR (First Information Report):**

**Step-by-Step Process:**
1. Visit the nearest police station (jurisdiction where the crime occurred)
2. Narrate the incident to the duty officer verbally or in writing
3. The officer will record your statement and register the FIR
4. You will receive a copy of the FIR with a unique FIR number
5. Keep this number safe — you'll need it to track your case

**Important Rights:**
- Police **cannot refuse** to register an FIR (Section 154 CrPC)
- If refused, you can send a written complaint to the SP/SSP or file with the Magistrate under Section 156(3)
- You can also file a **Zero FIR** at ANY police station, regardless of jurisdiction
- You are entitled to a **free copy** of the FIR

**Online FIR Options:**
- Many states allow e-FIR via their police websites
- National Cybercrime Portal: **cybercrime.gov.in** (for cyber offences)

**Documents to Carry:**
- Government ID proof (Aadhaar, Voter ID, Passport)
- Any evidence you have (screenshots, documents, photos)
- Details of witnesses, if any

Would you like help drafting your complaint?"""
    },
    {
        "keywords": ["my rights", "victim rights", "legal rights", "what rights", "rights as victim", "rights of victim"],
        "response": """⚖️ **Your Rights as a Victim / Complainant:**

**Fundamental Rights:**
1. **Right to file FIR** — Police cannot refuse (Section 154 CrPC)
2. **Right to free FIR copy** — Must be provided immediately
3. **Right to Zero FIR** — File at any police station, regardless of jurisdiction
4. **Right to legal aid** — Free lawyer if you can't afford one (Article 39A)
5. **Right to know case progress** — You can ask the IO for updates

**During Investigation:**
- Right to be treated with dignity and respect
- Right to have a female officer present (for women/children)
- Right to medical examination (in assault cases)
- Right to protection from the accused
- Right to victim compensation under government schemes

**In Court:**
- Right to engage a private lawyer
- Right to be informed about bail hearings
- Right to file an appeal if unsatisfied with the verdict
- Right to victim impact statement

**Helpline Numbers:**
- 📞 Emergency: **112**
- 👩 Women Helpline: **181**
- 🌐 Cybercrime: **1930**
- 👶 Child Helpline: **1098**
- 🏛️ Legal Aid: **NALSA — 15100**

Would you like guidance on any specific right?"""
    },
    {
        "keywords": ["cyber", "hack", "phishing", "online fraud", "internet", "social media", "digital", "ransomware", "malware", "email scam", "otp", "upi fraud"],
        "response": """🛡️ **Cybercrime — Guidance & Reporting:**

**If You Are a Victim:**
1. **Don't panic** — Document everything immediately
2. Take **screenshots** of messages, emails, transactions
3. Note down phone numbers, email IDs, UPI IDs of the fraudster
4. **Do NOT delete** any evidence (chats, call logs, emails)
5. Report within **24 hours** for best chance of fund recovery

**How to Report:**
- 🌐 **National Cybercrime Portal**: cybercrime.gov.in
- 📞 **Helpline**: 1930 (available 24/7)
- 🏛️ Local **Cyber Crime Cell** at your nearest police station
- 🏦 **RBI** for banking fraud: cms.rbi.org.in
- Inform your **bank immediately** to freeze the transaction

**Common Cyber Threats:**
| Threat | Description |
|--------|-------------|
| Phishing | Fake emails/SMS to steal credentials |
| UPI Fraud | Fake payment requests or QR codes |
| Identity Theft | Misusing your personal details |
| Ransomware | Locking your data and demanding ransom |
| Sextortion | Blackmailing with intimate content |

**Prevention Tips:**
- Never share OTP, PIN, or CVV with anyone
- Enable **2-Factor Authentication** on all accounts
- Verify URLs before clicking — look for **https://**
- Don't install apps from unknown sources
- Regularly change passwords

**Applicable Laws:**
- Section 66 IT Act — Computer related offences (up to 3 yrs)
- Section 66C IT Act — Identity theft (up to 3 yrs + fine)
- Section 66D IT Act — Cheating by personation (up to 3 yrs)
- Section 43 IT Act — Damage to computer systems (₹1 Cr compensation)

What specific cybercrime issue can I help you with?"""
    },
    {
        "keywords": ["ipc", "section", "bns", "legal section", "penal code", "law section", "applicable section", "which section", "punishment for"],
        "response": """⚖️ **Indian Legal Sections — Quick Reference:**

**Common IPC Sections:**
| Section | Offence | Punishment |
|---------|---------|------------|
| 302 | Murder | Life imprisonment / Death |
| 307 | Attempt to murder | Up to 10 years + fine |
| 376 | Rape | 10 years to life imprisonment |
| 420 | Cheating / Fraud | Up to 7 years + fine |
| 406 | Criminal breach of trust | Up to 3 years + fine |
| 354 | Assault on woman | 1-5 years + fine |
| 498A | Dowry harassment | Up to 3 years + fine |
| 379 | Theft | Up to 3 years + fine |
| 392 | Robbery | Up to 10 years + fine |
| 323 | Voluntarily causing hurt | Up to 1 year + fine |
| 506 | Criminal intimidation | Up to 2 years + fine |

**IT Act Sections (Cybercrime):**
| Section | Offence | Punishment |
|---------|---------|------------|
| 66 | Computer offences | Up to 3 years + ₹5L fine |
| 66C | Identity theft | Up to 3 years + ₹1L fine |
| 66D | Cheating by personation | Up to 3 years + ₹1L fine |
| 67 | Publishing obscene content | Up to 5 years + ₹10L fine |

**Note:** India is transitioning from IPC to **Bharatiya Nyaya Sanhita (BNS)** 2023. New section numbers may apply.

Ask me about a specific crime to get the exact applicable sections!"""
    },
    {
        "keywords": ["evidence", "proof", "document", "preserve", "collect evidence", "chain of custody", "forensic"],
        "response": """🔍 **Evidence Collection & Preservation Guide:**

**Types of Evidence:**
1. **Physical** — Weapons, clothing, biological samples
2. **Documentary** — Letters, receipts, contracts, bank statements
3. **Digital** — Screenshots, emails, call logs, CCTV footage
4. **Testimonial** — Witness statements, victim statements

**Collection Best Practices:**
- Photograph everything before touching
- Use gloves when handling physical evidence
- Maintain a **chain of custody** log for every item
- Seal evidence in tamper-proof bags with labels
- Record date, time, location, and collector's name

**Digital Evidence:**
- Take screenshots with **timestamps** visible
- Save original files — don't edit or crop
- Record **hash values** (MD5/SHA256) for integrity
- Clone hard drives before forensic examination
- Preserve metadata (file creation dates, GPS data)

**CCTV Footage:**
- Request within **72 hours** (before overwritten)
- Get footage in original format (not re-recorded)
- Obtain certificate under Section 65B of Indian Evidence Act

**Legal Admissibility:**
- Digital evidence requires **Section 65B certificate**
- Original documents preferred over photocopies
- Witnesses must verify their statements in court

Need help with a specific evidence-related query?"""
    },
    {
        "keywords": ["investigate", "investigation", "crime scene", "procedure", "detective", "case solve"],
        "response": """📋 **Investigation Procedures & Guidelines:**

**Initial Response:**
1. Secure and cordon off the crime scene
2. Identify and separate witnesses
3. Call forensic team if needed
4. Begin documenting scene (photos, sketches, notes)

**Investigation Steps:**
1. Record FIR and victim statement (Section 154 CrPC)
2. Visit crime scene and prepare **panchnama**
3. Collect and seal physical evidence
4. Record witness statements (Section 161 CrPC)
5. Obtain CCTV footage from nearby locations
6. Send forensic evidence to **FSL** (Forensic Science Lab)
7. Arrest suspect with proper procedure (Sections 41-60 CrPC)
8. File **chargesheet** within 60/90 days

**Digital Investigation:**
- Obtain CDR (Call Detail Records) from telecom providers
- Request IP logs from ISPs
- Analyze social media accounts
- Use IMEI tracking for stolen devices

**Legal Timelines:**
- Chargesheet: **60 days** (serious offences) / **90 days** (others)
- Custody: Max **15 days** police custody, **60/90 days** judicial
- Complete investigation before filing final report

**Tools Available:**
- CCTNS (Crime and Criminal Tracking Network)
- NATGRID for inter-agency data sharing
- Forensic labs for DNA, ballistics, digital forensics

What specific aspect of investigation do you need help with?"""
    },
    {
        "keywords": ["bail", "anticipatory bail", "regular bail", "get bail", "bail process", "jail"],
        "response": """🏛️ **Bail — Types & Procedures:**

**Types of Bail:**
1. **Regular Bail** (Section 437/439 CrPC) — After arrest
2. **Anticipatory Bail** (Section 438 CrPC) — Before arrest
3. **Interim Bail** — Temporary, pending final hearing
4. **Default Bail** (Section 167(2) CrPC) — If chargesheet not filed in time

**How to Apply:**
- Through a **lawyer** before the appropriate court
- Sessions Court or High Court for anticipatory bail
- Magistrate Court for regular bail (bailable offences)

**Bailable vs Non-Bailable:**
| Bailable | Non-Bailable |
|----------|-------------|
| Bail is a **right** | Bail at **court's discretion** |
| Police can grant at station | Only court can grant |
| e.g., Theft, Cheating | e.g., Murder, Kidnapping |

**Conditions Usually Imposed:**
- Surrender passport
- Regular attendance at police station
- Not tampering with evidence/witnesses
- Providing surety/bond

**Important Notes:**
- Right to legal aid if unable to afford a lawyer
- Bail applications can be filed multiple times
- Undertrial prisoners held beyond half the max sentence may apply for bail

Need specific guidance on a bail matter?"""
    },
    {
        "keywords": ["women", "domestic violence", "dowry", "harassment", "sexual", "molestation", "stalking", "eve teasing", "protection of women"],
        "response": """👩 **Women Safety — Laws & Resources:**

**Key Laws for Protection:**
- **Section 354 IPC** — Assault on woman (1-5 years)
- **Section 376 IPC** — Rape (10 years to life)
- **Section 498A IPC** — Dowry harassment (up to 3 years)
- **Section 354D IPC** — Stalking (up to 3 years)
- **Domestic Violence Act, 2005** — Protection orders, residence rights
- **POCSO Act** — Protection of children from sexual offences
- **Sexual Harassment at Workplace Act, 2013**

**Immediate Steps if in Danger:**
1. Call **112** (Emergency) or **181** (Women Helpline)
2. Reach the nearest police station
3. Go to a **One Stop Centre (Sakhi)** for shelter + legal + medical help
4. Apply for a **Protection Order** under DV Act

**How to Report:**
- File FIR at any police station (Zero FIR)
- Online: **cybercrime.gov.in** (for online harassment)
- **NCW** (National Commission for Women): ncw.nic.in
- She-Box portal for workplace harassment

**Helplines:**
- 📞 **181** — Women Helpline (24/7)
- 📞 **112** — Emergency
- 📞 **1091** — Women Police Helpline
- 📞 **1098** — Child Helpline

You are not alone. How can I help further?"""
    },
    {
        "keywords": ["missing", "kidnap", "abduct", "lost person", "child missing", "missing person"],
        "response": """🔎 **Missing Person / Kidnapping — Immediate Steps:**

**What To Do Immediately:**
1. File a **missing person report** at the nearest police station
2. Police **cannot refuse** or ask you to wait 24 hours — this is a myth
3. Provide a recent photograph and physical description
4. Share last known location, clothing, and contacts

**Information to Provide:**
- Full name, age, height, weight, complexion
- Last seen location, date, and time
- Clothing and distinguishing marks
- Mobile number and IMEI (check phone box)
- Recent contacts and social media accounts

**Police Actions:**
- FIR under **Section 363 IPC** (Kidnapping) if foul play suspected
- Alert to nearby stations and state CCTNS
- CCTV footage collection from last seen area
- Mobile phone tracking via service provider
- Public announcement / social media alerts

**Helplines:**
- 📞 **112** — Emergency
- 📞 **1098** — Child Helpline (for missing children)
- 📞 **trackthemissingchild.gov.in** — National portal
- State-specific helplines

**For Kidnapping Cases:**
- Applicable Sections: 359-369 IPC
- Punishment: Up to 7-10 years imprisonment
- Ransom demand: Section 364A (may extend to death penalty)

Time is critical. Report immediately!"""
    },
    {
        "keywords": ["theft", "robbery", "burglary", "stolen", "stole", "steal", "stealing", "snatch", "pickpocket", "house break"],
        "response": """🚨 **Theft / Robbery — Report & Recovery:**

**Immediate Steps:**
1. Call **112** if the crime is in progress
2. Note down descriptions — suspect, vehicle, direction of escape
3. Do NOT touch anything at the crime scene
4. File FIR at the nearest police station immediately

**Applicable Legal Sections:**
| Offence | Section | Punishment |
|---------|---------|------------|
| Theft | 379 IPC | Up to 3 years + fine |
| Robbery | 392 IPC | Up to 10 years + fine |
| Dacoity | 395 IPC | Up to life imprisonment |
| House-breaking | 457 IPC | Up to 5 years + fine |
| Snatching | 356 + 379 IPC | Up to 5 years |
| Stolen property | 411 IPC | Up to 3 years + fine |

**For Stolen Mobile/Device:**
- Block your SIM immediately via carrier helpline
- Report IMEI to **CEIR portal** (ceir.gov.in) to block the device
- Change passwords for all linked accounts
- File FIR mentioning make, model, and IMEI number

**Evidence to Preserve:**
- CCTV footage from nearby areas
- Purchase bills / warranty cards (for ownership proof)
- Bank/UPI transaction records
- Witness contact details

What was stolen? I can provide more specific guidance."""
    },
    {
        "keywords": ["hello", "hi", "hey", "good morning", "good evening", "namaste", "help"],
        "response": """👋 **Hello! I'm CrimeGPT Assistant.**

I'm here to help you with legal guidance, crime reporting, and investigation support. Here's what I can do:

🔹 **Ask me about:**
- How to file an FIR or complaint
- Your legal rights as a victim
- Cybercrime reporting and prevention
- Applicable IPC/IT Act sections for any offence
- Evidence collection and preservation
- Investigation procedures
- Bail process and types
- Women safety laws and helplines
- Missing person procedures
- Theft/robbery reporting

🔹 **Quick Helplines:**
- 📞 Emergency: **112**
- 👩 Women: **181**
- 🌐 Cybercrime: **1930**
- 👶 Child: **1098**

**Try asking:**
- "How do I file an FIR?"
- "What are my rights as a victim?"
- "Someone hacked my account, what do I do?"
- "What IPC section applies to theft?"
- "How does bail work?"

What can I help you with today?"""
    },
    {
        "keywords": ["track", "status", "progress", "follow up", "check fir", "fir status", "complaint status", "case status"],
        "response": """📊 **Track Your FIR / Case Status:**

**Online Tracking:**
1. Visit your state police website (e.g., delhipolice.gov.in)
2. Go to "FIR Status" or "Citizen Services" section
3. Enter your FIR number, year, and police station
4. View current status and investigation updates

**Other Methods:**
- Contact the **Investigating Officer (IO)** directly
- Visit the police station and request a progress update
- Send a written request to the **SP/SSP** if no response
- File an RTI application for case details
- Check **CCTNS** portal if available in your state

**Your Rights:**
- You have the right to know the status of your case
- Police must provide updates when requested
- If chargesheet is filed, you'll be notified by court

**If No Action Taken:**
1. Send written complaint to the **Superintendent of Police (SP)**
2. File complaint with **State Human Rights Commission**
3. Approach the **Magistrate under Section 156(3) CrPC**
4. File a **PIL** or writ petition in High Court

**CrimeGPT Tip:** In this app, go to **Cases** page to see all your filed cases and their real-time status.

Need help following up on a specific case?"""
    },
    {
        "keywords": ["lawyer", "legal aid", "advocate", "attorney", "legal help", "court", "how to get lawyer"],
        "response": """🏛️ **Legal Aid & Finding a Lawyer:**

**Free Legal Aid (Your Right):**
- Under **Article 39A** of the Constitution, every citizen has the right to free legal aid
- **NALSA** (National Legal Services Authority) provides free lawyers
- Helpline: **15100**
- Website: nalsa.gov.in

**Who is Eligible for Free Legal Aid?**
- Women and children
- SC/ST community members
- Persons with disabilities
- Victims of human trafficking
- Industrial workers
- Persons in custody
- Anyone with annual income below ₹3 lakhs (varies by state)

**How to Find a Lawyer:**
1. Contact your **District Legal Services Authority (DLSA)**
2. Visit the local **Bar Association** at your district court
3. Use online platforms: Bar Council of India website
4. Ask for referrals from NGOs working in legal aid

**Important Tips:**
- Always get a **written fee agreement** before hiring
- Ask about their experience with your type of case
- Verify their Bar Council registration number
- Keep copies of all documents you share

Need more specific legal guidance?"""
    },
    {
        "keywords": ["fraud", "scam", "cheated", "money lost", "financial fraud", "cheat"],
        "response": """💰 **Fraud / Scam — Reporting & Recovery:**

**Immediate Steps:**
1. **Contact your bank** to block/freeze the transaction
2. Call **1930** (Cybercrime Helpline) within 24 hours for best recovery chances
3. File FIR at the nearest police station
4. Report on **cybercrime.gov.in** (for online fraud)

**Applicable Legal Sections:**
| Type | Section | Punishment |
|------|---------|------------|
| Cheating | 420 IPC | Up to 7 years + fine |
| Breach of trust | 406 IPC | Up to 3 years + fine |
| Forgery | 468 IPC | Up to 7 years + fine |
| Online fraud | 66D IT Act | Up to 3 years + fine |
| Identity theft | 66C IT Act | Up to 3 years + fine |

**Evidence to Collect:**
- Transaction IDs, UTR numbers, bank statements
- Screenshots of chats, emails, SMS
- Phone numbers and UPI IDs of the fraudster
- Website/app screenshots
- Any documents or receipts

**Recovery Options:**
- Request bank reversal through complaint
- File for compensation through Consumer Court
- Civil suit for recovery of money
- Insurance claim if applicable

**Prevention:**
- Never share OTP, CVV, PIN with anyone
- Verify before transferring money to unknown persons
- If a deal seems too good to be true, it probably is

How were you scammed? I can provide specific guidance."""
    },
]


def chat_response(message: str, context: str = "general", user_role: str = "victim", language: str = "en") -> str:
    """AI chatbot response — matches user question to relevant knowledge."""
    if MOCK_MODE:
        return _smart_mock_response(message, context, user_role, language)

    context_prompts = {
        "victim_guidance": "You are a compassionate victim assistance counselor for Indian law enforcement. Provide detailed, actionable guidance.",
        "investigation": "You are a senior investigation officer providing investigation guidance with legal references.",
        "cybercrime": "You are a cybercrime specialist providing awareness, prevention, and reporting guidance.",
        "general": "You are CrimeGPT, an AI assistant for crime documentation and legal intelligence in India. Answer the user's question directly and thoroughly.",
        "laws": "You are an Indian legal expert specializing in BNS, BNSS, BSA, IPC, CrPC and IT Act. Provide accurate legal information.",
        "landmark": "You are an Indian legal researcher. Provide information about landmark Supreme Court and High Court judgments.",
    }

    lang_instructions = {
        "hi": " Respond in Hindi (Devanagari script).",
        "ta": " Respond in Tamil.",
        "te": " Respond in Telugu.",
        "bn": " Respond in Bengali.",
        "mr": " Respond in Marathi.",
        "gu": " Respond in Gujarati.",
        "kn": " Respond in Kannada.",
        "ml": " Respond in Malayalam.",
        "pa": " Respond in Punjabi.",
    }

    system_prompt = context_prompts.get(context, context_prompts["general"])
    system_prompt += lang_instructions.get(language, "")
    return _ai_call(system_prompt, message)


# ─── Slash Command Responses ──────────────────────────────────────────────────

_SLASH_COMMANDS = {
    "/help": """📖 **CrimeGPT Slash Commands:**

| Command | Description |
|---------|-------------|
| `/fir` | Step-by-step FIR filing guide |
| `/rights` | Your rights as a victim |
| `/cyber` | Cybercrime reporting & prevention |
| `/bail` | Bail types and process |
| `/laws` | Key IPC/BNS sections quick reference |
| `/sections <crime>` | Legal sections for a specific crime |
| `/landmark <crime>` | Landmark court judgments |
| `/drugs` | NDPS Act & drug offense info |
| `/murder` | Murder law & investigation |
| `/dv` | Domestic violence laws & helplines |
| `/pocso` | Child protection laws (POCSO) |
| `/rti` | Right to Information Act guide |
| `/wc` | White-collar crime & corruption |
| `/missing` | Missing person reporting |
| `/evidence` | Evidence collection guide |
| `/translate <lang>` | Switch response language (hi/ta/te/bn/mr/gu) |
| `/helplines` | All important helpline numbers |
| `/contacts` | Complaint portals & contacts |

💡 **Tip:** Type any question in plain English — you don't need commands!""",

    "/fir": """📋 **How to File an FIR (First Information Report):**

**Step-by-Step Process:**
1. Visit the nearest police station (jurisdiction where the crime occurred)
2. Narrate the incident to the duty officer verbally or in writing
3. The officer will record your statement and register the FIR
4. You will receive a copy of the FIR with a unique FIR number
5. Keep this number safe — you'll need it to track your case

**Important Rights:**
- Police **cannot refuse** to register an FIR (Section 154 CrPC / Section 173 BNSS)
- If refused, you can send a written complaint to the SP/SSP or file with the Magistrate under Section 156(3)
- You can also file a **Zero FIR** at ANY police station, regardless of jurisdiction
- You are entitled to a **free copy** of the FIR

**Online FIR Options:**
- Many states allow e-FIR via their police websites
- National Cybercrime Portal: **cybercrime.gov.in** (for cyber offences)

**Documents to Carry:**
- Government ID proof (Aadhaar, Voter ID, Passport)
- Any evidence you have (screenshots, documents, photos)
- Details of witnesses, if any

📌 *Landmark Case:* Lalita Kumari v. Govt. of U.P. (2014) — FIR registration is mandatory for cognizable offences.""",

    "/rights": """⚖️ **Your Rights as a Victim / Complainant:**

**Fundamental Rights:**
1. **Right to file FIR** — Police cannot refuse (Section 154 CrPC / 173 BNSS)
2. **Right to free FIR copy** — Must be provided immediately
3. **Right to Zero FIR** — File at any police station
4. **Right to legal aid** — Free lawyer if you can't afford one (Article 39A)
5. **Right to know case progress** — Can ask the IO for updates

**During Investigation:**
- Right to be treated with dignity and respect
- Right to have a female officer present (for women/children)
- Right to medical examination (in assault/rape cases)
- Right to protection from the accused
- Right to victim compensation under government schemes

**In Court:**
- Right to engage a private lawyer
- Right to be informed about bail hearings
- Right to file an appeal if unsatisfied with verdict
- Right to victim impact statement

**Special Rights for Women:**
- Female officer must record statement of rape victim
- Examination of victim in sexual offence cases only by female doctor
- Statement can be recorded at victim's residence

**Helplines:** 112 | Women: 181 | Legal Aid: 15100 | Child: 1098""",

    "/cyber": """🛡️ **Cybercrime — Guidance & Reporting:**

**If You Are a Victim:**
1. **Don't panic** — Document everything immediately
2. Take **screenshots** of messages, emails, transactions
3. Note phone numbers, email IDs, UPI IDs of the fraudster
4. **Do NOT delete** any evidence (chats, call logs, emails)
5. Report within **24 hours** for best chance of fund recovery

**How to Report:**
- 🌐 **National Cybercrime Portal**: cybercrime.gov.in
- 📞 **Helpline**: 1930 (available 24/7)
- 🏛️ Local **Cyber Crime Cell** at your nearest police station
- 🏦 **RBI** for banking fraud: cms.rbi.org.in
- Inform your **bank immediately** to freeze the transaction

**Common Cyber Threats:**
| Threat | Description |
|--------|-------------|
| Phishing | Fake emails/SMS to steal credentials |
| UPI Fraud | Fake payment requests or QR codes |
| Identity Theft | Misusing your personal details |
| Ransomware | Locking your data and demanding ransom |
| Sextortion | Blackmailing with intimate content |
| SIM Swap | Taking over your mobile number |
| Job Scam | Fake job offers to extract money |

**Applicable Laws:** IT Act Sections 66, 66C, 66D, 66E, 67, 67A, 67B

📞 Cybercrime Helpline: **1930**""",

    "/bail": """🏛️ **Bail — Types & Procedures:**

**Types of Bail:**
1. **Regular Bail** (Section 437/439 CrPC / 480/483 BNSS) — After arrest
2. **Anticipatory Bail** (Section 438 CrPC / 484 BNSS) — Before arrest
3. **Interim Bail** — Temporary, pending final hearing
4. **Default Bail** (Section 167(2) CrPC / 187(2) BNSS) — If chargesheet not filed in time

**How to Apply:**
- Through a **lawyer** before the appropriate court
- Sessions Court or High Court for anticipatory bail
- Magistrate Court for regular bail (bailable offences)

**Bailable vs Non-Bailable:**
| Bailable | Non-Bailable |
|----------|-------------|
| Bail is a **right** | Bail at **court's discretion** |
| Police can grant at station | Only court can grant |
| e.g., Theft, Cheating | e.g., Murder, Kidnapping |

**Conditions Usually Imposed:**
- Surrender passport
- Regular attendance at police station
- Not tampering with evidence/witnesses
- Providing surety/bond

📌 *Note:* Under BNSS 2023, undertrial prisoners who have served half the maximum sentence may apply for bail.""",

    "/laws": """📚 **Key Legal Sections — Quick Reference:**

**BNS 2023 (Replaces IPC 1860):**
| Section | Offence | Punishment |
|---------|---------|------------|
| 101 | Murder | Life / Death |
| 109 | Attempt to murder | Up to 10 yrs |
| 64 | Rape | 10 yrs to Life |
| 318 | Cheating / Fraud | Up to 7 yrs |
| 316 | Criminal breach of trust | Up to 3 yrs |
| 74 | Assault on woman | 1-5 yrs |
| 85 | Dowry harassment | Up to 3 yrs |
| 303 | Theft | Up to 3 yrs |
| 309 | Robbery | Up to 10 yrs |
| 115 | Voluntarily causing hurt | Up to 1 yr |
| 351 | Criminal intimidation | Up to 2 yrs |

**IT Act 2000 (Cybercrime):**
| Section | Offence | Punishment |
|---------|---------|------------|
| 66 | Computer offences | Up to 3 yrs |
| 66C | Identity theft | Up to 3 yrs |
| 66D | Cheating by personation | Up to 3 yrs |
| 67 | Publishing obscene content | Up to 5 yrs |

**NDPS Act (Drug Offences):**
| Quantity | Punishment |
|----------|------------|
| Small quantity | Up to 1 yr |
| Intermediate | Up to 10 yrs |
| Commercial quantity | 10-20 yrs (mandatory min) |

📝 *Note:* IPC 1860 is replaced by BNS 2023 (effective 1 July 2024)""",

    "/drugs": """💊 **NDPS Act — Drug Offences & Legal Framework:**

**NDPS Act 1985 (Narcotic Drugs & Psychotropic Substances):**

**Key Offences:**
| Offence | Section | Punishment |
|---------|---------|------------|
| Cultivation of opium/cannabis | Sec 18/20 | Up to 20 yrs |
| Manufacture/sale | Sec 8, 21, 22 | 10-20 yrs |
| Consumption (small qty) | Sec 27 | Up to 1 yr / fine |
| Financing drug trade | Sec 27A | 10-20 yrs |
| Allowing premises for drug use | Sec 29 | Up to 10 yrs |
| Possession (commercial qty) | Varies | 10-20 yrs (mandatory) |

**Quantity Thresholds (Cannabis example):**
- Small quantity: Below 1 kg
- Commercial quantity: 20 kg and above
- Intermediate: Between small and commercial

**Reversed Burden of Proof:**
Under NDPS Act, once possession is proved, the accused must prove innocence.

**How to Report:**
- Call **1800-11-0031** (NCB Helpline)
- Report to local police station
- Contact Narcotics Control Bureau (NCB): narcoticsindia.nic.in

**Investigation Authority:**
- NCB (Narcotics Control Bureau)
- State ATS (Anti-Terrorism Squad)
- Local police (with powers under NDPS Act)

📌 *Landmark:* Union of India v. Bal Mukund Shah (2008) — reversed burden of proof""",

    "/murder": """🔴 **Murder — Law, Investigation & Punishment:**

**Legal Sections:**
- **Section 302 IPC / Section 101 BNS** — Murder — Life imprisonment or Death
- **Section 307 IPC / Section 109 BNS** — Attempt to murder — Up to 10 years
- **Section 304 IPC / Section 105 BNS** — Culpable homicide — Up to life/10 yrs

**Distinction:**
| Murder (302 IPC) | Culpable Homicide (304 IPC) |
|------------------|----------------------------|
| Intention to kill | Knowledge that death may occur |
| Premeditated | May be impulsive |
| Higher punishment | Lesser punishment |

**Investigation Steps:**
1. Secure and document the crime scene
2. Call FSL (Forensic Science Lab) immediately
3. Conduct post-mortem examination
4. Collect CCTV footage from nearby areas
5. Record witness statements (161 CrPC)
6. Obtain CDR (Call Detail Records)
7. Arrest suspect under Section 41 CrPC

**Death Penalty — "Rarest of Rare" Doctrine:**
Courts award death penalty only in the most heinous cases:
- Mass murders
- Murder of children after rape
- Contract killings

📌 *Landmark:* Bachan Singh v. State of Punjab (1980) — "Rarest of Rare" doctrine established""",

    "/dv": """🏠 **Domestic Violence — Laws & Protection:**

**Key Laws:**
- **Protection of Women from Domestic Violence Act, 2005 (PWDVA)**
- **Section 498A IPC / Section 85 BNS** — Dowry harassment
- **Section 304B IPC / Section 80 BNS** — Dowry death
- **Dowry Prohibition Act, 1961**

**Types of Domestic Violence (under PWDVA):**
1. Physical abuse
2. Sexual abuse
3. Emotional/verbal abuse
4. Economic abuse
5. Dowry-related harassment

**Reliefs Available Under PWDVA:**
- **Protection Order** — Prevents abuser from contacting victim
- **Residence Order** — Right to stay in shared household
- **Monetary Relief** — Maintenance, compensation
- **Custody Order** — Temporary custody of children

**How to Get Help:**
1. Call **112** (Emergency) or **181** (Women Helpline)
2. Visit nearest police station and file FIR
3. Contact **Protection Officer** in your district
4. Go to **One Stop Centre (Sakhi)** — shelter + legal + medical
5. Approach Magistrate directly for emergency protection order

**Helplines:**
- 📞 **181** — Women Helpline (24/7)
- 📞 **112** — Emergency
- 📞 **1091** — Women Police Helpline
- 📞 **NCW**: 7827170170

📌 *Note:* You can seek protection order within 24 hours in urgent cases.""",

    "/pocso": """👶 **POCSO Act — Child Protection Laws:**

**Protection of Children from Sexual Offences (POCSO) Act, 2012:**

**Definition:** Any person below 18 years of age is a "child" under POCSO.

**Key Offences & Punishments:**
| Offence | Section | Punishment |
|---------|---------|------------|
| Penetrative sexual assault | Sec 3 | Min 7 yrs to Life |
| Aggravated penetrative sexual assault | Sec 5 | Min 20 yrs to Life/Death |
| Sexual assault (non-penetrative) | Sec 7 | Min 3 yrs |
| Sexual harassment | Sec 11 | Up to 3 yrs |
| Using child for pornography | Sec 13/14 | Up to 5 yrs |

**Special Provisions:**
- **Mandatory reporting** — Even suspicion must be reported to police (failure = 6 months jail)
- **Child-friendly procedures** — Statement recorded in child-friendly environment
- **No disclosure of identity** — Child's identity protected in media
- **Special courts** — Cases tried in Special Courts (POCSO Courts)
- **Presumption of guilt** — Accused must prove innocence in some cases

**How to Report:**
- Call **1098** (Child Helpline)
- Nearest police station (Zero FIR)
- Online: cybercrime.gov.in (for online POCSO)
- **Childline**: childlineindia.org

**Timeline:** POCSO cases must be completed within 1 year of cognizance.""",

    "/rti": """📜 **Right to Information (RTI) Act, 2005:**

**What is RTI?**
RTI Act gives every citizen the right to request information from any public authority. Police, courts, municipalities — all are covered.

**How to File an RTI:**
1. Write an application to the **Public Information Officer (PIO)** of the concerned department
2. Attach ₹10 court fee stamp (or demand draft)
3. Specify exactly what information you need
4. Submit by post, in person, or online at **rtionline.gov.in**

**Key Timelines:**
- PIO must respond within **30 days** (48 hours for life/liberty matters)
- If PIO fails, appeal to **First Appellate Authority** within 30 days
- Second appeal to **Central Information Commission (CIC)** within 90 days

**What You Can Ask For:**
- FIR status and investigation updates
- Police action taken on your complaint
- Government scheme benefits and eligibility
- File noting, inspection reports, decisions

**What Cannot Be Disclosed:**
- National security / RAW / IB information
- Personal information with no public interest
- Cabinet papers (until decision made)
- Ongoing investigations (partially)

**RTI Portal:** rtionline.gov.in
**CIC Website:** cic.gov.in
**Helpline:** 1800-11-4422 (toll-free)""",

    "/wc": """💼 **White-Collar Crime & Corruption:**

**Common Types:**
| Crime | Section | Authority |
|-------|---------|-----------|
| Bribery | Sec 7 PC Act | CBI / ACB |
| Embezzlement | Sec 316 BNS | Police / EOW |
| Money laundering | PMLA 2002 | ED (Enforcement Directorate) |
| Tax evasion | Income Tax Act | IT Dept / CBI |
| Corporate fraud | Companies Act | SFIO |
| Insider trading | SEBI Act | SEBI |
| Benami transactions | Benami Act | IT Dept |

**Prevention of Corruption Act, 1988:**
- Section 7: Public servant taking bribe — up to 7 years
- Section 13: Criminal misconduct — up to 7 years
- Section 17A: Prior sanction required for prosecution of senior officials

**How to Report:**
- **CBI (Central Bureau of Investigation)**: cbi.gov.in
- **CVC (Central Vigilance Commission)**: cvc.gov.in (1800-11-0180)
- **ED (Enforcement Directorate)**: enforcementdirectorate.gov.in
- **SFIO**: sfio.gov.in (corporate fraud)
- **Lokpal**: lokpal.gov.in
- **State ACB (Anti-Corruption Bureau)**: check state police website

📌 *Note:* Bribe-giver can also be prosecuted under Prevention of Corruption Act.""",

    "/missing": """🔎 **Missing Person / Kidnapping — Immediate Steps:**

**What To Do Immediately:**
1. File a **missing person report** at the nearest police station
2. Police **cannot refuse** or ask you to wait 24 hours — this is a myth
3. Provide a recent photograph and physical description
4. Share last known location, clothing, and contacts

**FIR Sections:**
- **Section 363 IPC / Section 137 BNS** — Kidnapping (up to 7 yrs)
- **Section 364A IPC / Section 140 BNS** — Kidnapping for ransom (Death / Life)
- **Section 365 IPC / Section 139 BNS** — Abduction (up to 7 yrs)

**For Missing Children:**
- **Khoya Paya Portal**: khoyapaya.gov.in
- **Child Helpline**: 1098
- AMBER Alert issued through police network

**Police Actions:**
- Alert to nearby stations and state CCTNS
- CCTV footage collection from last seen area
- Mobile phone IMEI/SIM tracking
- Social media monitoring

**Helplines:**
- 📞 **112** — Emergency
- 📞 **1098** — Child Helpline
- 🌐 trackthemissingchild.gov.in

⚠️ Time is critical — report immediately!""",

    "/evidence": """🔍 **Evidence Collection & Preservation Guide:**

**Types of Evidence:**
1. **Physical** — Weapons, clothing, biological samples, fingerprints
2. **Documentary** — Letters, receipts, contracts, bank statements
3. **Digital** — Screenshots, emails, call logs, CCTV footage, metadata
4. **Testimonial** — Witness statements, victim statements

**Collection Best Practices:**
- Photograph everything before touching
- Use gloves when handling physical evidence
- Maintain a **chain of custody** log for every item
- Seal evidence in tamper-proof bags with labels
- Record date, time, location, and collector's name

**Digital Evidence (BSA 2023 — Replaces Section 65B IEA):**
- Take screenshots with **timestamps** visible
- Save original files — don't edit or crop
- Record **hash values** (MD5/SHA256) for integrity
- Preserve metadata (file creation dates, GPS data)
- Get **Section 63 BSA certificate** for electronic evidence admissibility

**CCTV Footage:**
- Request within **72 hours** (before overwritten)
- Get footage in original format (not re-recorded)

**DNA Evidence:**
- Handled only by forensic teams
- Chain of custody strictly maintained
- DNA profiling through FSL (Forensic Science Lab)

📌 *Landmark:* Anvar P.V. v. P.K. Basheer (2014) — Section 65B certificate mandatory""",

    "/helplines": """📞 **All Important Helpline Numbers:**

**Emergency Services:**
| Service | Number |
|---------|--------|
| Emergency (All) | **112** |
| Police | **100** |
| Fire | **101** |
| Ambulance | **108** |

**Specialized Helplines:**
| Service | Number |
|---------|--------|
| Women Helpline | **181** |
| Cybercrime | **1930** |
| Child Helpline | **1098** |
| Women Police | **1091** |
| Senior Citizen | **14567** |
| Legal Aid (NALSA) | **15100** |
| Anti-Corruption (CVC) | **1800-11-0180** |
| NCB (Drug Trafficking) | **1800-11-0031** |
| RBI Banking Fraud | **14440** |
| Railway Helpline | **139** |
| Road Accident | **1073** |

**Online Portals:**
- 🌐 **Cybercrime**: cybercrime.gov.in
- 📋 **RTI**: rtionline.gov.in
- 👶 **Missing Child**: khoyapaya.gov.in
- ⚖️ **Legal Aid**: nalsa.gov.in
- 👩 **NCW**: ncw.nic.in
- 🏛️ **Lokpal**: lokpal.gov.in""",

    "/contacts": """📬 **Complaint Portals & Contacts:**

**National Portals:**
| Portal | URL | Purpose |
|--------|-----|---------|
| Cybercrime | cybercrime.gov.in | Cyber fraud, harassment |
| CPGRAMS | pgportal.gov.in | Govt grievances |
| RTI Online | rtionline.gov.in | Information requests |
| Lokpal | lokpal.gov.in | Corruption complaints |
| NCW | ncw.nic.in | Women's issues |
| NHRC | nhrc.nic.in | Human rights violations |
| CBI | cbi.gov.in | Serious crimes |
| CVC | cvc.gov.in | Corruption (public servants) |
| SEBI | scores.sebi.gov.in | Investment fraud |

**Banking & Finance:**
- **RBI Ombudsman**: cms.rbi.org.in
- **IRDAI (Insurance)**: bimabharosa.irdai.gov.in
- **CEIR (Mobile blocking)**: ceir.gov.in

**Consumer Complaints:**
- **NCDRC**: consumerhelpline.gov.in (1800-11-4000)

📌 *Tip:* Always note your complaint/ticket number for follow-up!""",
}

# Hindi translations for slash command responses
_SLASH_COMMANDS_HI = {
    "/fir": """📋 **एफआईआर (प्राथमिकी) कैसे दर्ज करें:**

**चरण-दर-चरण प्रक्रिया:**
1. निकटतम पुलिस स्टेशन जाएं (जहाँ अपराध हुआ है)
2. ड्यूटी अधिकारी को मौखिक या लिखित रूप से घटना बताएं
3. अधिकारी आपका बयान दर्ज करके एफआईआर पंजीकृत करेगा
4. आपको एक विशिष्ट एफआईआर नंबर के साथ एक प्रति मिलेगी
5. इस नंबर को सुरक्षित रखें — आपको इसे अपना मामला ट्रैक करने के लिए चाहिए

**महत्वपूर्ण अधिकार:**
- पुलिस एफआईआर दर्ज करने से **मना नहीं कर सकती** (धारा 154 CrPC / 173 BNSS)
- अगर मना करे, तो SP/SSP को लिखित शिकायत दें या मजिस्ट्रेट के पास जाएं
- आप किसी भी पुलिस स्टेशन में **शून्य एफआईआर** दर्ज करा सकते हैं
- आपको **मुफ्त एफआईआर प्रति** मिलने का अधिकार है

**ऑनलाइन एफआईआर:**
- कई राज्यों में ई-एफआईआर की सुविधा है
- साइबर अपराध के लिए: **cybercrime.gov.in**

📞 **हेल्पलाइन:** आपातकाल: 112 | महिला: 181 | साइबर: 1930""",

    "/rights": """⚖️ **पीड़ित के अधिकार:**

**मूल अधिकार:**
1. **एफआईआर दर्ज करने का अधिकार** — पुलिस मना नहीं कर सकती
2. **मुफ्त एफआईआर प्रति** — तुरंत प्रदान की जानी चाहिए
3. **शून्य एफआईआर** — किसी भी पुलिस स्टेशन में
4. **मुफ्त कानूनी सहायता** — अगर आप वकील का खर्च नहीं उठा सकते (अनुच्छेद 39A)
5. **केस की प्रगति जानने का अधिकार** — IO से अपडेट मांग सकते हैं

**जांच के दौरान:**
- सम्मान के साथ व्यवहार का अधिकार
- महिला/बच्चे के लिए महिला अधिकारी की उपस्थिति का अधिकार
- चिकित्सा जांच का अधिकार (हमले के मामलों में)
- आरोपी से सुरक्षा का अधिकार

📞 **हेल्पलाइन:** 112 | महिला: 181 | कानूनी सहायता: 15100""",

    "/cyber": """🛡️ **साइबर अपराध — मार्गदर्शन और रिपोर्टिंग:**

**अगर आप पीड़ित हैं:**
1. **घबराएं नहीं** — तुरंत सब कुछ दस्तावेज करें
2. संदेश, ईमेल, लेनदेन के **स्क्रीनशॉट** लें
3. धोखेबाज के फोन नंबर, UPI आईडी नोट करें
4. कोई भी **सबूत न हटाएं** (चैट, कॉल लॉग, ईमेल)
5. धनराशि वसूली के लिए **24 घंटे के भीतर** रिपोर्ट करें

**रिपोर्ट कहाँ करें:**
- 🌐 **राष्ट्रीय साइबर अपराध पोर्टल**: cybercrime.gov.in
- 📞 **हेल्पलाइन**: 1930 (24/7)
- 🏛️ निकटतम **साइबर क्राइम सेल**
- 🏦 **बैंक को तुरंत सूचित करें** लेनदेन फ्रीज करने के लिए

📞 साइबर अपराध हेल्पलाइन: **1930**""",
}

def _handle_slash_command(command: str, language: str = "en") -> str:
    """Handle slash commands and return appropriate response."""
    cmd_lower = command.lower().strip()

    # Exact command match
    if cmd_lower in _SLASH_COMMANDS:
        if language == "hi" and cmd_lower in _SLASH_COMMANDS_HI:
            return _SLASH_COMMANDS_HI[cmd_lower]
        return _SLASH_COMMANDS[cmd_lower]

    # Dynamic /sections <crime> command
    if cmd_lower.startswith("/sections "):
        crime = cmd_lower[10:].strip()
        return _get_sections_for_crime(crime)

    # Dynamic /landmark <crime> command
    if cmd_lower.startswith("/landmark "):
        crime = cmd_lower[10:].strip()
        judgments = get_landmark_judgments(crime)
        if not judgments:
            return f"No landmark judgments found for '{crime}'. Try: cybercrime, fraud, murder, theft, assault, domestic_violence, sexual_harassment, kidnapping"
        lines = [f"🏛️ **Landmark Judgments for '{crime.title()}':**\n"]
        for j in judgments:
            lines.append(f"**📋 {j['case']}**")
            lines.append(f"*Court:* {j['court']}")
            lines.append(f"*Citation:* {j['citation']}")
            lines.append(f"*Significance:* {j['significance']}")
            if j.get('url'):
                lines.append(f"*Reference:* {j['url']}")
            lines.append("")
        return "\n".join(lines)

    # /translate command
    if cmd_lower.startswith("/translate"):
        lang = cmd_lower.replace("/translate", "").strip()
        lang_names = {"hi": "Hindi 🇮🇳", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam"}
        if lang in lang_names:
            return f"✅ Language switched to **{lang_names[lang]}**. I'll now respond in {lang_names[lang]}.\n\nTry asking a question now! For example:\n- 'एफआईआर कैसे दर्ज करें?' (for FIR in Hindi)\n- Or use /fir, /rights, /cyber commands"
        return f"❌ Unknown language code: '{lang}'\n\nSupported: hi (Hindi), ta (Tamil), te (Telugu), bn (Bengali), mr (Marathi), gu (Gujarati), kn (Kannada), ml (Malayalam)\n\nExample: `/translate hi`"

    return None


def _get_sections_for_crime(crime: str) -> str:
    """Return legal sections for a specific crime type."""
    sections_db = {
        "murder": [("302 IPC / 101 BNS", "Murder", "Life / Death"), ("307 IPC / 109 BNS", "Attempt to murder", "Up to 10 yrs"), ("304 IPC / 105 BNS", "Culpable homicide", "Up to life/10 yrs")],
        "theft": [("378/379 IPC / 303 BNS", "Theft", "Up to 3 yrs"), ("392 IPC / 309 BNS", "Robbery", "Up to 10 yrs"), ("395 IPC / 310 BNS", "Dacoity", "Up to life"), ("457 IPC / 329 BNS", "House-breaking at night", "Up to 5 yrs")],
        "fraud": [("420 IPC / 318 BNS", "Cheating / Fraud", "Up to 7 yrs"), ("406 IPC / 316 BNS", "Criminal breach of trust", "Up to 3 yrs"), ("467 IPC / 336 BNS", "Forgery of valuable security", "Up to 10 yrs"), ("468 IPC / 337 BNS", "Forgery for cheating", "Up to 7 yrs")],
        "cybercrime": [("66 IT Act", "Computer related offences", "Up to 3 yrs"), ("66C IT Act", "Identity theft", "Up to 3 yrs"), ("66D IT Act", "Cheating by personation", "Up to 3 yrs"), ("66E IT Act", "Violation of privacy", "Up to 3 yrs"), ("67 IT Act", "Publishing obscene material", "Up to 5 yrs")],
        "assault": [("323 IPC / 115 BNS", "Voluntarily causing hurt", "Up to 1 yr"), ("325 IPC / 117 BNS", "Grievous hurt", "Up to 7 yrs"), ("307 IPC / 109 BNS", "Attempt to murder", "Up to 10 yrs")],
        "rape": [("376 IPC / 64 BNS", "Rape", "Min 10 yrs to Life"), ("376A IPC / 66 BNS", "Rape causing death", "20 yrs to Life/Death"), ("376AB BNS", "Rape of minor under 12", "Min 20 yrs / Life")],
        "kidnapping": [("363 IPC / 137 BNS", "Kidnapping", "Up to 7 yrs"), ("364 IPC / 138 BNS", "Kidnapping to murder", "Life"), ("364A IPC / 140 BNS", "Kidnapping for ransom", "Death / Life"), ("365 IPC / 139 BNS", "Abduction", "Up to 7 yrs")],
        "domestic violence": [("498A IPC / 85 BNS", "Dowry harassment", "Up to 3 yrs"), ("304B IPC / 80 BNS", "Dowry death", "7 yrs to Life"), ("3 PWDVA 2005", "Domestic violence", "Protection order + compensation")],
        "drugs": [("8/21/22 NDPS", "Manufacture/sale of drugs", "10-20 yrs"), ("27 NDPS", "Consumption (small qty)", "Up to 1 yr"), ("27A NDPS", "Financing drug trade", "10-20 yrs")],
        "corruption": [("7 PC Act", "Bribery (public servant)", "3-7 yrs"), ("13 PC Act", "Criminal misconduct", "Up to 7 yrs"), ("8 PC Act", "Bribe-giver", "3-7 yrs")],
    }

    crime_lower = crime.lower()
    # Try to match
    for key, sections in sections_db.items():
        if crime_lower in key or key in crime_lower:
            lines = [f"⚖️ **Legal Sections for '{crime.title()}':**\n"]
            lines.append("| Section | Offence | Punishment |")
            lines.append("|---------|---------|------------|")
            for sec, offence, punishment in sections:
                lines.append(f"| {sec} | {offence} | {punishment} |")
            lines.append(f"\n💡 *Use `/landmark {crime}` to see relevant court judgments.*")
            return "\n".join(lines)

    return f"No sections found for '{crime}'. Try: murder, theft, fraud, cybercrime, assault, rape, kidnapping, 'domestic violence', drugs, corruption"


# ─── Full Multilingual Knowledge Base ──────────────────────────────────────────
# Each topic has: keywords (across ALL language scripts) and responses per language.

_MULTILINGUAL_TOPICS = [
    {
        "id": "fir",
        "keywords": [
            # English
            "fir", "file fir", "lodge fir", "register fir", "file complaint", "lodge complaint", "police complaint", "how to complain",
            # Hindi
            "एफआईआर", "प्राथमिकी", "शिकायत", "शिकायत दर्ज", "रिपोर्ट", "पुलिस शिकायत", "थाना",
            # Gujarati
            "ફરિયાદ", "પોલીસ ફરિયાદ", "એફઆઈઆર", "ફરિયાદ નોંધાવવી", "પોલીસ સ્ટેશન", "ફરિયાદ કરવી", "રિપોર્ટ",
            # Tamil
            "புகார்", "காவல்", "எஃப்ஐஆர்",
            # Telugu
            "ఫిర్యాదు", "పోలీసు", "ఎఫ్ఐఆర్",
            # Bengali
            "অভিযোগ", "থানা", "এফআইআর",
            # Marathi
            "तक्रार", "पोलीस तक्रार", "एफआयआर",
        ],
        "responses": {
            "en": """📋 **How to File an FIR (First Information Report):**

**Step-by-Step Process:**
1. Visit the nearest police station (jurisdiction where the crime occurred)
2. Narrate the incident to the duty officer verbally or in writing
3. The officer will record your statement and register the FIR
4. You will receive a copy of the FIR with a unique FIR number
5. Keep this number safe — you'll need it to track your case

**Important Rights:**
- Police **cannot refuse** to register an FIR (Section 154 CrPC)
- If refused, send a written complaint to the SP/SSP
- You can file a **Zero FIR** at ANY police station
- You are entitled to a **free copy** of the FIR

**Online FIR:** cybercrime.gov.in (for cyber offences)

**Documents to Carry:**
- Aadhaar / Voter ID / Passport
- Any evidence (screenshots, documents, photos)
- Details of witnesses

📞 Emergency: **112** | Women: **181** | Cybercrime: **1930**""",

            "hi": """📋 **एफआईआर (प्राथमिकी) कैसे दर्ज करें:**

**चरण-दर-चरण प्रक्रिया:**
1. निकटतम पुलिस स्टेशन जाएं (जहाँ अपराध हुआ है)
2. ड्यूटी अधिकारी को मौखिक या लिखित रूप से घटना बताएं
3. अधिकारी आपका बयान दर्ज करके एफआईआर पंजीकृत करेगा
4. आपको एक विशिष्ट एफआईआर नंबर के साथ एक प्रति मिलेगी
5. इस नंबर को सुरक्षित रखें — मामला ट्रैक करने के लिए चाहिए

**महत्वपूर्ण अधिकार:**
- पुलिस एफआईआर दर्ज करने से **मना नहीं कर सकती** (धारा 154 CrPC)
- अगर मना करे तो SP/SSP को लिखित शिकायत दें
- आप किसी भी पुलिस स्टेशन में **शून्य एफआईआर** दर्ज करा सकते हैं
- आपको **मुफ्त एफआईआर प्रति** मिलने का अधिकार है

**ऑनलाइन एफआईआर:** cybercrime.gov.in (साइबर अपराध के लिए)

**साथ में ले जाएं:**
- आधार / वोटर आईडी / पासपोर्ट
- सबूत (स्क्रीनशॉट, दस्तावेज, फोटो)

📞 आपातकाल: **112** | महिला: **181** | साइबर: **1930**""",

            "gu": """📋 **FIR (એફઆઈઆર) કેવી રીતે નોંધાવવી:**

**સ્ટેપ-બાય-સ્ટેપ પ્રક્રિયા:**
1. નજીકના પોલીસ સ્ટેશન પર જાઓ (જ્યાં ગુનો થયો હોય)
2. ડ્યુટી ઓફિસરને ઘટના મૌખિક અથવા લેખિતમાં જણાવો
3. ઓફિસર તમારું બયાન લખીને FIR નોંધશે
4. તમને FIR નંબર સાથે FIR ની નકલ મળશે
5. આ નંબર સાચવી રાખો — કેસ ટ્રેક કરવા માટે જરૂરી છે

**તમારા અધિકારો:**
- પોલીસ FIR નોંધવાની **ના પાડી શકે નહીં** (કલમ 154 CrPC)
- જો ના પાડે તો SP/SSP ને લેખિત ફરિયાદ આપો
- તમે કોઈપણ પોલીસ સ્ટેશનમાં **ઝીરો FIR** નોંધાવી શકો છો
- તમને **મફત FIR ની નકલ** મેળવવાનો અધિકાર છે

**ઓનલાઈન FIR:** cybercrime.gov.in (સાયબર ગુનાઓ માટે)

**સાથે લઈ જાઓ:**
- આધાર / વોટર ID / પાસપોર્ટ
- પુરાવા (સ્ક્રીનશૉટ, દસ્તાવેજો, ફોટા)

📞 ઈમરજન્સી: **112** | મહિલા: **181** | સાયબર: **1930**""",

            "ta": """📋 **FIR (முதல் தகவல் அறிக்கை) எவ்வாறு பதிவு செய்வது:**

1. அருகிலுள்ள காவல் நிலையத்திற்கு செல்லுங்கள்
2. கடமை அதிகாரியிடம் சம்பவத்தை தெரிவிக்கவும்
3. அதிகாரி FIR பதிவு செய்வார்
4. FIR எண்ணுடன் நகல் பெறுங்கள்
5. இந்த எண்ணை பாதுகாப்பாக வைக்கவும்

**உங்கள் உரிமைகள்:**
- காவல்துறை FIR பதிவு செய்ய **மறுக்க முடியாது**
- எந்த காவல் நிலையத்திலும் **ஜீரோ FIR** அளிக்கலாம்
- **இலவச FIR நகல்** பெறும் உரிமை உள்ளது

📞 அவசரம்: **112** | பெண்கள்: **181** | சைபர்: **1930**""",

            "te": """📋 **FIR (ఎఫ్ఐఆర్) ఎలా నమోదు చేయాలి:**

1. సమీపంలోని పోలీసు స్టేషన్‌కు వెళ్ళండి
2. డ్యూటీ ఆఫీసర్‌కు సంఘటన గురించి చెప్పండి
3. ఆఫీసర్ FIR నమోదు చేస్తారు
4. FIR నంబర్‌తో కాపీ పొందండి

**మీ హక్కులు:**
- పోలీసులు FIR నమోదు చేయడానికి **నిరాకరించలేరు**
- ఏ పోలీసు స్టేషన్‌లోనైనా **జీరో FIR** ఇవ్వవచ్చు
- **ఉచిత FIR కాపీ** పొందే హక్కు ఉంది

📞 ఎమర్జెన్సీ: **112** | మహిళలు: **181** | సైబర్: **1930**""",

            "bn": """📋 **FIR (এফআইআর) কিভাবে দায়ের করবেন:**

1. নিকটস্থ থানায় যান
2. ঘটনা জানান ডিউটি অফিসারকে
3. অফিসার FIR নথিভুক্ত করবেন
4. FIR নম্বরসহ কপি নিন

**আপনার অধিকার:**
- পুলিশ FIR নথিভুক্ত করতে **অস্বীকার করতে পারে না**
- যেকোনো থানায় **জিরো FIR** করা যায়
- **বিনামূল্যে FIR কপি** পাওয়ার অধিকার

📞 জরুরি: **112** | মহিলা: **181** | সাইবার: **1930**""",

            "mr": """📋 **FIR (एफआयआर) कसा नोंदवायचा:**

1. जवळच्या पोलीस ठाण्यात जा
2. ड्युटी अधिकाऱ्याला घटना सांगा
3. अधिकारी FIR नोंदवेल
4. FIR क्रमांकासह प्रत मिळवा

**तुमचे अधिकार:**
- पोलीस FIR नोंदवण्यास **नकार देऊ शकत नाही**
- कोणत्याही ठाण्यात **शून्य FIR** नोंदवता येते
- **मोफत FIR प्रत** मिळवण्याचा अधिकार

📞 आणीबाणी: **112** | महिला: **181** | सायबर: **1930**""",
        },
    },
    {
        "id": "rights",
        "keywords": [
            "rights", "my rights", "victim rights", "legal rights", "what rights",
            "अधिकार", "हक", "मेरे अधिकार", "कानूनी अधिकार",
            "અધિકાર", "હક", "મારા અધિકાર", "કાનૂની અધિકાર", "અધિકારો",
            "உரிமைகள்", "உரிமை", "హక్కులు", "অধিকার", "अधिकार", "हक्क",
        ],
        "responses": {
            "en": """⚖️ **Your Rights as a Victim / Complainant:**

**Fundamental Rights:**
1. **Right to file FIR** — Police cannot refuse (Section 154 CrPC)
2. **Right to free FIR copy** — Must be provided immediately
3. **Right to Zero FIR** — File at any police station
4. **Right to legal aid** — Free lawyer if you can't afford one (Article 39A)
5. **Right to know case progress** — You can ask for updates

**During Investigation:**
- Right to be treated with dignity and respect
- Right to have a female officer present (for women/children)
- Right to medical examination (in assault cases)
- Right to protection from the accused
- Right to victim compensation

**Helplines:**
- 📞 Emergency: **112**
- 👩 Women: **181**
- ⚖️ Legal Aid (NALSA): **15100**
- 👶 Child: **1098**""",

            "hi": """⚖️ **पीड़ित के अधिकार:**

**मूल अधिकार:**
1. **एफआईआर दर्ज करने का अधिकार** — पुलिस मना नहीं कर सकती
2. **मुफ्त एफआईआर प्रति** — तुरंत मिलनी चाहिए
3. **शून्य एफआईआर** — किसी भी थाने में
4. **मुफ्त कानूनी सहायता** — वकील का खर्च न उठा सकें तो (अनुच्छेद 39A)
5. **केस की प्रगति जानने का अधिकार**

**जांच के दौरान:**
- सम्मान के साथ व्यवहार का अधिकार
- महिला/बच्चों के लिए महिला अधिकारी
- चिकित्सा जांच का अधिकार
- आरोपी से सुरक्षा का अधिकार
- मुआवज़े का अधिकार

📞 आपातकाल: **112** | महिला: **181** | कानूनी सहायता: **15100**""",

            "gu": """⚖️ **પીડિતના અધિકારો:**

**મૂળભૂત અધિકારો:**
1. **FIR નોંધાવવાનો અધિકાર** — પોલીસ ના પાડી શકે નહીં
2. **મફત FIR ની નકલ** — તરત મળવી જોઈએ
3. **ઝીરો FIR** — કોઈપણ પોલીસ સ્ટેશનમાં
4. **મફત કાનૂની સહાય** — વકીલનો ખર્ચ ન ઉઠાવી શકો તો (અનુચ્છેદ 39A)
5. **કેસની પ્રગતિ જાણવાનો અધિકાર**

**તપાસ દરમિયાન:**
- સન્માન સાથે વ્યવહારનો અધિકાર
- મહિલા/બાળકો માટે મહિલા અધિકારી
- તબીબી તપાસનો અધિકાર
- આરોપીથી સુરક્ષાનો અધિકાર
- વળતરનો અધિકાર

📞 ઈમરજન્સી: **112** | મહિલા: **181** | કાનૂની સહાય: **15100**""",

            "ta": """⚖️ **பாதிக்கப்பட்டவரின் உரிமைகள்:**

1. **FIR பதிவு செய்யும் உரிமை** — காவல்துறை மறுக்க முடியாது
2. **இலவச FIR நகல்** பெறும் உரிமை
3. **ஜீரோ FIR** — எந்த காவல் நிலையத்திலும்
4. **இலவச சட்ட உதவி** — வழக்கறிஞர் நியமனம்
5. **வழக்கின் நிலை அறியும் உரிமை**

📞 அவசரம்: **112** | பெண்கள்: **181** | சட்ட உதவி: **15100**""",

            "te": """⚖️ **బాధితుని హక్కులు:**

1. **FIR నమోదు చేసే హక్కు** — పోలీసులు నిరాకరించలేరు
2. **ఉచిత FIR కాపీ** పొందే హక్కు
3. **జీరో FIR** — ఏ పోలీసు స్టేషన్‌లోనైనా
4. **ఉచిత న్యాయ సహాయం**
5. **కేసు పురోగతి తెలుసుకునే హక్కు**

📞 ఎమర్జెన్సీ: **112** | మహిళలు: **181** | న్యాయ సహాయం: **15100**""",

            "bn": """⚖️ **ভুক্তভোগীর অধিকার:**

1. **FIR দায়ের করার অধিকার** — পুলিশ প্রত্যাখ্যান করতে পারে না
2. **বিনামূল্যে FIR কপি** পাওয়ার অধিকার
3. **জিরো FIR** — যেকোনো থানায়
4. **বিনামূল্যে আইনি সহায়তা**
5. **মামলার অগ্রগতি জানার অধিকার**

📞 জরুরি: **112** | মহিলা: **181** | আইনি সহায়তা: **15100**""",

            "mr": """⚖️ **पीडिताचे अधिकार:**

1. **FIR नोंदवण्याचा अधिकार** — पोलीस नकार देऊ शकत नाही
2. **मोफत FIR प्रत** मिळवण्याचा अधिकार
3. **शून्य FIR** — कोणत्याही ठाण्यात
4. **मोफत कायदेशीर मदत**
5. **प्रकरणाची प्रगती जाणून घेण्याचा अधिकार**

📞 आणीबाणी: **112** | महिला: **181** | कायदेशीर मदत: **15100**""",
        },
    },
    {
        "id": "cyber",
        "keywords": [
            "cyber", "hack", "phishing", "online fraud", "internet", "digital", "ransomware", "malware", "email scam", "otp", "upi fraud", "social media",
            "साइबर", "हैक", "ऑनलाइन ठगी", "ओटीपी", "यूपीआई",
            "સાયબર", "હેક", "ઓનલાઈન છેતરપિંડી", "ઓટીપી", "યુપીઆઈ", "ઈન્ટરનેટ", "ઓનલાઈન ફ્રોડ", "ફિશિંગ", "હેકિંગ",
            "சைபர்", "ஹேக்", "ஆன்லைன் மோசடி",
            "సైబర్", "హ్యాక్", "ఆన్‌లైన్ మోసం",
            "সাইবার", "হ্যাক", "অনলাইন জালিয়াতি",
            "सायबर", "हॅक", "ऑनलाईन फसवणूक",
        ],
        "responses": {
            "en": """🛡️ **Cybercrime — Guidance & Reporting:**

**If You Are a Victim:**
1. **Don't panic** — Document everything immediately
2. Take **screenshots** of messages, emails, transactions
3. Note phone numbers, email IDs, UPI IDs of the fraudster
4. **Do NOT delete** any evidence
5. Report within **24 hours** for best chance of fund recovery

**How to Report:**
- 🌐 **National Cybercrime Portal**: cybercrime.gov.in
- 📞 **Helpline**: 1930 (available 24/7)
- 🏛️ Local **Cyber Crime Cell**
- 🏦 **Inform your bank immediately** to freeze the transaction

**Common Threats:**
- Phishing — Fake emails/SMS to steal credentials
- UPI Fraud — Fake payment requests or QR codes
- Identity Theft — Misusing your personal details
- Sextortion — Blackmailing with intimate content

**Prevention:**
- Never share OTP, PIN, or CVV with anyone
- Enable **2-Factor Authentication** on all accounts
- Verify URLs before clicking
- Don't install apps from unknown sources

📞 Cybercrime Helpline: **1930**""",

            "hi": """🛡️ **साइबर अपराध — मार्गदर्शन और रिपोर्टिंग:**

**अगर आप पीड़ित हैं:**
1. **घबराएं नहीं** — तुरंत सब कुछ दस्तावेज करें
2. संदेश, ईमेल, लेनदेन के **स्क्रीनशॉट** लें
3. धोखेबाज के फोन नंबर, UPI आईडी नोट करें
4. कोई भी **सबूत न हटाएं**
5. पैसे वापस पाने के लिए **24 घंटे के भीतर** रिपोर्ट करें

**रिपोर्ट कहाँ करें:**
- 🌐 **cybercrime.gov.in** — ऑनलाइन शिकायत
- 📞 **हेल्पलाइन: 1930** (24/7 उपलब्ध)
- 🏛️ नजदीकी **साइबर क्राइम सेल**
- 🏦 **बैंक को तुरंत सूचित करें**

**बचाव के उपाय:**
- OTP, PIN, CVV किसी को न बताएं
- अनजान लिंक पर क्लिक न करें
- अनजान ऐप इंस्टॉल न करें

📞 साइबर अपराध हेल्पलाइन: **1930**""",

            "gu": """🛡️ **સાયબર ક્રાઈમ — માર્ગદર્શન અને રિપોર્ટિંગ:**

**જો તમે પીડિત છો:**
1. **ગભરાશો નહીં** — તરત જ બધું ડોક્યુમેન્ટ કરો
2. મેસેજ, ઈમેઈલ, ટ્રાન્ઝેક્શનના **સ્ક્રીનશૉટ** લો
3. છેતરનારના ફોન નંબર, UPI ID નોંધો
4. કોઈ પણ **પુરાવા ડિલીટ ન કરો**
5. પૈસા પાછા મેળવવા **24 કલાકમાં** રિપોર્ટ કરો

**રિપોર્ટ ક્યાં કરવો:**
- 🌐 **cybercrime.gov.in** — ઓનલાઈન ફરિયાદ
- 📞 **હેલ્પલાઈન: 1930** (24/7 ઉપલબ્ધ)
- 🏛️ નજીકનું **સાયબર ક્રાઈમ સેલ**
- 🏦 **બેંકને તરત જાણ કરો**

**બચાવના ઉપાયો:**
- OTP, PIN, CVV કોઈને ન આપો
- અજાણ્યા લિંક પર ક્લિક ન કરો
- અજાણી એપ ઈન્સ્ટોલ ન કરો
- કોઈ પણ વ્યક્તિ ફોન પર પૈસા માંગે તો ન આપો

📞 સાયબર ક્રાઈમ હેલ્પલાઈન: **1930**""",

            "ta": """🛡️ **சைபர் குற்றம் — வழிகாட்டுதல்:**

1. **பதற வேண்டாம்** — உடனே ஆதாரங்களை சேகரியுங்கள்
2. மெசேஜ், இமெயில் **ஸ்கிரீன்ஷாட்** எடுங்கள்
3. மோசடி செய்தவரின் தொலைபேசி எண் குறியுங்கள்
4. ஆதாரங்களை **அழிக்காதீர்கள்**
5. **24 மணி நேரத்திற்குள்** புகார் செய்யுங்கள்

**புகார் செய்ய:**
- 🌐 cybercrime.gov.in
- 📞 ஹெல்ப்லைன்: **1930**
- 🏦 வங்கிக்கு உடனே தெரிவிக்கவும்

📞 சைபர் ஹெல்ப்லைன்: **1930**""",

            "te": """🛡️ **సైబర్ నేరం — మార్గదర్శకత్వం:**

1. **భయపడకండి** — వెంటనే ఆధారాలను సేకరించండి
2. మెసేజ్‌లు, ఈమెయిల్ **స్క్రీన్‌షాట్** తీయండి
3. మోసగాడి ఫోన్ నంబర్ నోట్ చేయండి
4. **ఆధారాలను తొలగించకండి**
5. **24 గంటల్లో** ఫిర్యాదు చేయండి

**ఫిర్యాదు చేయడానికి:**
- 🌐 cybercrime.gov.in
- 📞 హెల్ప్‌లైన్: **1930**

📞 సైబర్ హెల్ప్‌లైన్: **1930**""",

            "bn": """🛡️ **সাইবার অপরাধ — নির্দেশিকা:**

1. **ভয় পাবেন না** — সাথে সাথে প্রমাণ সংগ্রহ করুন
2. মেসেজ, ইমেইলের **স্ক্রীনশট** নিন
3. প্রতারকের ফোন নম্বর নোট করুন
4. **প্রমাণ মুছবেন না**
5. **24 ঘণ্টার মধ্যে** রিপোর্ট করুন

📞 সাইবার হেল্পলাইন: **1930**""",

            "mr": """🛡️ **सायबर गुन्हा — मार्गदर्शन:**

1. **घाबरू नका** — लगेच पुरावे गोळा करा
2. मेसेज, ईमेलचे **स्क्रीनशॉट** घ्या
3. फसवणूक करणाऱ्याचा फोन नंबर नोंदवा
4. **पुरावे हटवू नका**
5. **24 तासांत** तक्रार करा

📞 सायबर हेल्पलाईन: **1930**""",
        },
    },
    {
        "id": "fraud",
        "keywords": [
            "fraud", "scam", "cheated", "money lost", "cheat", "financial fraud",
            "ठगी", "धोखाधड़ी", "पैसे गए", "चीट",
            "છેતરપિંડી", "ફ્રોડ", "ઠગાઈ", "પૈસા ગયા", "છેતરાઈ ગયા", "પૈસા ખોવાયા", "ઠગાઈ થઈ",
            "மோசடி", "ஏமாற்றம்", "பணம் இழந்தேன்",
            "మోసం", "మోసగించారు", "డబ్బులు పోయాయి",
            "প্রতারণা", "জালিয়াতি", "টাকা গেছে",
            "फसवणूक", "फ्रॉड", "पैसे गेले",
        ],
        "responses": {
            "en": """💰 **Fraud / Scam — Reporting & Recovery:**

**Immediate Steps:**
1. **Contact your bank** to block/freeze the transaction
2. Call **1930** (Cybercrime Helpline) within 24 hours
3. File FIR at the nearest police station
4. Report on **cybercrime.gov.in** (for online fraud)

**Applicable Legal Sections:**
- Section 420 IPC — Cheating / Fraud — Up to 7 years
- Section 406 IPC — Criminal breach of trust — Up to 3 years
- Section 66D IT Act — Cheating by personation — Up to 3 years

**Evidence to Collect:**
- Transaction IDs, UTR numbers, bank statements
- Screenshots of chats, emails, SMS
- Phone numbers and UPI IDs of the fraudster
- Website/app screenshots

**Recovery Options:**
- Request bank reversal through complaint
- File for compensation through Consumer Court
- Civil suit for recovery of money

📞 Emergency: **112** | Cybercrime: **1930**""",

            "hi": """💰 **धोखाधड़ी / ठगी — रिपोर्टिंग और पैसे वापसी:**

**तुरंत करें:**
1. **बैंक को कॉल करें** — ट्रांज़ैक्शन फ्रीज़ करवाएं
2. **1930** (साइबर हेल्पलाइन) पर 24 घंटे में कॉल करें
3. नजदीकी थाने में FIR दर्ज करें
4. **cybercrime.gov.in** पर ऑनलाइन शिकायत करें

**लागू कानूनी धाराएं:**
- धारा 420 IPC — धोखाधड़ी — 7 साल तक
- धारा 406 IPC — विश्वासघात — 3 साल तक
- धारा 66D IT Act — 3 साल तक

**ये सबूत इकट्ठा करें:**
- बैंक स्टेटमेंट, ट्रांज़ैक्शन ID
- चैट, ईमेल, SMS के स्क्रीनशॉट
- ठग के फोन नंबर, UPI ID

📞 आपातकाल: **112** | साइबर: **1930**""",

            "gu": """💰 **છેતરપિંડી / ઠગાઈ — રિપોર્ટિંગ અને પૈસા રિકવરી:**

**તરત જ કરો:**
1. **બેંકને કૉલ કરો** — ટ્રાન્ઝેક્શન ફ્રીઝ કરાવો
2. **1930** (સાયબર હેલ્પલાઈન) પર 24 કલાકમાં કૉલ કરો
3. નજીકના પોલીસ સ્ટેશનમાં FIR નોંધાવો
4. **cybercrime.gov.in** પર ઓનલાઈન ફરિયાદ કરો

**લાગુ પડતી કાયદાકીય કલમો:**
- કલમ 420 IPC — છેતરપિંડી — 7 વર્ષ સુધી
- કલમ 406 IPC — વિશ્વાસઘાત — 3 વર્ષ સુધી
- કલમ 66D IT Act — 3 વર્ષ સુધી

**આ પુરાવા ભેગા કરો:**
- બેંક સ્ટેટમેન્ટ, ટ્રાન્ઝેક્શન ID
- ચેટ, ઈમેઈલ, SMS ના સ્ક્રીનશૉટ
- છેતરનારના ફોન નંબર, UPI ID

**પૈસા પરત મેળવવાના રસ્તા:**
- બેંકમાં ફરિયાદ દ્વારા ટ્રાન્ઝેક્શન રિવર્સ
- કન્ઝ્યુમર કોર્ટમાં ફરિયાદ
- પૈસા વસૂલી માટે સિવિલ કેસ

📞 ઈમરજન્સી: **112** | સાયબર: **1930**""",

            "ta": """💰 **மோசடி — புகார் & பணம் மீட்பு:**

1. **வங்கியை உடனே தொடர்பு கொள்ளுங்கள்**
2. **1930** ஹெல்ப்லைனில் 24 மணி நேரத்தில் அழையுங்கள்
3. காவல் நிலையத்தில் FIR பதிவு செய்யுங்கள்
4. **cybercrime.gov.in** இல் புகார் செய்யுங்கள்

📞 சைபர் ஹெல்ப்லைன்: **1930**""",

            "te": """💰 **మోసం — ఫిర్యాదు & డబ్బు రికవరీ:**

1. **బ్యాంక్‌కు వెంటనే ఫోన్ చేయండి**
2. **1930** హెల్ప్‌లైన్‌లో 24 గంటల్లో ఫిర్యాదు చేయండి
3. పోలీసు స్టేషన్‌లో FIR నమోదు చేయండి

📞 సైబర్ హెల్ప్‌లైన్: **1930**""",

            "bn": """💰 **প্রতারণা — অভিযোগ & টাকা ফেরত:**

1. **ব্যাংকে এখনই ফোন করুন**
2. **1930** হেল্পলাইনে 24 ঘণ্টায় কল করুন
3. থানায় FIR করুন

📞 সাইবার হেল্পলাইন: **1930**""",

            "mr": """💰 **फसवणूक — तक्रार & पैसे परत:**

1. **बँकेला लगेच फोन करा**
2. **1930** हेल्पलाईनवर 24 तासांत कॉल करा
3. पोलीस ठाण्यात FIR नोंदवा

📞 सायबर हेल्पलाईन: **1930**""",
        },
    },
    {
        "id": "women",
        "keywords": [
            "women", "domestic violence", "dowry", "harassment", "sexual", "molestation", "stalking", "eve teasing", "protection of women",
            "महिला", "दहेज", "घरेलू हिंसा", "यौन उत्पीड़न", "छेड़छाड़", "पीछा करना",
            "મહિલા", "દહેજ", "ઘરેલું હિંસા", "જાતીય સતામણી", "છેડછાડ", "સ્ત્રી", "મહિલા સુરક્ષા", "સતામણી",
            "பெண்கள்", "தொல்லை", "வரதட்சணை",
            "మహిళ", "వేధింపు", "కట్నం",
            "মহিলা", "যৌতুক", "হয়রানি",
            "महिला", "हुंडा", "छळ",
        ],
        "responses": {
            "en": """👩 **Women Safety — Laws & Resources:**

**Key Laws:**
- **Section 354 IPC** — Assault on woman (1-5 years)
- **Section 376 IPC** — Rape (10 years to life)
- **Section 498A IPC** — Dowry harassment (up to 3 years)
- **Domestic Violence Act, 2005** — Protection orders
- **POCSO Act** — Protection of children

**If You Are in Danger:**
1. Call **112** (Emergency) or **181** (Women Helpline)
2. Go to the nearest police station
3. Go to a **One Stop Centre (Sakhi)** for shelter + legal + medical help
4. Apply for a **Protection Order** under DV Act

**Helplines:**
- 📞 **181** — Women Helpline (24/7)
- 📞 **112** — Emergency
- 📞 **1091** — Women Police Helpline
- 📞 **1098** — Child Helpline""",

            "hi": """👩 **महिला सुरक्षा — कानून और मदद:**

**प्रमुख कानून:**
- **धारा 354 IPC** — महिला पर हमला (1-5 साल)
- **धारा 376 IPC** — बलात्कार (10 साल से उम्रकैद)
- **धारा 498A IPC** — दहेज उत्पीड़न (3 साल तक)
- **घरेलू हिंसा अधिनियम 2005** — सुरक्षा आदेश

**अगर आप खतरे में हैं:**
1. **112** (आपातकाल) या **181** (महिला हेल्पलाइन) पर कॉल करें
2. नजदीकी पुलिस स्टेशन जाएं
3. **वन स्टॉप सेंटर (सखी)** जाएं — आश्रय + कानूनी + चिकित्सा मदद

📞 महिला हेल्पलाइन: **181** | आपातकाल: **112**""",

            "gu": """👩 **મહિલા સુરક્ષા — કાયદા અને મદદ:**

**મુખ્ય કાયદા:**
- **કલમ 354 IPC** — મહિલા પર હુમલો (1-5 વર્ષ)
- **કલમ 376 IPC** — બળાત્કાર (10 વર્ષ થી આજીવન)
- **કલમ 498A IPC** — દહેજ સતામણી (3 વર્ષ સુધી)
- **ઘરેલું હિંસા કાયદો 2005** — સુરક્ષા આદેશ

**જો તમે જોખમમાં છો:**
1. **112** (ઈમરજન્સી) અથવા **181** (મહિલા હેલ્પલાઈન) પર કૉલ કરો
2. નજીકના પોલીસ સ્ટેશન જાઓ
3. **વન સ્ટોપ સેન્ટર (સખી)** જાઓ — આશરો + કાનૂની + તબીબી મદદ
4. DV Act હેઠળ **સુરક્ષા આદેશ** માટે અરજી કરો

**હેલ્પલાઈન:**
- 📞 **181** — મહિલા હેલ્પલાઈન (24/7)
- 📞 **112** — ઈમરજન્સી
- 📞 **1091** — મહિલા પોલીસ હેલ્પલાઈન
- 📞 **1098** — ચાઈલ્ડ હેલ્પલાઈન

તમે એકલા નથી. અમે મદદ કરવા અહીં છીએ.""",

            "ta": """👩 **பெண்கள் பாதுகாப்பு:**

- **112** அவசர உதவி | **181** பெண்கள் ஹெல்ப்லைன்
- காவல் நிலையத்தில் புகார் செய்யுங்கள்
- ஒன் ஸ்டாப் சென்டர் (சகி) — தங்குமிடம் + சட்ட + மருத்துவ உதவி

📞 பெண்கள் ஹெல்ப்லைன்: **181**""",

            "te": """👩 **మహిళా భద్రత:**

- **112** ఎమర్జెన్సీ | **181** మహిళా హెల్ప్‌లైన్
- పోలీసు స్టేషన్‌లో ఫిర్యాదు చేయండి

📞 మహిళా హెల్ప్‌లైన్: **181**""",

            "bn": """👩 **মহিলা নিরাপত্তা:**

- **112** জরুরি | **181** মহিলা হেল্পলাইন
- থানায় অভিযোগ করুন

📞 মহিলা হেল্পলাইন: **181**""",

            "mr": """👩 **महिला सुरक्षा:**

- **112** आणीबाणी | **181** महिला हेल्पलाईन
- पोलीस ठाण्यात तक्रार करा

📞 महिला हेल्पलाईन: **181**""",
        },
    },
    {
        "id": "theft",
        "keywords": [
            "theft", "robbery", "burglary", "stolen", "stole", "steal", "snatch", "pickpocket", "house break",
            "चोरी", "लूट", "डकैती", "चुराया", "छीना",
            "ચોરી", "લૂંટ", "ડાકુ", "ચોરાયું", "છીનવી લીધું", "ઘરફોડ", "લૂંટફાટ",
            "திருட்டு", "கொள்ளை",
            "దొంగతనం", "దోపిడీ",
            "চুরি", "ডাকাতি",
            "चोरी", "दरोडा",
        ],
        "responses": {
            "en": """🚨 **Theft / Robbery — Report & Recovery:**

**Immediate Steps:**
1. Call **112** if the crime is in progress
2. Note descriptions — suspect, vehicle, direction
3. Do NOT touch anything at the crime scene
4. File FIR at nearest police station

**Legal Sections:**
- Section 379 IPC — Theft — Up to 3 years
- Section 392 IPC — Robbery — Up to 10 years
- Section 395 IPC — Dacoity — Up to life imprisonment
- Section 457 IPC — House-breaking — Up to 5 years

**For Stolen Mobile:**
- Block SIM via carrier helpline
- Report IMEI on **ceir.gov.in** to block device
- Change passwords for all linked accounts
- Mention IMEI in FIR

📞 Emergency: **112**""",

            "hi": """🚨 **चोरी / लूट — रिपोर्ट करें:**

**तुरंत करें:**
1. अगर अपराध हो रहा है तो **112** पर कॉल करें
2. संदिग्ध का विवरण नोट करें
3. घटनास्थल पर कुछ न छुएं
4. नजदीकी थाने में FIR दर्ज करें

**मोबाइल चोरी होने पर:**
- SIM ब्लॉक करें
- **ceir.gov.in** पर IMEI रिपोर्ट करें
- सभी पासवर्ड बदलें

📞 आपातकाल: **112**""",

            "gu": """🚨 **ચોરી / લૂંટ — રિપોર્ટ કરો:**

**તરત જ કરો:**
1. જો ગુનો થઈ રહ્યો હોય તો **112** પર કૉલ કરો
2. શંકાસ્પદ વ્યક્તિનું વર્ણન નોંધો
3. ઘટનાસ્થળ પર કંઈ ન અડો
4. નજીકના પોલીસ સ્ટેશનમાં FIR નોંધાવો

**કાયદાકીય કલમો:**
- કલમ 379 IPC — ચોરી — 3 વર્ષ સુધી
- કલમ 392 IPC — લૂંટ — 10 વર્ષ સુધી
- કલમ 395 IPC — ડાકુ — આજીવન કેદ
- કલમ 457 IPC — ઘરફોડ — 5 વર્ષ સુધી

**મોબાઈલ ચોરાયો હોય તો:**
- SIM બ્લૉક કરો
- **ceir.gov.in** પર IMEI રિપોર્ટ કરો
- બધા પાસવર્ડ બદલો
- FIR માં IMEI નંબર લખાવો

📞 ઈમરજન્સી: **112**""",

            "ta": """🚨 **திருட்டு / கொள்ளை:**

1. **112** அழையுங்கள்
2. FIR பதிவு செய்யுங்கள்
3. மொபைல் திருடப்பட்டால் **ceir.gov.in** இல் IMEI புகார் செய்யுங்கள்

📞 அவசரம்: **112**""",

            "te": """🚨 **దొంగతనం / దోపిడీ:**

1. **112** కాల్ చేయండి
2. FIR నమోదు చేయండి

📞 ఎమర్జెన్సీ: **112**""",

            "bn": """🚨 **চুরি / ডাকাতি:**

1. **112** কল করুন
2. FIR করুন

📞 জরুরি: **112**""",

            "mr": """🚨 **चोरी / दरोडा:**

1. **112** वर कॉल करा
2. FIR नोंदवा

📞 आणीबाणी: **112**""",
        },
    },
    {
        "id": "missing",
        "keywords": [
            "missing", "kidnap", "abduct", "lost person", "child missing",
            "गायब", "अपहरण", "लापता", "बच्चा गायब",
            "ગુમ", "અપહરણ", "ગાયબ", "બાળક ગુમ", "ખોવાયેલ", "ખોવાયેલું",
            "காணாமல்", "கடத்தல்",
            "తప్పిపోయిన", "కిడ్నాప్",
            "নিখোঁজ", "অপহরণ",
            "बेपत्ता", "अपहरण",
        ],
        "responses": {
            "en": """🔎 **Missing Person — Immediate Steps:**

1. File a **missing person report** at nearest police station
2. Police **cannot refuse** or ask you to wait 24 hours — this is a myth
3. Provide recent photograph and physical description
4. Share last known location, clothing, contacts

**For Missing Children:**
- **Child Helpline**: 1098
- **Khoya Paya Portal**: khoyapaya.gov.in

📞 Emergency: **112** | Child: **1098**""",

            "hi": """🔎 **लापता व्यक्ति — तुरंत करें:**

1. नजदीकी थाने में **गुमशुदगी रिपोर्ट** दर्ज करें
2. पुलिस 24 घंटे **इंतज़ार करने को नहीं कह सकती**
3. हालिया फोटो और विवरण दें
4. आखिरी ज्ञात स्थान, कपड़े, संपर्क बताएं

📞 आपातकाल: **112** | बाल हेल्पलाइन: **1098**""",

            "gu": """🔎 **ગુમ થયેલ વ્યક્તિ — તરત જ કરો:**

1. નજીકના પોલીસ સ્ટેશનમાં **ગુમ થયાની ફરિયાદ** નોંધાવો
2. પોલીસ 24 કલાક **રાહ જોવાનું કહી શકે નહીં** — આ ખોટી માન્યતા છે
3. તાજેતરનો ફોટો અને શારીરિક વર્ણન આપો
4. છેલ્લે ક્યાં જોવામાં આવ્યા, કપડાં, સંપર્ક જણાવો

**ગુમ થયેલ બાળકો માટે:**
- **ચાઈલ્ડ હેલ્પલાઈન**: 1098
- **ખોયા પાયા પોર્ટલ**: khoyapaya.gov.in

📞 ઈમરજન્સી: **112** | ચાઈલ્ડ: **1098**""",

            "ta": """🔎 **காணாமல் போனவர்:**

1. காவல் நிலையத்தில் புகார் செய்யுங்கள்
2. 24 மணி நேரம் காத்திருக்க வேண்டாம்

📞 அவசரம்: **112** | குழந்தை: **1098**""",

            "te": """🔎 **తప్పిపోయిన వ్యక్తి:**

1. పోలీసు స్టేషన్‌లో ఫిర్యాదు చేయండి

📞 ఎమర్జెన్సీ: **112** | చిల్డ్రన్: **1098**""",

            "bn": """🔎 **নিখোঁজ ব্যক্তি:**

1. থানায় অভিযোগ করুন

📞 জরুরি: **112** | শিশু: **1098**""",

            "mr": """🔎 **बेपत्ता व्यक्ती:**

1. पोलीस ठाण्यात तक्रार करा

📞 आणीबाणी: **112** | बाल: **1098**""",
        },
    },
    {
        "id": "hello",
        "keywords": [
            "hello", "hi", "hey", "good morning", "good evening", "namaste", "help",
            "नमस्ते", "मदद", "हेलो",
            "નમસ્તે", "મદદ", "હેલો", "કેમ છો", "મદદ કરો", "જય શ્રી કૃષ્ણ",
            "வணக்கம்", "உதவி",
            "నమస్కారం", "సహాయం",
            "নমস্কার", "সাহায্য",
            "नमस्कार", "मदत",
        ],
        "responses": {
            "en": """👋 **Hello! I'm CrimeGPT Assistant.**

I'm here to help you with legal guidance, crime reporting, and investigation support.

🔹 **Ask me about:**
- How to file an FIR or complaint
- Your legal rights as a victim
- Cybercrime reporting and prevention
- Applicable IPC/IT Act sections
- Evidence collection
- Bail process
- Women safety laws and helplines
- Missing person procedures
- Theft/robbery reporting

🔹 **Helplines:**
- 📞 Emergency: **112**
- 👩 Women: **181**
- 🌐 Cybercrime: **1930**
- 👶 Child: **1098**

What can I help you with today?""",

            "hi": """👋 **नमस्ते! मैं CrimeGPT सहायक हूं।**

मैं कानूनी मार्गदर्शन, अपराध रिपोर्टिंग और जांच में मदद के लिए यहां हूं।

🔹 **मुझसे पूछें:**
- FIR कैसे दर्ज करें
- पीड़ित के अधिकार
- साइबर अपराध रिपोर्टिंग
- कानूनी धाराएं
- महिला सुरक्षा
- जमानत प्रक्रिया

📞 आपातकाल: **112** | महिला: **181** | साइबर: **1930**

आज मैं आपकी कैसे मदद कर सकता हूं?""",

            "gu": """👋 **નમસ્તે! હું CrimeGPT સહાયક છું.**

હું કાનૂની માર્ગદર્શન, ગુના રિપોર્ટિંગ અને તપાસમાં મદદ માટે અહીં છું.

🔹 **મને પૂછો:**
- FIR કેવી રીતે નોંધાવવી
- પીડિતના અધિકારો
- સાયબર ક્રાઈમ રિપોર્ટિંગ
- છેતરપિંડી / ઠગાઈ
- ચોરી / લૂંટ
- મહિલા સુરક્ષા
- ગુમ થયેલ વ્યક્તિ
- જમાનત પ્રક્રિયા

📞 ઈમરજન્સી: **112** | મહિલા: **181** | સાયબર: **1930**

આજે હું તમારી કેવી રીતે મદદ કરી શકું?""",

            "ta": """👋 **வணக்கம்! நான் CrimeGPT உதவியாளர்.**

📞 அவசரம்: **112** | பெண்கள்: **181** | சைபர்: **1930**

நான் உங்களுக்கு எப்படி உதவ முடியும்?""",

            "te": """👋 **నమస్కారం! నేను CrimeGPT సహాయకుడిని.**

📞 ఎమర్జెన్సీ: **112** | మహిళలు: **181** | సైబర్: **1930**

నేను మీకు ఎలా సహాయం చేయగలను?""",

            "bn": """👋 **নমস্কার! আমি CrimeGPT সহায়ক।**

📞 জরুরি: **112** | মহিলা: **181** | সাইবার: **1930**

আমি কিভাবে সাহায্য করতে পারি?""",

            "mr": """👋 **नमस्कार! मी CrimeGPT सहाय्यक आहे.**

📞 आणीबाणी: **112** | महिला: **181** | सायबर: **1930**

मी तुम्हाला कशी मदत करू शकतो?""",
        },
    },
    {
        "id": "bail",
        "keywords": [
            "bail", "anticipatory bail", "regular bail", "jail", "arrest",
            "ज़मानत", "जमानत", "गिरफ्तारी", "जेल",
            "જામીન", "ધરપકડ", "જેલ", "જામીન કેવી રીતે", "જામીન મળશે",
            "ஜாமீன்", "கைது",
            "జామీన్", "అరెస్ట్",
            "জামিন", "গ্রেপ্তার",
            "जामीन", "अटक",
        ],
        "responses": {
            "en": """🏛️ **Bail — Types & Procedures:**

**Types:**
1. **Regular Bail** (Section 437/439 CrPC) — After arrest
2. **Anticipatory Bail** (Section 438 CrPC) — Before arrest
3. **Interim Bail** — Temporary
4. **Default Bail** — If chargesheet not filed in time

**How to Apply:**
- Through a lawyer before appropriate court
- Sessions Court / High Court for anticipatory bail
- Magistrate Court for regular bail

📞 Legal Aid (NALSA): **15100**""",

            "hi": """🏛️ **जमानत — प्रकार और प्रक्रिया:**

**प्रकार:**
1. **नियमित जमानत** — गिरफ्तारी के बाद
2. **अग्रिम जमानत** — गिरफ्तारी से पहले
3. **अंतरिम जमानत** — अस्थायी
4. **डिफ़ॉल्ट जमानत** — चार्जशीट समय पर न दाखिल हो तो

📞 कानूनी सहायता: **15100**""",

            "gu": """🏛️ **જામીન — પ્રકાર અને પ્રક્રિયા:**

**પ્રકારો:**
1. **રેગ્યુલર જામીન** (કલમ 437/439 CrPC) — ધરપકડ પછી
2. **આગોતરી જામીન** (કલમ 438 CrPC) — ધરપકડ પહેલાં
3. **વચગાળાનો જામીન** — અસ્થાયી
4. **ડિફૉલ્ટ જામીન** — ચાર્જશીટ સમયસર ન દાખલ થાય તો

**અરજી કેવી રીતે કરવી:**
- વકીલ દ્વારા યોગ્ય કોર્ટ સમક્ષ
- સેશન્સ કોર્ટ / હાઈ કોર્ટ — આગોતરી જામીન
- મેજિસ્ટ્રેટ કોર્ટ — રેગ્યુલર જામીન

📞 કાનૂની સહાય (NALSA): **15100**""",

            "ta": """🏛️ **ஜாமீன்:**
1. வழக்கமான ஜாமீன் — கைதுக்குப் பின்
2. முன்கூட்டிய ஜாமீன் — கைதுக்கு முன்
📞 சட்ட உதவி: **15100**""",

            "te": """🏛️ **జామీన్:**
1. రెగ్యులర్ జామీన్ — అరెస్ట్ తర్వాత
2. ముందస్తు జామీన్ — అరెస్ట్ ముందు
📞 న్యాయ సహాయం: **15100**""",

            "bn": """🏛️ **জামিন:**
1. নিয়মিত জামিন — গ্রেপ্তারের পরে
2. আগাম জামিন — গ্রেপ্তারের আগে
📞 আইনি সহায়তা: **15100**""",

            "mr": """🏛️ **जामीन:**
1. नियमित जामीन — अटकेनंतर
2. अटकपूर्व जामीन — अटकेपूर्वी
📞 कायदेशीर मदत: **15100**""",
        },
    },
    {
        "id": "helplines",
        "keywords": [
            "helpline", "phone number", "contact", "emergency number", "call",
            "हेल्पलाइन", "फोन नंबर", "नंबर", "कॉल",
            "હેલ્પલાઈન", "ફોન નંબર", "નંબર", "કૉલ", "ઈમરજન્સી નંબર", "ફોન",
            "ஹெல்ப்லைன்", "தொலைபேசி",
            "హెల్ప్‌లైన్", "ఫోన్",
            "হেল্পলাইন", "ফোন",
            "हेल्पलाईन", "फोन",
        ],
        "responses": {
            "en": """📞 **Important Helpline Numbers:**

| Service | Number |
|---------|--------|
| Emergency (All) | **112** |
| Police | **100** |
| Fire | **101** |
| Ambulance | **108** |
| Women Helpline | **181** |
| Cybercrime | **1930** |
| Child Helpline | **1098** |
| Senior Citizen | **14567** |
| Legal Aid (NALSA) | **15100** |
| Anti-Corruption | **1800-11-0180** |
| RBI Banking Fraud | **14440** |""",

            "hi": """📞 **महत्वपूर्ण हेल्पलाइन नंबर:**

- 🚨 आपातकाल: **112**
- 👮 पुलिस: **100**
- 🚒 फायर: **101**
- 🚑 एम्बुलेंस: **108**
- 👩 महिला: **181**
- 🌐 साइबर: **1930**
- 👶 बाल हेल्पलाइन: **1098**
- 👴 वरिष्ठ नागरिक: **14567**
- ⚖️ कानूनी सहायता: **15100**""",

            "gu": """📞 **મહત્વપૂર્ણ હેલ્પલાઈન નંબર:**

- 🚨 ઈમરજન્સી: **112**
- 👮 પોલીસ: **100**
- 🚒 ફાયર: **101**
- 🚑 એમ્બ્યુલન્સ: **108**
- 👩 મહિલા: **181**
- 🌐 સાયબર: **1930**
- 👶 ચાઈલ્ડ હેલ્પલાઈન: **1098**
- 👴 વરિષ્ઠ નાગરિક: **14567**
- ⚖️ કાનૂની સહાય: **15100**
- 🏦 બેંકિંગ ફ્રોડ (RBI): **14440**""",

            "ta": """📞 **உதவி எண்கள்:**
🚨 அவசரம்: **112** | 👩 பெண்கள்: **181** | 🌐 சைபர்: **1930** | 👶 குழந்தை: **1098** | ⚖️ சட்ட உதவி: **15100**""",

            "te": """📞 **సహాయ నంబర్లు:**
🚨 ఎమర్జెన్సీ: **112** | 👩 మహిళలు: **181** | 🌐 సైబర్: **1930** | 👶 చిల్డ్రన్: **1098** | ⚖️ న్యాయ సహాయం: **15100**""",

            "bn": """📞 **হেল্পলাইন নম্বর:**
🚨 জরুরি: **112** | 👩 মহিলা: **181** | 🌐 সাইবার: **1930** | 👶 শিশু: **1098** | ⚖️ আইনি সহায়তা: **15100**""",

            "mr": """📞 **हेल्पलाईन नंबर:**
🚨 आणीबाणी: **112** | 👩 महिला: **181** | 🌐 सायबर: **1930** | 👶 बाल: **1098** | ⚖️ कायदेशीर: **15100**""",
        },
    },
    {
        "id": "evidence",
        "keywords": [
            "evidence", "proof", "document", "preserve", "collect evidence",
            "सबूत", "प्रमाण", "दस्तावेज",
            "પુરાવા", "સાબિતી", "દસ્તાવેજ", "પુરાવો",
            "ஆதாரம்", "சான்று",
            "ఆధారం", "రుజువు",
            "প্রমাণ", "দলিল",
            "पुरावा", "दस्तऐवज",
        ],
        "responses": {
            "en": """🔍 **Evidence Collection Guide:**

**Types of Evidence:**
1. **Physical** — Weapons, clothing, biological samples
2. **Documentary** — Letters, receipts, contracts
3. **Digital** — Screenshots, emails, call logs, CCTV
4. **Testimonial** — Witness statements

**Best Practices:**
- Photograph everything before touching
- Use gloves when handling physical evidence
- Save original digital files — don't edit
- Request CCTV within **72 hours**
- Preserve screenshots with **timestamps**""",

            "hi": """🔍 **सबूत इकट्ठा करने की गाइड:**

**सबूतों के प्रकार:**
1. **भौतिक** — हथियार, कपड़े
2. **दस्तावेज़ी** — पत्र, रसीदें
3. **डिजिटल** — स्क्रीनशॉट, ईमेल, कॉल लॉग, CCTV
4. **गवाही** — गवाहों के बयान

**सावधानियां:**
- छूने से पहले फोटो लें
- CCTV **72 घंटे** में मांगें
- ऑरिजिनल फाइल सेव करें""",

            "gu": """🔍 **પુરાવા ભેગા કરવાની માર્ગદર્શિકા:**

**પુરાવાના પ્રકારો:**
1. **ભૌતિક** — હથિયાર, કપડાં
2. **દસ્તાવેજી** — પત્રો, રસીદો
3. **ડિજિટલ** — સ્ક્રીનશૉટ, ઈમેઈલ, કૉલ લૉગ, CCTV
4. **સાક્ષી** — સાક્ષીઓના બયાન

**સાવચેતીઓ:**
- અડતા પહેલાં ફોટો લો
- CCTV **72 કલાકમાં** માંગો
- ઓરિજિનલ ફાઈલ સેવ કરો — એડિટ ન કરો
- ટાઈમસ્ટેમ્પ સાથે સ્ક્રીનશૉટ લો""",

            "ta": """🔍 **ஆதாரங்கள் சேகரிப்பு:** ஸ்கிரீன்ஷாட் எடுங்கள், CCTV **72 மணி நேரத்தில்** கேளுங்கள், அசல் கோப்புகளை சேமியுங்கள்.""",
            "te": """🔍 **ఆధారాలు సేకరణ:** స్క్రీన్‌షాట్ తీయండి, CCTV **72 గంటల్లో** కోరండి.""",
            "bn": """🔍 **প্রমাণ সংগ্রহ:** স্ক্রীনশট নিন, CCTV **72 ঘণ্টায়** চান।""",
            "mr": """🔍 **पुरावे गोळा करा:** स्क्रीनशॉट घ्या, CCTV **72 तासांत** मागवा.""",
        },
    },
    {
        "id": "ipc_sections",
        "keywords": [
            "ipc", "section", "bns", "legal section", "penal code", "law section", "which section", "punishment",
            "धारा", "सजा", "कानून",
            "કલમ", "સજા", "કાયદો", "કયો કાયદો", "કયો કલમ",
            "சட்டப் பிரிவு", "தண்டனை",
            "సెక్షన్", "శిక్ష",
            "ধারা", "শাস্তি",
            "कलम", "शिक्षा",
        ],
        "responses": {
            "en": """⚖️ **Common IPC / BNS Sections:**

| Section | Offence | Punishment |
|---------|---------|------------|
| 302 IPC / 101 BNS | Murder | Life / Death |
| 307 IPC / 109 BNS | Attempt to murder | Up to 10 years |
| 376 IPC / 64 BNS | Rape | 10 years to life |
| 420 IPC / 318 BNS | Cheating / Fraud | Up to 7 years |
| 379 IPC / 303 BNS | Theft | Up to 3 years |
| 392 IPC / 309 BNS | Robbery | Up to 10 years |
| 498A IPC / 85 BNS | Dowry harassment | Up to 3 years |
| 66 IT Act | Computer offences | Up to 3 years |
| 66C IT Act | Identity theft | Up to 3 years |

**Note:** India has moved from IPC to **BNS 2023** (effective 1 July 2024)""",

            "hi": """⚖️ **प्रमुख IPC / BNS धाराएं:**

- 302 IPC / 101 BNS — हत्या — उम्रकैद / मृत्युदंड
- 420 IPC / 318 BNS — धोखाधड़ी — 7 साल
- 379 IPC / 303 BNS — चोरी — 3 साल
- 376 IPC / 64 BNS — बलात्कार — 10 साल से उम्रकैद
- 498A IPC / 85 BNS — दहेज उत्पीड़न — 3 साल
- 66 IT Act — साइबर अपराध — 3 साल""",

            "gu": """⚖️ **મુખ્ય IPC / BNS કલમો:**

- 302 IPC / 101 BNS — હત્યા — આજીવન કેદ / ફાંસી
- 420 IPC / 318 BNS — છેતરપિંડી — 7 વર્ષ
- 379 IPC / 303 BNS — ચોરી — 3 વર્ષ
- 376 IPC / 64 BNS — બળાત્કાર — 10 વર્ષ થી આજીવન
- 498A IPC / 85 BNS — દહેજ સતામણી — 3 વર્ષ
- 392 IPC / 309 BNS — લૂંટ — 10 વર્ષ
- 66 IT Act — સાયબર ગુનો — 3 વર્ષ
- 66C IT Act — ઓળખ ચોરી — 3 વર્ષ

**નોંધ:** ભારત IPC થી **BNS 2023** પર આવી ગયું છે (1 જુલાઈ 2024 થી)""",

            "ta": """⚖️ **முக்கிய சட்டப் பிரிவுகள்:** 302 IPC — கொலை | 420 IPC — மோசடி | 376 IPC — பலாத்காரம் | 379 IPC — திருட்டு""",
            "te": """⚖️ **ముఖ్య చట్ట సెక్షన్లు:** 302 IPC — హత్య | 420 IPC — మోసం | 376 IPC — అత్యాచారం | 379 IPC — దొంగతనం""",
            "bn": """⚖️ **প্রধান ধারাসমূহ:** 302 IPC — খুন | 420 IPC — প্রতারণা | 376 IPC — ধর্ষণ | 379 IPC — চুরি""",
            "mr": """⚖️ **प्रमुख कलम:** 302 IPC — खून | 420 IPC — फसवणूक | 376 IPC — बलात्कार | 379 IPC — चोरी""",
        },
    },
    {
        "id": "track_case",
        "keywords": [
            "track", "status", "progress", "follow up", "fir status", "complaint status", "case status",
            "स्थिति", "केस कहाँ तक", "शिकायत का स्टेटस",
            "સ્ટેટસ", "ફરિયાદ ક્યાં સુધી", "કેસ ક્યાં સુધી", "ફરિયાદનો સ્ટેટસ",
            "நிலை", "புகார் நிலை",
            "స్టేటస్", "ఫిర్యాదు స్థితి",
            "অবস্থা", "মামলার স্থিতি",
            "स्थिती", "तक्रार स्थिती",
        ],
        "responses": {
            "en": """📊 **Track Your Case / FIR Status:**

1. Visit your state police website
2. Go to "FIR Status" section
3. Enter FIR number, year, police station
4. Contact the **Investigating Officer** directly
5. Send written request to **SP/SSP** if no response
6. File **RTI** for case details

📞 Emergency: **112**""",

            "hi": """📊 **अपना केस / FIR स्टेटस ट्रैक करें:**

1. अपने राज्य की पुलिस वेबसाइट पर जाएं
2. "FIR स्टेटस" में देखें
3. FIR नंबर, साल, थाना भरें
4. जांच अधिकारी से सीधे संपर्क करें
5. जवाब न मिले तो **SP/SSP** को लिखें""",

            "gu": """📊 **તમારો કેસ / FIR સ્ટેટસ ટ્રેક કરો:**

1. તમારા રાજ્યની પોલીસ વેબસાઈટ પર જાઓ
2. "FIR Status" સેક્શનમાં જુઓ
3. FIR નંબર, વર્ષ, પોલીસ સ્ટેશન ભરો
4. **તપાસ અધિકારી (IO)** ને સીધો સંપર્ક કરો
5. જવાબ ન મળે તો **SP/SSP** ને લેખિત ફરિયાદ આપો
6. કેસ ડિટેલ માટે **RTI** ફાઈલ કરો

📞 ઈમરજન્સી: **112**""",

            "ta": """📊 **வழக்கு நிலை:** காவல்துறை இணையதளத்தில் FIR நிலை பார்க்கவும்.""",
            "te": """📊 **కేసు స్థితి:** పోలీసు వెబ్‌సైట్‌లో FIR స్టేటస్ చూడండి.""",
            "bn": """📊 **মামলার অবস্থা:** পুলিশ ওয়েবসাইটে FIR স্ট্যাটাস দেখুন।""",
            "mr": """📊 **केस स्थिती:** पोलीस वेबसाईटवर FIR स्थिती पहा.""",
        },
    },
    {
        "id": "lawyer",
        "keywords": [
            "lawyer", "legal aid", "advocate", "attorney", "court",
            "वकील", "कानूनी सहायता", "कोर्ट", "अदालत",
            "વકીલ", "કાનૂની સહાય", "કોર્ટ", "અદાલત", "વકીલ ક્યાં મળશે",
            "வழக்கறிஞர்", "நீதிமன்றம்",
            "న్యాయవాది", "కోర్టు",
            "উকিল", "আদালত",
            "वकील", "न्यायालय",
        ],
        "responses": {
            "en": """🏛️ **Legal Aid & Finding a Lawyer:**

**Free Legal Aid (Your Right under Article 39A):**
- NALSA Helpline: **15100**
- Website: nalsa.gov.in

**Who Gets Free Legal Aid:**
- Women and children
- SC/ST community
- Persons with disabilities
- Income below ₹3 lakhs

**How to Find a Lawyer:**
1. Contact **District Legal Services Authority (DLSA)**
2. Visit local **Bar Association**
3. Ask NGOs working in legal aid

📞 Legal Aid: **15100**""",

            "hi": """🏛️ **कानूनी सहायता और वकील:**

**मुफ्त कानूनी सहायता (अनुच्छेद 39A):**
- NALSA हेल्पलाइन: **15100**

**किसे मिलती है मुफ्त मदद:**
- महिलाएं और बच्चे
- SC/ST वर्ग
- विकलांग व्यक्ति
- ₹3 लाख से कम आय

📞 कानूनी सहायता: **15100**""",

            "gu": """🏛️ **કાનૂની સહાય અને વકીલ:**

**મફત કાનૂની સહાય (અનુચ્છેદ 39A — તમારો અધિકાર):**
- NALSA હેલ્પલાઈન: **15100**
- વેબસાઈટ: nalsa.gov.in

**કોને મળે છે મફત સહાય:**
- મહિલાઓ અને બાળકો
- SC/ST સમુદાય
- દિવ્યાંગ વ્યક્તિઓ
- ₹3 લાખ થી ઓછી આવક

**વકીલ કેવી રીતે શોધવો:**
1. **જિલ્લા કાનૂની સેવા સત્તામંડળ (DLSA)** નો સંપર્ક કરો
2. સ્થાનિક **બાર એસોસિએશન** ની મુલાકાત લો

📞 કાનૂની સહાય: **15100**""",

            "ta": """🏛️ **சட்ட உதவி:** NALSA ஹெல்ப்லைன்: **15100**""",
            "te": """🏛️ **న్యాయ సహాయం:** NALSA హెల్ప్‌లైన్: **15100**""",
            "bn": """🏛️ **আইনি সহায়তা:** NALSA হেল্পলাইন: **15100**""",
            "mr": """🏛️ **कायदेशीर मदत:** NALSA हेल्पलाईन: **15100**""",
        },
    },
]


# ─── Language-native fallback messages ─────────────────────────────────────────

_NATIVE_FALLBACK = {
    "en": """I understand you're asking about: *"{message}"*

I can help you with:
- How to file an FIR
- Your legal rights
- Cybercrime reporting
- Fraud / theft reporting
- Women safety
- Missing person
- Bail process
- Legal sections & helplines

📞 Emergency: **112** | Women: **181** | Cybercrime: **1930**

Please try asking in a different way — for example, "How do I file an FIR?" or "I was cheated" """,

    "hi": """मैं आपका सवाल समझ रहा हूं: *"{message}"*

मैं इन विषयों में मदद कर सकता हूं:
- FIR कैसे दर्ज करें
- पीड़ित के अधिकार
- साइबर अपराध रिपोर्टिंग
- धोखाधड़ी / चोरी
- महिला सुरक्षा
- लापता व्यक्ति
- जमानत प्रक्रिया
- हेल्पलाइन नंबर

📞 आपातकाल: **112** | महिला: **181** | साइबर: **1930**

कृपया अपना सवाल दूसरे तरीके से पूछें — जैसे "FIR कैसे करें" या "मुझसे ठगी हुई" """,

    "gu": """હું તમારો પ્રશ્ન સમજી રહ્યો છું: *"{message}"*

હું આ વિષયોમાં મદદ કરી શકું છું:
- FIR કેવી રીતે નોંધાવવી
- પીડિતના અધિકારો
- સાયબર ક્રાઈમ રિપોર્ટિંગ
- છેતરપિંડી / ચોરી
- મહિલા સુરક્ષા
- ગુમ થયેલ વ્યક્તિ
- જામીન પ્રક્રિયા
- હેલ્પલાઈન નંબર

📞 ઈમરજન્સી: **112** | મહિલા: **181** | સાયબર: **1930**

કૃપા કરીને તમારો પ્રશ્ન અલગ રીતે પૂછો — જેમ કે "FIR કેવી રીતે કરાવવી" અથવા "મારી સાથે છેતરપિંડી થઈ" """,

    "ta": """நான் உங்கள் கேள்வியைப் புரிந்து கொள்கிறேன்: *"{message}"*

📞 அவசரம்: **112** | பெண்கள்: **181** | சைபர்: **1930**

வேறு விதமாகக் கேளுங்கள் — உதாரணம்: "FIR எப்படி பதிவு செய்வது?" """,

    "te": """నేను మీ ప్రశ్నను అర్థం చేసుకుంటున్నాను: *"{message}"*

📞 ఎమర్జెన్సీ: **112** | మహిళలు: **181** | సైబర్: **1930**""",

    "bn": """আমি আপনার প্রশ্ন বুঝতে পারছি: *"{message}"*

📞 জরুরি: **112** | মহিলা: **181** | সাইবার: **1930**""",

    "mr": """मी तुमचा प्रश्न समजत आहे: *"{message}"*

📞 आणीबाणी: **112** | महिला: **181** | सायबर: **1930**""",
}


def _smart_mock_response(message: str, context: str, user_role: str, language: str = "en") -> str:
    """Keyword-based intelligent response matching — fully multilingual."""
    msg_lower = message.lower().strip()

    # ── Handle slash commands (still works for tech-savvy users) ───────────
    if msg_lower.startswith("/"):
        slash_resp = _handle_slash_command(msg_lower, language)
        if slash_resp:
            return slash_resp

    # ── Match against multilingual topics ──────────────────────────────────
    best_topic = None
    best_score = 0

    for topic in _MULTILINGUAL_TOPICS:
        score = sum(1 for kw in topic["keywords"] if kw in msg_lower)
        if score > best_score:
            best_score = score
            best_topic = topic

    if best_topic and best_score > 0:
        # Return in the user's language; fall back to English if translation missing
        responses = best_topic["responses"]
        return responses.get(language, responses.get("en", ""))

    # ── Also try the original English knowledge base as backup ─────────────
    for entry in _KNOWLEDGE_BASE:
        score = sum(1 for kw in entry["keywords"] if kw in msg_lower)
        if score > best_score:
            best_score = score
            best_topic = entry

    if best_topic and best_score > 0 and "response" in best_topic:
        return best_topic["response"]

    # ── Language-native fallback ───────────────────────────────────────────
    fallback_template = _NATIVE_FALLBACK.get(language, _NATIVE_FALLBACK["en"])
    return fallback_template.format(message=message)


def analyze_evidence(text_content: str, evidence_type: str) -> str:
    """Analyze uploaded evidence content."""
    if MOCK_MODE:
        return f"""📄 **Evidence Analysis Report**

**Type:** {evidence_type.upper()}
**Analysis Date:** Auto-generated

**Key Findings:**
- Document has been processed and text extracted
- Content appears relevant to the case
- No signs of digital tampering detected in metadata

**Extracted Information:**
- Document contains {len(text_content.split())} words
- Language: English
- Relevant keywords identified

**Recommendations:**
- Cross-reference with other evidence in the case
- Verify authenticity through forensic examination
- Preserve original document in evidence locker

**Confidence Score:** 85%"""
    
    system_prompt = """Analyze the following evidence content and provide a detailed analysis report 
    including key findings, relevant information, and recommendations."""
    return _ai_call(system_prompt, f"Evidence Type: {evidence_type}\nContent: {text_content[:3000]}")


def _mock_response(system_prompt: str, user_prompt: str) -> str:
    """Fallback mock response when no AI API key is configured."""
    return "AI response would be generated here with OpenAI API. Please configure OPENAI_API_KEY."


# ─── Enhanced AI Features ──────────────────────────────────────────────────────

_LANDMARK_JUDGMENTS = {
    "cybercrime": [
        {"case": "Shreya Singhal v. Union of India (2015)", "court": "Supreme Court of India", "citation": "AIR 2015 SC 1523", "significance": "Struck down Section 66A IT Act as unconstitutional. Landmark judgment on online free speech and cyber laws.", "url": "https://indiankanoon.org/doc/110813550/"},
        {"case": "Anvar P.V. v. P.K. Basheer (2014)", "court": "Supreme Court of India", "citation": "(2014) 10 SCC 473", "significance": "Established mandatory Section 65B certificate for admissibility of electronic evidence. Landmark for digital evidence.", "url": "https://indiankanoon.org/doc/56221078/"},
        {"case": "Gagan Harsh Sharma v. State of Maharashtra (2019)", "court": "Bombay High Court", "citation": "2019 SCC OnLine Bom 3226", "significance": "Clarified distinction between hacking and unauthorized access. Important for cybercrime investigations.", "url": "https://indiankanoon.org/doc/76155609/"},
    ],
    "fraud": [
        {"case": "K. Satwant Singh v. Punjab National Bank (1979)", "court": "Supreme Court of India", "citation": "AIR 1980 SC 1275", "significance": "Established key principles of cheating under Section 420 IPC — deceitful intent and inducement required.", "url": "https://indiankanoon.org/doc/1483148/"},
        {"case": "Hira Lal Hari Lal Bhagwati v. C.B.I. (2003)", "court": "Supreme Court of India", "citation": "AIR 2003 SC 4257", "significance": "Distinguished criminal breach of trust (406 IPC) from civil dispute. Essential for white-collar crime cases.", "url": "https://indiankanoon.org/doc/1399941/"},
        {"case": "S.W. Palanitkar v. State of Bihar (2002)", "court": "Supreme Court of India", "citation": "AIR 2002 SC 1975", "significance": "Defined elements of cheating — false representation and fraudulent inducement.", "url": "https://indiankanoon.org/doc/1050571/"},
    ],
    "murder": [
        {"case": "Bachan Singh v. State of Punjab (1980)", "court": "Supreme Court of India", "citation": "AIR 1980 SC 898", "significance": "Established 'rarest of rare' doctrine for death penalty. Landmark for all murder cases involving capital punishment.", "url": "https://indiankanoon.org/doc/1090484/"},
        {"case": "Machhi Singh v. State of Punjab (1983)", "court": "Supreme Court of India", "citation": "AIR 1983 SC 957", "significance": "Elaborated on 'rarest of rare' doctrine — five categories where death penalty is appropriate.", "url": "https://indiankanoon.org/doc/1499055/"},
        {"case": "Sharad Birdhichand Sarda v. State of Maharashtra (1984)", "court": "Supreme Court of India", "citation": "AIR 1984 SC 1622", "significance": "Five golden principles for circumstantial evidence in murder cases. Essential reference.", "url": "https://indiankanoon.org/doc/1499055/"},
    ],
    "theft": [
        {"case": "Pyare Lal Bhargava v. State of Rajasthan (1963)", "court": "Supreme Court of India", "citation": "AIR 1963 SC 1094", "significance": "Defined 'dishonest intention' in theft. Established that temporary taking is also theft.", "url": "https://indiankanoon.org/doc/1413536/"},
        {"case": "Om Prakash v. State of Rajasthan (2012)", "court": "Supreme Court of India", "citation": "(2012) 5 SCC 201", "significance": "Chain snatching held to be robbery under Section 390 IPC — sudden force used during theft.", "url": "https://indiankanoon.org/doc/138268/"},
    ],
    "assault": [
        {"case": "State of Andhra Pradesh v. M. Sobhan Babu (2011)", "court": "Supreme Court of India", "citation": "(2011) 11 SCC 234", "significance": "Laid down distinction between hurt (319 IPC) and grievous hurt (320 IPC). Important for injury cases.", "url": "https://indiankanoon.org/doc/1671543/"},
    ],
    "domestic_violence": [
        {"case": "Arnesh Kumar v. State of Bihar (2014)", "court": "Supreme Court of India", "citation": "(2014) 8 SCC 273", "significance": "Guidelines for arrest under Section 498A IPC. Mandatory checklist before arrest in domestic violence cases.", "url": "https://indiankanoon.org/doc/89485/"},
        {"case": "V.D. Bhanot v. Savita Bhanot (2012)", "court": "Supreme Court of India", "citation": "(2012) 3 SCC 183", "significance": "Defined 'shared household' under Domestic Violence Act — women can continue residing in matrimonial home.", "url": "https://indiankanoon.org/doc/1578097/"},
    ],
    "sexual_harassment": [
        {"case": "Vishaka v. State of Rajasthan (1997)", "court": "Supreme Court of India", "citation": "AIR 1997 SC 3011", "significance": "Laid down 'Vishaka Guidelines' — basis of POSH Act 2013. Landmark on sexual harassment at workplace.", "url": "https://indiankanoon.org/doc/1031794/"},
        {"case": "Mukesh v. State (NCT of Delhi) (2017)", "court": "Supreme Court of India", "citation": "(2017) 6 SCC 1", "significance": "Nirbhaya case — upheld death penalty for gang rape and murder. Landmark for sexual violence law.", "url": "https://indiankanoon.org/doc/81742033/"},
    ],
    "kidnapping": [
        {"case": "Vikram Singh v. Union of India (2015)", "court": "Supreme Court of India", "citation": "(2015) 9 SCC 502", "significance": "Upheld constitutional validity of Section 364A IPC (kidnapping for ransom). Death penalty can be awarded.", "url": "https://indiankanoon.org/doc/18879139/"},
    ],
    "drug_offense": [
        {"case": "Union of India v. Bal Mukund Shah (2008)", "court": "Supreme Court of India", "citation": "(2008) 3 SCC 737", "significance": "Reversed burden of proof under NDPS Act — accused must prove innocence once possession proved.", "url": "https://indiankanoon.org/doc/1413536/"},
    ],
}

_NLP_KEYWORDS = {
    "cybercrime": ["hack", "phish", "otp", "upi", "fraud", "online", "cyber", "digital", "internet", "password", "account", "bank transfer", "ransomware", "malware", "data breach", "dark web"],
    "theft": ["steal", "stolen", "theft", "rob", "burglary", "pickpocket", "snatch", "loot", "dacoity", "missing item", "chain snatching"],
    "fraud": ["cheat", "deceive", "scam", "invest", "ponzi", "fake", "forged", "document fraud", "insurance fraud", "property fraud"],
    "assault": ["beat", "hit", "punch", "attack", "assault", "fight", "wound", "injury", "hurt", "stab", "knife"],
    "murder": ["kill", "murder", "dead body", "death", "poison", "strangle", "shoot", "gunshot", "homicide"],
    "kidnapping": ["kidnap", "abduct", "missing person", "ransom", "hostage", "taken away"],
    "domestic_violence": ["husband", "wife", "dowry", "domestic", "family violence", "matrimonial", "spouse abuse"],
    "sexual_harassment": ["rape", "molestation", "sexual assault", "harassment", "eve teasing", "stalking", "obscene", "indecent"],
    "drug_offense": ["drug", "narcotic", "cocaine", "heroin", "ganja", "mdma", "contraband", "smuggle"],
    "property_crime": ["property", "encroach", "land grab", "illegal construction", "damage property", "arson"],
    "white_collar": ["embezzle", "bribery", "corruption", "money laundering", "tax evasion", "insider trading"],
}

_TRANSLATIONS = {
    "hi": {
        "FIR Number": "एफआईआर संख्या",
        "Status": "स्थिति",
        "Priority": "प्राथमिकता",
        "Case Description": "मामले का विवरण",
        "Legal Sections": "कानूनी धाराएं",
        "Investigation Steps": "जांच के चरण",
        "Evidence Required": "आवश्यक साक्ष्य",
        "Filed": "दर्ज",
        "Under Investigation": "जांच के अधीन",
        "Closed": "बंद",
        "Critical": "अत्यंत महत्वपूर्ण",
        "High": "उच्च",
        "Medium": "मध्यम",
        "Low": "निम्न",
        "Complainant": "शिकायतकर्ता",
        "Police Station": "पुलिस स्टेशन",
    },
    "ta": {
        "FIR Number": "எஃப்ஐஆர் எண்",
        "Status": "நிலை",
        "Priority": "முன்னுரிமை",
        "Case Description": "வழக்கு விவரம்",
        "Filed": "தாக்கல் செய்யப்பட்டது",
        "Closed": "மூடப்பட்டது",
    },
    "te": {
        "FIR Number": "ఎఫ్ఐఆర్ సంఖ్య",
        "Status": "స్థితి",
        "Priority": "ప్రాధాన్యత",
        "Filed": "దాఖలు చేయబడింది",
        "Closed": "మూసివేయబడింది",
    },
    "bn": {
        "FIR Number": "এফআইআর নম্বর",
        "Status": "অবস্থা",
        "Priority": "অগ্রাধিকার",
        "Filed": "দাখিল করা হয়েছে",
        "Closed": "বন্ধ",
    },
    "mr": {
        "FIR Number": "एफआयआर क्रमांक",
        "Status": "स्थिती",
        "Priority": "प्राधान्य",
        "Filed": "दाखल",
        "Closed": "बंद",
    },
}


def get_landmark_judgments(category: str, sections: list = None) -> list:
    """Get landmark Supreme Court / High Court judgments for a case category."""
    judgments = _LANDMARK_JUDGMENTS.get(category, [])
    
    # Also try to match based on sections
    if sections and not judgments:
        for sec in sections:
            s = sec.get("section", "").lower() if isinstance(sec, dict) else str(sec).lower()
            if "murder" in s or "302" in s or "101" in s:
                judgments.extend(_LANDMARK_JUDGMENTS.get("murder", []))
            elif "theft" in s or "379" in s or "303" in s:
                judgments.extend(_LANDMARK_JUDGMENTS.get("theft", []))

    if not judgments:
        # Return general landmark cases on evidence and FIR
        judgments = [
            {"case": "Lalita Kumari v. Govt. of U.P. (2014)", "court": "Supreme Court of India", "citation": "(2014) 2 SCC 1", "significance": "Mandatory FIR registration — police cannot refuse to register an FIR for cognizable offences.", "url": "https://indiankanoon.org/doc/88685537/"},
            {"case": "D.K. Basu v. State of West Bengal (1997)", "court": "Supreme Court of India", "citation": "AIR 1997 SC 610", "significance": "Guidelines for arrest and detention. Established rights of arrested persons. Mandatory reading for all police officers.", "url": "https://indiankanoon.org/doc/501198/"},
            {"case": "Joginder Kumar v. State of U.P. (1994)", "court": "Supreme Court of India", "citation": "AIR 1994 SC 1349", "significance": "Right against arbitrary arrest. Established guidelines for arrest — not to be made merely because it is lawful.", "url": "https://indiankanoon.org/doc/1706811/"},
        ]

    return judgments[:5]


def classify_crime_nlp(text: str) -> dict:
    """NLP-based crime classification from free text with confidence scores."""
    if not text:
        return {"category": "other", "confidence": 0.0, "all_scores": {}}

    text_lower = text.lower()
    scores = {}

    for category, keywords in _NLP_KEYWORDS.items():
        score = sum(2 if kw in text_lower else 0 for kw in keywords)
        # Partial match bonus
        score += sum(0.5 for kw in keywords if any(k in text_lower for k in kw.split()))
        scores[category] = round(score, 2)

    if not any(v > 0 for v in scores.values()):
        return {"category": "other", "confidence": 0.5, "all_scores": scores}

    best_category = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    confidence = round(min(scores[best_category] / total, 1.0), 2)

    return {
        "category": best_category,
        "confidence": confidence,
        "all_scores": {k: round(v / total, 2) for k, v in sorted(scores.items(), key=lambda x: -x[1]) if v > 0},
        "top_matches": sorted([(k, round(v / total, 2)) for k, v in scores.items() if v > 0], key=lambda x: -x[1])[:3]
    }


def translate_ui_label(text: str, lang: str) -> str:
    """Translate common UI labels to supported languages."""
    if lang == "en" or lang not in _TRANSLATIONS:
        return text
    return _TRANSLATIONS[lang].get(text, text)


def get_multilingual_guidance(topic: str, lang: str = "en") -> str:
    """Get victim guidance in multiple Indian languages."""
    if lang == "hi":
        guidance_map = {
            "fir": "🇮🇳 **प्राथमिकी (FIR) कैसे दर्ज करें:**\n\n1. निकटतम पुलिस स्टेशन जाएं\n2. अपनी शिकायत लिखित या मौखिक रूप से दें\n3. पुलिस अधिकारी एफआईआर दर्ज करेगा\n4. एफआईआर की एक प्रति निःशुल्क प्राप्त करें\n\n**आपके अधिकार:**\n- पुलिस एफआईआर दर्ज करने से मना नहीं कर सकती\n- शून्य एफआईआर किसी भी थाने में दर्ज करा सकते हैं\n- एफआईआर की एक प्रति मुफ्त में मांगें\n\n**हेल्पलाइन:** आपातकाल: 112 | महिला: 181 | साइबर अपराध: 1930",
            "rights": "⚖️ **पीड़ित के अधिकार:**\n\n1. एफआईआर दर्ज कराने का अधिकार (धारा 173 BNSS)\n2. मुफ्त कानूनी सहायता का अधिकार\n3. केस की प्रगति जानने का अधिकार\n4. महिला अधिकारी की उपस्थिति का अधिकार\n5. मुआवजे का अधिकार\n\nNALSA हेल्पलाइन: 15100",
        }
        return guidance_map.get(topic, f"🇮🇳 कृपया पुलिस हेल्पलाइन 112 पर कॉल करें या निकटतम थाने जाएं।")
    
    elif lang == "ta":
        guidance_map = {
            "fir": "🇮🇳 **FIR பதிவு செய்வது எப்படி:**\n\n1. அருகிலுள்ள காவல் நிலையத்திற்கு செல்லுங்கள்\n2. உங்கள் புகாரை எழுத்தில் அல்லது வாய்மொழியாக கொடுங்கள்\n3. FIR-ன் இலவச நகலை பெறுங்கள்\n\nதொலைபேசி: அவசரகாலம்: 112 | மகளிர்: 181",
        }
        return guidance_map.get(topic, f"🇮🇳 காவல் உதவி வரியில் 112 அழைக்கவும்.")

    # Default English
    return ""
