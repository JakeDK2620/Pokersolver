import streamlit as st
import numpy as np
import pandas as pd
from itertools import combinations

st.set_page_config(layout="wide")

# ========== EV-BEREGNINGER ==========
class GTOSolver:
    def __init__(self):
        self.hand_strengths = self._init_hand_strengths()
        
    def _init_hand_strengths(self):
        """Precomputed hand vs hand equities (fra PokerStove-lignende data)"""
        strengths = {
            'AA': 0.85, 'KK': 0.82, 'QQ': 0.80, 'JJ': 0.78, 'TT': 0.75,
            'AKs': 0.67, 'AQs': 0.66, 'AJs': 0.65, 'KQs': 0.63, 
            'AKo': 0.65, 'AQo': 0.64, 'KQo': 0.60, 'JJ-': 0.55
        }
        return strengths
    
    def calculate_ev(self, my_range, opp_range, stack=100, bet_size=3):
        """Simplificeret EV-model"""
        my_hands = self._expand_range(my_range)
        opp_hands = self._expand_range(opp_range)
        
        total_ev = 0
        for my_hand in my_hands:
            equity = self.hand_strengths.get(my_hand, 0.5)
            ev = (equity * (stack + bet_size)) - ((1 - equity) * bet_size)
            total_ev += ev
        
        return total_ev / len(my_hands) if my_hands else 0
    
    def _expand_range(self, range_str):
        """Konverter range notation til individuelle hænder"""
        if 'JJ+' in range_str:
            return ['AA', 'KK', 'QQ', 'JJ']
        elif 'AKs' in range_str:
            return ['AKs']
        return []

# ========== STREAMLIT UI ==========
st.title("📱 Poker GTO Solver")
solver = GTOSolver()

with st.expander("⚙️ Range Indstillinger", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        my_range = st.selectbox(
            "Din Range",
            ["JJ+", "AKs", "AQo+", "KQs", "Custom"],
            index=0
        )
        
    with col2:
        opp_range = st.selectbox(
            "Modstanders Range",
            ["JJ+", "TT+", "AKs", "AJo+", "Loose"],
            index=1
        )

with st.expander("💰 EV Beregner", expanded=True):
    stack = st.slider("Stack (BB)", 10, 200, 100)
    bet_size = st.slider("Bet Size (BB)", 1, 10, 3)
    
    if st.button("Beregn EV"):
        ev = solver.calculate_ev(my_range, opp_range, stack, bet_size)
        st.metric("Forventet Værdi (EV)", f"{ev:.2f} BB")
        
        # EV Visualisering
        ev_diff = ev - bet_size
        st.progress(max(0, min(1, (ev + 5) / 10)))
        st.caption(f"EV difference: {'+' if ev_diff >=0 else ''}{ev_diff:.2f} BB")

# ========== RANGE MATRIX ==========
st.subheader("🧮 Range Matrix")
hands = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
matrix = pd.DataFrame(np.zeros((13,13)), index=hands, columns=hands)

# Populér matrix baseret på valgt range
if 'JJ+' in my_range:
    matrix.loc['J':'A', 'J':'A'] = 0.8  # Pocket pairs
    matrix.loc['A', 'K'] = 0.6  # AK

st.dataframe(
    matrix.style.applymap(
        lambda x: f"background-color: rgba(0,255,0,{x})" if x > 0 
        else f"background-color: rgba(255,0,0,{abs(x)})"
    ),
    height=600
)

# ========== MOBILOPTIMERING ==========
st.markdown("""
<style>
    .stDataFrame { font-size: 0.8em; }
    [data-testid="stMetricValue"] { font-size: 1.5em; }
</style>
""", unsafe_allow_html=True)
