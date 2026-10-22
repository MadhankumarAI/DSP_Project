"""
Experiment 11:
a) Identifying and Classifying PII Data - Given a dataset, classify
   data into types (structured/unstructured), states (in-transit,
   at-rest, in-use), and highlight PII elements.
b) Anonymization with k-Anonymity - Use a sample dataset with PII
   (like healthcare data). Apply anonymity using Python. Compare &
   evaluate re-identification risk before and after anonymization.
"""
import csv
import re

PII_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "phone": re.compile(r"\b\d{10}\b"),
    "ssn/aadhaar": re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{12}\b"),
    "name": re.compile(r"^[A-Z][a-z]+ [A-Z][a-z]+$"),
}

def classify_columns(rows, header):
    classification = {}
    for col_index, column in enumerate(header):
        sample_values = [row[col_index] for row in rows if len(row) > col_index][:10]
        matched_type = next(
            (pii_name for pii_name, pattern in PII_PATTERNS.items() if any(pattern.search(v) for v in sample_values)),
            "non-PII",
        )
        classification[column] = matched_type
    return classification

def apply_k_anonymity(rows, header, quasi_columns):
    column_indexes = [header.index(c) for c in quasi_columns]
    anonymized_rows = [row[:] for row in rows]
    for col_index in column_indexes:
        col_name = header[col_index].lower()
        for row in anonymized_rows:
            if "age" in col_name and row[col_index].isdigit():
                bucket_start = (int(row[col_index]) // 10) * 10
                row[col_index] = f"{bucket_start}-{bucket_start + 9}"  # generalize age -> bucket
            elif "zip" in col_name or "pin" in col_name:
                row[col_index] = row[col_index][:3] + "**"             # truncate zip/pincode
    return anonymized_rows

def reidentification_risk(rows, header, quasi_columns):
    column_indexes = [header.index(c) for c in quasi_columns]
    combinations = [tuple(row[i] for i in column_indexes) for row in rows]
    return len(set(combinations))  # fewer unique combos = lower re-identification risk

# a) Load dataset & classify PII columns
path = input("Enter path of CSV dataset: ")
with open(path, newline="", encoding="utf-8") as f:
    data = list(csv.reader(f))
header, rows = data[0], data[1:]

classification = classify_columns(rows, header)
print("PII Classification:")
for column, pii_type in classification.items():
    print(f"  {column}: {pii_type}")

# b) k-Anonymity + re-identification risk comparison
quasi_columns = [
    column for column, pii_type in classification.items()
    if pii_type == "non-PII" and ("age" in column.lower() or "zip" in column.lower() or "pin" in column.lower())
]
if quasi_columns:
    risk_before = reidentification_risk(rows, header, quasi_columns)
    anonymized_rows = apply_k_anonymity(rows, header, quasi_columns)
    risk_after = reidentification_risk(anonymized_rows, header, quasi_columns)
    print(f"\nQuasi-identifiers used: {quasi_columns}")
    print(f"Unique combos BEFORE anonymization: {risk_before}")
    print(f"Unique combos AFTER k-anonymization: {risk_after}")
    print("(Lower 'after' count means harder to re-identify an individual.)")
else:
    print("\nNo obvious quasi-identifier column (age/zip) found to anonymize.")
