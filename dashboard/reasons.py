# dashboard/pages/reasons.py

from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
ANALYSIS_DIR = DATA_DIR / "analysis"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_csv(filename: str) -> pd.DataFrame:
    """
    Safely load an analysis CSV file.
    """

    file_path = ANALYSIS_DIR / filename

    if not file_path.exists():
        st.warning(f"Analysis file not found: {filename}")
        return pd.DataFrame()

    try:
        return pd.read_csv(file_path)
    except Exception as exc:
        st.error(f"Could not load {filename}: {exc}")
        return pd.DataFrame()


def find_column(df: pd.DataFrame, candidates):
    """
    Find the first matching column from a list of possible names.
    """

    if df.empty:
        return None

    normalized = {
        str(col).strip().lower().replace(" ", "_"): col
        for col in df.columns
    }

    for candidate in candidates:
        key = candidate.strip().lower().replace(" ", "_")

        if key in normalized:
            return normalized[key]

    return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning for visualization.
    """

    if df.empty:
        return df

    result = df.copy()

    result.columns = [
        str(col).strip()
        for col in result.columns
    ]

    return result


def show_dataframe(df: pd.DataFrame, height=300):
    """
    Display a dataframe in a consistent dashboard format.
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


# ============================================================
# PAGE HEADER
# ============================================================

def render():
    """
    Render the Investment Reasons Analysis page.
    """

    st.title("Reasons & Decision Drivers")

    st.markdown(
        """
        Understand **why investors choose particular investment avenues**.

        This page analyses the factors, purposes, and motivations
        influencing investment decisions.
        """
    )

    st.divider()

    # ========================================================
    # LOAD DATA
    # ========================================================

    factor_df = clean_dataframe(
        load_csv("factor_investment_analysis.csv")
    )

    purpose_df = clean_dataframe(
        load_csv("purpose_investment_analysis.csv")
    )

    preference_df = clean_dataframe(
        load_csv("investment_preference_analysis.csv")
    )

    # ========================================================
    # SECTION 1 — DECISION FACTORS
    # ========================================================

    st.subheader("1. Investment Decision Factors")

    if not factor_df.empty:

        factor_col = find_column(
            factor_df,
            [
                "Decision_Factor",
                "Investment_Factor",
                "Factor",
                "Investment Decision Factor",
            ],
        )

        count_col = find_column(
            factor_df,
            [
                "Unique_Respondents",
                "Respondent_Count",
                "Respondents",
                "Count",
                "Investor_Count",
            ],
        )

        investment_col = find_column(
            factor_df,
            [
                "Investment_Type",
                "Investment Type",
            ],
        )

        avg_rank_col = find_column(
            factor_df,
            [
                "Average_Preference_Rank",
                "Avg_Preference_Rank",
                "Average Rank",
            ],
        )

        # ----------------------------------------------------
        # Factor summary
        # ----------------------------------------------------

        if factor_col and count_col:

            summary = (
                factor_df
                .groupby(factor_col, as_index=False)[count_col]
                .sum()
                .sort_values(count_col, ascending=False)
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("**Decision Factor Distribution**")

                chart_data = summary.set_index(factor_col)[count_col]

                st.bar_chart(
                    chart_data,
                    width="stretch",
                )

            with col2:

                st.markdown("**Top Decision Factors**")

                display_df = summary.head(10).copy()

                show_dataframe(
                    display_df,
                    height=300,
                )

        # ----------------------------------------------------
        # Investment type by decision factor
        # ----------------------------------------------------

        if factor_col and investment_col and count_col:

            st.markdown(
                "**Investment Type by Decision Factor**"
            )

            pivot = factor_df.pivot_table(
                index=factor_col,
                columns=investment_col,
                values=count_col,
                aggfunc="sum",
                fill_value=0,
            )

            if not pivot.empty:

                st.bar_chart(
                    pivot,
                    width="stretch",
                )

        # ----------------------------------------------------
        # Average preference rank by factor
        # ----------------------------------------------------

        if factor_col and avg_rank_col:

            st.markdown(
                "**Average Preference Rank by Decision Factor**"
            )

            rank_summary = (
                factor_df
                .groupby(factor_col, as_index=False)[avg_rank_col]
                .mean()
                .sort_values(avg_rank_col)
            )

            st.dataframe(
                rank_summary,
                width="stretch",
                hide_index=True,
            )

            st.caption(
                "Lower average preference rank indicates stronger preference."
            )

    else:

        st.info(
            "Decision-factor analysis data is not available."
        )

    st.divider()

    # ========================================================
    # SECTION 2 — INVESTMENT PURPOSE
    # ========================================================

    st.subheader("2. Investment Purpose")

    if not purpose_df.empty:

        purpose_col = find_column(
            purpose_df,
            [
                "Investment_Purpose",
                "Purpose",
                "Investment Purpose",
            ],
        )

        count_col = find_column(
            purpose_df,
            [
                "Unique_Respondents",
                "Respondent_Count",
                "Respondents",
                "Count",
                "Investor_Count",
            ],
        )

        investment_col = find_column(
            purpose_df,
            [
                "Investment_Type",
                "Investment Type",
            ],
        )

        avg_rank_col = find_column(
            purpose_df,
            [
                "Average_Preference_Rank",
                "Avg_Preference_Rank",
                "Average Rank",
            ],
        )

        # ----------------------------------------------------
        # Purpose distribution
        # ----------------------------------------------------

        if purpose_col and count_col:

            purpose_summary = (
                purpose_df
                .groupby(purpose_col, as_index=False)[count_col]
                .sum()
                .sort_values(count_col, ascending=False)
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "**Investment Purpose Distribution**"
                )

                chart_data = (
                    purpose_summary
                    .set_index(purpose_col)[count_col]
                )

                st.bar_chart(
                    chart_data,
                    width="stretch",
                )

            with col2:

                st.markdown(
                    "**Top Investment Purposes**"
                )

                show_dataframe(
                    purpose_summary.head(10),
                    height=300,
                )

        # ----------------------------------------------------
        # Purpose × investment type
        # ----------------------------------------------------

        if purpose_col and investment_col and count_col:

            st.markdown(
                "**Investment Type by Investment Purpose**"
            )

            pivot = purpose_df.pivot_table(
                index=purpose_col,
                columns=investment_col,
                values=count_col,
                aggfunc="sum",
                fill_value=0,
            )

            if not pivot.empty:

                st.bar_chart(
                    pivot,
                    width="stretch",
                )

        # ----------------------------------------------------
        # Purpose preference ranking
        # ----------------------------------------------------

        if purpose_col and avg_rank_col:

            st.markdown(
                "**Average Preference Rank by Purpose**"
            )

            purpose_rank = (
                purpose_df
                .groupby(purpose_col, as_index=False)[avg_rank_col]
                .mean()
                .sort_values(avg_rank_col)
            )

            show_dataframe(
                purpose_rank,
                height=250,
            )

    else:

        st.info(
            "Investment-purpose analysis data is not available."
        )

    st.divider()

    # ========================================================
    # SECTION 3 — KEY MOTIVATION
    # ========================================================

    st.subheader("3. Key Investor Motivation")

    motivation_df = pd.DataFrame()

    if not factor_df.empty:

        factor_col = find_column(
            factor_df,
            [
                "Decision_Factor",
                "Investment_Factor",
                "Factor",
            ],
        )

        count_col = find_column(
            factor_df,
            [
                "Unique_Respondents",
                "Respondent_Count",
                "Respondents",
                "Count",
            ],
        )

        if factor_col and count_col:

            motivation_df = (
                factor_df
                .groupby(factor_col, as_index=False)[count_col]
                .sum()
                .sort_values(count_col, ascending=False)
            )

    if not motivation_df.empty:

        top_factor = motivation_df.iloc[0][factor_col]
        top_count = motivation_df.iloc[0][count_col]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Top Decision Factor",
                str(top_factor),
            )

        with col2:

            st.metric(
                "Investors",
                f"{int(top_count):,}",
            )

        with col3:

            total = motivation_df[count_col].sum()

            if total > 0:

                percentage = (
                    float(top_count) / float(total) * 100
                )

                st.metric(
                    "Share",
                    f"{percentage:.1f}%",
                )

    else:

        st.info(
            "Unable to calculate the primary investor motivation."
        )

    st.divider()

    # ========================================================
    # SECTION 4 — INVESTMENT PREFERENCE CONTEXT
    # ========================================================

    st.subheader("4. Reasons Behind Investment Preferences")

    if not preference_df.empty:

        investment_col = find_column(
            preference_df,
            [
                "Investment_Type",
                "Investment Type",
            ],
        )

        avg_rank_col = find_column(
            preference_df,
            [
                "Average_Preference_Rank",
                "Avg_Preference_Rank",
                "Average Rank",
            ],
        )

        respondent_col = find_column(
            preference_df,
            [
                "Unique_Respondents",
                "Respondent_Count",
                "Respondents",
            ],
        )

        if investment_col and avg_rank_col:

            preference_display = preference_df[
                [
                    col
                    for col in [
                        investment_col,
                        respondent_col,
                        avg_rank_col,
                    ]
                    if col
                ]
            ].copy()

            preference_display = (
                preference_display
                .sort_values(
                    avg_rank_col,
                    ascending=True,
                )
            )

            st.dataframe(
                preference_display,
                width="stretch",
                hide_index=True,
            )

            st.caption(
                "Preference ranking is interpreted using ascending "
                "average rank: Rank 1 represents the strongest preference."
            )

    else:

        st.info(
            "Investment preference analysis is not available."
        )

    st.divider()

    # ========================================================
    # SECTION 5 — BUSINESS INTERPRETATION
    # ========================================================

    st.subheader("5. Business Interpretation")

    interpretation_points = []

    # Determine top factor
    if not motivation_df.empty:

        top_factor = str(
            motivation_df.iloc[0][factor_col]
        )

        interpretation_points.append(
            f"**{top_factor}** is the strongest observed "
            "investment decision factor in the available survey data."
        )

    # Determine top purpose
    if not purpose_df.empty:

        purpose_col_tmp = find_column(
            purpose_df,
            [
                "Investment_Purpose",
                "Purpose",
                "Investment Purpose",
            ],
        )

        count_col_tmp = find_column(
            purpose_df,
            [
                "Unique_Respondents",
                "Respondent_Count",
                "Respondents",
                "Count",
            ],
        )

        if purpose_col_tmp and count_col_tmp:

            tmp = (
                purpose_df
                .groupby(
                    purpose_col_tmp,
                    as_index=False,
                )[count_col_tmp]
                .sum()
                .sort_values(
                    count_col_tmp,
                    ascending=False,
                )
            )

            if not tmp.empty:

                top_purpose = str(
                    tmp.iloc[0][purpose_col_tmp]
                )

                interpretation_points.append(
                    f"**{top_purpose}** is the most common "
                    "investment purpose among respondents."
                )

    # Preference interpretation
    if not preference_df.empty:

        investment_col_tmp = find_column(
            preference_df,
            [
                "Investment_Type",
                "Investment Type",
            ],
        )

        rank_col_tmp = find_column(
            preference_df,
            [
                "Average_Preference_Rank",
                "Avg_Preference_Rank",
                "Average Rank",
            ],
        )

        if investment_col_tmp and rank_col_tmp:

            tmp = (
                preference_df
                .sort_values(
                    rank_col_tmp,
                    ascending=True,
                )
            )

            if not tmp.empty:

                top_investment = str(
                    tmp.iloc[0][investment_col_tmp]
                )

                interpretation_points.append(
                    f"**{top_investment}** has the strongest "
                    "overall preference based on the lowest "
                    "average preference rank."
                )

    if interpretation_points:

        for point in interpretation_points:

            st.markdown(
                f"• {point}"
            )

    else:

        st.info(
            "Not enough analytical data is available to generate "
            "business interpretation."
        )


# ============================================================
# STREAMLIT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    render()