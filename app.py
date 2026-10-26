import streamlit as st
from pathlib import Path
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import pdf_extractor
import nlp_analyser
import csv_reporter


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

OUTPUT_FOLDER = Path("output")
OUTPUT_FOLDER.mkdir(exist_ok=True)

st.set_page_config(
    page_title="ConcallIQ",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>

    .main {
        background-color: #f8fafc;
    }

    div[data-testid="metric-container"]{
        border-radius:12px;
        padding:15px;
        background-color:#f1f5f9;
        border:1px solid #cbd5e1;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }

    .concalliq-header {
        padding: 18px 22px;
        border-radius:14px;
        background: linear-gradient(90deg,#0f172a,#1e293b);
        color:#f8fafc;
        margin-bottom: 18px;
    }

    .concalliq-header h1 {
        margin:0;
        font-size:26px;
    }

    .concalliq-header p {
        margin:4px 0 0 0;
        color:#cbd5e1;
        font-size:14px;
    }

    .section-block {
        background-color:#ffffff;
        border:1px solid #e2e8f0;
        border-radius:12px;
        padding:18px 20px;
        margin-bottom:18px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------

if "analyses" not in st.session_state:
    st.session_state.analyses = None

if "company" not in st.session_state:
    st.session_state.company = ""

if "excel_path" not in st.session_state:
    st.session_state.excel_path = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("📊 ConcallIQ")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Quarter Analysis",
        "Risks",
        "Business Changes",
        "Downloads"
    ]
)

st.sidebar.markdown("---")

company_input = st.sidebar.text_input(
    "Enter Company Name",
    value=st.session_state.company
)

analyze_clicked = st.sidebar.button("Analyze Company")


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def generate_ai_summary(analyses):

    triggers = []
    risks = []
    changes = []

    for q in analyses:
        triggers.extend(q.get("earnings_triggers", []))
        risks.extend(q.get("risks_and_issues", []))
        changes.extend(q.get("business_changes", []))

    return f"""
### Executive Summary

✅ Total Quarters Analysed: {len(analyses)}

📈 Growth Drivers Identified: {len(triggers)}

🏢 Business Changes Identified: {len(changes)}

⚠ Risks Identified: {len(risks)}
"""


def build_insight_df(analyses):

    rows = []

    for q in analyses:
        rows.append({
            "Quarter": q["quarter"],
            "Tone": q["management_tone"]["overall"],
            "Tone Score": q["management_tone"]["score"],
            "Triggers": len(q.get("earnings_triggers", [])),
            "Risks": len(q.get("risks_and_issues", [])),
            "Commitments": len(q.get("commitments_made", []))
        })

    return pd.DataFrame(rows)


def build_risks_df(analyses):

    rows = []

    for q in analyses:
        for r in q.get("risks_and_issues", []):
            rows.append({
                "Quarter": q["quarter"],
                "Risk": r.get("risk", "")
            })

    return pd.DataFrame(rows)


def build_changes_df(analyses):

    rows = []

    for q in analyses:

        for c in q.get(
            "business_changes",
            []
        ):

            rows.append({
                "Quarter": q["quarter"],
                "Change": str(c)
            })

    return pd.DataFrame(rows)


# --------------------------------------------------
# ANALYSIS TRIGGER
# --------------------------------------------------

if analyze_clicked:

    if not company_input.strip():
        st.error("Please enter a company name before analyzing.")
    else:
        try:
            with st.spinner("Analyzing company..."):

                transcripts = pdf_extractor.load_company_pdfs(company_input)

                result = nlp_analyser.run_full_analysis(
                    transcripts=transcripts,
                    company_name=company_input
                )

                analyses = result["quarterly_analyses"]

                if not analyses:
                    st.error("No quarterly analyses were returned for this company.")
                else:
                    excel_path = OUTPUT_FOLDER / f"{company_input.upper()}_report.xlsx"

                    csv_reporter.generate_excel_report(
                        analyses,
                        company_input,
                        excel_path
                    )

                    st.session_state.analyses = analyses
                    st.session_state.company = company_input
                    st.session_state.excel_path = excel_path

                    st.success(f"{len(analyses)} quarters analysed for {company_input.upper()}")

        except Exception as e:
            st.error(f"Something went wrong during analysis: {e}")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

header_company = st.session_state.company.upper() if st.session_state.company else "No Company Selected"

st.markdown(
    f"""
    <div class="concalliq-header">
        <h1>📈 ConcallIQ — {header_company}</h1>
        <p>AI Powered Earnings Call Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)

analyses = st.session_state.analyses

if analyses is None:
    st.info("Enter a company name in the sidebar and click **Analyze Company** to get started.")
    st.stop()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    try:

        positive_count = sum(
            1 for q in analyses
            if q["management_tone"]["overall"] == "Positive"
        )

        risk_count = sum(len(q.get("risks_and_issues", [])) for q in analyses)
        commitment_count = sum(len(q.get("commitments_made", [])) for q in analyses)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Quarters", len(analyses))
        col2.metric("Positive Tone", positive_count)
        col3.metric("Risks", risk_count)
        col4.metric("Commitments", commitment_count)

        st.markdown("<div class='section-block'>", unsafe_allow_html=True)
        st.subheader("AI Executive Summary")
        st.info(generate_ai_summary(analyses))
        st.markdown("</div>", unsafe_allow_html=True)

        # SENTIMENT TREND
        tone_scores = [
            {"Quarter": q["quarter"], "Score": q["management_tone"]["score"]}
            for q in analyses
        ]
        df_tone = pd.DataFrame(tone_scores)

        st.subheader("📊 Sentiment Trend")
        fig = px.line(df_tone, x="Quarter", y="Score", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # TONE GAUGE
        latest_score = analyses[-1]["management_tone"]["score"]

        st.subheader("🎯 Latest Management Tone")
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=latest_score,
                title={"text": "Tone Score"},
                gauge={"axis": {"range": [-1, 1]}}
            )
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # SENTIMENT DISTRIBUTION
        sentiment_df = pd.DataFrame({
            "Sentiment": [q["management_tone"]["overall"] for q in analyses]
        })

        st.subheader("🥧 Sentiment Distribution")
        fig_sentiment = px.pie(
            sentiment_df,
            names="Sentiment",
            title="Management Sentiment Distribution"
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)

        # TOPIC FREQUENCY
        all_triggers = []
        for q in analyses:
            for item in q.get("earnings_triggers", []):
                all_triggers.append(item.get("trigger", ""))

        if all_triggers:
            trigger_df = pd.DataFrame({"Trigger": all_triggers})
            trigger_counts = (
                trigger_df["Trigger"]
                .value_counts()
                .head(10)
                .reset_index()
            )
            trigger_counts.columns = ["Trigger", "Count"]

            st.subheader("📈 Topic Frequency (Top 10)")
            fig_triggers = px.bar(
                trigger_counts,
                x="Trigger",
                y="Count",
                title="Top 10 Earnings Triggers"
            )
            st.plotly_chart(fig_triggers, use_container_width=True)

        # RISK TREND
        risk_summary = [
            {"Quarter": q["quarter"], "Risk Count": len(q.get("risks_and_issues", []))}
            for q in analyses
        ]
        risk_chart_df = pd.DataFrame(risk_summary)

        st.subheader("⚠ Risk Trend")
        fig_risk = px.bar(
            risk_chart_df,
            x="Quarter",
            y="Risk Count",
            title="Risk Trend Across Quarters"
        )
        st.plotly_chart(fig_risk, use_container_width=True)

        # QUARTER INSIGHTS TABLE
        st.subheader("📋 Quarter-wise Detailed Insights")
        insight_df = build_insight_df(analyses)
        st.dataframe(insight_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")


# --------------------------------------------------
# QUARTER ANALYSIS
# --------------------------------------------------

elif page == "Quarter Analysis":

    try:
        st.subheader("🗂 Quarter-wise Analysis")

        for q in analyses:

            with st.expander(f"📌 {q['quarter']}"):

                st.markdown("**Summary**")
                st.write(q.get("summary", "No summary available."))

                st.markdown("**Management Tone**")
                st.write(
                    f"{q['management_tone']['overall']} "
                    f"(Score: {q['management_tone']['score']})"
                )

                st.markdown("**Commitments**")
                commitments = q.get("commitments_made", [])
                if commitments:
                    for c in commitments:
                        st.write(f"- {c.get('commitment', '')}")
                else:
                    st.write("No commitments recorded.")

                st.markdown("**Deviations**")
                deviations = q.get("deviations", [])
                if deviations:
                    for d in deviations:
                        st.write(f"- {d}")
                else:
                    st.write("No deviations recorded.")

    except Exception as e:
        st.error(f"Error rendering quarter analysis: {e}")


# --------------------------------------------------
# RISKS
# --------------------------------------------------

elif page == "Risks":

    try:
        st.subheader("⚠ Risks and Issues")

        risks_df = build_risks_df(analyses)

        if risks_df.empty:
            st.info("No risks recorded across the analysed quarters.")
        else:
            st.dataframe(risks_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error rendering risks page: {e}")


# --------------------------------------------------
# BUSINESS CHANGES
# --------------------------------------------------

elif page == "Business Changes":

    try:

        st.subheader("🏢 Business Changes")

        for q in analyses:

            st.markdown(
                f"## 📅 {q['quarter']}"
            )

            st.markdown(
                "### Major & Important Changes"
            )

            changes = q.get(
                "business_changes",
                []
            )

            if not changes:

                st.info(
                    "No major business changes identified."
                )

            else:

                shown = 0

                for change in changes:

                    if isinstance(change, dict):

                        text = change.get(
                            "description",
                            ""
                        )

                    else:

                        text = str(change)

                    text = text.strip()

                    if len(text) < 40:
                        continue

                    st.markdown(
                        f"• {text}"
                    )

                    shown += 1

                    if shown >= 5:
                        break

            st.markdown("---")

    except Exception as e:

        st.error(
            f"Error rendering business changes page: {e}"
        )
# --------------------------------------------------
# DOWNLOADS
# --------------------------------------------------

elif page == "Downloads":

    try:
        st.subheader("⬇ Downloads")

        company_name = st.session_state.company.upper()

        # EXCEL
        excel_path = st.session_state.excel_path

        if excel_path and Path(excel_path).exists():
            with open(excel_path, "rb") as f:
                st.download_button(
                    label="Download Excel Report",
                    data=f.read(),
                    file_name=f"{company_name}_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("Excel report not available.")

        # CSV
        insight_df = build_insight_df(analyses)
        csv_bytes = insight_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV Summary",
            data=csv_bytes,
            file_name=f"{company_name}_summary.csv",
            mime="text/csv"
        )

        # JSON
        json_bytes = json.dumps(analyses, indent=2, default=str).encode("utf-8")

        st.download_button(
            label="Download Raw JSON",
            data=json_bytes,
            file_name=f"{company_name}_analysis.json",
            mime="application/json"
        )

    except Exception as e:
        st.error(f"Error rendering downloads page: {e}")