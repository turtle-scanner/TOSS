import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from antigravity_logic import analyze_antigravity
from bonde_engine import BondeEngine
from toss_api import TossSecuritiesAPI
import base64
import os
import hashlib

# --- [ SECURITY CONSTANTS ] ---
USER_ID = "cntfed"
USER_PW_HASH = hashlib.sha256("cntfed".encode()).hexdigest()

# --- [ ASSETS LOAD ] ---
def get_base64_bin(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- [ UI/UX ] Premium Tactical Design ---
def inject_premium_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Outfit:wght@300;400;700&display=swap');
        :root { --neon-blue: #00F2FF; --neon-pink: #FF00E5; --neon-green: #39FF14; }
        .stApp { background: #050505; color: #ffffff; font-family: 'Outfit', sans-serif; }
        .login-box { background: rgba(20, 20, 30, 0.8); border: 1px solid var(--neon-blue); border-radius: 20px; padding: 40px; max-width: 500px; margin: 100px auto; text-align: center; }
        .tactical-card { background: rgba(20, 20, 30, 0.8); border-left: 5px solid var(--neon-blue); border-radius: 10px; padding: 20px; margin-bottom: 15px; }
        .ai-box { background: linear-gradient(135deg, rgba(0, 242, 255, 0.05), rgba(255, 0, 229, 0.05)); border: 1px dashed var(--neon-blue); border-radius: 10px; padding: 15px; font-style: italic; }
        h1, h2 { font-family: 'Orbitron', sans-serif; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Dragonfly 전술 동산", layout="wide")
inject_premium_style()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'trade_log' not in st.session_state: st.session_state.trade_log = []

def add_trade_log(ticker, side, qty, price):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.trade_log.append({"Time": now, "Ticker": ticker, "Side": side, "Qty": qty, "Price": price, "Total": qty*price})

def login():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    if os.path.exists("StockDragonfly.png"): st.image("StockDragonfly.png", width=120)
    st.title("🚁 Dragonfly by Toss")
    st.markdown("##### Dragonfly by Toss - 전술 트레이딩 동산")
    with st.form("login_form"):
        user_id = st.text_input("User ID", placeholder="ID를 입력하세요")
        password = st.text_input("Password", type="password", placeholder="비밀번호를 입력하세요")
        submit = st.form_submit_button("SYSTEM LOGIN")
        if submit:
            if user_id == USER_ID and hashlib.sha256(password.encode()).hexdigest() == USER_PW_HASH:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("인증 실패")
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login()
else:
    toss = TossSecuritiesAPI("key", "secret", mock=True)
    toss.get_access_token()

    @st.cache_data(ttl=600)
    def fetch_market_data(ticker):
        try: return yf.download(ticker, period="60d", progress=False)
        except: return pd.DataFrame()

    def fetch_news(ticker):
        try:
            t = yf.Ticker(ticker)
            return t.news[:3] # 최근 뉴스 3개
        except: return []

    with st.sidebar:
        if os.path.exists("StockDragonfly.png"): st.image("StockDragonfly.png", use_container_width=True)
        st.header("📊 Market State")
        market_state = st.radio("[ 법칙 5 ] 상황 인식", ["AGGRESSIVE", "NORMAL", "DEFENSIVE"], index=1)
        st.divider()
        st.header("🎵 Tactical BGM")
        bgm_choice = st.selectbox("전술 음악", ["None", "YouRaise", "full", "my bonde"])
        volume = st.slider("Volume", 0, 100, 20)
        if bgm_choice != "None" and os.path.exists(f"{bgm_choice}.mp3"):
            audio_base64 = get_base64_bin(f"{bgm_choice}.mp3")
            st.markdown(f'<audio id="bgm-player" autoplay loop><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio><script>var audio = window.parent.document.getElementById("bgm-player"); if (audio) {{ audio.volume = {volume / 100}; }}</script>', unsafe_allow_html=True)
        st.divider()
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    # --- HEADER ---
    c_h1, c_h2 = st.columns([1, 8])
    with c_h1:
        if os.path.exists("StockDragonfly.png"): st.image("StockDragonfly.png", width=80)
    with c_h2:
        st.title("Dragonfly 전술 동산")
        st.markdown("##### TOSS 증권과 함께하는 주도주 사냥")

    # --- [ UPGRADE 1: MARKET BREADTH & VIX ] ---
    st.divider()
    bg1, bg2, bg3 = st.columns([2, 1, 1])
    with bg1:
        st.subheader("🏦 실시간 계좌 및 자산 현황")
        balance = toss.get_balance()
        st.metric("총 자산 (Equity)", f"{balance['total_equity']:,} 원", delta=f"{balance['total_equity'] - balance['total_cash']:,}")
    
    with bg2:
        # VIX Fear Gauge
        vix_df = fetch_market_data("^VIX")
        vix = vix_df['Close'].iloc[-1] if not vix_df.empty else 20.0
        st.metric("VIX (Fear Gauge)", f"{vix:.2f}", delta=f"{vix-vix_df['Close'].iloc[-2]:.2f}", delta_color="inverse")
        
    with bg3:
        # 시장 건강도 게이지 (Rule 5 시각화)
        health_score = 80 if market_state == "AGGRESSIVE" else (50 if market_state == "NORMAL" else 20)
        # VIX가 30 이상이면 감점
        if vix > 30: health_score -= 20
        fig_g = go.Figure(go.Indicator(
            mode = "gauge+number", value = max(0, health_score), title = {'text': "Market Health"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "var(--neon-blue)"}, 'steps': [{'range': [0, 30], 'color': "red"}, {'range': [30, 70], 'color': "gray"}, {'range': [70, 100], 'color': "green"}]}
        ))
        fig_g.update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        st.plotly_chart(fig_g, use_container_width=True)

    # --- TACTICAL MONITOR ---
    st.markdown("#### 🛰️ 실시간 전술 모니터링 (Top 10)")
    TOP_10 = ["NVDA", "TSLA", "AAPL", "PLTR", "MSFT", "AMD", "META", "AVGO", "MSTR", "005930.KS"]
    benchmark = fetch_market_data("^GSPC")
    results = [analyze_antigravity(t, fetch_market_data(t), benchmark) for t in TOP_10]
    
    cols = st.columns(5)
    for i, res in enumerate(results):
        with cols[i % 5]:
            st.markdown(f'<div class="tactical-card"><b>{res["ticker"]}</b><br><small>{res["action"]}</small><br><span style="color:var(--neon-blue);">{res["score"]} PTS</span></div>', unsafe_allow_html=True)

    # --- EXECUTION & AI INSIGHTS ---
    st.divider()
    ex1, ex2 = st.columns([1, 1])
    with ex1:
        st.subheader("⚙️ 전술 집행 및 주문")
        sel = st.selectbox("분석 대상", TOP_10)
        f_res = next(r for r in results if r['ticker'] == sel)
        f_df = fetch_market_data(sel)
        curr = f_df['Close'].iloc[-1] if not f_df.empty else 0
        
        engine = BondeEngine(balance['total_equity'], 0.01, market_state)
        stops = engine.get_stop_levels(curr, f_res['lod'], f_res['is_ep'])
        qty, inv = engine.calculate_position_size(curr, stops['hard_stop'])
        
        st.success(f"추천 수량: {qty:,} 주 (손절가: {stops['hard_stop']:,})")
        if st.button(f"🚀 {sel} 즉시 매수"): 
            add_trade_log(sel, "BUY", qty, curr)
            st.balloons()
            st.success(f"{sel} {qty}주 매수 주문 전송 완료")
        
        # 실시간 뉴스 섹션 추가
        st.markdown("---")
        st.markdown("#### 📰 Latest News (Catalysts)")
        news = fetch_news(sel)
        for n in news:
            st.markdown(f"- [{n['title']}]({n['link']})")
        
    with ex2:
        st.subheader("🧠 AI 전술 브리핑 (Insights)")
        st.markdown(f"""
        <div class="ai-box">
            "현재 <b>{sel}</b> 종목은 {f_res['score']}점의 전술 등급을 기록 중입니다. 
            특히 { '변동성이 좁아지는 Tightness 구간' if f_res['is_tight'] else '추세 강도가 유지되는 구간' }에 진입하여 
            <b>법칙 4</b>에 따른 리스크 1% 진입이 유효해 보입니다. 본데의 원칙에 따라 LOD 손절을 엄수하십시오."
        </div>
        """, unsafe_allow_html=True)
        # 차트
        fig = go.Figure(data=[go.Candlestick(x=f_df.index, open=f_df['Open'], high=f_df['High'], low=f_df['Low'], close=f_df['Close'])])
        fig.update_layout(template="plotly_dark", height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    # --- TACTICAL LOG ---
    st.divider()
    st.subheader("📝 전술 매매 로그 (Tactical Log)")
    if st.session_state.trade_log:
        st.table(pd.DataFrame(st.session_state.trade_log))
    else:
        st.info("오늘의 매매 기록이 없습니다.")

st.caption(f"Dragonfly 전술 동산 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
