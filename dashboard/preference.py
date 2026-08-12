# ============================================================
# INVESTMENT SURVEY DASHBOARD
# PAGE: INVESTMENT PREFERENCE ANALYSIS
# File: dashboard/pages/preference.py
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
    page_title="Investment Preference Analysis",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

@st.cache_data
def load_csv(filename: str) -> pd.DataFrame:
    """
    Load an analysis CSV safely.
    """

    file_path = ANALYSIS_DIR / filename

    if not file_path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)

        # Remove accidental unnamed/index columns
        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        return df

    except Exception as error:
        st.error(f"Unable to load {filename}: {error}")
        return pd.DataFrame()


def find_column(df: pd.DataFrame, possible_names):
    """
    Find a column using case-insensitive matching.
    """

    if df.empty:
        return None

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:
        key = str(name).strip().lower()

        if key in normalized:
            return normalized[key]

    return None


def show_dataframe(df: pd.DataFrame, height=350):
    """
    Display dataframe safely.
    """

    if df.empty:
        st.info("No data available for this analysis.")
        return

    st.dataframe(
        df,
        width="stretch",
        height=height,
        hide_index=True,
    )


def format_number(value):
    """
    Format numeric values for KPI cards.
    """

    if pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):,.2f}"
    except Exception:
        return str(value)


# ============================================================
# LOAD DATA
# ============================================================

overall = load_csv("investment_preference_analysis.csv")
gender = load_csv("gender_investment_analysis.csv")
age = load_csv("age_investment_analysis.csv")
objective = load_csv("objective_investment_analysis.csv")

female = load_csv("female_investment_preference.csv")
young = load_csv("young_investor_preference.csv")
bond = load_csv("bond_preference_analysis.csv")


# ============================================================
# PAGE HEADER
# ============================================================

st.title("Investment Preference Analysis")

st.markdown(
    """
    ### How do investors rank different investment avenues?

    This page analyzes investment preferences using **Preference Rank**.

    **Important:** A lower average preference rank means a stronger
    investment preference.

    For example:

    - Rank 1 → strongest preference
    - Rank 2 → second strongest
    - Rank 7 → weakest preference
    """
)


# ============================================================
# DATA AVAILABILITY CHECK
# ============================================================

if overall.empty:
    st.error(
        "Investment preference analysis data was not found.\n\n"
        "Expected file:\n"
        "`data/analysis/investment_preference_analysis.csv`"
    )

    st.stop()


# ============================================================
# IDENTIFY OVERALL COLUMNS
# ============================================================

overall_type_col = find_column(
    overall,
    [
        "Investment_Type",
        "Investment Type",
        "investment_type",
        "Investment",
        "Type",
    ],
)

overall_rank_col = find_column(
    overall,
    [
        "Average_Preference_Rank",
        "Average Preference Rank",
        "avg_preference_rank",
        "Preference_Rank",
        "Preference Rank",
    ],
)

overall_count_col = find_column(
    overall,
    [
        "Unique_Respondents",
        "Unique Respondents",
        "Respondent_Count",
        "Respondent Count",
        "Count",
    ],
)


# ============================================================
# STANDARDIZE OVERALL DATA
# ============================================================

if overall_type_col:
    overall["Investment_Type_Display"] = (
        overall[overall_type_col]
        .astype(str)
        .str.strip()
    )

if overall_rank_col:
    overall["Average_Rank_Display"] = pd.to_numeric(
        overall[overall_rank_col],
        errors="coerce",
    )

if overall_count_col:
    overall["Respondent_Count_Display"] = pd.to_numeric(
        overall[overall_count_col],
        errors="coerce",
    )


# ============================================================
# CALCULATE TOP / SECOND / LEAST PREFERENCES
# ============================================================

if overall_rank_col:

    preference_sorted = (
        overall
        .dropna(subset=["Average_Rank_Display"])
        .sort_values(
            "Average_Rank_Display",
            ascending=True,
        )
        .reset_index(drop=True)
    )

else:

    preference_sorted = pd.DataFrame()


top_investment = "N/A"
second_investment = "N/A"
least_investment = "N/A"

top_rank = None
second_rank = None
least_rank = None


if not preference_sorted.empty:

    top_investment = preference_sorted.iloc[0][
        "Investment_Type_Display"
    ]

    top_rank = preference_sorted.iloc[0][
        "Average_Rank_Display"
    ]

    if len(preference_sorted) >= 2:

        second_investment = preference_sorted.iloc[1][
            "Investment_Type_Display"
        ]

        second_rank = preference_sorted.iloc[1][
            "Average_Rank_Display"
        ]

    least_investment = preference_sorted.iloc[-1][
        "Investment_Type_Display"
    ]

    least_rank = preference_sorted.iloc[-1][
        "Average_Rank_Display"
    ]


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("Preference Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.metric(
        label="Most Preferred Investment",
        value=top_investment,
        delta=(
            f"Avg Rank: {top_rank:.2f}"
            if top_rank is not None
            else None
        ),
    )


with kpi2:

    st.metric(
        label="Second Most Preferred",
        value=second_investment,
        delta=(
            f"Avg Rank: {second_rank:.2f}"
            if second_rank is not None
            else None
        ),
    )


with kpi3:

    st.metric(
        label="Least Preferred Investment",
        value=least_investment,
        delta=(
            f"Avg Rank: {least_rank:.2f}"
            if least_rank is not None
            else None
        ),
    )


with kpi4:

    st.metric(
        label="Investment Categories",
        value=len(preference_sorted),
    )


# ============================================================
# OVERALL PREFERENCE RANKING
# ============================================================

st.divider()

st.subheader("Overall Investment Preference Ranking")

if preference_sorted.empty:

    st.warning(
        "Preference ranking could not be calculated because "
        "Average_Preference_Rank is unavailable."
    )

else:

    ranking_display = preference_sorted.copy()

    ranking_display.insert(
        0,
        "Preference",
        range(1, len(ranking_display) + 1),
    )

    ranking_display = ranking_display[
        [
            "Preference",
            "Investment_Type_Display",
            "Average_Rank_Display",
        ]
    ]

    ranking_display.columns = [
        "Preference",
        "Investment Type",
        "Average Preference Rank",
    ]

    ranking_display["Average Preference Rank"] = (
        ranking_display["Average Preference Rank"]
        .round(2)
    )

    show_dataframe(
        ranking_display,
        height=330,
    )

    st.caption(
        "Lower Average Preference Rank = Stronger Investor Preference"
    )


# ============================================================
# BAR CHART
# ============================================================

st.subheader("Investment Preference Ranking")

if not preference_sorted.empty:

    chart_data = preference_sorted[
        [
            "Investment_Type_Display",
            "Average_Rank_Display",
        ]
    ].copy()

    chart_data = chart_data.set_index(
        "Investment_Type_Display"
    )

    chart_data.columns = [
        "Average Preference Rank"
    ]

    st.bar_chart(
        chart_data,
        horizontal=True,
        width="stretch",
    )

    st.caption(
        "The investment with the shortest bar has the strongest preference "
        "because lower rank indicates stronger preference."
    )


# ============================================================
# GENDER ANALYSIS
# ============================================================

st.divider()

st.subheader("Investment Preference by Gender")

if gender.empty:

    st.info(
        "Gender investment analysis is not available."
    )

else:

    gender_type_col = find_column(
        gender,
        [
            "Investment_Type",
            "Investment Type",
            "investment_type",
            "Investment",
            "Type",
        ],
    )

    gender_col = find_column(
        gender,
        [
            "Gender",
            "gender",
        ],
    )

    gender_rank_col = find_column(
        gender,
        [
            "Average_Preference_Rank",
            "Average Preference Rank",
            "avg_preference_rank",
        ],
    )

    gender_count_col = find_column(
        gender,
        [
            "Unique_Respondents",
            "Unique Respondents",
            "Respondent_Count",
            "Respondent Count",
        ],
    )

    if gender_type_col is None:

        st.warning(
            "Gender analysis does not contain an Investment_Type column."
        )

    else:

        gender_display = gender.copy()

        if gender_col:

            selected_gender = st.selectbox(
                "Select Gender",
                sorted(
                    gender_display[gender_col]
                    .dropna()
                    .astype(str)
                    .unique()
                ),
            )

            gender_display = gender_display[
                gender_display[gender_col].astype(str)
                == selected_gender
            ]

        else:

            selected_gender = None

        if gender_rank_col:

            gender_display["Average Rank"] = pd.to_numeric(
                gender_display[gender_rank_col],
                errors="coerce",
            )

            gender_display = gender_display.sort_values(
                "Average Rank",
                ascending=True,
            )

        if gender_count_col:

            gender_display["Respondents"] = pd.to_numeric(
                gender_display[gender_count_col],
                errors="coerce",
            )

        columns_to_show = []

        if gender_type_col:
            columns_to_show.append(gender_type_col)

        if gender_rank_col:
            columns_to_show.append("Average Rank")

        if gender_count_col:
            columns_to_show.append("Respondents")

        if columns_to_show:

            gender_table = gender_display[
                columns_to_show
            ].copy()

            rename_map = {
                gender_type_col: "Investment Type",
            }

            if gender_type_col:
                gender_table = gender_table.rename(
                    columns=rename_map
                )

            show_dataframe(
                gender_table,
                height=300,
            )

        # Gender chart
        if gender_rank_col:

            gender_chart = gender_display[
                [
                    gender_type_col,
                    "Average Rank",
                ]
            ].copy()

            gender_chart = gender_chart.set_index(
                gender_type_col
            )

            st.bar_chart(
                gender_chart,
                horizontal=True,
                width="stretch",
            )


# ============================================================
# AGE ANALYSIS
# ============================================================

st.divider()

st.subheader("Investment Preference by Age Group")

if age.empty:

    st.info(
        "Age investment analysis is not available."
    )

else:

    age_type_col = find_column(
        age,
        [
            "Investment_Type",
            "Investment Type",
            "investment_type",
        ],
    )

    age_group_col = find_column(
        age,
        [
            "Age_Group",
            "Age Group",
            "age_group",
            "Age",
            "age",
        ],
    )

    age_rank_col = find_column(
        age,
        [
            "Average_Preference_Rank",
            "Average Preference Rank",
            "avg_preference_rank",
        ],
    )

    if age_type_col is None:

        st.warning(
            "Age analysis does not contain an Investment_Type column."
        )

    else:

        age_display = age.copy()

        if age_group_col:

            age_groups = sorted(
                age_display[age_group_col]
                .dropna()
                .astype(str)
                .unique()
            )

            selected_age = st.selectbox(
                "Select Age Group",
                age_groups,
                key="preference_age_group",
            )

            age_display = age_display[
                age_display[age_group_col].astype(str)
                == selected_age
            ]

        if age_rank_col:

            age_display["Average Rank"] = pd.to_numeric(
                age_display[age_rank_col],
                errors="coerce",
            )

            age_display = age_display.sort_values(
                "Average Rank",
                ascending=True,
            )

            age_chart = age_display[
                [
                    age_type_col,
                    "Average Rank",
                ]
            ].copy()

            age_chart = age_chart.set_index(
                age_type_col
            )

            st.bar_chart(
                age_chart,
                horizontal=True,
                width="stretch",
            )

            st.caption(
                "Lower average rank indicates stronger preference."
            )

        show_dataframe(
            age_display,
            height=300,
        )


# ============================================================
# OBJECTIVE ANALYSIS
# ============================================================

st.divider()

st.subheader("Investment Preference by Investment Objective")

if objective.empty:

    st.info(
        "Investment objective analysis is not available."
    )

else:

    objective_type_col = find_column(
        objective,
        [
            "Investment_Type",
            "Investment Type",
            "investment_type",
        ],
    )

    objective_col = find_column(
        objective,
        [
            "Investment_Objective",
            "Investment Objective",
            "Objective",
            "objective",
        ],
    )

    objective_rank_col = find_column(
        objective,
        [
            "Average_Preference_Rank",
            "Average Preference Rank",
            "avg_preference_rank",
        ],
    )

    if objective_type_col is None:

        st.warning(
            "Objective analysis does not contain an Investment_Type column."
        )

    else:

        objective_display = objective.copy()

        if objective_col:

            objectives = sorted(
                objective_display[objective_col]
                .dropna()
                .astype(str)
                .unique()
            )

            selected_objective = st.selectbox(
                "Select Investment Objective",
                objectives,
                key="preference_objective",
            )

            objective_display = objective_display[
                objective_display[objective_col].astype(str)
                == selected_objective
            ]

        if objective_rank_col:

            objective_display["Average Rank"] = pd.to_numeric(
                objective_display[objective_rank_col],
                errors="coerce",
            )

            objective_display = objective_display.sort_values(
                "Average Rank",
                ascending=True,
            )

            objective_chart = objective_display[
                [
                    objective_type_col,
                    "Average Rank",
                ]
            ].copy()

            objective_chart = objective_chart.set_index(
                objective_type_col
            )

            st.bar_chart(
                objective_chart,
                horizontal=True,
                width="stretch",
            )

        show_dataframe(
            objective_display,
            height=300,
        )


# ============================================================
# FEMALE INVESTOR ANALYSIS
# ============================================================

st.divider()

st.subheader("Female Investor Preference")

if female.empty:

    st.info(
        "Female investor preference analysis is not available."
    )

else:

    female_type_col = find_column(
        female,
        [
            "Investment_Type",
            "Investment Type",
            "investment_type",
        ],
    )

    female_rank_col = find_column(
        female,
        [
            "Average_Preference_Rank",
            "Average Preference Rank",
            "avg_preference_rank",
        ],
    )

    if female_type_col and female_rank_col:

        female_display = female.copy()

        female_display["Average Rank"] = pd.to_numeric(
            female_display[female_rank_col],
            errors="coerce",
        )

        female_display = female_display.sort_values(
            "Average Rank",
            ascending=True,
        )

        female_chart = female_display[
            [
                female_type_col,
                "Average Rank",
            ]
        ].copy()

        female_chart = female_chart.set_index(
            female_type_col
        )

        st.bar_chart(
            female_chart,
            horizontal=True,
            width="stretch",
        )

        show_dataframe(
            female_display,
            height=300,
        )

    else:

        show_dataframe(female)


# ============================================================
# YOUNG INVESTOR ANALYSIS
# ============================================================

st.divider()

st.subheader("Young Investor Preference")

if young.empty:

    st.info(
        "Young investor preference analysis is not available."
    )

else:

    young_type_col = find_column(
        young,
        [
            "Investment_Type",
            "Investment Type",
            "investment_type",
        ],
    )

    young_rank_col = find_column(
        young,
        [
            "Average_Preference_Rank",
            "Average Preference Rank",
            "avg_preference_rank",
        ],
    )

    if young_type_col and young_rank_col:

        young_display = young.copy()

        young_display["Average Rank"] = pd.to_numeric(
            young_display[young_rank_col],
            errors="coerce",
        )

        young_display = young_display.sort_values(
            "Average Rank",
            ascending=True,
        )

        young_chart = young_display[
            [
                young_type_col,
                "Average Rank",
            ]
        ].copy()

        young_chart = young_chart.set_index(
            young_type_col
        )

        st.bar_chart(
            young_chart,
            horizontal=True,
            width="stretch",
        )

        show_dataframe(
            young_display,
            height=300,
        )

    else:

        show_dataframe(young)


# ============================================================
# BOND PREFERENCE ANALYSIS
# ============================================================

st.divider()

st.subheader("Bond Preference Analysis")

if bond.empty:

    st.info(
        "Bond preference analysis is not available."
    )

else:

    show_dataframe(
        bond,
        height=350,
    )


# ============================================================
# BUSINESS INTERPRETATION
# ============================================================

st.divider()

st.subheader("Analytical Interpretation")

if top_investment != "N/A":

    st.markdown(
        f"""
        **Key Finding**

        **{top_investment}** has the strongest overall investor preference
        based on the lowest average preference rank.

        The calculated average rank is approximately
        **{top_rank:.2f}**.

        Because preference rank is ordinal:

        > **Lower rank = stronger preference**

        Therefore, the analysis should not interpret a higher numerical
        rank as a stronger investment preference.
        """
    )

if least_investment != "N/A":

    st.markdown(
        f"""
        **Weakest Preference**

        **{least_investment}** has the weakest relative preference because
        it has the highest average preference rank among the available
        investment categories.
        """
    )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander("Methodology & Definitions"):

    st.markdown(
        """
        ### Preference Rank

        Preference Rank represents the order in which respondents ranked
        investment avenues.

        ### Interpretation

        | Rank | Meaning |
        |---:|---|
        | 1 | Strongest preference |
        | 2 | Very strong preference |
        | 3 | Strong preference |
        | 4 | Moderate preference |
        | 5 | Lower preference |
        | 6 | Weak preference |
        | 7 | Weakest preference |

        ### Average Preference Rank

        For each investment type:

        **Average Preference Rank = Mean of respondent preference ranks**

        The investment with the **lowest average rank** is considered the
        most preferred.

        ### Respondent Count

        Respondent counts should be based on unique `Respondent_ID`,
        not investment rows.

        This prevents multiple investment records belonging to the same
        respondent from being incorrectly counted as separate people.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Investment Survey Analytics | Preference Analysis | "
    "HiLyst Analytics"
)