from flask import Flask, request, render_template_string
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Hardcoded GTO strategies for heads-up, 100BB
GTO_STRATEGIES = {
    ('SB', 'AhKd'): [
        {'action': 'raise', 'frequency': 0.8, 'ev': 0.9},
        {'action': 'call', 'frequency': 0.1, 'ev': 0.3},
        {'action': 'fold', 'frequency': 0.1, 'ev': 0.0}
    ],
    ('SB', '72o'): [
        {'action': 'raise', 'frequency': 0.1, 'ev': 0.2},
        {'action': 'call', 'frequency': 0.1, 'ev': 0.1},
        {'action': 'fold', 'frequency': 0.8, 'ev': 0.0}
    ],
    ('BB', 'AhKd'): [
        {'action': 'raise', 'frequency': 0.6, 'ev': 0.7},
        {'action': 'call', 'frequency': 0.3, 'ev': 0.4},
        {'action': 'fold', 'frequency': 0.1, 'ev': 0.0}
    ],
    ('BB', '72o'): [
        {'action': 'raise', 'frequency': 0.0, 'ev': 0.0},
        {'action': 'call', 'frequency': 0.2, 'ev': 0.1},
        {'action': 'fold', 'frequency': 0.8, 'ev': 0.0}
    ]
}

# HTML template optimized for iPhone
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GTO Preflop Poker Solver</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; text-align: center; }
        input, select, button { margin: 10px; padding: 10px; width: 90%; max-width: 300px; font-size: 16px; }
        button { background-color: #1E90FF; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .result { margin-top: 20px; font-size: 16px; }
        h3 { margin: 10px 0; }
        p { font-size: 14px; }
    </style>
</head>
<body>
    <h2>GTO Preflop Poker Solver</h2>
    <form method="POST">
        <input type="text" name="hole_cards" placeholder="Hole Cards (e.g., AhKd or 72o)" value="{{ hole_cards }}" required>
        <select name="position">
            <option value="SB" {% if position == 'SB' %}selected{% endif %}>Small Blind (SB)</option>
            <option value="BB" {% if position == 'BB' %}selected{% endif %}>Big Blind (BB)</option>
        </select>
        <p>Stack Depth: 100 BB</p>
        <button type="submit">Find GTO Strategy</button>
    </form>
    {% if result %}
        <div class="result">
            <h3>{{ result | safe }}</h3>
            {{ chart | safe }}
        </div>
    {% endif %}
    <p><b>Instructions:</b> Enter hole cards (e.g., AhKd or 72o), select position, and click 'Find GTO Strategy'. Add to Home Screen for app-like use.</p>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    hole_cards = "AhKd"
    position = "SB"
    result = ""
    chart = ""

    if request.method == 'POST':
        hole_cards = request.form.get('hole_cards', '').strip()
        position = request.form.get('position', 'SB')
        key = (position, hole_cards)
        strategies = GTO_STRATEGIES.get(key, [])

        if strategies:
            result = f"GTO Strategies for {hole_cards} in {position} (100 BB):<br>"
            df = pd.DataFrame(strategies)
            for _, row in df.iterrows():
                result += f"{row['action'].capitalize()}: {row['frequency']*100:.0f}%, EV: {row['ev']:.2f} BB<br>"

            # Create Plotly bar chart
            fig = px.bar(
                df,
                x="action",
                y="frequency",
                title=f"Action Frequencies for {hole_cards} in {position}",
                labels={"action": "Action", "frequency": "Frequency (%)"},
                color="action",
                color_discrete_map={"raise": "#1E90FF", "call": "#32CD32", "fold": "#FF4500"}
            )
            fig.update_layout(yaxis_tickformat=".0%", showlegend=False, height=300)
            chart = pio.to_html(fig, full_html=False)
        else:
            result = "No strategy found. Try AhKd or 72o."

    return render_template_string(HTML_TEMPLATE, hole_cards=hole_cards, position=position, result=result, chart=chart)

if __name__ == '__main__':
    app.run(debug=True)
