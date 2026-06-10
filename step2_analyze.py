"""
STEP 2: 통계적 상관관계 분석
========================================================
data_raw.csv 를 읽어 다음 분석을 수행합니다:
  1. 기술통계 (평균, 표준편차, min/max)
  2. 국가별 피어슨 상관계수
  3. 전체 패널 상관계수 + p-value
  4. 결과를 analysis_results.txt 로 저장
"""

import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
def load_data():
    try:
        df = pd.read_csv('data_raw.csv')
        print(f"✅ 데이터 로드 완료: {len(df)}행")
        return df
    except FileNotFoundError:
        print("❌ data_raw.csv 파일이 없습니다. step1_download_data.py 를 먼저 실행하세요.")
        exit()

# ── 분석 함수들 ───────────────────────────────────────────────────────────────
def descriptive_stats(df):
    """기술통계"""
    print("\n" + "="*55)
    print("  [1] 기술통계")
    print("="*55)
    
    stats_table = df.groupby('country')[['internet_users_pct', 'gdp_growth_pct']].agg(
        ['mean', 'std', 'min', 'max']
    ).round(2)
    print(stats_table.to_string())
    return stats_table

def country_correlations(df):
    """국가별 상관계수"""
    print("\n" + "="*55)
    print("  [2] 국가별 상관계수 (ICT ↔ GDP 성장률)")
    print("="*55)
    
    results = []
    for country, group in df.groupby('country'):
        if len(group) >= 5:
            r, p = stats.pearsonr(group['internet_users_pct'], group['gdp_growth_pct'])
            results.append({
                'Country': country,
                'Correlation (r)': round(r, 3),
                'p-value': round(p, 3),
                'Significant?': '✅ Yes' if p < 0.05 else '❌ No',
                'Interpretation': interpret_r(r)
            })
    
    result_df = pd.DataFrame(results)
    print(result_df.to_string(index=False))
    return result_df

def panel_correlation(df):
    """전체 패널 데이터 상관분석"""
    print("\n" + "="*55)
    print("  [3] 전체 패널 상관분석 (모든 국가 합산)")
    print("="*55)
    
    r, p = stats.pearsonr(df['internet_users_pct'], df['gdp_growth_pct'])
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df['internet_users_pct'], df['gdp_growth_pct']
    )
    
    print(f"  피어슨 상관계수 (r)    : {r:.3f}")
    print(f"  p-value               : {p:.4f}")
    print(f"  통계적 유의성 (p<0.05) : {'✅ 유의함' if p < 0.05 else '❌ 유의하지 않음'}")
    print(f"  R² (설명력)           : {r_value**2:.3f}")
    print(f"  회귀 기울기           : {slope:.4f}")
    print(f"\n  해석: {interpret_panel(r, p)}")
    
    return {'r': r, 'p': p, 'r2': r_value**2, 'slope': slope, 'intercept': intercept}

def interpret_r(r):
    """상관계수 해석"""
    abs_r = abs(r)
    direction = "positive" if r > 0 else "negative"
    if abs_r >= 0.7: strength = "Strong"
    elif abs_r >= 0.4: strength = "Moderate"
    else: strength = "Weak"
    return f"{strength} {direction}"

def interpret_panel(r, p):
    """패널 결과 해석 (한글)"""
    if p >= 0.05:
        return "통계적으로 유의미하지 않음 — 추가 변수 검토 필요"
    direction = "양의" if r > 0 else "음의"
    abs_r = abs(r)
    if abs_r >= 0.7:
        return f"강한 {direction} 상관관계 — ICT 인프라 수준이 높을수록 GDP 성장률이 {'높은' if r > 0 else '낮은'} 경향"
    elif abs_r >= 0.4:
        return f"중간 {direction} 상관관계 — ICT 인프라 수준이 GDP 성장률에 부분적 영향"
    else:
        return f"약한 {direction} 상관관계 — 직접적 연관성 제한적"

# ── 메인 실행 ─────────────────────────────────────────────────────────────────
def main():
    print("="*55)
    print("  통계 분석 시작")
    print("="*55)
    
    df = load_data()
    
    desc = descriptive_stats(df)
    country_corr = country_correlations(df)
    panel = panel_correlation(df)
    
    # 결과 저장
    with open('analysis_results.txt', 'w', encoding='utf-8') as f:
        f.write("=== ICT Infrastructure & GDP Growth Analysis ===\n\n")
        f.write("Countries: UAE, Singapore, South Korea, Germany, Saudi Arabia\n")
        f.write("Period: 2010–2022\n\n")
        f.write("--- Descriptive Statistics ---\n")
        f.write(desc.to_string())
        f.write("\n\n--- Country-level Correlations ---\n")
        f.write(country_corr.to_string(index=False))
        f.write(f"\n\n--- Panel Correlation ---\n")
        f.write(f"r = {panel['r']:.3f}, p = {panel['p']:.4f}, R² = {panel['r2']:.3f}\n")
    
    print("\n✅ 분석 완료! 결과가 analysis_results.txt 에 저장되었습니다.")
    print("👉 다음 단계: python step3_visualize.py 를 실행하세요")

if __name__ == "__main__":
    main()
