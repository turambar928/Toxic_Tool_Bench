"""Localized text replacements on the user's ORIGINAL Figure 2 PNG.
Keep original artwork, panel geometry, shadows, icons and four-step sequence.
User explicitly authorized local programmatic PNG edits.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path.cwd()
p=ROOT/'figures/figure2.png'
im=Image.open(p).convert('RGB');src=im.copy();s=im.width/2048;d=ImageDraw.Draw(im)
regular='/System/Library/Fonts/Supplemental/Arial Narrow.ttf'
bold='/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf'
edits=[]
def rect(b):return tuple(round(v*s) for v in b)
def erase(b,sample_x):
 x,y,x2,y2=rect(b)
 if isinstance(sample_x,tuple):
  color=src.getpixel(tuple(round(v*s) for v in sample_x));d.rectangle((x,y,x2-1,y2-1),fill=color);return
 sx=round(sample_x*s)
 # Extend a clean background scanline; this preserves original vertical gradients.
 for yy in range(y,y2):d.line((x,yy,x2-1,yy),fill=src.getpixel((sx,yy)))
def text(b,t,size=25,weight=True,color='#111111',align='center'):
 x,y,x2,y2=rect(b);fs=size
 while True:
  f=ImageFont.truetype(bold if weight else regular,round(fs*s));gap=round(fs*s*.10)
  q=d.multiline_textbbox((0,0),t,font=f,spacing=gap,align=align)
  w,h=q[2]-q[0],q[3]-q[1]
  if w<x2-x-4*s and h<y2-y-3*s:break
  fs-=.25
  if fs<9:raise ValueError(('Text does not fit',t,b))
 tx=x+(x2-x-w)/2 if align=='center' else x+2*s
 ty=y+(y2-y-h)/2-q[1]
 d.multiline_text((tx,ty),t,font=f,spacing=gap,fill=color,align=align)
def replace(b,t,sample_x,size=25,weight=True,color='#111111',align='center'):
 erase(b,sample_x);text(b,t,size,weight,color,align);edits.append((b,t))
# Header: preserve corner graphics and gradient.
replace((560,19,1491,63),'Figure 2 | ToxicBench and Evidence Verification',530,34,True,'white')
# A: preserve all task icons, badges and operator cells.
replace((16,101,267,128),'A  Task Suites',280,25,align='left')
replace((888,92,1343,128),'Cross-model Tasks',800,30)
# Use existing blank heading space to distinguish larger evaluations without moving panels.
text((1430,95,2025,126),'Expanded: 120 tasks  |  Multi-table: 13 tasks',24)
replace((40,216,336,243),'Operator examples across suites:',325,21,True,'#36589b',align='left')
replace((1069,216,1395,243),'Operator examples across suites:',1385,21,True,'#70399c',align='left')
replace((751,260,914,289),'Rank Swap',740,23)
# B: preserve tool, proxy, database and matching illustrations.
replace((866,367,1235,398),'Same Query and Source Data',824,29)
replace((787,433,951,458),'Paired Task',966,26)
replace((984,533,1068,578),'Matched\nSettings',977,23,False)
# The cross in the matching diamond is now an equals sign.
replace((1007,485,1042,514),'=',1023,28)
# Above patch must be a clean diamond-interior fill (sampling the old cross is unsafe).
d.rectangle(rect((1007,485,1042,514)),fill=src.getpixel((round(1024*s),round(479*s))))
text((1007,485,1042,514),'=',27)
replace((1290,533,1622,566),'Tool-output Proxy',1640,25)
text((1700,537,2006,568),'Source Data Unchanged',23,True,'#8d2929')
replace((1283,484,1390,516),"o′ = P(o; q)",1387,23,False,'#a32727')
# C: keep all six original metric panels and their icon artwork.
replace((17,608,325,636),'C  Evaluation Metrics',344,25,align='left')
replace((905,600,1170,636),'Evaluation Metrics',1190,29)
replace((28,751,89,774),'',94,18)
replace((465,661,559,697),'PAR / VPA',556,26,True,'white')
replace((442,729,655,767),'',(570,768),19,False)
im.paste(src.crop(rect((587,671,665,743))),(round(587*s),round(671*s)))
text((444,743,660,772),'Poison adoption / after validation',19,False)
# Match the existing exposure badge, without changing the original BCR/ADR/VR/RR cards.
badge=src.crop(rect((896,637,1021,662)))
im.paste(badge,(round(553*s),round(637*s)))
# D: preserve the four-step diagram, not the rejected four-method replacement.
replace((39,809,522,843),'D  Generic Guard: Four-step Protocol',531,25,True,'white',align='left')
replace((885,807,1164,845),'Evidence Verification',855,29,True,'white')
replace((1213,813,1966,842),'Check Evidence and Select the Final Answer',1200,26,True,'white')
# 1. Generic prompt, not a learned or oracle-informed expectation.
replace((95,882,300,939),'Generic\nExpectation',286,25,True,'white',align='left')
replace((219,1082,283,1127),'Plausible\nValues',288,21,False)
replace((44,1094,150,1127),'Prompt',161,24,False)
# 2. Primary route: preserve its execution devices and arrow.
replace((547,1068,795,1128),'Run the agent\nwith tools.',538,24,False,align='left')
# 3. Fresh execution is not an independent data source or a guarantee of correctness.
replace((1054,958,1259,1010),'Additional tool evidence\nfrom the same source',(1200,1014),23,False,align='left')
replace((1058,1088,1305,1128),'Returns a second answer',1045,23,False,align='left')
erase((1302,1077,1515,1129),(1200,1077))
text((1304,1080,1410,1127),'Recompute',21,False)
text((1413,1080,1513,1127),'Inspect\nMetadata',21,False)
# 4. Keep scanner illustration as output-selection metaphor; remove automatic gating claims.
replace((1601,882,1792,939),'Answer\nSelection',1785,26,True,'white',align='left')
replace((1570,959,1656,987),'Select',1560,24,False,align='left')
replace((1725,959,1814,987),'answer',1818,23,False)
# Replace the three status icons and labels locally, leaving the gate illustration intact.
replace((1836,960,2027,1076),'Use the\nRoute 2\nanswer',2026,28,False)
replace((1822,1087,2012,1118),'Route 2 answer selected',1830,22,True,'white')
# The badge fill is solid red; restore it independently of original text pixels.
d.rounded_rectangle(rect((1820,1083,2017,1122)),radius=round(7*s),fill='#c83639')
text((1825,1086,2012,1118),'Route 2 answer selected',22,True,'white')
out=ROOT/'figures/figure2_revised_v2.png';im.save(out,optimize=True,dpi=(300,300))
(ROOT/'output/imagegen/figure_revision_20260916/figure2_v2_changes.txt').write_text('\n'.join(f'{b}: {t}' for b,t in edits)+'\n')
print(out)
