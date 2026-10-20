import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import os
import textwrap

sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
OUTPUT_DIR = 'factor_analysis/outputs/factor'
os.makedirs(OUTPUT_DIR, exist_ok=True)

df_coeff = pd.read_csv('factor_analysis/outputs/factor_coefficients.csv')
df_comp = pd.read_csv('factor_analysis/outputs/factor_model_comparison.csv')
key_assets = ['GROWTH_FROZEN_SAMPLE_MV', 'REJECTED_MIN_VARIANCE', 'AAPL', 'MSFT', 'JNJ', 'PG']

# Hàm tự động xuống dòng và để chữ nằm ngang
def wrap_labels(ax, width=15):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        # Ép xuống dòng cố định cho 2 tên quá dài
        text = text.replace('GROWTH_FROZEN_SAMPLE_MV', 'GROWTH_FROZEN\nSAMPLE_MV')
        text = text.replace('REJECTED_MIN_VARIANCE', 'REJECTED\nMIN_VARIANCE')
        labels.append(textwrap.fill(text, width=width))
    # Chỉnh rotation=0 để chữ nằm ngang hoàn toàn
    ax.set_xticklabels(labels, rotation=0, fontsize=10)

# Chart 1: Factor Exposures
df_ff3 = df_coeff[(df_coeff['model'] == 'FF3') & (df_coeff['strategy_or_ticker'].isin(key_assets))]
fig1, ax1 = plt.subplots(figsize=(12, 6))
df_melted_beta = df_ff3.melt(id_vars='strategy_or_ticker', value_vars=['Mkt_RF', 'SMB', 'HML'], var_name='Factor', value_name='Coefficient')
sns.barplot(data=df_melted_beta, x='strategy_or_ticker', y='Coefficient', hue='Factor', ax=ax1, palette='Set2')
ax1.set_title('Figure 1: Factor Exposures (Mkt-RF, SMB, HML) under FF3', fontsize=14, fontweight='bold')
ax1.set_ylabel('Coefficient (Beta)')
ax1.set_xlabel('')
ax1.axhline(0, color='black', linewidth=1)
wrap_labels(ax1) # Gọi hàm chỉnh format
plt.tight_layout()
fig1.savefig(os.path.join(OUTPUT_DIR, '01_factor_exposures_update.png'), dpi=300)

# Chart 2: Alpha Disappearance
df_alpha_comp = df_comp[df_comp['strategy_or_ticker'].isin(key_assets)].copy()
df_alpha_comp['Annualized CAPM Alpha'] = df_alpha_comp['alpha_capm'] * 12
df_alpha_comp['Annualized FF3 Alpha'] = df_alpha_comp['alpha_ff3'] * 12
fig2, ax2 = plt.subplots(figsize=(10, 6))
df_melted_alpha = df_alpha_comp.melt(id_vars='strategy_or_ticker', value_vars=['Annualized CAPM Alpha', 'Annualized FF3 Alpha'], var_name='Model', value_name='Annualized Alpha')
sns.barplot(data=df_melted_alpha, x='strategy_or_ticker', y='Annualized Alpha', hue='Model', ax=ax2, palette='magma')
ax2.set_title('Figure 2: Alpha Disappearance (CAPM vs FF3)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Annualized Alpha')
ax2.set_xlabel('')
wrap_labels(ax2) # Gọi hàm chỉnh format
plt.tight_layout()
fig2.savefig(os.path.join(OUTPUT_DIR, '02_alpha_disappearance.png'), dpi=300)

# Chart 3: R-Squared
fig3, ax3 = plt.subplots(figsize=(10, 6))
df_melted_r2 = df_comp[df_comp['strategy_or_ticker'].isin(key_assets)].melt(id_vars='strategy_or_ticker', value_vars=['r2_adj_capm', 'r2_adj_ff3'], var_name='Model', value_name='Adjusted R-Squared')
df_melted_r2['Model'] = df_melted_r2['Model'].replace({'r2_adj_capm': 'CAPM', 'r2_adj_ff3': 'FF3'})
sns.lineplot(data=df_melted_r2, x='strategy_or_ticker', y='Adjusted R-Squared', hue='Model', marker='o', markersize=10, linewidth=2, ax=ax3, palette='dark')
ax3.set_title('Figure 3: Explanatory Power (Adjusted R²)', fontsize=14, fontweight='bold')
ax3.set_ylim(0.2, 1.0)
ax3.set_xlabel('')
wrap_labels(ax3) # Gọi hàm chỉnh format
plt.tight_layout()
fig3.savefig(os.path.join(OUTPUT_DIR, '03_rsquared_comparison.png'), dpi=300)

# Chart 4: Scatter Plot
df_returns = pd.read_csv('portfolio_construction/outputs/growth_static_exposure_returns.csv')
df_returns['month'] = pd.to_datetime(df_returns['month']).dt.to_period('M')
with zipfile.ZipFile('factor_analysis/data/raw/french/F-F_Research_Data_Factors_CSV.zip', 'r') as z:
    csv_name = z.namelist()[0]
    with z.open(csv_name) as f:
        df_french = pd.read_csv(f, skiprows=3)
        df_french.rename(columns={df_french.columns[0]: 'month'}, inplace=True)
        df_french = df_french[df_french['month'].apply(lambda x: str(x).isnumeric())].copy()
        df_french['month'] = pd.to_datetime(df_french['month'], format='%Y%m').dt.to_period('M')
        df_french[['Mkt-RF', 'SMB', 'HML', 'RF']] = df_french[['Mkt-RF', 'SMB', 'HML', 'RF']].astype(float) / 100
df_merged = pd.merge(df_returns, df_french, on='month', how='inner')
port_ff3 = df_coeff[(df_coeff['model'] == 'FF3') & (df_coeff['strategy_or_ticker'] == 'GROWTH_FROZEN_SAMPLE_MV')].iloc[0]
predicted_excess = (port_ff3['alpha'] + port_ff3['Mkt_RF'] * df_merged['Mkt-RF'] + port_ff3['SMB'] * df_merged['SMB'] + port_ff3['HML'] * df_merged['HML'])
df_merged['Predicted_Return'] = predicted_excess + df_merged['RF']
df_merged['Actual_Return'] = df_merged['growth_static_exposure_monthly']

fig4, ax4 = plt.subplots(figsize=(8, 8))
sns.scatterplot(x='Predicted_Return', y='Actual_Return', data=df_merged, alpha=0.8, color='teal', edgecolor='black', s=60, ax=ax4)
min_val = min(df_merged['Predicted_Return'].min(), df_merged['Actual_Return'].min())
max_val = max(df_merged['Predicted_Return'].max(), df_merged['Actual_Return'].max())
ax4.plot([min_val, max_val], [min_val, max_val], color='red', linestyle='--', linewidth=2, label='Perfect Prediction (Actual = Predicted)')
ax4.set_title(f"Figure 4: Actual vs. FF3 Predicted Returns\n(Growth Portfolio, R² = {port_ff3['r2']:.2f})", fontsize=14, fontweight='bold')
ax4.set_xlabel('Predicted Returns')
ax4.set_ylabel('Actual Returns')
ax4.legend()
plt.tight_layout()
fig4.savefig(os.path.join(OUTPUT_DIR, '04_actual_vs_predicted.png'), dpi=300)

print("Xong! 4 hinh da duoc tao lai voi truc X nam ngang va xuong dong gon gang.")
