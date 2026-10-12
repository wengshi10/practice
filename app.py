from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from src.analytics_data import load_data, building_summary
from src.animated_view import animated_view
from src.analytics_charts import (style, monthly_chart, town_chart, lease_heatmap,
                                  location_2d, spatial_3d, time_bubbles, LABELS, TEAL)

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='HDB Observatory · Visual Analytics', page_icon='◈', layout='wide')
st.markdown('''<style>
.stApp {background:#f5f6f1;color:#16352f}
.block-container {padding-top:2rem;padding-bottom:3rem;max-width:1550px}
[data-testid="stSidebar"] {background:#eaf0e9;border-right:1px solid #d7e2d7}
h1,h2,h3 {color:#16352f;letter-spacing:-.035em}
h1 {font-size:3.2rem!important;font-weight:700!important}
[data-testid="stSidebar"] h1 {font-size:1.75rem!important;line-height:1.2!important}
[data-testid="stMetric"] {background:#fff;border:1px solid #e0e6dd;border-radius:14px;padding:18px 22px}
[data-testid="stMetricLabel"] {color:#6b7b70;font-size:.8rem;text-transform:uppercase;letter-spacing:.07em}
[data-testid="stMetricValue"] {font-size:1.85rem;color:#16352f}
[data-testid="stPlotlyChart"] {background:white;border-radius:16px;border:1px solid #e0e6dd;padding:8px}
.eyebrow {color:#167d72;font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;margin:10px 0}
.deck {color:#617167;font-size:1.05rem;max-width:800px;line-height:1.65;margin-bottom:24px}
.note {border-left:3px solid #167d72;padding:12px 18px;background:#eaf0e9;border-radius:0 8px 8px 0;color:#395449;line-height:1.6;margin:16px 0}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>''', unsafe_allow_html=True)

@st.cache_data(show_spinner='Reading the three supplied datasets…')
def get_data():
    return load_data(ROOT / 'data/resale_flat_prices.csv')

df = get_data()
with st.sidebar:
    st.markdown('<div class="eyebrow">SC4024 / Visual analytics</div>', unsafe_allow_html=True)
    st.title('HDB Observatory')
    st.caption('Explore the trade-offs behind a resale price.')
    st.divider()
    towns = st.multiselect('Towns', sorted(df.town.unique()), placeholder='All towns')
    types = st.multiselect('Flat types', sorted(df.flat_type.unique()), placeholder='All flat types')
    dates = st.select_slider('Registration months', options=sorted(df.month.unique()),
                             value=(df.month.min(), df.month.max()))
    lease = st.slider('Remaining lease · years', 0, 100, (0,100))
    motion = st.toggle('Enable animation', value=True, help='Turn off playback and transitions for a static presentation.')
    st.caption('Empty town/type selections include all values. All views share these filters.')
    st.divider()
    st.caption('Three supplied CSVs only. No fetched market data, basemap, or forecast.')

f = df[(df.month >= dates[0]) & (df.month <= dates[1]) &
       df.remaining_lease_years.between(*lease)].copy()
if towns:
    f = f[f.town.isin(towns)]
if types:
    f = f[f.flat_type.isin(types)]

st.markdown('<div class="eyebrow">Singapore housing / 2017—2026 / supplied transactions</div>', unsafe_allow_html=True)
st.title('A home. A location. A trade-off.')
st.markdown('<div class="deck">Follow the resale market through time, compare like-for-like lease bands, and explore the relationship between price and place in two and three dimensions.</div>', unsafe_allow_html=True)
a,b,c,d=st.columns(4)
a.metric('Selected transactions',f'{len(f):,}')
b.metric('Median resale price',f'S${f.resale_price.median():,.0f}' if len(f) else '—')
c.metric('Median price / m²',f'S${f.price_per_sqm.median():,.0f}' if len(f) else '—')
d.metric('Location coverage',f'{f.has_spatial.mean():.1%}' if len(f) else '—',
         help='Share of selected transactions with supplied MRT/CBD distance features.')
st.caption(f'{dates[0]} → {dates[1]} · {f.town.nunique()} towns · {f.flat_type.nunique()} flat types · All source rows retained, including exact duplicate rows.')
if f.empty:
    st.info('No transactions match these filters. Broaden the month or lease range, or clear the town/type selections.')
    st.stop()

page=st.radio('Explore', ['Market pulse','Lease & price','Location lab','3D explorer','Time machine','Data notebook'],
              horizontal=True, label_visibility='collapsed',key='page')


def chart(fig, key=None, **kwargs):
    if not motion:
        fig.update_layout(transition_duration=0)
    return st.plotly_chart(fig, width='stretch', key=key, config={'displaylogo':False,'scrollZoom':False}, **kwargs)


def note(text):
    st.markdown(f'<div class="note">{text}</div>',unsafe_allow_html=True)


if page=='Market pulse':
    st.subheader('01 / Market pulse')
    st.write('How have transaction prices and volumes changed?')
    metric=st.radio('Price measure',['Price per m²','Total resale price'],horizontal=True)
    column='price_per_sqm' if metric=='Price per m²' else 'resale_price'
    chart(monthly_chart(f,column),key='monthly')
    st.caption('Each point is the median of individual transactions that month. Bars show transaction counts; absent months are not filled. The final month/year may be incomplete.')
    left,right=st.columns([1.3,1])
    with left:
        st.subheader('Town price distributions')
        chart(town_chart(f),key='town_distribution')
        st.caption('Dot = median. Line = middle 50% of transactions. Different sale mixes can explain differences between towns.')
    with right:
        st.subheader('What is being sold?')
        mix=f.groupby('flat_type').size().rename('transactions').reset_index().sort_values('transactions')
        fig=px.bar(mix,x='transactions',y='flat_type',orientation='h',color_discrete_sequence=[TEAL],text='transactions',labels={'transactions':'Transactions','flat_type':'Flat type'})
        fig.update_traces(texttemplate='%{text:,}',textposition='outside')
        chart(style(fig,400),key='mix')
        note('Price per m² helps compare homes of different sizes. It does not control for town, storey, lease, or flat model. The trend describes homes sold, not the appreciation of the same home.')

elif page=='Lease & price':
    st.subheader('02 / The lease–price relationship')
    st.write('Does the relationship persist when we separate flat types and towns?')
    minimum=st.slider('Minimum transactions per summary cell',5,100,30,step=5)
    heat, cells=lease_heatmap(f,minimum)
    chart(heat,key='lease_heatmap')
    st.caption(f'Colour and numbers = median S$/m². Blank cells have no sales or fewer than {minimum} transactions. Hover to inspect sample size. Lease bands are left-inclusive and right-exclusive.')
    left,right=st.columns([1.2,1])
    with left:
        comparison=st.selectbox('Compare one flat type',sorted(f.flat_type.unique()),index=0)
        q=f[f.flat_type==comparison].copy()
        q['lease_bin']=(q.remaining_lease_years//5*5).astype(int)
        summary=q.groupby(['town','lease_bin']).agg(price_per_sqm=('price_per_sqm','median'),n=('record_id','size')).reset_index()
        summary=summary[summary.n>=minimum].copy()
        summary['lease_end']=summary.lease_bin+5
        fig=px.line(summary,x='lease_bin',y='price_per_sqm',color='town',markers=True,
                    custom_data=['n','lease_end'],labels={'lease_bin':'Lease bin lower bound (years)','price_per_sqm':'Median S$/m²','town':'Town'})
        fig.update_traces(hovertemplate='%{x}–<%{customdata[1]} years<br>S$%{y:,.0f}/m²<br>n=%{customdata[0]:,}<extra>%{fullData.name}</extra>')
        fig.update_layout(showlegend=False)
        chart(style(fig,440),key='lease_lines')
        st.caption('Five-year bins, separated by town. Filter to a few towns for easier comparison. Lines connect observed eligible bins; gaps do not imply observations.')
    with right:
        st.subheader('Lease composition')
        fig=px.histogram(f,x='remaining_lease_years',nbins=30,color_discrete_sequence=[TEAL],labels={'remaining_lease_years':'Remaining lease (years)'})
        fig.update_layout(bargap=.08,yaxis_title='Transactions')
        chart(style(fig,400),key='lease_composition')
    note('These are cross-sectional associations. The data cannot establish a causal lease-depreciation rate or forecast a future selling price. Price ÷ years remaining is not measured annual depreciation.')

elif page=='Location lab':
    st.subheader('03 / Price and place')
    bld=building_summary(f)
    st.caption(f'{len(bld):,} geocoded addresses · {f.has_coordinates.sum():,} of {len(f):,} selected transactions. Unlocated transactions stay in all non-spatial views.')
    if bld.empty:
        st.info('No coordinates are available for this selection. Broaden your filters.');st.stop()
    st.write('Lasso or box-select addresses in the 2D view. The selected addresses appear in gold in 3D and in the table below.')
    l,r=st.columns(2)
    with l:
        st.markdown('**2D / Location footprint**')
        event=chart(location_2d(bld),key='location_selection',on_select='rerun',selection_mode=['points','box','lasso'])
    selected=[point['customdata'][0] for point in event.selection.points if point.get('customdata')]
    with r:
        st.markdown('**3D / Price landscape**')
        chart(spatial_3d(bld,selected=selected),key='location_3d')
    st.caption('Each mark is one address: position = supplied coordinates, colour/3D height = median S$/m², bubble size = transactions. Height is price, not building height. Longitude/latitude are angular coordinates, not a distance scale. Drag the 3D scene to rotate.')
    spatial=f[f.has_spatial].copy()
    left,right=st.columns([1.2,1])
    with left:
        st.subheader('How does MRT proximity relate to price?')
        spatial['distance_band']=pd.cut(spatial.min_mrt_dist_km,[0,.5,1,1.5,2,np.inf],right=False,
                                        labels=['<0.5','0.5–<1','1–<1.5','1.5–<2','≥2'])
        a=spatial.groupby('distance_band',observed=True).agg(median=('price_per_sqm','median'),n=('record_id','size'),
            q1=('price_per_sqm',lambda x:x.quantile(.25)),q3=('price_per_sqm',lambda x:x.quantile(.75))).reset_index()
        fig=px.bar(a,x='distance_band',y='median',color_discrete_sequence=[TEAL],custom_data=['n'],
            error_y=a.q3-a['median'],error_y_minus=a['median']-a.q1,
            labels={'distance_band':'Supplied nearest-MRT distance (km)','median':'Median S$/m²'})
        fig.update_traces(hovertemplate='%{x} km<br>S$%{y:,.0f}/m²<br>n=%{customdata[0]:,}<extra></extra>')
        chart(style(fig,350),key='mrt_bands')
        st.caption('Whiskers = middle 50%, not confidence intervals. Distance differences also reflect town, lease and flat-type mix.')
    with right:
        st.subheader('Coverage varies by town')
        a=f.groupby('town').has_spatial.agg(['mean','sum','size']).sort_values('mean')
        fig=px.bar(a.reset_index(),x='mean',y='town',orientation='h',color_discrete_sequence=['#b9d5cb'],
                   custom_data=['sum','size'],labels={'mean':'Transactions with distance features','town':''})
        fig.update_xaxes(tickformat='.0%',range=[0,1]);fig.update_traces(hovertemplate='%{y}<br>%{x:.1%}<br>%{customdata[0]:,} / %{customdata[1]:,}<extra></extra>')
        chart(style(fig,max(350,22*len(a))),key='coverage_town')
    shown=bld[bld.address.isin(selected)] if selected else bld
    st.caption(f'{len(shown):,} addresses in table'+(' · linked 2D selection' if selected else ' · select addresses above to narrow this table'))
    st.dataframe(shown[['address','town','transactions','price_per_sqm','lease','mrt','cbd']],hide_index=True,width='stretch')
    note('The supplied spatial lookup covers a subset of addresses. No location is guessed or geocoded live. These distance fields are taken as supplied; station/school inventories and reference dates cannot be independently verified from these files.')

elif page=='3D explorer':
    st.subheader('04 / A third dimension, with a purpose')
    st.write('Explore how price, remaining lease and location vary together. Use the 2D companion to check patterns hidden by perspective.')
    bld=building_summary(f)
    bld=bld[bld.mrt.notna() & bld.cbd.notna()]
    if bld.empty:
        st.info('No distance features are available for this selection.');st.stop()
    minimum=st.slider('Minimum sales per address',1,30,5)
    bld=bld[bld.transactions>=minimum]
    if bld.empty:
        st.info('No address meets this threshold. Lower the minimum sales.');st.stop()
    axes={'Remaining lease':'lease','MRT distance':'mrt','CBD distance':'cbd','Floor area':'area','Selected-school distance':'school'}
    x=axes[st.selectbox('Horizontal dimension',list(axes),index=1)]
    z=axes[st.selectbox('Depth dimension',list(axes),index=0)]
    if x==z:
        st.info('Choose distinct dimensions to explore an additional relationship.');st.stop()
    l,r=st.columns([1.4,1])
    with l:
        chart(spatial_3d(bld,x=x,y='price_per_sqm',z=z),key='tradeoff_3d')
    with r:
        fig=px.scatter(bld,x=x,y='price_per_sqm',color=z,size='transactions',size_max=25,
                       color_continuous_scale='Teal',hover_name='address',hover_data=['town','transactions'],labels=LABELS)
        chart(style(fig,560),key='tradeoff_2d')
    st.caption(f'{len(bld):,} address summaries · {bld.transactions.sum():,} underlying sales · no sampling. One bubble = address; size = sales. All medians describe the current filtered period, not one transaction or property valuation.')
    dims=['lease','area','mrt','cbd','price_per_sqm']
    fig=px.parallel_coordinates(bld,dimensions=dims,color='price_per_sqm',labels=LABELS,color_continuous_scale='Teal')
    fig.update_layout(margin=dict(l=70,r=70,t=70,b=40))
    chart(style(fig,400),key='parallel')
    st.caption('Drag along a parallel-coordinate axis to brush value ranges. This highlights lines within this chart; global filters remain in the sidebar. Raw units are labelled on every axis.')
    note('3D rotation supports exploration, while the matching 2D projection supports precise comparison. Building-level medians can conceal within-address variation; aggregate correlations are not individual effects.')

elif page=='Time machine':
    st.subheader('05 / Watch the market mix change')
    st.write('How do towns move through the lease–price space over time?')
    c1,c2=st.columns(2)
    dimension=c1.radio('Animation view',['2D · lease × price','3D · add floor area'],horizontal=True)
    minimum=c2.slider('Minimum sales per town-quarter',5,100,30,step=5)
    fig, summary=time_bubbles(f,minimum,3 if dimension.startswith('3D') else 2,motion)
    if fig is None:
        st.info('No town-quarter meets the minimum count. Lower the threshold or broaden filters.')
    else:
        if dimension.startswith('2D'):
            animated_view(fig,motion)
        else:
            chart(fig,key='time_bubbles')
        st.caption('One bubble = a town in a quarter. X = median remaining lease; Y = median individual S$/m²; Z in 3D = median floor area. Bubble area scales with transaction volume. Axis ranges and town colours stay fixed across frames. Towns below the count threshold disappear rather than being imputed.')
        note('Use Play/Pause in 2D for a presentation. In 3D, use the quarter slider and rotate the view to compare individual frames. These are different homes sold each quarter, not the same homes ageing along a path. 2026 Q4 contains October only in this file and may be incomplete.')
        st.download_button('Download town-quarter summaries',summary.to_csv(index=False),'town_quarter_summary.csv','text/csv')

else:
    st.subheader('06 / Evidence behind every mark')
    st.write('Inspect the source coverage, definitions, and underlying records.')
    audit=[]
    for name in ['resale_flat_prices.csv','hdb_coordinates.csv','hdb_spatial_features.csv']:
        path=ROOT/'data'/name
        source=pd.read_csv(path)
        audit.append({'File':name,'Rows':len(source),'Columns':len(source.columns),'SHA-256':hashlib.sha256(path.read_bytes()).hexdigest()})
    st.dataframe(pd.DataFrame(audit),hide_index=True,width='stretch')
    a,b,c=st.columns(3)
    a.metric('Source records retained',f'{len(df):,}')
    b.metric('Geocoded unique addresses',f'{df.loc[df.has_coordinates,"address"].nunique():,} / {df.address.nunique():,}')
    c.metric('Exact duplicate source rows',f'{pd.read_csv(ROOT/"data/resale_flat_prices.csv").duplicated().sum():,}')
    st.markdown('''**Data rules**
- Join on normalized block + street address, with many-to-one validation; no multiplication of sales rows.
- Compare overlapping coordinates from both lookups before combining them. Missing coordinates and distances stay missing.
- Remaining lease = years + months / 12. Price / m² is calculated per transaction, then summarized.
- Exact duplicate rows remain: without a unique transaction ID, they cannot safely be treated as duplicate sales.
- Dates are registration months supplied by the file. The extraction date is unknown; final-period totals may be incomplete.
- School distance refers only to the supplied selected-school list, not all schools or a quality rating.
- No interest rates, price forecasts, causal depreciation rates, or external map layers are added.''')
    st.markdown('**Inspect selected records**')
    query=st.text_input('Search address or town',placeholder='e.g. ANG MO KIO')
    records=f
    if query:
        records=f[f.address.str.contains(query.upper(),regex=False,na=False)|f.town.str.contains(query.upper(),regex=False,na=False)]
    cols=['record_id','month','town','flat_type','address','floor_area_sqm','remaining_lease_years','resale_price',
          'price_per_sqm','latitude','longitude','min_mrt_dist_km','cbd_dist_km']
    st.caption(f'{len(records):,} matching records · showing the first 500; download includes all matches.')
    st.dataframe(records[cols].head(500),hide_index=True,width='stretch')
    if st.button('Prepare filtered CSV'):
        st.download_button('Download all matching records',records[cols].to_csv(index=False),'hdb_selected_records.csv','text/csv')

st.divider()
st.caption('HDB OBSERVATORY / SC4024 · Descriptive visual analytics · Supplied CSVs only · Source coverage is part of the story.')
