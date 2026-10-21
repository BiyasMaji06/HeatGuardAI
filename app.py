import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from heatwave_ai import classify_severity, get_priority, generate_advisory
from scheduler import fcfs, sjf, srtf, round_robin, priority_scheduling
from metrics import calculate_metrics, get_average_metrics, create_metrics_dataframe

st.set_page_config(page_title="HeatGuard AI | Climate Insights", page_icon="☀️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#f3f7fb;--surface:#ffffff;--surface2:#edf4f8;--line:#d8e4ec;--text:#172b3c;--muted:#607589;--teal:#007f79;--teal2:#0ba99b;--orange:#d96b28;--red:#d83e50}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif}
[data-testid="stHeader"]{background:rgba(243,247,251,.88)}
.block-container{max-width:1450px;padding-top:1.2rem;padding-bottom:2.5rem}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif!important;color:var(--text)!important;letter-spacing:-.035em}
p,label,li{color:#425b70}
[data-testid="stMetric"]{background:#fff;border:1px solid #dce7ee;padding:16px 18px;border-radius:15px;box-shadow:0 5px 18px rgba(23,57,78,.045)}
[data-testid="stMetricLabel"]{color:#61778a!important;font-size:.8rem}
[data-testid="stMetricValue"]{color:#152d40!important;font-family:'Space Grotesk',sans-serif}
.stButton>button,.stDownloadButton>button{border-radius:10px;border:1px solid #c7d9e4;background:#fff;color:#17364a;font-weight:700;min-height:40px;transition:all .15s}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#008f86;color:#007f79;background:#effbf9}
.stButton>button[kind="primary"]{background:#087f79!important;color:#ffffff!important;border-color:#087f79!important}
.stButton>button[kind="primary"]:hover{background:#056c67!important;color:#ffffff!important}
[data-testid="stDataEditor"],[data-testid="stDataFrame"]{border:1px solid #d6e3eb;border-radius:12px;overflow:hidden;background:#fff}
[data-testid="stTabs"] button{color:#607589;font-weight:700}
[data-testid="stTabs"] button[aria-selected="true"]{color:#007f79}
hr{border-color:#d8e4ec}
.hg-nav{display:flex;align-items:center;justify-content:space-between;gap:14px;background:#fff;border:1px solid #dce7ee;border-radius:14px;padding:13px 18px;margin-bottom:18px;box-shadow:0 4px 16px rgba(23,57,78,.035)}
.hg-logo{font-size:1.22rem;font-weight:700;font-family:'Space Grotesk';letter-spacing:-.04em;color:#17364a;white-space:nowrap}
.hg-logo span{color:#e35c45}
.hg-navlinks{display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.hg-navlinks a{color:#50677b!important;text-decoration:none!important;font-size:.86rem;font-weight:600;padding:8px 10px;border-radius:8px}
.hg-navlinks a:hover{background:#edf7f6;color:#007f79!important}
.hg-navcta{background:#087f79;color:white!important;text-decoration:none!important;padding:9px 14px;border-radius:9px;font-weight:700;font-size:.85rem;white-space:nowrap}
.hg-hero{border:1px solid #d4e3eb;border-radius:20px;overflow:hidden;padding:34px 32px;background:radial-gradient(ellipse at 87% 10%,rgba(255,187,126,.45),transparent 31%),linear-gradient(110deg,#fff 0%,#f4fafb 57%,#e5f3f3 100%);margin-bottom:18px}
.hg-eyebrow{font-size:.73rem;letter-spacing:.14em;color:#007f79;font-weight:700;text-transform:uppercase;margin-bottom:10px}
.hg-hero h1{font-size:clamp(2.1rem,4vw,3.45rem);line-height:1.04;margin:0 0 13px}
.hg-hero p{max-width:690px;color:#536b7f;line-height:1.65;margin-bottom:16px}
.hg-chip{display:inline-block;padding:6px 10px;border:1px solid #b8e0dc;background:#e8f8f6;color:#00746e;border-radius:99px;font-size:.75rem;font-weight:700}
.hg-section{display:flex;gap:10px;align-items:center;margin:24px 0 12px}
.hg-mark{width:4px;height:23px;border-radius:8px;background:#0ba99b}
.hg-section-title{font-family:'Space Grotesk';font-size:1.14rem;font-weight:700;color:#17364a}
.hg-sub{font-size:.82rem;color:#657b8e;margin-top:3px}
.hg-footer{border-top:1px solid #d8e4ec;margin-top:30px;padding-top:16px;color:#687e90;font-size:.78rem}
div[data-testid="stAlert"]{border-radius:12px}\n.stButton>button[kind="primary"],.stButton>button[kind="primary"] p,.stButton>button[kind="primary"] span{color:#fff!important;opacity:1!important}\n
@media(max-width:760px){.hg-hero{padding:24px 19px}.hg-nav{align-items:flex-start;flex-direction:column}.hg-navlinks{gap:2px}.hg-navlinks a{padding:6px}}
</style>
""", unsafe_allow_html=True)

DATA_PATH = Path(__file__).parent / "sample_data.csv"

def load_sample_data():
    if DATA_PATH.exists():
        raw = pd.read_csv(DATA_PATH)
        return raw[["process_id","region","temperature","arrival_time","burst_time"]].copy()
    return pd.DataFrame([
        {"process_id":"P1","region":"Mumbai","temperature":39.0,"arrival_time":0,"burst_time":5},
        {"process_id":"P2","region":"Pune","temperature":42.0,"arrival_time":0,"burst_time":3},
        {"process_id":"P3","region":"Nashik","temperature":38.0,"arrival_time":0,"burst_time":4},
        {"process_id":"P4","region":"Nagpur","temperature":44.0,"arrival_time":0,"burst_time":2},
        {"process_id":"P5","region":"Thane","temperature":36.5,"arrival_time":1,"burst_time":3},
    ])

if "process_input" not in st.session_state:
    st.session_state.process_input = load_sample_data()
if "simulation_output" not in st.session_state:
    st.session_state.simulation_output = None

st.markdown("""
<div class="hg-nav">
 <div class="hg-logo">☀ HeatGuard <span>AI</span></div>
 <div class="hg-navlinks">
  <a href="#home">Home</a><a href="#simulator">Simulator</a><a href="#insights">Insights</a>
 </div>
 <a class="hg-navcta" href="#simulator">Explore your region ↗</a>
</div>
<div id="home" class="hg-hero">
 <div class="hg-eyebrow">Climate intelligence for everyday decisions</div>
 <h1>Understand the heat.<br><span style="color:#087f79">Prepare with confidence.</span></h1>
 <p>Explore regional temperatures, compare response strategies, and turn incoming heat alerts into a clear, prioritized view of conditions across your area.</p>
 <span class="hg-chip">REGIONAL HEAT RISK INSIGHTS</span>
</div>
""", unsafe_allow_html=True)

def section(title, subtitle=""):
    st.markdown(f'<div class="hg-section"><div class="hg-mark"></div><div><div class="hg-section-title">{title}</div><div class="hg-sub">{subtitle}</div></div></div>', unsafe_allow_html=True)

section("Explore regional conditions", "Edit the locations and values below, then choose a scheduling algorithm to compare how alerts are handled.")
st.markdown('<div id="simulator"></div>', unsafe_allow_html=True)
edited_df = st.data_editor(
    st.session_state.process_input, key="region_editor_v2", num_rows="dynamic",
    use_container_width=True, hide_index=True,
    column_config={
        "process_id": st.column_config.TextColumn("Process ID", required=True),
        "region": st.column_config.TextColumn("Region", required=True),
        "temperature": st.column_config.NumberColumn("Temperature (°C)", min_value=-50.0, max_value=70.0, step=0.5, format="%.1f", required=True),
        "arrival_time": st.column_config.NumberColumn("Arrival time", min_value=0, step=1, required=True),
        "burst_time": st.column_config.NumberColumn("Burst time", min_value=1, step=1, required=True),
    },
)

s1,s2,s3 = st.columns([2.1,1.1,2.3])
with s1:
    algorithm = st.selectbox("Scheduling algorithm", ["FCFS", "SJF", "SRTF", "Round Robin", "Priority Scheduling"])
with s2:
    quantum = st.selectbox("Time quantum", [1,2,3,4,5,6,8,10], index=1, disabled=algorithm != "Round Robin")
with s3:
    st.markdown('<div style="padding-top:30px;color:#607589;font-size:.83rem">Lower priority number means a higher-priority alert.</div>', unsafe_allow_html=True)

b1,b2 = st.columns([1.5,1.5])
with b1: run_clicked = st.button("Analyze conditions", type="primary", use_container_width=True)
with b2: reset_clicked = st.button("Restore sample data", use_container_width=True)

if reset_clicked:
    st.session_state.process_input = load_sample_data()
    st.session_state.simulation_output = None
    if "region_editor_v2" in st.session_state:
        del st.session_state["region_editor_v2"]
    st.rerun()

def validate(df):
    cols=["process_id","region","temperature","arrival_time","burst_time"]
    if df.empty: return "Add at least one region."
    if any(c not in df.columns for c in cols): return "The table is missing a required column."
    if df[cols].isnull().any().any(): return "Please fill in every cell."
    d=df.copy()
    d["process_id"]=d.process_id.astype(str).str.strip()
    d["region"]=d.region.astype(str).str.strip()
    if (d.process_id=="").any() or (d.region=="").any(): return "Process IDs and region names cannot be blank."
    if d.process_id.duplicated().any(): return "Each Process ID must be unique."
    try:
        for col in ["temperature","arrival_time","burst_time"]: d[col]=pd.to_numeric(d[col],errors="raise")
    except Exception: return "Temperature and time values must be numeric."
    if ((d.temperature < -50)|(d.temperature > 70)).any(): return "Temperature must be between -50°C and 70°C."
    if (d.arrival_time<0).any() or (d.burst_time<=0).any(): return "Arrival time must be non-negative and burst time must be positive."
    if ((d.arrival_time%1)!=0).any() or ((d.burst_time%1)!=0).any(): return "Arrival time and burst time must be whole numbers."
    return None

if run_clicked:
    d=edited_df.copy()
    error=validate(d)
    if error:
        st.error(error)
    else:
        d["process_id"]=d.process_id.astype(str).str.strip()
        d["region"]=d.region.astype(str).str.strip()
        d["temperature"]=pd.to_numeric(d.temperature).astype(float)
        d["arrival_time"]=pd.to_numeric(d.arrival_time).astype(int)
        d["burst_time"]=pd.to_numeric(d.burst_time).astype(int)
        d["severity"]=d.temperature.apply(classify_severity)
        d["priority"]=d.severity.apply(get_priority)
        processes=d.to_dict("records")
        if algorithm=="FCFS": results,timeline=fcfs(processes)
        elif algorithm=="SJF": results,timeline=sjf(processes)
        elif algorithm=="SRTF": results,timeline=srtf(processes)
        elif algorithm=="Round Robin": results,timeline=round_robin(processes,quantum=quantum)
        else: results,timeline=priority_scheduling(processes)
        calculated=calculate_metrics(results)
        st.session_state.process_input=d[["process_id","region","temperature","arrival_time","burst_time"]].copy()
        st.session_state.simulation_output={"input_df":d,"results":calculated,"timeline":timeline,"avgs":get_average_metrics(calculated),"algorithm":algorithm,"quantum":quantum}

out=st.session_state.simulation_output
if out:
    df=out["input_df"]; results=out["results"]; timeline=out["timeline"]; av=out["avgs"]
    elevated=int(df.severity.isin(["Extreme","High"]).sum())
    end_time=max([s["end"] for s in timeline],default=0)
    section("Your heat-risk snapshot", "A summary of the currently analyzed locations.")
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Regions analyzed",len(df))
    m2.metric("Elevated risk alerts",elevated)
    m3.metric("Average waiting time",f'{av["avg_waiting_time"]:.2f}')
    m4.metric("Total elapsed time",f"{end_time} units")

    tab1,tab2,tab3=st.tabs(["Execution timeline","Risk insights","Algorithm comparison"])
    with tab1:
        section("Gantt chart","Each bar shows when a process uses the CPU. Hover over a bar for exact start and finish times.")
        if timeline:
            td = pd.DataFrame(timeline)
            fig = go.Figure()
            palette = ["#0b8f87", "#ef9650", "#5077c8", "#8a63c7", "#d95d72",
                       "#47a4b5", "#9baf3d", "#d17dba", "#64748b", "#e2b93b"]
            pids = list(dict.fromkeys(td["process_id"].astype(str).tolist()))
            colors = {pid: ("#b8c5cf" if pid == "IDLE" else palette[i % len(palette)])
                      for i, pid in enumerate(pids)}
            for _, row in td.iterrows():
                pid = str(row["process_id"])
                start = float(row["start"])
                end = float(row["end"])
                fig.add_trace(go.Bar(
                    x=[end - start], y=[pid], base=[start], orientation="h",
                    marker=dict(color=colors[pid], line=dict(width=0)),
                    name=pid, showlegend=False,
                    customdata=[[start, end, end - start]],
                    hovertemplate="<b>%{y}</b><br>Start: %{customdata[0]}<br>Finish: %{customdata[1]}<br>Duration: %{customdata[2]}<extra></extra>"
                ))
            max_time = max(float(td["end"].max()), 1)
            fig.update_yaxes(autorange="reversed", title="", categoryorder="array",
                             categoryarray=list(reversed(pids)), tickfont=dict(size=12))
            fig.update_xaxes(title="Time units", range=[0, max_time + max(0.5, max_time * 0.02)],
                             dtick=1 if max_time <= 30 else max(1, round(max_time / 15)),
                             gridcolor="#dbe5ec", zeroline=False)
            fig.update_layout(
                barmode="overlay", paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor="#ffffff",
                font=dict(color="#294358", family="DM Sans"),
                margin=dict(l=12, r=12, t=8, b=10),
                height=max(280, min(620, 42 * len(pids) + 90)),
                showlegend=False, bargap=0.32
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.caption("Idle periods, when present, are represented by the scheduler's timeline output.")
        section("Process-level results","Start, completion, waiting, turnaround, and response times.")
        st.dataframe(create_metrics_dataframe(results),use_container_width=True,hide_index=True)
        st.download_button("Download results as CSV",data=pd.DataFrame(results).to_csv(index=False).encode("utf-8"),file_name="heatguard_results.csv",mime="text/csv")
    with tab2:
        section("Regional risk distribution","Risk bands are illustrative and are calculated from the entered temperatures.")
        counts=df["severity"].value_counts().reindex(["Extreme","High","Moderate","Low"],fill_value=0).rename_axis("Severity").reset_index(name="Regions")
        left,right=st.columns([1,1.25])
        with left:
            fig=px.pie(counts,values="Regions",names="Severity",hole=.62,color="Severity",
                       color_discrete_map={"Extreme":"#d83e50","High":"#e9853d","Moderate":"#e9bd3e","Low":"#0ba99b"})
            fig.update_layout(paper_bgcolor="rgba(255,255,255,0)",font=dict(color="#294358"),margin=dict(l=5,r=5,t=5,b=5),height=320,legend=dict(orientation="h",y=-.1))
            st.plotly_chart(fig,use_container_width=True)
        with right:
            view=df[["region","temperature","severity","priority"]].copy()
            view.columns=["Region","Temperature °C","Risk level","Alert priority"]
            st.dataframe(view,use_container_width=True,hide_index=True)
        section("Suggested precautions","General reminders associated with each illustrative risk band.")
        for _,row in df.iterrows():
            color={"Extreme":"#d83e50","High":"#d96b28","Moderate":"#ad8410","Low":"#007f79"}[row.severity]
            with st.container(border=True):
                st.markdown(f'**{row.region}** · <span style="color:{color};font-weight:700">{row.severity.upper()}</span> · {row.temperature:.1f}°C',unsafe_allow_html=True)
                st.write(generate_advisory(row.severity,row.region))
    with tab3:
        section("Compare scheduling algorithms","All algorithms process the same set of incoming tasks.")
        comparisons=[]
        for name,fn in [("FCFS",fcfs),("SJF",sjf),("SRTF",srtf),("Priority Scheduling",priority_scheduling)]:
            rr,tt=fn(df.to_dict("records")); mm=get_average_metrics(calculate_metrics(rr))
            comparisons.append({"Algorithm":name,"Avg waiting":mm["avg_waiting_time"],"Avg turnaround":mm["avg_turnaround_time"],"Avg response":mm["avg_response_time"]})
        rr,tt=round_robin(df.to_dict("records"),quantum=out["quantum"]); mm=get_average_metrics(calculate_metrics(rr))
        comparisons.append({"Algorithm":"Round Robin","Avg waiting":mm["avg_waiting_time"],"Avg turnaround":mm["avg_turnaround_time"],"Avg response":mm["avg_response_time"]})
        comp=pd.DataFrame(comparisons)
        st.dataframe(comp,use_container_width=True,hide_index=True)
        fig=go.Figure()
        for col in ["Avg waiting","Avg turnaround","Avg response"]:
            fig.add_trace(go.Bar(name=col,x=comp["Algorithm"],y=comp[col]))
        fig.update_layout(barmode="group",paper_bgcolor="rgba(255,255,255,0)",plot_bgcolor="#ffffff",
                          font=dict(color="#294358"),margin=dict(l=5,r=5,t=15,b=5),height=370,
                          yaxis=dict(gridcolor="#dbe5ec",title="Time units"),xaxis_title="",
                          legend=dict(orientation="h",y=1.15))
        st.plotly_chart(fig,use_container_width=True)
else:
    section("Your heat-risk snapshot","Analyze your regional conditions to see results here.")
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Regions analyzed","—");m2.metric("Elevated risk alerts","—");m3.metric("Average waiting time","—");m4.metric("Total elapsed time","—")
    st.info("Enter or edit the regional values above and select **Analyze conditions** to generate the Gantt chart and insights.")

st.markdown("""
<div id="insights"></div>
<div class="hg-footer"><b style="color:#17364a">☀ HeatGuard <span style="color:#e35c45">AI</span></b><br>
Regional heat-risk insights for safer, more prepared communities.<br><br>
""",unsafe_allow_html=True)