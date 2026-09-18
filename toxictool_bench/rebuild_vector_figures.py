"""Native SVG reconstruction of the two diagram PNGs; old PDFs are read-only.

No raster elements, auto-tracing, text-as-image, or filter effects. Text remains
editable in SVG and is embedded/subset as fonts by the native SVG/PDF renderer.
Decorative icons are newly drawn paths, not exact copies of raster artwork.
"""
from __future__ import annotations
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import cairo
import gi
gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg
from PIL import ImageFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/"figures"
W,H=2000.,2000.*3072/5504
NAVY="#263650"; BLUE="#244873"; GREEN="#2b794b"; RED="#b1262d"
INK="#162331"; GRAY="#758397"; PURPLE="#713cc2"; ORANGE="#c77d32"
WHITE="#ffffff"
NS="http://www.w3.org/2000/svg"
ET.register_namespace("",NS)
FONTS=Path("/usr/share/fonts/truetype/msttcorefonts")


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


class SVG:
    def __init__(self,title):
        self.root=ET.Element(f"{{{NS}}}svg",{"width":str(W),"height":str(H),"viewBox":f"0 0 {W} {H}","role":"img"})
        ET.SubElement(self.root,f"{{{NS}}}title").text=title
        self.parent=self.root;self.texts=[];self.font_cache={}
        self.rect(0,0,W,H,WHITE,stroke="none",r=0)

    def el(self,name,**kw):
        return ET.SubElement(self.parent,f"{{{NS}}}{name}",{k.replace('_','-'):str(v) for k,v in kw.items() if v is not None})

    def rect(self,x,y,w,h,fill,stroke=BLUE,r=14,sw=2):
        return self.el("rect",x=x,y=y,width=w,height=h,rx=r,fill=fill,stroke=stroke,stroke_width=sw)

    def circle(self,x,y,r,fill,stroke="none",sw=2):
        return self.el("circle",cx=x,cy=y,r=r,fill=fill,stroke=stroke,stroke_width=sw)

    def path(self,d,stroke=BLUE,fill="none",sw=2.5):
        return self.el("path",d=d,stroke=stroke,fill=fill,stroke_width=sw,stroke_linecap="round",stroke_linejoin="round")

    def line(self,x1,y1,x2,y2,color=BLUE,sw=2.5):
        return self.el("line",x1=x1,y1=y1,x2=x2,y2=y2,stroke=color,stroke_width=sw,stroke_linecap="round")

    def polygon(self,points,fill,stroke=BLUE,sw=2.5):
        return self.el("polygon",points=" ".join(f"{x},{y}" for x,y in points),fill=fill,stroke=stroke,stroke_width=sw,stroke_linejoin="round")

    def arrow(self,points,color=BLUE,sw=3,head=11):
        self.path("M "+" L ".join(f"{x} {y}" for x,y in points),color,sw=sw)
        x,y=points[-1];px,py=points[-2];a=math.atan2(y-py,x-px)
        self.polygon([(x,y),(x-head*math.cos(a)+head*.48*math.sin(a),y-head*math.sin(a)-head*.48*math.cos(a)),
                      (x-head*math.cos(a)-head*.48*math.sin(a),y-head*math.sin(a)+head*.48*math.cos(a))],color,color,1)

    def font(self,size,bold=False,mono=False):
        key=(round(size*10),bold,mono)
        if key not in self.font_cache:
            name=("courbd.ttf" if bold else "cour.ttf") if mono else ("arialbd.ttf" if bold else "arial.ttf")
            self.font_cache[key]=ImageFont.truetype(str(FONTS/name),max(1,round(size*10)))
        return self.font_cache[key]

    def text(self,x,y,value,size=24,color=INK,bold=False,anchor="start",width=None,mono=False,italic=False):
        value=str(value)
        measured=self.font(size,bold,mono).getlength(value)/10
        if width and measured>width:
            size=size*width/measured
            measured=self.font(size,bold,mono).getlength(value)/10
        e=self.el("text",x=x,y=y,fill=color,font_family="Courier New, monospace" if mono else "Arial, Helvetica, Liberation Sans, sans-serif",
                  font_size=f"{size:.3f}",font_weight="bold" if bold else "normal",text_anchor=anchor,
                  font_style="italic" if italic else None)
        e.text=value
        left=x if anchor=="start" else x-measured/2 if anchor=="middle" else x-measured
        self.texts.append({"text":value,"x":x,"baseline":y,"font_size":size,"font":"Courier New" if mono else "Arial",
                           "bold":bold,"left":left,"right":left+measured})
        return e

    def lines(self,x,y,values,size=24,leading=None,**kw):
        for i,t in enumerate(values):self.text(x,y+i*(leading or size*1.25),t,size,**kw)

    def panel(self,x,y,w,h,color,fill,title=None,header=52,title_size=28):
        self.rect(x+2,y+4,w,h,"#dbe1e8",stroke="none")
        self.rect(x,y,w,h,fill,color,r=18,sw=2.7)
        if title:
            self.rect(x,y,w,header,color,color,r=17)
            self.rect(x,y+header/2,w,header/2,color,color,r=0,sw=0)
            self.text(x+w/2,y+header*.69,title,title_size,WHITE,True,"middle",w-28)

    def group(self,x=0,y=0,scale=1):
        parent=self.parent
        self.parent=self.el("g",transform=f"translate({x} {y}) scale({scale})")
        return parent

    def icon(self,kind,x,y,size=60,color=BLUE):
        old=self.group(x,y,size/100)
        if kind in {"robot","engineer"}:
            self.line(50,5,50,17,color,3);self.circle(50,5,4,"#96c7b0",color)
            self.rect(18,18,64,43,"#bbcedb",color,10,3)
            self.rect(27,29,46,20,"#213746",color,7)
            self.circle(39,39,5,"#9dd3b4");self.circle(61,39,5,"#9dd3b4")
            self.rect(29,63,42,32,"#b8cbd7",color,5,3)
            self.rect(8,66,15,28,"#c6d7df",color,4,3);self.rect(77,66,15,28,"#c6d7df",color,4,3)
            self.line(36,96,36,100,color,6);self.line(64,96,64,100,color,6)
            self.rect(39,73,22,12,"#83c296",color,2)
            if kind=="engineer":
                self.path("M 17 22 Q 19 -4 49 -4 Q 80 -4 84 22 Z",color,"#e8b35c",3)
                self.rect(45,-9,10,29,"#f2c56c",color,2,2)
                self.rect(7,20,84,7,"#f2c56c",color,2,2)
        elif kind=="user":
            self.circle(50,28,18,color)
            self.path("M 12 91 L 12 77 Q 12 53 50 53 Q 88 53 88 77 L 88 91 Z",color,color)
        elif kind in {"gear","tools"}:
            pts=[]
            for i in range(40):
                a=math.pi*2*i/40;r=43 if i%4 in {0,1} else 34
                pts.append((50+r*math.cos(a),50+r*math.sin(a)))
            self.polygon(pts,"#9cb5ca",color,3);self.circle(50,50,17,"#f6f9fc",color,3)
            if kind=="tools":
                self.path("M 8 90 L 61 35 Q 52 14 77 8 L 71 24 L 82 31 L 95 22 Q 99 43 77 49 L 26 99 Z",color,"#dce5eb",3)
        elif kind=="briefcase":
            self.rect(13,28,74,60,"#dd4852",RED,7,3)
            self.path("M 35 28 L 35 12 L 64 12 L 64 28",RED,sw=5)
            self.line(13,47,87,47,"#8f202d",4);self.rect(43,42,15,18,"#f5c2aa",RED,2,2)
        elif kind=="brain":
            self.path("M 39 87 C 13 95 6 75 15 64 C 1 52 8 34 20 31 C 15 15 29 7 40 13 C 45 1 63 7 67 21 L 78 21 L 78 85 Z",color,"#dceaf3",3)
            self.path("M 26 24 C 41 23 23 44 38 45 M 16 57 C 31 44 42 58 28 70 M 40 15 L 40 88",color,sw=2)
            self.rect(45,34,48,37,color,color,3)
            self.text(69,59,"LLM",17,WHITE,True,"middle")
        elif kind in {"database","poison"}:
            self.path("M 16 22 L 16 78 C 16 96 84 96 84 78 L 84 22",color,"#cbd8e3",3)
            self.el("ellipse",cx=50,cy=22,rx=34,ry=12,fill="#e6edf3",stroke=color,stroke_width=3)
            self.path("M 16 47 C 16 63 84 63 84 47 M 16 70 C 16 86 84 86 84 70",color,sw=3)
            if kind=="poison":
                self.path("M 77 42 C 68 57 55 71 55 83 C 55 105 93 105 93 83 C 93 71 81 52 77 42 Z",RED,"#ea8996",3)
                self.circle(70,83,4,RED);self.circle(82,87,4,RED)
        elif kind=="csv":
            self.path("M 19 5 L 63 5 L 84 27 L 84 95 L 19 95 Z",color,"#cfdee5",3)
            self.path("M 63 5 L 63 27 L 84 27",color,sw=3)
            self.rect(7,48,78,29,GREEN,GREEN,3)
            self.text(46,69,"CSV",22,WHITE,True,"middle")
        elif kind=="ghost":
            self.path("M 20 88 L 20 38 C 20 2 80 2 80 38 L 88 55 L 78 64 L 80 88 L 65 82 L 51 90 L 36 82 Z",color,"#e2e9fb",3)
            self.circle(38,43,5,color);self.circle(62,43,5,color)
            self.el("ellipse",cx=50,cy=64,rx=7,ry=11,fill=color)
        elif kind in {"check","cross"}:
            self.circle(50,50,44,color)
            if kind=="check":self.path("M 25 50 L 43 69 L 76 30",WHITE,sw=10)
            else:
                self.line(32,32,68,68,WHITE,9);self.line(68,32,32,68,WHITE,9)
        elif kind=="shield":
            self.path("M 50 5 L 88 20 L 83 57 Q 78 78 50 96 Q 21 78 17 57 L 12 20 Z",color,"#91cca3",4)
            self.path("M 30 47 L 45 65 L 71 32",WHITE,sw=9)
        elif kind=="eye":
            self.path("M 4 53 Q 50 4 96 53 Q 50 101 4 53 Z",color,"#f5fbff",3)
            self.circle(50,53,18,color);self.circle(55,47,5,WHITE)
        elif kind=="magnify":
            self.circle(39,39,29,"#e4eff7",color,4)
            self.path("M 60 61 L 92 94",color,sw=12)
            self.line(25,32,51,32,color,3);self.line(25,43,51,43,color,3)
        elif kind in {"table","calculator"}:
            self.rect(9,7,83,87,"#dce8ee",color,4,3)
            self.rect(17,16,67,16,"#8dbbd0",color,2)
            for xx in [33,58,80]:self.line(xx,40,xx,88,color,2)
            for yy in [40,55,71,87]:self.line(17,yy,85,yy,color,2)
        elif kind in {"network","schema"}:
            for p,q in [((24,19),(66,38)),((24,19),(30,78)),((66,38),(83,81)),((30,78),(83,81))]:self.line(*p,*q,color,3)
            for xx,yy,c in [(24,19,"#80bbcf"),(66,38,"#ecaeb6"),(30,78,"#bcace5"),(83,81,"#e7bb74")]:self.circle(xx,yy,11,c,color,3)
        elif kind in {"scale","chart","downchart"}:
            for xx,hh,c in [(15,28,"#deb47a"),(40,48,"#85acbe"),(65,72,"#88bb9e")]:self.rect(xx,86-hh,18,hh,c,color,1,2)
            self.line(8,91,95,91,color,3)
            if kind=="downchart":self.arrow([(8,9),(35,32),(54,22),(91,61)],RED,4,12)
        elif kind=="swap":
            self.arrow([(12,28),(86,28)],color,7,17);self.arrow([(86,72),(12,72)],color,7,17)
        elif kind=="rank":
            for i in range(3):
                self.text(13,27+i*29,str(i+1),23,color,True)
                self.rect(39,10+i*29,52-i*9,14,"#9fc4e2",color,2,2)
        elif kind=="sign":
            self.line(10,28,44,28,color,7);self.line(27,11,27,45,color,7)
            self.line(59,75,93,75,color,7)
        elif kind in {"ratio","denom"}:
            self.line(15,50,85,50,color,7);self.circle(50,19,10,"#84bca2",color,2);self.circle(50,81,10,"#8caeca",color,2)
            if kind=="denom":self.line(64,69,91,93,RED,5);self.line(91,69,64,93,RED,5)
        elif kind=="filter":
            self.path("M 6 12 L 94 12 L 62 52 L 62 88 L 39 98 L 39 52 Z",color,"#b2c5d2",3)
            self.line(72,67,95,90,RED,5);self.line(95,67,72,90,RED,5)
        elif kind=="tag":
            self.path("M 9 12 L 52 12 L 94 54 L 54 95 L 9 50 Z",color,"#edc087",3);self.circle(30,32,5,WHITE,color)
        elif kind=="syringe":
            self.path("M 13 79 L 64 25 L 82 43 L 31 97 Z",color,"#dfabb4",3)
            self.line(64,12,95,42,color,5);self.line(15,89,3,100,color,3)
        elif kind=="clock":
            self.circle(45,43,37,"#fff6df",color,3);self.line(45,17,45,43,color,4);self.line(45,43,66,55,color,4)
            self.rect(39,70,58,25,"#efbd79",color,3,2);self.text(68,89,"Old",17,color,True,"middle")
        elif kind=="warning":
            self.polygon([(50,4),(97,94),(3,94)],"#f1ce56",color,3)
            self.circle(50,47,17,"#fff2ba",color,2);self.circle(44,45,4,color);self.circle(57,45,4,color)
            self.line(31,69,70,83,color,5);self.line(70,69,31,83,color,5)
        elif kind=="trophy":
            self.path("M 24 9 L 77 9 L 70 48 Q 63 66 50 68 Q 34 65 29 48 Z",color,"#ebbc59",3)
            self.path("M 24 17 L 7 17 Q 7 51 31 52 M 77 17 L 94 17 Q 94 50 70 52",color,sw=5)
            self.line(50,68,50,86,color,6);self.rect(24,88,52,10,"#c1c9d1",color,2,3)
            self.polygon([(50,20),(55,33),(69,34),(59,43),(62,58),(50,50),(38,58),(41,43),(31,34),(45,33)],"#fff0aa",color,2)
        elif kind=="alert":
            self.circle(50,50,44,"#d897b8",color,3);self.rect(44,20,12,40,WHITE,color,5,2);self.circle(50,77,7,WHITE,color,2)
        elif kind=="recovery":
            self.path("M 49 70 Q 14 61 4 14 L 35 39 L 24 6 L 51 30 L 76 7 L 65 42 L 97 16 Q 85 57 57 69 L 72 91 L 50 83 L 28 92 Z",color,"#e6a451",3)
            self.line(51,65,51,91,color,3)
        elif kind in {"camera","sensor"}:
            self.rect(9,23,82,50,"#c4d7e1",color,8,3);self.circle(50,47,17,"#829cab",color,3);self.circle(50,47,7,"#c3e4b7",color,2)
            self.line(50,73,50,91,color,4);self.line(27,93,74,93,color,5)
        else:
            self.rect(12,12,76,76,"#d7e4ed",color,8,3)
            self.circle(50,50,22,WHITE,color,3)
        self.parent=old

    def write(self,path):
        ET.indent(self.root,space="  ")
        ET.ElementTree(self.root).write(path,encoding="utf-8",xml_declaration=True)


def figure1():
    s=SVG("Figure 1 | Silent Tool Poisoning: An Example")
    s.rect(10,7,1980,76,NAVY,NAVY,14)
    s.text(1000,58,"Figure 1 | Silent Tool Poisoning: An Example",37,WHITE,True,"middle",1900)
    s.panel(430,108,1110,117,BLUE,"#eef3fa","USER QUERY",44,28)
    s.icon("user",449,163,45)
    s.text(510,198,'“Which store had the highest revenue last quarter, and what was it?”',25,width=1000)
    s.arrow([(985,225),(985,249)],BLUE,3,9)
    s.panel(660,250,650,250,BLUE,"#eef3fa","DATA AGENT WITH TOOL ACCESS",51,29)
    s.icon("brain",915,323,98);s.icon("tools",1031,327,91)
    s.text(985,445,"Data Agent",28,bold=True,anchor="middle")
    s.text(985,478,"LLM + Tool Calls",25,anchor="middle")
    s.panel(465,326,321,160,BLUE,"#e7eff8")
    s.icon("briefcase",479,340,37,RED)
    s.text(529,365,"REGISTERED TOOL",24,bold=True,width=244)
    s.rect(478,381,294,90,"#273247",stroke="none",r=10)
    s.text(495,435,"csv_tool(query)",28,"#a4d397",mono=True,width=263)
    s.panel(1490,251,496,249,BLUE,"#f6f8fa","DATA SOURCE",52,30)
    s.icon("csv",1925,259,49)
    s.text(1511,335,"Store",25,bold=True);s.text(1697,335,"Q4 Revenue",25,bold=True)
    s.line(1511,347,1965,347,"#ccd4dc",2)
    s.rect(1507,392,466,44,"#d6ead9",stroke="none",r=8)
    for y,store,value,bold in [(380,"Store A","$230,000",False),(423,"Store B","$450,000",True),(471,"Store C","$310,000",False)]:
        s.text(1514,y,store,26,bold=bold);s.text(1697,y,value,26,bold=bold)
    s.arrow([(1870,412),(1838,412)],GREEN,2.5,10);s.text(1883,423,"highest",23,GREEN,width=87)
    s.arrow([(1310,387),(1487,387)],BLUE,3,13)
    s.text(1399,363,"READS",26,bold=True,anchor="middle")
    s.text(1399,420,"(stores.csv)",22,anchor="middle")
    s.arrow([(965,500),(965,556),(500,556),(500,612)],GREEN,3,13)
    s.circle(731,556,27,GREEN);s.icon("tools",711,536,40,WHITE)
    s.arrow([(990,500),(1018,500),(1018,722),(1041,722)],RED,3,13)
    s.icon("cross",997,639,42,RED)
    s.panel(12,613,959,445,GREEN,"#fcfffd","PATH 1: CLEAN ENVIRONMENT",58,31)
    s.icon("check",28,624,40,GREEN)
    s.panel(35,735,394,176,GREEN,"#dff0e3")
    s.text(232,773,"CSV Tool",30,bold=True,anchor="middle")
    s.rect(47,790,370,106,"#273247",stroke="none",r=10)
    s.lines(59,817,['row = stores.loc[','    stores["Q4 Revenue"].idxmax()]','return row["Store"], row["Q4 Revenue"]'],16.5,23,color="#e8f0fa",mono=True,width=346)
    s.panel(457,780,207,117,GREEN,"#e1f0e5")
    s.lines(560,812,["Original Tool","Output"],23,26,bold=True,anchor="middle",width=190)
    s.text(560,875,"No Modification",20,anchor="middle",width=190)
    s.panel(695,780,254,117,GREEN,WHITE)
    s.text(822,824,"Store B – $450,000",26,GREEN,anchor="middle",width=234)
    s.text(822,867,"Correct Observation",22,anchor="middle",width=234)
    s.arrow([(429,839),(457,839)],GREEN,3,10);s.arrow([(664,839),(695,839)],GREEN,3,10)
    s.icon("check",922,761,40,GREEN)
    s.rect(278,1027,435,58,GREEN,GREEN,12)
    s.icon("check",290,1039,35,GREEN)
    s.text(514,1067,"CORRECT STORE-VALUE PAIR",28,WHITE,True,"middle",364)
    s.panel(1045,526,944,532,RED,"#fffafa","PATH 2: POISONED ENVIRONMENT",58,29)
    s.icon("cross",1059,539,37,RED)
    s.panel(1064,603,904,163,"#dca951","#fff1cf")
    s.icon("ghost",1080,651,59)
    s.text(1150,635,"TOOL-OUTPUT POISONING",25,bold=True,width=394)
    s.lines(1150,663,["• The original tool runs successfully.","• The proxy swaps Store A and Store B","  in the output.","• No exception, error, or warning is shown."],19,23,width=386)
    s.panel(1550,642,176,97,GREEN,"#edf3f8")
    s.text(1638,670,"Original output",18,bold=True,anchor="middle",width=160)
    s.text(1638,713,"Store B – $450,000",19,anchor="middle",width=160)
    s.panel(1780,642,176,97,GREEN,WHITE)
    s.text(1868,670,"Modified output",18,bold=True,anchor="middle",width=160)
    s.text(1868,713,"Store A – $450,000",19,anchor="middle",width=160)
    s.lines(1753,661,["Label","swap"],16,18,color=RED,bold=True,anchor="middle")
    s.arrow([(1727,702),(1778,702)],RED,3,12)
    s.panel(1064,789,904,203,RED,"#fdebed")
    s.text(1516,828,"MODIFIED TOOL OBSERVATION",29,bold=True,anchor="middle",width=850)
    for x,w in [(1081,264),(1380,235),(1650,300)]:s.panel(x,852,w,112,RED,WHITE)
    s.text(1213,889,"Original Tool Output",22,bold=True,anchor="middle",width=244)
    s.text(1213,936,"Store B – $450,000",25,anchor="middle",width=244)
    s.text(1497,889,"Output Proxy",24,bold=True,anchor="middle",width=215)
    s.text(1497,936,"Swap Store Labels",22,anchor="middle",width=215)
    s.text(1800,894,"Store A – $450,000",28,RED,anchor="middle",width=280)
    s.lines(1800,927,["Observation Received","by the Agent"],19,24,anchor="middle",width=280)
    s.arrow([(1345,909),(1379,909)],RED,3,11);s.arrow([(1615,909),(1649,909)],RED,3,11)
    s.icon("cross",1930,835,39,RED)
    s.rect(1254,1027,512,58,RED,RED,12)
    s.icon("cross",1268,1038,38,RED)
    s.text(1520,1067,"WRONG STORE-VALUE PAIR",29,WHITE,True,"middle",434)
    s.text(1000,1110,"A Successful Tool Call Can Return a Plausible but Wrong Observation",26,anchor="middle",width=1960)
    return s


def operator(s,x,y,w,label,kind,color):
    s.rect(x,y,w,43,"#f2f5fb",color,8,1.8)
    s.icon(kind,x+9,y+6,31,color)
    s.text(x+51,y+28,label,22,color=INK,bold=True,width=w-64)


def slider(s,x,y,color):
    s.rect(x,y+13,124,14,"#eee3d4",color,8,1.5)
    s.rect(x,y+13,60,14,"#b7cbea",color,8,1.5)
    for xx in [x+31,x+96]:
        s.circle(xx,y,8,"#fff0d8",NAVY,1.5);s.circle(xx-2,y-1,1,NAVY);s.circle(xx+2,y-1,1,NAVY)


def figure2():
    s=SVG("Figure 2 | ToxicBench and Evidence Verification")
    s.rect(8,5,1980,73,NAVY,NAVY,14)
    s.icon("tools",22,17,44,"#b8cbdc");s.text(84,51,"Data Agents",26,WHITE,True)
    s.text(1000,51,"Figure 2 | ToxicBench and Evidence Verification",32,WHITE,True,"middle",1290)
    s.text(1790,51,"Poisoning",26,WHITE,True,width=144);s.icon("warning",1928,11,58,NAVY)
    s.text(17,117,"A  Task Suites",26,bold=True)
    s.text(995,117,"Cross-model Tasks",29,bold=True,anchor="middle")
    s.text(1980,117,"Expanded: 120 tasks  |  Multi-table: 13 tasks",24,bold=True,anchor="end",width=620)
    s.panel(9,136,972,209,"#4264ce","#eef2ff")
    s.rect(9,136,972,59,"#4264ce","#4264ce",14)
    s.icon("calculator",27,145,42);s.icon("csv",58,166,27)
    s.text(92,175,"Numerical Tasks",31,WHITE,True,width=289)
    s.circle(403,166,21,WHITE);s.text(403,175,"N",27,"#4264ce",True,"middle")
    s.text(448,175,"34",29,WHITE,True);s.text(505,175,"11 CSV datasets",26,WHITE,True)
    s.text(36,223,"Operator examples across suites:",22,BLUE,True)
    for x,y,label,kind in [(31,240,"Aggregate Scale","chart"),(344,240,"Sign Flip","sign"),(657,240,"Rank Swap","rank"),
                           (31,293,"Ratio Inversion","ratio"),(344,293,"Denom. Swap","denom"),(657,293,"Omit Filter","filter")]:
        operator(s,x,y,303,label,kind,"#4264ce")
    s.panel(1012,136,977,209,PURPLE,"#f5effd")
    s.rect(1012,136,977,59,PURPLE,PURPLE,14)
    s.icon("network",1028,145,42)
    s.text(1081,175,"Semantic / Schema Tasks",30,WHITE,True,width=410)
    s.circle(1525,166,21,WHITE);s.text(1525,175,"S",27,PURPLE,True,"middle")
    s.text(1570,175,"24",29,WHITE,True);s.text(1642,175,"17 datasets",26,WHITE,True)
    s.text(1038,223,"Operator examples across suites:",22,PURPLE,True)
    operator(s,1034,240,286,"Label Swap","tag",PURPLE)
    operator(s,1332,240,335,"Treatment/Control Flip","syringe",PURPLE)
    operator(s,1680,240,287,"Biased Retrieval","magnify",PURPLE)
    operator(s,1034,293,444,"Column-Semantic Swap","table",PURPLE)
    operator(s,1490,293,477,"Stale Metadata","clock",PURPLE)
    s.rect(1885,300,66,27,"#f0c28c",ORANGE,5);s.text(1918,320,"Old",18,bold=True,anchor="middle")
    s.text(17,382,"B  Paired Evaluation Protocol",25,bold=True)
    s.text(1040,382,"Same Query and Source Data",29,bold=True,anchor="middle")
    s.line(8,398,1989,398,"#e3e7ed",4)
    s.panel(10,413,430,165,GREEN,"#e7f5e9")
    s.text(285,447,"Clean Env.",27,GREEN,True,"middle")
    s.icon("robot",41,449,99)
    s.text(95,567,"Data Agent",22,bold=True,anchor="middle")
    s.text(226,477,"calls",23,anchor="middle");s.arrow([(160,496),(288,496)],"#54a36a",4,15)
    s.text(226,525,"output",23,anchor="middle");s.text(226,554,"data flow",21,anchor="middle")
    s.icon("tools",312,469,80);s.text(352,568,"Tool",24,bold=True,anchor="middle")
    s.arrow([(440,496),(473,496)],"#54a36a",4,12)
    s.panel(475,413,745,165,"#a3adc3","#f6f7fc")
    s.text(848,450,"Paired Task",28,bold=True,anchor="middle")
    s.text(555,500,"o = f(x)",24,GREEN,anchor="middle",italic=True)
    s.icon("swap",640,466,38,GREEN);s.icon("database",685,466,48)
    s.text(848,501,"(query + dataset)",22,anchor="middle",width=213,italic=True)
    s.arrow([(948,495),(973,495)],"#80828b",3,10)
    s.polygon([(1003,462),(1036,495),(1003,528),(970,495)],"#e6e8ec","#626670",3)
    s.text(1003,505,"=",28,bold=True,anchor="middle")
    s.arrow([(1036,495),(1094,495)],"#80828b",3,12)
    s.circle(1137,495,27,"#e2e5ec","#626670",3);s.text(1137,504,"vC",24,bold=True,anchor="middle",italic=True)
    s.text(555,556,"Correct output",22,anchor="middle")
    s.text(846,556,"data flow",22,anchor="middle")
    s.lines(1003,553,["Matched","Settings"],20,22,anchor="middle")
    s.text(1137,556,"compare",22,anchor="middle")
    s.panel(1250,413,739,165,RED,"#fceced")
    s.text(1628,447,"Poisoned Env.",27,RED,True,"middle")
    s.arrow([(1250,496),(1223,496)],RED,4,12)
    s.text(1268,509,"o' = P(o; q)",22,RED,width=148)
    s.arrow([(1410,496),(1436,496)],RED,3,11);s.icon("poison",1440,455,89)
    s.text(1477,566,"Tool-output Proxy",23,bold=True,anchor="middle",width=225)
    s.rect(1630,478,336,43,"#fff7e7","#cba667",7,2)
    s.text(1784,508,"Silent – no error / warning",20,RED,True,"middle",277,italic=True)
    s.icon("cross",1930,485,29,RED)
    s.text(1800,553,"Source Data Unchanged",24,RED,True,"middle",350)
    s.text(17,620,"C  Evaluation Metrics",25,bold=True)
    s.text(1000,620,"Evaluation Metrics",29,bold=True,anchor="middle")
    metrics=[("TSR",["Task Success Rate"],"#4162cf","#edf1ff","trophy"),
             ("PAR / VPA",["Poison adoption /","after validation"],"#c73532","#fcecec","downchart"),
             ("BCR",["Blind Compliance Rate"],ORANGE,"#fff2e0","eye"),
             ("ADR",["Anomaly Detection Rate"],PURPLE,"#f5eefc","alert"),
             ("VR",["Validation Rate"],"#4d965c","#ebf7ed","shield"),
             ("RR",["Recovery Rate"],"#535e73","#eff1f5","recovery")]
    for i,(label,desc,color,fill,icon) in enumerate(metrics):
        x=9+i*332;w=320
        s.panel(x,643,w,123,color,fill)
        s.rect(x,643,w,48,color,color,12)
        s.icon(icon,x+15,661,66,NAVY)
        s.text(x+197,677,label,27,WHITE,True,"middle",224)
        s.lines(x+197,732 if len(desc)==1 else 719,desc,20,25,anchor="middle",width=232)
        if i:
            s.rect(x+151,634,166,23,fill,color,4,1.5)
            s.text(x+234,651,"IF POISON DELIVERED",12.8,color,True,"middle",157)
    s.rect(9,790,1980,53,NAVY,NAVY,10)
    s.text(30,825,"D  Generic Guard: Four-step Protocol",25,WHITE,True,width=680)
    s.text(967,825,"Evidence Verification",27,WHITE,True,"middle",390)
    s.rect(1171,798,803,36,"#4f995d",stroke="none",r=8)
    s.text(1572,824,"Check Evidence and Select the Final Answer",25,WHITE,True,"middle",770)
    cards=[(9,"#4162cf","#f2f5ff",["Generic","Expectation"]),
           (507,ORANGE,"#fff6e7",["Primary","Tool Route"]),
           (1005,PURPLE,"#f6effc",["Verification","Route"]),
           (1503,"#4d965c","#eff9ef",["Answer","Selection"])]
    for i,(x,color,fill,title) in enumerate(cards):
        s.panel(x,860,485,247,color,fill)
        s.rect(x,860,485,70,color,color,14)
        s.circle(x+44,895,23,WHITE)
        s.text(x+44,905,str(i+1),27,color,True,"middle")
        s.lines(x+88,889,title,26,28,color=WHITE,bold=True,width=256)
        slider(s,x+342,884,color)
    s.icon("engineer",29,955,100)
    s.text(79,1090,"Prompt",22,anchor="middle")
    for x,y,label,kind in [(172,952,["Value","Ranges"],"chart"),(282,952,["Schema","Bindings"],"schema"),
                           (395,952,["Rank/Label","Swap"],"tag"),(172,1024,["Plausible","Values"],"ratio"),
                           (282,1024,["Denom.","Swap"],"sign"),(395,1024,["Null/sign","Filter"],"filter")]:
        s.icon(kind,x-17,y,31)
        s.lines(x,y+48,label,17.5,20,anchor="middle",width=103)
    s.text(530,962,"Primary pathway",23)
    s.icon("camera",753,952,45);s.icon("sensor",851,952,45)
    s.path("M 533 1004 L 940 1004 L 940 989 L 977 1025 L 940 1061 L 940 1045 L 533 1045 Z",ORANGE,"#eee2ce",2.5)
    s.lines(530,1076,["Run the agent","with tools."],22,24)
    s.icon("sensor",782,1050,43);s.icon("camera",849,1050,43)
    s.text(881,1098,"monitoring",17,anchor="middle")
    for left in [494,992,1490]:
        s.arrow([(left,994),(left+28,994)],BLUE,5,15)
    s.lines(1028,961,["Additional tool evidence","from the same source"],22,27,width=403)
    s.path("M 1030 1013 L 1216 1013 L 1216 1001 L 1253 1026 L 1216 1051 L 1216 1039 L 1030 1039 Z",PURPLE,"#e0d4ee",2.5)
    s.icon("gear",1280,1011,62,PURPLE);s.icon("magnify",1393,1006,69,BLUE)
    s.lines(1028,1073,["Returns a second","answer"],21,24,width=222)
    s.text(1310,1093,"Recompute",17,anchor="middle",width=105)
    s.lines(1427,1072,["Inspect","Metadata"],18,21,anchor="middle",width=115)
    s.text(1524,965,"Select",23);s.text(1690,965,"answer",23,anchor="middle")
    s.icon("robot",1526,1014,69,GREEN);s.icon("robot",1600,979,124,GREEN);s.icon("robot",1730,1026,58,GREEN)
    s.lines(1877,969,["Use the","Route 2","answer"],25,30,anchor="middle",width=183)
    s.rect(1800,1058,174,38,RED,RED,8)
    s.text(1887,1084,"Route 2 answer selected",17,WHITE,True,"middle",158)
    return s


def render(svg,pdf):
    surface=cairo.PDFSurface(str(pdf),396,396*H/W)
    surface.set_metadata(cairo.PDF_METADATA_TITLE,svg.stem+" — native vector reconstruction")
    surface.set_metadata(cairo.PDF_METADATA_SUBJECT,"Native vector shapes and embedded text; no raster image elements.")
    context=cairo.Context(surface)
    viewport=Rsvg.Rectangle();viewport.x=0;viewport.y=0;viewport.width=396;viewport.height=396*H/W
    handle=Rsvg.Handle.new_from_file(str(svg))
    handle.render_document(context,viewport)
    surface.finish()


def main():
    preserved={str(p.relative_to(ROOT)):digest(p) for p in [FIG/"figure1.png",FIG/"figure2.png",FIG/"figure1.pdf",FIG/"figure2.pdf"]}
    report={"preserved_original_sha256":preserved,"font":"Arial; Courier New for code", "figures":[]}
    for n,make in [(1,figure1),(2,figure2)]:
        s=make();svg=FIG/f"figure{n}_vector.svg";pdf=svg.with_suffix(".pdf")
        s.write(svg);render(svg,pdf)
        reader=PdfReader(pdf)
        assert len(reader.pages)==1 and not list(reader.pages[0].images)
        assert not list(s.root.iter(f"{{{NS}}}image"))
        extracted=reader.pages[0].extract_text()
        assert len(extracted)>200
        report["figures"].append({"svg":svg.name,"pdf":pdf.name,"svg_sha256":digest(svg),"pdf_sha256":digest(pdf),
            "embedded_raster_images":0,"text_selectable":True,"text_elements":s.texts})
    for name,expected in preserved.items():assert digest(ROOT/name)==expected
    (FIG/"vector_rebuild_manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"preserved_originals":list(preserved),"outputs":[{k:v for k,v in f.items() if k!="text_elements"} for f in report["figures"]]},indent=2))


if __name__=="__main__":main()
