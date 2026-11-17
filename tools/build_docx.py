#!/usr/bin/env python3
"""DOCX CV/cover-letter builder helpers - generate native Word documents, never via
PDF-to-DOCX conversion (that produces floating text frames and references the LaTeX
template's fonts, which Word does not have - see commits b5d3962/1be3a5c).

Confirmed house style (Nov 2026, Splunk-MarkusKlein.docx round-trip):
- Calibri default font, #1F5C99 accent color, bottom-border section headings.
- CV header: bold 20pt accent-blue centered role/company headline line, blank
  line, then "Markus Klein" bold at body size (NOT a large masthead) underneath.
- Role/company and title/dates lines use a borderless 2-column TABLE with fixed
  column widths (add_role_header), never a right tab stop - a tab stop's wrap
  point is computed differently by Word and LibreOffice and can split a word
  mid-character in Word even when it renders fine in LibreOffice.
- Several same-shape entries in one section (e.g. multiple Education degrees)
  go in a single multi-row table (add_grouped_entries_table), not one table
  per entry.

This file's bottom build_cv()/build_cover_letter() functions hold the Cisco/Splunk
AVP application's specific content as a worked example. For a new application,
write a new small script that imports the helper functions above the "=== content
below is per-application ===" marker and supplies that application's own content -
do not hand-build DOCX from scratch or convert from PDF."""

from docx import Document
from docx.shared import Pt, Twips, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ACCENT = RGBColor(0x1F, 0x5C, 0x99)


def set_cell_border_bottom(p):
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:color'), '1F5C99')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '2')
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_section_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    set_cell_border_bottom(p)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = ACCENT
    return p


def _set_table_borders_none(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'nil')
        borders.append(el)
    tblPr.append(borders)


def _set_cell_margins(table, top=0, bottom=0, start=0, end=0):
    tbl = table._tbl
    tblPr = tbl.tblPr
    mar = OxmlElement('w:tblCellMar')
    for tag, val in (('top', top), ('start', start), ('bottom', bottom), ('end', end)):
        el = OxmlElement(f'w:{tag}')
        el.set(qn('w:w'), str(val))
        el.set(qn('w:type'), 'dxa')
        mar.append(el)
    tblPr.append(mar)


def add_role_header(doc, company, location, title, dates):
    """Company/location and title/dates as a 2x2 borderless, fixed-width
    table: a table column deterministically reserves its width in every
    renderer, unlike a right tab stop, whose wrap threshold varies between
    Word and LibreOffice and can split a word mid-character."""
    section = doc.sections[0]
    usable_twips = int((section.page_width - section.left_margin - section.right_margin) / 635)
    left_w = int(usable_twips * 0.68)
    right_w = usable_twips - left_w

    table = doc.add_table(rows=2, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    _set_table_borders_none(table)
    _set_cell_margins(table)

    for col, width in ((0, left_w), (1, right_w)):
        table.columns[col].width = Twips(width)
        for row in table.rows:
            row.cells[col].width = Twips(width)

    def _fill(cell, text, bold=False, italic=False, align_right=False, space_before=0, space_after=0):
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        if align_right:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic

    _fill(table.rows[0].cells[0], company, bold=True, space_before=5)
    _fill(table.rows[0].cells[1], location, bold=True, align_right=True, space_before=5)
    _fill(table.rows[1].cells[0], title, italic=True, space_after=2)
    _fill(table.rows[1].cells[1], dates, italic=True, align_right=True, space_after=2)


def add_grouped_entries_table(doc, entries):
    """Several same-shape entries (e.g. multiple Education degrees) as one
    multi-row borderless table instead of one separate table per entry -
    the house-style convention confirmed with Markus, Nov 2026.
    entries: list of (name, location, subtitle, dates) tuples."""
    section = doc.sections[0]
    usable_twips = int((section.page_width - section.left_margin - section.right_margin) / 635)
    left_w = int(usable_twips * 0.68)
    right_w = usable_twips - left_w

    table = doc.add_table(rows=2 * len(entries), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    _set_table_borders_none(table)
    _set_cell_margins(table)

    for col, width in ((0, left_w), (1, right_w)):
        table.columns[col].width = Twips(width)
        for row in table.rows:
            row.cells[col].width = Twips(width)

    def _fill(cell, text, bold=False, italic=False, align_right=False, space_before=0, space_after=0):
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        if align_right:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic

    for i, (name, location, subtitle, dates) in enumerate(entries):
        r0, r1 = 2 * i, 2 * i + 1
        _fill(table.rows[r0].cells[0], name, bold=True, space_before=5)
        _fill(table.rows[r0].cells[1], location, bold=True, align_right=True, space_before=5)
        _fill(table.rows[r1].cells[0], subtitle, italic=True, space_after=2)
        _fill(table.rows[r1].cells[1], dates, italic=True, align_right=True, space_after=2)


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style='List Paragraph')
        p.paragraph_format.space_after = Pt(4)
        pPr = p._p.get_or_add_pPr()
        numPr = OxmlElement('w:numPr')
        ilvl = OxmlElement('w:ilvl')
        ilvl.set(qn('w:val'), '0')
        numId = OxmlElement('w:numId')
        numId.set(qn('w:val'), '1')
        numPr.append(ilvl)
        numPr.append(numId)
        pPr.append(numPr)
        if isinstance(item, tuple):
            label, rest = item
            rb = p.add_run(label + ': ')
            rb.bold = True
            p.add_run(rest)
        else:
            p.add_run(item)


# === content below is per-application: Cisco/Splunk AVP worked example ===


def build_cv(path, role_title):
    """role_title: the target role/company headline, e.g.
    'Area Vice President, Solutions Engineering - Splunk Germany'.
    House style (confirmed with Markus, Nov 2026): a bold, 20pt, accent-blue,
    centered role headline leads the document; the name follows underneath,
    bold but at body size, not as a large masthead."""
    doc = Document()
    section = doc.sections[0]
    section.page_width = Twips(11906)
    section.page_height = Twips(16838)
    section.left_margin = Twips(900)
    section.right_margin = Twips(900)
    section.top_margin = Twips(720)
    section.bottom_margin = Twips(720)

    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(4)
    style.paragraph_format.line_spacing = 1.0

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(role_title)
    r.bold = True
    r.font.size = Pt(20)
    r.font.color.rgb = ACCENT

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Markus Klein')
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run('Auenstr. 203, 85354 Freising, Germany')
    r.font.size = Pt(10)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run('+49 155 630 90 736  •  m_klein@web.de  •  ')
    r.font.size = Pt(10)
    add_hyperlink(p, 'https://www.linkedin.com/in/virtualmkl', 'LinkedIn', size=10)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "Solutions Engineering executive with 25+ years leading technical sales organisations in the "
        "Germany region, including second-line leadership of managers-of-managers teams (up to 20+ "
        "Solution Engineering Managers, 190+ engineers) at VMware and Citrix. Twice led the exact "
        "transformation this role calls for: converting a reactive, product-focused presales function "
        "into a proactive, value-selling business driver, once during the VMware by Broadcom "
        "post-acquisition integration and once at Citrix. Deep domain expertise across cybersecurity, "
        "enterprise infrastructure, cloud and AI, with a track record of exceeding revenue targets, "
        "engaging VP/CxO stakeholders across Enterprise, Public Sector and Service Provider segments, "
        "and developing technical talent into business leaders."
    )

    add_section_heading(doc, 'Core Competencies')
    add_bullets(doc, [
        ('Solutions Engineering Leadership (Leader of Leaders)',
         'Scaling and leading managers-of-managers organisations across EMEA (up to 190 engineers, '
         '20+ SE Managers), with a career-development framework adopted by 700+ SEs that held '
         'attrition below 5%'),
        ('Pre-Sales Transformation & Value Selling',
         'Converted presales from a reactive, technical-support function into a proactive, '
         'value-selling organisation at both VMware and Citrix, driving multi-solution/SaaS adoption '
         'and consistent double-digit annual revenue growth'),
        ('Post-Acquisition Organisational Integration (M&A)',
         'Rebuilt the EMEA Partner & Commercial Solutions Engineering organisation from the ground up '
         'following the Broadcom acquisition of VMware, re-establishing the channel at 200% of target '
         'in the first fiscal year'),
        ('Executive & C-Level Engagement',
         'Trusted-advisor relationships with VP/CxO buyers across Enterprise, Public Sector, Service '
         'Provider and Commercial segments – the exact customer-segment mix named in this role; '
         'VMware press spokesperson and keynote speaker to audiences of 500-1,000+'),
        ('Germany & DACH Market Leadership',
         'Munich-based throughout career; built and led German/DACH Solutions Engineering teams at '
         'Citrix (15 to 30+) and VMware (60 to 110+ direct)'),
        ('Cybersecurity, Cloud & AI Domain Expertise',
         'Identity & Access Management, Zero Trust, micro-segmentation, hybrid cloud, and holistic '
         'security strategy'),
    ])

    add_section_heading(doc, 'Professional Experience')

    add_role_header(doc, '', 'Freising, Germany',
                     'Presales Leadership Advisor & Interim Executive (Self-employed)', '2025–Present')
    add_bullets(doc, [
        'Advises technology companies on building and scaling high-performance Presales and Solution '
        'Consulting organisations',
        'Engagements cover interim leadership, go-to-market strategy, presales team design, and '
        'value-selling frameworks',
        'Coaches SE managers moving from technical delivery into people leadership',
    ])

    add_role_header(doc, 'VMware by Broadcom', 'Munich, Germany',
                     'Regional Executive Leader, Solutions Engineering EMEA', '2023–2025')
    add_bullets(doc, [
        'Built the newly established EMEA Partner and Commercial Solution Engineering team from the '
        'ground up following the Broadcom acquisition, leading 30+ Partner SEs across all EMEA regions',
        'Re-established the VMware by Broadcom channel in EMEA post-acquisition, delivering 200% of '
        'target in the first fiscal year',
        'Launched the EMEA Knights program, activating the strongest VMware consultants across the '
        'partner ecosystem',
        'Senior member of the EMEA leadership team for the Partner & Commercial division, aligning '
        'go-to-market strategy and competitive positioning with regional sales targets',
    ])

    add_role_header(doc, 'VMware', 'Munich, Germany',
                     'Senior Director, Solutions Engineering Central Europe', '2014–2023')
    add_bullets(doc, [
        'Grew the direct organization from 60 to 110+ employees, including 20+ Solution Engineering '
        'Managers, plus dotted-line responsibility for 80 further specialists across EMEA (190+ total '
        'oversight) – a leader-of-leaders structure spanning DACH, Eastern Europe, Russia and Israel',
        'Transformed presales from a product-focused to a multi-solution SaaS model, improving customer '
        'success and adoption rates; drove continuous revenue growth >10% YoY, supporting €1B+ in '
        'annual enterprise revenue influence',
        'Reduced team attrition to <5% via a career development framework adopted by 700+ SEs across '
        'EMEA',
        'Delivered C-level trainings and served as VMware press spokesperson and keynote speaker at '
        'major industry events (audiences 500-1,000+)',
    ])

    add_role_header(doc, 'Citrix Systems', 'Greater Munich, Germany',
                     'Director, Systems Engineering Central Europe', '2000–2014')
    add_bullets(doc, [
        'Expanded the DACH SE team from 15 to 30+ members, keeping attrition below 5% while delivering '
        'consistent annual revenue growth >20%',
        'Transformed the team from product-focused to solution-oriented, building go-to-market '
        'frameworks for security solutions (secure access, identity, SSO, MDM) and establishing true '
        'enterprise sales',
    ])

    add_section_heading(doc, 'Education')
    add_grouped_entries_table(doc, [
        ('Hartnack-Schule', 'Offenbach, Germany', 'IT Business Engineer', '1993–1995'),
        ('FH Frankfurt am Main', 'Frankfurt, Germany', 'Studies in Process Engineering', '1989–1992'),
    ])

    add_section_heading(doc, 'Languages')
    doc.add_paragraph('German (native), English (full professional), French (learning).')

    add_section_heading(doc, 'Certifications')
    doc.add_paragraph('Subject Matter Expert – Design Thinking (2022).')

    add_section_heading(doc, 'References')
    doc.add_paragraph('Available upon request.')

    doc.save(path)


def add_hyperlink(paragraph, url, text, size=11):
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0563C1')
    rPr.append(color)
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(size * 2))
    rPr.append(sz)
    new_run.append(rPr)
    t = OxmlElement('w:t')
    t.text = text
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def build_cover_letter(path):
    doc = Document()
    section = doc.sections[0]
    section.page_width = Twips(11906)
    section.page_height = Twips(16838)
    section.left_margin = Twips(900)
    section.right_margin = Twips(900)
    section.top_margin = Twips(900)
    section.bottom_margin = Twips(900)

    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(10)
    style.paragraph_format.line_spacing = 1.0

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Markus Klein')
    r.font.size = Pt(26)
    r.font.color.rgb = ACCENT

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    p.add_run('m_klein@web.de | +49 155 630 90 736 | ')
    add_hyperlink(p, 'https://www.linkedin.com/in/virtualmkl', 'LinkedIn')

    p = doc.add_paragraph('November 17, 2026')
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(14)

    doc.add_paragraph('Dear Hiring Manager,')

    doc.add_paragraph(
        "I am writing to apply for the Area Vice President, Solutions Engineering role for Splunk "
        "Germany. Having spent 25 years building and transforming Solutions Engineering organisations "
        "in this region, most recently leading the post-acquisition rebuild of VMware's EMEA Partner & "
        "Commercial Solutions Engineering organisation under Broadcom, I recognise in this role the "
        "same mandate I have delivered twice before: converting a technical pre-sales function into a "
        "proactive, value-selling business driver during a period of corporate integration."
    )

    doc.add_paragraph(
        "I am drawn to this role because it sits at the center of Cisco's AgenticOps strategy, "
        "unifying Splunk's data platform with Cisco's security and networking stack for the AI era, in "
        "the Germany region I have served, and been based in, throughout my career. My domain depth is "
        "strongest in cybersecurity, identity and cloud infrastructure; observability and large-scale "
        "data platforms are a natural extension of that same value-selling discipline, and one I am "
        "ready to grow into quickly."
    )

    doc.add_paragraph(
        "At VMware and Citrix, I led exactly this kind of transformation, developing leaders of "
        "leaders rather than managing individual contributors directly:"
    )

    add_bullets(doc, [
        ('Leader of leaders',
         "Grew VMware's Central Europe organisation from 60 to 110+ employees across 20+ Solution "
         "Engineering Managers, with dotted-line oversight of 190+ specialists across EMEA"),
        ('Post-M&A integration',
         'Rebuilt the EMEA Partner & Commercial Solutions Engineering team from the ground up after '
         'the Broadcom acquisition, re-establishing the channel at 200% of target in the first fiscal '
         'year'),
        ('Value-selling transformation',
         "Shifted Citrix's and VMware's presales motions from product-focused to solution- and "
         "outcome-oriented, sustaining double-digit annual revenue growth and attrition below 5%"),
    ])

    doc.add_paragraph(
        "I have spent my career making sure Solutions Engineering sits at the table with Sales, "
        "Product and Customer Success, not downstream of them, and I am an experienced executive "
        "communicator: VMware press spokesperson and keynote speaker to audiences of up to 1,000. I am "
        "fluent in German and English and based in the Munich area, with no relocation required."
    )

    doc.add_paragraph(
        "I would welcome the opportunity to discuss how I can help lead this transformation for "
        "Splunk Germany."
    )

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.add_run('Kind regards,')

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(28)
    p.add_run('Markus Klein')

    doc.save(path)


if __name__ == '__main__':
    import sys
    build_cv(sys.argv[1], 'Area Vice President, Solutions Engineering - Splunk Germany')
    build_cover_letter(sys.argv[2])
    print('done')
