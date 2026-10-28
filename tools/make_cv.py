#!/usr/bin/env python3
"""
make_cv.py -- render cv.md and cover-letter.md files to ATS-friendly PDFs.

Job portals want a PDF, not markdown. This keeps the layout plain on purpose:
no tables, no columns, no header/footer, standard fonts, real selectable text,
which is what an applicant tracking system can actually parse.

  python3 tools/make_cv.py                      # every folder in applications/
  python3 tools/make_cv.py applications/acme-*  # just one
  python3 tools/make_cv.py me/cv                # your base CV
"""
import glob, os, re, sys

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

NAME = ParagraphStyle('name', fontName='Helvetica-Bold', fontSize=17, leading=20,
                      spaceAfter=2, alignment=TA_LEFT)
CONTACT = ParagraphStyle('contact', fontName='Helvetica', fontSize=8.5, leading=11,
                         spaceAfter=1, textColor='#333333')
H2 = ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=10, leading=12,
                    spaceBefore=9, spaceAfter=3, textColor='#1F3864')
H3 = ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=9.5, leading=12,
                    spaceBefore=6, spaceAfter=1)
BODY = ParagraphStyle('body', fontName='Helvetica', fontSize=9, leading=11.5, spaceAfter=2)
BULLET = ParagraphStyle('bullet', parent=BODY, leftIndent=9, bulletIndent=1, spaceAfter=1.5)
ITALIC = ParagraphStyle('italic', parent=BODY, fontName='Helvetica-Oblique',
                        textColor='#444444', spaceAfter=3)


def inline(t):
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)


def build(md_path, pdf_path):
    lines = open(md_path, encoding='utf-8').read().split('\n')
    flow, in_header = [], True
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith('# '):
            flow.append(Paragraph(inline(line[2:]), NAME))
        elif line.startswith('## '):
            in_header = False
            flow.append(Paragraph(inline(line[3:]).upper(), H2))
            flow.append(HRFlowable(width='100%', thickness=0.6, color='#1F3864',
                                   spaceBefore=1, spaceAfter=4))
        elif line.startswith('### '):
            flow.append(Paragraph(inline(line[4:]), H3))
        elif line.startswith('- '):
            flow.append(Paragraph(inline(line[2:]), BULLET, bulletText='•'))
        elif in_header:
            flow.append(Paragraph(inline(line), CONTACT))
        else:
            flow.append(Paragraph(inline(line), ITALIC))
    if flow and isinstance(flow[0], Paragraph):
        flow.insert(1, Spacer(1, 1))
    SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=13 * mm, bottomMargin=13 * mm,
                      leftMargin=15 * mm, rightMargin=15 * mm,
                      title=os.path.basename(pdf_path).replace('.pdf', ''),
        author='Candidate').build(flow)


LETTER = ParagraphStyle('letter', fontName='Helvetica', fontSize=10.5, leading=14.5, spaceAfter=9)


def build_letter(md_path, pdf_path):
    """A cover letter: '# Name' and contact lines on top, then plain paragraphs."""
    blocks = open(md_path, encoding='utf-8').read().strip().split('\n\n')
    flow = []
    for b in blocks:
        b = b.strip()
        if b.startswith('# '):
            head = b.split('\n')
            flow.append(Paragraph(inline(head[0][2:]), NAME))
            for c in head[1:]:
                flow.append(Paragraph(inline(c), CONTACT))
            flow.append(Spacer(1, 12))
        else:
            flow.append(Paragraph(inline(b).replace('\n', '<br/>'), LETTER))
    SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm,
                      leftMargin=20 * mm, rightMargin=20 * mm,
                      title=os.path.basename(pdf_path).replace('.pdf', ''),
                      author='Candidate').build(flow)


def main():
    pats = sys.argv[1:] or ['applications/*']
    dirs = sorted({d for p in pats for d in glob.glob(p) if os.path.isdir(d)})
    for d in dirs:
        for md, pdf, fn in (('cv.md', 'CV.pdf', build), ('cover-letter.md', 'Cover-Letter.pdf', build_letter)):
            src = os.path.join(d, md)
            if os.path.exists(src):
                out = os.path.join(d, pdf)
                fn(src, out)
                print(f'{out}  ({os.path.getsize(out)//1024} KB)')


if __name__ == '__main__':
    main()
