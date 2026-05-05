#!/usr/bin/env python3
"""buildPdf.py - Smith & Winters Electrical Branded Report Generator
Usage: python3 buildPdf.py <job.json> <output.pdf> <logo.png>
"""
import sys,json,os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
YELLOW=colors.HexColor("#F5C200")
DARK_RED=colors.HexColor("#8B0000")
RED_MARK=colors.HexColor("#C0392B")
BLACK=colors.HexColor("#1A1A1A")
SECTION_BG=colors.HexColor("#4A4A4A")
LIGHT_BG=colors.HexColor("#F5F5F5")
MID_GREY=colors.HexColor("#DDDDDD")
DARK_GREY=colors.HexColor("#555555")
WHITE=colors.white
GREEN_TICK=colors.HexColor("#27AE60")
RED_CROSS=colors.HexColor("#C0392B")
PAGE_W,PAGE_H=A4
MARGIN=14*mm
BODY_W=PAGE_W-2*MARGIN
def make_on_page(job_no,logo_path):
 def on_page(c,doc):
  c.saveState();w,h=A4
  c.setFillColor(BLACK);c.rect(0,h-22*mm,w,22*mm,fill=1,stroke=0)
  if logo_path and os.path.exists(logo_path):c.drawImage(logo_path,MARGIN,h-20*mm,width=52*mm,height=17*mm,preserveAspectRatio=True,mask="auto")
  c.setFont("Helvetica",7);c.setFillColor(YELLOW);c.drawRightString(w-MARGIN,h-7*mm,"Job Completion Report")
  c.setFont("Helvetica-Bold",14);c.setFillColor(WHITE);c.drawRightString(w-MARGIN,h-18*mm,f"Job No. {job_no}")
  c.setStrokeColor(YELLOW);c.setLineWidth(2.5);c.line(0,h-22.5*mm,w,h-22.5*mm)
  c.setFillColor(BLACK);c.rect(0,0,w,10*mm,fill=1,stroke=0)
  c.setFont("Helvetica",6.5);c.setFillColor(colors.HexColor("#AAAAAA"))
  c.drawString(MARGIN,3.5*mm,"Smith & Winters Electrical  |  ABN 70 626 942 596  |  Licence VIC: 26114  QLD: 91858")
  c.setFillColor(YELLOW);c.drawRightString(w-MARGIN,3.5*mm,f"Job No. {job_no}  |  Page {doc.page}")
  c.restoreState()
 return on_page
def sh(title):
 s=ParagraphStyle("sh",fontName="Helvetica-Bold",fontSize=10,textColor=WHITE,leftIndent=4*mm)
 t=Table([[Paragraph(title,s)]],colWidths=[BODY_W],style=TableStyle([("BACKGROUND",(0,0),(-1,-1),SECTION_BG),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),10)]))
 return [Spacer(1,4*mm),t,Spacer(1,2*mm)]
def dg(rows):
 nm=ParagraphStyle("n",fontName="Helvetica",fontSize=8.5,leading=12)
 bd=ParagraphStyle("b",fontName="Helvetica-Bold",fontSize=8,leading=12,textColor=DARK_GREY)
 data=[[Paragraph(k,bd),Paragraph(str(v) if v else "\u2014",nm)] for k,v in rows]
 ts=TableStyle([("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LIGHT_BG]),("GRID",(0,0),(-1,-1),0.3,MID_GREY),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,-1),(-1,-1),1,YELLOW)])
 return Table(data,colWidths=[BODY_W*0.35,BODY_W*0.65],style=ts,hAlign="LEFT")
def sc(qr,t,d):
 rs=ParagraphStyle("r",fontName="Helvetica-Bold",fontSize=8,textColor=RED_MARK)
 ts=ParagraphStyle("t",fontName="Helvetica-Bold",fontSize=9.5,textColor=BLACK)
 bs=ParagraphStyle("b",fontName="Helvetica",fontSize=8.5,leading=13,textColor=BLACK)
 mk=Table([[""]],colWidths=[3*mm],style=TableStyle([("BACKGROUND",(0,0),(-1,-1),RED_MARK),("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
 col=[Paragraph(f"Quote Ref. {qr}" if qr else "",rs),Spacer(1,1*mm),Paragraph(t,ts),Spacer(1,1*mm),Paragraph(d,bs)]
 ct=Table([[i] for i in col],colWidths=[BODY_W-5*mm],style=TableStyle([("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),0)]))
 card=Table([[mk,ct]],colWidths=[5*mm,BODY_W-5*mm],style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),("LINEBELOW",(0,-1),(-1,-1),0.5,MID_GREY),("BACKGROUND",(0,0),(-1,-1),WHITE)]))
 return [card,Spacer(1,1*mm)]
def cr(text,ok=True):
 ts=ParagraphStyle("t",fontName="Helvetica-Bold",fontSize=10,textColor=GREEN_TICK if ok else RED_CROSS)
 tx=ParagraphStyle("x",fontName="Helvetica",fontSize=8.5,leading=13,textColor=DARK_RED if not ok else BLACK)
 return [Paragraph("&#10004;" if ok else "&#10008;",ts),Paragraph(text,tx)]
def build(jp,op,lp):
 with open(jp,"r") as f:data=json.load(f)
 jn=data.get("jobNo","")
 doc=SimpleDocTemplate(op,pagesize=A4,leftMargin=MARGIN,rightMargin=MARGIN,topMargin=26*mm,bottomMargin=14*mm)
 on_page=make_on_page(jn,lp)
 story=[]
 nm=ParagraphStyle("n",fontName="Helvetica",fontSize=8.5,leading=13)
 bd=ParagraphStyle("b",fontName="Helvetica-Bold",fontSize=8.5,leading=13)
 it=ParagraphStyle("i",fontName="Helvetica",fontSize=8.5,leading=13,textColor=DARK_GREY)
 story+=sh("CLIENT & JOB DETAILS")
 cu=data.get("customer",{})
 qr=", ".join(data.get("quoteRefs",[]))or "\u2014"
 rows=[("CLIENT",cu.get("name")),("BUSINESS",cu.get("business")),("CONTACT",cu.get("phone")or cu.get("contact")),("JOB NO.",jn),("SITE ADDRESS",data.get("siteAddress")),("LICENCE",data.get("licence","VIC: 26114  QLD: 91858")),("ABN",data.get("abn","70 626 942 596")),("STATUS",data.get("status","COMPLETED")),("TECHNICIAN",data.get("technician","Smith & Winters Licensed Electrician")),("WORKS DATE",data.get("worksDate",date.today().strftime("%B %Y"))),("QUOTE REF.",qr),("CERT. SAFETY",data.get("certSafety","To be issued on finalisation"))]
 lt=dg(rows[:6]);rt=dg(rows[6:])
 story.append(Table([[lt,rt]],colWidths=[BODY_W/2-2*mm,BODY_W/2-2*mm],style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])))
 story.append(Spacer(1,4*mm))
 story+=sh("SCOPE OF WORKS COMPLETED")
 sn=cu.get("business")or"the site";sa=data.get("siteAddress","")
 story.append(Paragraph(f"All works below were completed by licensed electricians at {sn}, {sa}. A Certificate of Electrical Safety will be issued upon finalisation.",it))
 story.append(Spacer(1,3*mm))
 for item in data.get("scopeItems",[]):story+=sc(item.get("quoteRef"),item.get("title","Works Completed"),item.get("description",""))
 story.append(Spacer(1,4*mm))
 story+=sh("WHAT'S INCLUDED IN THIS JOB")
 inc=data.get("whatsIncluded")or["Supply and installation of all electrical fittings and fixtures as listed above","Certificate of Electrical Safety upon completion","All work carried out by licensed electricians following Australian Standards","All materials supplied are new and fit for purpose"]
 ni=data.get("whatsNotIncluded")or["Any items or work not listed in the scope above"]
 ir=[]
 for i in range(0,len(inc),2):
  l=cr(inc[i],True);r=cr(inc[i+1],True)if i+1<len(inc)else["",""]
  ir.append([l[0],l[1],r[0],r[1]])
 if ir:story.append(Table(ir,colWidths=[6*mm,BODY_W/2-8*mm,6*mm,BODY_W/2-8*mm],style=TableStyle([("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LIGHT_BG]),("GRID",(0,0),(-1,-1),0.3,MID_GREY),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6)])))
 story.append(Spacer(1,2*mm));story.append(Paragraph("<b>Not Included:</b>",bd));story.append(Spacer(1,1*mm))
 for item in ni:
  row=cr(item,False)
  story.append(Table([[row[0],row[1]]],colWidths=[6*mm,BODY_W-6*mm],style=TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),6)])))
 story.append(Spacer(1,4*mm))
 phs=[p for p in data.get("photoPaths",[])if os.path.exists(p)and os.path.splitext(p)[1].lower()in{".jpg",".jpeg",".png",".webp"}]
 if phs:
  story+=sh("PHOTO DOCUMENTATION - WORKS COMPLETED")
  story.append(Paragraph(f"The following photographs document the completed works on-site at {sn}, {sa}.",it))
  story.append(Spacer(1,3*mm))
  for i,pp in enumerate(phs):
   if i>0:story.append(PageBreak())
   pt=ParagraphStyle("pt",fontName="Helvetica-Bold",fontSize=10,textColor=BLACK)
   pb=ParagraphStyle("pb",fontName="Helvetica",fontSize=8.5,leading=13,textColor=DARK_GREY)
   story.append(Table([[Paragraph(f"Site Photo {i+1}",pt)],[Paragraph(f"Works completed at {sn}, {sa}.",pb)]],colWidths=[BODY_W],style=TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT_BG),("GRID",(0,0),(-1,-1),0.3,MID_GREY),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LINEBELOW",(0,-1),(-1,-1),1.5,YELLOW)])))
   story.append(Spacer(1,4*mm))
   try:
    img=Image(pp);r=min(BODY_W/img.imageWidth,160*mm/img.imageHeight)
    img.drawWidth=img.imageWidth*r;img.drawHeight=img.imageHeight*r;img.hAlign="CENTER"
    story.append(img)
   except:pass
 story.append(PageBreak())
 story+=sh("COMPLETION SIGN-OFF")
 story.append(Paragraph("By signing below, both parties confirm that all works described in this report have been completed to the agreed scope and in accordance with Australian Standards. A Certificate of Electrical Safety will be forwarded upon finalisation.",it))
 story.append(Spacer(1,5*mm))
 hs=ParagraphStyle("h",fontName="Helvetica-Bold",fontSize=9,textColor=WHITE,alignment=TA_CENTER)
 lb=ParagraphStyle("l",fontName="Helvetica-Bold",fontSize=8,textColor=DARK_GREY)
 vl=ParagraphStyle("v",fontName="Helvetica",fontSize=9,leading=22)
 cn=cu.get("name","");cw=BODY_W/2-2*mm
 def sig_col(name_val):
  return Table([[Paragraph("Name:",lb)],[Paragraph(name_val,vl)],[Paragraph("Signature:",lb)],[Paragraph(" ",ParagraphStyle("sv",fontName="Helvetica",fontSize=9,leading=30))],[Paragraph("Date:",lb)],[Paragraph("_____ / _____ / _____",vl)]],colWidths=[cw],style=TableStyle([("LEFTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
 sd=[[Paragraph("CLIENT SIGN-OFF",hs),Paragraph("SMITH &amp; WINTERS ELECTRICAL",hs)],[sig_col(cn),sig_col("___________________________")]]
 sts=TableStyle([("BACKGROUND",(0,0),(-1,0),SECTION_BG),("BACKGROUND",(1,0),(1,0),DARK_RED),("GRID",(0,0),(-1,-1),0.4,MID_GREY),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,0),6),("BOTTOMPADDING",(0,0),(-1,0),6),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),("LINEBELOW",(0,-1),(-1,-1),1.5,YELLOW)])
 story.append(Table(sd,colWidths=[cw,cw],style=sts,hAlign="LEFT"))
 story.append(Spacer(1,10*mm))
 tys=ParagraphStyle("ty",fontName="Helvetica-Oblique",fontSize=10,leading=16,textColor=DARK_GREY,alignment=TA_CENTER,backColor=LIGHT_BG,borderPad=8)
 story.append(Table([[Paragraph("Thank you for choosing Smith &amp; Winters Electrical. We appreciate your business and look forward to working with you again. If you have any questions about the works completed please don't hesitate to get in touch.",tys)]],colWidths=[BODY_W],style=TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT_BG),("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),("BOX",(0,0),(-1,-1),0.5,MID_GREY)])))
 doc.build(story,onFirstPage=on_page,onLaterPages=on_page)
 print(f"PDF written to {op}")
if __name__=="__main__":
 if len(sys.argv)<4:print("Usage: buildPdf.py <job.json> <output.pdf> <logo.png>");sys.exit(1)
 build(sys.argv[1],sys.argv[2],sys.argv[3])
