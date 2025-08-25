import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import uuid

st.set_page_config(page_title="Item Balancing Tool", layout="wide")
st.title("🎮 Item Balancing Tool")

# Initialize session state
if "items" not in st.session_state:
    st.session_state["items"] = [
        {
            "item_name": "Power Sword",
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

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Data Input", "⚖️ Balance Analysis", "📈 Advanced Metrics"])

# Sidebar for global settings
st.sidebar.markdown("### ⚙️ Global Settings")
new_cost_max = st.sidebar.number_input(
    "Maximum Cost Value",
    min_value=1,
    max_value=10_000_000,
    value=st.session_state["cost_max_value"],
    step=1000,
    help="Maximum cost when success_rate and efficiency are both 100% (cost = (s × e / 10000) × max_cost)."
)

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
        df = pd.DataFrame(st.session_state["items"])
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "item_name": st.column_config.TextColumn("Item Name", width="medium"),
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
        # Enable sorting for all columns
        # Users can click column headers to sort

        # Update costs if data was edited
        if not edited_df.equals(df):
            updated_items = []
            for _, row in edited_df.iterrows():
                row['calculated_cost'] = calculate_cost(row['success_rate'], row['efficiency'], st.session_state["cost_max_value"])
                updated_items.append(row.to_dict())
            st.session_state["items"] = updated_items
            st.rerun()
    else:
        st.info("No items added yet. Use the form above to add your first item.")


    # Split 50/50 layout: Overview graph and Add new items
    col_overview, col_add_item = st.columns(2)
    
    with col_overview:
        st.subheader("📊 Overview of All Items")
        if st.session_state["items"]:
            df = pd.DataFrame(st.session_state["items"])

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
                st.metric("Total Items", len(df))
                st.metric("Avg Success Rate", f"{df['success_rate'].mean():.1f}%")
            with metrics_col2:
                st.metric("Avg Efficiency", f"{df['efficiency'].mean():.1f}%")
                st.metric("Avg Cost", f"{df['calculated_cost'].mean():.0f}")
            
            # Max cost indicator
            st.info(f"💰 **Max Cost Value:** {st.session_state['cost_max_value']:,} - Formula: (success × efficiency / 10000) × max_cost")
        else:
            st.info("No items to visualize yet. Add your first item using the form on the right!")

    with col_add_item:
        st.subheader("➕ Add New Items")
        
        new_item_name = st.text_input("Item Name", key="new_item_name")
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
        df = pd.DataFrame(st.session_state["items"])
        
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
                name=name,
                x=df['item_name'],
                y=df[col],
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
        st.plotly_chart(fig2, use_container_width=True)
        
        # Balance insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Performers")
            best_efficiency = df.loc[df['efficiency'].idxmax()]
            best_success = df.loc[df['success_rate'].idxmax()]
            best_value = df.loc[(df['success_rate'] + df['efficiency'] - df['calculated_cost'] * 100).idxmax()]
            
            st.metric("Most Efficient Item", best_efficiency['item_name'], f"{best_efficiency['efficiency']:.1f}%")
            st.metric("Highest Success Rate", best_success['item_name'], f"{best_success['success_rate']:.1f}%")
            st.metric("Best Value", best_value['item_name'], f"Score: {(best_value['success_rate'] + best_value['efficiency'] - best_value['calculated_cost'] * 100):.1f}")
            
        with col2:
            st.subheader("Balance Recommendations")
            
            # Identify overpowered items
            overpowered = df[(df['success_rate'] > 80) & (df['efficiency'] > 80) & (df['calculated_cost'] < 0.6)]
            if not overpowered.empty:
                st.warning(f"⚠️ Potentially overpowered: {', '.join(overpowered['item_name'])}")
            
            # Identify underpowered items
            underpowered = df[(df['success_rate'] < 40) & (df['efficiency'] < 40) & (df['calculated_cost'] > 0.5)]
            if not underpowered.empty:
                st.info(f"💡 Consider buffing: {', '.join(underpowered['item_name'])}")
            
            # Resource diversity
            avg_resource_usage = df[resource_cols].mean()
            underused_resources = avg_resource_usage[avg_resource_usage < 10].index
            if len(underused_resources) > 0:
                underused_names = [resource_names[resource_cols.index(col)] for col in underused_resources]
                st.info(f"🔍 Underused resources: {', '.join(underused_names)}")
    else:
        st.info("Add some items in the Data Input tab to see balance analysis.")

with tab3:
    st.header("Advanced Metrics")
    
    if st.session_state["items"]:
        df = pd.DataFrame(st.session_state["items"])
        
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
            st.metric("Cost Range", f"{df['calculated_cost'].min():.2f} - {df['calculated_cost'].max():.2f}")
            
        with col2:
            correlation = df['calculated_cost'].corr(df['performance_score'])
            st.metric("Cost-Performance Correlation", f"{correlation:.3f}")
            balance_score = 100 - abs(correlation - 0.8) * 100  # Ideal correlation is ~0.8
            st.metric("Balance Score", f"{max(balance_score, 0):.0f}/100")
            
        with col3:
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

# Show current item count
if st.session_state["items"]:
    st.sidebar.info(f"Currently managing {len(st.session_state['items'])} items")
else:
    st.sidebar.info("No items loaded")
