import io
import pytest
import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.template_generator import build_template_workbook, generate_candidate_template_xlsx
from backend.app.routers.students import find_column, REGISTER_NO_SYNONYMS, NAME_SYNONYMS, BRANCH_SYNONYMS
from conftest import test_session as _test_db

client = TestClient(app)

def test_template_workbook_structure():
    wb = build_template_workbook()
    assert "Candidate Register" in wb.sheetnames
    assert "Template Guidelines" in wb.sheetnames

    ws = wb["Candidate Register"]
    headers = [cell.value for cell in ws[1]]
    assert "Register Number" in headers
    assert "Student Name" in headers
    assert "Branch" in headers
    assert "Semester" in headers
    assert "Course Code" in headers

    # Verify column A has text format '@'
    assert ws["A2"].number_format == "@"

def test_template_download_endpoint():
    response = client.get("/api/v1/students/template")
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert "candidate_register_template.xlsx" in response.headers.get("content-disposition", "")

    # Read response bytes with pandas
    df = pd.read_excel(io.BytesIO(response.content), sheet_name="Candidate Register", dtype=str)
    assert len(df) >= 5
    assert "Register Number" in df.columns
    # Check that register numbers are exact 16 digits
    for reg in df["Register Number"]:
        assert len(str(reg).strip()) == 16
        assert str(reg).strip().isdigit()

def test_find_column_flexible_matching():
    # Standard headers
    cols = ["Register Number", "Student Name", "Branch", "Semester", "Course Code"]
    assert find_column(cols, REGISTER_NO_SYNONYMS) == "Register Number"
    assert find_column(cols, NAME_SYNONYMS) == "Student Name"
    assert find_column(cols, BRANCH_SYNONYMS) == "Branch"

    # Variant headers with asterisks, (required), lowercase, underscores
    variant_cols = ["Register Number (Required)", "Student_Name", "dept", "sem", "subject code"]
    assert find_column(variant_cols, REGISTER_NO_SYNONYMS) == "Register Number (Required)"
    assert find_column(variant_cols, NAME_SYNONYMS) == "Student_Name"
    assert find_column(variant_cols, BRANCH_SYNONYMS) == "dept"

    reg_star = ["Reg No*", "Name"]
    assert find_column(reg_star, REGISTER_NO_SYNONYMS) == "Reg No*"

def test_template_upload_preview_integration():
    # Test uploading Excel with newly generated numbers
    wb = build_template_workbook()
    ws = wb["Candidate Register"]
    # Change register numbers to unique test numbers
    for i in range(2, 12):
        ws.cell(row=i, column=1).value = f"888800001111{i:04d}"
    
    test_buf = io.BytesIO()
    wb.save(test_buf)
    test_buf.seek(0)

    response = client.post(
        "/api/v1/students/upload-preview",
        files={"file": ("candidate_register_template.xlsx", test_buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid_count"] == 10
    assert data["invalid_count"] == 0
    assert len(data["valid_preview"]) == 10
    assert len(data["all_valid"]) == 10
