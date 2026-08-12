# ==============================================================================
# dashboard/app.py
# ==============================================================================
"""
INVESTMENT SURVEY ANALYTICS DASHBOARD

Streamlit dashboard for the Investment Survey analytical pipeline.

Pipeline:

01_data_loader
02_data_audit
03_data_cleaning
04_data_transformation
05_feature_engineering
06_business_metrics
07_analysis
08_validation
09_dashboard

Dashboard Sections:

1. Executive Overview
2. Investment Preference
3. Demographic Analysis
4. Investment Behaviour
5. Investment Reasons
6. Savings Objectives
7. Information & Monitoring
8. Business Questions
9. Executive Insights
10. Recommendations
11. Data Quality & Validation

Important business rules:

- Respondent grain = one row per respondent.
- Investment grain = one row per investment preference.
- Respondent counts use unique Respondent_ID.
- Preference Rank:
      1 = Highest Preference
      7 = Lowest Preference
- Lower Average Preference Rank = stronger preference.
- Expected Return remains categorical.
"""

# ==============================================================================
# 1. IMPORTS
# ==============================================================================

from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st


# ==============================================================================
# 2. PAGE CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="Investment Survey Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==============================================================================
# 3. PROJECT PATHS
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

FEATURES_DIR = DATA_DIR / "features"
ANALYSIS_DIR = DATA_DIR / "analysis"
VALIDATION_DIR = DATA_DIR / "validation"


# ==============================================================================
# 4. GLOBAL STYLING
# ==============================================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 650;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    .info-box {
        padding: 1rem;
        border-radius: 10px;
        background: white;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==============================================================================
# 5. DATA LOADER
# ==============================================================================

@st.cache_data
def load_csv(path):

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


# ==============================================================================
# 6. LOAD CORE DATA
# ==============================================================================

respondent_df = load_csv(
    FEATURES_DIR / "respondent_features.csv"
)

investment_df = load_csv(
    FEATURES_DIR / "investment_features.csv"
)


# ==============================================================================
# 7. LOAD ANALYTICAL OUTPUTS
# ==============================================================================

investment_analysis = load_csv(
    ANALYSIS_DIR /
    "investment_preference_analysis.csv"
)

gender_analysis = load_csv(
    ANALYSIS_DIR /
    "gender_investment_analysis.csv"
)

age_analysis = load_csv(
    ANALYSIS_DIR /
    "age_investment_analysis.csv"
)

objective_analysis = load_csv(
    ANALYSIS_DIR /
    "objective_investment_analysis.csv"
)

female_analysis = load_csv(
    ANALYSIS_DIR /
    "female_investment_preference.csv"
)

young_analysis = load_csv(
    ANALYSIS_DIR /
    "young_investor_preference.csv"
)

bond_analysis = load_csv(
    ANALYSIS_DIR /
    "bond_preference_analysis.csv"
)

gender_gap = load_csv(
    ANALYSIS_DIR /
    "gender_preference_gap.csv"
)

purpose_analysis = load_csv(
    ANALYSIS_DIR /
    "purpose_investment_analysis.csv"
)

factor_analysis = load_csv(
    ANALYSIS_DIR /
    "factor_investment_analysis.csv"
)

duration_analysis = load_csv(
    ANALYSIS_DIR /
    "duration_investment_analysis.csv"
)

expected_return_analysis = load_csv(
    ANALYSIS_DIR /
    "expected_return_analysis.csv"
)

savings_analysis = load_csv(
    ANALYSIS_DIR /
    "savings_investment_analysis.csv"
)

source_analysis = load_csv(
    ANALYSIS_DIR /
    "source_investment_analysis.csv"
)

monitoring_analysis = load_csv(
    ANALYSIS_DIR /
    "monitoring_investment_analysis.csv"
)

insights_df = load_csv(
    ANALYSIS_DIR /
    "executive_analytical_insights.csv"
)

recommendations_df = load_csv(
    ANALYSIS_DIR /
    "analytical_recommendations.csv"
)

analysis_summary = load_csv(
    ANALYSIS_DIR /
    "analysis_summary.csv"
)


# ==============================================================================
# 8. VALIDATION DATA
# ==============================================================================

validation_report = load_csv(
    VALIDATION_DIR /
    "validation_report.csv"
)

validation_results = load_csv(
    VALIDATION_DIR /
    "validation_results.csv"
)

validation_errors = load_csv(
    VALIDATION_DIR /
    "validation_errors.csv"
)


# ==============================================================================
# 9. HELPER FUNCTIONS
# ==============================================================================

def find_column(df, candidates):

    if df.empty:
        return None

    normalized = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for candidate in candidates:

        key = str(candidate).strip().lower()

        if key in normalized:
            return normalized[key]

    return None


def unique_count(df, column):

    if df.empty or column is None:
        return 0

    return int(
        df[column]
        .dropna()
        .nunique()
    )


def format_number(value):

    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


def format_decimal(value):

    try:
        return f"{float(value):.2f}"
    except Exception:
        return str(value)


def show_dataframe(df, height=350):

    if df.empty:

        st.info(
            "No data available for this section."
        )

        return

    st.dataframe(
        df,
        use_container_width=True,
        height=height
    )


def get_numeric_series(df, column):

    if df.empty or column not in df.columns:
        return pd.Series(dtype="float64")

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ==============================================================================
# 10. COLUMN DETECTION
# ==============================================================================

RESPONDENT_ID = find_column(
    respondent_df,
    [
        "Respondent_ID",
        "respondent_id",
        "Response_ID",
        "response_id"
    ]
)

AGE = find_column(
    respondent_df,
    [
        "Age",
        "age"
    ]
)

GENDER = find_column(
    respondent_df,
    [
        "Gender",
        "gender"
    ]
)

OBJECTIVE = find_column(
    respondent_df,
    [
        "Investment_Objective",
        "investment_objective",
        "Objective",
        "objective"
    ]
)

PURPOSE = find_column(
    respondent_df,
    [
        "Investment_Purpose",
        "investment_purpose",
        "Purpose",
        "purpose"
    ]
)

EXPECTED_RETURN = find_column(
    respondent_df,
    [
        "Expected_Return_Range",
        "expected_return_range",
        "Expected_Return",
        "expected_return"
    ]
)

INVESTMENT_ID = find_column(
    investment_df,
    [
        "Respondent_ID",
        "respondent_id",
        "Response_ID",
        "response_id"
    ]
)

INVESTMENT_TYPE = find_column(
    investment_df,
    [
        "Investment_Type",
        "investment_type",
        "Investment Type"
    ]
)

PREFERENCE_RANK = find_column(
    investment_df,
    [
        "Preference_Rank",
        "preference_rank",
        "Preference Rank"
    ]
)


# ==============================================================================
# 11. SIDEBAR
# ==============================================================================

with st.sidebar:

    st.markdown(
        "## Investment Survey"
    )

    st.caption(
        "Analytical Intelligence Dashboard"
    )

    st.divider()

    page = st.radio(
        "Navigate",
        [
            "Executive Overview",
            "Investment Preference",
            "Demographic Analysis",
            "Investment Behaviour",
            "Investment Reasons",
            "Savings Objectives",
            "Information & Monitoring",
            "Business Questions",
            "Executive Insights",
            "Recommendations",
            "Data Quality & Validation"
        ]
    )

    st.divider()

    st.markdown(
        "### Data Grain"
    )

    st.write(
        "Respondent: 1 row / respondent"
    )

    st.write(
        "Investment: multiple rows / respondent"
    )

    st.divider()

    st.caption(
        "Investment Survey Analytics"
    )


# ==============================================================================
# 12. HEADER
# ==============================================================================

st.markdown(
    """
    <div class="dashboard-title">
        Investment Survey Analytics
    </div>

    <div class="dashboard-subtitle">
        Data-driven analysis of investor preferences,
        behaviour, demographics and decision patterns.
    </div>
    """,
    unsafe_allow_html=True
)


# ==============================================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# ==============================================================================

if page == "Executive Overview":

    st.markdown(
        '<div class="section-title">Executive Overview</div>',
        unsafe_allow_html=True
    )

    total_respondents = (
        respondent_df[RESPONDENT_ID]
        .nunique()
        if RESPONDENT_ID
        else len(respondent_df)
    )

    total_investments = len(
        investment_df
    )

    avg_age = (
        pd.to_numeric(
            respondent_df[AGE],
            errors="coerce"
        ).mean()
        if AGE
        else np.nan
    )

    female_count = 0
    male_count = 0

    if GENDER:

        gender_values = (
            respondent_df[GENDER]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        female_count = int(
            gender_values.eq("female").sum()
        )

        male_count = int(
            gender_values.eq("male").sum()
        )

    cols = st.columns(5)

    cols[0].metric(
        "Total Respondents",
        format_number(total_respondents)
    )

    cols[1].metric(
        "Investment Records",
        format_number(total_investments)
    )

    cols[2].metric(
        "Average Investor Age",
        format_decimal(avg_age)
        if not pd.isna(avg_age)
        else "N/A"
    )

    cols[3].metric(
        "Male Investors",
        format_number(male_count)
    )

    cols[4].metric(
        "Female Investors",
        format_number(female_count)
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### Investment Preference"
        )

        if not investment_analysis.empty:

            type_col = find_column(
                investment_analysis,
                [
                    "Investment_Type",
                    "investment_type"
                ]
            )

            rank_col = find_column(
                investment_analysis,
                [
                    "Average_Preference_Rank"
                ]
            )

            if type_col and rank_col:

                chart_df = (
                    investment_analysis[
                        [
                            type_col,
                            rank_col
                        ]
                    ]
                    .copy()
                    .sort_values(
                        rank_col,
                        ascending=True
                    )
                    .set_index(type_col)
                )

                st.bar_chart(
                    chart_df
                )

        else:

            st.info(
                "Investment preference analysis unavailable."
            )

    with col2:

        st.markdown(
            "### Gender Distribution"
        )

        if GENDER:

            gender_chart = (
                respondent_df[
                    GENDER
                ]
                .value_counts()
            )

            st.bar_chart(
                gender_chart
            )

    st.markdown(
        "### Overall Investment Ranking"
    )

    show_dataframe(
        investment_analysis
    )


# ==============================================================================
# PAGE 2 — INVESTMENT PREFERENCE
# ==============================================================================

elif page == "Investment Preference":

    st.markdown(
        '<div class="section-title">Investment Preference Analysis</div>',
        unsafe_allow_html=True
    )

    if not investment_analysis.empty:

        type_col = find_column(
            investment_analysis,
            [
                "Investment_Type",
                "investment_type"
            ]
        )

        avg_rank_col = find_column(
            investment_analysis,
            [
                "Average_Preference_Rank"
            ]
        )

        unique_col = find_column(
            investment_analysis,
            [
                "Unique_Respondents"
            ]
        )

        if type_col and avg_rank_col:

            sorted_df = (
                investment_analysis
                .sort_values(
                    avg_rank_col,
                    ascending=True
                )
                .reset_index(drop=True)
            )

            top_investment = (
                sorted_df.iloc[0][type_col]
            )

            bottom_investment = (
                sorted_df.iloc[-1][type_col]
            )

            cols = st.columns(3)

            cols[0].metric(
                "Most Preferred",
                str(top_investment)
            )

            cols[1].metric(
                "Least Preferred",
                str(bottom_investment)
            )

            if unique_col:

                cols[2].metric(
                    "Investor Groups",
                    format_number(
                        sorted_df[
                            unique_col
                        ].nunique()
                    )
                )

            st.markdown(
                "### Average Preference Rank"
            )

            chart = (
                sorted_df[
                    [
                        type_col,
                        avg_rank_col
                    ]
                ]
                .set_index(type_col)
            )

            st.bar_chart(
                chart
            )

        show_dataframe(
            sorted_df
            if "sorted_df" in locals()
            else investment_analysis
        )

    else:

        st.warning(
            "Investment preference analysis is unavailable."
        )


# ==============================================================================
# PAGE 3 — DEMOGRAPHIC ANALYSIS
# ==============================================================================

elif page == "Demographic Analysis":

    st.markdown(
        '<div class="section-title">Demographic Analysis</div>',
        unsafe_allow_html=True
    )

    tabs = st.tabs(
        [
            "Gender",
            "Age",
            "Investment Objective"
        ]
    )

    with tabs[0]:

        st.markdown(
            "### Gender × Investment Preference"
        )

        show_dataframe(
            gender_analysis
        )

        if not gender_analysis.empty:

            rank_col = find_column(
                gender_analysis,
                [
                    "Average_Preference_Rank"
                ]
            )

            if rank_col:

                st.bar_chart(
                    gender_analysis[
                        rank_col
                    ]
                )

    with tabs[1]:

        st.markdown(
            "### Age × Investment Preference"
        )

        show_dataframe(
            age_analysis
        )

        if not age_analysis.empty:

            rank_col = find_column(
                age_analysis,
                [
                    "Average_Preference_Rank"
                ]
            )

            if rank_col:

                st.bar_chart(
                    age_analysis[
                        rank_col
                    ]
                )

    with tabs[2]:

        st.markdown(
            "### Investment Objective × Preference"
        )

        show_dataframe(
            objective_analysis
        )

        if not objective_analysis.empty:

            rank_col = find_column(
                objective_analysis,
                [
                    "Average_Preference_Rank"
                ]
            )

            if rank_col:

                st.bar_chart(
                    objective_analysis[
                        rank_col
                    ]
                )


# ==============================================================================
# PAGE 4 — INVESTMENT BEHAVIOUR
# ==============================================================================

elif page == "Investment Behaviour":

    st.markdown(
        '<div class="section-title">Investment Behaviour</div>',
        unsafe_allow_html=True
    )

    tabs = st.tabs(
        [
            "Purpose",
            "Decision Factor",
            "Duration",
            "Expected Return"
        ]
    )

    with tabs[0]:

        show_dataframe(
            purpose_analysis
        )

        if not purpose_analysis.empty:

            st.bar_chart(
                purpose_analysis
            )

    with tabs[1]:

        show_dataframe(
            factor_analysis
        )

        if not factor_analysis.empty:

            st.bar_chart(
                factor_analysis
            )

    with tabs[2]:

        show_dataframe(
            duration_analysis
        )

        if not duration_analysis.empty:

            st.bar_chart(
                duration_analysis
            )

    with tabs[3]:

        st.info(
            "Expected Return is intentionally treated as "
            "categorical. No artificial numerical average "
            "is calculated."
        )

        show_dataframe(
            expected_return_analysis
        )

        if EXPECTED_RETURN:

            return_distribution = (
                respondent_df[
                    EXPECTED_RETURN
                ]
                .value_counts()
            )

            st.bar_chart(
                return_distribution
            )


# ==============================================================================
# PAGE 5 — INVESTMENT REASONS
# ==============================================================================

elif page == "Investment Reasons":

    st.markdown(
        '<div class="section-title">Investment Reasons</div>',
        unsafe_allow_html=True
    )

    if PURPOSE:

        st.markdown(
            "### Investment Purpose"
        )

        purpose_counts = (
            respondent_df[
                PURPOSE
            ]
            .value_counts()
        )

        st.bar_chart(
            purpose_counts
        )

    if not factor_analysis.empty:

        st.markdown(
            "### Decision Factors"
        )

        show_dataframe(
            factor_analysis
        )


# ==============================================================================
# PAGE 6 — SAVINGS OBJECTIVES
# ==============================================================================

elif page == "Savings Objectives":

    st.markdown(
        '<div class="section-title">Savings Objectives</div>',
        unsafe_allow_html=True
    )

    show_dataframe(
        savings_analysis
    )

    if not savings_analysis.empty:

        st.markdown(
            "### Savings Objective Analysis"
        )

        st.bar_chart(
            savings_analysis
        )


# ==============================================================================
# PAGE 7 — INFORMATION & MONITORING
# ==============================================================================

elif page == "Information & Monitoring":

    st.markdown(
        '<div class="section-title">Information & Monitoring</div>',
        unsafe_allow_html=True
    )

    tabs = st.tabs(
        [
            "Information Source",
            "Monitoring Frequency"
        ]
    )

    with tabs[0]:

        show_dataframe(
            source_analysis
        )

        if not source_analysis.empty:

            st.bar_chart(
                source_analysis
            )

    with tabs[1]:

        show_dataframe(
            monitoring_analysis
        )

        if not monitoring_analysis.empty:

            st.bar_chart(
                monitoring_analysis
            )


# ==============================================================================
# PAGE 8 — BUSINESS QUESTIONS
# ==============================================================================

elif page == "Business Questions":

    st.markdown(
        '<div class="section-title">Business Questions</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "### Female Investor Preference"
    )

    show_dataframe(
        female_analysis
    )

    st.markdown(
        "### Young Investor Preference"
    )

    show_dataframe(
        young_analysis
    )

    st.markdown(
        "### Bond Preference"
    )

    show_dataframe(
        bond_analysis
    )

    st.markdown(
        "### Gender Preference Gap"
    )

    show_dataframe(
        gender_gap
    )


# ==============================================================================
# PAGE 9 — EXECUTIVE INSIGHTS
# ==============================================================================

elif page == "Executive Insights":

    st.markdown(
        '<div class="section-title">Executive Analytical Insights</div>',
        unsafe_allow_html=True
    )

    if insights_df.empty:

        st.info(
            "No executive insights available."
        )

    else:

        for _, row in insights_df.iterrows():

            category = row.get(
                "Insight_Category",
                "Insight"
            )

            finding = row.get(
                "Finding",
                ""
            )

            interpretation = row.get(
                "Interpretation",
                ""
            )

            priority = row.get(
                "Priority",
                ""
            )

            with st.container():

                st.markdown(
                    f"### {category}"
                )

                st.write(
                    f"**Finding:** {finding}"
                )

                st.write(
                    f"**Interpretation:** {interpretation}"
                )

                if priority:

                    st.caption(
                        f"Priority: {priority}"
                    )

                st.divider()


# ==============================================================================
# PAGE 10 — RECOMMENDATIONS
# ==============================================================================

elif page == "Recommendations":

    st.markdown(
        '<div class="section-title">Executive Recommendations</div>',
        unsafe_allow_html=True
    )

    if recommendations_df.empty:

        st.info(
            "No analytical recommendations available."
        )

    else:

        for _, row in recommendations_df.iterrows():

            recommendation_id = row.get(
                "Recommendation_ID",
                ""
            )

            area = row.get(
                "Area",
                "Business Area"
            )

            recommendation = row.get(
                "Recommendation",
                ""
            )

            rationale = row.get(
                "Business_Rationale",
                ""
            )

            priority = row.get(
                "Priority",
                ""
            )

            st.markdown(
                f"### {recommendation_id} — {area}"
            )

            st.write(
                f"**Recommendation:** {recommendation}"
            )

            st.write(
                f"**Business Rationale:** {rationale}"
            )

            if priority:

                st.caption(
                    f"Priority: {priority}"
                )

            st.divider()


# ==============================================================================
# PAGE 11 — DATA QUALITY & VALIDATION
# ==============================================================================

elif page == "Data Quality & Validation":

    st.markdown(
        '<div class="section-title">Data Quality & Validation</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------------------------
    # Validation Summary
    # --------------------------------------------------------------------------

    st.markdown(
        "### Validation Summary"
    )

    if validation_report.empty:

        st.error(
            "validation_report.csv was not found."
        )

    else:

        summary = validation_report.iloc[0]

        total_checks = summary.get(
            "Total_Checks",
            0
        )

        passed = summary.get(
            "Passed",
            0
        )

        warnings = summary.get(
            "Warnings",
            0
        )

        failed = summary.get(
            "Failed",
            0
        )

        pass_rate = summary.get(
            "Pass_Rate_Percent",
            0
        )

        final_status = summary.get(
            "Final_Validation_Status",
            "UNKNOWN"
        )

        cols = st.columns(5)

        cols[0].metric(
            "Total Checks",
            format_number(total_checks)
        )

        cols[1].metric(
            "Passed",
            format_number(passed)
        )

        cols[2].metric(
            "Warnings",
            format_number(warnings)
        )

        cols[3].metric(
            "Failed",
            format_number(failed)
        )

        cols[4].metric(
            "Pass Rate",
            f"{pass_rate}%"
        )

        if str(final_status).upper() == "PASS":

            st.success(
                "Validation Status: PASS"
            )

        elif str(final_status).upper() == "WARNING":

            st.warning(
                "Validation Status: WARNING"
            )

        else:

            st.error(
                "Validation Status: FAIL"
            )

    # --------------------------------------------------------------------------
    # Validation Results
    # --------------------------------------------------------------------------

    st.markdown(
        "### Validation Results"
    )

    show_dataframe(
        validation_results,
        height=500
    )

    # --------------------------------------------------------------------------
    # Validation Failures
    # --------------------------------------------------------------------------

    st.markdown(
        "### Validation Errors"
    )

    if validation_errors.empty:

        st.success(
            "No validation errors detected."
        )

    else:

        st.error(
            f"{len(validation_errors)} validation failure(s) detected."
        )

        show_dataframe(
            validation_errors,
            height=350
        )


# ==============================================================================
# 13. FOOTER
# ==============================================================================

st.divider()

st.caption(
    "Investment Survey Analytics | "
    "Analytical pipeline + validation framework"
)