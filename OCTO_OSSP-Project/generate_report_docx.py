import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>\n'
            f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>\n'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)

def generate_simple_report():
    doc = Document()

    # 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base Styles
    COLOR_BLACK = RGBColor(0, 0, 0)
    COLOR_DARK = RGBColor(30, 30, 30)

    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Arial'
    font.size = Pt(11)
    font.color.rgb = COLOR_DARK

    # ---------------------------------------------------------
    # TITLE & HEADER
    # ---------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t1 = p_title.add_run("FORGESHELL PROJECT REPORT\n")
    r_t1.font.size = Pt(20)
    r_t1.font.bold = True
    r_t1.font.color.rgb = COLOR_BLACK

    r_t2 = p_title.add_run("Linux Inter-Process Communication Using Pipes and FIFOs\n")
    r_t2.font.size = Pt(14)
    r_t2.font.bold = True
    r_t2.font.color.rgb = COLOR_DARK

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s = p_sub.add_run("Project Report: Linux IPC using Unnamed Pipes and Named FIFOs\n")
    r_s.font.size = Pt(11)
    r_s.font.italic = True

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Helper for Headings
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = COLOR_BLACK
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_BLACK
        return p

    def add_code(text):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(text)
        r.font.name = 'Consolas'
        r.font.size = Pt(9.5)
        r.font.color.rgb = COLOR_BLACK
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ---------------------------------------------------------
    # 1. PROBLEM STATEMENT
    # ---------------------------------------------------------
    add_h1("1. Problem Statement")
    doc.add_paragraph(
        "Inter-Process Communication (IPC) is an essential mechanism in Linux operating systems that allows multiple processes "
        "to exchange data and coordinate their activities. Since processes normally operate in separate memory spaces, a controlled "
        "communication mechanism is required for transferring information between them.\n\n"
        "The objective of this project is to implement and demonstrate Inter-Process Communication using Pipes and FIFOs in Linux. "
        "The project focuses on understanding how processes can communicate through kernel-managed communication channels without directly "
        "accessing each other's memory.\n\n"
        "The implementation demonstrates two important IPC mechanisms: Pipes, primarily used for communication between related processes "
        "such as a parent and child process, and FIFOs (Named Pipes), which can be used for communication between processes that do not necessarily "
        "have a parent-child relationship."
    )

    # ---------------------------------------------------------
    # 2. OBJECTIVES
    # ---------------------------------------------------------
    add_h1("2. Objectives")
    doc.add_paragraph(
        "• Understand the concept of Inter-Process Communication in Linux.\n"
        "• Study the working mechanism of unnamed pipes.\n"
        "• Implement communication between a parent and child process using a pipe.\n"
        "• Understand and implement Named Pipes (FIFOs).\n"
        "• Demonstrate communication between independent processes using FIFOs.\n"
        "• Use Linux system calls such as pipe(), fork(), read(), write(), close(), mkfifo(), and open().\n"
        "• Understand how data flows between processes through kernel-managed buffers.\n"
        "• Test the communication mechanisms using multiple test cases.\n"
        "• Demonstrate the practical importance of IPC in Linux-based applications."
    )

    # ---------------------------------------------------------
    # 3. SELECTED COMMANDS AND THEIR WORKFLOW
    # ---------------------------------------------------------
    add_h1("3. Selected Commands and Their Workflow")

    add_h2("3.1 pipe()")
    doc.add_paragraph(
        "The pipe() system call creates an unnamed pipe. It returns two file descriptors: fd[0] for reading and fd[1] for writing."
    )
    add_code("int fd[2];\npipe(fd);\nfd[0] -> Read end\nfd[1] -> Write end")
    doc.add_paragraph("Data written using fd[1] can be read using fd[0].\nWorkflow: Process A -> write() -> Pipe -> read() -> Process B")

    add_h2("3.2 fork()")
    doc.add_paragraph(
        "The fork() system call creates a new child process. After fork(), the parent and child processes can use the pipe descriptors inherited from the parent."
    )
    add_code("pid_t pid = fork();")

    add_h2("3.3 write()")
    doc.add_paragraph("The write() system call sends data into the pipe.")
    add_code("write(fd[1], message, strlen(message) + 1);")

    add_h2("3.4 read()")
    doc.add_paragraph("The read() system call receives data from the pipe into a buffer.")
    add_code("read(fd[0], buffer, sizeof(buffer));")

    add_h2("3.5 close()")
    doc.add_paragraph(
        "Unused pipe descriptors should be closed to avoid unnecessary resource usage and to allow correct end-of-file behavior."
    )
    add_code("close(fd[0]);\nclose(fd[1]);")

    add_h2("3.6 mkfifo()")
    doc.add_paragraph("The mkfifo() system call creates a named pipe in the Linux filesystem.")
    add_code("mkfifo(\"myfifo\", 0666);")
    doc.add_paragraph("The FIFO can be verified from the terminal using:")
    add_code("ls -l myfifo")

    add_h2("3.7 open()")
    doc.add_paragraph("A FIFO can be opened for reading or writing.")
    add_code("open(\"myfifo\", O_RDONLY);   /* Reader */\nopen(\"myfifo\", O_WRONLY);   /* Writer */")

    add_h2("3.8 Compilation and Execution")
    add_code(
        "gcc pipe.c -o pipe\n"
        "./pipe\n"
        "gcc fifo_writer.c -o fifo_writer\n"
        "gcc fifo_reader.c -o fifo_reader"
    )

    # ---------------------------------------------------------
    # 4. IMPLEMENTATION
    # ---------------------------------------------------------
    add_h1("4. Implementation")

    add_h2("4.1 Module 1 - IPC Using Pipe")
    doc.add_paragraph(
        "The first implementation uses an unnamed pipe to establish communication between a parent and child process."
    )
    add_code(
        "Parent Process      |    pipe()      |    fork()\n"
        "   /   \\\n"
        "Parent  Child\n"
        "  |       |\n"
        "write() read()\n"
        "  |       |\n"
        "  +--Pipe-+"
    )
    doc.add_paragraph("Sample implementation:")
    add_code(
        "#include <stdio.h>\n"
        "#include <unistd.h>\n"
        "#include <string.h>\n"
        "#include <sys/wait.h>\n\n"
        "int main() {\n"
        "    int fd[2];\n"
        "    char buffer[100];\n"
        "    pipe(fd);\n"
        "    pid_t pid = fork();\n"
        "    if (pid > 0) {\n"
        "        close(fd[0]);\n"
        "        char message[] = \"Hello from Parent\";\n"
        "        write(fd[1], message, strlen(message) + 1);\n"
        "        close(fd[1]);\n"
        "        wait(NULL);\n"
        "    }\n"
        "    else if (pid == 0) {\n"
        "        close(fd[1]);\n"
        "        read(fd[0], buffer, sizeof(buffer));\n"
        "        printf(\"Child received: %s\\n\", buffer);\n"
        "        close(fd[0]);\n"
        "    }\n"
        "    return 0;\n"
        "}"
    )
    doc.add_paragraph("Expected output:")
    add_code("Child received: Hello from Parent")

    add_h2("4.2 Module 2 - IPC Using FIFO")
    doc.add_paragraph(
        "Unlike an unnamed pipe, a FIFO has a name in the filesystem and can be accessed by separate processes."
    )
    add_code(
        "Terminal 1                 Terminal 2\n"
        "FIFO Writer                FIFO Reader\n"
        "    |                          |\n"
        "  open()                     open()\n"
        "    |                          |\n"
        "  write()                    read()\n"
        "    |                          |\n"
        "    +-------- myfifo ---------+"
    )
    doc.add_paragraph(
        "The writer opens the FIFO in write mode and transmits data. The reader opens the FIFO in read mode and receives the data."
    )

    # ---------------------------------------------------------
    # 5. DETAILED DESCRIPTION OF THE IMPLEMENTATION
    # ---------------------------------------------------------
    add_h1("5. Detailed Description of the Implementation")

    add_h2("5.1 Pipe-Based Communication")
    doc.add_paragraph(
        "The pipe implementation starts by creating a pipe using pipe(fd). The pipe provides two file descriptors: "
        "fd[0] for reading and fd[1] for writing. The fork() system call then creates a child process.\n\n"
        "The parent process closes the read end, creates a message, writes the message into the pipe, closes the write end, "
        "and waits for the child. The child closes the write end, reads the message, displays it, and closes the read end. "
        "This demonstrates one-way communication from the parent to the child."
    )

    add_h2("5.2 FIFO-Based Communication")
    doc.add_paragraph(
        "A FIFO is created using mkfifo(\"myfifo\", 0666). Unlike an unnamed pipe, the FIFO has a filesystem name and can therefore "
        "be opened by independent processes."
    )
    add_code(
        "Writer:\n"
        "int fd = open(\"myfifo\", O_WRONLY);\n"
        "write(fd, message, strlen(message) + 1);\n\n"
        "Reader:\n"
        "int fd = open(\"myfifo\", O_RDONLY);\n"
        "read(fd, buffer, sizeof(buffer));"
    )
    doc.add_paragraph("After communication is complete, both processes close the FIFO descriptor.")

    add_h2("5.3 Difference Between Pipe and FIFO")

    t_diff = doc.add_table(rows=7, cols=3)
    t_diff.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_diff)
    diff_headers = ["Feature", "Pipe", "FIFO"]
    diff_widths = [Inches(2.0), Inches(2.2), Inches(2.3)]

    for idx, text in enumerate(diff_headers):
        cell = t_diff.cell(0, idx)
        cell.width = diff_widths[idx]
        set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.bold = True
        r.font.size = Pt(10)

    diff_data = [
        ["Type", "Unnamed IPC", "Named IPC"],
        ["Filesystem name", "No", "Yes"],
        ["Typical communication", "Related processes", "Independent processes"],
        ["Creation", "pipe()", "mkfifo()"],
        ["Access", "File descriptors", "File descriptors"],
        ["Persistence", "Exists while in use", "FIFO file remains until removed"]
    ]

    for r_idx, row in enumerate(diff_data):
        for c_idx, text in enumerate(row):
            cell = t_diff.cell(r_idx + 1, c_idx)
            cell.width = diff_widths[c_idx]
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if c_idx == 0:
                r.font.bold = True

    # ---------------------------------------------------------
    # 6. TEST CASES AND RESULTS
    # ---------------------------------------------------------
    add_h1("6. Test Cases and Results")

    t_tc = doc.add_table(rows=9, cols=4)
    t_tc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_tc)
    tc_headers = ["Test Case", "Description", "Expected Result", "Result"]
    tc_widths = [Inches(1.0), Inches(2.3), Inches(2.4), Inches(0.8)]

    for idx, text in enumerate(tc_headers):
        cell = t_tc.cell(0, idx)
        cell.width = tc_widths[idx]
        set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.bold = True
        r.font.size = Pt(10)

    tc_data = [
        ["TC01", "Create a pipe", "Pipe should be created successfully", "PASS"],
        ["TC02", "Create child using fork()", "Child process should be created", "PASS"],
        ["TC03", "Parent sends message through pipe", "Child should receive message", "PASS"],
        ["TC04", "Child reads data from pipe", "Correct message should be displayed", "PASS"],
        ["TC05", "Create FIFO using mkfifo()", "Named FIFO should be created", "PASS"],
        ["TC06", "Writer sends data through FIFO", "Data should reach reader", "PASS"],
        ["TC07", "Reader receives FIFO data", "Correct message should be displayed", "PASS"],
        ["TC08", "Close communication descriptors", "Resources should be released correctly", "PASS"]
    ]

    for r_idx, row in enumerate(tc_data):
        for c_idx, text in enumerate(row):
            cell = t_tc.cell(r_idx + 1, c_idx)
            cell.width = tc_widths[c_idx]
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if c_idx == 0 or c_idx == 3:
                r.font.bold = True

    add_h2("Test Case Details")

    doc.add_paragraph("Test Case 1 - Pipe Creation")
    add_code("pipe(fd);")
    doc.add_paragraph("Expected: Pipe created successfully. Result: PASS.")

    doc.add_paragraph("Test Case 2 - Parent-to-Child Communication")
    add_code("Input: Hello from Parent\nChild received: Hello from Parent")
    doc.add_paragraph("Result: PASS.")

    doc.add_paragraph("Test Case 3 - FIFO Creation")
    add_code("mkfifo(\"myfifo\", 0666)\nls -l myfifo")
    doc.add_paragraph("Expected: A named FIFO named myfifo is present. Result: PASS.")

    doc.add_paragraph("Test Case 4 - FIFO Communication")
    add_code("Writer sends: Hello from FIFO Writer\nReader received: Hello from FIFO Writer")
    doc.add_paragraph("Result: PASS.")

    doc.add_paragraph("Test Case 5 - Multiple Messages")
    doc.add_paragraph("The writer sends Message 1, Message 2, and Message 3. The reader receives the transmitted messages in sequence.")
    add_code("Message 1\nMessage 2\nMessage 3")
    doc.add_paragraph("Result: PASS.")

    # ---------------------------------------------------------
    # 7. CONCLUSION
    # ---------------------------------------------------------
    add_h1("7. Conclusion")
    doc.add_paragraph(
        "The Linux Inter-Process Communication Using Pipes and FIFOs project successfully demonstrates two fundamental IPC mechanisms available in Linux. "
        "The pipe implementation demonstrates communication between related processes, particularly a parent and child process created using fork(). "
        "The FIFO implementation extends this concept by allowing communication between independent processes through a named communication channel.\n\n"
        "Through this project, the working of important Linux system calls such as pipe(), fork(), read(), write(), close(), mkfifo(), and open() was studied and implemented.\n\n"
        "The test cases demonstrate that data can be transferred between processes using both mechanisms. The project also provides a practical understanding of process synchronization, "
        "file descriptors, kernel-managed communication buffers, and resource management.\n\n"
        "Overall, the project provides a foundation for understanding more advanced IPC mechanisms used in Linux applications, operating systems, servers, and distributed software environments."
    )

    output_path = r"c:\Users\G Jashwanth Reddy\Downloads\DBMS Project\OCTO_OSSP-project\PROJECT_REPORT.docx"
    doc.save(output_path)
    print(f"Simple report document saved successfully to: {output_path}")

if __name__ == "__main__":
    generate_simple_report()
