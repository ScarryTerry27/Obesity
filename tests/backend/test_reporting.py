import os
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from backend.reporting import generate_patient_report


def test_generate_patient_report_creates_file(tmp_path):
    patient = {"id": 1, "fio": "Test Patient", "age": 30}
    scales = {"TestScale": 5}

    pdf_path = generate_patient_report(patient, scales, output_dir=tmp_path)

    assert os.path.isfile(pdf_path)
    assert os.path.getsize(pdf_path) > 0
