import streamlit as st
import pandas as pd
import numpy as np

# Simpel GTO Preflop Range Solver
st.title("♠️♥️ GTO Preflop Solver ♦️♣️")
st.write("Simpel mobilvenlig version - juster parametre og se GTO-ranges")

# Brugervalg
st.sidebar.header("Indstillinger")
stack_size = st.sidebar.slider("Stackstørrelse (BB)", 10, 200, 100)
position = st.sidebar.selectbox("Din position", ["SB", "BB", "UTG", "MP", "CO", "BTN"])
villain_position = st.sidebar.selectbox("Modstanders position", ["SB", "BB", "UTG", "MP", "CO", "BTN"])

# Simpel GTO-range matrix (meget forenklet)
def get_gto_range(pos, villain_pos, stack):
    # Basisranges (procent af hænder)
    ranges = {
        ("BTN", "SB"): 0.45,
        ("BTN", "BB"): 0.48,
        ("CO", "BTN"): 0.32,
        ("MP", "CO"): 0.25,
        ("UTG", "MP"): 0.18,
        ("SB", "BB"): 0.65,
    }
    
    # Juster baseret på stackstørrelse
    adjustment = np.clip(stack / 100, 0.5, 1.5)
    base_range = ranges.get((pos, villain_pos), 0.22) * adjustment
    
    # Generer tilfældige GTO-ranges (i virkeligheden ville dette være en database)
    hands = ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "AKs", "AQs", "AJs", "ATs",
             "AKo", "AQo", "KQs", "QJs", "JTs", "T9s", "98s", "87s", "76s", "65s", "54s"]
    
    selected = hands[:int(len(hands) * base_range)]
    return sorted(selected)

# Beregn range
gto_range = get_gto_range(position, villain_position, stack_size)

# Vis resultater
st.subheader(f"GTO Preflop Range for {position} vs {villain_position} ({stack_size}BB)")
st.write("**Anbefalede hænder:**")
st.write(", ".join(gto_range))

# Visualisering
st.subheader("Range Matrix")
hand_matrix = pd.DataFrame(np.zeros((13,13)), 
                          index=["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"],
                          columns=["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"])

for hand in gto_range:
    if len(hand) == 3:  # suited
        row, col = hand[0], hand[1]
        hand_matrix.loc[row, col] = 1
    else:  # offsuit
        row, col = hand[0], hand[1]
        hand_matrix.loc[row, col] = 0.5

st.dataframe(hand_matrix.style.applymap(lambda x: f"background-color: {'#4CAF50' if x > 0 else '#f44336'}"))

# Forklaring
st.markdown("""
**Brugsanvisning:**
1. Vælg din position og modstanders position
2. Juster stackstørrelse
3. Se den anbefalede GTO-range

**Symbolforklaring:**
- 1.0 = Raise/call med suited
- 0.5 = Raise/call med offsuit
- 0 = Fold
""")
