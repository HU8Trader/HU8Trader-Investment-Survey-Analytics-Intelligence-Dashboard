# ============================================================
# INVESTMENT SURVEY DASHBOARD
# PAGE: INVESTMENT BEHAVIOUR ANALYSIS
# File: dashboard/pages/behaviour.py
# ============================================================

from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
ANALYSIS_DIR = DATA_DIR / "analysis"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Investment Behaviour Analysis",
    page_icon="📈",
    layout="wide",
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

@st.cache_data
def load_csv(filename: str) -> pd.DataFrame:
    """Load an analysis CSV safely."""

    file_path = ANALYSIS_DIR / filename

    if not file_path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)

        # Remove accidental pandas index columns
        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        return df

    except Exception as error:
        st.error(f"Unable to load {filename}: {error}")
        return pd.DataFrame()


def find_column(df: pd.DataFrame, possible_names):
    """Find a column using case-insensitive matching."""

    if df.empty:
        return None

    normalized_columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:

        key = str(name).strip().lower()

        if key in normalized_columns:
            return normalized_columns[key]

    return None


def clean_text_series(series):
    """Clean text values."""

    return (
        series
        .astype(str)
        .str.strip()
        .replace(
            {
                "nan": "Unknown",
                "None": "Unknown",
                "": "Unknown",
            }
        )
    )


def show_table(df: pd.DataFrame, height=320):
    """Display dataframe safely."""

    if df.empty:
        st.info("No data available.")
        return

    st.dataframe(
        df,
        width="stretch",
        height=height,
        hide_index=True,
    )


def prepare_category_data(
    df: pd.DataFrame,
    category_candidates,
):
    """
    Detect category column and create respondent/count column.
    """

    if df.empty:
        return pd.DataFrame(), None, None

    category_col = find_column(
        df,
        category_candidates,
    )

    if category_col is None:
        return pd.DataFrame(), None, None

    result = df.copy()

    result[category_col] = clean_text_series(
        result[category_col]
    )

    count_col = find_column(
        result,
        [
            "Unique_Respondents",
            "Unique Respondents",
            "Respondent_Count",
            "Respondent Count",
            "Respondents",
            "Count",
            "Investor_Count",
            "Investor Count",
        ],
    )

    if count_col:

        result["Respondents"] = pd.to_numeric(
            result[count_col],
            errors="coerce",
        ).fillna(0)

    else:

        result["Respondents"] = 1

        result = (
            result
            .groupby(category_col, as_index=False)
            ["Respondents"]
            .sum()
        )

    result = result.sort_values(
        "Respondents",
        ascending=False,
    )

    return result, category_col, "Respondents"


def render_category_section(
    title,
    df,
    category_candidates,
    chart_title=None,
    key_prefix="section",
):
    """Render a reusable category analysis section."""

    st.subheader(title)

    if df.empty:

        st.info(
            f"No data available for {title.lower()}."
        )

        return

    data, category_col, count_col = prepare_category_data(
        df,
        category_candidates,
    )

    if data.empty or category_col is None:

        st.warning(
            "Required category column was not found."
        )

        return

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    top_row = data.iloc[0]

    top_value = top_row[category_col]
    top_count = top_row[count_col]

    kpi1, kpi2 = st.columns(2)

    with kpi1:

        st.metric(
            "Most Common",
            str(top_value),
        )

    with kpi2:

        st.metric(
            "Respondents",
            f"{int(top_count):,}",
        )

    # --------------------------------------------------------
    # Chart
    # --------------------------------------------------------

    chart_title = chart_title or title

    st.markdown(f"**{chart_title}**")

    chart_data = data[
        [
            category_col,
            count_col,
        ]
    ].copy()

    chart_data = chart_data.set_index(
        category_col
    )

    chart_data.columns = [
        "Respondents"
    ]

    st.bar_chart(
        chart_data,
        horizontal=True,
        width="stretch",
    )

    # --------------------------------------------------------
    # Table
    # --------------------------------------------------------

    table = data[
        [
            category_col,
            count_col,
        ]
    ].copy()

    table.columns = [
        "Category",
        "Respondents",
    ]

    table["Respondents"] = (
        pd.to_numeric(
            table["Respondents"],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )

    show_table(
        table,
        height=280,
    )


# ============================================================
# LOAD ANALYSIS OUTPUTS
# ============================================================

purpose = load_csv(
    "purpose_investment_analysis.csv"
)

factor = load_csv(
    "factor_investment_analysis.csv"
)

duration = load_csv(
    "duration_investment_analysis.csv"
)

expected_return = load_csv(
    "expected_return_analysis.csv"
)

monitoring = load_csv(
    "monitoring_investment_analysis.csv"
)

savings = load_csv(
    "savings_investment_analysis.csv"
)

source = load_csv(
    "source_investment_analysis.csv"
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("Investment Behaviour Analysis")

st.markdown(
    """
    ### Understanding how investors make investment decisions

    This page analyzes investor behaviour across:

    - Investment Purpose
    - Decision Factors
    - Investment Duration
    - Expected Return Expectations
    - Investment Monitoring Frequency
    - Savings Objectives
    - Information Sources
    """
)


# ============================================================
# DATA AVAILABILITY
# ============================================================

available_outputs = {
    "Purpose": purpose,
    "Decision Factor": factor,
    "Duration": duration,
    "Expected Return": expected_return,
    "Monitoring": monitoring,
    "Savings Objective": savings,
    "Information Source": source,
}

available_count = sum(
    not df.empty
    for df in available_outputs.values()
)


if available_count == 0:

    st.error(
        "No behaviour analysis files were found.\n\n"
        "Expected directory:\n"
        "`data/analysis/`"
    )

    st.stop()


# ============================================================
# OVERVIEW KPIs
# ============================================================

st.subheader("Behaviour Overview")

kpi_columns = st.columns(4)


def get_top_category(df, candidates):

    if df.empty:
        return "N/A", 0

    data, category_col, count_col = prepare_category_data(
        df,
        candidates,
    )

    if data.empty or category_col is None:
        return "N/A", 0

    row = data.iloc[0]

    return (
        str(row[category_col]),
        int(row[count_col]),
    )


top_purpose, purpose_count = get_top_category(
    purpose,
    [
        "Investment_Purpose",
        "Investment Purpose",
        "Purpose",
        "purpose",
    ],
)


top_factor, factor_count = get_top_category(
    factor,
    [
        "Decision_Factor",
        "Decision Factor",
        "Factor",
        "factor",
    ],
)


top_duration, duration_count = get_top_category(
    duration,
    [
        "Investment_Duration",
        "Investment Duration",
        "Duration",
        "duration",
    ],
)


top_monitoring, monitoring_count = get_top_category(
    monitoring,
    [
        "Investment_Monitoring",
        "Investment Monitoring",
        "Monitoring_Frequency",
        "Monitoring Frequency",
        "Monitoring",
        "Frequency",
    ],
)


with kpi_columns[0]:

    st.metric(
        "Most Common Purpose",
        top_purpose,
    )


with kpi_columns[1]:

    st.metric(
        "Top Decision Factor",
        top_factor,
    )


with kpi_columns[2]:

    st.metric(
        "Most Common Duration",
        top_duration,
    )


with kpi_columns[3]:

    st.metric(
        "Most Common Monitoring",
        top_monitoring,
    )


# ============================================================
# INVESTMENT PURPOSE
# ============================================================

st.divider()

render_category_section(
    title="Investment Purpose",
    df=purpose,
    category_candidates=[
        "Investment_Purpose",
        "Investment Purpose",
        "Purpose",
        "purpose",
    ],
    chart_title="Why Do Investors Invest?",
    key_prefix="purpose",
)


# ============================================================
# DECISION FACTOR
# ============================================================

st.divider()

render_category_section(
    title="Investment Decision Factors",
    df=factor,
    category_candidates=[
        "Decision_Factor",
        "Decision Factor",
        "Factor",
        "factor",
    ],
    chart_title="What Influences Investment Decisions?",
    key_prefix="factor",
)


# ============================================================
# INVESTMENT DURATION
# ============================================================

st.divider()

render_category_section(
    title="Investment Duration",
    df=duration,
    category_candidates=[
        "Investment_Duration",
        "Investment Duration",
        "Duration",
        "duration",
    ],
    chart_title="How Long Do Investors Plan to Stay Invested?",
    key_prefix="duration",
)


# ============================================================
# EXPECTED RETURN
# ============================================================

st.divider()

st.subheader("Expected Return Expectations")

if expected_return.empty:

    st.info(
        "Expected return analysis is not available."
    )

else:

    expected_type_col = find_column(
        expected_return,
        [
            "Expected_Return_Range",
            "Expected Return Range",
            "Expected_Return",
            "Expected Return",
            "Return_Range",
            "Return Range",
            "expected_return",
        ],
    )

    if expected_type_col is None:

        st.warning(
            "Expected return range column was not found."
        )

        show_table(expected_return)

    else:

        return_data = expected_return.copy()

        return_data[expected_type_col] = clean_text_series(
            return_data[expected_type_col]
        )

        return_count_col = find_column(
            return_data,
            [
                "Unique_Respondents",
                "Unique Respondents",
                "Respondent_Count",
                "Respondent Count",
                "Respondents",
                "Count",
            ],
        )

        if return_count_col:

            return_data["Respondents"] = pd.to_numeric(
                return_data[return_count_col],
                errors="coerce",
            ).fillna(0)

        else:

            return_data["Respondents"] = 1

            return_data = (
                return_data
                .groupby(
                    expected_type_col,
                    as_index=False,
                )
                ["Respondents"]
                .sum()
            )

        return_data = return_data.sort_values(
            "Respondents",
            ascending=False,
        )

        # KPI
        top_return = return_data.iloc[0][
            expected_type_col
        ]

        top_return_count = return_data.iloc[0][
            "Respondents"
        ]

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Most Common Expected Return",
                str(top_return),
            )

        with col2:

            st.metric(
                "Respondents",
                f"{int(top_return_count):,}",
            )

        # Chart
        chart = return_data[
            [
                expected_type_col,
                "Respondents",
            ]
        ].copy()

        chart = chart.set_index(
            expected_type_col
        )

        st.bar_chart(
            chart,
            horizontal=True,
            width="stretch",
        )

        show_table(
            return_data[
                [
                    expected_type_col,
                    "Respondents",
                ]
            ].rename(
                columns={
                    expected_type_col: "Expected Return Range"
                }
            ),
            height=280,
        )

        st.caption(
            "Expected Return is treated as a categorical range. "
            "No artificial numeric average is calculated."
        )


# ============================================================
# MONITORING FREQUENCY
# ============================================================

st.divider()

render_category_section(
    title="Investment Monitoring Frequency",
    df=monitoring,
    category_candidates=[
        "Investment_Monitoring",
        "Investment Monitoring",
        "Monitoring_Frequency",
        "Monitoring Frequency",
        "Monitoring",
        "Frequency",
    ],
    chart_title="How Frequently Do Investors Monitor Investments?",
    key_prefix="monitoring",
)


# ============================================================
# SAVINGS OBJECTIVES
# ============================================================

st.divider()

render_category_section(
    title="Savings Objectives",
    df=savings,
    category_candidates=[
        "Savings_Objective",
        "Savings Objective",
        "Investment_Objective",
        "Investment Objective",
        "Objective",
        "objective",
    ],
    chart_title="What Are Investors Saving For?",
    key_prefix="savings",
)


# ============================================================
# INFORMATION SOURCES
# ============================================================

st.divider()

render_category_section(
    title="Investment Information Sources",
    df=source,
    category_candidates=[
        "Information_Source",
        "Information Source",
        "Source",
        "source",
        "Information_Sources",
        "Information Sources",
    ],
    chart_title="Where Do Investors Get Investment Information?",
    key_prefix="source",
)


# ============================================================
# CROSS-BEHAVIOUR INSIGHTS
# ============================================================

st.divider()

st.subheader("Key Behavioural Insights")


insight_count = 0


if top_purpose != "N/A":

    st.info(
        f"**Investment Purpose:** "
        f"{top_purpose} is the most common investment purpose "
        f"among respondents."
    )

    insight_count += 1


if top_factor != "N/A":

    st.info(
        f"**Decision Factor:** "
        f"{top_factor} is the most frequently observed "
        f"decision factor."
    )

    insight_count += 1


if top_duration != "N/A":

    st.info(
        f"**Investment Duration:** "
        f"{top_duration} is the most common investment duration."
    )

    insight_count += 1


if top_monitoring != "N/A":

    st.info(
        f"**Monitoring Behaviour:** "
        f"{top_monitoring} is the most common investment monitoring "
        f"frequency."
    )

    insight_count += 1


if not expected_return.empty:

    expected_type_col = find_column(
        expected_return,
        [
            "Expected_Return_Range",
            "Expected Return Range",
            "Expected_Return",
            "Expected Return",
            "Return_Range",
            "Return Range",
        ],
    )

    if expected_type_col:

        st.info(
            "**Return Expectations:** "
            "Investors are analyzed using expected-return ranges "
            "rather than fabricated numeric averages."
        )

        insight_count += 1


if insight_count == 0:

    st.warning(
        "Not enough analytical outputs are available to generate insights."
    )


# ============================================================
# BUSINESS INTERPRETATION
# ============================================================

st.divider()

st.subheader("Business Interpretation")

st.markdown(
    """
    ### What this analysis can tell a business

    **1. Investment Purpose**

    Understanding why investors invest helps organizations design
    products around real financial objectives.

    **2. Decision Factors**

    The dominant decision factor indicates what should be emphasized
    during product communication and investor education.

    **3. Investment Duration**

    Duration helps identify whether the investor base is primarily
    short-term, medium-term, or long-term oriented.

    **4. Expected Return**

    Expected return ranges reveal investor expectations without
    introducing misleading numeric averages.

    **5. Monitoring Frequency**

    Monitoring behaviour can guide notification frequency, portfolio
    dashboards, and investor engagement strategies.

    **6. Savings Objective**

    Savings objectives can support targeted financial-product
    recommendations.

    **7. Information Sources**

    Understanding where investors obtain information can help determine
    the most effective communication and educational channels.
    """
)


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander("Methodology & Data Definitions"):

    st.markdown(
        """
        ### Respondent-Level Analysis

        Wherever possible, respondent counts are based on unique
        `Respondent_ID`.

        This prevents multiple investment rows belonging to the same
        respondent from being incorrectly treated as multiple investors.

        ### Expected Return

        Expected Return remains categorical.

        Example:

        - 10%-20%
        - 20%-30%
        - 30%-40%

        These values are **not converted into artificial averages**.

        ### Investment Behaviour

        Behaviour is analyzed across:

        - Purpose
        - Decision Factor
        - Duration
        - Expected Return
        - Monitoring Frequency
        - Savings Objective
        - Information Source
        """
    )


# ============================================================
# DATASET STATUS
# ============================================================

st.divider()

st.subheader("Analysis Output Status")

status_rows = []

for name, df in available_outputs.items():

    status_rows.append(
        {
            "Analysis": name,
            "Status": "Available" if not df.empty else "Missing",
            "Rows": len(df),
        }
    )


status_df = pd.DataFrame(status_rows)

show_table(
    status_df,
    height=280,
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Investment Survey Analytics | Behaviour Analysis | "
    "HiLyst Analytics"
)