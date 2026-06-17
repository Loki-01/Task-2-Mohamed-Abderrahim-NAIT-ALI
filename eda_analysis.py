"""
Project 2 — Exploratory Data Analysis
E-Commerce Order Dataset (1,200 records, Jan 2023 - Jun 2025)

Reproduces every statistic and chart referenced in EDA_Report.pdf.
Run: python eda_analysis.py  (expects dataset.xlsx in the same folder)
"""
import pandas as pd
import numpy as np
from scipy.stats import skew
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

# --------------------------------------------------------------------------
# 1. LOAD & VALIDATE
# --------------------------------------------------------------------------
df = pd.read_excel('dataset.xlsx')

print(f"Shape: {df.shape}")
print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")

# Internal consistency check: TotalPrice should equal Quantity * UnitPrice
calc_total = df['Quantity'] * df['UnitPrice']
max_diff = (calc_total - df['TotalPrice']).abs().max()
print(f"\nMax |Quantity*UnitPrice - TotalPrice| = {max_diff:.2e}  (should be ~0)")

# Treat missing CouponCode as a structural "no coupon applied" flag, not a gap
df['HasCoupon'] = df['CouponCode'].notna()

# --------------------------------------------------------------------------
# 2. DESCRIPTIVE STATISTICS
# --------------------------------------------------------------------------
NUMERIC = ['Quantity', 'UnitPrice', 'ItemsInCart', 'TotalPrice']

def five_number_summary(s: pd.Series) -> dict:
    return {
        'count': s.count(), 'mean': s.mean(), 'median': s.median(),
        'std': s.std(), 'min': s.min(), 'q1': s.quantile(.25),
        'q3': s.quantile(.75), 'max': s.max(), 'skew': skew(s)
    }

print("\n--- Descriptive statistics ---")
desc = pd.DataFrame({col: five_number_summary(df[col]) for col in NUMERIC}).round(2)
print(desc)

# --------------------------------------------------------------------------
# 3. OUTLIER DETECTION — IQR rule and Z-score rule
# --------------------------------------------------------------------------
def iqr_outliers(s: pd.Series, k: float = 1.5):
    q1, q3 = s.quantile(.25), s.quantile(.75)
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return s[(s < lo) | (s > hi)], lo, hi

def zscore_outliers(s: pd.Series, threshold: float = 3.0):
    z = (s - s.mean()) / s.std()
    return s[z.abs() > threshold]

print("\n--- Outlier detection ---")
for col in NUMERIC:
    out_iqr, lo, hi = iqr_outliers(df[col])
    out_z = zscore_outliers(df[col])
    print(f"{col}: IQR outliers={len(out_iqr)} (fence=[{lo:.2f}, {hi:.2f}]) | "
          f"Z-score outliers={len(out_z)}")

flagged = df.loc[iqr_outliers(df['TotalPrice'])[0].index]
print("\nManual review of IQR-flagged TotalPrice orders:")
print(flagged[['OrderID', 'Product', 'Quantity', 'UnitPrice', 'TotalPrice', 'OrderStatus']])

# --------------------------------------------------------------------------
# 4. TREND ANALYSIS
# --------------------------------------------------------------------------
df['YearMonth'] = df['Date'].dt.to_period('M')
monthly = df.groupby('YearMonth').agg(
    orders=('OrderID', 'count'), revenue=('TotalPrice', 'sum')
).reset_index()

print("\n--- Year-over-year (note: 2025 is partial, through June) ---")
df['Year'] = df['Date'].dt.year
print(df.groupby('Year')['TotalPrice'].agg(['count', 'sum', 'mean']).round(2))

# --------------------------------------------------------------------------
# 5. SEGMENT ANALYSIS
# --------------------------------------------------------------------------
print("\n--- Revenue & AOV by Product ---")
print(df.groupby('Product').agg(orders=('OrderID', 'count'),
                                  revenue=('TotalPrice', 'sum'),
                                  avg_order=('TotalPrice', 'mean')).round(2)
      .sort_values('revenue', ascending=False))

print("\n--- Order status (fulfillment health) ---")
status = df.groupby('OrderStatus').agg(orders=('OrderID', 'count'),
                                         revenue=('TotalPrice', 'sum'))
status['pct_orders'] = (status['orders'] / len(df) * 100).round(1)
status['pct_revenue'] = (status['revenue'] / df['TotalPrice'].sum() * 100).round(1)
print(status.round(2))

at_risk = df[df['OrderStatus'].isin(['Cancelled', 'Returned'])]
print(f"\nAt-risk revenue (Cancelled+Returned): ${at_risk['TotalPrice'].sum():,.2f} "
      f"({at_risk['TotalPrice'].sum() / df['TotalPrice'].sum() * 100:.1f}% of total)")

print("\n--- Revenue by Payment Method ---")
print(df.groupby('PaymentMethod')['TotalPrice'].agg(['count', 'mean', 'sum']).round(2))

print("\n--- Revenue by Referral Source ---")
print(df.groupby('ReferralSource')['TotalPrice'].agg(['count', 'mean', 'sum']).round(2))

print("\n--- Coupon effect on order value ---")
print(df.groupby('HasCoupon')['TotalPrice'].agg(['count', 'mean', 'median']).round(2))

# --------------------------------------------------------------------------
# 6. CORRELATION ANALYSIS
# --------------------------------------------------------------------------
print("\n--- Correlation matrix (numeric fields) ---")
print(df[NUMERIC].corr().round(3))

# --------------------------------------------------------------------------
# 7. CHARTS (saved to ./charts/)
# --------------------------------------------------------------------------
import os
os.makedirs('charts', exist_ok=True)
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
ACCENT, ACCENT2, GREY = '#2563eb', '#f97316', '#6b7280'

# Distribution
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.hist(df['TotalPrice'], bins=30, color=ACCENT, alpha=0.85, edgecolor='white')
ax.axvline(df['TotalPrice'].mean(), color=ACCENT2, linestyle='--', linewidth=2,
           label=f"Mean: ${df['TotalPrice'].mean():.0f}")
ax.axvline(df['TotalPrice'].median(), color='#16a34a', linestyle='--', linewidth=2,
           label=f"Median: ${df['TotalPrice'].median():.0f}")
ax.set_title('Distribution of Order Value (TotalPrice)', fontweight='bold')
ax.set_xlabel('Total Price ($)'); ax.set_ylabel('Number of Orders'); ax.legend()
plt.tight_layout(); plt.savefig('charts/01_totalprice_dist.png', dpi=150); plt.close()

# Boxplot
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.boxplot(df['TotalPrice'], vert=False, patch_artist=True,
           boxprops=dict(facecolor=ACCENT, alpha=0.6),
           medianprops=dict(color=ACCENT2, linewidth=2),
           flierprops=dict(marker='o', markerfacecolor='red', markersize=6, alpha=0.7))
ax.set_title('Boxplot of Order Value — Outlier Detection (IQR Method)', fontweight='bold')
ax.set_xlabel('Total Price ($)'); ax.set_yticks([])
plt.tight_layout(); plt.savefig('charts/02_totalprice_box.png', dpi=150); plt.close()

# Monthly trend
monthly['dt'] = monthly['YearMonth'].dt.to_timestamp()
fig, ax1 = plt.subplots(figsize=(9, 4.2))
ax1.plot(monthly['dt'], monthly['revenue'], color=ACCENT, marker='o', markersize=4,
         linewidth=2, label='Revenue')
ax1.set_ylabel('Monthly Revenue ($)', color=ACCENT); ax1.tick_params(axis='y', labelcolor=ACCENT)
ax2 = ax1.twinx()
ax2.plot(monthly['dt'], monthly['orders'], color=ACCENT2, marker='s', markersize=4,
         linewidth=2, linestyle='--', label='Orders')
ax2.set_ylabel('Order Count', color=ACCENT2); ax2.tick_params(axis='y', labelcolor=ACCENT2)
ax1.set_title('Monthly Revenue & Order Volume Trend', fontweight='bold')
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
plt.tight_layout(); plt.savefig('charts/03_monthly_trend.png', dpi=150); plt.close()

# Revenue by product
prod = df.groupby('Product')['TotalPrice'].sum().sort_values()
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.barh(prod.index, prod.values, color=ACCENT)
ax.set_title('Total Revenue by Product Category', fontweight='bold'); ax.set_xlabel('Revenue ($)')
for i, v in enumerate(prod.values):
    ax.text(v + 2000, i, f'${v:,.0f}', va='center', fontsize=9, color=GREY)
plt.tight_layout(); plt.savefig('charts/04_revenue_by_product.png', dpi=150); plt.close()

# Order status
status_counts = df['OrderStatus'].value_counts()
fig, ax = plt.subplots(figsize=(7, 4.2))
colors_ = [ACCENT2 if s in ['Cancelled', 'Returned'] else ACCENT for s in status_counts.index]
bars = ax.bar(status_counts.index, status_counts.values, color=colors_)
ax.set_title('Order Status Distribution (Cancelled/Returned highlighted)', fontweight='bold')
ax.set_ylabel('Number of Orders')
for b, v in zip(bars, status_counts.values):
    ax.text(b.get_x() + b.get_width() / 2, v + 3, str(v), ha='center')
plt.tight_layout(); plt.savefig('charts/05_order_status.png', dpi=150); plt.close()

# Correlation heatmap
corr = df[NUMERIC].corr()
fig, ax = plt.subplots(figsize=(5.5, 4.8))
im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(len(corr.columns))); ax.set_xticklabels(corr.columns, rotation=45, ha='right')
ax.set_yticks(range(len(corr.columns))); ax.set_yticklabels(corr.columns)
for i in range(len(corr.columns)):
    for j in range(len(corr.columns)):
        ax.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center',
                 color='white' if abs(corr.iloc[i, j]) > 0.5 else 'black')
ax.set_title('Correlation Matrix — Numeric Variables', fontweight='bold')
fig.colorbar(im, ax=ax, shrink=0.8)
plt.tight_layout(); plt.savefig('charts/06_correlation.png', dpi=150); plt.close()

# Revenue by referral source
ref = df.groupby('ReferralSource')['TotalPrice'].sum().sort_values()
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.barh(ref.index, ref.values, color=ACCENT)
ax.set_title('Total Revenue by Referral Source', fontweight='bold'); ax.set_xlabel('Revenue ($)')
for i, v in enumerate(ref.values):
    ax.text(v + 2000, i, f'${v:,.0f}', va='center', fontsize=9, color=GREY)
plt.tight_layout(); plt.savefig('charts/07_revenue_referral.png', dpi=150); plt.close()

print("\nAll charts saved to ./charts/")
print("Analysis complete.")
