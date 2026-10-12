"""Charts aggregate real records; no simulated benchmarks or filled observations."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

INK = '#16352f'
TEAL = '#167d72'
GOLD = '#d3a34a'
PALETTE = ['#167d72', '#d3a34a', '#5f7fa5', '#b87965', '#91a881', '#9477a5', '#52665e']
LABELS = {'price_per_sqm': 'Median price / m² (S$)', 'resale_price': 'Resale price (S$)',
          'remaining_lease_years': 'Remaining lease (years)', 'lease': 'Median remaining lease (years)',
          'area': 'Median floor area (m²)', 'mrt': 'Nearest MRT distance (km)',
          'cbd': 'CBD distance (km)', 'school': 'Selected-school distance (km)',
          'transactions': 'Transactions', 'town': 'Town', 'longitude': 'Longitude (°E)',
          'latitude': 'Latitude (°N)', 'floor_area_sqm': 'Floor area (m²)'}


def style(fig, height=450):
    fig.update_layout(template='plotly_white', height=height, paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Arial, sans-serif', color=INK, size=12),
                      margin=dict(l=35, r=20, t=35, b=35), colorway=PALETTE,
                      hoverlabel=dict(bgcolor='#16352f', font_color='white'),
                      legend=dict(orientation='h', y=1.08), transition_duration=350)
    fig.update_xaxes(gridcolor='#e7ece8', zeroline=False)
    fig.update_yaxes(gridcolor='#e7ece8', zeroline=False)
    return fig


def monthly_chart(df, metric):
    a = df.groupby('month', sort=True).agg(value=(metric, 'median'), n=('record_id', 'size')).reset_index()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=.12, row_heights=[.73, .27])
    fig.add_trace(go.Scatter(x=a.month, y=a.value, mode='lines+markers', line=dict(color=TEAL, width=3),
                            marker_size=4, customdata=a[['n']], name='Monthly median',
                            hovertemplate='%{x}<br>S$%{y:,.0f}<br>%{customdata[0]:,} transactions<extra></extra>'), row=1, col=1)
    fig.add_trace(go.Bar(x=a.month, y=a.n, marker_color='#b9d5cb', name='Transactions',
                        hovertemplate='%{x}<br>%{y:,} transactions<extra></extra>'), row=2, col=1)
    fig.update_yaxes(title_text=LABELS[metric].replace('Resale price', 'Median resale price'), row=1, col=1)
    fig.update_yaxes(title_text='Sales', row=2, col=1)
    fig.update_layout(showlegend=False)
    return style(fig, 500)


def town_chart(df):
    a = df.groupby('town').agg(median=('price_per_sqm', 'median'), q1=('price_per_sqm', lambda x:x.quantile(.25)),
                              q3=('price_per_sqm', lambda x:x.quantile(.75)), n=('record_id', 'size')).sort_values('median')
    fig = go.Figure()
    for town, r in a.iterrows():
        fig.add_trace(go.Scatter(x=[r.q1, r.q3], y=[town, town], mode='lines', line=dict(color='#b9d5cb', width=7),
                                showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=a['median'], y=a.index, mode='markers', marker=dict(color=TEAL, size=9),
                            customdata=a[['n', 'q1', 'q3']], showlegend=False,
                            hovertemplate='%{y}<br>Median S$%{x:,.0f}/m²<br>IQR S$%{customdata[1]:,.0f}–%{customdata[2]:,.0f}<br>n=%{customdata[0]:,}<extra></extra>'))
    fig.update_xaxes(title='Price / m² (S$)')
    return style(fig, max(350, 25*len(a)+70))


def lease_heatmap(df, minimum):
    d = df.copy()
    d['lease_band'] = pd.cut(d.remaining_lease_years, [0,50,60,70,80,100], right=False,
                             labels=['<50','50–<60','60–<70','70–<80','80–<100'])
    a = d.groupby(['flat_type','lease_band'], observed=True).agg(median=('price_per_sqm','median'), n=('record_id','size')).reset_index()
    vals = a.pivot(index='flat_type', columns='lease_band', values='median').reindex(columns=d.lease_band.cat.categories)
    counts = a.pivot(index='flat_type', columns='lease_band', values='n').reindex_like(vals).fillna(0)
    z = vals.where(counts >= minimum)
    fig = go.Figure(go.Heatmap(z=z.to_numpy(), x=list(z.columns), y=list(z.index), customdata=counts.to_numpy(),
        colorscale='Teal', colorbar_title='S$/m²', text=np.where(z.notna(),z.round().astype('string').to_numpy(),''),
        texttemplate='%{text}', hovertemplate='%{y} · %{x} years<br>Median S$%{z:,.0f}/m²<br>n=%{customdata:,}<extra></extra>', hoverongaps=False))
    fig.update_xaxes(title='Remaining lease band (years)')
    return style(fig, 390), a


def location_2d(b):
    fig = px.scatter(b, x='longitude', y='latitude', color='price_per_sqm', size='transactions', size_max=24,
                     color_continuous_scale='Teal', hover_name='address', custom_data=['address'],
                     hover_data={'town':True,'transactions':True,'price_per_sqm':':,.0f','longitude':':.5f','latitude':':.5f'}, labels=LABELS)
    fig.update_traces(marker_line_width=.5, marker_line_color='white', opacity=.8)
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    fig.update_layout(dragmode='lasso', coloraxis_colorbar=dict(title='S$/m²', thickness=10))
    return style(fig, 510)


def spatial_3d(b, x='longitude', y='latitude', z='price_per_sqm', selected=None):
    fig=px.scatter_3d(b,x=x,y=y,z=z,color='price_per_sqm',size='transactions',size_max=16,
                     color_continuous_scale='Teal',hover_name='address',hover_data={'town':True,'transactions':True,
                     'price_per_sqm':':,.0f','lease':':.1f','mrt':':.2f'},labels=LABELS)
    fig.update_traces(marker=dict(opacity=.75, line=dict(width=0)), selector=dict(type='scatter3d'))
    if selected:
        a=b[b.address.isin(selected)]
        fig.add_trace(go.Scatter3d(x=a[x],y=a[y],z=a[z],mode='markers',name='2D selection',
                                 marker=dict(size=8,color=GOLD,line=dict(color=INK,width=2)),text=a.address,
                                 hovertemplate='%{text}<extra>Selected address</extra>'))
    fig.update_layout(scene=dict(xaxis_title=LABELS[x],yaxis_title=LABELS[y],zaxis_title=LABELS[z],
        bgcolor='rgba(0,0,0,0)',aspectmode='cube',camera=dict(eye=dict(x=1.6,y=1.6,z=1.0))),
        coloraxis_colorbar=dict(title='S$/m²',thickness=10),uirevision=f'{x}-{y}-{z}')
    return style(fig, 560)


def time_bubbles(df, minimum, dimensions=2, motion=True):
    a=df.groupby(['quarter','town'],sort=True).agg(price_per_sqm=('price_per_sqm','median'),
        lease=('remaining_lease_years','median'),area=('floor_area_sqm','median'), transactions=('record_id','size')).reset_index()
    a=a[a.transactions>=minimum].sort_values(['quarter','town'])
    if a.empty:
        return None,a
    towns=sorted(a.town.unique())
    # Stable town-to-trace assignments prevent one town morphing into another.
    quarters=sorted(a.quarter.unique())
    frames=[]
    colors=px.colors.qualitative.Alphabet
    max_n=a.transactions.max()
    for quarter in quarters:
        traces=[]
        for i,town in enumerate(towns):
            r=a[(a.quarter==quarter)&(a.town==town)]
            common=dict(x=r.lease.tolist(), y=r.price_per_sqm.tolist(), name=town, legendgroup=town,
                mode='markers', customdata=r[['town','transactions','area']].to_numpy(),
                marker=dict(size=(32*np.sqrt(r.transactions/max_n)).tolist(), color=colors[i%len(colors)],opacity=.8),
                hovertemplate='%{customdata[0]}<br>Lease %{x:.1f} years<br>S$%{y:,.0f}/m²<br>%{customdata[1]:,} sales<br>Area %{customdata[2]:.1f} m²<extra></extra>')
            traces.append(go.Scatter3d(z=r.area.tolist(),**common) if dimensions==3 else go.Scatter(**common))
        frames.append(go.Frame(name=quarter, data=traces, traces=list(range(len(towns)))))
    fig=go.Figure(data=frames[0].data,frames=frames)
    def padded(s):
        lo,hi=s.min(),s.max(); gap=max((hi-lo)*.08,1); return [lo-gap,hi+gap]
    if dimensions==3:
        fig.update_layout(scene=dict(xaxis=dict(title=LABELS['lease'],range=padded(a.lease)),
            yaxis=dict(title=LABELS['price_per_sqm'],range=padded(a.price_per_sqm)),
            zaxis=dict(title=LABELS['area'],range=padded(a.area)),aspectmode='cube'))
    else:
        fig.update_xaxes(title=LABELS['lease'],range=padded(a.lease))
        fig.update_yaxes(title=LABELS['price_per_sqm'],range=padded(a.price_per_sqm))
    duration=650 if motion else 0
    args=dict(frame=dict(duration=duration,redraw=dimensions==3),transition=dict(duration=350 if motion and dimensions==2 else 0),fromcurrent=True)
    buttons=[dict(label='▶ Play',method='animate',args=[None,args]),
             dict(label='Ⅱ Pause',method='animate',args=[[None],dict(frame=dict(duration=0,redraw=False),mode='immediate',transition=dict(duration=0))])]
    fig.update_layout(updatemenus=[dict(type='buttons',direction='left',x=0,y=1.18,buttons=buttons)] if motion and dimensions==2 else [],
        sliders=[dict(active=0,currentvalue=dict(prefix='Quarter · '),pad=dict(t=40),steps=[dict(label=q,method='animate',args=[[q],dict(mode='immediate',frame=dict(duration=duration,redraw=True),transition=dict(duration=0))]) for q in quarters])],
        showlegend=False)
    return style(fig,650),a
