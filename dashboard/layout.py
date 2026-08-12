"""
Investment Survey Analytics Dashboard
=====================================

File:
    dashboard/layout.py

Purpose:
    Centralized UI/layout utilities for the Streamlit dashboard.

This module contains:
    - Global CSS
    - Dashboard header
    - Sidebar navigation
    - KPI cards
    - Section headers
    - Information / insight cards
    - Tables
    - Footer
    - Common chart configuration helpers

Usage from app.py:

    from dashboard.layout import (
        apply_dashboard_style,
        render_header,
        render_sidebar,
        render_kpi_cards,
        render_section_header,
        render_insight_card,
        render_footer,
    )
"""

from __future__ import annotations

from typing import Any, Iterable, Optional

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

APP_TITLE = "Investment Survey Analytics"
APP_SUBTITLE = "Data-driven analysis of investor preferences and behaviour"

BRAND_NAME = "HiLyst Analytics"
BRAND_TAGLINE = "Visualize. Analyze. Then Decide."

AUTHOR_NAME = "Himansh Upadhyay"


# ============================================================
# COLOR PALETTE
# ============================================================

COLORS = {
    "primary": "#2563EB",
    "primary_dark": "#1D4ED8",
    "secondary": "#0F766E",
    "accent": "#7C3AED",
    "success": "#16A34A",
    "warning": "#D97706",
    "danger": "#DC2626",
    "dark": "#111827",
    "text": "#1F2937",
    "muted": "#6B7280",
    "light": "#F3F4F6",
    "border": "#E5E7EB",
    "white": "#FFFFFF",
    "background": "#F8FAFC",
}


# ============================================================
# GLOBAL CSS
# ============================================================

def apply_dashboard_style() -> None:
    """
    Apply the complete global CSS for the dashboard.

    Call once near the beginning of app.py.
    """

    st.markdown(
        f"""
        <style>

        /* ==================================================
           GLOBAL
        ================================================== */

        .stApp {{
            background: {COLORS["background"]};
            color: {COLORS["text"]};
        }}

        .main {{
            padding-top: 1rem;
        }}

        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }}

        /* Remove unnecessary Streamlit spacing */

        div[data-testid="stVerticalBlock"] {{
            gap: 0.75rem;
        }}


        /* ==================================================
           SIDEBAR
        ================================================== */

        section[data-testid="stSidebar"] {{
            background: linear-gradient(
                180deg,
                #111827 0%,
                #172033 100%
            );
        }}

        section[data-testid="stSidebar"] * {{
            color: #F9FAFB;
        }}

        section[data-testid="stSidebar"] .stRadio label {{
            padding: 8px 10px;
            border-radius: 8px;
            transition: all 0.2s ease;
        }}

        section[data-testid="stSidebar"] .stRadio label:hover {{
            background: rgba(255,255,255,0.08);
        }}


        /* ==================================================
           DASHBOARD HEADER
        ================================================== */

        .dashboard-header {{
            background: linear-gradient(
                135deg,
                #111827 0%,
                #1E3A8A 55%,
                #2563EB 100%
            );

            padding: 28px 32px;
            border-radius: 18px;
            margin-bottom: 24px;

            box-shadow:
                0 10px 25px rgba(15, 23, 42, 0.12);
        }}

        .dashboard-header h1 {{
            color: white;
            font-size: 32px;
            font-weight: 750;
            margin: 0;
            letter-spacing: -0.5px;
        }}

        .dashboard-header p {{
            color: rgba(255,255,255,0.82);
            font-size: 15px;
            margin: 7px 0 0 0;
        }}

        .dashboard-header .brand {{
            color: #BFDBFE;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 7px;
        }}


        /* ==================================================
           SECTION HEADER
        ================================================== */

        .section-header {{
            margin-top: 22px;
            margin-bottom: 12px;
        }}

        .section-header h2 {{
            font-size: 21px;
            font-weight: 700;
            color: {COLORS["dark"]};
            margin: 0;
        }}

        .section-header p {{
            color: {COLORS["muted"]};
            font-size: 13px;
            margin-top: 4px;
        }}

        .section-line {{
            height: 3px;
            width: 48px;
            background: {COLORS["primary"]};
            border-radius: 10px;
            margin-top: 8px;
        }}


        /* ==================================================
           KPI CARDS
        ================================================== */

        .kpi-card {{
            background: {COLORS["white"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 14px;
            padding: 18px 20px;
            min-height: 118px;

            box-shadow:
                0 4px 12px rgba(15, 23, 42, 0.05);

            transition:
                transform 0.2s ease,
                box-shadow 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);

            box-shadow:
                0 8px 20px rgba(15, 23, 42, 0.09);
        }}

        .kpi-label {{
            color: {COLORS["muted"]};
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 7px;
        }}

        .kpi-value {{
            color: {COLORS["dark"]};
            font-size: 28px;
            font-weight: 750;
            line-height: 1.15;
        }}

        .kpi-description {{
            color: {COLORS["muted"]};
            font-size: 11px;
            margin-top: 6px;
        }}

        .kpi-accent {{
            width: 34px;
            height: 4px;
            background: {COLORS["primary"]};
            border-radius: 10px;
            margin-bottom: 12px;
        }}


        /* ==================================================
           INSIGHT CARD
        ================================================== */

        .insight-card {{
            background: white;
            border: 1px solid {COLORS["border"]};
            border-left: 4px solid {COLORS["primary"]};

            border-radius: 12px;
            padding: 16px 18px;
            margin: 8px 0;

            box-shadow:
                0 3px 10px rgba(15, 23, 42, 0.04);
        }}

        .insight-title {{
            font-size: 14px;
            font-weight: 700;
            color: {COLORS["dark"]};
            margin-bottom: 5px;
        }}

        .insight-text {{
            font-size: 13px;
            line-height: 1.55;
            color: {COLORS["muted"]};
        }}


        /* ==================================================
           RECOMMENDATION CARD
        ================================================== */

        .recommendation-card {{
            background: linear-gradient(
                135deg,
                #EFF6FF 0%,
                #F5F3FF 100%
            );

            border: 1px solid #DBEAFE;
            border-radius: 14px;

            padding: 18px 20px;
            margin-bottom: 12px;
        }}

        .recommendation-id {{
            color: {COLORS["primary"]};
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }}

        .recommendation-title {{
            color: {COLORS["dark"]};
            font-size: 15px;
            font-weight: 700;
            margin-top: 5px;
        }}

        .recommendation-text {{
            color: {COLORS["muted"]};
            font-size: 13px;
            line-height: 1.55;
            margin-top: 5px;
        }}


        /* ==================================================
           STATUS BADGES
        ================================================== */

        .status-pass {{
            display: inline-block;
            background: #DCFCE7;
            color: #166534;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
        }}

        .status-warning {{
            display: inline-block;
            background: #FEF3C7;
            color: #92400E;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
        }}

        .status-fail {{
            display: inline-block;
            background: #FEE2E2;
            color: #991B1B;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
        }}


        /* ==================================================
           FILTER CONTAINER
        ================================================== */

        .filter-container {{
            background: white;
            border: 1px solid {COLORS["border"]};
            border-radius: 14px;
            padding: 15px 18px;
            margin-bottom: 15px;
        }}


        /* ==================================================
           INFO BOX
        ================================================== */

        .info-box {{
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 12px;
            padding: 14px 16px;
            color: #1E40AF;
            font-size: 13px;
            line-height: 1.5;
        }}

        .warning-box {{
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            border-radius: 12px;
            padding: 14px 16px;
            color: #92400E;
            font-size: 13px;
            line-height: 1.5;
        }}


        /* ==================================================
           FOOTER
        ================================================== */

        .dashboard-footer {{
            border-top: 1px solid {COLORS["border"]};
            margin-top: 35px;
            padding-top: 18px;
            text-align: center;
            color: {COLORS["muted"]};
            font-size: 11px;
        }}

        .dashboard-footer strong {{
            color: {COLORS["text"]};
        }}


        /* ==================================================
           BUTTONS
        ================================================== */

        .stButton > button {{
            border-radius: 8px;
            border: 1px solid {COLORS["border"]};
            font-weight: 600;
        }}


        /* ==================================================
           DATAFRAME
        ================================================== */

        div[data-testid="stDataFrame"] {{
            border-radius: 12px;
            overflow: hidden;
        }}


        /* ==================================================
           MOBILE
        ================================================== */

        @media (max-width: 768px) {{

            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}

            .dashboard-header {{
                padding: 22px;
            }}

            .dashboard-header h1 {{
                font-size: 25px;
            }}

            .kpi-value {{
                font-size: 24px;
            }}
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HEADER
# ============================================================

def render_header(
    title: str = APP_TITLE,
    subtitle: str = APP_SUBTITLE,
) -> None:
    """
    Render the main dashboard header.
    """

    st.markdown(
        f"""
        <div class="dashboard-header">

            <div class="brand">
                {BRAND_NAME} · Investment Analytics
            </div>

            <h1>{title}</h1>

            <p>{subtitle}</p>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar(
    pages: Optional[Iterable[str]] = None,
    default_page: Optional[str] = None,
) -> str:
    """
    Render dashboard sidebar navigation.

    Returns:
        Selected page name.
    """

    if pages is None:
        pages = [
            "Executive Overview",
            "Investment Preferences",
            "Demographic Analysis",
            "Investment Behaviour",
            "Reasons & Decision Factors",
            "Savings Objectives",
            "Information Sources",
            "Monitoring Behaviour",
            "Executive Recommendations",
            "Data Validation",
        ]

    pages = list(pages)

    st.sidebar.markdown(
        f"""
        <div style="
            padding: 10px 5px 20px 5px;
            text-align: center;
        ">

            <div style="
                font-size: 25px;
                font-weight: 800;
                color: white;
            ">
                HiLyst
            </div>

            <div style="
                font-size: 11px;
                color: #CBD5E1;
                letter-spacing: 0.8px;
                margin-top: 3px;
            ">
                ANALYTICS
            </div>

            <div style="
                height: 1px;
                background: rgba(255,255,255,0.15);
                margin-top: 18px;
            ">
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if default_page and default_page in pages:
        default_index = pages.index(default_page)
    else:
        default_index = 0

    selected_page = st.sidebar.radio(
        "Navigation",
        pages,
        index=default_index,
        label_visibility="collapsed",
    )

    st.sidebar.markdown(
        """
        <div style="
            margin-top: 25px;
            padding: 12px;
            background: rgba(255,255,255,0.06);
            border-radius: 10px;
            font-size: 11px;
            color: #CBD5E1;
            line-height: 1.5;
        ">
            <strong>Investment Survey</strong><br>
            Analytical dashboard for understanding
            investor preferences, demographics and
            investment behaviour.
        </div>
        """,
        unsafe_allow_html=True,
    )

    return selected_page


# ============================================================
# SECTION HEADER
# ============================================================

def render_section_header(
    title: str,
    description: Optional[str] = None,
) -> None:
    """
    Render a consistent section title.
    """

    description_html = ""

    if description:
        description_html = f"""
        <p>{description}</p>
        """

    st.markdown(
        f"""
        <div class="section-header">

            <h2>{title}</h2>

            {description_html}

            <div class="section-line"></div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# KPI CARD
# ============================================================

def render_kpi_card(
    label: str,
    value: Any,
    description: Optional[str] = None,
) -> None:
    """
    Render one KPI card.
    """

    description_html = ""

    if description:
        description_html = (
            f'<div class="kpi-description">{description}</div>'
        )

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-accent"></div>

            <div class="kpi-label">
                {label}
            </div>

            <div class="kpi-value">
                {value}
            </div>

            {description_html}

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MULTIPLE KPI CARDS
# ============================================================

def render_kpi_cards(
    metrics: Iterable[dict[str, Any]],
    columns: int = 4,
) -> None:
    """
    Render multiple KPI cards.

    Example:

        render_kpi_cards([
            {
                "label": "Total Respondents",
                "value": "40",
                "description": "Unique survey participants"
            },
            {
                "label": "Investment Records",
                "value": "280",
                "description": "Investment-level observations"
            }
        ])
    """

    metrics = list(metrics)

    if not metrics:
        return

    columns = max(1, min(columns, len(metrics)))

    cols = st.columns(columns)

    for index, metric in enumerate(metrics):

        with cols[index % columns]:

            render_kpi_card(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                description=metric.get("description"),
            )


# ============================================================
# INSIGHT CARD
# ============================================================

def render_insight_card(
    title: str,
    text: str,
) -> None:
    """
    Render an analytical insight.
    """

    st.markdown(
        f"""
        <div class="insight-card">

            <div class="insight-title">
                {title}
            </div>

            <div class="insight-text">
                {text}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RECOMMENDATION CARD
# ============================================================

def render_recommendation_card(
    recommendation_id: str,
    title: str,
    text: str,
) -> None:
    """
    Render a business recommendation card.
    """

    st.markdown(
        f"""
        <div class="recommendation-card">

            <div class="recommendation-id">
                Recommendation {recommendation_id}
            </div>

            <div class="recommendation-title">
                {title}
            </div>

            <div class="recommendation-text">
                {text}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# INFO BOX
# ============================================================

def render_info_box(
    message: str,
) -> None:
    """
    Render informational message.
    """

    st.markdown(
        f"""
        <div class="info-box">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# WARNING BOX
# ============================================================

def render_warning_box(
    message: str,
) -> None:
    """
    Render warning message.
    """

    st.markdown(
        f"""
        <div class="warning-box">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DATAFRAME
# ============================================================

def render_dataframe(
    dataframe: Any,
    height: int = 400,
    hide_index: bool = True,
) -> None:
    """
    Standardized dataframe renderer.

    Uses the modern Streamlit width API.
    """

    st.dataframe(
        dataframe,
        width="stretch",
        height=height,
        hide_index=hide_index,
    )


# ============================================================
# DOWNLOAD BUTTON
# ============================================================

def render_download_button(
    dataframe: Any,
    filename: str,
    label: str = "Download CSV",
) -> None:
    """
    Render CSV download button.
    """

    csv_data = dataframe.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        width="stretch",
    )


# ============================================================
# TWO COLUMN INFORMATION
# ============================================================

def render_two_column_info(
    left_title: str,
    left_value: Any,
    right_title: str,
    right_value: Any,
) -> None:
    """
    Render two simple information blocks.
    """

    col1, col2 = st.columns(2)

    with col1:
        render_kpi_card(
            label=left_title,
            value=left_value,
        )

    with col2:
        render_kpi_card(
            label=right_title,
            value=right_value,
        )


# ============================================================
# DIVIDER
# ============================================================

def render_divider() -> None:
    """
    Render a consistent divider.
    """

    st.markdown(
        f"""
        <div style="
            height: 1px;
            background: {COLORS["border"]};
            margin: 20px 0;
        "></div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

def render_footer() -> None:
    """
    Render dashboard footer.
    """

    st.markdown(
        f"""
        <div class="dashboard-footer">

            <strong>{BRAND_NAME}</strong>
            · {BRAND_TAGLINE}

            <br>

            Investment Survey Analytics Dashboard
            · Developed by {AUTHOR_NAME}

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CHART CONFIGURATION
# ============================================================

def get_plotly_config() -> dict[str, Any]:
    """
    Return common Plotly configuration.
    """

    return {
        "displayModeBar": False,
        "responsive": True,
    }


def get_plotly_layout(
    title: Optional[str] = None,
) -> dict[str, Any]:
    """
    Return common Plotly layout configuration.
    """

    layout: dict[str, Any] = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",

        "font": {
            "family": "Arial, sans-serif",
            "color": COLORS["text"],
        },

        "margin": {
            "l": 45,
            "r": 25,
            "t": 50 if title else 20,
            "b": 45,
        },

        "hoverlabel": {
            "font": {
                "size": 12,
            }
        },
    }

    if title:
        layout["title"] = {
            "text": title,
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": COLORS["dark"],
            },
        }

    return layout


# ============================================================
# PAGE INTRO
# ============================================================

def render_page_intro(
    page_number: str,
    title: str,
    description: str,
) -> None:
    """
    Render a small page-level introduction.
    """

    st.markdown(
        f"""
        <div style="
            margin-bottom: 18px;
        ">

            <div style="
                font-size: 11px;
                font-weight: 700;
                color: {COLORS["primary"]};
                text-transform: uppercase;
                letter-spacing: 1px;
            ">
                {page_number}
            </div>

            <div style="
                font-size: 26px;
                font-weight: 750;
                color: {COLORS["dark"]};
                margin-top: 3px;
            ">
                {title}
            </div>

            <div style="
                font-size: 13px;
                color: {COLORS["muted"]};
                margin-top: 5px;
                max-width: 900px;
                line-height: 1.5;
            ">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# EMPTY STATE
# ============================================================

def render_empty_state(
    title: str = "No data available",
    message: str = "There is no analytical data available for this selection.",
) -> None:
    """
    Render a professional empty state.
    """

    st.markdown(
        f"""
        <div style="
            background: white;
            border: 1px dashed {COLORS["border"]};
            border-radius: 14px;
            padding: 35px;
            text-align: center;
            margin: 15px 0;
        ">

            <div style="
                font-size: 18px;
                font-weight: 700;
                color: {COLORS["dark"]};
            ">
                {title}
            </div>

            <div style="
                font-size: 13px;
                color: {COLORS["muted"]};
                margin-top: 7px;
            ">
                {message}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ERROR STATE
# ============================================================

def render_error_state(
    title: str = "Unable to load data",
    message: str = "An error occurred while loading the analytical output.",
) -> None:
    """
    Render a professional error state.
    """

    st.markdown(
        f"""
        <div style="
            background: #FEF2F2;
            border: 1px solid #FECACA;
            border-left: 4px solid {COLORS["danger"]};
            border-radius: 12px;
            padding: 15px 18px;
            margin: 12px 0;
        ">

            <div style="
                font-size: 14px;
                font-weight: 700;
                color: #991B1B;
            ">
                {title}
            </div>

            <div style="
                font-size: 13px;
                color: #7F1D1D;
                margin-top: 5px;
            ">
                {message}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# UTILITY: SAFE VALUE
# ============================================================

def safe_display_value(
    value: Any,
    default: str = "N/A",
) -> str:
    """
    Convert a value into a dashboard-safe display string.
    """

    if value is None:
        return default

    try:
        if hasattr(value, "empty") and value.empty:
            return default
    except Exception:
        pass

    text = str(value).strip()

    if text.lower() in {
        "",
        "nan",
        "none",
        "null",
        "na",
        "n/a",
    }:
        return default

    return text


# ============================================================
# UTILITY: FORMAT NUMBER
# ============================================================

def format_number(
    value: Any,
    decimals: int = 0,
) -> str:
    """
    Format numerical values for KPI cards.

    Examples:
        4000 -> 4,000
        12.345 -> 12.35
    """

    try:
        number = float(value)

        if decimals == 0:
            return f"{number:,.0f}"

        return f"{number:,.{decimals}f}"

    except (TypeError, ValueError):
        return safe_display_value(value)


# ============================================================
# UTILITY: FORMAT PERCENTAGE
# ============================================================

def format_percentage(
    value: Any,
    decimals: int = 1,
) -> str:
    """
    Format a percentage value.

    Example:
        42.5 -> 42.5%
    """

    try:
        number = float(value)
        return f"{number:.{decimals}f}%"

    except (TypeError, ValueError):
        return safe_display_value(value)


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "APP_TITLE",
    "APP_SUBTITLE",
    "BRAND_NAME",
    "BRAND_TAGLINE",
    "AUTHOR_NAME",
    "COLORS",

    "apply_dashboard_style",
    "render_header",
    "render_sidebar",
    "render_section_header",

    "render_kpi_card",
    "render_kpi_cards",

    "render_insight_card",
    "render_recommendation_card",

    "render_info_box",
    "render_warning_box",

    "render_dataframe",
    "render_download_button",

    "render_two_column_info",
    "render_divider",

    "render_footer",

    "get_plotly_config",
    "get_plotly_layout",

    "render_page_intro",
    "render_empty_state",
    "render_error_state",

    "safe_display_value",
    "format_number",
    "format_percentage",
]