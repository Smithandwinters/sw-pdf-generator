#!/usr/bin/env python3
"""
buildPdf.py â Smith & Winters Electrical Branded Report Generator
Usage: python3 buildPdf.py <job_data.json> <output.pdf> <logo.png>

Matches the Job 4170 completion report style exactly:
- Black header bar with logo + "Job Completion Report" + Job No
- Yellow accent line under header
- Dark grey section headers with yellow left accent
- Per-quote scope cards with red left marker
- Checklist: What's Included / Not Included
- Photo documentation pages (one photo per page with caption)
- Completion sign-off page
- Yellow/dark footer with page numbers
"""

import sys
import json
import os
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.platypus.flowables import Flowable

# ------------------------------------------------
# Brand colours
# ------------------------------------------------
YELLOW   = colors.HexColor("#F5C200")
DARK_RED = colors.HexColor("#8B0000")
RED_MARK = colors.HexColor("#C0392B")
BLACK    = colors.HexColor("#1A1A1A")
DARK_BG  = colors.HexColor("#2D2D2D")
SECTION_BG = colors.HexColor("#4A4A4A")
LIGHT_BG = colors.HexColor("#F5F5F5")
MID_GREY = colors.HexColor("#DDDDDD")
DARK_GREY = colors.HexColor("#555555")
WHITE    = colors.white
GREEN_TICK = colors.HexColor("#27AE60")
RED_CROSS  = colors.HexColor("#C0392B")

PAGE_W, PACE_H = A4
MARGIN = 14 * mm
BODY_W = PAGE_W - 2 * MARGIN


# ------------------------------------------------
# Page template
# ------------------------------------------------
def make_on_page(job_no, logo_path):
    def on_page(canvas, doc):
        canvas.saveState()
        w, h = A4

        # Black header bar
        canvas.setFillColor(BLACK)
        canvas.rect(0, h - 22*mm, w, 22*mm, fill=1, stroke=0)

        # Logo
        if logo_path and os.path.exists(logo_path):
            canvas.drawImage(
                logo_path, MARGIN, h - 20*mm,
                width=52*mm, height=17*mm,
                preserveAspectRatio=True, mask="auto"
            )

        # "Job Completion Report" top right
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(YELLOW)
        canvas.drawRightString(w - MARGIN, h - 7*mm, "Job Completion Report")

        # "Job No. XXXX"
        canvas.setFont("Helvetica-Bold", 14)
        canvas.setFillColor(WHITE)
        canvas.drawRightString(w - MARGIN, h - 18*mm, f"Job No. {job_no}")

        # Yellow accent line
        canvas.setStrokeColor(YELLOW)
        canvas.setLineWidth(2.5)
        canvas.line(0, h - 22.5*mm, w, h - 22.5*mm)

        # Footer bar
        canvas.setFillColor(BLACK)
        canvas.rect(0, 0, w, 10*mm, fill=1, stroke=0)
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(colors.HexColor("#AAAAAA"))
        canvas.drawString(MARGIN, 3.5*mm, "Smith & Winters Electrical  |  ABN 70 626 942 596  |  Licence VIC: 26114  QLA: 91858")
        canvas.setFillColor(YELLOW)
        canvas.drawRightString(w - MARGIN, 3.5*mm, f"Job No. {job_no}  |  Page {doc.page}")
        canvas.restoreState()
    return on_page


# ------------------------------------------------
# Helpers
# ------------------------------------------------
def section_header(title):
    s = ParagraphStyle("sh", fontName="Helvetica-Bold", fontSize=10,
                        textColor=WHITE, leftIndent=4*mm)
    t = Table([[Paragraph(title, s)]], colWidths=[BODY_W],
              style=TableStyle([
                  ("BACKGROUND", (0, 0), (-1, -1), SECTION_BG),
                  ("TOPPADDING", (0, 0), (-1, -1), 6),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                  ("LEFTPADDING", (0, 0), (-1, -1), 10),
              ]))
    return [Spacer(1, 4*mm), t, Spacer(1, 2*mm)]


def detail_grid(rows):
    normal = ParagraphStyle("dv", fontName="Helvetica", fontSize=8.5, leading=12, wordWrap="CJK")
    bold   = ParagraphStyle("dk", fontName="Helvetica-Bold", fontSize=8, leading=12,
                             textColor=DARK_GREY)
    data = []
    for k, v in rows:
        data.append([Paragraph(k, bold), Paragraph(str(v) if v else "â", normal)])
    ts = TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID",           (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW",      (0, -1), (-1, -1), 1, YELLOW),
    ])
    return Table(data, colWidths=[BODY_W * 0.35, BODY_W * 0.65], style=ts, hAlign="LEFT")


def scope_card(quote_ref, title, description):
    ref_style  = ParagraphStyle("ref", fontName="Helvetica-Bold", fontSize=8, textColor=RED_MARK)
    title_style = ParagraphStyle("st", fontName="Helvetica-Bold", fontSize=9.5, textColor=BLACK)
    body_style  = ParagraphStyle("sb", fontName="Helvetica", fontSize=8.5, leading=13, textColor=BLACK)
    content_col = [
        Paragraph(f"Quote Ref. {quote_ref}" if quote_ref else "", ref_style),
        Spacer(1, 1*mm),
        Paragraph(title, title_style),
        Spacer(1, 1*mm),
        Paragraph(description, body_style),
    ]
    marker_col = Table([[""]], colWidths=[3*mm],
                        style=TableStyle([
                            ("BACKGROUND", (0, 0), (-1, -1), RED_MARK),
                            ("TOPPADDING",     (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ]))
    content_tbl = Table([[item] for item in content_col],
                         colWidths=[BODY_W - 5*mm],
                         style=TableStyle([
                             ("TOPPADDING",    (0, 0), (-1, -1), 0),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                             ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                             ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                         ]))
    card = Table([[marker_col, content_tbl]],
                 colWidths=[5*mm, BODY_W - 5*mm],
                 style=TableStyle([
                     ("VALIGN",         (0, 0), (-1, -1), "TOP"),
                     ("TOPPADDING",     (0, 0), (-1, -1), 6),
                     ("BOTTOMPADDING",  (0, 0), (-1, -1), 6),
                     ("LEFTPADDING",    (0, 0), (-1, -1), 0),
                     ("RIGHTPADDING",   (0, 0), (-1, -1), 0),
                     ("LINEBELOW",      (0, -1), (-1, -1), 0.4, MID_GREY),
                     ("BACKGROUND",     (0, 0), (-1, -1), WHITE),
                 ]))
    return [card, Spacer(1, 1*mm)]


def checklist_row(text, is_included=True):
    tick_style = ParagraphStyle("tick", fontName="Helvetica-Bold", fontSize=10,
                                 textColor=GREEN_TICK if is_included else RED_CROSS)
    text_style = ParagraphStyle("ct", fontName="Helvetica", fontSize=8.5, leading=13,
                                  textColor=DARK_RED if not is_included else BLACK)
    symbol = "&#10004;" if is_included else "&#10008;"
    return [
        Paragraph(symbol, tick_style),
        Paragraph(text, text_style),
    ]


def photo_page(photo_path, caption_title, caption_body):
    elements = []
    ts = ParagraphStyle("pt", fontName="Helvetica-Bold", fontSize=10, textColor=BLACK)
    bs = ParagraphStyle("pb", fontName="Helvetica", fontSize=8.5, leading=13, textColor=DARK_GREY)
    caption_tbl = Table(
        [[Paragraph(caption_title, ts)], [Paragraph(caption_body, bs)]],
        colWidths=[BODY_W],
        style=TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), LIGHT_BG),
            ("GRID",         (0, 0), (-1, -1), 0.3, MID_GREY),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
            ("LINEBELOW",    (0, -1), (-1, -1), 1.5, YELLOW),
        ])
    )
    elements.append(caption_tbl)
    elements.append(Spacer(1, 4*mm))
    if photo_path and os.path.exists(photo_path):
        try:
            img = Image(photo_path)
            ratio = min(BODY_W / img.imageWidth, 160 * mm / img.imageHeight)
            img.drawWidth  = img.imageWidth  * ratio
            img.drawHeight = img.imageHeight * ratio
            img.hAlign = "CENTER"
            elements.append(img)
        except Exception:
            pass
    return elements


# ------------------------------------------------
# Main build function
# ------------------------------------------------
def build(json_path, out_path, logo_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    job_no = data.get("jobNo", "")

    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=26*mm, bottomMargin=14*mm,
    )

    on_page = make_on_page(job_no, logo_path)
    story = []

    normal = ParagraphStyle("n", fontName="Helvetica", fontSize=8.5, leading=13)
    bold   = ParagraphStyle("b", fontName="Helvetica-Bold", fontSize=8.5, leading=13)
    intro  = ParagraphStyle("i", fontName="Helvetica", fontSize=8.5, leading=13,
                             textColor=DARK_GREY)

    # CLIENT & JOB DETAILS
    story += section_header("CLIENT & JOB DETAILS")

    customer = data.get("customer", {})
    quote_refs = ", ".join(data.get("quoteRefs", [])) or "—"
    rows = [
        ("CLIENT",       customer.get("name") or "—"),
        ("BUSINESS",     customer.get("business") or "—"),
        ("CONTACT",      customer.get("phone") or customer.get("contact") or "—"),
        ("JOB NO.",      job_no),
        ("SITE ADDRESS", data.get("siteAddress") or "—"),
        ("LICENCE",      data.get("licence") or "VIC: 26114  QLA: 91858"),
        ("ABN",          data.get("abn") or "70 626 942 596"),
        ("STATUS",       data.get("status") or "COMPLETED"),
        ("TECHNICIAN",   data.get("technician") or "—"),
        ("WORKS DATE",   data.get("worksDate") or date.today().strftime("%B %Y")),
        ("QUOTE REF.",   quote_refs),
        ("CERT. SAFETY", data.get("certSafety") or "To be issued on finalisation"),
    ]

    # Single full-width grid (no truncation)
    story.append(detail_grid(rows))
    story.append(Spacer(1, 4�mm))

    # SCOPE OF WORKS
    story += section_header("SCOPE OF WORKS COMPLETED")
    site_name = customer.get("business") or "the site"
    site_addr = data.get("siteAddress", "")
    story.append(Paragraph(
        f"All works below were completed by licensed electricans at {site_name}, {site_addr}. "
        f"A Certificate of Electrical Safety will be issued upon finalisation.", intro))
    story.append(Spacer(1, 3*mm))
    for item in data.get("scopeItems", []):
        story += scope_card(
            item.get("quoteRef"), item.get("title", "Works Completed"),
            item.get("description", "")
        )
    story.append(Spacer(1, 4*mm))

    # WHAT'S INCLUDED
    story += section_header("WHAT'S INCLUDED IN THIS JOB")
    included = data.get("whatsIncluded") or [
        "Supply and installation of all electrical fittings and fixtures (as listed in the quote)",
        "Certificate of electrical safety upon completion",
        "All work carried out by licensed electricians, following Australian standards",
    ]
    not_included = data.get("whatsNotIncluded") or  ["Any items or work not listed in the quantity breakdown"]
    inc_rows = []
    for i in range(0, len(included), 2):
        l = checklist_row(included[i], True)
        r = checklist_row(included[i+1], True) if i+1 < len(included) else ["", ""]
        inc_rows.append([l[0], l[1], r[0], r[1]])
    if inc_rows:
        story.append(Table(inc_rows,
                            colWidths=[6*mm, BODY_W/2-8*mm, 6*mm, BODY_W/2-8*mm],
                            style=TableStyle([
                                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_BG]),
                                ("GRID", (0, 0), (-1, -1), 0.3, MID_GREY),
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("TOPPADDING", (0, 0), (-1, -1), 5),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ])))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("<b>Not Included:</b>", bold))
    story.append(Spacer(1, 1*mm))
    for item in not_included:
        row = checklist_row(item, False)
        story.append(Table([[row[0], row[1]]],
                             colWidths=[6*mm, BODY_W - 6*mm],
                             style=TableStyle([
                                 ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("TOPPADDING", (0, 0), (-1, -1), 3),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 6),
                             ])))
    story.append(Spacer(1, 4�mm))

    # PHOTOS
    photos = [
        p for p in data.get("photoPaths", [])
        if os.path.exists(p) and os.path.splitext(p)[1].lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ]
    if photos:
        story += section_header("PHOTO DOCUMENTATION — WORKS COMPLETED")
        story.append(Paragraph(
            f"The following photographs document the completed works on-site at {site_name}, {site_addr}.",
            intro))
        story.append(Spacer(1, 3*mm))
        for i, pp in enumerate(photos):
            if i > 0:
                story.append(PageBreak())
            story += photo_page(
                pp,
                f"Site Photo {i+1}",
                f"Works completed at {site_name}, {site_addr}."
            )

    # SIGN-OFF
    story.append(PageBreak())
    story += section_header("COMPLETION SIGN-OFF")
    story.append(Paragraph(
        "By signing below, both parties confirm that all works described in this report "
        "have been completed to the agreed scope and in accordance with Australian Standards. "
        "A Certificate of Electrical Safety will be forwarded upon finalisation.", intro))
    story.append(Spacer(1, 5*mm))

    hs = ParagraphStyle("hdr", fontName="Helvetica-Bold", fontSize=9,
                         textColor=WHITE, alignment=TA_CENTER)
    lb = ParagraphStyle("lbl", fontName="Helvetica-Bold", fontSize=8, textColor=DARK_GREY)
    vl = ParagraphStyle("val", fontName="Helvetica", fontSize=9, leading=22)
    cw = BODY_W / 2 - 2*mm

    def sig_col(name_val):
        return Table(
            [[Paragraph("Name:", lb)], [Paragraph(name_val, vl)],
             [Paragraph("Signature:", lb)], [Paragraph(" ", vl)],
             [Paragraph("Date:", lb)], [Paragraph("_____ / _____ / _____", vl)]],
            colWidths=[cw],
            style=TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )

    client_name = customer.get("name", "")
    sd = [
        [Paragraph("CLIENT SIGN-OFF", hs), Paragraph("SMITH &amp; WINTERS ELECTP�ICAL", hs)],
        [sig_col(client_name), sig_col("_________________________")]
    ]
    story.append(Table(sd, colWidths=[cw, cw],
                        style=TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), SECTION_BG),
                            ("BACKGROUND", (1, 0), (1, 0), DARK_RED),
                            ("GRID", (0, 0), (-1, -1), 0.4, MIDG_GREY),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("TOPPADDING", (0, 0), (-1, 0), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("LINEBELOW", (0, -1), (-1, -1), 1, YELLOW),
                        ]), hAlign="LEFT"))
    story.append(Spacer(1, 10*mm))

    # Thank you
    tys = ParagraphStyle("ty", fontName="Helvetica-Oblique", fontSize=10,
                          leading=16, textColor=DARK_GREY, alignment=TA_CENTER)
    story.append(Table(
        [[Paragraph(
            "Thank you for choosing Smith &amp; Winters Electrical. We appreciate your business "
            "and look forward to working with you again. If you have any questions about the "
            "works completed please don't hesitate to get in touch.", tys)]],
        colWidths=[BODY_W],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 0.5, MID_GREY),
        ])
    ))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF written to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: buildPdf.py <job.json> <output.pdf> <logo.png>")
        sys.exit(1)
    build(sys.argv[1], sys.argv[2], sys.argv[3])
