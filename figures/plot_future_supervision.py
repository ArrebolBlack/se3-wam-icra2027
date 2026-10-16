"""Plot verified FUTURE0 success rates without estimating new intervals.

Source: accepted independent1260 analysis. Each arm has one training seed.
The source summaries provide point estimates and paired McNemar tests, but no
confidence intervals; this plot does not add intervals or combine fixed140.
"""
from pathlib import Path
import argparse
import csv
import json
import shutil
from generate_figures import start, text, line, rect, render, COL, ROOT

DEFAULT=Path(r"C:/workspace/se3-wam-research/docs/experiments/FUTURE0/results/independent1260/analysis")
ARMS=['P00','P01','P02','P03','P04','P05','P06','P07','P08','P09','Aalpha','P12','P13','P14','P15']
FOCUS={'P00','P03','P05','P07','P09'}

def main(source):
    with (source/'arm-summary.csv').open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    analysis=json.loads((source/'analysis.json').read_text(encoding='utf-8'))
    assert [r['arm'] for r in rows] == ARMS
    assert all(int(r['n']) == 1260 for r in rows)
    assert analysis['training_seeds_per_arm'] == 1
    assert analysis['cross_arm_scene_seed_pairing_checked'] is True
    assert sum(int(r['n']) for r in rows) == 18900
    for r in rows:
        assert abs(float(r['sr'])-int(r['successes'])/int(r['n'])) < 1e-12
    # Preserve exactly the source summary used for the visual, not a second fact store.
    shutil.copyfile(source/'arm-summary.csv',ROOT/'future_supervision_data.csv')
    h=222
    s=start(h)
    text(s,7,13,'Future supervision across 15 representation conditions',12,weight='bold')
    text(s,7,29,'Success rate (%)',10.667)
    text(s,653,29,'One training seed per arm · no intervals',10.667,color=COL['gray'],anchor='end')
    left,right,top,bottom=39,647,49,143
    ymin,ymax=58,66
    def y(v): return bottom-(v-ymin)/(ymax-ymin)*(bottom-top)
    for tick in (58,60,62,64,66):
        line(s,left,y(tick),right,y(tick),color='#DDE1E4',width=.6)
        text(s,left-7,y(tick)+3.5,str(tick),10.667,anchor='end')
    line(s,left,top,left,bottom,color=COL['gray'],width=.8)
    line(s,left,bottom,right,bottom,color=COL['gray'],width=.8)
    base=100*float(rows[0]['sr'])
    line(s,left,y(base),right,y(base),color='#6E777D',width=.8,dash='3 2')
    # Uniform symbol and color; bold labels only mark the main-text discussion set.
    for i,r in enumerate(rows):
        x=left+15+i*(right-left-28)/14
        rate=float(r['sr'])*100
        s.append(f'<circle cx="{x}" cy="{y(rate)}" r="3.3" fill="{COL["blue"]}" stroke="white" stroke-width=".6"/>')
        s.append(f'<rect x="{x-16}" y="{y(rate)-18}" width="32" height="12" fill="white"/>')
        text(s,x,y(rate)-7,f'{rate:.2f}',10.667,anchor='middle')
        label='Aα' if r['arm']=='Aalpha' else r['arm']
        text(s,x,161,label,10.667,weight='bold' if r['arm'] in FOCUS else 'normal',anchor='middle')
        text(s,x,179,str(r['successes']),10.667,color=COL['gray'],anchor='middle')
    text(s,7,179,'nₛ',10.667,color=COL['gray'])
    line(s,7,195,27,195,color='#6E777D',width=.8,dash='3 2')
    text(s,33,199,'P00: 791 / 1260 = 62.78%',10.667)
    text(s,653,199,'nₛ: successes / 1260 scenes',10.667,color=COL['gray'],anchor='end')
    text(s,7,216,'14 tasks × 90 scenes; original validation distribution; fixed140 kept separate.',10.667,color=COL['gray'])
    s.append('</g></svg>')
    path=ROOT/'future_supervision.svg'
    path.write_text('\n'.join(s),encoding='utf-8')
    render(path)
    print(path.name)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=DEFAULT)
    main(parser.parse_args().source)
