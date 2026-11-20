import re
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def add_hyperlink_to_paragraph(paragraph, url: str, text: str, color="2563EB", bold=False):
    """
    Appends a clickable hyperlink element to a python-docx paragraph.
    """
    try:
        # Sanitize URL
        url_clean = url.strip()
        if not (url_clean.startswith("http://") or url_clean.startswith("https://") or url_clean.startswith("mailto:")):
            if "@" in url_clean:
                url_clean = f"mailto:{url_clean}"
            else:
                url_clean = f"https://{url_clean}"

        part = paragraph.part
        r_id = part.relate_to(url_clean, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

        hyperlink = OxmlElement('w:hyperlink')
        hyperlink.set(qn('r:id'), r_id)

        new_run = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')

        if color:
            c = OxmlElement('w:color')
            c.set(qn('w:val'), color)
            rPr.append(c)

        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rPr.append(u)

        if bold:
            b = OxmlElement('w:b')
            rPr.append(b)

        new_run.append(rPr)
        new_run.text = text
        hyperlink.append(new_run)
        paragraph._p.append(hyperlink)
        return True
    except Exception:
        # Fallback to plain text run if relationship fails
        run = paragraph.add_run(f" {text} ({url}) ")
        run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
        return False

def add_styled_text_runs(paragraph, text: str, default_color=None, base_size=10, is_bold=False):
    """
    Parses inline markdown like **bold text** and [Link Text](url) within a line
    and appends corresponding runs or hyperlinks to the paragraph.
    """
    # Pattern to match [Link](url) or **bold text**
    token_pattern = r'(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*)'
    tokens = re.split(token_pattern, text)

    for token in tokens:
        if not token:
            continue

        # Check markdown link [Label](URL)
        link_match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', token)
        if link_match:
            label = link_match.group(1).strip()
            url = link_match.group(2).strip()
            add_hyperlink_to_paragraph(paragraph, url, label, color="2563EB", bold=True)
            continue

        # Check bold **word**
        bold_match = re.match(r'\*\*([^*]+)\*\*', token)
        if bold_match:
            bold_text = bold_match.group(1)
            run = paragraph.add_run(bold_text)
            run.bold = True
            run.font.size = Pt(base_size)
            if default_color:
                run.font.color.rgb = default_color
            continue

        # Regular plain text
        run = paragraph.add_run(token)
        run.bold = is_bold
        run.font.size = Pt(base_size)
        if default_color:
            run.font.color.rgb = default_color

def add_heading_bottom_border(paragraph, hex_color="2563EB", sz="8"):
    """
    Adds a clean horizontal accent line under a heading paragraph.
    """
    try:
        pPr = paragraph._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), sz)
        bottom.set(qn('w:space'), '4')
        bottom.set(qn('w:color'), hex_color)
        pBdr.append(bottom)
        pPr.append(pBdr)
    except Exception:
        pass

def create_docx(content: str, filename: str) -> bool:
    """
    Builds a beautifully styled, ATS-compliant Microsoft Word (.docx) resume
    from structured markdown content.
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        doc = Document()

        # Set 0.5-inch margins (standard ATS resume format)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)

        # Set Normal style typography
        style_normal = doc.styles['Normal']
        font = style_normal.font
        font.name = 'Calibri'
        font.size = Pt(10)
        font.color.rgb = RGBColor(0x33, 0x41, 0x55)  # Slate 700

        # Colors
        COLOR_PRIMARY = RGBColor(0x0F, 0x17, 0x2A)    # Deep Navy
        COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)      # Muted Slate
        COLOR_DARK = RGBColor(0x1E, 0x29, 0x3B)       # Slate 800

        lines = content.split('\n')
        elements_count = 0

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # 1. Title / Candidate Name (# Name)
            if trimmed.startswith('# '):
                name = trimmed[2:].strip()
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(4)
                
                run = p.add_run(name)
                run.bold = True
                run.font.size = Pt(21)
                run.font.color.rgb = COLOR_PRIMARY
                elements_count += 1

            # 2. Contact Info Subtitle (directly under title)
            elif (trimmed.startswith('**') and trimmed.endswith('**') and elements_count == 1) or \
                 (any(ind in trimmed.lower() for ind in ['@', 'linkedin.com', 'github.com', ' | ']) and elements_count <= 2):
                clean_contact = trimmed.strip('*')
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(10)

                add_styled_text_runs(p, clean_contact, default_color=COLOR_MUTED, base_size=9.5)
                elements_count += 1

            # 3. Major Section Header (## Section)
            elif trimmed.startswith('## '):
                section_title = trimmed[3:].strip()
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.keep_with_next = True

                run = p.add_run(section_title.upper())
                run.bold = True
                run.font.size = Pt(12)
                run.font.color.rgb = COLOR_PRIMARY

                # Add modern accent divider line beneath heading
                add_heading_bottom_border(p, hex_color="2563EB", sz="8")
                elements_count += 1

            # 4. Role / Sub-heading (### Role / Company / Timeline)
            elif trimmed.startswith('### '):
                sub_title = trimmed[4:].strip()
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(5)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.keep_with_next = True

                add_styled_text_runs(p, sub_title, default_color=COLOR_DARK, base_size=10.5, is_bold=True)
                elements_count += 1

            # 5. Bullet Points (- Bullet or * Bullet)
            elif trimmed.startswith('- ') or trimmed.startswith('* ') or trimmed.startswith('• '):
                bullet_content = trimmed[2:].strip()
                p = doc.add_paragraph(style='List Bullet')
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(2.5)
                p.paragraph_format.line_spacing = 1.15

                add_styled_text_runs(p, bullet_content, default_color=COLOR_DARK, base_size=10)
                elements_count += 1

            # 6. Regular Body Paragraph
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.15

                add_styled_text_runs(p, trimmed, default_color=COLOR_DARK, base_size=10)
                elements_count += 1

        doc.save(filename)
        return True
    except Exception as e:
        print(f"Error creating DOCX: {e}")
        # Fallback to basic document
        try:
            fallback_doc = Document()
            for line in content.split('\n'):
                if line.strip():
                    fallback_doc.add_paragraph(line.strip())
            fallback_doc.save(filename)
            return True
        except Exception as fb_err:
            print(f"Fallback DOCX also failed: {fb_err}")
            return False
