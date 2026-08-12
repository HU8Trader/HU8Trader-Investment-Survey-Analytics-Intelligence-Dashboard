"""
Investment Survey Dashboard
File: dashboard/filters.py

Purpose:
    Reusable Streamlit filters for the Investment Survey dashboard.

Filters included:
    - Gender
    - Age Group
    - Investment Type
    - Investment Objective
    - Investment Purpose
    - Decision Factor
    - Expected Return Range
    - Investment Duration
    - Information Source
    - Monitoring Frequency
    - Savings Objective
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import pandas as pd
import streamlit as st


# ============================================================
# CONSTANTS
# ============================================================

ALL_OPTION = "All"


# ============================================================
# GENERAL HELPERS
# ============================================================

def _clean_values(
    series: Optional[pd.Series],
    include_all: bool = True,
) -> list[str]:
    """
    Return clean, unique, sorted values from a pandas Series.
    """

    if series is None:
        return [ALL_OPTION] if include_all else []

    if not isinstance(series, pd.Series):
        series = pd.Series(series)

    values = (
        series
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[values != ""]
    values = values[values.str.lower() != "nan"]

    unique_values = sorted(
        values.unique().tolist(),
        key=lambda x: x.lower()
    )

    if include_all:
        return [ALL_OPTION] + unique_values

    return unique_values


def _find_column(
    df: pd.DataFrame,
    candidates: Iterable[str],
) -> Optional[str]:
    """
    Find a dataframe column using case-insensitive matching.
    """

    if df is None or df.empty:
        return None

    column_map = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:
        key = str(candidate).strip().lower()

        if key in column_map:
            return column_map[key]

    return None


def _apply_filter(
    df: pd.DataFrame,
    column: Optional[str],
    selected_value: Any,
) -> pd.DataFrame:
    """
    Apply a single categorical filter.

    'All' means no filtering.
    """

    if df is None:
        return df

    if column is None:
        return df

    if selected_value in (None, ALL_OPTION):
        return df

    return df[
        df[column]
        .astype(str)
        .str.strip()
        == str(selected_value).strip()
    ].copy()


# ============================================================
# AGE GROUP
# ============================================================

def create_age_groups(
    df: pd.DataFrame,
    age_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Create an Age_Group column if it does not already exist.

    Groups:
        Under 25
        25–34
        35–44
        45–54
        55+
    """

    if df is None:
        return df

    result = df.copy()

    if "Age_Group" in result.columns:
        return result

    if age_column is None:
        age_column = _find_column(
            result,
            [
                "age",
                "Age",
                "Investor_Age",
                "Age_Years",
            ],
        )

    if age_column is None:
        return result

    age = pd.to_numeric(
        result[age_column],
        errors="coerce",
    )

    def classify_age(value):
        if pd.isna(value):
            return "Unknown"

        if value < 25:
            return "Under 25"

        if value < 35:
            return "25–34"

        if value < 45:
            return "35–44"

        if value < 55:
            return "45–54"

        return "55+"

    result["Age_Group"] = age.apply(classify_age)

    return result


# ============================================================
# SINGLE FILTER FUNCTIONS
# ============================================================

def gender_filter(
    df: pd.DataFrame,
    key: str = "gender_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Gender filter.
    """

    column = _find_column(
        df,
        [
            "Gender",
            "gender",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Gender",
        options,
        key=key,
    )

    return _apply_filter(df, column, selected), selected


def age_group_filter(
    df: pd.DataFrame,
    key: str = "age_group_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Age-group filter.
    """

    result = create_age_groups(df)

    if "Age_Group" not in result.columns:
        return result, ALL_OPTION

    options = _clean_values(result["Age_Group"])

    selected = st.selectbox(
        "Age Group",
        options,
        key=key,
    )

    return _apply_filter(
        result,
        "Age_Group",
        selected,
    ), selected


def investment_type_filter(
    df: pd.DataFrame,
    key: str = "investment_type_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Investment type filter.
    """

    column = _find_column(
        df,
        [
            "Investment_Type",
            "Investment Type",
            "investment_type",
            "Investment",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Investment Type",
        options,
        key=key,
    )

    return _apply_filter(
        df,
        column,
        selected,
    ), selected


def objective_filter(
    df: pd.DataFrame,
    key: str = "objective_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Investment objective filter.
    """

    column = _find_column(
        df,
        [
            "Investment_Objective",
            "Investment Objective",
            "objective",
            "Objective",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Investment Objective",
        options,
        key=key,
    )

    return _apply_filter(
        df,
        column,
        selected,
    ), selected


def purpose_filter(
    df: pd.DataFrame,
    key: str = "purpose_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Investment purpose filter.
    """

    column = _find_column(
        df,
        [
            "Investment_Purpose",
            "Investment Purpose",
            "purpose",
            "Purpose",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Investment Purpose",
        options,
        key=key,
    )

    return _apply_filter(
        df,
        column,
        selected,
    ), selected


def decision_factor_filter(
    df: pd.DataFrame,
    key: str = "decision_factor_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Decision factor filter.
    """

    column = _find_column(
        df,
        [
            "Decision_Factor",
            "Decision Factor",
            "factor",
            "Factor",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Decision Factor",
        options,
        key=key,
    )

    return _apply_filter(
        df,
        column,
        selected,
    ), selected


def expected_return_filter(
    df: pd.DataFrame,
    key: str = "expected_return_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Expected return range filter.

    Important:
        Expected return remains categorical.
        Values such as 10%-20% are NOT converted
        into artificial numeric averages.
    """

    column = _find_column(
        df,
        [
            "Expected_Return_Range",
            "Expected Return Range",
            "Expected_Return",
            "Expected Return",
            "expected",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Expected Return Range",
        options,
        key=key,
    )

    return _apply_filter(
        df,
        column,
        selected,
    ), selected


def duration_filter(
    df: pd.DataFrame,
    key: str = "duration_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Investment duration filter.
    """

    column = _find_column(
        df,
        [
            "Investment_Duration",
            "Investment Duration",
            "Duration",
            "duration",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Investment Duration",
        options,
        key=key,
    )

    return _apply_filter(
        df,
        column,
        selected,
    ), selected


def source_filter(
    df: pd.DataFrame,
    key: str = "source_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Information source filter.
    """

    column = _find_column(
        df,
        [
            "Information_Source",
            "Information Source",
            "Source",
            "source",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Information Source",
        options,
        key=key,
    )

    return _apply_filter(
        df,
        column,
        selected,
    ), selected


def monitoring_filter(
    df: pd.DataFrame,
    key: str = "monitoring_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Investment monitoring frequency filter.
    """

    column = _find_column(
        df,
        [
            "Monitoring_Frequency",
            "Monitoring Frequency",
            "monitoring",
            "Monitoring",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Monitoring Frequency",
        options,
        key=key,
    )

    return _apply_filter(
        df,
        column,
        selected,
    ), selected


def savings_objective_filter(
    df: pd.DataFrame,
    key: str = "savings_objective_filter",
) -> tuple[pd.DataFrame, str]:
    """
    Savings objective filter.
    """

    column = _find_column(
        df,
        [
            "Savings_Objective",
            "Savings Objective",
            "Savings",
            "savings",
        ],
    )

    if column is None:
        return df, ALL_OPTION

    options = _clean_values(df[column])

    selected = st.selectbox(
        "Savings Objective",
        options,
        key=key,
    )

    return _apply_filter(
        df,
        column,
        selected,
    ), selected


# ============================================================
# MULTI-SELECT FILTERS
# ============================================================

def multiselect_filter(
    df: pd.DataFrame,
    column: str,
    label: str,
    key: str,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Generic multiselect filter.

    If nothing is selected, all values are included.
    """

    if df is None or column not in df.columns:
        return df, []

    options = _clean_values(
        df[column],
        include_all=False,
    )

    selected = st.multiselect(
        label,
        options,
        default=[],
        key=key,
    )

    if not selected:
        return df, options

    result = df[
        df[column]
        .astype(str)
        .str.strip()
        .isin(selected)
    ].copy()

    return result, selected


# ============================================================
# SIDEBAR FILTER PANEL
# ============================================================

def render_sidebar_filters(
    respondents: pd.DataFrame,
    investments: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Render the complete dashboard filter panel.

    Returns:
        {
            "respondents": filtered respondents,
            "investments": filtered investments,
            "gender": selected gender,
            "age_group": selected age group,
            "objective": selected objective,
            "purpose": selected purpose,
            "factor": selected decision factor,
            "expected_return": selected expected return,
            "duration": selected duration,
            "source": selected source,
            "monitoring": selected monitoring frequency,
            "savings": selected savings objective,
        }
    """

    if respondents is None:
        respondents = pd.DataFrame()

    respondent_filtered = respondents.copy()

    investment_filtered = (
        investments.copy()
        if investments is not None
        else pd.DataFrame()
    )

    selections: Dict[str, Any] = {}

    with st.sidebar:

        st.markdown("## Dashboard Filters")

        st.caption(
            "Use the filters below to interactively "
            "explore the investment survey."
        )

        st.divider()

        # ----------------------------------------------------
        # DEMOGRAPHICS
        # ----------------------------------------------------

        st.markdown("### Demographics")

        respondent_filtered, selections["gender"] = gender_filter(
            respondent_filtered,
            key="sidebar_gender",
        )

        respondent_filtered, selections["age_group"] = age_group_filter(
            respondent_filtered,
            key="sidebar_age_group",
        )

        st.divider()

        # ----------------------------------------------------
        # INVESTMENT BEHAVIOUR
        # ----------------------------------------------------

        st.markdown("### Investment Behaviour")

        respondent_filtered, selections["objective"] = objective_filter(
            respondent_filtered,
            key="sidebar_objective",
        )

        respondent_filtered, selections["purpose"] = purpose_filter(
            respondent_filtered,
            key="sidebar_purpose",
        )

        respondent_filtered, selections["factor"] = decision_factor_filter(
            respondent_filtered,
            key="sidebar_factor",
        )

        respondent_filtered, selections["expected_return"] = (
            expected_return_filter(
                respondent_filtered,
                key="sidebar_expected_return",
            )
        )

        st.divider()

        # ----------------------------------------------------
        # INVESTMENT DETAILS
        # ----------------------------------------------------

        st.markdown("### Investment Details")

        respondent_filtered, selections["duration"] = duration_filter(
            respondent_filtered,
            key="sidebar_duration",
        )

        respondent_filtered, selections["source"] = source_filter(
            respondent_filtered,
            key="sidebar_source",
        )

        respondent_filtered, selections["monitoring"] = monitoring_filter(
            respondent_filtered,
            key="sidebar_monitoring",
        )

        respondent_filtered, selections["savings"] = savings_objective_filter(
            respondent_filtered,
            key="sidebar_savings",
        )

        st.divider()

        # ----------------------------------------------------
        # INVESTMENT TYPE
        # ----------------------------------------------------

        if not investment_filtered.empty:

            investment_filtered, selections["investment_type"] = (
                investment_type_filter(
                    investment_filtered,
                    key="sidebar_investment_type",
                )
            )

        else:
            selections["investment_type"] = ALL_OPTION

        st.divider()

        # ----------------------------------------------------
        # RESET BUTTON
        # ----------------------------------------------------

        st.caption(
            f"Respondents available: "
            f"{len(respondent_filtered):,}"
        )

        if not investment_filtered.empty:
            st.caption(
                f"Investment records available: "
                f"{len(investment_filtered):,}"
            )

    return {
        "respondents": respondent_filtered,
        "investments": investment_filtered,
        **selections,
    }


# ============================================================
# CROSS-FILTER INVESTMENT DATA
# ============================================================

def filter_investments_by_respondents(
    investments: pd.DataFrame,
    filtered_respondents: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep investment rows belonging to currently
    filtered respondents.

    This preserves the respondent -> investment
    relationship.
    """

    if investments is None or investments.empty:
        return investments

    if filtered_respondents is None:
        return investments

    respondent_id_in_respondents = _find_column(
        filtered_respondents,
        [
            "Respondent_ID",
            "Respondent ID",
            "respondent_id",
            "ID",
        ],
    )

    respondent_id_in_investments = _find_column(
        investments,
        [
            "Respondent_ID",
            "Respondent ID",
            "respondent_id",
            "ID",
        ],
    )

    if (
        respondent_id_in_respondents is None
        or respondent_id_in_investments is None
    ):
        return investments

    valid_ids = set(
        filtered_respondents[
            respondent_id_in_respondents
        ]
        .dropna()
        .astype(str)
        .str.strip()
    )

    result = investments[
        investments[respondent_id_in_investments]
        .astype(str)
        .str.strip()
        .isin(valid_ids)
    ].copy()

    return result


# ============================================================
# FILTER SUMMARY
# ============================================================

def get_filter_summary(
    filter_state: Dict[str, Any],
) -> pd.DataFrame:
    """
    Convert current filter selections into
    a small dataframe for display/export.
    """

    labels = {
        "gender": "Gender",
        "age_group": "Age Group",
        "investment_type": "Investment Type",
        "objective": "Investment Objective",
        "purpose": "Investment Purpose",
        "factor": "Decision Factor",
        "expected_return": "Expected Return Range",
        "duration": "Investment Duration",
        "source": "Information Source",
        "monitoring": "Monitoring Frequency",
        "savings": "Savings Objective",
    }

    rows = []

    for key, label in labels.items():

        value = filter_state.get(
            key,
            ALL_OPTION,
        )

        rows.append(
            {
                "Filter": label,
                "Selected Value": value,
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# DISPLAY ACTIVE FILTERS
# ============================================================

def display_active_filters(
    filter_state: Dict[str, Any],
) -> None:
    """
    Display active filters above dashboard content.
    """

    active_filters = []

    labels = {
        "gender": "Gender",
        "age_group": "Age",
        "investment_type": "Investment",
        "objective": "Objective",
        "purpose": "Purpose",
        "factor": "Decision Factor",
        "expected_return": "Expected Return",
        "duration": "Duration",
        "source": "Source",
        "monitoring": "Monitoring",
        "savings": "Savings Objective",
    }

    for key, label in labels.items():

        value = filter_state.get(
            key,
            ALL_OPTION,
        )

        if value not in (
            None,
            ALL_OPTION,
            "",
        ):
            active_filters.append(
                f"**{label}:** {value}"
            )

    if active_filters:

        st.info(
            " | ".join(active_filters)
        )


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "ALL_OPTION",
    "create_age_groups",
    "gender_filter",
    "age_group_filter",
    "investment_type_filter",
    "objective_filter",
    "purpose_filter",
    "decision_factor_filter",
    "expected_return_filter",
    "duration_filter",
    "source_filter",
    "monitoring_filter",
    "savings_objective_filter",
    "multiselect_filter",
    "render_sidebar_filters",
    "filter_investments_by_respondents",
    "get_filter_summary",
    "display_active_filters",
]