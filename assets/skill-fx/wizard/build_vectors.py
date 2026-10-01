"""Deterministic single-frame spell geometry, independent of character sprites."""
from pathlib import Path
import math
import random

ROOT = Path(__file__).parent

def save(name, w, h, body, defs=''):
    fit=' preserveAspectRatio="none"' if name.startswith(('gravity-beam','gravity-foot','blizzard')) else ''
    (ROOT / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"{fit}><defs>{defs}</defs>{body}</svg>', encoding='utf-8')

def sigil():
    s = ''.join(f'<circle r="{r}"/>' for r in (190,181,153,63,48))
    s += '<path d="M0 -153L132.5 76.5H-132.5Z M0 153L132.5 -76.5H-132.5Z"/>'
    for i in range(6):
        a=math.radians(i*60); x,y=math.sin(a)*106,math.cos(a)*106
        s += f'<g transform="translate({x} {y})"><circle r="32"/><circle r="25"/><path d="M0 -24L21 12H-21Z M0 24L21 -12H-21Z"/></g>'
    for i in range(48):
        s += f'<path transform="rotate({i*7.5})" d="M0 -164V-{174 if i%4 else 179}"/>'
    return s+'<path d="M0 -47L41 24H-41Z M0 47L41 -24H-41Z"/>'

mark=sigil()
planes=''
for x,y,color in [(170,303,'#42cfff'),(230,299,'#ff614d'),(290,295,'#b68aff')]:
    geometry=f'<g transform="translate({x} {y}) rotate(-8) scale(.48 1)" fill="none" stroke="{color}" stroke-width="2.6">{mark}</g>'
    planes+=f'<g opacity=".65" filter="url(#g)">{geometry}</g>'+geometry
save('triple-circle.svg',550,570,planes,'<filter id="g" x="-50%" y="-30%" width="200%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>')

circle_defs='''<filter id="halo" x="-30%" y="-50%" width="160%" height="200%"><feGaussianBlur stdDeviation="5"/></filter><radialGradient id="pool"><stop stop-color="#fff8ff" stop-opacity=".45"/><stop offset=".75" stop-color="#dbc0ff" stop-opacity=".28"/><stop offset="1" stop-color="#a767fa" stop-opacity="0"/></radialGradient>'''
circle='<ellipse cx="320" cy="120" rx="314" ry="114" fill="url(#pool)"/>'
for color,stroke,extra in [('#a457ff',9,' filter="url(#halo)"'),('#9251ed',6,''),('#dcc0ff',3.8,''),('#fff5ff',1.9,'')]:
    circle+=f'<g transform="translate(320 120) scale(1.6 .55)" fill="none" stroke="{color}" stroke-width="{stroke}"{extra}>{mark}</g>'
save('gravity-circle.svg',640,240,circle,circle_defs)
beam='''<path d="M16 0H624V800H16Z" fill="url(#beam)"/><path d="M16 0H624V800H16Z" fill="url(#rise)"/><path d="M16 0V800 M624 0V800" stroke="#542098" stroke-opacity=".95" stroke-width="12"/><path d="M24 0V800 M616 0V800" stroke="#bb7eff" stroke-opacity=".9" stroke-width="7"/><path d="M29 0V800 M611 0V800" stroke="#fff3ff" stroke-opacity=".8" stroke-width="3"/>'''
r=random.Random(408)
for i in range(36):
    x=r.randint(35,605); y=r.randint(0,780)
    beam+=f'<path d="M{x} {y}v{r.randint(12,85)}" stroke="#e9d4ff" stroke-width="{r.choice([1,1,2])}" opacity="{r.uniform(.15,.5):.2f}"/>'
save('gravity-beam.svg',640,800,beam,'''<linearGradient id="beam" x1="0" x2="1"><stop stop-color="#af6cff" stop-opacity=".48"/><stop offset=".16" stop-color="#efdfff" stop-opacity=".52"/><stop offset=".5" stop-color="#fffaff" stop-opacity=".62"/><stop offset=".84" stop-color="#efdfff" stop-opacity=".52"/><stop offset="1" stop-color="#af6cff" stop-opacity=".48"/></linearGradient><linearGradient id="rise" x1="0" y1="1" x2="0" y2="0"><stop stop-color="#fff4ff" stop-opacity=".38"/><stop offset=".55" stop-color="#f2dfff" stop-opacity=".04"/><stop offset="1" stop-color="#f2dfff" stop-opacity="0"/></linearGradient>''')

# Continue the cylinder over the near half of the floor sigil without a seam.
beam_defs=(ROOT/'gravity-beam.svg').read_text(encoding='utf-8').split('<defs>')[1].split('</defs>')[0]
cap_path='M16 0H624A304 104.5 0 0 1 16 0Z'
cap=f'<path d="{cap_path}" fill="url(#beam)"/><path d="{cap_path}" fill="#fff4ff" fill-opacity=".38"/>'
for color,stroke,rx,ry,start,end in [('#542098',8,304,104.5,16,624),('#bb7eff',5,297,100,23,617),('#fff3ff',2,292,96,28,612)]:
    cap+=f'<path d="M{start} 0A{rx} {ry} 0 0 0 {end} 0" fill="none" stroke="{color}" stroke-width="{stroke}" opacity=".85"/>'
save('gravity-foot.svg',640,110,cap,beam_defs)

for name,count,front in [('blizzard-back.svg',480,False),('blizzard-front.svg',95,True)]:
    snow=''
    if not front:
        snow='<path d="M0 0H1200V700H0Z" fill="url(#mist)"/>'
    for i in range(count):
        x=r.randint(0,1200); y=r.randint(-30,700); size=r.uniform(1.5,4) if not front else r.uniform(3,7)
        if i%3:
            length=size*(6 if front else 4)
            snow+=f'<path d="M{x} {y}l{length*.7:.2f} {length:.2f}" stroke="#effbff" stroke-width="{size:.2f}" stroke-linecap="round" opacity="{r.uniform(.35,.9):.2f}"/>'
        else:
            snow+=f'<circle cx="{x}" cy="{y}" r="{size:.2f}" fill="#fff" opacity=".85"/>'
    save(name,1200,700,snow,'<radialGradient id="mist"><stop stop-color="#c8eeff" stop-opacity=".28"/><stop offset="1" stop-color="#a5e1ff" stop-opacity="0"/></radialGradient>')
