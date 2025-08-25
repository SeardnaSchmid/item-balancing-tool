# Item Balancing Tool

This Streamlit app visualizes and balances items using the Chance/Effect/Cost triangle. You can add, edit, and move items in a ternary plot, with costs calculated live based on your balancing rules.

## Features
- Add/edit/remove items
- Drag items in a ternary plot (Chance/Effect/Cost)
- Live cost calculation
- Export/import item data

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

## Requirements
- Python 3.8+
- Streamlit
- Plotly
- Pandas

## Customization
You can adjust the cost calculation logic in `app.py` to fit your game's balancing rules.
