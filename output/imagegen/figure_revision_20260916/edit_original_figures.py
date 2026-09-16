"""Deterministic, user-authorized edits of the original ToxicBench PNGs.
Preserves source PNGs; draws English labels and replacement panels at source resolution.
Run from the repository root with Pillow installed.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path.cwd()
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
NAVY='#223650'; INK='#142536'; BLUE='#365ad4'; PURPLE='#7536d0'; GREEN='#378b50'; RED='#ae2828'
class Canvas:
 def __init__(self,path,h):
  self.im=Image.open(path).convert('RGB');self.source=self.im.copy();self.s=self.im.width/2048;self.h=h;self.d=ImageDraw.Draw(self.im)
 def box(self,b,fill,outline=None,r=0,w=1):
  b=tuple(round(v*self.s) for v in b)
  if r:self.d.rounded_rectangle(b,radius=round(r*self.s),fill=fill,outline=outline,width=max(1,round(w*self.s)))
  else:self.d.rectangle(b,fill=fill,outline=outline,width=max(1,round(w*self.s)))
 def text(self,b,text,size=24,bold=False,color=INK,align='center',pad=4):
  x,y,x2,y2=b;lines=text.split('\n'); fs=size
  while True:
   f=ImageFont.truetype(BOLD if bold else FONT,round(fs*self.s))
   spacing=round(fs*self.s*.23)
   bounds=self.d.multiline_textbbox((0,0),text,font=f,spacing=spacing,align=align)
   tw,th=bounds[2]-bounds[0],bounds[3]-bounds[1]
   if (tw <= (x2-x-2*pad)*self.s and th <= (y2-y-2*pad)*self.s) or fs<9:break
   fs-=.5
  tx=(x+x2)*self.s/2-tw/2 if align=='center' else (x+pad)*self.s
  ty=(y+y2)*self.s/2-th/2-bounds[1]
  self.d.multiline_text((tx,ty),text,font=f,fill=color,spacing=spacing,align=align)
 def arrow(self,x1,y1,x2,y2,color=INK):
  s=self.s; self.d.line((x1*s,y1*s,x2*s,y2*s),fill=color,width=round(3*s))
  if x2>x1:self.d.polygon([(x2*s,y2*s),((x2-9)*s,(y2-6)*s),((x2-9)*s,(y2+6)*s)],fill=color)
 def icon(self,crop,xy,size=None):
  tile=self.source.crop(tuple(round(v*self.s) for v in crop))
  if size:tile=tile.resize(tuple(round(v*self.s) for v in size),Image.Resampling.LANCZOS)
  self.im.paste(tile,tuple(round(v*self.s) for v in xy))
 def panel(self,b,title,color,body='#ffffff',title_size=24,head=48):
  x,y,x2,y2=b;self.box((x+2,y+4,x2+2,y2+4),'#d5dae0',r=14)
  self.box(b,body,color,r=14,w=2);self.box((x+1,y+1,x2-1,y+head),color,r=12)
  self.box((x+1,y+head-10,x2-1,y+head),color)
  self.text((x+8,y+4,x2-8,y+head-2),title,title_size,True,'white')
 def save(self,path):self.im.save(path,optimize=True,dpi=(300,300))

c=Canvas(ROOT/'figures/figure1.png',869)
# Original top banner, central agent, table, source arrow and surrounding design retained.
c.box((385,16,1720,79),NAVY,r=5);c.text((410,17,1700,77),'Figure 1 | Silent Tool Poisoning: An Example',35,True,'white')
c.box((710,212,1340,252),'#203c61');c.text((710,212,1340,252),'DATA AGENT WITH TOOL ACCESS',25,True,'white')
c.box((905,361,1170,410),'#e5ecf4');c.text((905,359,1170,412),'Data Agent\nLLM + Tool Calls',23,True)
c.box((560,274,780,309),'#d2deee');c.text((558,273,785,311),'REGISTERED TOOL',23,True)
c.box((520,325,777,389),'#252f40',r=6);c.text((526,333,772,383),'csv_tool(query)',26,False,'#b2d98b')
# Green branch: retain its outer frame, header, and icon; replace its inner content.
c.box((21,559,970,780),'white')
c.panel((35,577,415,732),'CSV Tool',GREEN,'#eef7ef',25,39)
c.box((47,626,403,719),'#24303d',r=8)
c.text((50,628,399,715),'row = stores.loc[stores["Q4 Revenue"].idxmax()]\nreturn row["Store"], row["Q4 Revenue"]',16,False,'#ffffff',align='left',pad=8)
c.panel((454,610,649,713),'Original Tool Output',GREEN,'#f1f8f2',20,41)
c.text((460,653,643,710),'No Modification',21)
c.arrow(417,662,450,662,GREEN)
c.box((688,611,958,713),'#ffffff',GREEN,r=14,w=2)
c.text((693,615,954,669),'Store B — $450,000',28,True,color='#236b36')
c.text((695,670,951,704),'Correct Observation',20)
c.arrow(651,662,684,662,GREEN)
c.box((290,761,786,818),GREEN,r=10);c.text((300,765,776,813),'CORRECT STORE–VALUE PAIR',27,True,'white')
# Red branch: preserve original outer frame/header, repaint old executor-poisoning illustration.
c.box((1078,483,2026,780),'#fffafa')
c.panel((1086,491,2016,598),'TOOL-OUTPUT POISONING','#b47b22','#fff5da',23,35)
c.text((1097,530,1633,590),'• The original tool runs successfully.\n• The proxy swaps Store A and Store B in the output.\n• No exception, error, or warning is shown.',18,False,align='left',pad=5)
for box,title,value in [((1642,534,1800,586),'Original output','Store B — $450,000'),((1837,534,2006,586),'Modified output','Store A — $450,000')]:
 c.box(box,'#ffffff','#bd964c',r=7,w=1);x,y,x2,y2=box;c.text((x,y+1,x2,y+25),title,16,True);c.text((x,y+25,x2,y2),value,17)
c.text((1778,506,1851,535),'Label swap',13,True,color=RED);c.arrow(1804,560,1833,560,RED)
c.panel((1092,610,2014,744),'MODIFIED TOOL OBSERVATION',RED,'#fff3f3',24,37)
for b,t in [((1106,656,1400,732),'Original Tool Output\nStore B — $450,000'),((1451,656,1680,732),'Output Proxy\nSwap Store Labels'),((1728,656,2001,732),'Store A — $450,000\nObservation Received by the Agent')]:
 c.box(b,'#ffffff',RED,r=12,w=2);c.text(b,t,23,True,pad=10)
c.arrow(1404,695,1446,695,RED);c.arrow(1684,695,1723,695,RED)
c.box((1290,762,1880,819),RED,r=10);c.text((1300,766,1870,814),'WRONG STORE–VALUE PAIR',28,True,'white')
c.box((355,823,1870,867),'white');c.text((363,824,1863,866),'A Successful Tool Call Can Return a Plausible but Wrong Observation',29)
c.save(ROOT/'figures/figure1_revised.png')

c=Canvas(ROOT/'figures/figure2.png',1143)
# Retain original navy top bar and corner illustrations.
c.box((400,9,1690,74),NAVY);c.text((405,10,1685,73),'Figure 2 | ToxicBench: Benchmark and Verification Protocols',31,True,'white')
c.box((1740,18,1960,62),NAVY);c.text((1740,18,1952,62),'Tool-output Poisoning',23,True,'white')
# A: retain the original colored panel headings and task icons, replace all labels and operator rows.
c.box((0,91,2048,133),'white');c.text((8,93,300,132),'A  Task Suites',25,True,align='left')
c.text((350,93,2032,132),'Cross-model: 58 Tasks | Expanded: 120 Tasks | Multi-table: 13 Tasks',27,True)
for x,x2,color,title,sub in [(7,1003,BLUE,'Numerical Tasks','Cross-model: 34 tasks | 11 CSV datasets'),(1040,2035,PURPLE,'Semantic / Schema Tasks','Cross-model: 24 tasks | 17 datasets')]:
 c.panel((x,139,x2,348),'',color,'#f0f0fa',head=63)
 c.icon((x+8,144,x+88,199),(x+8,144))
 c.box((x+95,145,x2-8,197),color);c.text((x+105,143,x+450,198),title,29,True,'white');c.text((x+450,143,x2-10,198),sub,24,False,'white')
 c.box((x+9,209,x2-7,341),'#f0f0fa');c.text((x+24,213,x2-15,246),'Operators across the benchmark:',21,True,align='left')
labels1=['Aggregate Scale','Sign Flip','Rank Swap','Ratio Inversion','Denominator Swap','Omit Filter / Unit Conversion']
labels2=['Label Swap','Treatment/Control Flip','Biased Retrieval','Column-Semantic Swap','Stale Metadata']
for start,labels,color in [(22,labels1,BLUE),(1054,labels2,PURPLE)]:
 for i,label in enumerate(labels):
  x=start+(i%3)*322;y=251+(i//3)*47;c.box((x,y,x+310,y+39),'#fafaff',color,r=7,w=1);c.text((x+3,y,x+307,y+39),label,21,True)
# B panels preserve relative sizes and colors; reuse original agent/tool illustration crops.
c.box((0,362,2048,598),'white');c.text((9,367,630,405),'B  Paired Evaluation Protocol',25,True,align='left');c.text((680,367,1700,405),'Same Query and Source Data',28,True)
c.panel((6,415,444,584),'Clean Environment',GREEN,'#e6f6e9',26,39)
c.icon((20,427,142,546),(21,462),(85,90));c.icon((286,436,419,548),(326,464),(90,83))
c.text((106,462,324,495),'Tool Call',24,True);c.arrow(119,500,317,500,GREEN);c.text((111,505,320,541),'Original Output',22)
c.text((17,555,117,580),'Data Agent',18,True);c.text((328,555,410,580),'Tool',19,True)
c.panel((478,415,1238,584),'Matched Task Pair','#66708d','#f2f3fa',26,39)
for b,t in [((488,467,691,568),'Same query\nSame source data'),((700,467,972,568),'Same model and adapter\nSame execution budget'),((986,467,1229,568),'Compare Answers\nand Trajectories')]:c.text(b,t,24,True)
c.panel((1270,415,2036,584),'Poisoned Environment',RED,'#fff0ef',26,39)
c.box((1287,473,1470,542),'#ffffff',RED,r=8,w=2);c.text((1290,473,1467,542),'Tool-output\nProxy',24,True)
c.arrow(1479,509,1530,509,RED);c.box((1538,468,1780,546),'white',RED,r=8,w=2);c.text((1541,470,1777,544),'Modify Returned\nObservation',23,True)
c.text((1787,470,2022,541),'No Exception\nor Warning',23,True,color=RED)
c.text((1320,550,2000,579),'Source Data Unchanged',20,True)
# C: six metric cards; no unsupported success counts or reliability claims.
c.box((0,601,2048,789),'white');c.text((9,603,635,641),'C  Evaluation Metrics',25,True,align='left');c.text((690,603,1745,641),'Task Success and Evidence Use',28,True)
metrics=[('TSR',BLUE,'Task Success Rate\nAll Runs'),('PAR / VPA','#bb3636','PAR: Poisoned-answer Adoption\nVPA: Adoption after Validation'),('BCR','#cb8330','Blind Compliance Rate'),('ADR / VR',PURPLE,'ADR: Anomaly Detection\nVR: Evidence Validation'),('RR',GREEN,'Recovery Rate'),('Human Audit','#535c72','240 Trajectories\nTwo Annotators + Adjudication')]
for i,(title,color,body) in enumerate(metrics):
 x=7+i*341;c.panel((x,657,x+329,780),title,color,'#f7f8fc',28,40);c.text((x+5,703,x+324,773),body,21,False)
 if i in (1,2,3,4):
  c.box((x+77,642,x+322,663),'#fff9e9','#bbb2a0',r=4);c.text((x+78,643,x+321,662),'EXPOSED RUNS ONLY',15,True,pad=1)
# D: replace the four old sequential stages with parallel protocol cards.
c.box((0,794,2048,1143),'white');c.box((5,799,2036,855),NAVY,r=10)
c.text((15,804,635,851),'D  Verification Protocols',27,True,'white',align='left')
c.text((626,804,1250,851),'Controlled Method Comparison',28,True,'white')
c.box((1262,807,2021,848),GREEN,r=7);c.text((1270,808,2014,847),'Matched Per-route Step and Token Limits',25,True,'white')
cards=[('1  Base',BLUE,'One ordinary route','Solve the task with tools.','Route 1 answer'),('2  Double-pass','#cb7831','Two ordinary routes','Route 2 starts without\nthe Route 1 answer.','Route 2 answer'),('3  Verification-only',PURPLE,'Ordinary route + verification route','Route 2 checks the first answer\nas an untrusted claim.','Route 2 answer'),('4  Generic Guard',GREEN,'Expectation prompt + verification route','Route 1 receives a generic expectation.\nRoute 2 checks the first answer.','Route 2 answer')]
for i,(title,color,sub,body,answer) in enumerate(cards):
 x=7+i*511;c.panel((x,867,x+498,1136),title,color,'#f5f7fb',29,54)
 c.text((x+12,933,x+486,983),sub,24,True)
 c.text((x+15,988,x+483,1058),body,23)
 c.box((x+22,1071,x+476,1121),'#ffffff',color,r=8,w=1)
 c.text((x+28,1075,x+470,1117),'Final answer: '+answer,24,True)
c.save(ROOT/'figures/figure2_revised.png')
print('Saved figures/figure1_revised.png and figures/figure2_revised.png at original resolution.')
