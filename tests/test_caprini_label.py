import sys, types, pathlib
# Ensure external dependencies are stubbed to avoid import issues during tests
sys.modules.setdefault("streamlit", types.ModuleType("streamlit"))
sys.modules.setdefault("pandas", types.ModuleType("pandas"))

# Stub database.functions module to avoid heavy dependencies during import
database_module = types.ModuleType("database")
functions_module = types.ModuleType("database.functions")
def _stub(*args, **kwargs):
    raise NotImplementedError
for name in [
    "get_person", "elg_get_result", "ar_get_result", "sb_get_result",
    "get_soba", "rcri_get_result", "caprini_get_result"
]:
    setattr(functions_module, name, _stub)
database_module.functions = functions_module
sys.modules.setdefault("database", database_module)
sys.modules.setdefault("database.functions", functions_module)

# Add src directory to path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from frontend.component.loader import _caprini_label


def test_caprini_label_ranges():
    assert _caprini_label(0) == "Очень низкий"
    assert _caprini_label(1) == "Низкий"
    assert _caprini_label(2) == "Умеренный"
    assert _caprini_label(3) == "Высокий"
    assert _caprini_label(4) == "Очень высокий"
    # Values above defined range should be capped at the highest label
    assert _caprini_label(10) == "Очень высокий"


def test_caprini_label_none():
    assert _caprini_label(None) == "—"
