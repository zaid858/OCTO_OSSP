"""
set_matter_font_size.py
Sets the font size of all body text / matter across all slides in
OSSP_IPC_Project_Presentation.pptx to 16 pt, while preserving slide titles
and subheadings.
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

PPTX_PATH = "OCTO_OSSP-Project/OSSP_IPC_Project_Presentation.pptx"

def set_matter_size():
    if not os.path.exists(PPTX_PATH):
        print(f"Error: {PPTX_PATH} not found.")
        sys.exit(1)

    prs = pptx.Presentation(PPTX_PATH)
    print(f"Processing {len(prs.slides)} slides in {PPTX_PATH}...")

    total_matter_paras = 0
    total_table_cells = 0

    for idx, slide in enumerate(prs.slides):
        slide_num = idx + 1

        # =====================================================================
        # SLIDE 1: Title Slide
        # =====================================================================
        if slide_num == 1:
            for s_idx, shape in enumerate(slide.shapes):
                if shape.has_text_frame:
                    tf = shape.text_frame
                    for p_idx, p in enumerate(tf.paragraphs):
                        # Shape 1 is category header (subheading): keep as is
                        # Shape 2 P0 is main title (heading): keep as is
                        # Shape 2 P1 is subtitle (subheading): keep as is
                        # Shape 2 P2 is description (matter): set to 16 pt
                        if s_idx == 2 and p_idx >= 2:
                            set_para_font_size(p, Pt(16))
                            total_matter_paras += 1
                        # Shape 4: Author & Stack (matter): set to 16 pt
                        elif s_idx == 4:
                            set_para_font_size(p, Pt(16))
                            total_matter_paras += 1
            continue

        # =====================================================================
        # SLIDE 2 & SLIDE 7: Tables
        # =====================================================================
        for shape in slide.shapes:
            if shape.has_table:
                table = shape.table
                # Row 0 is the table header (heading)
                # Rows 1 to N are data rows (matter) -> set to 16 pt
                for r_idx in range(1, len(table.rows)):
                    for c_idx in range(len(table.columns)):
                        cell = table.cell(r_idx, c_idx)
                        for p in cell.text_frame.paragraphs:
                            set_para_font_size(p, Pt(16))
                            total_table_cells += 1

        # =====================================================================
        # CONTENT SLIDES (SLIDES 3 TO 12): Text Frames & Cards
        # =====================================================================
        for s_idx, shape in enumerate(slide.shapes):
            # Shape 0 is accent bar
            # Shape 1 is top category header (subheading): keep as is
            # Shape 2 is slide main title (heading): keep as is
            if s_idx in [0, 1, 2]:
                continue

            if shape.has_text_frame and not shape.has_table:
                tf = shape.text_frame
                # Skip empty shapes (e.g. background cards)
                if not tf.text.strip():
                    continue

                # Slide 10: Conclusion has alternating section titles & matter
                if slide_num == 10:
                    for p_idx, p in enumerate(tf.paragraphs):
                        # Even indices (0, 2, 4, 6) are section titles (keep 16pt bold)
                        # Odd indices (1, 3, 5, 7) are matter -> set to 16 pt
                        if p_idx % 2 == 1:
                            set_para_font_size(p, Pt(16))
                            total_matter_paras += 1
                        else:
                            # Section title: ensure it's bold and at least 16 pt
                            set_para_font_size(p, Pt(16), keep_bold=True)
                    continue

                # Standard card content shapes:
                # Paragraph 0 is the Card Title / Section Heading (keep as heading, e.g. 16-17pt bold)
                # Paragraphs 1..N are the Matter -> set to 16 pt!
                for p_idx, p in enumerate(tf.paragraphs):
                    if p_idx == 0:
                        # Card heading: keep bold and size around 16.5 pt
                        p.font.bold = True
                        p.font.size = Pt(16.5)
                        for r in p.runs:
                            r.font.bold = True
                            r.font.size = Pt(16.5)
                    else:
                        # Body matter: set font size to 16 pt
                        set_para_font_size(p, Pt(16))
                        total_matter_paras += 1

    prs.save(PPTX_PATH)
    print(f"Done! Updated {total_matter_paras} matter paragraphs and {total_table_cells} table cells to 16 pt.")
    print(f"Saved to {PPTX_PATH}")

def set_para_font_size(p, size, keep_bold=None):
    p.font.size = size
    if keep_bold is not None:
        p.font.bold = keep_bold
    for r in p.runs:
        r.font.size = size
        if keep_bold is not None:
            r.font.bold = keep_bold

if __name__ == "__main__":
    set_matter_size()
