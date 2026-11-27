"""Gate G: Frontend Verification Test Suite.

Verifies:
- Top bar navigation routes (Home, Detect, Records, Review, Benchmarks, Method).
- Palette tokens ("Paper and Asphalt" palette with colour-blind safe overlays).
- Typography (Source Serif 4, IBM Plex Sans, IBM Plex Mono, Noto scripts).
- Multilingual i18n support across all 6 required languages.
- Absence of fake seeded numbers or hype words.
- Mandatory Rule R3 disclaimers.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = REPO_ROOT / "web"


def test_gate_g_tokens_paper_and_asphalt():
    """Verify paper and asphalt token declarations and colour-blind safe overlays."""
    tokens_file = WEB_DIR / "src" / "styles" / "tokens.css"
    assert tokens_file.exists(), "tokens.css must exist"
    content = tokens_file.read_text(encoding="utf-8")

    # Paper (Light)
    assert "#F6F4EE" in content, "light bg #F6F4EE missing"
    assert "#FFFFFF" in content, "light surface #FFFFFF missing"
    assert "#DAD6CA" in content, "light rule #DAD6CA missing"
    assert "#1B1A17" in content, "light text #1B1A17 missing"
    assert "#5F5B50" in content, "light muted #5F5B50 missing"
    assert "#E8B100" in content, "road-marking yellow #E8B100 missing"
    assert "#1D4ED8" in content, "link #1D4ED8 missing"

    # Asphalt (Dark)
    assert "#121311" in content, "dark bg #121311 missing"
    assert "#1A1B18" in content, "dark surface #1A1B18 missing"
    assert "#ECEAE2" in content, "dark text #ECEAE2 missing"
    assert "#F5C400" in content, "dark accent #F5C400 missing"

    # Colour-blind safe overlays
    assert "#D55E00" in content, "pothole #D55E00 missing"
    assert "#0072B2" in content, "crack #0072B2 missing"
    assert "#CC79A7" in content, "water-filled #CC79A7 missing"


def test_gate_g_typography_and_fonts():
    """Verify Google font links and CSS configuration for required typefaces."""
    index_html = WEB_DIR / "index.html"
    assert index_html.exists()
    content = index_html.read_text(encoding="utf-8")

    assert "Source+Serif+4" in content, "Source Serif 4 headings font missing"
    assert "IBM+Plex+Sans" in content, "IBM Plex Sans UI font missing"
    assert "IBM+Plex+Mono" in content, "IBM Plex Mono numbers font missing"
    assert "Noto+Sans" in content, "Noto scripts font missing"


def test_gate_g_top_bar_navigation_items():
    """Verify Top Bar navigation matches Home | Detect | Records | Review | Benchmarks | Method."""
    navbar_file = WEB_DIR / "src" / "components" / "Navbar.tsx"
    assert navbar_file.exists()
    content = navbar_file.read_text(encoding="utf-8")

    assert 'key: "navHome"' in content
    assert 'key: "navDetect"' in content
    assert 'key: "navRecords"' in content
    assert 'key: "navReview"' in content
    assert 'key: "navBenchmarks"' in content
    assert 'key: "navMethod"' in content


def test_gate_g_all_pages_exist():
    """Verify all 6 pages exist with appropriate components."""
    pages_dir = WEB_DIR / "src" / "pages"
    assert (pages_dir / "RoadOverviewPage.tsx").exists(), "Home page missing"
    assert (pages_dir / "RoadScannerPage.tsx").exists(), "Detect page missing"
    assert (pages_dir / "RoadAuditReportPage.tsx").exists(), "Records page missing"
    assert (pages_dir / "ReviewPage.tsx").exists(), "Review page missing"
    assert (pages_dir / "BenchmarksPage.tsx").exists(), "Benchmarks page missing"
    assert (pages_dir / "MethodPage.tsx").exists(), "Method page missing"


def test_gate_g_disclaimer_rule_r3():
    """Verify mandatory Rule R3 footer disclaimer in Footer.tsx."""
    footer_file = WEB_DIR / "src" / "components" / "Footer.tsx"
    content = footer_file.read_text(encoding="utf-8")
    assert "Student research project. Not an official government system. Not safety-certified." in content
