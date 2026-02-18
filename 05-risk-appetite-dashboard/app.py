import os
import json
import csv
import io
import datetime
import streamlit as st  # type: ignore
import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

matplotlib.use("Agg")

st.set_page_config(
    page_title="Risk Appetite & Metrics Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .main { background-color: #0d1117; }
  .block-container { padding-top: 2rem; }
  .kpi-card {
    background:#161b22; border:1px solid #21262d;
    border-radius:10px; padding:20px; text-align:center;
  }
  .kpi-num  { font-size:2rem; font-weight:700; }
  .kpi-label{ font-size:.85rem; color:#8b949e; margin-top:4px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────

RAG_COLORS = {"Red":"#e74c3c","Amber":"#f1c40f","Green":"#2ecc71"}
RAG_ICONS  = {"Red":"🔴","Amber":"🟡","Green":"🟢"}
STYLE      = {"bg":"#0d1117","text":"#e6edf3","grid":"#21262d"}

HIGHER_IS_BETTER = ["BCP Tests Completed","Security Awareness Completion"]

FRAMEWORKS = {
    "Regulatory Breach Count":        "FCA SYSC 6.1 / ISO 27001 A.5.26",
    "Third-Party High Risk Vendors":  "FCA SS2/21 / ISO 27001 A.5.19",
    "Overdue Risk Reviews":           "ISO 27001 A.6.1 / FCA SYSC 4",
    "Critical Vulnerabilities Open":  "ISO 27001 A.8.8 / NIST CSF",
    "Data Subject Complaints":        "UK GDPR Art.57 / ICO",
    "AI Model Incidents":             "ISO 42001 / FCA AI Principles",
    "BCP Tests Completed":            "ISO 27001 A.5.30 / FCA SYSC 4",
    "Security Awareness Completion":  "ISO 27001 A.6.3",
    "Audit Findings Open":            "ISO 27001 A.9 / FCA SYSC",
    "Policy Exceptions Active":       "ISO 27001 A.5.1",
}

DEFAULT_METRICS = [
    {"metric":"Regulatory Breach Count",      "current":2, "appetite":1,"tolerance":3, "unit":"count","period":"Q1 2026","owner":"Chief Compliance Officer","action":"Review compliance calendar and close open items","history":[0,1,1,2]},
    {"metric":"Third-Party High Risk Vendors", "current":4, "appetite":3,"tolerance":5, "unit":"count","period":"Q1 2026","owner":"Head of TPRM","action":"Increase assessment frequency for critical suppliers","history":[2,3,3,4]},
    {"metric":"Overdue Risk Reviews",          "current":7, "appetite":5,"tolerance":8, "unit":"count","period":"Q1 2026","owner":"Chief Risk Officer","action":"Allocate additional review capacity in Q2","history":[3,4,6,7]},
    {"metric":"Critical Vulnerabilities Open", "current":12,"appetite":5,"tolerance":10,"unit":"count","period":"Q1 2026","owner":"CISO","action":"Prioritise patching sprint for critical CVEs","history":[8,9,10,12]},
    {"metric":"Data Subject Complaints",       "current":3, "appetite":2,"tolerance":5, "unit":"count","period":"Q1 2026","owner":"DPO","action":"Review complaint handling SLAs","history":[1,2,2,3]},
    {"metric":"AI Model Incidents",            "current":1, "appetite":0,"tolerance":2, "unit":"count","period":"Q1 2026","owner":"Chief Risk Officer","action":"Conduct post-incident review and update AI governance controls","history":[0,0,1,1]},
    {"metric":"BCP Tests Completed",           "current":3, "appetite":4,"tolerance":3, "unit":"count","period":"Q1 2026","owner":"COO","action":"Schedule outstanding BCP exercises before Q2 end","history":[2,3,3,3]},
    {"metric":"Security Awareness Completion", "current":82,"appetite":90,"tolerance":75,"unit":"%",    "period":"Q1 2026","owner":"CISO","action":"Issue reminder communications to outstanding staff","history":[70,75,80,82]},
    {"metric":"Audit Findings Open",           "current":6, "appetite":4,"tolerance":8, "unit":"count","period":"Q1 2026","owner":"Head of Internal Audit","action":"Agree remediation deadlines with finding owners","history":[3,4,5,6]},
    {"metric":"Policy Exceptions Active",      "current":2, "appetite":2,"tolerance":4, "unit":"count","period":"Q1 2026","owner":"Chief Compliance Officer","action":"Review and time-limit all active exceptions","history":[1,1,2,2]},
]

# ─── Core Logic ───────────────────────────────────────────────────────────────

def get_rag(metric, value, appetite, tolerance):
    if metric in HIGHER_IS_BETTER:
        if value >= appetite:    return "Green"
        elif value >= tolerance: return "Amber"
        else:                    return "Red"
    else:
        if value <= appetite:    return "Green"
        elif value <= tolerance: return "Amber"
        else:                    return "Red"

def assess_metric(m):
    rag = get_rag(m["metric"], m["current"], m["appetite"], m["tolerance"])
    hib = m["metric"] in HIGHER_IS_BETTER
    breach = (m["current"] < m["tolerance"]) if hib else (m["current"] > m["tolerance"])

    # Trend: current vs last history point
    trend_dir = None
    hist = m.get("history", [])
    if hist:
        last = hist[-1]
        if hib:
            trend_dir = "improving" if m["current"] >= last else "worsening"
        else:
            trend_dir = "improving" if m["current"] <= last else "worsening"

    return {**m, "rag": rag, "breach": breach, "trend": trend_dir}

def validate_thresholds(metric, appetite, tolerance):
    """Returns error string or None if valid."""
    hib = metric in HIGHER_IS_BETTER
    if not hib and tolerance < appetite:
        return "Tolerance must be ≥ Appetite for 'lower is better' metrics."
    if hib and appetite < tolerance:
        return "For 'higher is better' metrics, Appetite must be ≥ Tolerance."
    return None

# ─── Charts ───────────────────────────────────────────────────────────────────

def _apply_style():
    plt.rcParams.update({
        "text.color":STYLE["text"],"axes.labelcolor":STYLE["text"],
        "xtick.color":STYLE["text"],"ytick.color":STYLE["text"],
    })

def chart_rag_summary(results):
    _apply_style()
    counts = {s: sum(1 for r in results if r["rag"]==s) for s in ["Red","Amber","Green"]}
    non_zero = [(s,c,RAG_COLORS[s]) for s,c in counts.items() if c > 0]
    fig, ax = plt.subplots(figsize=(5,5), facecolor=STYLE["bg"])
    ax.set_facecolor(STYLE["bg"])
    if non_zero:
        _, texts, autotexts = ax.pie(
            [x[1] for x in non_zero], labels=[x[0] for x in non_zero],
            colors=[x[2] for x in non_zero], autopct="%1.0f%%", startangle=90,
            wedgeprops={"width":0.5,"edgecolor":STYLE["bg"],"linewidth":2},
            textprops={"color":STYLE["text"],"fontsize":11},
        )
        for at in autotexts: at.set_color(STYLE["bg"]); at.set_fontweight("bold")
    ax.set_title("RAG Status Distribution", color=STYLE["text"], fontsize=12, pad=15)
    fig.tight_layout()
    return fig

def chart_metrics_bar(results):
    _apply_style()
    names   = [r["metric"].replace(" ","\n") for r in results]
    current = [r["current"] for r in results]
    app_val = [r["appetite"] for r in results]
    tol_val = [r["tolerance"] for r in results]
    colors  = [RAG_COLORS[r["rag"]] for r in results]
    x = list(range(len(results)))

    fig, ax = plt.subplots(figsize=(14,5), facecolor=STYLE["bg"])
    ax.set_facecolor(STYLE["bg"])
    ax.bar(x, current, color=colors, alpha=0.8, width=0.5, label="Current Value")
    ax.plot(x, app_val, "o--", color="#2ecc71", linewidth=1.5,
            markersize=6, label="Appetite", alpha=0.8)
    ax.plot(x, tol_val, "s--", color="#e74c3c", linewidth=1.5,
            markersize=6, label="Tolerance", alpha=0.8)
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=7)
    ax.set_title("Metrics vs Risk Appetite & Tolerance Thresholds",
                 color=STYLE["text"], fontsize=12, pad=12)
    ax.legend(facecolor=STYLE["bg"], labelcolor=STYLE["text"], framealpha=0.5)
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(STYLE["grid"])
    ax.yaxis.grid(True, color=STYLE["grid"], linewidth=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig

def chart_trend(result):
    _apply_style()
    history = result.get("history", [])
    if len(history) < 2: return None

    # Fix: use numeric x consistently
    x      = list(range(len(history)))
    labels = [f"T-{len(history)-1-i}" for i in range(len(history)-1)] + ["Current"]

    fig, ax = plt.subplots(figsize=(6,3), facecolor=STYLE["bg"])
    ax.set_facecolor(STYLE["bg"])
    ax.plot(x, history, "o-", color=RAG_COLORS[result["rag"]], linewidth=2, markersize=8)
    ax.axhline(result["appetite"],  color="#2ecc71", linestyle="--",
               linewidth=1, alpha=0.7, label="Appetite")
    ax.axhline(result["tolerance"], color="#e74c3c", linestyle="--",
               linewidth=1, alpha=0.7, label="Tolerance")
    ax.fill_between(x, history, alpha=0.1, color=RAG_COLORS[result["rag"]])
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_title(f"Trend: {result['metric']}", color=STYLE["text"], fontsize=10, pad=10)
    ax.legend(facecolor=STYLE["bg"], labelcolor=STYLE["text"], framealpha=0.5, fontsize=8)
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(STYLE["grid"])
    ax.yaxis.grid(True, color=STYLE["grid"], linewidth=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig

# ─── Sidebar ──────────────────────────────────────────────────────────────────

def sidebar_form():
    st.sidebar.markdown("## ➕ Add / Update Metric")
    with st.sidebar.form("metric_form", clear_on_submit=True):
        metric   = st.selectbox("Metric", list(FRAMEWORKS.keys()))
        current  = st.number_input("Current Value",    min_value=0, max_value=1000, value=0)
        appetite = st.number_input("Appetite Threshold",min_value=0, max_value=1000, value=5)
        tolerance= st.number_input("Tolerance Threshold",min_value=0,max_value=1000, value=10)
        unit     = st.selectbox("Unit", ["count","%","days","£k"])
        period   = st.text_input("Reporting Period", value="Q1 2026")
        owner    = st.text_input("Metric Owner")
        action   = st.text_area("Remediation Action", height=60)
        submitted= st.form_submit_button("Add / Update Metric")

    if submitted:
        # Validate thresholds
        err = validate_thresholds(metric, appetite, tolerance)
        if err:
            st.sidebar.error(err)
            return

        existing = next((m for m in st.session_state.metrics
                         if m["metric"]==metric), None)
        if existing:
            history = list(existing.get("history", []))
            history.append(existing["current"])
            if len(history) > 6: history = history[-6:]
            st.session_state.metrics = [
                m for m in st.session_state.metrics if m["metric"]!=metric
            ]
        else:
            history = [current]

        st.session_state.metrics.append({
            "metric":metric,"current":current,"appetite":appetite,
            "tolerance":tolerance,"unit":unit,"period":period,
            "owner":owner or "—","action":action or "—",
            "history":history,
        })
        st.sidebar.success(f"✓ {metric} updated")

    # JSON upload
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📂 Upload Metrics JSON")
    uploaded = st.sidebar.file_uploader("Upload metrics.json", type=["json"])
    if uploaded:
        try:
            data = json.load(uploaded)
            st.session_state.metrics = data
            st.sidebar.success(f"✓ {len(data)} metrics loaded")
        except Exception as e:
            st.sidebar.error(f"Invalid JSON: {e}")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if "metrics" not in st.session_state:
        st.session_state.metrics = DEFAULT_METRICS

    sidebar_form()

    st.markdown("# 🎯 Risk Appetite & Metrics Dashboard")
    st.markdown(
        "<div style='color:#8b949e;font-size:.9rem;margin-bottom:24px'>"
        f"Reporting Period: {datetime.date.today().strftime('%d %B %Y')} &nbsp;·&nbsp; "
        "ISO 27001:2022 &nbsp;·&nbsp; FCA SYSC &nbsp;·&nbsp; "
        "UK GDPR &nbsp;·&nbsp; ISO 42001:2023"
        "</div>", unsafe_allow_html=True
    )

    if not st.session_state.metrics:
        st.info("No metrics loaded. Add metrics using the sidebar.")
        return

    results  = [assess_metric(m) for m in st.session_state.metrics]
    breaches = [r for r in results if r["rag"]=="Red"]
    ambers   = [r for r in results if r["rag"]=="Amber"]
    greens   = [r for r in results if r["rag"]=="Green"]

    # KPIs
    st.markdown("### Risk Appetite Overview")
    k1,k2,k3,k4,k5 = st.columns(5)
    for col, val, color, label in [
        (k1, len(results),   "#58a6ff","Total Metrics"),
        (k2, len(breaches),  "#e74c3c","🔴 Red — Breached"),
        (k3, len(ambers),    "#f1c40f","🟡 Amber — At Risk"),
        (k4, len(greens),    "#2ecc71","🟢 Green — Within Appetite"),
        (k5, sum(1 for r in results if r.get("trend")=="worsening"),"#e74c3c","📈 Worsening"),
    ]:
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-num" style="color:{color}">{val}</div>'
            f'<div class="kpi-label">{label}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Breach alerts
    if breaches:
        st.markdown("---")
        st.markdown("### 🔴 Risk Appetite Breaches — Escalation Required")
        for r in breaches:
            st.error(
                f"**{r['metric']}** — Current: {r['current']}{r['unit']}  |  "
                f"Tolerance: {r['tolerance']}{r['unit']}  |  "
                f"Owner: {r.get('owner','—')}  |  "
                f"Action: {r.get('action','—')}"
            )
    if ambers:
        st.markdown("### 🟡 Amber — Approaching Tolerance")
        for r in ambers:
            st.warning(
                f"**{r['metric']}** — Current: {r['current']}{r['unit']}  |  "
                f"Appetite: {r['appetite']}{r['unit']}  |  "
                f"Tolerance: {r['tolerance']}{r['unit']}  |  "
                f"Owner: {r.get('owner','—')}"
            )

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts","📋 Metrics Register","🔍 Metric Detail","📄 Export"])

    # Tab 1
    with tab1:
        c1, c2 = st.columns([1,2])
        with c1: st.pyplot(chart_rag_summary(results))
        with c2: st.pyplot(chart_metrics_bar(results))

    # Tab 2
    with tab2:
        st.markdown("#### Compliance Risk Appetite Metrics")
        rf = st.multiselect("Filter by RAG",["Red","Amber","Green"],
                             default=["Red","Amber","Green"])
        sorted_r = sorted(
            [r for r in results if r["rag"] in rf],
            key=lambda x: (["Red","Amber","Green"].index(x["rag"]),
                           -abs(x["current"]-x["tolerance"]))
        )
        for r in sorted_r:
            color = RAG_COLORS[r["rag"]]
            trend_str = (" 📈 Worsening" if r["trend"]=="worsening"
                         else " 📉 Improving" if r["trend"]=="improving" else "")
            with st.expander(
                f"{RAG_ICONS[r['rag']]}  {r['metric']}  |  "
                f"Current: {r['current']}{r['unit']}  |  "
                f"{r['rag']}{trend_str}"
            ):
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(f"**Current Value:** {r['current']} {r['unit']}")
                    st.markdown(f"**Appetite Threshold:** {r['appetite']} {r['unit']}")
                    st.markdown(f"**Tolerance Threshold:** {r['tolerance']} {r['unit']}")
                    st.markdown(f"**Reporting Period:** {r['period']}")
                    st.markdown(f"**Metric Owner:** {r.get('owner','—')}")
                    st.markdown(f"**Framework Ref:** `{FRAMEWORKS.get(r['metric'],'—')}`")
                with cb:
                    st.markdown(
                        f"<div style='font-size:1.4rem;color:{color}'>"
                        f"{RAG_ICONS[r['rag']]} {r['rag']}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**Remediation Action:** {r.get('action','—')}")
                    if r["breach"]:
                        st.error("⚠ Tolerance breached — escalation required")
                    if r["trend"]=="worsening":
                        st.warning("📈 Trending in wrong direction")
                    elif r["trend"]=="improving":
                        st.success("📉 Metric improving")

                fig = chart_trend(r)
                if fig: st.pyplot(fig)

    # Tab 3
    with tab3:
        names    = [r["metric"] for r in results]
        selected = st.selectbox("Select Metric", names)
        r = next(x for x in results if x["metric"]==selected)

        c1,c2,c3 = st.columns(3)
        c1.metric("Current Value", f"{r['current']} {r['unit']}")
        c2.metric("Appetite",      f"{r['appetite']} {r['unit']}")
        c3.metric("Tolerance",     f"{r['tolerance']} {r['unit']}")

        color = RAG_COLORS[r["rag"]]
        st.markdown(
            f"<div style='font-size:1.8rem;color:{color};margin:12px 0'>"
            f"{RAG_ICONS[r['rag']]} {r['rag']}</div>",
            unsafe_allow_html=True
        )
        st.markdown(f"**Metric Owner:** {r.get('owner','—')}")
        st.markdown(f"**Remediation Action:** {r.get('action','—')}")
        st.markdown(f"**Framework Ref:** `{FRAMEWORKS.get(r['metric'],'—')}`")
        st.markdown(f"**Reporting Period:** {r['period']}")

        if r["breach"]:
            st.error("Tolerance breached — immediate escalation required")
        if r["trend"]=="worsening":
            st.warning("Metric trending in wrong direction — review actions")
        elif r["trend"]=="improving":
            st.success("Metric improving — continue monitoring")

        fig = chart_trend(r)
        if fig: st.pyplot(fig)

    # Tab 4
    with tab4:
        st.markdown("#### Export Reports")
        today = datetime.date.today().strftime("%d %B %Y")

        lines = [
            "# Risk Appetite & Metrics Report",
            f"**Reporting Date:** {today}  ",
            "**Classification:** Internal — Risk Committee  ",
            "**Framework:** ISO 27001:2022 · FCA SYSC · UK GDPR · ISO 42001:2023",
            "","---","","## Executive Summary","",
            f"Total metrics tracked: **{len(results)}**","",
            "| RAG Status | Count |","|---|---|",
        ]
        for s in ["Red","Amber","Green"]:
            lines.append(f"| {RAG_ICONS[s]} {s} | {sum(1 for r in results if r['rag']==s)} |")

        if breaches:
            lines += ["","### ⚠ Appetite Breaches Requiring Escalation"]
            for r in breaches:
                lines.append(
                    f"- **{r['metric']}** — Current: {r['current']}{r['unit']} "
                    f"(Tolerance: {r['tolerance']}{r['unit']}) — "
                    f"Owner: {r.get('owner','—')} — Action: {r.get('action','—')}"
                )

        lines += ["","---","","## Full Metrics Register",""]
        for r in sorted(results, key=lambda x: ["Red","Amber","Green"].index(x["rag"])):
            lines += [
                f"### {RAG_ICONS[r['rag']]} {r['metric']}",
                f"| Field | Value |","|---|---|",
                f"| Current Value | {r['current']} {r['unit']} |",
                f"| Appetite | {r['appetite']} {r['unit']} |",
                f"| Tolerance | {r['tolerance']} {r['unit']} |",
                f"| RAG Status | {r['rag']} |",
                f"| Trend | {r.get('trend','—')} |",
                f"| Owner | {r.get('owner','—')} |",
                f"| Action | {r.get('action','—')} |",
                f"| Framework | {FRAMEWORKS.get(r['metric'],'—')} |",
                f"| Period | {r['period']} |","",
            ]
        lines.append("*Generated by Risk Appetite & Metrics Dashboard — Ajibola Yusuff*")

        st.download_button("⬇ Download Metrics Report (Markdown)",
            data="\n".join(lines),
            file_name=f"risk_appetite_report_{datetime.date.today()}.md",
            mime="text/markdown")

        csv_buf = io.StringIO()
        writer  = csv.DictWriter(csv_buf, fieldnames=[
            "metric","current","unit","appetite","tolerance",
            "rag","trend","owner","action","period","framework"
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "metric":r["metric"],"current":r["current"],"unit":r["unit"],
                "appetite":r["appetite"],"tolerance":r["tolerance"],
                "rag":r["rag"],"trend":r.get("trend","—"),
                "owner":r.get("owner","—"),"action":r.get("action","—"),
                "period":r["period"],"framework":FRAMEWORKS.get(r["metric"],"—"),
            })
        st.download_button("⬇ Download Metrics (CSV)",
            data=csv_buf.getvalue(),
            file_name=f"risk_appetite_{datetime.date.today()}.csv",
            mime="text/csv")

        st.download_button("⬇ Download Metrics (JSON)",
            data=json.dumps(st.session_state.metrics, indent=2),
            file_name=f"metrics_{datetime.date.today()}.json",
            mime="application/json")

        st.markdown("---")
        if st.button("🗑 Reset to Default Metrics"):
            st.session_state.metrics = DEFAULT_METRICS
            st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='color:#8b949e;font-size:.8rem'>"
        "Risk Appetite & Metrics Dashboard &nbsp;·&nbsp; Ajibola Yusuff &nbsp;·&nbsp; "
        "ISO 27001 | ISO 42001 | CompTIA Security+"
        "</div>", unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()