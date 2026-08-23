#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import html


OUT = Path("submission/Coleman_Chase_CSE543_Fuzz_Them_All_Project/Coleman_Chase_CSE543_Fuzz_Them_All_Project.docx")


def esc(text):
    return html.escape(text, quote=True)


def run(text, bold=False, size=None, font=None):
    props = []
    if bold:
        props.append("<w:b/>")
    if size:
        props.append(f'<w:sz w:val="{size}"/>')
    if font:
        props.append(f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"


def para(text="", style=None, align=None, spacing_after=160):
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    if spacing_after is not None:
        ppr.append(f'<w:spacing w:after="{spacing_after}"/>')
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    return f"<w:p>{ppr_xml}{run(text)}</w:p>"


def heading(text, level=1):
    return para(text, style=f"Heading{level}", spacing_after=120)


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def code_para(text):
    return para(text, style="Code", spacing_after=120)


def table(rows):
    grid = (
        "<w:tblGrid>"
        '<w:gridCol w:w="1100"/><w:gridCol w:w="1700"/>'
        '<w:gridCol w:w="1500"/><w:gridCol w:w="5100"/>'
        "</w:tblGrid>"
    )
    tbl_pr = (
        "<w:tblPr>"
        '<w:tblStyle w:val="TableGrid"/>'
        '<w:tblW w:w="9400" w:type="dxa"/>'
        '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
        "</w:tblPr>"
    )
    body = []
    for row_index, row in enumerate(rows):
        cells = []
        for cell in row:
            shade = '<w:shd w:fill="EDEDED"/>' if row_index == 0 else ""
            tc_pr = f'<w:tcPr><w:tcW w:w="2350" w:type="dxa"/>{shade}</w:tcPr>'
            cells.append(f"<w:tc>{tc_pr}{para(cell, spacing_after=0)}</w:tc>")
        body.append(f"<w:tr>{''.join(cells)}</w:tr>")
    return f"<w:tbl>{tbl_pr}{grid}{''.join(body)}</w:tbl>"


def document_xml():
    rows = [
        ["Level", "Status", "Crash Input Size", "Notes"],
        ["1", "Solved", "198 bytes", "Verified with /challenge/challenge < crash_0."],
        ["2", "Solved", "414 bytes", "Found using repeated characters and numeric edge cases."],
        ["3", "Solved", "210 bytes", "Found through mutated byte input testing."],
        ["4", "Solved", "300 bytes", "Found during randomized mutation testing."],
        ["5", "Solved", "312 bytes", "Saved and verified as crash_0."],
        ["6", "Solved", "1150 bytes", "Larger crashing input found by the same fuzzer strategy."],
        ["7", "Solved", "105 bytes", "Generated testcase triggered a segmentation fault."],
        ["8", "Solved", "186 bytes", "Verified through the challenge wrapper."],
        ["9", "Attempted, unresolved", "N/A", "Argv-focused fuzzer completed a deterministic pass and reached about 28,000 mutation cases in a 10 minute run without producing crash_0."],
        ["10", "Solved", "966 bytes", "Found with the same mutation based approach and verified with the challenge wrapper."],
    ]

    parts = [
        para("Fuzz Them All Project", style="Title", align="center", spacing_after=240),
        para("Chase Coleman", align="center", spacing_after=80),
        para("CSE543", align="center", spacing_after=80),
        para("July 5, 2026", align="center", spacing_after=480),
        page_break(),
        heading("Submission Overview"),
        para("This submission includes a Python mutation fuzzer, solved test program notes, and exact crashing inputs for levels 1 through 8 and level 10. Level 9 was attempted but is not included as a solved level because the fuzzer continued running without discovering a verified crashing input despite repeated attempts."),
        heading("Dependencies"),
        para("The fuzzer is implemented in Python 3 and uses only Python standard library modules: os, random, signal, subprocess, and sys. It expects the target program to be executable at /challenge/prog in the pwn.college environment unless a different target is supplied with the FUZZ_TARGET environment variable or as the first command-line argument."),
        heading("Input Generation Strategy"),
        para("The fuzzer uses mutation based input generation. It starts from a seed corpus containing empty input, small strings, integer boundary values, format string tokens, path traversal strings, repeated bytes, and selected binary byte values. For each test case, it randomly selects one seed and applies one or more mutations."),
        para("The mutation operators include bit flips, byte/string insertion, deletion, overwrite, appending interesting values, and splicing random bytes. Generated inputs are capped at 4096 bytes to avoid runaway test cases. The fuzzer executes the target with each generated input through standard input, suppresses normal output, and treats fatal signal exits and common crash exit statuses as crashes. When a crash is detected, it saves the exact input as crash_0 for verification and submission."),
        heading("Level Summary"),
        table(rows),
        heading("Level Notes"),
    ]

    notes = [
        ("Level 1", "Level 1 used the mutation strategy above. The fuzzer found a 198 byte input that reliably crashed the target program. The crash was verified in pwn.college with /challenge/challenge < crash_0."),
        ("Level 2", "Level 2 reused the mutation strategy against the new target binary. The fuzzer generated long inputs containing repeated characters and numeric edge cases, then found a crashing input that reproduced under /challenge/challenge < crash_0."),
        ("Level 3", "Level 3 reused the same fuzzer. It discovered a crashing mutated byte input, saved it as crash_0, and the crash was verified through /challenge/challenge."),
        ("Level 4", "Level 4 reused the mutation based fuzzer and found a crashing input during randomized testing. The saved testcase reproduced the segmentation fault when submitted to /challenge/challenge."),
        ("Level 5", "Level 5 reused the same strategy against the level 5 binary. The fuzzer found a crashing testcase, saved it as crash_0, and verification reproduced the crash."),
        ("Level 6", "Level 6 reused the same fuzzer and found a larger crashing input. The testcase was saved as crash_0 and verified with /challenge/challenge < crash_0."),
        ("Level 7", "Level 7 used the mutation based fuzzer on the level 7 target. A generated testcase triggered a segmentation fault and was verified with the challenge wrapper."),
        ("Level 8", "Level 8 reused the same fuzzer and found a crashing input that reproduced with /challenge/challenge < crash_0."),
        ("Level 9", "Level 9 was attempted with an argv-focused mutation strategy adapted for the target. The fuzzer performed a deterministic seed pass and then continued through mutation testing for a 10 minute run, reaching about 28,000 argv cases without producing a crash_0 file or a verified crash. Because no crashing input was found despite repeated attempts, I could not produce an exact .crash file for this level."),
        ("Level 10", "Level 10 reused the same mutation based fuzzer. It found a crashing input that reproduced under /challenge/challenge < crash_0."),
    ]
    for title, text in notes:
        parts.append(heading(title, level=2))
        parts.append(para(text))

    body = "".join(parts)
    sect = (
        "<w:sectPr>"
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'
        "</w:sectPr>"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}{sect}</w:body>"
        "</w:document>"
    )


def styles_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="24"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="40"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="30"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="26"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:rPr><w:rFonts w:ascii="Menlo" w:hAnsi="Menlo"/><w:sz w:val="20"/></w:rPr></w:style>'
        '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="777777"/><w:left w:val="single" w:sz="4" w:space="0" w:color="777777"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="777777"/><w:right w:val="single" w:sz="4" w:space="0" w:color="777777"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="777777"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="777777"/></w:tblBorders></w:tblPr></w:style>'
        "</w:styles>"
    )


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr("word/_rels/document.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        z.writestr("word/document.xml", document_xml())
        z.writestr("word/styles.xml", styles_xml())
    print(OUT)


if __name__ == "__main__":
    main()
