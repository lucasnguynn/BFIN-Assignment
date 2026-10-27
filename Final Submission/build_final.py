#!/usr/bin/env python3
"""Produce a clean, offline and source-checked group submission."""
from pathlib import Path
import csv, json, hashlib, zipfile, re, html
ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent
def csvrows(p):
    with open(p,encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def plain(t):
    return re.sub(r"\[([^\]]+)\]\([^)]+\)",r"\1",t).replace("*","").replace(chr(96),"")
def blocks():
    out=[]
    for raw in (HERE/"Committee Memo.md").read_text().splitlines():
        s=raw.strip()
        if not s:continue
        if s.startswith("# "):out.append(("title",plain(s[2:])));continue
        if s.startswith("## "):out.append(("section",plain(s[3:])));continue
        if s.startswith("|"):
            cells=[plain(t.strip()) for t in s.strip("|").split("|")]
            if cells and not all(set(c).issubset(set("-: ")) for c in cells):out.append(("table",cells))
            continue
        out.append(("text",plain(s)))
    return out

def verify_sources():
    f={r["Metric"]:r for r in csvrows(ROOT/"bond_funding/outputs/revised/revised_funding_summary.csv")}
    assert abs(float(f["Bond cost"]["Principal matching"])-5784228)<.01
    assert abs(float(f["Net equity purchases"]["Principal matching"])-6209562.437562439)<.01
    assert abs(float(f["Required CAGR"]["Principal matching"])-.04795107162727974)<1e-10
    r=json.loads((ROOT/"portfolio_construction/Portfolio Final/Sources/Observed Summary.json").read_text())
    assert abs(float(r["policy"]["CAGR_after_initial_cost"])-.176864)<.0001
    assert abs(float(r["VTI"]["CAGR_after_initial_cost"])-.224469)<.0001
    qa=json.loads((ROOT/"quality_assurance/qa_report.json").read_text())
    assert qa["counts"]["FAIL"]==0

def memo():
    from docx import Document
    from docx.shared import Inches,Pt
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate,Paragraph,PageBreak,Table,TableStyle,Spacer
    from pypdf import PdfReader
    doc=Document();sec=doc.sections[0]
    sec.left_margin=sec.right_margin=Inches(.65)
    sec.top_margin=sec.bottom_margin=Inches(.62)
    style=doc.styles["Normal"];style.font.name="Aptos";style.font.size=Pt(9)
    style.paragraph_format.space_after=Pt(6)
    styles={
      "title":ParagraphStyle("t",fontName="Helvetica-Bold",fontSize=14,leading=18,spaceAfter=9),
      "section":ParagraphStyle("s",fontName="Helvetica-Bold",fontSize=11,leading=14,spaceAfter=8),
      "text":ParagraphStyle("b",fontName="Helvetica",fontSize=8.55,leading=12.15,spaceAfter=7),
      "cell":ParagraphStyle("c",fontName="Helvetica",fontSize=7.9,leading=10)}
    story=[];sections=0;table=[]
    def flush():
        nonlocal table
        if not table:return
        n=len(table[0])
        cells=[[Paragraph(html.escape(x),styles["cell"]) for x in row] for row in table]
        t=Table(cells,colWidths=[(A4[0]-88)/n]*n,repeatRows=1)
        t.setStyle(TableStyle([
          ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#EEEEEE")),
          ("LINEBELOW",(0,0),(-1,0),.5,colors.gray),
          ("VALIGN",(0,0),(-1,-1),"TOP"),
          ("TOPPADDING",(0,0),(-1,-1),4),
          ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.extend([t,Spacer(1,6)])
        tb=doc.add_table(rows=len(table),cols=n);tb.style="Light Shading Accent 1"
        for i,row in enumerate(table):
            for j,x in enumerate(row):tb.cell(i,j).text=x
        table=[]
    for kind,val in blocks():
        if kind=="table":table.append(val);continue
        flush()
        if kind=="section":
            if sections:story.append(PageBreak());doc.add_page_break()
            sections+=1;doc.add_heading(val,2)
        elif kind=="title":doc.add_heading(val,0)
        else:doc.add_paragraph(val)
        story.append(Paragraph(html.escape(val),styles[kind]))
    flush()
    if sections!=8:raise AssertionError(f"Expected eight memo sections, got {sections}")
    doc.save(HERE/"Committee Memo.docx")
    def footer(c,d):
        c.setFont("Helvetica",7);c.setFillGray(.45)
        c.drawString(44,24,"Kappa Foundation | Committee memo")
        c.drawRightString(A4[0]-44,24,str(d.page))
    SimpleDocTemplate(str(HERE/"Committee Memo.pdf"),pagesize=A4,
        leftMargin=44,rightMargin=44,topMargin=42,bottomMargin=43).build(
        story,onFirstPage=footer,onLaterPages=footer)
    pages=len(PdfReader(str(HERE/"Committee Memo.pdf")).pages)
    if pages>8:raise AssertionError(f"Committee memo has {pages} pages; 8 is the maximum including references")
    return pages

SLIDES=[
 ("Recommendation","Fund payments first, then invest for growth.",
  ["Principal matching is our chosen revised funding plan","Keep the original Sample MV stock weights","Net equity USD 6.210m, after a 10bp entry fee","Required 2030 equity CAGR about 4.80%"],"Revised funding and approved stock policy"),
 ("Payment schedule","Total commitments stay at USD 6m.",
  ["2024: USD 2.4m in both schedules","2025: a new USD 1.2m payment","2027: USD 2.4m, down from USD 3.6m","Keep the 2022 case-date information cutoff"],"Trustee mandate update"),
 ("Funding trade-off","Principal matching leaves a larger cash cushion.",
  ["Bond cost USD 5.784m; revised equity USD 6.210m","Coupon funding allows roughly USD 354k more equity","Cash after 2025 payment: USD 396k vs near zero","The bond financing choice is a liquidity judgement"],"Bond cash-flow ledgers"),
 ("Stock allocation","We hold eight stocks, not a broad index.",
  ["AAPL, MSFT and PG each at the 15% stock cap","Technology holdings total 30%","No ETFs in the chosen portfolio","Concentration remains the main risk"],"Frozen decision weights"),
 ("Portfolio methods","Reoptimizing adds little at A = 3.",
  ["Sample MV: 12.05% estimated return; 14.98% volatility","Minimum Variance: 10.86%; 13.15%","Revised principal utility 0.053328705 vs 0.053328718","A = 8.94 compares fixed portfolios only"],"Portfolio comparisons"),
 ("Factor evidence","Market risk and a large-stock tilt drive returns.",
  ["FF3 market beta 0.867 and SMB -0.426","FF3 adjusted R-squared 0.844; CAPM 0.785","Positive historical alpha does not prove skill","Funding-only changes leave normalized factor returns unchanged"],"CAPM and FF3 outputs"),
 ("Downside and goals","Payment certainty does not eliminate equity risk.",
  ["Equity -25% and yields +100bp: 14.42% loss with principal","Coupon-funded alternative: 15.08% modeled loss","These are not the trustees' 12-month warning/review measure","Inflation and buffers change the 2030 hurdle"],"Combined stress and 2030 sensitivity"),
 ("Observed 2023-2025","Selected stocks grew but trailed VTI.",
  ["After-fee CAGR: stocks 17.69%; VTI 22.45%","Monthly-return volatility: 11.80% vs 12.60%","Annualized active return -4.11%; tracking error 6.91%","Later results did not change the original decision"],"Archived Yahoo data, 36 months"),
 ("Implementation","Keep the evidence and decisions clear.",
  ["Track the revised 2024, 2025 and 2027 payments","Review withdrawal-adjusted 12-month losses at 12% and 15%","Case bonds have modeled, not observed, market prices","University acceptance and original emailed hashes remain unverified"],"Decision log and source records")
]
def presentation():
    from pptx import Presentation
    from pptx.util import Inches,Pt
    from pptx.dml.color import RGBColor
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.colors import HexColor
    from pypdf import PdfReader
    ppt=Presentation();ppt.slide_width=Inches(13.333);ppt.slide_height=Inches(7.5)
    charcoal=RGBColor(43,46,49);muted=RGBColor(115,117,120)
    pdf=Canvas(str(HERE/"Presentation.pdf"),pagesize=(960,540))
    def textbox(s,x,y,w,h,t,size,bold=False,col=charcoal):
        tb=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
        tf=tb.text_frame;tf.clear();tf.word_wrap=True;p=tf.paragraphs[0];p.text=t
        p.font.name="Aptos";p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=col
    for index,(title,headline,items,source) in enumerate(SLIDES,1):
        slide=ppt.slides.add_slide(ppt.slide_layouts[6])
        textbox(slide,.65,.55,12,.55,title,27,True)
        textbox(slide,.65,1.36,12,.65,headline,17,True)
        pdf.setFillColor(HexColor("#292929"));pdf.setFont("Helvetica-Bold",26)
        pdf.drawString(49,477,title)
        pdf.setFont("Helvetica-Bold",15);pdf.drawString(49,428,headline)
        pdf.setStrokeColor(HexColor("#CCCCCC"));pdf.line(49,414,912,414)
        for j,item in enumerate(items):
            textbox(slide,.88,2.37+j*.87,11.5,.7,item,16)
            pdf.setFont("Helvetica",14);pdf.drawString(59,363-j*59,"- "+item[:110])
        textbox(slide,.67,7.1,11,.23,"Source: "+source,9,col=muted)
        pdf.setFont("Helvetica",8);pdf.setFillColor(HexColor("#888888"))
        pdf.drawString(49,23,"Source: "+source);pdf.drawRightString(910,23,str(index))
        pdf.showPage()
    ppt.save(HERE/"Presentation.pptx");pdf.save()
    assert len(PdfReader(str(HERE/"Presentation.pdf")).pages)==9

def decisions():
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import A4
    t=ParagraphStyle("entry",fontSize=9.5,leading=14,spaceAfter=12)
    story=[Paragraph("<b>Decision and contributions</b>",t)]
    notes=[
      ("Funding","Group-selected principal matching: 2,400 Beta, 1,200 Gamma, 2,400 Delta."),
      ("Stocks","Original Sample MV weights retained after revised funding."),
      ("Evaluation","The 2023-2025 results are a separate conditional test, not a 2022 model input."),
      ("Human review","Names, dates and approvals are not entered by AI; people must confirm their own work."),
      ("Provenance","Original emailed archive-member hashes and university acceptance have not been independently confirmed."),
      ("Academic integrity","Material AI help was used with code, arithmetic, source checking and editing; contributors must review and explain the output.")
    ]
    for h,b in notes:story.append(Paragraph("<b>"+h+"</b>. "+b,t))
    SimpleDocTemplate(str(HERE/"Decision Record.pdf"),pagesize=A4,
      topMargin=54,leftMargin=48,rightMargin=48).build(story)

def pack():
    analysis=HERE/"Analysis.zip"
    with zipfile.ZipFile(analysis,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(ROOT.rglob("*")):
            if not p.is_file():continue
            rel=p.relative_to(ROOT).as_posix()
            if rel.startswith("Final Submission/"):continue
            if any(part in (".git","__pycache__", ".venv",".pytest_cache") for part in p.parts):continue
            if rel=="portfolio_construction/Portfolio Final/Portfolio Files.zip":continue
            if not (rel.startswith(("bond_funding/","portfolio_construction/","factor_analysis/","quality_assurance/")) or
                    rel in ("README.md","requirements.txt","run_pipeline.py")):continue
            z.write(p,rel)
    assert zipfile.ZipFile(analysis).testzip() is None
    (HERE/"Read Me.txt").write_text(
      "Kappa Foundation group submission\n\n"
      "Read the Committee Memo and Presentation first. Both have editable copies.\n"
      "Analysis.zip holds research code, source records, original decision, models, data, tests and results.\n"
      "Rebuild the source models with python run_pipeline.py after installing requirements.txt.\n"
      "Original emailed ZIP acceptance and people-only signoffs remain unverified.\n"
      "Material AI assistance is disclosed.\n",encoding="utf8")
    items=["Committee Memo.pdf","Committee Memo.docx","Presentation.pdf",
           "Presentation.pptx","Decision Record.pdf","Analysis.zip","Read Me.txt"]
    final=HERE/"Final Submission.zip"
    with zipfile.ZipFile(final,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n in items:z.write(HERE/n,n)
    assert zipfile.ZipFile(final).testzip() is None
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    (HERE/"Checksums.txt").write_text("\n".join(sha(HERE/n)+"  "+n for n in items)+"\n")
    return final

def main():
    verify_sources();pages=memo();presentation();decisions();archive=pack()
    print(json.dumps({"status":"PASS","memo_pages":pages,"slides":9,
        "final_zip_bytes":archive.stat().st_size},indent=2))
if __name__=="__main__":main()
