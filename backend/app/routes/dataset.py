"""Dataset seeding and legal sections API routes."""
import json
import os
import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import (
    User, UserRole, Case, CaseStatus, CasePriority, CrimeCategory,
    TimelineEvent, Evidence, EvidenceType
)
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/dataset", tags=["Dataset"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _gen_fir():
    year = datetime.now().year
    num = ''.join(random.choices(string.digits, k=6))
    return f"FIR/{year}/{num}"


SAMPLE_FIRS = [
    {
        "title": "Online Banking Fraud via OTP Phishing",
        "description": "The complainant reports that on 15th May 2026 at approximately 2:30 PM, they received a call from an unknown person posing as a bank official. The caller stated that the complainant's debit card would be blocked and requested OTP verification. After sharing the OTP, the complainant found that Rs. 85,000 was debited from their account via multiple UPI transactions.",
        "category": CrimeCategory.CYBERCRIME,
        "priority": CasePriority.HIGH,
        "status": CaseStatus.UNDER_INVESTIGATION,
        "incident_location": "Connaught Place, New Delhi",
        "police_station": "Cybercrime Police Station, New Delhi",
        "ai_legal_sections": [
            {"section": "Section 66C IT Act", "description": "Identity theft", "penalty": "Up to 3 years + ₹1L fine"},
            {"section": "Section 66D IT Act", "description": "Cheating by personation using computer resource", "penalty": "Up to 3 years + ₹1L fine"},
            {"section": "Section 318(4) BNS", "description": "Cheating (formerly Section 420 IPC)", "penalty": "Up to 7 years + fine"},
            {"section": "Section 111 BNS", "description": "Organised crime", "penalty": "Up to 7 years + fine"}
        ],
        "ai_investigation_steps": [
            "Freeze the transaction with bank immediately",
            "Obtain call detail records (CDR) from telecom provider",
            "Trace UPI ID linked to fraudulent transactions",
            "Issue notice to payment gateway for KYC details",
            "Analyze IP logs from bank server",
            "Check CCTNS for similar MO cases"
        ],
        "ai_required_evidence": [
            "Bank statement showing fraudulent transactions",
            "Call recording or call log",
            "Screenshots of OTP messages",
            "Aadhaar/KYC documents of fraudster's UPI account",
            "IP address logs from bank"
        ],
        "ai_fir_text": "FIRST INFORMATION REPORT\nUnder Section 154 BNSS (Formerly Section 154 CrPC)\n\nDate: 15/05/2026 | P.S.: Cybercrime PS, New Delhi | FIR No.: Auto-Generated\n\nComplainant: [Complainant Name]\nIncident: Online Banking Fraud via OTP Phishing\n\nThe complainant states that on 15.05.2026 at 14:30 hrs, an unknown person called on complainant's mobile claiming to be a bank officer. The accused obtained OTP and fraudulently transferred Rs. 85,000/- from complainant's account to unknown accounts via UPI. Applicable sections: 66C, 66D IT Act; Section 318(4) BNS. Investigation initiated.",
        "timeline_events": [
            {"title": "Complaint Filed", "event_type": "complaint", "days_ago": 3},
            {"title": "FIR Registered", "event_type": "fir", "days_ago": 3},
            {"title": "CDR Obtained from Telecom", "event_type": "investigation", "days_ago": 2},
            {"title": "Bank Account Traced", "event_type": "investigation", "days_ago": 1}
        ]
    },
    {
        "title": "Residential Burglary with House Breaking",
        "description": "The complainant reports that on the night of 12th May 2026, unknown persons broke into their residential flat at Sector 15, Gurugram by breaking the window latch. The thieves stole gold jewellery worth approximately Rs. 3.5 lakhs, a laptop, two mobile phones, and cash of Rs. 25,000. The incident was discovered at 6 AM on 13th May when the family returned from an outstation trip.",
        "category": CrimeCategory.THEFT,
        "priority": CasePriority.HIGH,
        "status": CaseStatus.EVIDENCE_COLLECTION,
        "incident_location": "Sector 15, Gurugram, Haryana",
        "police_station": "Sector 14 Police Station, Gurugram",
        "ai_legal_sections": [
            {"section": "Section 331(4) BNS", "description": "House breaking by night (formerly Section 457 IPC)", "penalty": "Up to 14 years + fine"},
            {"section": "Section 305 BNS", "description": "Theft (formerly Section 379 IPC)", "penalty": "Up to 3 years + fine"},
            {"section": "Section 317 BNS", "description": "Receiving stolen property (formerly Section 411 IPC)", "penalty": "Up to 3 years + fine"}
        ],
        "ai_investigation_steps": [
            "Preserve crime scene — no cleaning before forensic team visit",
            "Collect CCTV footage from building and surrounding areas",
            "Record statements of neighbors and security guard",
            "Send fingerprint evidence to FSL",
            "Check pawn shops and second-hand electronics dealers",
            "Trace stolen phone IMEI via CEIR portal"
        ],
        "ai_required_evidence": [
            "Purchase invoices for stolen gold jewellery",
            "CCTV footage from building entrance",
            "Fingerprints from point of entry",
            "Mobile IMEI numbers for CEIR tracking",
            "Witness statements of neighbors"
        ],
        "ai_fir_text": "FIR registered for house-breaking and theft. Forensic team dispatched to collect fingerprints and other physical evidence from the scene.",
        "timeline_events": [
            {"title": "Burglary Discovered", "event_type": "complaint", "days_ago": 7},
            {"title": "FIR Registered", "event_type": "fir", "days_ago": 7},
            {"title": "Forensic Team Visited", "event_type": "investigation", "days_ago": 6},
            {"title": "CCTV Footage Collected", "event_type": "evidence", "days_ago": 5},
            {"title": "IMEI Reported to CEIR", "event_type": "investigation", "days_ago": 4}
        ]
    },
    {
        "title": "Domestic Violence and Physical Assault",
        "description": "The complainant, a 32-year-old woman, reports that her husband has been physically assaulting her for the past 6 months. On 10th May 2026, during an argument over household expenses, the accused punched the complainant on her face, causing a fracture to her nose and multiple bruises on her arms. The complainant managed to escape to her parents' home and is seeking protection and legal action.",
        "category": CrimeCategory.DOMESTIC_VIOLENCE,
        "priority": CasePriority.CRITICAL,
        "status": CaseStatus.FILED,
        "incident_location": "Malviya Nagar, New Delhi",
        "police_station": "Malviya Nagar Police Station",
        "ai_legal_sections": [
            {"section": "Section 115(2) BNS", "description": "Voluntarily causing grievous hurt (formerly Section 325 IPC)", "penalty": "Up to 7 years + fine"},
            {"section": "Section 85 BNS", "description": "Husband/relatives subjecting woman to cruelty (formerly Section 498A IPC)", "penalty": "Up to 3 years + fine"},
            {"section": "Domestic Violence Act 2005 Section 3", "description": "Domestic violence — physical, mental, economic abuse", "penalty": "Protection order + compensation"},
            {"section": "Section 74 BNS", "description": "Assault or use of criminal force on woman (formerly Section 354 IPC)", "penalty": "1-5 years + fine"}
        ],
        "ai_investigation_steps": [
            "Record victim's statement urgently with woman officer present",
            "Refer victim to Government hospital for medical examination",
            "Obtain medical certificate documenting injuries",
            "Issue protection order application under DV Act",
            "Record statements of neighbors and family members",
            "Seize any weapons used in assault"
        ],
        "ai_required_evidence": [
            "Medical examination certificate with injury details",
            "Photographs of injuries",
            "Witness statements of neighbors",
            "Previous complaint records if any",
            "Mobile call records showing threats"
        ],
        "ai_fir_text": "Urgent FIR registered for domestic violence and assault. Victim referred to One Stop Centre. Protection order application initiated.",
        "timeline_events": [
            {"title": "Incident Occurred", "event_type": "complaint", "days_ago": 10},
            {"title": "Victim Filed Complaint", "event_type": "complaint", "days_ago": 9},
            {"title": "FIR Registered", "event_type": "fir", "days_ago": 9},
            {"title": "Medical Examination Conducted", "event_type": "investigation", "days_ago": 8},
            {"title": "Protection Order Applied", "event_type": "legal", "days_ago": 7}
        ]
    },
    {
        "title": "Investment Fraud — Ponzi Scheme",
        "description": "The complainant invested Rs. 8 lakhs in what was presented as a high-return cryptocurrency investment scheme operated by a company named 'CryptoWealth Solutions'. The accused promised 40% returns in 3 months. After 2 months, all contact was lost. Investigation revealed the company was a sham with no physical office. Approximately 50 other victims have been identified.",
        "category": CrimeCategory.FRAUD,
        "priority": CasePriority.CRITICAL,
        "status": CaseStatus.UNDER_INVESTIGATION,
        "incident_location": "Bandra Kurla Complex, Mumbai",
        "police_station": "BKC Cybercrime Police Station, Mumbai",
        "ai_legal_sections": [
            {"section": "Section 318(4) BNS", "description": "Cheating — financial fraud (formerly Section 420 IPC)", "penalty": "Up to 7 years + fine"},
            {"section": "Section 316 BNS", "description": "Criminal breach of trust (formerly Section 406 IPC)", "penalty": "Up to 3 years + fine"},
            {"section": "Section 66D IT Act", "description": "Cheating by personation using online platforms", "penalty": "Up to 3 years + ₹1L fine"},
            {"section": "SEBI Act Section 12A", "description": "Fraudulent securities market activities", "penalty": "Up to 10 years + fine"}
        ],
        "ai_investigation_steps": [
            "Freeze all bank accounts linked to the accused company",
            "Obtain MCA records for company registration details",
            "Trace IP addresses used for online communication",
            "Contact all identified victims for coordinated FIR",
            "Approach SFIO (Serious Fraud Investigation Office)",
            "Issue Red Corner Notice if suspects flee abroad"
        ],
        "ai_required_evidence": [
            "Investment agreements and receipts",
            "Bank transfer records",
            "WhatsApp/email communications with accused",
            "Company registration documents",
            "Victim testimonies"
        ],
        "ai_fir_text": "FIR registered for large-scale investment fraud. Economic offences wing consulted. Bank accounts frozen.",
        "timeline_events": [
            {"title": "Fraud Discovered", "event_type": "complaint", "days_ago": 15},
            {"title": "First Victim Filed FIR", "event_type": "fir", "days_ago": 14},
            {"title": "Bank Accounts Frozen", "event_type": "investigation", "days_ago": 13},
            {"title": "50 Victims Identified", "event_type": "investigation", "days_ago": 10},
            {"title": "Company Records Seized", "event_type": "evidence", "days_ago": 7}
        ]
    },
    {
        "title": "Cyberstalking and Online Harassment",
        "description": "The complainant, a 26-year-old IT professional, reports being stalked online by a former colleague. The accused has been creating fake social media profiles using the complainant's photos and sharing morphed images. The accused has also been sending threatening messages from multiple phone numbers and email IDs, demanding a meeting and threatening to harm the complainant if refused.",
        "category": CrimeCategory.SEXUAL_HARASSMENT,
        "priority": CasePriority.HIGH,
        "status": CaseStatus.FILED,
        "incident_location": "Koramangala, Bengaluru",
        "police_station": "CEN (Cybercrime, Economic and Narcotic) PS, Bengaluru",
        "ai_legal_sections": [
            {"section": "Section 78 BNS", "description": "Cyberstalking (formerly Section 354D IPC)", "penalty": "Up to 3 years + fine (first conviction)"},
            {"section": "Section 351(2) BNS", "description": "Criminal intimidation (formerly Section 506 IPC)", "penalty": "Up to 7 years + fine"},
            {"section": "Section 67 IT Act", "description": "Publishing obscene material in electronic form", "penalty": "Up to 5 years + ₹10L fine"},
            {"section": "Section 66E IT Act", "description": "Violation of privacy", "penalty": "Up to 3 years + ₹2L fine"}
        ],
        "ai_investigation_steps": [
            "Preserve all evidence — screenshots, message logs, profile URLs",
            "Request social media platforms to preserve account data",
            "Obtain IP address logs from social media companies",
            "Issue legal notices to social media platforms for user data",
            "Analyze phone numbers — trace via telecom providers",
            "Apply for anticipatory bail if suspect is known"
        ],
        "ai_required_evidence": [
            "Screenshots of all harassing messages and fake profiles",
            "Proof of morphed images",
            "Call logs showing threatening calls",
            "Social media platform URLs",
            "Email headers from threatening emails"
        ],
        "ai_fir_text": "FIR registered for cyberstalking. Victim provided safety guidelines. Social media evidence preservation initiated.",
        "timeline_events": [
            {"title": "Harassment Started", "event_type": "complaint", "days_ago": 30},
            {"title": "Formal Complaint Filed", "event_type": "complaint", "days_ago": 5},
            {"title": "FIR Registered", "event_type": "fir", "days_ago": 4},
            {"title": "Social Media Evidence Preserved", "event_type": "evidence", "days_ago": 3}
        ]
    }
]


@router.post("/seed")
async def seed_sample_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seed the database with sample FIRs and legal documents for demo purposes."""
    if current_user.role not in [UserRole.ADMIN, UserRole.OFFICER]:
        raise HTTPException(status_code=403, detail="Only officers and admins can seed data")

    created_cases = []
    now = datetime.utcnow()

    for sample in SAMPLE_FIRS:
        case = Case(
            title=sample["title"],
            description=sample["description"],
            category=sample["category"],
            priority=sample["priority"],
            status=sample["status"],
            incident_location=sample.get("incident_location"),
            police_station=sample.get("police_station"),
            complainant_id=current_user.id,
            fir_number=_gen_fir(),
            filed_at=now - timedelta(days=sample["timeline_events"][0]["days_ago"]),
            ai_fir_text=sample.get("ai_fir_text", ""),
            ai_legal_sections=sample.get("ai_legal_sections", []),
            ai_investigation_steps=sample.get("ai_investigation_steps", []),
            ai_required_evidence=sample.get("ai_required_evidence", []),
            ai_priority_reasoning=f"AI classified as {sample['priority'].value} based on crime category and description keywords."
        )
        db.add(case)
        db.flush()

        for evt_data in sample.get("timeline_events", []):
            evt = TimelineEvent(
                case_id=case.id,
                title=evt_data["title"],
                description=f"Recorded in case diary",
                event_date=now - timedelta(days=evt_data["days_ago"]),
                event_type=evt_data["event_type"],
                created_by=current_user.id,
                is_ai_generated=evt_data["event_type"] in ["fir", "legal"]
            )
            db.add(evt)

        created_cases.append({"id": str(case.id), "title": case.title, "fir_number": case.fir_number})

    db.commit()
    return {
        "message": f"Successfully seeded {len(created_cases)} sample FIRs",
        "cases": created_cases
    }


@router.get("/legal-sections")
async def get_legal_sections(
    act: str = None,
    search: str = None,
    category: str = None
):
    """Get BNS/BNSS/BSA legal sections with optional filtering."""
    sections = _load_json("legal_sections.json")
    if not sections:
        sections = _get_builtin_sections()

    if act:
        sections = [s for s in sections if s.get("act", "").upper() == act.upper()]
    if category:
        sections = [s for s in sections if category.lower() in s.get("crime_category", "").lower()]
    if search:
        q = search.lower()
        sections = [s for s in sections if
                    q in s.get("section", "").lower() or
                    q in s.get("description", "").lower() or
                    q in s.get("offence", "").lower()]

    return {"sections": sections[:100], "total": len(sections)}


@router.get("/sample-firs")
async def get_sample_firs():
    """Get anonymized sample FIR records for research/demo."""
    return {
        "firs": [
            {
                "category": s["category"].value,
                "title": s["title"],
                "priority": s["priority"].value,
                "legal_sections_count": len(s.get("ai_legal_sections", [])),
                "description_preview": s["description"][:200] + "..."
            }
            for s in SAMPLE_FIRS
        ]
    }


def _get_builtin_sections():
    """Built-in BNS/BNSS/BSA sections (fallback if JSON not found)."""
    return [
        # BNS (Bharatiya Nyaya Sanhita) — replaces IPC
        {"act": "BNS", "section": "Section 101", "offence": "Murder", "description": "Punishment for murder", "penalty": "Death or life imprisonment + fine", "old_section": "Section 302 IPC", "crime_category": "murder", "landmark_cases": ["Bachan Singh v. State of Punjab (1980)", "Machhi Singh v. State of Punjab (1983)"]},
        {"act": "BNS", "section": "Section 109", "offence": "Attempt to murder", "description": "Attempt to commit murder", "penalty": "Up to 10 years + fine", "old_section": "Section 307 IPC", "crime_category": "assault", "landmark_cases": ["State of Maharashtra v. Balram Bama Patil (1983)"]},
        {"act": "BNS", "section": "Section 115(2)", "offence": "Grievous hurt", "description": "Voluntarily causing grievous hurt", "penalty": "Up to 7 years + fine", "old_section": "Section 325 IPC", "crime_category": "assault", "landmark_cases": []},
        {"act": "BNS", "section": "Section 303", "offence": "Theft", "description": "Whoever intending to take dishonestly any moveable property commits theft", "penalty": "Up to 3 years + fine", "old_section": "Section 378/379 IPC", "crime_category": "theft", "landmark_cases": ["Pyare Lal Bhargava v. State of Rajasthan (1963)"]},
        {"act": "BNS", "section": "Section 309", "offence": "Robbery", "description": "Theft + hurt/wrongful restraint = robbery", "penalty": "Up to 10 years + fine", "old_section": "Section 392 IPC", "crime_category": "theft", "landmark_cases": []},
        {"act": "BNS", "section": "Section 310", "offence": "Dacoity", "description": "Robbery committed by 5 or more persons", "penalty": "Up to life imprisonment + fine", "old_section": "Section 395 IPC", "crime_category": "theft", "landmark_cases": []},
        {"act": "BNS", "section": "Section 316", "offence": "Criminal breach of trust", "description": "Dishonest misappropriation of entrusted property", "penalty": "Up to 3 years + fine", "old_section": "Section 406 IPC", "crime_category": "fraud", "landmark_cases": []},
        {"act": "BNS", "section": "Section 318(4)", "offence": "Cheating", "description": "Cheating involving delivery of property or valuable security", "penalty": "Up to 7 years + fine", "old_section": "Section 420 IPC", "crime_category": "fraud", "landmark_cases": ["Dr. S. Dutt v. State of U.P. (1966)"]},
        {"act": "BNS", "section": "Section 329", "offence": "Forgery", "description": "Making false document or electronic record", "penalty": "Up to 2 years + fine", "old_section": "Section 463 IPC", "crime_category": "fraud", "landmark_cases": []},
        {"act": "BNS", "section": "Section 64", "offence": "Rape", "description": "Sexual assault on a woman without consent", "penalty": "10 years to life + fine", "old_section": "Section 376 IPC", "crime_category": "sexual_harassment", "landmark_cases": ["Vishaka v. State of Rajasthan (1997)", "Nirbhaya Case — Mukesh v. State (NCT of Delhi) (2017)"]},
        {"act": "BNS", "section": "Section 74", "offence": "Assault on woman", "description": "Assault or criminal force to woman with intent to outrage her modesty", "penalty": "1-5 years + fine", "old_section": "Section 354 IPC", "crime_category": "sexual_harassment", "landmark_cases": []},
        {"act": "BNS", "section": "Section 78", "offence": "Stalking", "description": "Following, contacting or monitoring a woman against her will", "penalty": "1-3 years + fine (first conviction)", "old_section": "Section 354D IPC", "crime_category": "sexual_harassment", "landmark_cases": []},
        {"act": "BNS", "section": "Section 85", "offence": "Domestic violence", "description": "Husband or relatives subjecting woman to cruelty", "penalty": "Up to 3 years + fine", "old_section": "Section 498A IPC", "crime_category": "domestic_violence", "landmark_cases": ["Arnesh Kumar v. State of Bihar (2014)"]},
        {"act": "BNS", "section": "Section 137", "offence": "Kidnapping", "description": "Kidnapping from India or from lawful guardianship", "penalty": "Up to 7 years + fine", "old_section": "Section 363 IPC", "crime_category": "kidnapping", "landmark_cases": []},
        {"act": "BNS", "section": "Section 140(1)", "offence": "Kidnapping for ransom", "description": "Kidnapping for ransom or extortion", "penalty": "Death or life imprisonment + fine", "old_section": "Section 364A IPC", "crime_category": "kidnapping", "landmark_cases": []},
        {"act": "BNS", "section": "Section 351", "offence": "Criminal intimidation", "description": "Threatening another with injury to person, reputation or property", "penalty": "Up to 2 years + fine", "old_section": "Section 506 IPC", "crime_category": "assault", "landmark_cases": []},
        {"act": "BNS", "section": "Section 111", "offence": "Organised crime", "description": "Participation in organised criminal activity or gang", "penalty": "Up to 7 years / Death (if results in death)", "old_section": "MCOCA (state level)", "crime_category": "other", "landmark_cases": []},
        # IT Act
        {"act": "IT_ACT", "section": "Section 43", "offence": "Damage to computer systems", "description": "Unauthorized access, downloading, introducing virus, damage to computer systems", "penalty": "Compensation up to ₹1 crore (civil)", "old_section": "N/A", "crime_category": "cybercrime", "landmark_cases": []},
        {"act": "IT_ACT", "section": "Section 66", "offence": "Computer related offences", "description": "Dishonestly or fraudulently committing acts under Section 43", "penalty": "Up to 3 years + ₹5L fine", "old_section": "N/A", "crime_category": "cybercrime", "landmark_cases": []},
        {"act": "IT_ACT", "section": "Section 66C", "offence": "Identity theft", "description": "Fraudulently using another's electronic signature, password, or unique identification", "penalty": "Up to 3 years + ₹1L fine", "old_section": "N/A", "crime_category": "cybercrime", "landmark_cases": []},
        {"act": "IT_ACT", "section": "Section 66D", "offence": "Cheating by personation", "description": "Cheating by personating using a computer resource", "penalty": "Up to 3 years + ₹1L fine", "old_section": "N/A", "crime_category": "cybercrime", "landmark_cases": []},
        {"act": "IT_ACT", "section": "Section 66E", "offence": "Violation of privacy", "description": "Publishing private images of a person without consent", "penalty": "Up to 3 years + ₹2L fine", "old_section": "N/A", "crime_category": "cybercrime", "landmark_cases": []},
        {"act": "IT_ACT", "section": "Section 67", "offence": "Obscene material online", "description": "Publishing or transmitting obscene material in electronic form", "penalty": "Up to 5 years + ₹10L fine", "old_section": "N/A", "crime_category": "cybercrime", "landmark_cases": []},
        {"act": "IT_ACT", "section": "Section 67A", "offence": "Sexually explicit content", "description": "Publishing material containing sexually explicit act", "penalty": "Up to 7 years + ₹10L fine", "old_section": "N/A", "crime_category": "sexual_harassment", "landmark_cases": []},
        {"act": "IT_ACT", "section": "Section 67B", "offence": "Child pornography", "description": "Publishing material depicting children in obscene acts", "penalty": "Up to 7 years + ₹10L fine", "old_section": "N/A", "crime_category": "other", "landmark_cases": []},
        # BNSS (procedural)
        {"act": "BNSS", "section": "Section 173", "offence": "FIR registration", "description": "Every information about cognizable offence to be recorded as FIR", "penalty": "N/A (procedural)", "old_section": "Section 154 CrPC", "crime_category": "all", "landmark_cases": ["Lalita Kumari v. Govt. of U.P. (2014)"]},
        {"act": "BNSS", "section": "Section 187", "offence": "Remand", "description": "Accused to be produced before Magistrate within 24 hours; remand provisions", "penalty": "N/A (procedural)", "old_section": "Section 167 CrPC", "crime_category": "all", "landmark_cases": []},
        {"act": "BNSS", "section": "Section 480", "offence": "Bail in bailable offences", "description": "Right to bail in bailable offences", "penalty": "N/A (procedural)", "old_section": "Section 436 CrPC", "crime_category": "all", "landmark_cases": []},
        {"act": "BNSS", "section": "Section 482", "offence": "Anticipatory bail", "description": "Direction to grant bail to person apprehending arrest", "penalty": "N/A (procedural)", "old_section": "Section 438 CrPC", "crime_category": "all", "landmark_cases": ["Gurbaksh Singh Sibbia v. State of Punjab (1980)"]},
        # BSA
        {"act": "BSA", "section": "Section 57", "offence": "Electronic records", "description": "Electronic records and digital evidence admissibility", "penalty": "N/A (evidentiary)", "old_section": "Section 65B IEA", "crime_category": "cybercrime", "landmark_cases": ["Anvar P.V. v. P.K. Basheer (2014)"]},
        {"act": "BSA", "section": "Section 26", "offence": "Confession to police officer", "description": "Confessions made to police officers — admissibility rules", "penalty": "N/A (evidentiary)", "old_section": "Section 25 IEA", "crime_category": "all", "landmark_cases": []},
    ]
