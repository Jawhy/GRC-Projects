import os
import json
import csv
import io
import datetime
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="SOC Command Terminal",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --bg:#070B0A; --surface:#0B1411; --surface2:#0E1B16;
  --text:#D9FFEF; --muted:rgba(217,255,239,.68); --faint:rgba(217,255,239,.40);
  --accent:#00FF8C; --accent2:#2EE6C5; --danger:#FF2E6E; --warn:#FFB020; --ok:#2CFFB8;
  --border:rgba(0,255,140,.14); --glow:0 0 18px rgba(0,255,140,.22);
  --shadow:0 24px 80px rgba(0,0,0,.65); --radius:16px;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'Inter',sans-serif!important;}
header{display:none!important;}
footer{display:none!important;}
#MainMenu{display:none!important;}
[data-testid="stHeader"]{display:none!important;}
[data-testid="stToolbar"]{display:none!important;}
div[data-testid="stDecoration"]{display:none!important;}
[data-testid="collapsedControl"]{display:none!important;}
[data-testid="stSidebarCollapseButton"]{display:none!important;}
button[kind="header"]{display:none!important;}
section[data-testid="stSidebar"] button[data-testid="baseButton-header"]{display:none!important;}

/* Fix text legibility against light backgrounds */
.stRadio label, .stRadio div, .stRadio p { color: var(--text) !important; }
.stSelectbox label, .stSelectbox div { color: var(--text) !important; }
.stTextInput label { color: var(--text) !important; }
.stTextArea label { color: var(--text) !important; }
.stNumberInput label { color: var(--text) !important; }
.stMultiSelect label { color: var(--text) !important; }
.stCheckbox label, .stCheckbox p { color: var(--text) !important; }
.stMarkdown p, .stMarkdown li { color: var(--text) !important; }
div[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
div[data-baseweb="select"] * { color: var(--text) !important; background-color: var(--surface) !important; }
div[data-baseweb="menu"] { background-color: var(--surface) !important; }
div[data-baseweb="menu"] li { color: var(--text) !important; }
div[data-baseweb="menu"] li:hover { background-color: rgba(0,255,140,.10) !important; }
div[role="listbox"] { background-color: var(--surface) !important; }
div[role="option"] { color: var(--text) !important; }
div[role="option"]:hover { background-color: rgba(0,255,140,.10) !important; }
.stForm { background-color: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; padding: 8px !important; }
p { color: var(--text) !important; }
span { color: var(--text) !important; }
label { color: var(--text) !important; }
section[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(0,255,140,.05),rgba(0,0,0,0) 35%),var(--bg)!important;border-right:1px solid rgba(0,255,140,.10);}
section[data-testid="stSidebar"] *{color:var(--text)!important;font-family:'Inter',sans-serif!important;}
.matrix-card{
  background:radial-gradient(1200px 400px at 10% 0%,rgba(0,255,140,.08),rgba(0,0,0,0)),
  linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,.01)),var(--surface);
  border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);padding:20px;margin-bottom:4px;
}
.matrix-card:hover{border-color:rgba(0,255,140,.28);}
.kpi-num{font-family:'JetBrains Mono',monospace!important;font-size:2rem;font-weight:600;letter-spacing:.5px;line-height:1.1;}
.kpi-label{font-family:'JetBrains Mono',monospace!important;font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.12em;margin-top:4px;}
.chip{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;font-size:.75rem;border:1px solid rgba(0,255,140,.18);background:rgba(0,255,140,.06);color:var(--text);font-family:'JetBrains Mono',monospace;}
.chip.danger{border-color:rgba(255,46,110,.35);background:rgba(255,46,110,.10);}
.chip.warn{border-color:rgba(255,176,32,.35);background:rgba(255,176,32,.10);}
.chip.ok{border-color:rgba(44,255,184,.35);background:rgba(44,255,184,.10);}
.stButton>button{
  border-radius:12px!important;
  font-family:'JetBrains Mono',monospace!important;
  border:1px solid rgba(0,255,140,.25)!important;
  background:rgba(0,255,140,.06)!important;
  color:var(--text)!important;
  outline:none!important;
  box-shadow:none!important;
  text-shadow:none!important;
}
.stButton>button:hover{
  box-shadow:0 0 12px rgba(0,255,140,.18)!important;
  border-color:rgba(0,255,140,.45)!important;
  background:rgba(0,255,140,.10)!important;
  color:var(--text)!important;
  text-shadow:none!important;
}
.stButton>button:focus{
  outline:none!important;
  box-shadow:none!important;
  border-color:rgba(0,255,140,.35)!important;
}
.stButton>button:active{
  outline:none!important;
  box-shadow:none!important;
  background:rgba(0,255,140,.15)!important;
}
.stButton>button p{
  margin:0!important;
  text-shadow:none!important;
}
[data-baseweb="input"] input,[data-baseweb="textarea"] textarea{background:rgba(255,255,255,.03)!important;border:1px solid rgba(0,255,140,.14)!important;border-radius:12px!important;color:var(--text)!important;font-family:'JetBrains Mono',monospace!important;}
[data-baseweb="select"]{background:rgba(255,255,255,.03)!important;border-radius:12px!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--border);}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;font-family:'JetBrains Mono',monospace!important;font-size:.8rem;}
.stTabs [data-baseweb="tab"][aria-selected="true"]{color:var(--accent)!important;border-bottom:2px solid var(--accent)!important;}
.streamlit-expanderHeader{background:var(--surface)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:12px!important;font-family:'JetBrains Mono',monospace!important;font-size:.85rem;}
div[data-testid="stAlert"]{background:var(--surface)!important;border-radius:12px!important;}
.stDownloadButton>button{border-radius:12px!important;font-family:'JetBrains Mono',monospace!important;border:1px solid rgba(0,255,140,.25)!important;background:rgba(0,255,140,.06)!important;color:var(--text)!important;}
.chat-user{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:12px 16px;margin:8px 0;font-family:'Inter',sans-serif;}
.chat-ai{background:var(--surface);border:1px solid rgba(0,255,140,.08);border-radius:12px;padding:12px 16px;margin:8px 0;font-family:'Inter',sans-serif;color:var(--text);}
::-webkit-scrollbar{width:6px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:rgba(0,255,140,.3);border-radius:3px;}
.matrix-overlay{
  position:fixed;inset:0;pointer-events:none;
  background:repeating-linear-gradient(
    to bottom,
    rgba(0,0,0,.03),rgba(0,0,0,.03) 1px,
    rgba(0,0,0,0) 2px,rgba(0,0,0,0) 4px
  );
  opacity:.4;z-index:9999;
}
.stMultiSelect [data-baseweb="tag"]{background:rgba(0,255,140,.12)!important;border:1px solid rgba(0,255,140,.25)!important;}
</style>
<div class="matrix-overlay"></div>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────

SEVERITY_COLORS = {"Critical":"#FF2E6E","High":"#FFB020","Medium":"#FFE566","Low":"#00FF8C"}
SEVERITY_ICONS  = {"Critical":"🔴","High":"🟠","Medium":"🟡","Low":"🟢"}
STATUS_COLORS   = {"Open":"#FF2E6E","In Progress":"#FFB020","Resolved":"#2CFFB8","Closed":"#666666"}
SLA_HOURS       = {"Critical":4,"High":24,"Medium":72,"Low":168}
STYLE = {
    "bg":"#070B0A","text":"#D9FFEF",
    "grid":(0/255, 255/255, 140/255, 0.10),  # tuple — matplotlib compatible
    "accent":"#00FF8C",
}

INCIDENT_CATEGORIES = [
    "Malware / Ransomware","Phishing / Social Engineering","Unauthorised Access",
    "Data Breach / Exfiltration","Denial of Service","Insider Threat",
    "Supply Chain Attack","Vulnerability Exploitation","Misconfiguration",
    "Physical Security","Other",
]
VULN_CATEGORIES = [
    "Operating System","Web Application","Network Device","Database",
    "Cloud Infrastructure","Third-Party Software","Identity & Access","Endpoint","Other",
]

README_CONTEXT = """
This is the Security Incident & Vulnerability Tracker — a cyber security operations tool.
It tracks security incidents and vulnerabilities, monitors SLA compliance, flags overdue items,
and generates security operations reports.
Incident SLAs: Critical=4hrs, High=24hrs, Medium=72hrs, Low=168hrs.
Frameworks: ISO 27001:2022, NIST CSF, CIS Controls, UK GDPR Art.33.
"""

PAGES = ["⚡ Command Center","🚨 Incidents","🧬 Vulnerabilities","🤖 AI Analyst","📦 Export"]

DEFAULT_INCIDENTS = [
    {"id":"INC001","title":"Ransomware detected on finance workstation","category":"Malware / Ransomware","severity":"Critical","status":"Resolved","owner":"SOC Team","logged_date":"2026-01-15","resolved_date":"2026-01-15","description":"Ransomware variant detected and isolated. EDR quarantined affected system.","actions_taken":"System isolated, EDR quarantine applied, backup restored, forensic analysis initiated.","framework_ref":"ISO 27001 A.5.26 / NIST CSF RS.RP"},
    {"id":"INC002","title":"Phishing campaign targeting finance staff","category":"Phishing / Social Engineering","severity":"High","status":"Resolved","owner":"Security Analyst","logged_date":"2026-01-20","resolved_date":"2026-01-22","description":"12 staff received phishing emails. 2 users clicked links.","actions_taken":"Credentials reset, email filter rules updated, awareness training delivered.","framework_ref":"ISO 27001 A.6.3 / A.5.26"},
    {"id":"INC003","title":"Unauthorised admin access attempt on server","category":"Unauthorised Access","severity":"High","status":"In Progress","owner":"IAM Team","logged_date":"2026-02-01","resolved_date":"","description":"Multiple failed admin login attempts from external IP. Brute force pattern identified.","actions_taken":"IP blocked, account locked, forensic log review in progress.","framework_ref":"ISO 27001 A.5.15 / A.8.15"},
    {"id":"INC004","title":"Sensitive data found on unencrypted USB drive","category":"Data Breach / Exfiltration","severity":"Medium","status":"Open","owner":"DPO","logged_date":"2026-02-10","resolved_date":"","description":"USB drive containing customer PII found without encryption.","actions_taken":"USB secured, data classification review initiated, ICO notification assessment underway.","framework_ref":"UK GDPR Art.33 / ISO 27001 A.8.24"},
    {"id":"INC005","title":"Cloud storage bucket misconfiguration","category":"Misconfiguration","severity":"Critical","status":"Resolved","owner":"Cloud Security","logged_date":"2026-02-12","resolved_date":"2026-02-12","description":"S3 bucket misconfigured with public read access. Contained internal project documentation.","actions_taken":"Access immediately restricted, full cloud storage audit initiated.","framework_ref":"ISO 27001 A.8.9 / NIST CSF PR.AC"},
]

DEFAULT_VULNS = [
    {"id":"VUL001","title":"Critical OpenSSL vulnerability (CVE-2024-0001)","category":"Operating System","severity":"Critical","status":"In Progress","owner":"Infrastructure Team","discovered_date":"2026-01-10","remediation_date":"2026-02-01","description":"Critical OpenSSL vulnerability allowing remote code execution on affected servers.","remediation":"Apply OpenSSL patch v3.0.8+. 14 servers identified as affected.","cvss_score":"9.8","framework_ref":"ISO 27001 A.8.8 / NIST CSF PR.IP"},
    {"id":"VUL002","title":"SQL injection in web portal login","category":"Web Application","severity":"High","status":"Open","owner":"Dev Security Team","discovered_date":"2026-01-18","remediation_date":"2026-03-01","description":"SQL injection vulnerability identified in customer portal login form during penetration test.","remediation":"Implement parameterised queries and input validation.","cvss_score":"8.1","framework_ref":"ISO 27001 A.8.25 / OWASP A03"},
    {"id":"VUL003","title":"Outdated TLS 1.0 on legacy payment gateway","category":"Network Device","severity":"High","status":"Open","owner":"Network Team","discovered_date":"2026-01-25","remediation_date":"2026-02-28","description":"Legacy payment gateway accepting TLS 1.0. PCI DSS non-compliant.","remediation":"Disable TLS 1.0/1.1, enforce TLS 1.2 minimum.","cvss_score":"7.4","framework_ref":"PCI DSS 4.2.1 / ISO 27001 A.8.24"},
    {"id":"VUL004","title":"Unpatched Windows Server — 3 critical CVEs","category":"Operating System","severity":"Critical","status":"Open","owner":"Infrastructure Team","discovered_date":"2026-02-05","remediation_date":"2026-02-20","description":"Three critical CVEs on Windows Server 2019 instances. February patches outstanding.","remediation":"Apply February 2026 Patch Tuesday updates. Schedule maintenance window.","cvss_score":"9.1","framework_ref":"ISO 27001 A.8.8 / CIS Control 7"},
    {"id":"VUL005","title":"Default credentials on network switches","category":"Network Device","severity":"Medium","status":"Resolved","owner":"Network Team","discovered_date":"2026-01-30","remediation_date":"2026-02-05","description":"Three network switches using manufacturer default credentials.","remediation":"Credentials updated, password management policy enforced.","cvss_score":"6.5","framework_ref":"ISO 27001 A.5.17 / CIS Control 5"},
]

# ─── Logic ────────────────────────────────────────────────────────────────────

def calc_sla(item):
    if item["status"] in ["Resolved","Closed"]: return "Met", None
    try:
        logged  = datetime.datetime.fromisoformat(item.get("logged_date","") + "T00:00:00")
        elapsed = (datetime.datetime.now() - logged).total_seconds() / 3600
        sla     = SLA_HOURS.get(item["severity"], 168)
        remaining = sla - elapsed
        if remaining < 0:          return "Breached", abs(remaining)
        elif remaining < sla*0.2:  return "At Risk",  remaining
        return "Within SLA", remaining
    except Exception:
        return "Unknown", None

def build_context(incidents, vulns):
    lines = ["INCIDENTS:"]
    for i in incidents:
        sla, _ = calc_sla(i)
        lines.append(f"- {i['id']} [{i['severity']}] {i['title']} | {i['status']} | SLA:{sla}")
    lines += ["","VULNERABILITIES:"]
    for v in vulns:
        lines.append(f"- {v['id']} [{v['severity']}] CVSS:{v.get('cvss_score','—')} {v['title']} | {v['status']}")
    return "\n".join(lines)

# ─── Charts ───────────────────────────────────────────────────────────────────

def _s():
    plt.rcParams.update({"text.color":STYLE["text"],"axes.labelcolor":STYLE["text"],
        "xtick.color":STYLE["text"],"ytick.color":STYLE["text"],
        "figure.facecolor":STYLE["bg"],"axes.facecolor":STYLE["bg"]})

def chart_sev_donut(items, title):
    _s()
    sevs   = ["Critical","High","Medium","Low"]
    counts = [sum(1 for i in items if i["severity"]==s) for s in sevs]
    nz = [(s,c,SEVERITY_COLORS[s]) for s,c in zip(sevs,counts) if c > 0]
    if not nz: return None
    fig, ax = plt.subplots(figsize=(4,4), facecolor=STYLE["bg"])
    ax.set_facecolor(STYLE["bg"])
    _, _, ats = ax.pie([x[1] for x in nz], labels=[x[0] for x in nz],
        colors=[x[2] for x in nz], autopct="%1.0f%%", startangle=90,
        wedgeprops={"width":0.55,"edgecolor":STYLE["bg"],"linewidth":2},
        textprops={"color":STYLE["text"],"fontsize":9,"fontfamily":"monospace"})
    for at in ats: at.set_color(STYLE["bg"]); at.set_fontweight("bold")
    ax.set_title(title, color=STYLE["text"], fontsize=10, pad=12, fontfamily="monospace")
    fig.tight_layout(); return fig

def chart_status_bar(items, title):
    _s()
    stats  = ["Open","In Progress","Resolved","Closed"]
    counts = [sum(1 for i in items if i["status"]==s) for s in stats]
    x = list(range(len(stats)))
    fig, ax = plt.subplots(figsize=(5,3), facecolor=STYLE["bg"])
    ax.set_facecolor(STYLE["bg"])
    bars = ax.bar(x, counts, color=[STATUS_COLORS[s] for s in stats], alpha=0.85, width=0.5)
    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
                str(count), ha="center", va="bottom",
                color=STYLE["text"], fontsize=9, fontweight="bold", fontfamily="monospace")
    ax.set_xticks(x); ax.set_xticklabels(stats, fontsize=8, fontfamily="monospace")
    ax.set_title(title, color=STYLE["text"], fontsize=10, pad=10, fontfamily="monospace")
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(STYLE["grid"])
    ax.yaxis.grid(True, color=STYLE["grid"], linewidth=0.5); ax.set_axisbelow(True)
    fig.tight_layout(); return fig

def chart_timeline(items, title):
    _s()
    by_date = {}
    for i in items:
        d = i.get("logged_date","") or i.get("discovered_date","")
        if d: by_date[d] = by_date.get(d,0)+1
    if not by_date: return None
    dates  = sorted(by_date.keys())
    counts = [by_date[d] for d in dates]
    x = list(range(len(dates)))
    fig, ax = plt.subplots(figsize=(9,3), facecolor=STYLE["bg"])
    ax.set_facecolor(STYLE["bg"])
    ax.plot(x, counts, "o-", color=STYLE["accent"], linewidth=2, markersize=7)
    ax.fill_between(x, counts, alpha=0.08, color=STYLE["accent"])
    ax.set_xticks(x); ax.set_xticklabels(dates, rotation=40, fontsize=7, fontfamily="monospace")
    ax.set_title(title, color=STYLE["text"], fontsize=10, pad=10, fontfamily="monospace")
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(STYLE["grid"])
    ax.yaxis.grid(True, color=STYLE["grid"], linewidth=0.3); ax.set_axisbelow(True)
    fig.tight_layout(); return fig

def chart_cvss_dist(vulns):
    _s()
    bins = {"9-10":0,"7-8.9":0,"4-6.9":0,"0-3.9":0}
    for v in vulns:
        try:
            score = float(v.get("cvss_score",0) or 0)
            if score >= 9:   bins["9-10"]  += 1
            elif score >= 7: bins["7-8.9"] += 1
            elif score >= 4: bins["4-6.9"] += 1
            else:            bins["0-3.9"] += 1
        except Exception: pass
    colors = ["#FF2E6E","#FFB020","#FFE566","#2CFFB8"]
    x = list(range(len(bins)))
    fig, ax = plt.subplots(figsize=(4,3), facecolor=STYLE["bg"])
    ax.set_facecolor(STYLE["bg"])
    bars = ax.bar(x, list(bins.values()), color=colors, alpha=0.85, width=0.5)
    for bar, count in zip(bars, bins.values()):
        if count > 0:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
                str(count), ha="center", va="bottom",
                color=STYLE["text"], fontsize=9, fontweight="bold", fontfamily="monospace")
    ax.set_xticks(x); ax.set_xticklabels(list(bins.keys()), fontsize=8, fontfamily="monospace")
    ax.set_title("CVSS Distribution", color=STYLE["text"], fontsize=10, pad=10, fontfamily="monospace")
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(STYLE["grid"])
    ax.yaxis.grid(True, color=STYLE["grid"], linewidth=0.5); ax.set_axisbelow(True)
    fig.tight_layout(); return fig

# ─── Groq AI ──────────────────────────────────────────────────────────────────

def get_client():
    key = os.environ.get("GROQ_API_KEY","")
    try: key = key or st.secrets.get("GROQ_API_KEY","")
    except Exception: pass
    return Groq(api_key=key) if key else None

def ai_briefing(incidents, vulns):
    client = get_client()
    if not client: return "⚠ Groq API key not configured."
    ctx = build_context(incidents, vulns)
    try:
        resp = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role":"user","content":f"{README_CONTEXT}\n{ctx}\n\nWrite a concise security operations briefing (max 150 words) for a security committee. Include open critical items, SLA breaches, top vulnerabilities, and recommended priorities. Use formal cyber security language."}],
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def ai_chat(user_msg, incidents, vulns, history):
    client = get_client()
    if not client: return "⚠ Groq API key not configured."
    ctx    = build_context(incidents, vulns)
    system = (f"You are a cyber security operations analyst. {README_CONTEXT}\n{ctx}\n"
              "Help users understand incidents, vulnerabilities, SLA status, and remediation priorities. "
              "Reference ISO 27001, NIST CSF, CIS Controls, UK GDPR where relevant. Be concise and technical.")
    messages = [{"role":"system","content":system}]
    for h in history[-6:]:
        messages.append({"role":"user","content":h["user"]})
        messages.append({"role":"assistant","content":h["assistant"]})
    messages.append({"role":"user","content":user_msg})
    try:
        resp = client.chat.completions.create(model="llama3-8b-8192", messages=messages, max_tokens=400)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ─── Sidebar ──────────────────────────────────────────────────────────────────

def sidebar():
    # Logo
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=260)
    st.sidebar.markdown("""
    <div style='padding:8px 0 16px;border-bottom:1px solid rgba(0,255,140,.12);margin-bottom:16px'>
      <div style='font-size:.72rem;color:rgba(217,255,239,.5);font-family:JetBrains Mono,monospace;letter-spacing:2px'>
        OPERATOR CONSOLE · SENTINELLABS
      </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")
    st.sidebar.markdown("---")

    inc_count  = len(st.session_state.get("incidents",[]))
    vuln_count = len(st.session_state.get("vulns",[]))
    breaches   = sum(1 for i in st.session_state.get("incidents",[]) if calc_sla(i)[0]=="Breached")
    chip_class = "danger" if breaches > 0 else "ok"
    status_txt = f"SLA BREACH: {breaches}" if breaches > 0 else "ALL SLAs OK"
    st.sidebar.markdown(
        f'<span class="chip {chip_class}">{status_txt}</span>&nbsp;'
        f'<span class="chip">{inc_count} INC</span>&nbsp;'
        f'<span class="chip">{vuln_count} VULN</span>',
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### > LOG INCIDENT")
    with st.sidebar.form("inc_form", clear_on_submit=True):
        inc_id  = st.text_input("ID", value=f"INC{inc_count+1:03d}")
        title   = st.text_input("Title")
        cat     = st.selectbox("Category", INCIDENT_CATEGORIES)
        sev     = st.selectbox("Severity", ["Critical","High","Medium","Low"])
        owner   = st.text_input("Owner")
        desc    = st.text_area("Description", height=50)
        actions = st.text_area("Actions Taken", height=50)
        ref     = st.text_input("Framework Ref")
        status  = st.selectbox("Status", ["Open","In Progress","Resolved","Closed"])
        sub     = st.form_submit_button("LOG INCIDENT >")
    if sub and title:
        st.session_state.incidents.append({
            "id":inc_id,"title":title,"category":cat,"severity":sev,"status":status,
            "owner":owner,"logged_date":str(datetime.date.today()),"resolved_date":"",
            "description":desc,"actions_taken":actions,"framework_ref":ref,
        })
        st.sidebar.success(f"✓ {inc_id} logged")

    st.sidebar.markdown("### > LOG VULNERABILITY")
    with st.sidebar.form("vuln_form", clear_on_submit=True):
        v_id   = st.text_input("ID", value=f"VUL{vuln_count+1:03d}")
        v_title= st.text_input("Title")
        v_cat  = st.selectbox("Category", VULN_CATEGORIES)
        v_sev  = st.selectbox("Severity", ["Critical","High","Medium","Low"])
        v_cvss = st.text_input("CVSS Score", value="0.0")
        v_own  = st.text_input("Owner")
        v_desc = st.text_area("Description", height=50)
        v_rem  = st.text_area("Remediation", height=50)
        v_ref  = st.text_input("Framework Ref")
        v_stat = st.selectbox("Status", ["Open","In Progress","Resolved","Closed"])
        v_sub  = st.form_submit_button("LOG VULNERABILITY >")
    if v_sub and v_title:
        st.session_state.vulns.append({
            "id":v_id,"title":v_title,"category":v_cat,"severity":v_sev,"status":v_stat,
            "owner":v_own,"cvss_score":v_cvss,"discovered_date":str(datetime.date.today()),
            "remediation_date":"","description":v_desc,"remediation":v_rem,"framework_ref":v_ref,
        })
        st.sidebar.success(f"✓ {v_id} logged")

    return page

# ─── Top Bar ──────────────────────────────────────────────────────────────────

def topbar(incidents, vulns):
    breaches  = sum(1 for i in incidents if calc_sla(i)[0]=="Breached")
    at_risk   = sum(1 for i in incidents if calc_sla(i)[0]=="At Risk")
    crit_open = sum(1 for i in incidents if i["severity"]=="Critical" and i["status"] not in ["Resolved","Closed"])
    risk_chip = "danger" if breaches > 0 or crit_open > 0 else ("warn" if at_risk > 0 else "ok")
    risk_txt  = "RISK: CRITICAL" if breaches > 0 else ("RISK: HIGH" if at_risk > 0 else "RISK: MANAGED")

    c1, c2, c3 = st.columns([0.25, 0.50, 0.25])
    with c1:
        st.markdown(
            '<div class="matrix-card" style="padding:12px 16px">'
            '<span style="font-family:JetBrains Mono,monospace;font-size:.9rem;color:#00FF8C;letter-spacing:3px">'
            '> SENTINELLABS · SOC TERMINAL_</span></div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f'<div class="matrix-card" style="padding:10px 16px;text-align:center">'
            f'<span class="chip ok">INGEST OK</span> '
            f'<span class="chip">LOGS 99.9%</span> '
            f'<span class="chip warn">SLA AT RISK: {at_risk}</span> '
            f'<span class="chip danger">BREACHED: {breaches}</span> '
            f'<span class="chip {risk_chip}">{risk_txt}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f'<div class="matrix-card" style="padding:12px 16px;text-align:right">'
            f'<span style="font-family:JetBrains Mono,monospace;font-size:.75rem;color:rgba(217,255,239,.5)">'
            f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></div>',
            unsafe_allow_html=True
        )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ─── Pages ────────────────────────────────────────────────────────────────────

def page_command(incidents, vulns):
    st.markdown("### ⚡ COMMAND CENTER")
    open_inc  = [i for i in incidents if i["status"] not in ["Resolved","Closed"]]
    open_vuln = [v for v in vulns     if v["status"] not in ["Resolved","Closed"]]
    crit_inc  = [i for i in incidents if i["severity"]=="Critical" and i["status"] not in ["Resolved","Closed"]]
    crit_vuln = [v for v in vulns     if v["severity"]=="Critical" and v["status"] not in ["Resolved","Closed"]]
    breaches  = [i for i in incidents if calc_sla(i)[0]=="Breached"]

    k1,k2,k3,k4,k5 = st.columns(5)
    for col, val, color, label in [
        (k1, len(incidents),  "#00FF8C","TOTAL INCIDENTS"),
        (k2, len(open_inc),   "#FFB020","OPEN INCIDENTS"),
        (k3, len(crit_inc),   "#FF2E6E","CRITICAL OPEN"),
        (k4, len(crit_vuln),  "#FF2E6E","CRITICAL VULNS"),
        (k5, len(breaches),   "#FF2E6E","SLA BREACHES"),
    ]:
        col.markdown(
            f'<div class="matrix-card"><div class="kpi-num" style="color:{color}">{val}</div>'
            f'<div class="kpi-label">{label}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if breaches:
        st.markdown("#### 🔴 SLA BREACHES — IMMEDIATE ACTION REQUIRED")
        for i in breaches:
            _, hrs = calc_sla(i)
            st.error(f"**{i['id']}** — {i['title']} | {i['severity']} | Owner: {i['owner']} | Breached by: **{int(hrs or 0)}h**")

    left, right = st.columns([0.65, 0.35])
    with left:
        fig = chart_timeline(incidents, "Incident Timeline")
        if fig:
            st.markdown('<div class="matrix-card" style="padding:12px">', unsafe_allow_html=True)
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)
    with right:
        fig = chart_sev_donut(incidents, "Incident Severity")
        if fig: st.pyplot(fig)
        fig = chart_cvss_dist(vulns)
        if fig: st.pyplot(fig)

    c1, c2 = st.columns(2)
    with c1:
        fig = chart_status_bar(incidents, "Incident Status")
        if fig: st.pyplot(fig)
    with c2:
        fig = chart_status_bar(vulns, "Vulnerability Status")
        if fig: st.pyplot(fig)

def page_incidents(incidents):
    st.markdown("### 🚨 INCIDENT REGISTER")
    breaches = [i for i in incidents if calc_sla(i)[0]=="Breached"]
    at_risk  = [i for i in incidents if calc_sla(i)[0]=="At Risk"]
    healthy  = [i for i in incidents if calc_sla(i)[0] in ["Within SLA","Met"]]
    st.markdown(
        f'<div class="matrix-card" style="padding:12px 16px;margin-bottom:16px">'
        f'<span class="chip danger">BREACHED: {len(breaches)}</span> &nbsp;'
        f'<span class="chip warn">AT RISK: {len(at_risk)}</span> &nbsp;'
        f'<span class="chip ok">HEALTHY: {len(healthy)}</span> &nbsp;'
        f'<span style="color:rgba(217,255,239,.4);font-size:.75rem;font-family:JetBrains Mono,monospace">'
        f'SLA POLICY: P1=4h · P2=24h · P3=72h · P4=168h</span>'
        f'</div>', unsafe_allow_html=True
    )

    cf1,cf2,cf3 = st.columns(3)
    sf  = cf1.multiselect("Severity",["Critical","High","Medium","Low"],default=["Critical","High","Medium","Low"],key="isev")
    stf = cf2.multiselect("Status",["Open","In Progress","Resolved","Closed"],default=["Open","In Progress","Resolved","Closed"],key="ista")
    show_breached = cf3.checkbox("Show SLA Breached Only", value=False)

    filtered = [i for i in incidents if i["severity"] in sf and i["status"] in stf]
    if show_breached: filtered = [i for i in filtered if calc_sla(i)[0]=="Breached"]
    filtered = sorted(filtered, key=lambda x:(
        ["Critical","High","Medium","Low"].index(x["severity"]),
        ["Open","In Progress","Resolved","Closed"].index(x["status"])
    ))

    list_col, drawer_col = st.columns([0.60, 0.40])
    with list_col:
        for i in filtered:
            if st.button(
                f"{SEVERITY_ICONS[i['severity']]} {i['id']} — {i['title'][:40]}{'...' if len(i['title'])>40 else ''}",
                key=f"inc_btn_{i['id']}", use_container_width=True,
            ):
                st.session_state.selected_incident = i["id"]
                st.rerun()

    with drawer_col:
        sel = st.session_state.get("selected_incident")
        if sel:
            record = next((i for i in incidents if i["id"]==sel), None)
            if record:
                sla_s, sla_h = calc_sla(record)
                col = SEVERITY_COLORS.get(record["severity"],"#00FF8C")
                sla_chip = "danger" if sla_s=="Breached" else ("warn" if sla_s=="At Risk" else "ok")
                st.markdown(
                    f'<div class="matrix-card">'
                    f'<div style="font-family:JetBrains Mono,monospace;font-size:.7rem;color:rgba(217,255,239,.4);margin-bottom:8px">INCIDENT DOSSIER</div>'
                    f'<div style="font-size:1rem;font-weight:600;margin-bottom:12px">{record["title"]}</div>'
                    f'<span class="chip" style="border-color:{col};color:{col}">{record["severity"]}</span> &nbsp;'
                    f'<span class="chip">{record["status"]}</span> &nbsp;'
                    f'<span class="chip {sla_chip}">{sla_s}</span>'
                    f'</div>', unsafe_allow_html=True
                )
                st.markdown(f"**ID:** `{record['id']}`  |  **Category:** {record['category']}")
                st.markdown(f"**Owner:** {record['owner']}  |  **Logged:** {record['logged_date']}")
                st.markdown(f"**Framework:** `{record.get('framework_ref','—')}`")
                st.markdown(f"**SLA Threshold:** {SLA_HOURS.get(record['severity'],'—')}h")
                if sla_s=="Breached":   st.error(f"SLA BREACHED by {int(sla_h or 0)}h")
                elif sla_s=="At Risk":  st.warning(f"SLA AT RISK — {int(sla_h or 0)}h remaining")
                st.markdown("---")
                st.markdown(f"**Description:**  \n{record.get('description','—')}")
                st.markdown(f"**Actions Taken:**  \n{record.get('actions_taken','—')}")
        else:
            st.markdown(
                '<div class="matrix-card" style="text-align:center;padding:40px;color:rgba(217,255,239,.3)">'
                '<div style="font-family:JetBrains Mono,monospace;font-size:.85rem">'
                '> SELECT AN INCIDENT TO VIEW DOSSIER_</div></div>',
                unsafe_allow_html=True
            )

def page_vulns(vulns):
    st.markdown("### 🧬 VULNERABILITY REGISTER")
    cf1,cf2 = st.columns(2)
    sf  = cf1.multiselect("Severity",["Critical","High","Medium","Low"],default=["Critical","High","Medium","Low"],key="vsev")
    stf = cf2.multiselect("Status",["Open","In Progress","Resolved","Closed"],default=["Open","In Progress","Resolved","Closed"],key="vsta")

    filtered = sorted(
        [v for v in vulns if v["severity"] in sf and v["status"] in stf],
        key=lambda x: float(x.get("cvss_score",0) or 0), reverse=True
    )

    list_col, drawer_col = st.columns([0.60, 0.40])
    with list_col:
        for v in filtered:
            cvss = v.get("cvss_score","—")
            if st.button(
                f"{SEVERITY_ICONS[v['severity']]} {v['id']} — CVSS:{cvss} — {v['title'][:35]}{'...' if len(v['title'])>35 else ''}",
                key=f"vuln_btn_{v['id']}", use_container_width=True,
            ):
                st.session_state.selected_vuln = v["id"]
                st.rerun()

    with drawer_col:
        sel = st.session_state.get("selected_vuln")
        if sel:
            record = next((v for v in vulns if v["id"]==sel), None)
            if record:
                col  = SEVERITY_COLORS.get(record["severity"],"#00FF8C")
                cvss = record.get("cvss_score","—")
                st.markdown(
                    f'<div class="matrix-card">'
                    f'<div style="font-family:JetBrains Mono,monospace;font-size:.7rem;color:rgba(217,255,239,.4);margin-bottom:8px">VULNERABILITY DOSSIER</div>'
                    f'<div style="font-size:1rem;font-weight:600;margin-bottom:12px">{record["title"]}</div>'
                    f'<span class="chip" style="border-color:{col};color:{col}">CVSS {cvss}</span> &nbsp;'
                    f'<span class="chip">{record["severity"]}</span> &nbsp;'
                    f'<span class="chip">{record["status"]}</span>'
                    f'</div>', unsafe_allow_html=True
                )
                st.markdown(f"**ID:** `{record['id']}`  |  **Category:** {record['category']}")
                st.markdown(f"**Owner:** {record['owner']}  |  **Discovered:** {record.get('discovered_date','—')}")
                st.markdown(f"**Target Remediation:** {record.get('remediation_date','—') or '—'}")
                st.markdown(f"**Framework:** `{record.get('framework_ref','—')}`")
                if record["status"] in ["Open","In Progress"] and record["severity"] in ["Critical","High"]:
                    st.error("⚠ IMMEDIATE REMEDIATION REQUIRED")
                st.markdown("---")
                st.markdown(f"**Description:**  \n{record.get('description','—')}")
                st.markdown(f"**Remediation:**  \n{record.get('remediation','—')}")
        else:
            st.markdown(
                '<div class="matrix-card" style="text-align:center;padding:40px;color:rgba(217,255,239,.3)">'
                '<div style="font-family:JetBrains Mono,monospace;font-size:.85rem">'
                '> SELECT A VULNERABILITY TO VIEW DOSSIER_</div></div>',
                unsafe_allow_html=True
            )

def page_ai(incidents, vulns):
    st.markdown("### 🤖 AI SECURITY ANALYST")
    st.markdown(
        '<div style="color:rgba(217,255,239,.5);font-size:.85rem;margin-bottom:16px;font-family:JetBrains Mono,monospace">'
        '> POWERED BY GROQ / LLAMA 3 — FULL INCIDENT & VULNERABILITY CONTEXT LOADED_</div>',
        unsafe_allow_html=True
    )
    brief_col, chat_col = st.columns([0.45, 0.55])

    with brief_col:
        st.markdown("#### SECURITY BRIEFING GENERATOR")
        st.radio("Briefing Mode", ["Operational (SOC)","Committee (Board)"], horizontal=True)
        if st.button("⚡ GENERATE BRIEFING", use_container_width=True):
            with st.spinner("Analysing security posture..."):
                briefing = ai_briefing(incidents, vulns)
            st.session_state.sec_briefing = briefing
        if "sec_briefing" in st.session_state:
            st.markdown(
                f'<div class="matrix-card" style="font-family:Inter,sans-serif;color:#D9FFEF;line-height:1.7">'
                f'{st.session_state.sec_briefing}</div>',
                unsafe_allow_html=True
            )
            st.download_button("⬇ EXPORT BRIEFING",
                data=st.session_state.sec_briefing,
                file_name=f"security_briefing_{datetime.date.today()}.txt",
                mime="text/plain", use_container_width=True)

    with chat_col:
        st.markdown("#### CHAT ANALYST")
        for msg in st.session_state.chat_history:
            st.markdown(f'<div class="chat-user"><span style="color:rgba(217,255,239,.5);font-size:.72rem;font-family:JetBrains Mono,monospace">USER ></span><br>{msg["user"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-ai"><span style="color:#00FF8C;font-size:.72rem;font-family:JetBrains Mono,monospace">AI ANALYST ></span><br>{msg["assistant"]}</div>', unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("INPUT >",
                placeholder="e.g. Which SLAs are breached? What are the top CVSS vulnerabilities?",
                label_visibility="collapsed")
            send = st.form_submit_button("SEND >", use_container_width=True)

        if send and user_input:
            with st.spinner("Processing..."):
                response = ai_chat(user_input, incidents, vulns, st.session_state.chat_history)
            st.session_state.chat_history.append({"user":user_input,"assistant":response})
            st.rerun()

        if st.session_state.chat_history:
            if st.button("CLEAR CHAT", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

def page_export(incidents, vulns):
    st.markdown("### 📦 EXPORT / REPORTS")
    today     = datetime.date.today().strftime("%d %B %Y")
    open_inc  = [i for i in incidents if i["status"] not in ["Resolved","Closed"]]
    open_vuln = [v for v in vulns     if v["status"] not in ["Resolved","Closed"]]
    breaches  = [i for i in incidents if calc_sla(i)[0]=="Breached"]

    lines = [
        "# Security Incident & Vulnerability Report",
        f"**Report Date:** {today}  ",
        "**Classification:** Internal — Security Committee  ",
        "**Framework:** ISO 27001:2022 · NIST CSF · CIS Controls · UK GDPR Art.33",
        "","---","","## Executive Summary","",
        f"- Total Incidents: **{len(incidents)}** | Open: **{len(open_inc)}**",
        f"- Total Vulnerabilities: **{len(vulns)}** | Open: **{len(open_vuln)}**",
        f"- SLA Breaches: **{len(breaches)}**","",
    ]
    if breaches:
        lines += ["### SLA Breaches"]
        for i in breaches:
            lines.append(f"- **{i['id']}** — {i['title']} ({i['severity']})")
    if "sec_briefing" in st.session_state:
        lines += ["","---","","## AI Security Briefing","", st.session_state.sec_briefing]
    lines += ["","---","","## Incident Register",""]
    for i in sorted(incidents, key=lambda x: ["Critical","High","Medium","Low"].index(x["severity"])):
        sla_s, _ = calc_sla(i)
        lines += [
            f"### {SEVERITY_ICONS[i['severity']]} {i['id']} — {i['title']}",
            "| Field | Value |","|---|---|",
            f"| Severity | {i['severity']} |",f"| Status | {i['status']} |",
            f"| Owner | {i['owner']} |",f"| Logged | {i['logged_date']} |",
            f"| SLA | {sla_s} |",f"| Framework | {i.get('framework_ref','—')} |",
            f"| Actions | {i.get('actions_taken','—')} |","",
        ]
    lines += ["---","","## Vulnerability Register",""]
    for v in sorted(vulns, key=lambda x: float(x.get("cvss_score",0) or 0), reverse=True):
        lines += [
            f"### {SEVERITY_ICONS[v['severity']]} {v['id']} — {v['title']}",
            "| Field | Value |","|---|---|",
            f"| CVSS | {v.get('cvss_score','—')} |",f"| Severity | {v['severity']} |",
            f"| Status | {v['status']} |",f"| Owner | {v['owner']} |",
            f"| Framework | {v.get('framework_ref','—')} |",
            f"| Remediation | {v.get('remediation','—')} |","",
        ]
    lines.append("*Generated by Security Incident & Vulnerability Tracker — Ajibola Yusuff · SentinelLabs*")

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇ DOWNLOAD SECURITY REPORT (MARKDOWN)",
            data="\n".join(lines),
            file_name=f"security_report_{datetime.date.today()}.md",
            mime="text/markdown", use_container_width=True)
    with c2:
        csv_buf = io.StringIO()
        writer  = csv.DictWriter(csv_buf, fieldnames=["id","title","type","severity","status","owner","date","cvss","framework_ref"])
        writer.writeheader()
        for i in incidents:
            writer.writerow({"id":i["id"],"title":i["title"],"type":"Incident","severity":i["severity"],
                "status":i["status"],"owner":i["owner"],"date":i["logged_date"],"cvss":"—","framework_ref":i.get("framework_ref","—")})
        for v in vulns:
            writer.writerow({"id":v["id"],"title":v["title"],"type":"Vulnerability","severity":v["severity"],
                "status":v["status"],"owner":v["owner"],"date":v.get("discovered_date","—"),
                "cvss":v.get("cvss_score","—"),"framework_ref":v.get("framework_ref","—")})
        st.download_button("⬇ DOWNLOAD COMBINED REGISTER (CSV)",
            data=csv_buf.getvalue(),
            file_name=f"security_register_{datetime.date.today()}.csv",
            mime="text/csv", use_container_width=True)

    st.markdown("---")
    if st.button("RESET TO DEFAULT DATA", use_container_width=True):
        st.session_state.incidents    = DEFAULT_INCIDENTS
        st.session_state.vulns        = DEFAULT_VULNS
        st.session_state.chat_history = []
        st.rerun()

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if "incidents"          not in st.session_state: st.session_state.incidents          = DEFAULT_INCIDENTS
    if "vulns"              not in st.session_state: st.session_state.vulns              = DEFAULT_VULNS
    if "chat_history"       not in st.session_state: st.session_state.chat_history       = []
    if "selected_incident"  not in st.session_state: st.session_state.selected_incident  = None
    if "selected_vuln"      not in st.session_state: st.session_state.selected_vuln      = None

    page = sidebar()
    topbar(st.session_state.incidents, st.session_state.vulns)

    incidents = st.session_state.incidents
    vulns     = st.session_state.vulns

    if   "Command Center"  in page: page_command(incidents, vulns)
    elif "Incidents"       in page: page_incidents(incidents)
    elif "Vulnerabilities" in page: page_vulns(vulns)
    elif "AI Analyst"      in page: page_ai(incidents, vulns)
    elif "Export"          in page: page_export(incidents, vulns)

    st.markdown(
        '<div style="color:rgba(217,255,239,.2);font-size:.72rem;margin-top:32px;'
        'border-top:1px solid rgba(0,255,140,.08);padding-top:12px;font-family:JetBrains Mono,monospace">'
        '> SENTINELLABS · SECURITY INCIDENT & VULNERABILITY TRACKER · AJIBOLA YUSUFF · '
        'ISO 27001 | ISO 42001 | COMPTIA SECURITY+ | SC-900 · ALL SYSTEMS NOMINAL_'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()