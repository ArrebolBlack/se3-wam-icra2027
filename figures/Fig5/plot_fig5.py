"""Draw real Fig. 5 cells; pending is a categorical missing code, never zero."""
from pathlib import Path
import argparse
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Rectangle
from matplotlib.cm import ScalarMappable
from matplotlib.text import Text
import pymupdf
from PIL import Image

ROOT=Path(__file__).resolve().parent
ROWS=['Uniform coarse flow','Uniform fine flow','No scene-flow supervision','No target history',
      'No future supervision','No auxiliary objectives']
IDS=['no_se3','fine_flow','no_flow','no_history','no_future','no_aux']
NR=len(IDS)
GROUPS=['All','Grasp','Place','Pass','Capture','Impact','Rotation-sensitive','Context-active']
COLS=['All','Grasp','Place','Pass','Capture','Impact','Rot.','Ctx.']
CMAP=LinearSegmentedColormap.from_list('orange_white_blue',['#C95318','#F2F2EF','#1674AB'],N=257)
NORM=Normalize(-15,15,clip=True)
NA='#DCDCDC'

def luminance(rgb):
    x=np.asarray(rgb)[:3]
    x=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
    return float(x @ np.array([.2126,.7152,.0722]))

def foreground(rgb):
    L=luminance(rgb)
    return '#FFFFFF' if 1.05/(L+.05)>(L+.05)/.05 else '#000000'

def draw(layout,output):
    cells=json.loads((ROOT/'data/cells.json').read_text())
    lookup={(c['added_latency_ms'],c['variant'],c['group']):c for c in cells}
    compact=layout=='original'
    paper=layout=='paper'
    stacked=layout=='stacked'
    stacked_panel_height=.174*NR
    width,height=(3.25,.53+2*stacked_panel_height+.37+.46) if stacked else ((3.25,1.4) if compact else ((6.875,1.92) if paper else (6.875,2.45)))
    # The original-budget diagnostic keeps 7 pt labels instead of hiding crowding with tiny text.
    fs=7 if compact else (7.5 if stacked else 8)
    plt.rcParams.update({'font.family':'Arial','font.size':fs,'svg.fonttype':'none',
                         'pdf.fonttype':42,'ps.fonttype':42,'axes.unicode_minus':True,
                         'savefig.facecolor':'white','hatch.linewidth':.23})
    fig=plt.figure(figsize=(width,height),facecolor='white',dpi=144)
    if compact:
        left,right,gap,bottom,top=1.05,.04,.12,.43,.36
        labels=['Uniform flow','Fine flow','No flow sup.','No tgt. history','No future sup.','No aux. obj.']
        header_y=height-.05
    elif stacked:
        left,right,gap,bottom,top=.78,.02,.37,.46,.53
        labels=['Uniform coarse','Uniform fine','No flow sup.','No target hist.','No future sup.','No aux. obj.']
        header_y=height-.035
    else:
        left,right,gap,bottom,top=(1.53,.08,.22,.45,.60) if paper else (1.53,.08,.22,.86,.68)
        labels=ROWS
        header_y=height-(.035 if paper else .085)
    pw=width-left-right if stacked else (width-left-right-gap)/2
    ph=stacked_panel_height if stacked else height-bottom-top
    axes=[]
    annotations=[]
    for panel,(delay,title) in enumerate([(0,'Native latency'),(150,'+150 ms added latency')]):
        ax_left=left if stacked else left+panel*(pw+gap)
        ax_bottom=(height-top-ph if panel==0 else bottom) if stacked else bottom
        ax=fig.add_axes([ax_left/width,ax_bottom/height,pw/width,ph/height])
        axes.append(ax)
        ax.set_xlim(-.5,7.5);ax.set_ylim(NR-.5,-.5)
        ax.set_xticks(range(8),COLS,rotation=45,ha='left',rotation_mode='anchor')
        ax.xaxis.tick_top()
        if stacked and panel==1:
            ax.set_xticklabels([])
        ax.tick_params(axis='both',length=0,pad=2,labelsize=fs)
        ax.set_yticks(range(NR),labels if panel==0 or stacked else ['']*NR)
        for sp in ax.spines.values():sp.set_visible(False)
        for i,variant in enumerate(IDS):
            for j,group in enumerate(GROUPS):
                c=lookup[(delay,variant,group)]
                missing=c['status']!='complete'
                value=c['delta_pp']
                if missing:
                    if value is not None or c['ci_low_pp'] is not None or c['ci_high_pp'] is not None or c['bold']:
                        raise ValueError('NA cannot carry a numeric estimate, interval or bold flag')
                    color=NA;text='NA';fg='#555555';weight='normal'
                else:
                    if not all(np.isfinite(c[k]) for k in ('delta_pp','ci_low_pp','ci_high_pp')):
                        raise ValueError('complete cells require finite values and intervals')
                    expected=c['ci_low_pp']>0 or c['ci_high_pp']<0
                    if c['bold']!=expected:raise ValueError('bold flag does not match paired CI')
                    color=CMAP(NORM(value));fg=foreground(color)
                    text=(f'{value:+.1f}'.replace('-','−')) if round(value,1)!=0 else '0.0'
                    weight='bold' if c['bold'] else 'normal'
                ax.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor=color,edgecolor='white',linewidth=.45))
                t=ax.text(j,i,text,ha='center',va='center',fontsize=7 if compact else 7.2,fontweight=weight,color=fg)
                annotations.append((t,ax,j,i))
        ax.axvline(5.5,color='#656565',lw=.55)
        title_y=(ax_bottom+ph+.23) if stacked and panel==1 else header_y
        fig.text((ax_left+pw/2)/width,title_y/height,title,
                 ha='center',va='top',fontsize=fs+.5,fontweight='bold')
    # One shared diverging colorbar, explicit saturated endpoints.
    cbx=1.05 if stacked else (left if compact else 2.18)
    cbw=2.04 if stacked else ((width-left-right) if compact else 3.52)
    cby=.15 if stacked else (.23 if compact else (.15 if paper else .47))
    cax=fig.add_axes([cbx/width,cby/height,cbw/width,.065/height])
    cb=fig.colorbar(ScalarMappable(norm=NORM,cmap=CMAP),cax=cax,orientation='horizontal',
                    ticks=[-15,0,15],extend='both',extendfrac=.025)
    cb.solids.set_rasterized(False)
    cb.solids.set_edgecolor('face')
    cb.outline.set_visible(False)
    cb.set_ticklabels(['≤−15','0','≥+15'])
    cb.ax.tick_params(length=2,width=.4,pad=1,labelsize=fs)
    if compact:
        fig.text(.025,.12,'ΔSR (pp); control − full',fontsize=7,va='center')
        fig.text(.025,.015,'Design preview · NA: pending',fontsize=7,va='bottom')
    elif stacked:
        fig.text(.05/width,.30/height,'ΔSR (pp)',fontsize=8,va='center')
        fig.text(cbx/width,.285/height,'Worse',fontsize=7.7,color='#9A3E13',ha='left')
        fig.text((cbx+cbw)/width,.285/height,'Better',fontsize=7.7,color='#155D8B',ha='right')
        fig.patches.append(Rectangle((.05/width,.075/height),.10/width,.105/height,
                                     transform=fig.transFigure,facecolor=NA,edgecolor='#888888',lw=.3))
        fig.text(.20/width,.085/height,'NA: pending',fontsize=7.2,va='bottom',color='#4C4C4C')
    elif paper:
        # The paper caption owns group expansions and interval semantics.
        fig.text(.06/width,.30/height,'ΔSR = control − full (pp)',fontsize=8,va='center')
        fig.text(cbx/width,.285/height,'Worse',fontsize=7.7,color='#9A3E13',ha='left')
        fig.text((cbx+cbw)/width,.285/height,'Better',fontsize=7.7,color='#155D8B',ha='right')
        fig.text((cbx+cbw+.16)/width,.19/height,'Color saturates\nat ±15 pp',fontsize=7,va='center')
        fig.patches.append(Rectangle((.06/width,.075/height),.13/width,.105/height,
                                     transform=fig.transFigure,facecolor=NA,edgecolor='#888888',lw=.3))
        fig.text(.25/width,.085/height,'NA: data pending',fontsize=7.4,va='bottom',color='#4C4C4C')
    else:
        fig.text(.06/width,.55/height,'ΔSR = control − full (pp)',fontsize=8,va='center')
        fig.text(cbx/width,.665/height,'Worse',fontsize=7.7,color='#9A3E13',ha='left')
        fig.text((cbx+cbw)/width,.665/height,'Better',fontsize=7.7,color='#155D8B',ha='right')
        fig.text((cbx+cbw+.16)/width,.51/height,'Color saturates\nat ±15 pp',fontsize=7,va='center')
        fig.text(.06/width,.24/height,'Rot.: rotation-sensitive   Ctx.: context-active',fontsize=7.5,va='center')
        fig.text(3.66/width,.24/height,'Bold: paired 95% interval excludes 0',fontsize=7.5,va='center')
        fig.text(.06/width,.045/height,'DESIGN PREVIEW — final-model paired results pending',
                 fontsize=7.4,va='bottom',color='#4C4C4C')
        fig.patches.append(Rectangle((5.43/width,.04/height),.13/width,.105/height,
                                     transform=fig.transFigure,facecolor=NA,edgecolor='#888888',lw=.3))
        fig.text(5.61/width,.045/height,'NA: unavailable',fontsize=7.4,va='bottom',color='#4C4C4C')
    output.mkdir(parents=True,exist_ok=True)
    path=output/'fig5'
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    overflow=[]
    for artist in fig.findobj(Text):
        if not artist.get_visible() or not artist.get_text():continue
        b=artist.get_window_extent(renderer)
        if b.x0<-.5 or b.y0<-.5 or b.x1>fig.bbox.width+.5 or b.y1>fig.bbox.height+.5:
            overflow.append(artist.get_text())
    # Width required for the full admissible range, not fabricated data in plotted cells.
    from matplotlib.font_manager import FontProperties
    worst_width=renderer.get_text_width_height_descent('−100.0',FontProperties(family='Arial',size=7 if compact else 7.2,weight='bold'),False)[0]/fig.dpi*72
    meta=dict(layout=layout,width_in=width,height_in=height,font_pt=fs,control_count=NR,row_ids=IDS,cell_width_pt=pw/8*72,
              worst_admissible_label_width_pt=worst_width,out_of_canvas=overflow,
              available_cells=sum(c['status']=='complete' for c in cells),pending_cells=sum(c['status']!='complete' for c in cells))
    for fmt in ('svg','pdf','png'):
        fig.savefig(path.with_suffix('.'+fmt),dpi=600,bbox_inches=None,facecolor='white')
    with Image.open(path.with_suffix('.png')) as raster:
        raster.convert('RGB').save(path.with_suffix('.png'),dpi=(600,600))
    plt.close(fig)
    doc=pymupdf.open(path.with_suffix('.pdf'))
    page=doc[0]
    page.get_pixmap(dpi=144).save(output/'preview.png')
    page.get_pixmap(dpi=96).save(output/'print_96dpi.png')
    page.get_pixmap(dpi=300).save(output/'print_300dpi.png')
    im=Image.open(output/'print_300dpi.png').convert('L')
    im.save(output/'grayscale.png',dpi=(300,300))
    meta.update(pdf_size_pt=list(page.rect)[2:],pdf_raster_image_count=len(page.get_images()),
                pdf_fonts=[font[3] for font in page.get_fonts()],png_px=list(Image.open(path.with_suffix('.png')).size))
    (output/'layout_report.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--layout',choices=['original','wide','paper','stacked'],default='stacked')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();draw(a.layout,a.output)
