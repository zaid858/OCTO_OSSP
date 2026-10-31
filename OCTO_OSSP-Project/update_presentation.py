"""
update_presentation.py
Updates OSSP_IPC_Project_Presentation.pptx with all latest project advancements:
- Single Shared Linux Named FIFO (linux-implementation/myfifo)
- Real-Time Node.js Backend Bridge (Vite middleware / server.js)
- In-Flight Display File (myfifo_display.txt) & Immediate Truncation Triggered by Process B Receipt
- Race-condition safe clearing with message matching
- Real-time disk file monitor badge in UI
- 2 New dedicated slides for System Architecture and Truncation Mechanics
"""

import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PPTX_PATH = "OCTO_OSSP-Project/OSSP_IPC_Project_Presentation.pptx"

def update_presentation():
    if not os.path.exists(PPTX_PATH):
        print(f"Error: {PPTX_PATH} not found.")
        sys.exit(1)

    prs = pptx.Presentation(PPTX_PATH)
    print(f"Opened {PPTX_PATH} with {len(prs.slides)} slides.")

    # Colors
    c_blue = RGBColor(29, 78, 216)       # #1d4ed8
    c_slate_dark = RGBColor(15, 23, 42)  # #0f172a
    c_slate_text = RGBColor(51, 65, 85)  # #334155
    c_slate_muted = RGBColor(100, 116, 139) # #64748b
    c_cyan = RGBColor(8, 145, 178)       # #0891b2
    c_green = RGBColor(16, 185, 129)     # #10b981
    c_purple = RGBColor(124, 58, 237)    # #7c3aed
    c_white = RGBColor(255, 255, 255)
    c_border = RGBColor(203, 213, 225)   # #cbd5e1

    # =========================================================================
    # SLIDE 1: Title Slide Updates
    # =========================================================================
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "Mapping Project Design" in p.text:
                    p.text = "Mapping Project Design & Code to Course Outcomes: CO1 (Syscall Abstraction), CO2 (Process Control), CO3 (IPC Mechanisms) | Shared Linux Named FIFO & Real-Time Kernel Bridge"
                    if p.font:
                        p.font.size = Pt(13)

    # =========================================================================
    # SLIDE 2: Course Outcomes Overview Table
    # =========================================================================
    s2 = prs.slides[1]
    for shape in s2.shapes:
        if shape.has_table:
            table = shape.table
            # Row 1: CO1
            table.cell(1, 2).text = "User/Kernel mode boundary traps via POSIX syscall interface (pipe, mkfifo, open, read, write, close). Real kernel execution under WSL/Ubuntu with live step-by-step activity timeline."
            # Row 3: CO3
            table.cell(3, 2).text = "Implementation of Anonymous Pipes for related processes and a Single Shared Persistent Named FIFO (linux-implementation/myfifo) bridging native C programs with web simulator, featuring immediate in-flight file truncation."

    # =========================================================================
    # SLIDE 3: CO1 Implementation: OS Layered Abstraction & Syscalls
    # =========================================================================
    s3 = prs.slides[2]
    # Shape 4 is Card 1, Shape 6 is Card 2, Shape 8 is Card 3
    if len(s3.shapes) >= 9:
        # Card 2: Syscall Interface
        tf = s3.shapes[6].text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "⚙️ POSIX Syscall Interface"
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = c_slate_dark

        items_c2 = [
            "• Core POSIX Calls: pipe(), fork(), mkfifo(), open(), read(), write(), close(), lstat().",
            "• POSIX Verification: Verifies FIFO integrity via lstat() and S_ISFIFO() before opening, guaranteeing it is a true FIFO special node.",
            "• Kernel Protection: Strict abstraction shields user code from virtual memory paging, inode management, and hardware ring buffers."
        ]
        for it in items_c2:
            p = tf.add_paragraph()
            p.text = it
            p.font.size = Pt(11)
            p.font.color.rgb = c_slate_text

        # Card 3: Syscall Execution Trace
        tf3 = s3.shapes[8].text_frame
        tf3.clear()
        p0 = tf3.paragraphs[0]
        p0.text = "🔍 Real Kernel Syscall Trace"
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = c_slate_dark

        items_c3 = [
            "• Zero Mock Simulation: Web Simulator communicates directly with real Linux kernel FIFO through a dedicated Node.js WSL bridge.",
            "• 6-Step Execution Timeline: Traces lstat(S_ISFIFO) -> open(O_WRONLY) -> write(payload) -> open(O_RDONLY) -> read(buffer) -> close(fd).",
            "• Activity Checklist: Live interactive UI ticks off completed kernel steps with exact descriptor numbers and byte counts."
        ]
        for it in items_c3:
            p = tf3.add_paragraph()
            p.text = it
            p.font.size = Pt(11)
            p.font.color.rgb = c_slate_text

    # =========================================================================
    # SLIDE 6: CO3 Implementation: Named FIFO Mechanics
    # =========================================================================
    s6 = prs.slides[5]
    if len(s6.shapes) >= 7:
        # Shape 4: Card 1 (Architecture)
        tf_s6_1 = s6.shapes[4].text_frame
        tf_s6_1.clear()
        p0 = tf_s6_1.paragraphs[0]
        p0.text = "1. Shared Named FIFO Architecture (myfifo)"
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = c_slate_dark

        items_s6_1 = [
            "• Unified Shared Path",
            "  Single real Linux FIFO at 'linux-implementation/myfifo' shared by both Web Simulator & Ubuntu C binaries.",
            "• S_ISFIFO Verification",
            "  Checks node with lstat(); guarantees POSIX named pipe (prw-r--r--) and refuses to overwrite regular files.",
            "• Persistent Lifecycle",
            "  FIFO remains present across sessions; no deletion after each message, matching real production system daemons.",
            "• Concurrency Protection",
            "  Exclusive session locks via flock() prevent simultaneous conflicting reader/writer executions."
        ]
        for it in items_s6_1:
            p = tf_s6_1.add_paragraph()
            p.text = it
            p.font.size = Pt(10.5)
            p.font.color.rgb = c_slate_text

        # Shape 6: Card 2 (Rendezvous & System Calls)
        tf_s6_2 = s6.shapes[6].text_frame
        tf_s6_2.clear()
        p0 = tf_s6_2.paragraphs[0]
        p0.text = "2. Rendezvous Handshake & System Calls"
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = c_slate_dark

        items_s6_2 = [
            "✓ mkfifo(path, 0666)",
            "  Creates real POSIX FIFO node in filesystem directory with read/write permissions.",
            "✓ open(path, O_WRONLY) [Process A]",
            "  Writer opens FIFO. Blocks in kernel until Reader attaches (unblocks on handshake).",
            "✓ open(path, O_RDONLY) [Process B]",
            "  Reader attaches to the same node, completing rendezvous and releasing both processes.",
            "✓ write() & read()",
            "  Transfers exact payload through kernel buffer; Process B confirms receipt instantly."
        ]
        for it in items_s6_2:
            p = tf_s6_2.add_paragraph()
            p.text = it
            p.font.size = Pt(10.5)
            p.font.color.rgb = c_slate_text

    # =========================================================================
    # SLIDE 7: Comparative Matrix Table
    # =========================================================================
    s7 = prs.slides[6]
    for shape in s7.shapes:
        if shape.has_table:
            table = shape.table
            table.cell(2, 2).text = "Dedicated persistent node: linux-implementation/myfifo"
            table.cell(4, 2).text = "Persistent: Retained on filesystem across sessions; verified via lstat() & S_ISFIFO"

    # =========================================================================
    # SLIDE 8: Interactive Web Simulator Design
    # =========================================================================
    s8 = prs.slides[7]
    if len(s8.shapes) >= 9:
        # Card 1
        tf_s8_1 = s8.shapes[4].text_frame
        tf_s8_1.clear()
        p0 = tf_s8_1.paragraphs[0]
        p0.text = "🎨 Modern Visual Laboratory"
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = c_slate_dark

        items_s8_1 = [
            "• Sleek dark aesthetic with cyan/purple accents, responsive glass cards, and status indicators.",
            "• Dual interactive modes: Anonymous Pipe Simulator vs Single Shared FIFO Visualizer.",
            "• Live Disk File Monitor: Real-time badge inside FIFO box reflecting exact 0-byte file status on disk."
        ]
        for it in items_s8_1:
            p = tf_s8_1.add_paragraph()
            p.text = it
            p.font.size = Pt(11)
            p.font.color.rgb = c_slate_text

        # Card 2
        tf_s8_2 = s8.shapes[6].text_frame
        tf_s8_2.clear()
        p0 = tf_s8_2.paragraphs[0]
        p0.text = "⚡ Real Linux Backend Bridge"
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = c_slate_dark

        items_s8_2 = [
            "• Local Node.js Backend Bridge (server.js & Vite middleware) wired directly to WSL2/Ubuntu.",
            "• Real Kernel Traps: Triggers actual C binaries via run_transfer.sh in < 1.2s total execution.",
            "• Process B displays actual received payload confirmed from Linux read(), eliminating mock strings."
        ]
        for it in items_s8_2:
            p = tf_s8_2.add_paragraph()
            p.text = it
            p.font.size = Pt(11)
            p.font.color.rgb = c_slate_text

        # Card 3
        tf_s8_3 = s8.shapes[8].text_frame
        tf_s8_3.clear()
        p0 = tf_s8_3.paragraphs[0]
        p0.text = "📄 In-Flight File Immediate Clear"
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = c_slate_dark

        items_s8_3 = [
            "• myfifo_display.txt mirrors message payload on disk strictly while in transit.",
            "• Immediate Truncation: Process B confirmation (bytes_read > 0) immediately truncates file to 0 bytes without delays.",
            "• Race Protection: clear_display_file_if_matching() ensures older cleanups never erase newer rapid messages."
        ]
        for it in items_s8_3:
            p = tf_s8_3.add_paragraph()
            p.text = it
            p.font.size = Pt(11)
            p.font.color.rgb = c_slate_text

    # =========================================================================
    # SLIDE 9: Execution & Verification Guide
    # =========================================================================
    s9 = prs.slides[8]
    if len(s9.shapes) >= 7:
        tf_s9_1 = s9.shapes[4].text_frame
        tf_s9_1.clear()
        p0 = tf_s9_1.paragraphs[0]
        p0.text = "1. Running the Web Simulator"
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = c_slate_dark

        items_s9_1 = [
            "# Project Root: OCTO_OSSP-Project/",
            "npm install            # Install Vite & dev tools",
            "npm run dev            # Start Vite + Linux Backend API",
            "# Opens automatically at: http://localhost:5173",
            "# VS Code One-Click: Press F5 to launch debugger",
            "# In-Editor View: Ctrl+Shift+P -> Simple Browser: Show"
        ]
        for it in items_s9_1:
            p = tf_s9_1.add_paragraph()
            p.text = it
            p.font.size = Pt(10)
            p.font.color.rgb = c_slate_text

        tf_s9_2 = s9.shapes[6].text_frame
        tf_s9_2.clear()
        p0 = tf_s9_2.paragraphs[0]
        p0.text = "2. Running Native C Programs (Linux/WSL)"
        p0.font.bold = True
        p0.font.size = Pt(14)
        p0.font.color.rgb = c_slate_dark

        items_s9_2 = [
            "cd OCTO_OSSP-Project/linux-implementation",
            "make all               # Compiles pipe_demo, fifo_writer, fifo_reader",
            "# Manual Shared FIFO (Two Terminal Windows):",
            "Terminal 1:  ./fifo_reader     # Process B: opens O_RDONLY",
            "Terminal 2:  ./fifo_writer     # Process A: opens O_WRONLY & writes",
            "# Coordinated Script: ./run_transfer.sh 'Message' (<1.2s)",
            "# Persistent Log:    cat received_messages.txt"
        ]
        for it in items_s9_2:
            p = tf_s9_2.add_paragraph()
            p.text = it
            p.font.size = Pt(10)
            p.font.color.rgb = c_slate_text

    # =========================================================================
    # SLIDE 10: Conclusion & Attainment
    # =========================================================================
    s10 = prs.slides[9]
    if len(s10.shapes) >= 5:
        tf_s10 = s10.shapes[4].text_frame
        tf_s10.clear()
        bullets = [
            ("🎯 CO1 Attainment — Layered Abstraction & Real Syscalls",
             "Demonstrated genuine User Space to Kernel Space transitions via direct system calls (pipe, mkfifo, open, read, write, close, lstat) with zero mock fakes and real-time execution logging."),
            ("🎯 CO2 Attainment — Unix Process Control & Hygiene",
             "Mastered Unix primitives (fork, wait, exit) for child process control, descriptor table inheritance, closing unused ends to guarantee EOF, and reaping to prevent zombie processes."),
            ("🎯 CO3 Attainment — Unified IPC & Immediate Synchronization",
             "Successfully implemented Anonymous Pipes for related streams and a Single Shared Linux Named FIFO (linux-implementation/myfifo) uniting a modern web lab with native Ubuntu C programs, featuring immediate 0-delay display file truncation."),
            ("🚀 Comprehensive Deliverable & Impact",
             "Bridged low-level Linux systems programming with an intuitive web laboratory simulator for complete conceptual, visual, and practical mastery.")
        ]
        for title, desc in bullets:
            p_t = tf_s10.add_paragraph() if tf_s10.paragraphs[0].text else tf_s10.paragraphs[0]
            p_t.text = title
            p_t.font.bold = True
            p_t.font.size = Pt(12)
            p_t.font.color.rgb = c_blue

            p_d = tf_s10.add_paragraph()
            p_d.text = desc
            p_d.font.size = Pt(10.5)
            p_d.font.color.rgb = c_slate_text

    # =========================================================================
    # NEW SLIDE 11: System Integration & Architectural Bridge
    # =========================================================================
    slide_layout = prs.slide_layouts[6] # Blank layout
    s11 = prs.slides.add_slide(slide_layout)
    s11.background.fill.solid()
    s11.background.fill.fore_color.rgb = RGBColor(248, 250, 252)

    # Accent bar
    bar = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.5), Inches(0.8), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = c_blue
    bar.line.fill.background()

    # Category header
    tb_cat = s11.shapes.add_textbox(Inches(1.7), Inches(0.4), Inches(10.0), Inches(0.3))
    p = tb_cat.text_frame.paragraphs[0]
    p.text = "OPERATING SYSTEMS & SYSTEM PROGRAMMING — ADVANCED INTEGRATION"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = c_slate_muted

    # Title
    tb_title = s11.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
    p = tb_title.text_frame.paragraphs[0]
    p.text = "System Integration: Real-Time Web-to-Kernel Architecture"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = c_slate_dark

    # 3 Cards Layout
    card_width = Inches(3.6)
    card_height = Inches(5.0)
    card_top = Inches(1.7)
    gap = Inches(0.3)
    start_left = Inches(0.8)

    cards_s11 = [
        ("🌐 1. Web Presentation Layer",
         [
             ("Interactive Web Client", "Built with modern HTML5/ES6 and responsive glassmorphism UI."),
             ("Process A (Writer)", "Captures user input message and initiates real transmission."),
             ("Channel Animation", "Animates data packet gliding into the central FIFO buffer with live status indicators."),
             ("Process B (Reader)", "Displays actual received payload read from the real Linux kernel FIFO.")
         ]),
        ("⚡ 2. Local Backend Bridge",
         [
             ("Node.js API Bridge", "Lightweight backend middleware (server.js & Vite) listening on port 5173."),
             ("REST Endpoints", "/api/fifo/write (transfer), /api/fifo/status, /api/fifo/display, /api/fifo/reset."),
             ("Session Locking (flock)", "Non-blocking locks prevent concurrent session collisions."),
             ("Coordinated Transfer", "Executes run_transfer.sh in WSL2/Ubuntu in < 1.2s total round-trip time.")
         ]),
        ("🐧 3. Native Linux Kernel IPC",
         [
             ("Single Shared FIFO", "Real POSIX named pipe at linux-implementation/myfifo (prw-r--r--)."),
             ("POSIX Verification", "lstat() and S_ISFIFO() ensure node is a real FIFO special file."),
             ("Native C Binaries", "fifo_writer.c and fifo_reader.c execute real kernel traps (open, read, write, close)."),
             ("Dual-Client Support", "Ubuntu terminal and Web Simulator use the exact same filesystem object.")
         ])
    ]

    for idx, (card_title, card_items) in enumerate(cards_s11):
        left = start_left + idx * (card_width + gap)
        # Background card
        card_bg = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, card_top, card_width, card_height)
        card_bg.fill.solid()
        card_bg.fill.fore_color.rgb = c_white
        card_bg.line.color.rgb = c_border
        card_bg.line.width = Pt(1)

        # Text inside card
        tb = s11.shapes.add_textbox(left + Inches(0.2), card_top + Inches(0.2), card_width - Inches(0.4), card_height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = card_title
        p0.font.bold = True
        p0.font.size = Pt(13.5)
        p0.font.color.rgb = c_slate_dark

        for item_title, item_desc in card_items:
            p_t = tf.add_paragraph()
            p_t.text = f"• {item_title}"
            p_t.font.bold = True
            p_t.font.size = Pt(11)
            p_t.font.color.rgb = c_blue

            p_d = tf.add_paragraph()
            p_d.text = f"  {item_desc}"
            p_d.font.size = Pt(10)
            p_d.font.color.rgb = c_slate_text

    # =========================================================================
    # NEW SLIDE 12: In-Flight Display File & Immediate Truncation Mechanics
    # =========================================================================
    s12 = prs.slides.add_slide(slide_layout)
    s12.background.fill.solid()
    s12.background.fill.fore_color.rgb = RGBColor(248, 250, 252)

    # Accent bar
    bar12 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.5), Inches(0.8), Inches(0.08))
    bar12.fill.solid()
    bar12.fill.fore_color.rgb = c_blue
    bar12.line.fill.background()

    # Category header
    tb_cat12 = s12.shapes.add_textbox(Inches(1.7), Inches(0.4), Inches(10.0), Inches(0.3))
    p = tb_cat12.text_frame.paragraphs[0]
    p.text = "OPERATING SYSTEMS & SYSTEM PROGRAMMING — ADVANCED INTEGRATION"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = c_slate_muted

    # Title
    tb_title12 = s12.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
    p = tb_title12.text_frame.paragraphs[0]
    p.text = "In-Flight File Synchronization & Immediate Truncation"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = c_slate_dark

    cards_s12 = [
        ("🎯 1. The Engineering Requirement",
         [
             ("Visual File Mirroring", "myfifo_display.txt mirrors payload on disk while in transit through FIFO."),
             ("Zero Stale Data", "File must become completely empty (0 bytes) as soon as Process B completes read()."),
             ("No Arbitrary Delays", "Prohibits sleep(), setTimeout(), or fixed delay timers for cleanup."),
             ("Disk File Integrity", "Ensures actual disk sectors are truncated, not just frontend visual hiding.")
         ]),
        ("⚡ 2. Immediate Receipt Trigger",
         [
             ("Read Confirmation Trigger", "fifo_reader.c triggers clear_display_file_if_matching() immediately upon read() > 0."),
             ("Atomic Truncation", "ftruncate(fileno(f), 0) instantly zeroes the file descriptor on disk."),
             ("Dual-Environment Sync", "Truncates both Linux ext4 and Windows NTFS file mirrors simultaneously."),
             ("Failed-Read Safety", "If read() returns <= 0 (timeout/error), clearing is aborted to preserve state.")
         ]),
        ("🛡️ 3. Race & Sequence Protection",
         [
             ("Payload Matching Check", "Compares current file content with received message before truncating."),
             ("Protects Newer Messages", "Prevents an asynchronous cleanup of a previous message from erasing a newer message."),
             ("Persistent History Log", "received_messages.txt records timestamped payload and source for auditing."),
             ("Web Live Status Badge", "UI displays real-time disk file state: [EMPTY (0 bytes)] / [In Transit] / [CLEARED].")
         ])
    ]

    for idx, (card_title, card_items) in enumerate(cards_s12):
        left = start_left + idx * (card_width + gap)
        card_bg = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, card_top, card_width, card_height)
        card_bg.fill.solid()
        card_bg.fill.fore_color.rgb = c_white
        card_bg.line.color.rgb = c_border
        card_bg.line.width = Pt(1)

        tb = s12.shapes.add_textbox(left + Inches(0.2), card_top + Inches(0.2), card_width - Inches(0.4), card_height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = card_title
        p0.font.bold = True
        p0.font.size = Pt(13.5)
        p0.font.color.rgb = c_slate_dark

        for item_title, item_desc in card_items:
            p_t = tf.add_paragraph()
            p_t.text = f"• {item_title}"
            p_t.font.bold = True
            p_t.font.size = Pt(11)
            p_t.font.color.rgb = c_blue

            p_d = tf.add_paragraph()
            p_d.text = f"  {item_desc}"
            p_d.font.size = Pt(10)
            p_d.font.color.rgb = c_slate_text

    # Save presentation
    prs.save(PPTX_PATH)
    print(f"Successfully updated {PPTX_PATH}! Total slides now: {len(prs.slides)}")

if __name__ == "__main__":
    update_presentation()
