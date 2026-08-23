import csv
import pytest
from pathlib import Path

PROVENANCE_CSV = Path(__file__).parent.parent / "research" / "parameter_provenance.csv"
LITERATURE_CSV = Path(__file__).parent.parent / "research" / "literature_matrix.csv"

REQUIRED_PROVENANCE_COLUMNS = [
    "Parameter_ID",
    "Parameter",
    "Category",
    "Value",
    "Unit",
    "Evidence_Label",
    "Source",
    "Source_Type",
    "Publication_Year",
    "DOI_or_Identifier",
    "Evidence_Location",
    "Justification",
    "Confidence",
    "Used_In",
    "Verification_Status"
]

REQUIRED_LITERATURE_COLUMNS = [
    "ID",
    "Title",
    "Authors",
    "Year",
    "Venue",
    "IEEE_Non_IEEE",
    "DOI",
    "Research_Problem",
    "Technology",
    "QKD",
    "PQC",
    "Hybrid_QKD_PQC",
    "6G",
    "Healthcare",
    "EHR",
    "IoMT",
    "Edge_Computing",
    "Methodology",
    "Simulation_Experimental_Setup",
    "Dataset_Network_Model",
    "Metrics",
    "Main_Findings",
    "Limitations",
    "Relevance_To_Our_Paper",
    "Potential_Overlap_With_Proposed_Work",
    "Tier",
    "Evidence_Label",
    "Verified"
]

VALID_EVIDENCE_LABELS = {
    "ESTABLISHED",
    "REPORTED_RANGE",
    "DESIGN_ASSUMPTION",
    "EXPERIMENTAL_VALUE",
    "UNKNOWN"
}

VALID_SOURCE_TYPES = {
    "PRIMARY_RESEARCH",
    "SYSTEMATIC_REVIEW",
    "STANDARD",
    "TECHNICAL_REPORT",
    "VENDOR_DOCUMENTATION",
    "SECONDARY_SOURCE",
    "DESIGN_DOCUMENT"
}

VALID_VERIFICATION_STATUSES = {
    "VERIFIED",
    "PARTIALLY_VERIFIED",
    "UNVERIFIED"
}

VALID_CONFIDENCE_LEVELS = {
    "HIGH",
    "MEDIUM",
    "LOW",
    "NONE"
}

@pytest.fixture
def provenance_data():
    if not PROVENANCE_CSV.exists():
        pytest.skip(f"Provenance file not found at {PROVENANCE_CSV}")

    with open(PROVENANCE_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def test_provenance_file_exists():
    assert PROVENANCE_CSV.exists(), f"Provenance file not found at {PROVENANCE_CSV}"

def test_required_columns():
    with open(PROVENANCE_CSV, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            headers = []

    for col in REQUIRED_PROVENANCE_COLUMNS:
        assert col in headers, f"Missing required column in provenance: {col}"

def test_literature_matrix_schema():
    assert LITERATURE_CSV.exists(), f"Literature matrix not found at {LITERATURE_CSV}"
    with open(LITERATURE_CSV, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            headers = []

    assert headers == REQUIRED_LITERATURE_COLUMNS, "Literature matrix schema does not match the exact requirement."

def test_unique_parameter_ids(provenance_data):
    ids = [row["Parameter_ID"] for row in provenance_data]
    assert len(ids) == len(set(ids)), "Parameter_IDs must be unique"

def test_controlled_vocabularies(provenance_data):
    for row_idx, row in enumerate(provenance_data, start=2):
        pid = row.get("Parameter_ID", f"Row-{row_idx}")

        evidence_label = row.get("Evidence_Label")
        assert evidence_label in VALID_EVIDENCE_LABELS, f"[{pid}] Invalid Evidence_Label: {evidence_label}"

        source_type = row.get("Source_Type")
        if source_type:
            assert source_type in VALID_SOURCE_TYPES, f"[{pid}] Invalid Source_Type: {source_type}"

        status = row.get("Verification_Status")
        if status:
            assert status in VALID_VERIFICATION_STATUSES, f"[{pid}] Invalid Verification_Status: {status}"

        conf = row.get("Confidence")
        if conf:
            assert conf in VALID_CONFIDENCE_LEVELS, f"[{pid}] Invalid Confidence: {conf}"

def test_verified_entries_require_source(provenance_data):
    for row_idx, row in enumerate(provenance_data, start=2):
        pid = row.get("Parameter_ID", f"Row-{row_idx}")
        status = row.get("Verification_Status")
        evidence = row.get("Evidence_Label")

        if status == "VERIFIED":
            source = row.get("Source", "").strip()
            source_type = row.get("Source_Type", "").strip()
            year = row.get("Publication_Year", "").strip()
            doi = row.get("DOI_or_Identifier", "").strip()
            location = row.get("Evidence_Location", "").strip()

            assert source, f"[{pid}] VERIFIED entry requires Source"
            assert source_type, f"[{pid}] VERIFIED entry requires Source_Type"
            assert year, f"[{pid}] VERIFIED entry requires Publication_Year"
            assert doi, f"[{pid}] VERIFIED entry requires DOI_or_Identifier"
            assert location, f"[{pid}] VERIFIED entry requires Evidence_Location"
            assert evidence != "UNKNOWN", f"[{pid}] VERIFIED entry cannot have UNKNOWN evidence"

def test_partially_verified_entries(provenance_data):
    for row_idx, row in enumerate(provenance_data, start=2):
        pid = row.get("Parameter_ID", f"Row-{row_idx}")
        status = row.get("Verification_Status")
        evidence = row.get("Evidence_Label")

        if status == "PARTIALLY_VERIFIED":
            assert evidence != "ESTABLISHED", f"[{pid}] PARTIALLY_VERIFIED entry cannot claim ESTABLISHED evidence"

def test_unverified_entries_cannot_claim_established_evidence(provenance_data):
    for row_idx, row in enumerate(provenance_data, start=2):
        pid = row.get("Parameter_ID", f"Row-{row_idx}")
        status = row.get("Verification_Status")
        evidence = row.get("Evidence_Label")

        if status == "UNVERIFIED":
            assert evidence != "ESTABLISHED", f"[{pid}] UNVERIFIED/UNKNOWN entry cannot claim ESTABLISHED evidence"

        if evidence == "UNKNOWN":
            assert status == "UNVERIFIED", f"[{pid}] UNKNOWN evidence must be UNVERIFIED"

def validate_row(row):
    pid = row.get("Parameter_ID", "TestRow")
    evidence_label = row.get("Evidence_Label")
    source_type = row.get("Source_Type")
    status = row.get("Verification_Status")
    conf = row.get("Confidence")

    if evidence_label:
        assert evidence_label in VALID_EVIDENCE_LABELS, f"[{pid}] Invalid Evidence_Label: {evidence_label}"

    if source_type:
        assert source_type in VALID_SOURCE_TYPES, f"[{pid}] Invalid Source_Type: {source_type}"

    if status:
        assert status in VALID_VERIFICATION_STATUSES, f"[{pid}] Invalid Verification_Status: {status}"

    if conf:
        assert conf in VALID_CONFIDENCE_LEVELS, f"[{pid}] Invalid Confidence: {conf}"

    if status == "VERIFIED":
        source = row.get("Source", "").strip()
        stype = row.get("Source_Type", "").strip()
        year = row.get("Publication_Year", "").strip()
        doi = row.get("DOI_or_Identifier", "").strip()
        location = row.get("Evidence_Location", "").strip()

        assert source, f"[{pid}] VERIFIED entry requires Source"
        assert stype, f"[{pid}] VERIFIED entry requires Source_Type"
        assert year, f"[{pid}] VERIFIED entry requires Publication_Year"
        assert doi, f"[{pid}] VERIFIED entry requires DOI_or_Identifier"
        assert location, f"[{pid}] VERIFIED entry requires Evidence_Location"
        assert evidence_label != "UNKNOWN", f"[{pid}] VERIFIED entry cannot have UNKNOWN evidence"

    if status == "PARTIALLY_VERIFIED":
        assert evidence_label != "ESTABLISHED", f"[{pid}] PARTIALLY_VERIFIED entry cannot claim ESTABLISHED evidence"

    if status == "UNVERIFIED":
        assert evidence_label != "ESTABLISHED", f"[{pid}] UNVERIFIED entry cannot claim ESTABLISHED evidence"

    if evidence_label == "UNKNOWN":
        assert status == "UNVERIFIED", f"[{pid}] UNKNOWN evidence must be UNVERIFIED"

def test_explicit_validation_rules():
    # 1. valid Evidence_Label accepted
    validate_row({"Evidence_Label": "ESTABLISHED"})
    # 2. invalid Evidence_Label rejected
    with pytest.raises(AssertionError):
        validate_row({"Evidence_Label": "INVALID_LABEL"})
    # 3. valid Source_Type accepted
    validate_row({"Source_Type": "PRIMARY_RESEARCH"})
    # 4. invalid Source_Type rejected
    with pytest.raises(AssertionError):
        validate_row({"Source_Type": "BLOG_POST"})
    # 5. valid Verification_Status accepted
    validate_row({"Verification_Status": "UNVERIFIED"})
    # 6. invalid Verification_Status rejected
    with pytest.raises(AssertionError):
        validate_row({"Verification_Status": "SUPER_VERIFIED"})
    # 7. VERIFIED without Source rejected
    with pytest.raises(AssertionError):
        validate_row({"Verification_Status": "VERIFIED", "Source": "", "Source_Type": "STANDARD", "Publication_Year": "2024", "DOI_or_Identifier": "10.1", "Evidence_Location": "P1"})
    # 8. VERIFIED without Evidence_Location rejected
    with pytest.raises(AssertionError):
        validate_row({"Verification_Status": "VERIFIED", "Source": "A", "Source_Type": "STANDARD", "Publication_Year": "2024", "DOI_or_Identifier": "10.1", "Evidence_Location": ""})
    # 9. UNVERIFIED + ESTABLISHED rejected
    with pytest.raises(AssertionError):
        validate_row({"Verification_Status": "UNVERIFIED", "Evidence_Label": "ESTABLISHED"})
    # 10. UNKNOWN + VERIFIED rejected
    with pytest.raises(AssertionError):
        validate_row({"Evidence_Label": "UNKNOWN", "Verification_Status": "VERIFIED", "Source": "A", "Source_Type": "STANDARD", "Publication_Year": "2024", "DOI_or_Identifier": "10.1", "Evidence_Location": "P1"})
