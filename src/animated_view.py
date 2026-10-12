"""Self-contained playback; one awaited frame at a time, with no queued cancellation."""
import json
import streamlit as st


def animated_view(fig, motion=True):
    quarters=[frame.name for frame in fig.frames]
    # Native Plotly menu/slider animation callbacks discard interrupted promises.
    # Own both controls and schedule only one frame, so Pause cleanly ends the loop.
    fig.update_layout(updatemenus=[],sliders=[],height=590)
    chart_html=fig.to_html(full_html=False,include_plotlyjs=True,auto_play=False,div_id='hdb-time',
                           config={'displaylogo':False,'responsive':True})
    buttons='<button id="play">▶ Play</button><button id="pause">Ⅱ Pause</button>' if motion else ''
    html='''<style>
    body{margin:0;background:#fff;font:13px Arial,sans-serif;color:#16352f}
    .controls{display:flex;gap:8px;padding:14px 18px;align-items:center;flex-wrap:wrap}
    button{padding:9px 17px;border:1px solid #cbd9d0;border-radius:7px;background:#edf3ed;color:#16352f;cursor:pointer}
    button:hover{background:#dce9df}#state{color:#617167;margin-left:8px}
    .timeline{padding:5px 25px 20px}input{width:100%;accent-color:#167d72}label{display:block;margin-bottom:8px}
    </style><div class="controls">'''+buttons+'''<span id="state">Use the quarter slider to inspect a frame.</span></div>'''+chart_html
    html+='''<div class="timeline"><label id="quarter-label" for="quarter"></label><input id="quarter" type="range" min="0" step="1" value="0"></div><script>
    const graph=document.getElementById('hdb-time');
    const state=document.getElementById('state');
    const slider=document.getElementById('quarter');
    const label=document.getElementById('quarter-label');
    const quarters=QUARTERS;
    slider.max=quarters.length-1;label.textContent='Quarter · '+quarters[0];
    let index=0,token=0,playing=false;
    async function draw(i){
        await Plotly.animate(graph,[quarters[i]],{mode:'afterall',frame:{duration:DURATION,redraw:false},transition:{duration:TRANSITION}});
        index=i;slider.value=i;label.textContent='Quarter · '+quarters[i];
    }
    function showError(error){playing=false;state.textContent='Playback error: '+String(error);console.error(error);}
    slider.oninput=()=>{
        ++token;playing=false;state.textContent='Inspecting a quarter.';
        draw(Number(slider.value)).catch(showError);
    };
    PLAY_HANDLERS
    </script>'''.replace('QUARTERS',json.dumps(quarters)).replace('DURATION','650' if motion else '0').replace('TRANSITION','350' if motion else '0')
    handlers='''
    document.getElementById('play').onclick=async()=>{
        if(playing)return;
        playing=true;const run=++token;state.textContent='Playing quarterly summaries…';
        try{
            for(let i=index===quarters.length-1?0:index+1;i<quarters.length && run===token;i++)await draw(i);
            if(run===token){playing=false;state.textContent='Playback complete.';}
        }catch(error){showError(error);}
    };
    document.getElementById('pause').onclick=()=>{
        ++token;playing=false;state.textContent='Paused. Hover a town or choose a quarter.';
    };''' if motion else ''
    st.iframe(html.replace('PLAY_HANDLERS',handlers),height=760)
