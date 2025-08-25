import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import uuid
import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np
import uuid

st.set_page_config(page_title="Item Balancing Tool", layout="wide")
st.title("🎮 Item Balancing Tool")

# Data file (local to this source file)
DATA_FILE = Path(__file__).parent / "data.json"

# Item categories
CATEGORIES = [
    "Weapons",
    "Armor",
    "Gadgets",
    "Medical Items",
    "Consumables",
    "Upgrades/Mods",
    "Tools",
    "Resources",
    "Blueprints",
    "Special/Unique"
]


def load_data_file(path: Path):
    """Try to load items from a JSON file.

    Accepts either a top-level list of item dicts or an object with an "items" key.
    Returns list on success, or None on failure.
    """
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        # Accept both list-of-dicts and { "items": [...] }
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            return data["items"]
        # Unexpected format
        st.warning(f"{path.name} exists but has unexpected JSON structure; expected a list or {{'items': [...]}}")
        return None
    except Exception as e:
        st.warning(f"Failed to read {path.name}: {e}")
        return None


def save_data_file(path: Path, items):
    try:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(items, fh, indent=2, ensure_ascii=False)
        st.success(f"Saved {len(items)} items to {path}")
    except Exception as e:
        st.error(f"Failed to save data to {path}: {e}")


# Initialize session state (try loading from data.json first)
if "items" not in st.session_state:
    loaded = load_data_file(DATA_FILE)
    if loaded is not None:
        st.session_state["items"] = loaded
    else:
        st.session_state["items"] = [
            {
                "item_name": "Power Sword",
                "category": "Weapons",
                "success_rate": 85.0,
                "efficiency": 90.0,
                "calculated_cost": 76500,  # Will be recalculated
                "metals_alloys": 40.0,
                "synthetic_materials": 20.0,
                "tech_components": 30.0,
                "energy_sources": 5.0,
                "biomatter": 0.0,
                "chemicals": 5.0
            },
            {
                "item_name": "Healing Potion",
                "category": "Medical Items",
                "success_rate": 95.0,
                "efficiency": 60.0,
                "calculated_cost": 57000,  # Will be recalculated
                "metals_alloys": 5.0,
                "synthetic_materials": 10.0,
                "tech_components": 5.0,
                "energy_sources": 10.0,
                "biomatter": 50.0,
                "chemicals": 20.0
            }
        ]

# Initialize max cost value if not exists
if "cost_max_value" not in st.session_state:
    st.session_state["cost_max_value"] = 100000

# Cost calculation function
def calculate_cost(success_rate, efficiency, cost_max):
    """Calculate item cost as (success_rate * efficiency / 10000) * cost_max

    success_rate and efficiency are percentages (0-100). The product is divided
    by 10000 to map 100*100 -> 1.0, then scaled by cost_max.
    """
    cost_factor = (success_rate * efficiency) / 10000.0
    final_cost = cost_factor * cost_max
    return final_cost

# Update costs for existing items
for item in st.session_state["items"]:
    item['calculated_cost'] = calculate_cost(item['success_rate'], item['efficiency'], st.session_state["cost_max_value"])

# Generate resource costs based on total cost and resource distribution
def calculate_resource_costs(items):
    """Calculate the cost of each resource type based on item's total cost and resource distribution."""
    resource_fields = [
        "metals_alloys", "synthetic_materials", "tech_components", 
        "energy_sources", "biomatter", "chemicals"
    ]
    
    resource_costs = []
    for item in items:
        item_resource_costs = {
            "item_name": item["item_name"],
            "category": item.get("category", ""),
            "calculated_cost": item["calculated_cost"]
        }
        
        total_resource_percentage = sum(item.get(field, 0) for field in resource_fields)
        
        # Avoid division by zero
        if total_resource_percentage > 0:
            for field in resource_fields:
                percentage = item.get(field, 0)
                # Calculate the cost for this resource
                cost = (percentage / total_resource_percentage) * item["calculated_cost"]
                item_resource_costs[f"{field}_cost"] = cost
        else:
            # If no resources specified, set all costs to 0
            for field in resource_fields:
                item_resource_costs[f"{field}_cost"] = 0
                
        resource_costs.append(item_resource_costs)
    
    return resource_costs

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Data Input", "⚖️ Balance Analysis", "📈 Advanced Metrics"])

# Sidebar for global settings
st.sidebar.markdown("### ⚙️ Global Settings")

# Category filter
st.sidebar.markdown("### 🔎 Filter Items")
category_filter = st.sidebar.radio("Filter by:", ["All Categories", "Specific Category"], key="filter_type")

filtered_items = st.session_state["items"]

if category_filter == "Specific Category":
    selected_category = st.sidebar.selectbox(
        "Select Category",
        ["All"] + CATEGORIES,
        key="category_filter"
    )
    
    if selected_category != "All":
        filtered_items = [item for item in st.session_state["items"] 
                        if item.get("category") == selected_category]

st.sidebar.markdown("---")
new_cost_max = st.sidebar.number_input(
    "Maximum Cost Value",
    min_value=1,
    max_value=10_000_000,
    value=st.session_state["cost_max_value"],
    step=1000,
    help="Maximum cost when success_rate and efficiency are both 100% (cost = (s × e / 10000) × max_cost)."
)

# Display options
st.sidebar.markdown("### 📊 Display Options")

# Initialize in session state if not exists
if "show_resource_costs" not in st.session_state:
    st.session_state["show_resource_costs"] = False

show_resource_costs = st.sidebar.checkbox(
    "Show Resource Costs",
    value=st.session_state["show_resource_costs"],
    help="When enabled, shows the calculated cost for each resource type based on the total item cost."
)

# Update session state with current checkbox value
st.session_state["show_resource_costs"] = show_resource_costs

# Update max cost if changed
if new_cost_max != st.session_state["cost_max_value"]:
    st.session_state["cost_max_value"] = new_cost_max
    # Recalculate all item costs
    for item in st.session_state["items"]:
        item['calculated_cost'] = calculate_cost(item['success_rate'], item['efficiency'], st.session_state["cost_max_value"])
    st.rerun()

with tab1:
    st.header("Item Data Management")

    # Current Items Table
    st.subheader("📋 Current Items Table")
    if st.session_state["items"]:
        df = pd.DataFrame(filtered_items)
        
        # Standard data editor view (always shown)
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "item_name": st.column_config.TextColumn("Item Name", width="medium"),
                "category": st.column_config.SelectboxColumn("Category", options=CATEGORIES),
                "success_rate": st.column_config.NumberColumn("Success Rate (%)", min_value=0.0, max_value=100.0),
                "efficiency": st.column_config.NumberColumn("Efficiency (%)", min_value=0.0, max_value=100.0),
                "calculated_cost": st.column_config.NumberColumn("Calculated Cost", disabled=True, format="%.0f"),
                "metals_alloys": st.column_config.NumberColumn("Metals & Alloys (%)", min_value=0.0, max_value=100.0),
                "synthetic_materials": st.column_config.NumberColumn("Synthetic Materials (%)", min_value=0.0, max_value=100.0),
                "tech_components": st.column_config.NumberColumn("Tech Components (%)", min_value=0.0, max_value=100.0),
                "energy_sources": st.column_config.NumberColumn("Energy Sources (%)", min_value=0.0, max_value=100.0),
                "biomatter": st.column_config.NumberColumn("Biomatter (%)", min_value=0.0, max_value=100.0),
                "chemicals": st.column_config.NumberColumn("Chemicals (%)", min_value=0.0, max_value=100.0)
            },
            key="item_editor",
            column_order=None,  # Show all columns
            hide_index=True
        )
        
        # Display resource costs table if toggle is enabled
        if show_resource_costs:
            st.subheader("💰 Resource Costs Breakdown")
            resource_costs = calculate_resource_costs(filtered_items)
            cost_df = pd.DataFrame(resource_costs)
            
            # Format column names for better display
            column_config = {
                "item_name": st.column_config.TextColumn("Item Name", width="medium"),
                "category": st.column_config.TextColumn("Category"),
                "calculated_cost": st.column_config.NumberColumn("Total Cost", format="%.0f"),
                "metals_alloys_cost": st.column_config.NumberColumn("Metals & Alloys Cost", format="%.0f"),
                "synthetic_materials_cost": st.column_config.NumberColumn("Synthetic Materials Cost", format="%.0f"),
                "tech_components_cost": st.column_config.NumberColumn("Tech Components Cost", format="%.0f"),
                "energy_sources_cost": st.column_config.NumberColumn("Energy Sources Cost", format="%.0f"),
                "biomatter_cost": st.column_config.NumberColumn("Biomatter Cost", format="%.0f"),
                "chemicals_cost": st.column_config.NumberColumn("Chemicals Cost", format="%.0f")
            }
            
            st.dataframe(
                cost_df,
                use_container_width=True,
                column_config=column_config,
                hide_index=True
            )
            
            # Add a summary of total resource costs
            if not cost_df.empty:
                st.subheader("Resource Cost Summary")
                total_costs = cost_df.drop(["item_name", "category", "calculated_cost"], axis=1).sum()
                
                # Create bar chart of total resource costs
                resource_names = [
                    "Metals & Alloys", "Synthetic Materials", "Tech Components",
                    "Energy Sources", "Biomatter", "Chemicals"
                ]
                cost_fields = [
                    "metals_alloys_cost", "synthetic_materials_cost", "tech_components_cost",
                    "energy_sources_cost", "biomatter_cost", "chemicals_cost"
                ]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=resource_names,
                        y=[total_costs[field] for field in cost_fields],
                        marker_color=['#5A9BD5', '#7AC36A', '#FAA75B', '#CE9ECB', '#D97C7C', '#9E9E9E']
                    )
                ])
                fig.update_layout(
                    title='Total Cost by Resource Type',
                    xaxis_title='Resource Type',
                    yaxis_title='Total Cost',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Update costs if data was edited
        if not edited_df.equals(df):
            updated_items = []
            for _, row in edited_df.iterrows():
                item = row.to_dict()
                item['calculated_cost'] = calculate_cost(item['success_rate'], item['efficiency'], st.session_state["cost_max_value"])
                updated_items.append(item)
                
            # Find the original items in the full list and update them
            for updated_item in updated_items:
                for i, original_item in enumerate(st.session_state["items"]):
                    if original_item.get("item_name") == updated_item.get("item_name"):
                        st.session_state["items"][i] = updated_item
                        break
                
            st.rerun()
    else:
        st.info("No items added yet. Use the form above to add your first item.")


    # Split 50/50 layout: Overview graph and Add new items
    col_overview, col_add_item = st.columns(2)
    
    with col_overview:
        st.subheader("📊 Overview of All Items")
        if st.session_state["items"]:
            df = pd.DataFrame(filtered_items)

            # Main scatter plot - Efficiency vs Success Rate
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['success_rate'],
                y=df['efficiency'],
                mode='markers+text',
                text=df['item_name'],
                textposition="top center",
                marker=dict(
                    # Use a fixed marker size so points don't grow/shrink with cost
                    size=12,
                    color=df['calculated_cost'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Calculated Cost"),
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                hovertemplate="<b>%{text}</b><br>" +
                             "Success Rate: %{x:.1f}%<br>" +
                             "Efficiency: %{y:.1f}%<br>" +
                             "Cost: %{marker.color:.0f}<br>" +
                             "<extra></extra>",
                name="Items"
            ))
            fig.update_layout(
                title={'text': "Efficiency vs Success Rate", 'x': 0.5, 'xanchor': 'center'},
                xaxis_title="Success Rate (%)",
                yaxis_title="Efficiency (%)",
                height=500,
                template="plotly_white",
                showlegend=False,
                xaxis=dict(range=[0, 105]),
                yaxis=dict(range=[0, 105])
            )
            fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_annotation(x=25, y=75, text="Low Success<br>High Efficiency", showarrow=False, opacity=0.6)
            fig.add_annotation(x=75, y=75, text="High Success<br>High Efficiency", showarrow=False, opacity=0.6)
            fig.add_annotation(x=25, y=25, text="Low Success<br>Low Efficiency", showarrow=False, opacity=0.6)
            fig.add_annotation(x=75, y=25, text="High Success<br>Low Efficiency", showarrow=False, opacity=0.6)
            st.plotly_chart(fig, use_container_width=True)

            # Summary statistics
            metrics_col1, metrics_col2 = st.columns(2)
            with metrics_col1:
                if len(filtered_items) != len(st.session_state["items"]):
                    st.metric("Filtered Items", f"{len(df)} of {len(st.session_state['items'])}")
                else:
                    st.metric("Total Items", len(df))
                st.metric("Avg Success Rate", f"{df['success_rate'].mean():.1f}%")
            with metrics_col2:
                st.metric("Avg Efficiency", f"{df['efficiency'].mean():.1f}%")
                st.metric("Avg Cost", f"{df['calculated_cost'].mean():.0f}")
            
            # Max cost indicator
            st.info(f"💰 **Cost-Formula: (success × efficiency × {st.session_state['cost_max_value']})")
        else:
            st.info("No items to visualize yet. Add your first item using the form on the right!")

    with col_add_item:
        st.subheader("➕ Add New Items")
        
        new_item_name = st.text_input("Item Name", key="new_item_name")
        
        # Category selection - simplified to a single dropdown
        new_category = st.selectbox("Category", options=CATEGORIES, key="new_category")
        
        new_success_rate = st.slider("Success Rate (%)", 0.0, 100.0, 50.0, key="new_success_rate")
        new_efficiency = st.slider("Efficiency (%)", 0.0, 100.0, 50.0, key="new_efficiency")
        
        # Initialize previous values in session state if they don't exist
        resource_keys = ["new_metals", "new_synthetic", "new_tech", "new_energy", "new_bio", "new_chemicals"]
        for key in resource_keys:
            if f"prev_{key}" not in st.session_state:
                st.session_state[f"prev_{key}"] = st.session_state.get(key, 0.0)
        
        # Function to rebalance resources
        def rebalance_resources(changed_key):
            # Get current values
            values = {key: st.session_state[key] for key in resource_keys}
            
            # Calculate how much the changed value was adjusted
            prev_value = st.session_state[f"prev_{changed_key}"]
            current_value = values[changed_key]
            change = current_value - prev_value
            
            # Skip rebalancing if no change
            if abs(change) < 0.001:
                return
                
            # Find non-zero resources excluding the changed one
            non_zero_keys = [key for key in resource_keys if key != changed_key and values[key] > 0]
            
            if non_zero_keys:
                # Calculate total of non-zero, non-changed resources
                total_others = sum(values[key] for key in non_zero_keys)
                
                # Calculate adjustment needed to maintain 100% total
                total_current = sum(values.values())
                adjustment_needed = change / (len(non_zero_keys) if total_others == 0 else 1)
                
                # Adjust other resources proportionally
                for key in non_zero_keys:
                    proportion = values[key] / total_others if total_others > 0 else 1/len(non_zero_keys)
                    new_value = max(0.0, values[key] - change * proportion)
                    st.session_state[key] = new_value
            
            # Update all previous values
            for key in resource_keys:
                st.session_state[f"prev_{key}"] = st.session_state[key]
        
        st.write("**Resource Distribution (%)**")
        st.write("*Resources will auto-balance to 100%*")
        step = 5.0
        
        # Detect which slider changed and rebalance
        for i, key in enumerate(resource_keys):
            current = st.session_state.get(key, 0.0)
            prev = st.session_state.get(f"prev_{key}", current)
            if abs(current - prev) > 0.001:
                rebalance_resources(key)
                break
        
        new_metals = st.slider("🔩 Metals & Alloys", 0.0, 100.0, st.session_state.get("new_metals", 100.0), step=step, key="new_metals")
        new_synthetic = st.slider("🧵 Synthetic Materials", 0.0, 100.0, st.session_state.get("new_synthetic", 0.0), step=step, key="new_synthetic")
        new_tech = st.slider("💻 Tech Components", 0.0, 100.0, st.session_state.get("new_tech", 0.0), step=step, key="new_tech")
        new_energy = st.slider("⚡ Energy Sources", 0.0, 100.0, st.session_state.get("new_energy", 0.0), step=step, key="new_energy")
        new_bio = st.slider("🌿 Biomatter", 0.0, 100.0, st.session_state.get("new_bio", 0.0), step=step, key="new_bio")
        new_chemicals = st.slider("🧪 Chemicals", 0.0, 100.0, st.session_state.get("new_chemicals", 0.0), step=step, key="new_chemicals")
        
        resource_sum = new_metals + new_synthetic + new_tech + new_energy + new_bio + new_chemicals
        st.progress(resource_sum / 100.0, f"Total: {resource_sum:.1f}%")
        
        if abs(resource_sum - 100.0) > 0.1:
            st.warning(f"Resource distribution sums to {resource_sum:.1f}%, should be 100%")
        
        if st.button("Add Item", use_container_width=True):
            # Use UUID if item name is empty
            item_name = new_item_name if new_item_name else 'no-name-' + str(uuid.uuid4())
            if abs(resource_sum - 100.0) <= 0.1:
                calculated_cost = calculate_cost(new_success_rate, new_efficiency, st.session_state["cost_max_value"])
                new_item = {
                    "item_name": item_name,
                    "category": new_category,
                    "success_rate": new_success_rate,
                    "efficiency": new_efficiency,
                    "calculated_cost": calculated_cost,
                    "metals_alloys": new_metals,
                    "synthetic_materials": new_synthetic,
                    "tech_components": new_tech,
                    "energy_sources": new_energy,
                    "biomatter": new_bio,
                    "chemicals": new_chemicals
                }
                st.session_state["items"].append(new_item)
                st.success(f"Added {item_name}!")
                st.rerun()
            else:
                st.error("Resource distribution must sum to 100%")


with tab2:
    st.header("Balance Analysis")
    
    if st.session_state["items"]:
        df = pd.DataFrame(filtered_items)
        
        # Resource composition analysis
        st.subheader("Resource Composition Analysis")
        resource_cols = ['metals_alloys', 'synthetic_materials', 'tech_components', 
                        'energy_sources', 'biomatter', 'chemicals']
        resource_names = ['Metals & Alloys', 'Synthetic Materials', 'Tech Components',
                         'Energy Sources', 'Biomatter', 'Chemicals']
        
        fig2 = go.Figure()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for i, (col, name) in enumerate(zip(resource_cols, resource_names)):
            fig2.add_trace(go.Bar(
                x=df['item_name'],
                y=df[col],
                name=name,
                marker_color=colors[i % len(colors)]
            ))
            
        fig2.update_layout(
            barmode='stack',
            title="Resource Distribution by Item",
            xaxis_title="Items",
            yaxis_title="Percentage (%)",
            height=400,
            template="plotly_white"
        )
        
        # Balance insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Performers")
            if not df.empty:
                best_efficiency = df.loc[df['efficiency'].idxmax()]
                best_success = df.loc[df['success_rate'].idxmax()]
                best_value = df.loc[(df['success_rate'] + df['efficiency'] - df['calculated_cost']/1000).idxmax()]
                
                st.metric("Most Efficient Item", best_efficiency['item_name'], f"{best_efficiency['efficiency']:.1f}%")
                st.metric("Highest Success Rate", best_success['item_name'], f"{best_success['success_rate']:.1f}%")
                st.metric("Best Value", best_value['item_name'], f"Score: {(best_value['success_rate'] + best_value['efficiency'] - best_value['calculated_cost']/1000):.1f}")
            
                # Category distribution
                st.subheader("Category Distribution")
                if 'category' in df.columns:
                    category_counts = df['category'].value_counts()
                    fig_cat = go.Figure(data=[go.Pie(labels=category_counts.index, 
                                                    values=category_counts.values, 
                                                    hole=.3)])
                    fig_cat.update_layout(height=300)
                    st.plotly_chart(fig_cat, use_container_width=True)
            
        with col2:
            st.subheader("Balance Recommendations")
            if not df.empty:
                # Identify overpowered items
                overpowered = df[(df['success_rate'] > 80) & (df['efficiency'] > 80) & (df['calculated_cost'] < 60000)]
                if not overpowered.empty:
                    st.warning(f"⚠️ Potentially overpowered: {', '.join(overpowered['item_name'])}")
                
                # Identify underpowered items
                underpowered = df[(df['success_rate'] < 40) & (df['efficiency'] < 40) & (df['calculated_cost'] > 20000)]
                if not underpowered.empty:
                    st.info(f"💡 Consider buffing: {', '.join(underpowered['item_name'])}")
                
                # Resource diversity
                avg_resource_usage = df[resource_cols].mean()
                underused_resources = avg_resource_usage[avg_resource_usage < 10].index
                if len(underused_resources) > 0:
                    underused_names = [resource_names[resource_cols.index(col)] for col in underused_resources]
                    st.info(f"🔍 Underused resources: {', '.join(underused_names)}")
                
                # Category balance analysis
                if 'category' in df.columns:
                    # Group by category and compute averages
                    cat_stats = df.groupby('category').agg({
                        'success_rate': 'mean',
                        'efficiency': 'mean',
                        'calculated_cost': 'mean'
                    }).reset_index()
                    
                    # Find strongest and weakest categories
                    cat_stats['power_level'] = cat_stats['success_rate'] + cat_stats['efficiency'] - cat_stats['calculated_cost']/1000
                    
                    if len(cat_stats) > 1:
                        strongest = cat_stats.loc[cat_stats['power_level'].idxmax()]
                        weakest = cat_stats.loc[cat_stats['power_level'].idxmin()]
                        
                        st.markdown("#### Category Balance")
                        st.info(f"💪 Strongest category: **{strongest['category']}** (Power: {strongest['power_level']:.1f})")
                        st.info(f"⚖️ Weakest category: **{weakest['category']}** (Power: {weakest['power_level']:.1f})")
                        
                        # Display category comparison
                        fig_cat_comp = go.Figure()
                        fig_cat_comp.add_trace(go.Bar(
                            x=cat_stats['category'],
                            y=cat_stats['power_level'],
                            marker_color='darkblue'
                        ))
                        fig_cat_comp.update_layout(
                            title="Category Power Levels",
                            xaxis_title="Category",
                            yaxis_title="Power Level",
                            height=300
                        )
                        st.plotly_chart(fig_cat_comp, use_container_width=True)
    else:
        st.info("Add some items in the Data Input tab to see balance analysis.")

with tab3:
    st.header("Advanced Metrics")
    
    if st.session_state["items"]:
        df = pd.DataFrame(filtered_items)
        
        # Cost vs Performance Analysis
        st.subheader("Cost vs Performance Analysis")
        
        fig3 = go.Figure()
        
        # Create a performance score (combination of success rate and efficiency)
        df['performance_score'] = (df['success_rate'] + df['efficiency']) / 2
        
        fig3.add_trace(go.Scatter(
            x=df['calculated_cost'],
            y=df['performance_score'],
            mode='markers+text',
            text=df['item_name'],
            textposition="top center",
            marker=dict(
                size=15,
                color=df['performance_score'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Performance Score")
            ),
            name="Items"
        ))
        
        # Add ideal balance line (theoretical)
        x_line = np.linspace(0, 1, 100)
        y_ideal = x_line * 100  # Ideal: cost should scale with performance
        
        fig3.add_trace(go.Scatter(
            x=x_line,
            y=y_ideal,
            mode='lines',
            name='Ideal Balance Line',
            line=dict(dash='dash', color='red', width=2),
            opacity=0.7
        ))
        
        fig3.update_layout(
            title="Cost vs Performance Balance",
            xaxis_title="Calculated Cost",
            yaxis_title="Performance Score (%)",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Statistical analysis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Performance Std Dev", f"{df['performance_score'].std():.1f}")
            st.metric("Cost Range", f"{df['calculated_cost'].min():.0f} - {df['calculated_cost'].max():.0f}")
            
        with col2:
            correlation = df['calculated_cost'].corr(df['performance_score'])
            st.metric("Cost-Performance Correlation", f"{correlation:.3f}")
            balance_score = 100 - abs(correlation - 0.8) * 100  # Ideal correlation is ~0.8
            st.metric("Balance Score", f"{max(balance_score, 0):.0f}/100")
            
        with col3:
            if 'category' in df.columns and len(df['category'].unique()) > 1:
                # Count items per category
                category_counts = df['category'].value_counts()
                st.metric("Most Common Category", category_counts.index[0], f"{category_counts.values[0]} items")
                st.metric("Categories Present", f"{len(category_counts)} of {len(CATEGORIES)}")
            else:
                st.metric("Items Analyzed", f"{len(df)}")
                if len(filtered_items) != len(st.session_state["items"]):
                    st.metric("Total Items", f"{len(filtered_items)} of {len(st.session_state['items'])}")
                else:
                    st.metric("Total Items", f"{len(st.session_state['items'])}")
            
        # Add category-based analysis if categories exist
        if 'category' in df.columns and len(df['category'].unique()) > 1:
            st.subheader("Category Performance Analysis")
            
            # Create category comparison dataframe
            cat_stats = df.groupby('category').agg({
                'success_rate': 'mean', 
                'efficiency': 'mean',
                'calculated_cost': 'mean',
                'performance_score': 'mean'
            }).reset_index()
            
            # Bar chart comparing categories
            fig_cat = go.Figure()
            
            # Add performance score bars
            fig_cat.add_trace(go.Bar(
                x=cat_stats['category'],
                y=cat_stats['performance_score'],
                name='Performance Score',
                marker_color='darkblue'
            ))
            
            # Add cost line (on secondary y-axis)
            fig_cat.add_trace(go.Scatter(
                x=cat_stats['category'],
                y=cat_stats['calculated_cost'],
                name='Average Cost',
                mode='lines+markers',
                marker=dict(color='red'),
                yaxis='y2'
            ))
            
            fig_cat.update_layout(
                title='Category Performance vs Cost',
                xaxis_title='Category',
                yaxis_title='Performance Score',
                yaxis2=dict(
                    title='Cost',
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                height=400
            )
            
            st.plotly_chart(fig_cat, use_container_width=True)
            
            # Show detailed stats in table
            st.dataframe(
                cat_stats.round({
                    'success_rate': 1, 
                    'efficiency': 1, 
                    'calculated_cost': 0,
                    'performance_score': 1
                }),
                use_container_width=True,
                hide_index=True
            )
            # Calculate how many items are above/below ideal line
            expected_performance = df['calculated_cost'] * 100
            overperforming = (df['performance_score'] > expected_performance * 1.1).sum()
            underperforming = (df['performance_score'] < expected_performance * 0.9).sum()
            
            st.metric("Overperforming Items", overperforming)
            st.metric("Underperforming Items", underperforming)
            
    else:
        st.info("Add some items in the Data Input tab to see advanced metrics.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎮 Item Balancing Tool")
st.sidebar.markdown("Balance your game items using data-driven insights!")

# Export/Import functionality
st.sidebar.markdown("### 📁 Data Management")
if st.sidebar.button("Clear All Items"):
    st.session_state["items"] = []
    st.rerun()

# Load / Save controls
st.sidebar.markdown("*Local data operations (reads/writes to data.json in app folder)*")
if st.sidebar.button("Load data.json"):
    loaded = load_data_file(DATA_FILE)
    if loaded is not None:
        st.session_state["items"] = loaded
        st.success(f"Loaded {len(loaded)} items from {DATA_FILE.name}")
        st.rerun()
    else:
        st.error(f"Failed to load {DATA_FILE.name}")

if st.sidebar.button("Save to data.json"):
    save_data_file(DATA_FILE, st.session_state.get("items", []))

# Offer downloadable JSON blob as well
st.sidebar.markdown("---")
st.sidebar.markdown("#### Export JSON")
try:
    json_blob = json.dumps(st.session_state.get("items", []), indent=2, ensure_ascii=False)
    st.sidebar.download_button("Download items.json", data=json_blob, file_name="items.json", mime="application/json")
except Exception:
    # download_button may fail in some environments; ignore
    pass

# Import external JSON file (uploaded by user)
st.sidebar.markdown("---")
st.sidebar.markdown("#### Import JSON File")
uploaded = st.sidebar.file_uploader("Choose a JSON file to import", type=["json"], key="uploader")
if uploaded is not None:
    try:
        # uploaded is a BytesIO-like object
        data = json.load(uploaded)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            items = data["items"]
        else:
            st.error("Uploaded JSON must be an array of items or an object with an 'items' list")
            items = None

        if items is not None:
            # Validate each item has required fields and add category if missing
            valid_items = []
            for item in items:
                if isinstance(item, dict) and "item_name" in item:
                    # If no category is set, default to first category
                    if "category" not in item:
                        item["category"] = CATEGORIES[0]
                    valid_items.append(item)
            
            if valid_items:
                st.session_state["items"] = valid_items
                st.success(f"Imported {len(valid_items)} items from uploaded file")
                st.rerun()
            else:
                st.error("No valid items found in the uploaded file")
    except Exception as e:
        st.error(f"Failed to parse uploaded JSON: {e}")

# Show current item count
if st.session_state["items"]:
    st.sidebar.info(f"Currently managing {len(st.session_state['items'])} items")
else:
    st.sidebar.info("No items loaded")
