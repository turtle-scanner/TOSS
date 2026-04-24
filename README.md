# Anti-Gravity Tactical Command Center (TOSS Edition)
# 🚀 전문가님을 위한 안티그래비티 전술 운용 매뉴얼

이 프로젝트는 토스증권 API의 현대적 REST 인터페이스를 활용하여, Mark Minervini와 Pradeep Bonde의 VCP/EP 전략을 실시간으로 추적하는 **프리미엄 트레이딩 대시보드**입니다.

## 🛠️ 핵심 전술 모듈
1. **Dry-up Scan**: 최근 3~5일 평균 대비 거래량이 급감하는 구간 포착 (수급의 일시적 진공 상태).
2. **Tightness Filter**: 주가 변동폭이 극도로 좁아지는 구간(변동성 축소) 필터링.
3. **EP Detection**: 900만 주 이상의 거래량 폭발 및 강력한 가격 돌파 감지.
4. **RS Leaderboard**: 벤치마크 대비 상대적 강도가 높은 주도주 자동 선별.

## 🚀 배포 가이드 (GitHub & Streamlit)

### 1. 환경 설정
`.env` 파일을 생성하고 발급받으신 토스 API 키를 입력하세요.
```env
TOSS_API_KEY=your_app_key
TOSS_SECRET_KEY=your_secret_key
```

### 2. 로컬 실행
```bash
pip install streamlit pandas yfinance plotly requests python-dotenv
streamlit run dashboard_v2.py
```

### 3. 클라우드 배포 (Streamlit Cloud)
1. 이 레포지토리를 GitHub에 업로드합니다.
2. [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 레포지토리를 연결합니다.
3. `Advanced Settings` -> `Secrets`에 `.env` 내용을 입력합니다.

## 💡 전문가님을 위한 조언
"로직의 단순화가 생명입니다." 
이 시스템은 가장 강한 **상위 10개 종목**에만 화력을 집중합니다. 복잡한 지표보다는 거래량이 마르고(Dry-up), 캔들이 좁아지는(Tightness) 순간의 **'고요함'**을 믿으십시오. 폭발은 항상 그 고요함 끝에서 시작됩니다.

---
**Status**: Tactical Readiness 100% | 동산 시스템 안정
