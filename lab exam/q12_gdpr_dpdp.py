"""
Experiment 12: Case Study on GDPR and DPDP Act 2023
Create a comparative chart of GDPR and DPDP Act 2023 principles and
explain roles like Data Protection Officer (DPO). Include a mock
incident report format.
"""
import datetime

COMPARISON_ROWS = [
    ("Jurisdiction", "European Union", "India"),
    ("Key Role", "Data Protection Officer (DPO) - mandatory for large-scale processing", "DPO - mandatory for Significant Data Fiduciaries"),
    ("Consent", "Explicit, granular consent required", "Clear, informed, specific consent required"),
    ("Breach Notification", "72 hours to supervisory authority", "To Data Protection Board 'without delay'"),
    ("Penalties", "Up to EUR 20M or 4% global turnover", "Up to INR 250 crore per instance"),
    ("Data Subject Rights", "Access, rectify, erase, portability, object", "Access, correction, erasure, grievance redressal"),
    ("Scope", "Applies to EU residents' data globally", "Applies to digital personal data of Indian residents"),
]

for aspect, gdpr, dpdp in COMPARISON_ROWS:
    print(f"\n{aspect}")
    print(f"  GDPR         : {gdpr}")
    print(f"  DPDP Act 2023: {dpdp}")

print("""
Role of the Data Protection Officer (DPO):
Under both laws, the DPO is the person responsible for overseeing an
organization's data protection strategy - monitoring compliance,
handling data subject/principal requests, acting as the contact point
for the regulator, and advising on data protection impact assessments.
""")

# Mock incident report format
report = f"""DATA BREACH INCIDENT REPORT (Mock)
Date/Time Reported : {datetime.datetime.now()}
Incident ID         : INC-{datetime.datetime.now():%Y%m%d%H%M}
Reported By         : DPO - Data Protection Officer
Nature of Breach     : Unauthorized access to customer database
Data Affected        : Names, emails (approx. 500 records)
Systems Affected     : Customer CRM server
Containment Actions  : Access revoked, affected server isolated
Notification Status  : Regulator notified per GDPR/DPDP timelines
Root Cause           : Weak access-control misconfiguration
Remediation Plan     : Rotate credentials, enable MFA, audit logs
"""
print(report)
