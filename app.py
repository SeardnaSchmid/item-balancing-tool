import streamlit as st
import plotly.figure_factory as ff
import pandas as pd

st.set_page_config(page_title="Item Balancing Tool", layout="wide")

st.title("Item Balancing Tool: Chance/Effect/Cost Triangle")

# Example item data
if "items" not in st.session_state:
    st.session_state["items"] = [
        {"name": "Powersword", "chance": 1.0, "effect": 0.8, "cost": 0.9},
        {"name": "Healing Potion", "chance": 0.7, "effect": 0.5, "cost": 0.5},
    ]

# Sidebar: Add/Edit Items
st.sidebar.header("Manage Items")
new_name = st.sidebar.text_input("Item Name")
new_chance = st.sidebar.slider("Chance (0-1)", 0.0, 1.0, 0.5)
new_effect = st.sidebar.slider("Effect (0-1)", 0.0, 1.0, 0.5)
if st.sidebar.button("Add Item"):
    st.session_state["items"].append({"name": new_name, "chance": new_chance, "effect": new_effect, "cost": None})

# Cost calculation function
def calculate_cost(chance, effect):
    # Example formula: cost increases with effect and chance
    # You can customize this formula
    if chance > 0.8 and effect > 0.7:
        return 0.9
    elif chance < 0.3 and effect > 0.7:
        return 0.7
    elif chance > 0.7 and effect < 0.4:
        return 0.3
    else:
        return (chance + effect) / 2

# Update costs
for item in st.session_state["items"]:
    item["cost"] = calculate_cost(item["chance"], item["effect"])

# Prepare data for ternary plot
item_names = [item["name"] for item in st.session_state["items"]]
chances = [item["chance"] for item in st.session_state["items"]]
effects = [item["effect"] for item in st.session_state["items"]]
costs = [item["cost"] for item in st.session_state["items"]]

# Create a simple ternary scatter plot instead
import plotly.graph_objects as go

fig = go.Figure()

# Add scatter points for items
fig.add_trace(go.Scatter(
    x=chances,
    y=effects,
    mode='markers+text',
    text=item_names,
    textposition="top center",
    marker=dict(
        size=10,
        color=costs,
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Cost")
    ),
    name="Items"
))

fig.update_layout(
    title="Item Balance: Chance vs Effect (Color = Cost)",
    xaxis_title="Chance",
    yaxis_title="Effect",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# Show item table
st.subheader("Item List")
st.dataframe(pd.DataFrame(st.session_state["items"]))
