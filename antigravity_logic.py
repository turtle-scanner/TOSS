import pandas as pd
import numpy as np

def check_dry_up(df, days=3, threshold=0.5):
    """
    Dry-up Logic: 최근 N일 평균 거래량 대비 현재 거래량이 현저히 줄었는지 체크
    (VCP 패턴의 수렴 단계에서 거래량이 말라붙는 현상을 포착)
    """
    if len(df) < days + 1:
        return False, 0.0
    
    avg_vol = df['Volume'].iloc[-(days+1):-1].mean()
    curr_vol = df['Volume'].iloc[-1]
    
    ratio = curr_vol / avg_vol if avg_vol > 0 else 1.0
    is_dry = ratio <= threshold
    
    return is_dry, ratio

def check_tightness(df, threshold=0.02):
    """
    Tightness Logic: 고가와 저가의 변동폭이 좁아지는 구간 필터링
    (주가가 좁은 박스권에서 움직이며 에너지를 응축하는 단계)
    """
    if len(df) < 1:
        return False, 0.0
    
    last_row = df.iloc[-1]
    range_ratio = (last_row['High'] - last_row['Low']) / last_row['Close']
    
    is_tight = range_ratio <= threshold
    
    return is_tight, range_ratio

def calculate_rs_score(ticker_df, benchmark_df):
    """
    RS 지수 (Relative Strength): 벤치마크(예: S&P500) 대비 종목의 상대적 강도 계산
    최근 1년 수익률에 가중치를 두는 Minervini/IBD 스타일
    """
    if len(ticker_df) < 20 or len(benchmark_df) < 20:
        return 0.0
    
    ticker_return = (ticker_df['Close'].iloc[-1] / ticker_df['Close'].iloc[0]) - 1
    bench_return = (benchmark_df['Close'].iloc[-1] / benchmark_df['Close'].iloc[0]) - 1
    
    # 단순화된 RS: 벤치마크 대비 초과 수익률
    rs_score = (ticker_return - bench_return) * 100
    return round(rs_score, 2)

def check_episodic_pivot(df, vol_threshold=9000000, price_change_threshold=0.04):
    """
    EP (Episodic Pivot) 감지: 
    1. 거래량 폭발 (900만 주 이상 또는 평균 대비 3배 이상)
    2. 강력한 가격 돌파 (4% 이상 갭상승 또는 장대양봉)
    """
    if len(df) < 2:
        return False, {}

    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    avg_vol = df['Volume'].iloc[-21:-1].mean() # 20일 평균 거래량
    vol_ratio = curr['Volume'] / avg_vol if avg_vol > 0 else 1.0
    price_change = (curr['Close'] / prev['Close']) - 1
    
    is_ep = (curr['Volume'] >= vol_threshold or vol_ratio >= 3.0) and (price_change >= price_change_threshold)
    
    # [ 추가 ] 3일 연속 상승 여부 (추격 매수 금지)
    recent_closes = df['Close'].iloc[-3:].values
    is_3_day_up = (recent_closes[2] > recent_closes[1]) and (recent_closes[1] > recent_closes[0]) if len(recent_closes) == 3 else False

    return is_ep, {
        "vol_ratio": round(vol_ratio, 2),
        "price_change": round(price_change * 100, 2),
        "total_volume": int(curr['Volume']),
        "is_chasing": is_3_day_up,
        "lod": curr['Low']
    }

def analyze_antigravity(ticker, df, benchmark_df=None):
    """
    종합 안티그래비티 로직: Dry-up, Tightness, RS, EP 통합 분석
    """
    is_dry, dry_ratio = check_dry_up(df)
    is_tight, tight_ratio = check_tightness(df)
    is_ep, ep_data = check_episodic_pivot(df)
    
    rs_score = calculate_rs_score(df, benchmark_df) if benchmark_df is not None else 0.0
    
    # 본데의 추격 매수 금지 룰 적용
    is_chasing = ep_data.get('is_chasing', False)
    
    score = 0
    if is_dry: score += 25
    if is_tight: score += 25
    if is_ep: score += 50
    if rs_score > 0: score += 10 # RS 가점
    
    # 추격 매수 시 점수 삭감 또는 경고
    if is_chasing:
        action = "DO NOT CHASE"
    else:
        action = "STRONG BUY" if is_ep and is_tight else ("WATCH" if score >= 50 else "IGNORE")
    
    return {
        "ticker": ticker,
        "is_dry": is_dry,
        "dry_ratio": round(dry_ratio, 2),
        "is_tight": is_tight,
        "tight_ratio": round(tight_ratio, 4),
        "is_ep": is_ep,
        "ep_data": ep_data,
        "rs_score": rs_score,
        "score": score,
        "action": action,
        "lod": ep_data.get('lod', 0)
    }

# 예제 사용법:
# import yfinance as yf
# df = yf.download("AAPL", period="10d")
# result = analyze_antigravity("AAPL", df)
# print(result)
