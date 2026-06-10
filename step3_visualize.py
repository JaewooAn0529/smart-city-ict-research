"""
STEP 3: 시각화 — 논문용 그래프 생성
========================================================
총 3개의 그래프를 생성합니다:
  Figure 1: 국가별 ICT 인프라 성장 추이 (꺾은선 그래프)
  Figure 2: ICT vs. GDP 성장률 산점도 + 회귀선
  Figure 3: 국가별 상관계수 비교 막대그래프

모든 그래프는 research_figures.png 로 저장됩니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── 스타일 설정 (학술 논문용) ──────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150,
    'axes.grid': True,
    'grid.alpha': 0.3
})

COUNTRY_COLORS = {
    'United Arab Emirates': '#006400',   # UAE green
    'Singapore':            '#D4001A',   # Singapore red
    'South Korea':          '#003478',   # Korea blue
    'Germany':              '#FFCE00',   # Germany yellow
    'Saudi Arabia':         '#006C35',   # Saudi green (darker)
}

COUNTRY_SHORT = {
    'United Arab Emirates': 'UAE',
    'Singapore': 'Singapore',
    'South Korea': 'S. Korea',
    'Germany': 'Germany',
    'Saudi Arabia': 'Saudi Arabia'
}

def load_data():
    try:
        return pd.read_csv('data_raw.csv')
    except FileNotFoundError:
        print("❌ data_raw.csv 없음. step1_download_data.py 먼저 실행하세요.")
        exit()

def plot_ict_trends(ax, df):
    """Figure 1: 국가별 인터넷 사용자 비율 추이"""
    for country, group in df.groupby('country'):
        group = group.sort_values('year')
        color = COUNTRY_COLORS.get(country, 'gray')
        ax.plot(group['year'], group['internet_users_pct'],
                marker='o', markersize=4, linewidth=2,
                color=color, label=COUNTRY_SHORT.get(country, country))
    
    ax.set_title('Figure 1: ICT Infrastructure Proxy\n(Internet Users, % of Population)')
    ax.set_xlabel('Year')
    ax.set_ylabel('Internet Users (%)')
    ax.legend(fontsize=9, loc='lower right')
    ax.set_xlim(2009, 2023)

def plot_scatter(ax, df):
    """Figure 2: ICT vs GDP 성장률 산점도 + 회귀선"""
    for country, group in df.groupby('country'):
        color = COUNTRY_COLORS.get(country, 'gray')
        ax.scatter(group['internet_users_pct'], group['gdp_growth_pct'],
                   color=color, alpha=0.7, s=50, zorder=3,
                   label=COUNTRY_SHORT.get(country, country))
    
    # 전체 회귀선
    slope, intercept, r, p, se = stats.linregress(
        df['internet_users_pct'], df['gdp_growth_pct']
    )
    x_range = pd.Series(range(
        int(df['internet_users_pct'].min()) - 2,
        int(df['internet_users_pct'].max()) + 3
    ))
    ax.plot(x_range, slope * x_range + intercept,
            color='#333333', linewidth=1.5, linestyle='--', zorder=2, label='Regression line')
    
    # 통계 주석
    sig = "p < 0.05 ✓" if p < 0.05 else f"p = {p:.3f}"
    ax.text(0.05, 0.95,
            f"r = {r:.3f}\nR² = {r**2:.3f}\n{sig}",
            transform=ax.transAxes, fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8))
    
    ax.set_title('Figure 2: ICT Infrastructure vs. GDP Growth Rate\n(All Countries, 2010–2022)')
    ax.set_xlabel('Internet Users (% of Population)')
    ax.set_ylabel('GDP Growth Rate (Annual %)')
    ax.axhline(0, color='gray', linewidth=0.8, linestyle=':')
    ax.legend(fontsize=9)

def plot_country_correlations(ax, df):
    """Figure 3: 국가별 상관계수 막대그래프"""
    corr_data = []
    for country, group in df.groupby('country'):
        if len(group) >= 5:
            r, p = stats.pearsonr(group['internet_users_pct'], group['gdp_growth_pct'])
            corr_data.append({
                'country': COUNTRY_SHORT.get(country, country),
                'r': r,
                'p': p,
                'color': COUNTRY_COLORS.get(country, 'gray')
            })
    
    corr_df = pd.DataFrame(corr_data).sort_values('r', ascending=True)
    
    bars = ax.barh(corr_df['country'], corr_df['r'],
                   color=corr_df['color'], edgecolor='white', height=0.6)
    
    # p-value 별표 표시
    for i, (_, row) in enumerate(corr_df.iterrows()):
        sig_marker = '*' if row['p'] < 0.05 else ''
        x_pos = row['r'] + (0.02 if row['r'] >= 0 else -0.02)
        ha = 'left' if row['r'] >= 0 else 'right'
        ax.text(x_pos, i, f"{row['r']:.3f}{sig_marker}", va='center', ha=ha, fontsize=9)
    
    ax.set_title('Figure 3: Country-level Correlation\n(ICT vs. GDP Growth, * = p < 0.05)')
    ax.set_xlabel("Pearson's r")
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlim(-1, 1)

# ── 메인 실행 ─────────────────────────────────────────────────────────────────
def main():
    print("="*55)
    print("  시각화 생성 시작")
    print("="*55)
    
    df = load_data()
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(
        'Smart City ICT Infrastructure & Economic Growth\nUAE · Singapore · South Korea · Germany · Saudi Arabia (2010–2022)',
        fontsize=14, fontweight='bold', y=1.02
    )
    
    plot_ict_trends(axes[0], df)
    plot_scatter(axes[1], df)
    plot_country_correlations(axes[2], df)
    
    plt.tight_layout()
    plt.savefig('research_figures.png', bbox_inches='tight', dpi=150)
    plt.show()
    
    print("\n✅ 그래프 저장 완료: research_figures.png")
    print("👉 다음 단계: step4_write_report.py 를 실행하세요")

if __name__ == "__main__":
    main()
