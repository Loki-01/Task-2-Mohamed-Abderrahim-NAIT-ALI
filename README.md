# Exploratory Data Analysis — E-Commerce Order Dataset

**DecodeLabs Data Analytics Internship · Task 2**
**Author:** Mohamed Abderrahim NAIT ALI

---

## Overview

End-to-end exploratory data analysis on an e-commerce order dataset containing **1,200 records** spanning **January 2023 to June 2025**. The analysis covers data validation, descriptive statistics, outlier detection, trend analysis, segment breakdowns, and correlation profiling — with all findings reproduced programmatically and exported as publication-ready charts.

---

## Repository Structure

```
├── eda_analysis.py      # Full analysis script (210 lines)
├── EDA_Report.pdf       # Written report with findings and interpretations
├── dataset.xlsx         # Source data (place in root before running)
└── charts/              # Auto-generated output folder
    ├── 01_totalprice_dist.png
    ├── 02_totalprice_box.png
    ├── 03_monthly_trend.png
    ├── 04_revenue_by_product.png
    ├── 05_order_status.png
    ├── 06_correlation.png
    └── 07_revenue_referral.png
```

---

## Dataset

| Property | Value |
|---|---|
| Records | 1,200 orders |
| Period | Jan 2023 – Jun 2025 |
| Format | Excel (.xlsx) |
| Key columns | OrderID, Date, Product, Quantity, UnitPrice, TotalPrice, OrderStatus, PaymentMethod, ReferralSource, CouponCode, ItemsInCart |

**Integrity check:** TotalPrice is validated against `Quantity × UnitPrice` on load. Missing CouponCode values are treated as structural (no coupon applied), not as data gaps.

---

## Analysis Sections

### 1. Load & Validate
- Shape check, date range confirmation
- Missing value audit
- Internal consistency check: `|Quantity × UnitPrice − TotalPrice|` max deviation
- Coupon flag engineering: `HasCoupon` boolean column

### 2. Descriptive Statistics
Five-number summary + mean, std, and skewness for all four numeric fields:

| Field | Description |
|---|---|
| Quantity | Units per order |
| UnitPrice | Price per unit |
| ItemsInCart | Cart size at time of order |
| TotalPrice | Final order value |

### 3. Outlier Detection
Two complementary methods applied to all numeric columns:

- **IQR rule** — flags values outside `[Q1 − 1.5×IQR, Q3 + 1.5×IQR]`
- **Z-score rule** — flags values with `|z| > 3.0`

Flagged TotalPrice orders are printed for manual review with full order context.

### 4. Trend Analysis
- Monthly aggregation: order count and revenue per month
- Year-over-year comparison (note: 2025 is partial through June)

### 5. Segment Analysis
| Dimension | Metric |
|---|---|
| Product category | Orders, total revenue, average order value |
| Order status | Count, revenue, % of total — Cancelled and Returned flagged as at-risk |
| Payment method | Count, mean, sum |
| Referral source | Count, mean, sum |
| Coupon usage | Order count, mean and median order value (with vs. without coupon) |

### 6. Correlation Analysis
Pearson correlation matrix across all four numeric fields. Identifies linear relationships between cart size, quantity, unit price, and total order value.

### 7. Charts
Seven charts auto-saved to `./charts/` at 150 dpi:

| File | Content |
|---|---|
| `01_totalprice_dist.png` | Histogram of order value with mean/median lines |
| `02_totalprice_box.png` | Horizontal boxplot for IQR-based outlier visualization |
| `03_monthly_trend.png` | Dual-axis line chart: monthly revenue and order volume |
| `04_revenue_by_product.png` | Horizontal bar chart: total revenue by product category |
| `05_order_status.png` | Bar chart: order status distribution (at-risk statuses highlighted) |
| `06_correlation.png` | Annotated heatmap of the numeric correlation matrix |
| `07_revenue_referral.png` | Horizontal bar chart: total revenue by referral source |

---

## How to Run

**Requirements**
```bash
pip install pandas numpy scipy matplotlib openpyxl
```

**Execution**
```bash
# Place dataset.xlsx in the same directory as eda_analysis.py
python eda_analysis.py
```

All console output (statistics, outlier tables, segment breakdowns) prints to stdout. All charts are written to `./charts/`.

---

## Key Findings

Refer to `EDA_Report.pdf` for the full written analysis. High-level takeaways:

- At-risk revenue from Cancelled and Returned orders quantified as a percentage of total revenue
- Monthly trend shows seasonal patterns in both order volume and revenue
- Coupon usage measurably impacts average order value
- Referral source breakdown reveals the highest-value acquisition channels
- IQR outlier detection on TotalPrice surfaces orders warranting manual review

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| pandas | Data loading, transformation, aggregation |
| numpy | Numerical operations |
| scipy.stats | Skewness computation |
| matplotlib | Chart generation |
| openpyxl | Excel file reading |

---

## Author

**Mohamed Abderrahim NAIT ALI**
Energy and Mechanical Engineer · Data Scientist
USTHB Algeria · GomyCode Data Science Bootcamp · DecodeLabs Batch 2026

GitHub: [github.com/Loki-01](https://github.com/Loki-01)
LinkedIn: [linkedin.com/in/nait-ali-mohamed-abderrahim-663a202a5](https://linkedin.com/in/nait-ali-mohamed-abderrahim-663a202a5)
