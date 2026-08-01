from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BILINGUAL_DOC_PAIRS = (
    (Path("ENVIRONMENT.md"), Path("ENVIRONMENT.zh-CN.md")),
    (Path("DEPENDENCIES.md"), Path("DEPENDENCIES.zh-CN.md")),
    (Path("REPRODUCIBILITY.md"), Path("REPRODUCIBILITY.zh-CN.md")),
    (Path("PACKAGING.md"), Path("PACKAGING.zh-CN.md")),
    (Path("THIRD_PARTY_LICENSES.md"), Path("THIRD_PARTY_LICENSES.zh-CN.md")),
    (Path("docs/SETUP.md"), Path("docs/SETUP.zh-CN.md")),
    (Path("docs/CONFIGURATION.md"), Path("docs/CONFIGURATION.zh-CN.md")),
    (Path("docs/G1_RELAY.md"), Path("docs/G1_RELAY.zh-CN.md")),
    (Path("docs/OPTIONAL_RAG.md"), Path("docs/OPTIONAL_RAG.zh-CN.md")),
    (Path("docs/TROUBLESHOOTING.md"), Path("docs/TROUBLESHOOTING.zh-CN.md")),
    (
        Path("docs/project_architecture.md"),
        Path("docs/project_architecture.zh-CN.md"),
    ),
    (
        Path("docs/voice_to_robot_call_chain.md"),
        Path("docs/voice_to_robot_call_chain.zh-CN.md"),
    ),
    (Path("beamforming/README.md"), Path("beamforming/README.zh-CN.md")),
    (
        Path("xjtlu-rag-system/README.md"),
        Path("xjtlu-rag-system/README.zh-CN.md"),
    ),
)
MAINTAINED_DOCS = (
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    *(ROOT / path for pair in BILINGUAL_DOC_PAIRS for path in pair),
)
PUBLIC_DOCS = MAINTAINED_DOCS + (ROOT / "docs" / "archive" / "README.md",)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _markdown_targets(text: str) -> set[str]:
    # Maintained repository docs use simple inline Markdown links.
    link_pattern = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
    return {
        target.strip().strip("<>").split("#", 1)[0]
        for target in link_pattern.findall(text)
    }


def test_all_public_documents_exist() -> None:
    missing = [
        document.relative_to(ROOT).as_posix()
        for document in PUBLIC_DOCS
        if not document.is_file()
    ]
    assert not missing, "Missing public documentation files:\n" + "\n".join(missing)


def test_public_document_internal_links_resolve() -> None:
    missing: list[str] = []
    for document in PUBLIC_DOCS:
        if not document.is_file():
            continue
        for raw_target in _markdown_targets(_read(document)):
            target = raw_target
            if not target or re.match(r"^(?:https?://|mailto:)", target):
                continue
            resolved = (document.parent / target).resolve()
            if not resolved.exists():
                missing.append(
                    f"{document.relative_to(ROOT).as_posix()} -> {raw_target}"
                )
    assert not missing, "Broken public documentation links:\n" + "\n".join(missing)


def test_each_maintained_topic_has_linked_english_and_chinese_versions() -> None:
    unlinked: list[str] = []
    for english_relative, chinese_relative in BILINGUAL_DOC_PAIRS:
        english = ROOT / english_relative
        chinese = ROOT / chinese_relative
        if not english.is_file() or not chinese.is_file():
            continue
        english_targets = _markdown_targets(_read(english))
        chinese_targets = _markdown_targets(_read(chinese))
        if chinese.name not in english_targets:
            unlinked.append(f"{english_relative.as_posix()} -> {chinese.name}")
        if english.name not in chinese_targets:
            unlinked.append(f"{chinese_relative.as_posix()} -> {english.name}")
    assert not unlinked, "Missing bilingual counterpart links:\n" + "\n".join(unlinked)


def test_bilingual_readmes_link_to_their_language_specific_entry_points() -> None:
    english_targets = _markdown_targets(_read(ROOT / "README.md"))
    chinese_targets = _markdown_targets(_read(ROOT / "README.zh-CN.md"))
    routing_errors: list[str] = []
    if "README.zh-CN.md" not in english_targets:
        routing_errors.append(
            "README.md: missing language-switch target README.zh-CN.md"
        )
    if "README.md" not in chinese_targets:
        routing_errors.append(
            "README.zh-CN.md: missing language-switch target README.md"
        )
    for english_target, chinese_target in BILINGUAL_DOC_PAIRS:
        english_target_text = english_target.as_posix()
        chinese_target_text = chinese_target.as_posix()
        if english_target_text not in english_targets:
            routing_errors.append(
                f"README.md: missing English target {english_target_text}"
            )
        if chinese_target_text in english_targets:
            routing_errors.append(
                f"README.md: wrong-language Chinese target {chinese_target_text}"
            )
        if chinese_target_text not in chinese_targets:
            routing_errors.append(
                f"README.zh-CN.md: missing Chinese target {chinese_target_text}"
            )
        if english_target_text in chinese_targets:
            routing_errors.append(
                f"README.zh-CN.md: wrong-language English target {english_target_text}"
            )
    assert not routing_errors, "Invalid README language routing:\n" + "\n".join(
        routing_errors
    )


def test_documented_default_backends_match_public_config() -> None:
    defaults = _read(ROOT / "config" / "default.env")
    readmes = _read(ROOT / "README.md") + _read(ROOT / "README.zh-CN.md")
    assert 'LLM_REPLY_BACKEND="${LLM_REPLY_BACKEND:-${QWEN_REPLY_BACKEND:-deepseek}}"' in defaults
    assert 'UNITREE_BACKEND="${UNITREE_BACKEND:-relay}"' in defaults
    assert 'ROBOT_RELAY_HOST="${ROBOT_RELAY_HOST:-}"' in defaults
    assert "LLM_REPLY_BACKEND=deepseek" in readmes
    assert "UNITREE_BACKEND=relay" in readmes


def test_monitor_controls_and_port_are_documented_from_the_ui_contract() -> None:
    html = _read(ROOT / "ui" / "pipeline_monitor" / "index.html")
    server = _read(ROOT / "pipeline_monitor" / "server.py")
    chinese = _read(ROOT / "README.zh-CN.md")
    for label in ("启动", "停止", "快速", "停顿", "标准", "兼容", "唤醒", "打断", "结束", "静默结束"):
        assert re.search(rf">\s*{label}\s*<", html)
        assert f"**{label}**" in chinese or label in ("启动", "停止")
    assert 'parser.add_argument("--port", type=int, default=8765)' in server
    assert "127.0.0.1:8765" in chinese
    assert "--port 8766" in chinese
    assert "我在" in chinese
    assert "小浦退下了" in chinese


def test_public_docs_mark_optional_and_blocked_material() -> None:
    readmes = _read(ROOT / "README.md") + _read(ROOT / "README.zh-CN.md")
    english_architecture = _read(ROOT / "docs" / "project_architecture.md")
    chinese_architecture = _read(
        ROOT / "docs" / "project_architecture.zh-CN.md"
    )
    assert "RAG is disabled by default" in readmes
    assert "XJTLU RAG is retained as an optional experimental backend" in (
        english_architecture
    )
    assert "XJTLU RAG 是保留的可选实验后端" in chinese_architecture
    assert "teacher_reference_20260630" in readmes
    assert (ROOT / "LICENSE").is_file()
    assert "Apache License 2.0" in readmes


def test_maintained_docs_do_not_claim_private_publication_approval() -> None:
    forbidden = re.compile(
        r"2026-08-01|provider confirmed|confirmed permission|"
        r"permission to publish|publication-blocked|"
        r"(?:教师|老师|波束成形|滤波器|参考录音)[^\n]*确认允许[^\n]*公开",
        re.IGNORECASE,
    )
    violations: list[str] = []
    for document in MAINTAINED_DOCS:
        if not document.is_file():
            continue
        relative = document.relative_to(ROOT).as_posix()
        for line_number, line in enumerate(_read(document).splitlines(), start=1):
            match = forbidden.search(line)
            if match:
                snippet = line.strip()[:160]
                violations.append(
                    f"{relative}:{line_number}: matched {match.group(0)!r}: {snippet}"
                )
    assert not violations, "Private publication approval text in maintained docs:\n" + "\n".join(
        violations
    )


def test_third_party_notice_matches_safe_bundle_and_ships_unitree_python_license() -> None:
    notice = _read(ROOT / "THIRD_PARTY_LICENSES.md")
    unitree_license = (
        ROOT
        / "deps"
        / "qwen_ros_node_edg_tts"
        / "third_party"
        / "unitree_sdk2_python"
        / "LICENSE"
    )
    assert unitree_license.is_file()
    assert "BSD 3-Clause License" in _read(unitree_license)
    assert "filtered Git-tracked\nsource snapshot" in notice
    assert "currently copies the local Qwen" not in notice


def test_active_first_party_docs_do_not_publish_machine_specific_robot_ips() -> None:
    active_docs = PUBLIC_DOCS + (
        ROOT / "deps" / "SURF2026_VoiceModule-main" / "README.md",
    )
    forbidden = re.compile(r"192\.168\.123\.(?:164|222|225)")
    leaks = [
        path.relative_to(ROOT).as_posix()
        for path in active_docs
        if path.is_file() and forbidden.search(_read(path))
    ]
    assert not leaks, "Machine-specific robot IPs in active docs: " + ", ".join(leaks)
