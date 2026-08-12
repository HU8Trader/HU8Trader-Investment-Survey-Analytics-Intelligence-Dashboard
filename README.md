# Investment Survey Analytics & Intelligence Dashboard

> A complete end-to-end investment survey analytics project built with Python, Pandas, data validation, analytical modeling, and Streamlit.

---

## Project Overview

The **Investment Survey Analytics & Intelligence Dashboard** is an end-to-end data analytics project designed to transform raw investment survey data into structured analytical insights and business recommendations.

The project follows a professional analytics workflow:

**Raw Data → Data Preparation → Analytical Modeling → Validation → Business Insights → Interactive Dashboard → Recommendations**

The objective is not simply to visualize the survey data, but to build a reliable analytical system that answers important business questions around:

- Investor demographics
- Investment preferences
- Investment behaviour
- Expected returns
- Investment objectives
- Decision factors
- Savings objectives
- Investment monitoring
- Gender-based investment patterns
- Young investor behaviour
- Female investor preferences
- Bond preferences
- Business recommendations

---

# Key Objectives

The project was developed to answer questions such as:

1. What investment options are most preferred by investors?
2. How do investment preferences differ by gender?
3. How do younger investors behave differently?
4. Which investment objectives are most common?
5. What factors influence investment decisions?
6. Which investment options are preferred by female investors?
7. How strong is the preference for equity among young investors?
8. How are bonds positioned across investor segments?
9. What expected return ranges are most common?
10. What savings objectives influence investment decisions?
11. How frequently do investors monitor their investments?
12. What business strategies can be derived from the analysis?

---

# Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data analysis and application development |
| Pandas | Data manipulation and analytical processing |
| NumPy | Numerical operations |
| Streamlit | Interactive dashboard |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| CSV | Data exchange and analytical outputs |
| Git/GitHub | Version control and project documentation |

---

# Project Architecture

```text
Investment Survey Analytics
│
├── data/
│   ├── raw/
│   │   └── investment_survey.csv
│   │
│   ├── processed/
│   │   ├── respondent_data.csv
│   │   └── investment_data.csv
│   │
│   ├── analysis/
│   │   ├── investment_preference_analysis.csv
│   │   ├── gender_investment_analysis.csv
│   │   ├── age_investment_analysis.csv
│   │   ├── objective_investment_analysis.csv
│   │   ├── female_investment_preference.csv
│   │   ├── young_investor_preference.csv
│   │   ├── bond_preference_analysis.csv
│   │   ├── gender_preference_gap.csv
│   │   ├── purpose_investment_analysis.csv
│   │   ├── factor_investment_analysis.csv
│   │   ├── duration_investment_analysis.csv
│   │   ├── expected_return_analysis.csv
│   │   ├── savings_investment_analysis.csv
│   │   ├── source_investment_analysis.csv
│   │   └── monitoring_investment_analysis.csv
│   │
│   └── validation/
│       ├── validation_report.csv
│       ├── validation_results.csv
│       ├── schema_validation.csv
│       ├── grain_validation.csv
│       ├── key_validation.csv
│       ├── preference_validation.csv
│       ├── category_validation.csv
│       ├── output_validation.csv
│       ├── business_rule_validation.csv
│       ├── data_quality_validation.csv
│       └── validation_errors.csv
│
├── src/
│   └── 08/
│       └── validation.py
│
├── dashboard/
│   ├── app.py
│   ├── layout.py
│   ├── components.py
│   ├── filters.py
│   │
│   └── pages/
│       ├── executive.py
│       ├── demographics.py
│       ├── preference.py
│       ├── behaviour.py
│       ├── reasons.py
│       ├── savings.py
│       └── recommendations.py
│
├── requirements.txt
├── README.md
└── .gitignore
