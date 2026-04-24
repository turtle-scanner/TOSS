import pandas as pd
import numpy as np

class BondeEngine:
    """
    Pradeep Bonde (Stockbee)의 5대 매매 원칙을 구현한 기계적 매매 엔진
    """
    def __init__(self, total_capital, risk_per_trade=0.01, market_status="NORMAL"):
        self.total_capital = total_capital
        self.risk_per_trade = risk_per_trade # [ 법칙 4 ] 리스크 1% 원칙
        self.market_status = market_status # [ 법칙 5 ] 상황 인식 (AGGRESSIVE, NORMAL, DEFENSIVE)

    def get_risk_multiplier(self):
        """
        [ 법칙 5 ] 상황 인식(Situational Awareness)에 따른 비중 조절
        - AGGRESSIVE: 100% 비중
        - NORMAL: 50% 비중
        - DEFENSIVE: 매매 중단 (0%)
        """
        multipliers = {"AGGRESSIVE": 1.0, "NORMAL": 0.5, "DEFENSIVE": 0.0}
        return multipliers.get(self.market_status, 0.5)

    def calculate_position_size(self, buy_price, stop_price):
        """
        [ 법칙 4 ] 철저한 자금 관리 (Position Sizing)
        """
        multiplier = self.get_risk_multiplier()
        risk_amount = self.total_capital * self.risk_per_trade * multiplier
        
        loss_per_share = buy_price - stop_price
        if loss_per_share <= 0: return 0, 0
            
        quantity = int(risk_amount / loss_per_share)
        total_investment = quantity * buy_price
        
        return quantity, total_investment

    def check_3_day_rule(self, df):
        """
        [ 법칙 2 ] 추격 매수 절대 금지 (The 3-Day Rule)
        3일 연속 상승한 종목은 진입 금지 (평균 회귀 위험)
        """
        if len(df) < 3:
            return True # 데이터 부족 시 보수적 접근
            
        recent_closes = df['Close'].iloc[-3:].values
        is_3_day_up = (recent_closes[2] > recent_closes[1]) and (recent_closes[1] > recent_closes[0])
        
        return not is_3_day_up # 3일 연속 상승이 아니어야 True

    def get_stop_levels(self, buy_price, lod, is_ep=False):
        """
        [ 법칙 1 ] 신성한 손절매 원칙 (Stops are sacred)
        - 기본 손절: -3% ~ -5%
        - LOD: 당일 최저점
        - EP 예외: 최대 -10%
        """
        default_stop = buy_price * 0.97 # -3% 원칙
        if is_ep:
            default_stop = buy_price * 0.90 # EP는 -10%까지 허용
            
        # LOD와 -3% 중 더 타이트한(높은 가격) 것을 우선 적용하거나 상황에 맞게 선택
        # 본데는 보통 LOD를 Hard Stop으로 삼음
        hard_stop = max(default_stop, lod) 
        
        return {
            "default_stop": round(default_stop, 2),
            "lod_stop": round(lod, 2),
            "hard_stop": round(hard_stop, 2)
        }

    def get_exit_strategy(self, buy_price, current_price, high_since_entry, days_held, df):
        """
        [ 법칙 3 ] 단기 이익 실현 (Hitting Singles) & 트레일링 스탑
        - 3~5일 내 8~20% 급등 시 절반 익절
        - 익절 후 본절가(Break-even)로 스탑 상향
        - 남은 물량은 10/20MA 이탈 시 전량 매도
        """
        profit_ratio = (current_price / buy_price) - 1
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        instructions = []
        
        # 1. 단기 이익 실현 체크
        if days_held <= 5 and profit_ratio >= 0.10: # 10% 이상 수익 시
            instructions.append("HALF_SELL: 10% 수익 달성, 물량 절반 익절 권고")
            
        # 2. 본절 상향 체크 (이미 일부 익절했을 경우)
        # (이 로직은 상태 저장이 필요하므로 여기서는 가이드만 제시)
        
        # 3. 추세 이탈 체크 (Trailing Stop)
        if current_price < ma10:
            instructions.append("TRAILING_STOP: 10MA 이탈, 전량 매도 검토")
        elif current_price < ma20:
            instructions.append("FINAL_EXIT: 20MA 이탈, 추세 종료 매도")
            
        return instructions

# 사용 예시
# engine = BondeEngine(total_capital=10000000) # 1000만원 계좌
# qty, inv = engine.calculate_position_size(buy_price=10000, stop_price=9700)
# print(f"진입 수량: {qty}주, 투자 금액: {inv}원")
