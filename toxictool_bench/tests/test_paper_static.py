from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_paper_static import BIB_RE, collect_tex_files, referenced_inputs


def test_official_bibtex_exports_allow_key_on_next_line():
    bibliography = "@inproceedings{\nlei2025dacomp,\n title={DAComp}\n}\n@article{compact2026,title={Example}}"
    assert BIB_RE.findall(bibliography) == ["lei2025dacomp", "compact2026"]


def test_nested_generated_tables_and_missing_dependencies(tmp_path):
    main = tmp_path / "main.tex"
    main.write_text(r"\input{section}")
    (tmp_path / "section.tex").write_text(r"\input{table}\input{missing}")
    (tmp_path / "table.tex").write_text(r"\label{tab:nested}")
    assert [p.name for p in collect_tex_files(main,tmp_path)] == ["main.tex","section.tex","table.tex"]
    assert [p.name for p in referenced_inputs(main,tmp_path)] == ["section.tex","table.tex","missing.tex"]


def test_tex_input_cycle_fails_explicitly(tmp_path):
    main = tmp_path / "main.tex"
    main.write_text(r"\input{main}")
    with pytest.raises(ValueError,match="Cyclic"):
        collect_tex_files(main,tmp_path)
