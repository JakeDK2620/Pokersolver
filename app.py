import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations

# ===== KONFIGURATION =====
st.set_page_config(layout="wide", page_title="♠️♥️ GTO Poker Solver ♦️♣️")

# ===== DATABASE =====
HAND_EQUITIES = {
    # Preflop equities (fra PioSolver)
    'preflop': {
        'AA': 0.85, 'KK': 0.82, 'QQ': 0.80, 'JJ': 0.78, 'TT': 0.75,
        'AKs': 0.67, 'AQs': 0.66, 'AJs': 0.64, 'KQs': 0.63,
        'AKo': 0.65, 'AQo': 0.63, 'KQo': 0.60
    },
    
    # Eksempel flop equities (kunne udvides)
    'flop': {
        'AA': {'T72r': 0.87, 'J83s': 0.85, 'Q54dd': 0.82},
        'AKs': {'T72r': 0.65, 'J83s': 0.70, 'Q54dd': 0.68}
    }
}

# ===== BEREGNINGSFUNKTIONER =====
def beregn_ev(hand, street, modstander_range, board=None, pot=20, bet=10, fold_equity=0.3):
    """Beregner EV for en hånd på enhver street"""
    if street == "preflop":
        equity = HAND_EQUITIES['preflop'].get(hand, 0.5)
    else:
        equity = HAND_EQUITIES['flop'].get(hand, {}).get(board, 0.5)
    
    ev = (equity * (pot + bet)) - ((1 - equity) * bet)
    ev_med_fold = fold_equity * pot + (1 - fold_equity) * ev
    return ev_med_fold

# ===== BRUGERFLADE =====
st.title("♠️♥️ Ultimate GTO Solver ♦️♣️")
st.write("Fra preflop til river - optimeret til iPhone")

tabs = st.tabs(["Preflop", "Flop", "Turn", "River"])

with tabs[0]:  # Preflop
    st.subheader("Preflop EV Matrix")
    col1, col2 = st.columns(2)
    with col1:
        stack = st.slider("Stack (BB)", 10, 200, 100, key='preflop_stack')
    with col2:
        bet = st.slider("Bet (BB)", 1, 10, 3, key='preflop_bet')
    
    # Preflop matrix
    ranks = ['A', 'K', 'Q', 'J', 'T', '9']
    df_preflop = pd.DataFrame("", index=ranks, columns=ranks)
    
    for (i, r1), (j, r2) in combinations(enumerate(ranks), 2):
        hand = f"{r1}{r2}{'s' if i < j else 'o' if i != j else ''}"
        if hand in HAND_EQUITIES['preflop']:
            ev = beregn_ev(hand, "preflop", "JJ+", pot=stack, bet=bet)
            df_preflop.at[r1, r2] = f"{ev:.1f}BB"
            df_preflop.at[r2, r1] = df_preflop.at[r1, r2]
    
    st.dataframe(df_preflop.style.applymap(
        lambda x: "background-color: #4CAF50" if x and float(x.split('BB')[0]) > 0 
        else "background-color: #f44336"
    ), height=500)

with tabs[1]:  # Flop
    st.subheader("Flop EV Analyzer")
    flop = st.text_input("Indtast Flop (fx. 'T72r')", "T72r").strip()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        pot = st.slider("Pot (BB)", 5, 50, 20, key='flop_pot')
    with col2:
        bet = st.slider("Bet (BB)", 1, 30, 10, key='flop_bet')
    with col3:
        fold_eq = st.slider("Fold Equity %", 0, 100, 30, key='flop_fold') / 100
    
    hands_to_analyze = st.multiselect(
        "Vælg hænder at analysere",
        list(HAND_EQUITIES['preflop'].keys()),
        default=['AA', 'AKs', 'AQs']
    )
    
    flop_data = []
    for hand in hands_to_analyze:
        ev = beregn_ev(hand, "flop", "JJ+", board=flop, pot=pot, bet=bet, fold_equity=fold_eq)
        flop_data.append([hand, f"{ev:.1f}BB"])
    
    st.table(pd.DataFrame(flop_data, columns=["Hand", "EV"]))

with tabs[2]:  # Turn
    st.subheader("Turn EV (Under Udvikling)")
    st.write("Kommer i næste version!")
    # TODO: Implementer turn-logik

with tabs[3]:  # River
    st.subheader("River EV (Under Udvikling)")
    st.write("Kommer i næste version!")
    # TODO: Implementer river-logik

# ===== MOBILOPTIMERING =====
st.markdown("""
<style>
    div[data-testid="stDataFrame"] table {
        font-size: 0.75rem !important;
    }
    @media (max-width: 600px) {
        div[data-testid="stDataFrame"] table {
            font-size: 0.65rem !important;
        }
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)
