"""Rebuild the downloadable guide from the website's current editorial content.
Requires beautifulsoup4, reportlab and qrcode. Run from any working directory.
"""
from pathlib import Path
from html import escape
from io import BytesIO
import re
from bs4 import BeautifulSoup, NavigableString
import qrcode
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'pre65/Pre-65-ACA-Strategy-Guide-PY2027.pdf'
SOUP=BeautifulSoup((ROOT/'pre65/index.html').read_text(),'html.parser')
URL='https://samueltrippmedicare-coder.github.io/aca-certification-hub/pre65/'
LOGO=ROOT/'pre65/assets/pinnacle-logo.png'
INK=HexColor('#24272e'); RED=HexColor('#aa0e33'); MUTED=HexColor('#58616b'); LINE=HexColor('#dfe3e7'); PAPER=HexColor('#f5f6f8')
for name,suffix in [('GuideSans','Regular'),('GuideSans-Bold','Bold'),('GuideSans-Italic','Italic'),('GuideSans-BoldItalic','BoldItalic')]:
    pdfmetrics.registerFont(TTFont(name,f'/usr/share/fonts/truetype/liberation/LiberationSans-{suffix}.ttf'))
pdfmetrics.registerFontFamily('GuideSans',normal='GuideSans',bold='GuideSans-Bold',italic='GuideSans-Italic',boldItalic='GuideSans-BoldItalic')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyGuide',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=8,textColor=INK))
styles.add(ParagraphStyle(name='TitleGuide',fontName='Helvetica-Bold',fontSize=26,leading=30,spaceAfter=16,textColor=INK))
styles.add(ParagraphStyle(name='SubGuide',fontName='Helvetica-Bold',fontSize=12,leading=16,spaceBefore=10,spaceAfter=7,textColor=RED,keepWithNext=True))
styles.add(ParagraphStyle(name='SmallGuide',parent=styles['BodyGuide'],fontSize=8,leading=11,textColor=MUTED,spaceAfter=7))
styles.add(ParagraphStyle(name='TableGuide',parent=styles['BodyGuide'],fontSize=9,leading=12,spaceAfter=0))
styles.add(ParagraphStyle(name='BulletGuide',parent=styles['BodyGuide'],leftIndent=12,firstLineIndent=-10,spaceAfter=6))
for style in styles.byName.values():
    if hasattr(style,'fontName'): style.fontName=style.fontName.replace('Helvetica','GuideSans')
def clean(s):
    return s.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u2018',"'").replace('\u2019',"'").replace('\u201c','"').replace('\u201d','"').replace('\u00a0',' ').replace('→','>').replace('✓','')
def inline(n):
    if isinstance(n,NavigableString): return escape(clean(str(n)))
    content=''.join(inline(c) for c in n.children)
    if n.name in ('strong','b'): return '<b>'+content+'</b>'
    if n.name in ('em','i'): return '<i>'+content+'</i>'
    if n.name=='br': return '<br/>'
    if n.name=='a':
        href=n.get('href','')
        if href.startswith('../'): href='https://samueltrippmedicare-coder.github.io/aca-certification-hub/'
        elif href.startswith('#'): href=URL+href
        if href.startswith(('https:','mailto:','tel:')): return '<a color="#aa0e33" href="'+escape(href,quote=True)+'">'+content+'</a>'
    return content
def para(text,style='BodyGuide'): return Paragraph(text,styles[style])
def table(rows,widths,header=True):
    cells=[[para(inline(c) if hasattr(c,'children') else escape(clean(str(c))),'TableGuide') for c in row] for row in rows]
    t=Table(cells,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),.4,LINE)]
    if header: commands.extend([('BACKGROUND',(0,0),(-1,0),PAPER),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#fafbfc')])])
    t.setStyle(TableStyle(commands));return t
def flow(n):
    if isinstance(n,NavigableString): return []
    name=n.name
    if 'kicker' in n.get('class',[]) or name in ('script','form'): return []
    if name=='h2': return [para(inline(n),'TitleGuide')]
    if name in ('h3','summary'): return [para(inline(n),'SubGuide')]
    if name=='p':
        style='SmallGuide' if 'sources' in n.get('class',[]) or 'small' in n.get('class',[]) else 'BodyGuide'
        return [para(inline(n),style)]
    if name in ('ol','ul'):
        return [para((str(i)+'. ' if name=='ol' else '- ')+inline(li),'BulletGuide') for i,li in enumerate(n.find_all('li',recursive=False),1)]
    if name=='table':
        rows=[tr.find_all(['th','td'],recursive=False) for tr in n.find_all('tr')]
        widths=[132,78,306] if len(rows[0])==3 else [128,388]
        return [table(rows,widths),Spacer(1,10)]
    if name=='span' and 'stat' in n.get('class',[]): return [para(inline(n),'SubGuide')]
    result=[]
    for child in n.children: result+=flow(child)
    return result
def section(id): return flow(SOUP.find(id=id))
def chrome(c,doc):
    c.saveState();w,h=doc.pagesize
    if doc.page>1:
        c.setFillColor(RED);c.rect(48,h-38,3,13,fill=1,stroke=0)
        c.setFont('GuideSans-Bold',9);c.setFillColor(INK);c.drawString(59,h-35,'PRE-65 ACA STRATEGY GUIDE  /  PY2027')
        c.drawImage(str(LOGO),454,h-66,width=108,height=65,preserveAspectRatio=True,mask='auto')
        c.linkURL('https://pfsinsurance.com/',(454,h-66,562,h-1),relative=0)
    c.setStrokeColor(LINE);c.line(48,42,w-48,42)
    c.setFillColor(MUTED);c.setFont('GuideSans',8);c.drawString(48,28,'Pinnacle Financial Services | Reviewed November 13, 2026')
    c.drawRightString(w-48,28,str(doc.page));c.restoreState()

pages=[]
logo=Image(str(LOGO),width=156,height=94);logo.hAlign='LEFT'
qrbuf=BytesIO();qrcode.make(URL).save(qrbuf,format='PNG');qrbuf.seek(0)
qr=Image(qrbuf,width=78,height=78)
cover=[logo,Spacer(1,8),para('PLAN YEAR 2027 | AGENT &amp; BROKER RESOURCE','SubGuide'),para('The Pre-65 Retiree<br/>Strategy Guide','TitleGuide'),para(inline(SOUP.select_one('.hero-lead'))),Spacer(1,8),table([['2027 reference','Single','Couple / family'],['400% FPL: 48 states & DC','$63,840','$86,560'],['HSA base limit','$4,500 self-only','$9,000 family'],['HSA age-55+ catch-up','$1,000 per eligible owner','Up to $11,000 combined*']],[240,122,154]),Spacer(1,8),para('*The shared family base plus two catch-ups requires both spouses to qualify, sufficient contribution room, and separate HSAs for the catch-ups. Employer contributions count toward limits.','SmallGuide'),para('HealthCare.gov Open Enrollment: November 1, 2026 - January 15, 2027. Enroll by December 15 for January 1 coverage. Check state Marketplace deadlines.'),para('Use this guide to review enrollment, annual income, HSA eligibility and the transition to Medicare. Verify individual eligibility before recommending an income strategy.'),Spacer(1,10),Table([[qr,para('<b>Interactive guide and calculator</b><br/><a href="'+URL+'" color="#aa0e33">Open the online guide</a><br/>Scan the QR code for the current version.','BodyGuide')]],colWidths=[95,421]),Spacer(1,14),para('For licensed agents and brokers. Educational information, not tax, legal or investment advice. Federal rules and state requirements may differ. Examples are illustrative. Not affiliated with or endorsed by any government agency.','SmallGuide')]
pages.append(('Cover',cover))
pages.append(('Opportunity',section('opportunity')))
pages.append(('Enrollment',section('enrollment')))
pages.append(('MAGI',section('magi')))
pages.append(('Cliff',section('cliff')+[para('Using the online calculator','SubGuide'),para('Use annual household income even for partial-year coverage. Enter the taxable portions of withdrawals and conversions once, all other countable income, and only allowable deductions. Confirm HSA room before claiming a deduction. Select eligible months and PTC-eligible premiums; the tool assumes the same eligible people and premiums across those months. Final PTC is calculated month by month.','SmallGuide')]))
pages.append(('Planning',section('levers')))
pages.append(('HSA',section('hsa')))
pages.append(('Medicare',section('medicare')+section('compliance')))
blueprint=section('blueprint')
split=next(i for i,x in enumerate(blueprint) if isinstance(x,Paragraph) and x.getPlainText()=='The discovery conversation')
pages.append(('Referral opportunities',blueprint[:split]))
pages.append(('Discovery and service',[para('Discovery &amp; annual service','TitleGuide')]+blueprint[split:]))
pages.append(('FAQ',section('faq')+[para('Case support','SubGuide'),para('Sam Tripp<br/>Sales Director - ACA | Pinnacle Financial Services<br/><a href="mailto:Samuel.Tripp@pfsinsurance.com">Samuel.Tripp@pfsinsurance.com</a><br/>(800) 772-6881 ext. 7721<br/><a href="https://pfsinsurance.com/">pfsinsurance.com</a>')]))
worksheet=[para('Client MAGI worksheet','TitleGuide'),para('Client / spouse: ______________________________________________<br/>Tax household size / state: ______________________________________<br/>Coverage dates / Medicare dates: _________________________________'),table([['Projected 2027 annual household income','Amount'],['Federal taxable wages','$'],['Net self-employment / consulting income','$'],['Traditional-account withdrawals: taxable, excluding conversions','$'],['Roth conversions: taxable portion only','$'],['Social Security: full benefit, excluding SSI','$'],['Pensions / annuities: taxable portion','$'],['Investment income, including tax-exempt interest','$'],['Other countable income: unemployment, net rent, foreign income, etc.','$'],['A. Total countable income','$'],['Allowable personal HSA deduction (confirm eligibility / room)','- $'],['Other allowable AGI adjustments (count each deduction once)','- $'],['B. Projected ACA MAGI','$'],['400% FPL threshold / remaining headroom','$']],[410,106]),Spacer(1,8),table([['Household','100% FPL','250% FPL','400% FPL']]+[[str(n),f'${(15960+5680*(n-1)):,}',f'${int((15960+5680*(n-1))*2.5):,}',f'${(15960+5680*(n-1))*4:,}'] for n in range(1,5)],[100,138,139,139]),Spacer(1,8),para('Uses 2026 HHS guidelines for 2027 Marketplace coverage in the 48 contiguous states and DC; Alaska and Hawaii differ. Medicaid generally uses current monthly income and current state rules. This annual worksheet does not determine Medicaid or Marketplace eligibility.','SmallGuide'),para('Confirm: enrollment window; doctors and prescriptions; other coverage; HSA eligibility and unused room; tax-professional review; consumer consent and application review; Medicare timing.','SmallGuide')]
pages.append(('Worksheet',worksheet))
story=[]
probe=canvas.Canvas(BytesIO())
for title,content in pages:
    frame=KeepInFrame(516,660,content,mode='shrink',hAlign='LEFT',vAlign='TOP')
    frame.wrapOn(probe,516,660)
    scale=getattr(frame,'_scale',1)
    print(f'{title}: scale={scale:.2f}')
    if scale>1.3: raise ValueError(f'{title} needs a page split; text would be too small')
    if story: story.append(PageBreak())
    story.append(frame)
doc=SimpleDocTemplate(str(OUT),pagesize=(612,792),leftMargin=48,rightMargin=48,topMargin=72,bottomMargin=48,title='Pre-65 ACA Strategy Guide - Plan Year 2027',author='Pinnacle Financial Services',pageCompression=1)
doc.build(story,onFirstPage=chrome,onLaterPages=chrome)
print(f'Wrote {OUT} ({len(pages)} pages)')
