import os
from pathlib import Path
from typing import Dict, Any

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except Exception:  # pragma: no cover - fallback when reportlab isn't installed
    A4 = (595.27, 841.89)

    class _SimpleCanvas:
        """Minimal fallback that writes plain text if ReportLab is unavailable."""

        def __init__(self, path, pagesize=A4):
            self._f = open(path, "wb")

        def setFont(self, *args, **kwargs):
            pass

        def drawString(self, x, y, text):
            self._f.write(f"{text}\n".encode("utf-8"))

        def showPage(self):
            self._f.write(b"\n")

        def save(self):
            self._f.write(b"\n")
            self._f.close()

    class _CanvasModule:
        Canvas = _SimpleCanvas

    canvas = _CanvasModule()


def generate_patient_report(patient: Dict[str, Any], scales: Dict[str, Any], output_dir: str = "reports", filename: str | None = None) -> str:
    """Generate a simple PDF report for a patient.

    Parameters
    ----------
    patient: dict
        Information about the patient. Keys and values will be rendered as
        lines of text.
    scales: dict
        Mapping of scale names to their calculated values.
    output_dir: str
        Directory where the file should be stored.
    filename: str | None
        Optional filename. If not provided, a name will be generated using the
        patient id (if available).

    Returns
    -------
    str
        Path to the created PDF file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    patient_id = patient.get("id", "unknown")
    if filename is None:
        filename = f"patient_{patient_id}_report.pdf"
    file_path = os.path.join(output_dir, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica", 14)
    c.drawString(50, y, f"Отчёт по пациенту: {patient.get('fio', '')}")
    y -= 30
    c.setFont("Helvetica", 12)
    for key, value in patient.items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    y -= 10
    c.drawString(50, y, "Шкалы:")
    y -= 30
    for key, value in scales.items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return file_path
