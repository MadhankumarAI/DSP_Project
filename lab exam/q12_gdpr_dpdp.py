"""Q12: GDPR vs DPDP Act 2023 comparative chart + mock data-breach incident report generator."""
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

COMPARISON_ROWS = [
    ("Jurisdiction", "European Union", "India"),
    ("Key Role", "Data Protection Officer (DPO) - mandatory for large-scale processing", "DPO - mandatory for Significant Data Fiduciaries"),
    ("Consent", "Explicit, granular consent required", "Clear, informed, specific consent required"),
    ("Breach Notification", "72 hours to supervisory authority", "To Data Protection Board 'without delay'"),
    ("Penalties", "Up to EUR 20M or 4% global turnover", "Up to INR 250 crore per instance"),
    ("Data Subject Rights", "Access, rectify, erase, portability, object", "Access, correction, erasure, grievance redressal"),
    ("Scope", "Applies to EU residents' data globally", "Applies to digital personal data of Indian residents"),
]

def show_comparison_chart():
    window = tk.Toplevel(root)
    window.title("GDPR vs DPDP Act 2023")
    tree = ttk.Treeview(window, columns=("Aspect", "GDPR", "DPDP Act 2023"), show="headings", height=8)
    for column, width in (("Aspect", 160), ("GDPR", 260), ("DPDP Act 2023", 260)):
        tree.heading(column, text=column)
        tree.column(column, width=width)
    for row in COMPARISON_ROWS:
        tree.insert("", tk.END, values=row)
    tree.pack(fill="both", expand=True, padx=8, pady=8)

def generate_incident_report():
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
    path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="incident_report.txt")
    if path:
        with open(path, "w") as f:
            f.write(report)
        messagebox.showinfo("Saved", "Mock incident report saved.")

root = tk.Tk()
root.title("Q12 - GDPR vs DPDP Act 2023")
root.geometry("320x160")

ttk.Button(root, text="Show Comparative Chart", command=show_comparison_chart).pack(pady=10)
ttk.Button(root, text="Generate Mock Incident Report", command=generate_incident_report).pack(pady=10)

root.mainloop()
