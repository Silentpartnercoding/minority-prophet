#!/usr/bin/env python3
"""Build the Minority Prophet peer-review PDF from its Markdown source."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab import rl_config
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
PAPER_VERSION = "1.2.0"
CURRENT_VERSION = PAPER_VERSION
DEFAULT_SOURCE = ROOT / f"papers/peer-review/minority-prophet-peer-review-v{PAPER_VERSION}.md"
DEFAULT_OUTPUT = ROOT / f"output/pdf/minority-prophet-peer-review-v{PAPER_VERSION}.pdf"
PAPER_TITLE = "The Minority Prophet Property: Copy-Invariant Evidence Aggregation in Rooted Claim Graphs"
SHORT_TITLE = "The Minority Prophet Property"


def register_fonts() -> tuple[str, str, str, str]:
    candidates = [
        (
            "/System/Library/Fonts/NewYork.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
        ),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        ),
    ]
    for serif, sans, sans_bold, sans_italic in candidates:
        if all(Path(p).exists() for p in (serif, sans, sans_bold, sans_italic)):
            pdfmetrics.registerFont(TTFont("PaperSerif", serif))
            pdfmetrics.registerFont(TTFont("PaperSans", sans))
            pdfmetrics.registerFont(TTFont("PaperSansBold", sans_bold))
            pdfmetrics.registerFont(TTFont("PaperSansItalic", sans_italic))
            return "PaperSerif", "PaperSans", "PaperSansBold", "PaperSansItalic"
    return "Times-Roman", "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


SERIF, SANS, SANS_BOLD, SANS_ITALIC = register_fonts()


def inline(text: str) -> str:
    links: list[tuple[str, str]] = []

    def save_link(match: re.Match[str]) -> str:
        links.append((match.group(1), match.group(2)))
        return f"@@LINK{len(links) - 1}@@"

    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", save_link, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", rf'<font name="{SANS}">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    for index, (label, url) in enumerate(links):
        replacement = f'<link href="{html.escape(url, quote=True)}" color="#245b78">{html.escape(label)}</link>'
        text = text.replace(f"@@LINK{index}@@", replacement)
    return text.replace("  ", " &nbsp;")


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PaperTitle", parent=base["Title"], fontName=SANS_BOLD, fontSize=20,
            leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#17384d"),
            spaceAfter=12,
        ),
        "meta": ParagraphStyle(
            "PaperMeta", parent=base["BodyText"], fontName=SANS, fontSize=9.5,
            leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#40505a"),
            spaceAfter=4,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading1"], fontName=SANS_BOLD, fontSize=14,
            leading=17, textColor=colors.HexColor("#17384d"), spaceBefore=13,
            spaceAfter=6, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading2"], fontName=SANS_BOLD, fontSize=11,
            leading=14, textColor=colors.HexColor("#2f5f72"), spaceBefore=10,
            spaceAfter=4, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName=SERIF, fontSize=9.2,
            leading=12.3, alignment=TA_JUSTIFY, textColor=colors.HexColor("#172027"),
            spaceAfter=6, allowWidows=0, allowOrphans=0,
        ),
        "abstract": ParagraphStyle(
            "Abstract", parent=base["BodyText"], fontName=SERIF, fontSize=9,
            leading=12.2, alignment=TA_JUSTIFY, leftIndent=18, rightIndent=18,
            borderWidth=0.6, borderColor=colors.HexColor("#9cb3bf"),
            borderPadding=9, backColor=colors.HexColor("#f4f8fa"), spaceAfter=9,
        ),
        "quote": ParagraphStyle(
            "Quote", parent=base["BodyText"], fontName=SANS, fontSize=8.8,
            leading=12, leftIndent=18, rightIndent=12, borderWidth=0,
            borderColor=colors.HexColor("#7b99a8"), borderPadding=6,
            backColor=colors.HexColor("#f5f7f8"), spaceAfter=7,
        ),
        "list": ParagraphStyle(
            "List", parent=base["BodyText"], fontName=SERIF, fontSize=9.1,
            leading=12.1, alignment=TA_LEFT, leftIndent=4, spaceAfter=2,
        ),
        "ref": ParagraphStyle(
            "Reference", parent=base["BodyText"], fontName=SERIF, fontSize=8.1,
            leading=10.5, leftIndent=15, firstLineIndent=-15, alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "table": ParagraphStyle(
            "Table", parent=base["BodyText"], fontName=SANS, fontSize=7.1,
            leading=9, alignment=TA_LEFT,
        ),
    }


def parse_table(lines: list[str], style_map: dict[str, ParagraphStyle], width: float):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append([Paragraph(inline(cell), style_map["table"]) for cell in cells])
    columns = max(len(row) for row in rows)
    col_widths = [width / columns] * columns
    if columns == 4:
        col_widths = [width * 0.28, width * 0.18, width * 0.25, width * 0.29]
    table = Table(rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce9ef")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17384d")),
        ("FONTNAME", (0, 0), (-1, 0), SANS_BOLD),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#aab9c0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fa")]),
    ]))
    return table


def story_from_markdown(source: Path, doc_width: float):
    style_map = styles()
    lines = source.read_text(encoding="utf-8").splitlines()
    story = []
    paragraph: list[str] = []
    list_items: list[str] = []
    ordered = False
    table_lines: list[str] = []
    in_abstract = False
    in_references = False
    seen_title = False

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            text = " ".join(item.strip() for item in paragraph)
            chosen = style_map["abstract"] if in_abstract else style_map["ref"] if in_references else style_map["body"]
            story.append(Paragraph(inline(text), chosen))
            paragraph = []

    def flush_list():
        nonlocal list_items
        if list_items:
            prefixes = [str(index) for index in range(1, len(list_items) + 1)] if ordered else ["-"] * len(list_items)
            rows = [
                [Paragraph(prefix, style_map["list"]), Paragraph(inline(item), style_map["list"])]
                for prefix, item in zip(prefixes, list_items)
            ]
            table = Table(rows, colWidths=[0.24 * inch, doc_width - 0.24 * inch], hAlign="LEFT")
            table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 5),
                ("RIGHTPADDING", (1, 0), (1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.append(table)
            story.append(Spacer(1, 5))
            list_items = []

    def flush_table():
        nonlocal table_lines
        if table_lines:
            story.append(parse_table(table_lines, style_map, doc_width))
            story.append(Spacer(1, 8))
            table_lines = []

    for line in lines + [""]:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph(); flush_list()
            table_lines.append(stripped)
            continue
        flush_table()
        if not stripped:
            flush_paragraph(); flush_list()
            continue
        if stripped.startswith("# "):
            flush_paragraph(); flush_list()
            if seen_title:
                story.append(PageBreak())
            story.append(Spacer(1, 0.45 * inch))
            story.append(Paragraph(inline(stripped[2:]), style_map["title"]))
            seen_title = True
            continue
        if stripped.startswith("## "):
            flush_paragraph(); flush_list()
            heading = stripped[3:]
            in_abstract = heading == "Abstract"
            in_references = heading == "References"
            story.append(Paragraph(inline(heading), style_map["h2"]))
            continue
        if stripped.startswith("### "):
            flush_paragraph(); flush_list()
            story.append(Paragraph(inline(stripped[4:]), style_map["h3"]))
            continue
        match = re.match(r"^[-*] (.+)$", stripped)
        number = re.match(r"^\d+\. (.+)$", stripped)
        if match or number:
            flush_paragraph()
            next_ordered = number is not None
            if list_items and ordered != next_ordered:
                flush_list()
            ordered = next_ordered
            list_items.append((number or match).group(1))
            continue
        if stripped.startswith("> "):
            flush_paragraph(); flush_list()
            story.append(Paragraph(inline(stripped[2:]), style_map["quote"]))
            continue
        if not story or (seen_title and not any(isinstance(x, Paragraph) and getattr(x.style, "name", "") == "H2" for x in story)):
            if stripped.startswith("**") or stripped.startswith("Peer-review") or stripped.startswith("Correspondence") or stripped.startswith("Archival DOI"):
                flush_paragraph()
                story.append(Paragraph(inline(stripped), style_map["meta"]))
                continue
        paragraph.append(stripped)
    return story


def _version_of(source: Path) -> str:
    """Version taken from the source filename, so the stamped metadata cannot
    disagree with the document it describes."""
    match = re.search(r"-v(\d+\.\d+\.\d+)\.md$", source.name)
    return match.group(1) if match else PAPER_VERSION


def page_decor(canvas, doc):
    canvas.saveState()
    canvas.setTitle(PAPER_TITLE)
    canvas.setAuthor("James Siyuan He")
    canvas.setSubject(f"Preprint v{CURRENT_VERSION}; not peer reviewed")
    canvas.setCreator("Minority Prophet reproducible ReportLab build")
    page = canvas.getPageNumber()
    if page > 1:
        canvas.setFont(SANS, 7.5)
        canvas.setFillColor(colors.HexColor("#64757e"))
        canvas.drawString(doc.leftMargin, letter[1] - 0.45 * inch, SHORT_TITLE)
        canvas.drawRightString(letter[0] - doc.rightMargin, 0.42 * inch, str(page))
        canvas.setStrokeColor(colors.HexColor("#c4d0d6"))
        canvas.setLineWidth(0.4)
        canvas.line(doc.leftMargin, letter[1] - 0.52 * inch, letter[0] - doc.rightMargin, letter[1] - 0.52 * inch)
    canvas.restoreState()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    global CURRENT_VERSION
    CURRENT_VERSION = _version_of(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rl_config.invariant = 1
    doc = SimpleDocTemplate(
        str(args.output), pagesize=letter,
        rightMargin=0.72 * inch, leftMargin=0.72 * inch,
        topMargin=0.80 * inch, bottomMargin=0.62 * inch,
        title=PAPER_TITLE,
        author="James Siyuan He",
        subject=f"Preprint v{CURRENT_VERSION}; not peer reviewed",
        creator="Minority Prophet reproducible ReportLab build",
        pageCompression=1,
    )
    story = story_from_markdown(args.source, doc.width)
    doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)
    print(args.output)


if __name__ == "__main__":
    main()
