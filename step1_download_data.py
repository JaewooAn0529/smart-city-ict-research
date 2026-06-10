"""
STEP 1: 세계은행(World Bank) 데이터 다운로드 및 저장
========================================================
이 코드를 실행하면 두 가지 지표의 실제 데이터를 자동으로 내려받아
'data_raw.csv' 파일로 저장합니다.

사용 지표:
- IT.NET.USER.ZS  : 인터넷 사용자 비율 (ICT 인프라 수준 proxy)
- NY.GDP.MKTP.KD.ZG : GDP 성장률 (연간 %)

비교 국가: UAE, 싱가포르, 한국, 독일, 사우디아라비아
"""

import requests
import pandas as pd

# ── 설정 ──────────────────────────────────────────────────────────────────────
COUNTRIES = {
    'AE': 'UAE',
    'SG': 'Singapore',
    'KR': 'South Korea',
    'DE': 'Germany',
    'SA': 'Saudi Arabia'
}

INDICATORS = {
    'IT.NET.USER.ZS':   'internet_users_pct',   # ICT 인프라 proxy
    'NY.GDP.MKTP.KD.ZG': 'gdp_growth_pct'       # GDP 성장률
}

YEARS = (2010, 2022)
BASE_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"

# ── 데이터 수집 함수 ──────────────────────────────────────────────────────────
def fetch_indicator(indicator_code, country_codes):
    """세계은행 API에서 특정 지표 데이터를 가져옵니다."""
    url = BASE_URL.format(
        countries=";".join(country_codes),
        indicator=indicator_code
    )
    params = {
        "date": f"{YEARS[0]}:{YEARS[1]}",
        "format": "json",
        "per_page": 500
    }
    
    print(f"  → {indicator_code} 다운로드 중...")
    response = requests.get(url, params=params, timeout=15)
    data = response.json()
    
    records = []
    for entry in data[1]:
        if entry['value'] is not None:
            records.append({
                'country_code': entry['country']['id'],
                'country':      entry['country']['value'],
                'year':         int(entry['date']),
                indicator_code: entry['value']
            })
    
    return pd.DataFrame(records)

# ── 메인 실행 ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  세계은행 데이터 다운로드 시작")
    print("=" * 55)
    
    country_codes = list(COUNTRIES.keys())
    dfs = []
    
    for code, col_name in INDICATORS.items():
        df = fetch_indicator(code, country_codes)
        df = df.rename(columns={code: col_name})
        dfs.append(df)
    
    # 두 지표를 country + year 기준으로 합치기
    merged = pd.merge(dfs[0], dfs[1], on=['country_code', 'country', 'year'])
    merged = merged.sort_values(['country', 'year']).reset_index(drop=True)
    
    # 저장
    merged.to_csv('data_raw.csv', index=False)
    
    print("\n✅ 다운로드 완료!")
    print(f"   총 {len(merged)}개 데이터 포인트")
    print(f"   국가별 데이터 수:\n{merged['country'].value_counts().to_string()}")
    print("\n   처음 5행 미리보기:")
    print(merged.head().to_string(index=False))
    print("\n👉 다음 단계: python step2_analyze.py 를 실행하세요")

if __name__ == "__main__":
    main()
