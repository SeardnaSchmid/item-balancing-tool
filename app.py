import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Item Balancing Tool", layout="wide")
st.title("🎮 Item Balancing Tool")

# Initialize session state
if "items" not in st.session_state:
    st.session_state["items"] = [
        {
            "item_name": "Power Sword",
            "success_rate": 85.0,
            "efficiency": 90.0,
            "calculated_cost": 87500,  # Will be recalculated
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
            "calculated_cost": 52500,  # Will be recalculated
            "metals_alloys": 5.0,
            "synthetic_materials": 10.0,
            "tech_components": 5.0,
            "energy_sources": 10.0,
            "biomatter": 50.0,
            "chemicals": 20.0
        }
    ]

# Initialize cost multiplier if not exists
if "cost_multiplier" not in st.session_state:
    st.session_state["cost_multiplier"] = 1.0

# Cost calculation function
def calculate_cost(success_rate, efficiency, resource_distribution, cost_multiplier=1.0):
    """Calculate item cost based on success rate, efficiency, and resource distribution"""
    base_cost = (success_rate + efficiency) / 200.0  # Normalize to 0-1 range
    
    # Resource complexity multiplier
    resource_multiplier = 1.0
    rare_resources = resource_distribution.get('tech_components', 0) + resource_distribution.get('synthetic_materials', 0)
    if rare_resources > 50:
        resource_multiplier += 0.3
    elif rare_resources > 30:
        resource_multiplier += 0.1
    
    # Apply the cost multiplier and scale to 1-100000 range
    normalized_cost = base_cost * resource_multiplier * cost_multiplier
    # Scale from 0-1 range to 1-100000 range
    final_cost = 1 + (normalized_cost * 99999)
    return min(final_cost, 100000)  # Cap at 100000

# Update costs for existing items
for item in st.session_state["items"]:
    resource_dist = {
        'metals_alloys': item.get('metals_alloys', 0),
        'synthetic_materials': item.get('synthetic_materials', 0),
        'tech_components': item.get('tech_components', 0),
        'energy_sources': item.get('energy_sources', 0),
        'biomatter': item.get('biomatter', 0),
        'chemicals': item.get('chemicals', 0)
    }
    item['calculated_cost'] = calculate_cost(item['success_rate'], item['efficiency'], resource_dist, st.session_state["cost_multiplier"])

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Data Input", "⚖️ Balance Analysis", "📈 Advanced Metrics"])

# Sidebar for global settings
st.sidebar.markdown("### ⚙️ Global Settings")
new_cost_multiplier = st.sidebar.slider(
    "Cost Multiplier", 
    min_value=0.1, 
    max_value=10.0, 
    value=st.session_state["cost_multiplier"], 
    step=0.1,
    help="Scale all item costs by this multiplier. Cost range: 1-100,000 gold/credits."
)

# Update cost multiplier if changed
if new_cost_multiplier != st.session_state["cost_multiplier"]:
    st.session_state["cost_multiplier"] = new_cost_multiplier
    # Recalculate all item costs
    for item in st.session_state["items"]:
        resource_dist = {
            'metals_alloys': item.get('metals_alloys', 0),
            'synthetic_materials': item.get('synthetic_materials', 0),
            'tech_components': item.get('tech_components', 0),
            'energy_sources': item.get('energy_sources', 0),
            'biomatter': item.get('biomatter', 0),
            'chemicals': item.get('chemicals', 0)
        }
        item['calculated_cost'] = calculate_cost(item['success_rate'], item['efficiency'], resource_dist, st.session_state["cost_multiplier"])
    st.rerun()

with tab1:
    st.header("Item Data Management")

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
                    size=df['calculated_cost'] / 2000 + 10,  # Adjusted for new cost range
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
            
            # Cost multiplier indicator
            st.info(f"🎚️ **Cost Multiplier:** {st.session_state['cost_multiplier']:.1f}x - Cost range: 1-100,000")
        else:
            st.info("No items to visualize yet. Add your first item using the form on the right!")

    with col_add_item:
        st.subheader("➕ Add New Items")
        
        new_item_name = st.text_input("Item Name", key="new_item_name")
        new_success_rate = st.slider("Success Rate (%)", 0.0, 100.0, 50.0, key="new_success_rate")
        new_efficiency = st.slider("Efficiency (%)", 0.0, 100.0, 50.0, key="new_efficiency")
        
        st.write("**Resource Distribution (%)**")
        st.write("*Must sum to 100%*")
        new_metals = st.number_input("Metals & Alloys", 0.0, 100.0, 20.0, key="new_metals")
        new_synthetic = st.number_input("Synthetic Materials", 0.0, 100.0, 20.0, key="new_synthetic")
        new_tech = st.number_input("Tech Components", 0.0, 100.0, 20.0, key="new_tech")
        new_energy = st.number_input("Energy Sources", 0.0, 100.0, 20.0, key="new_energy")
        new_bio = st.number_input("Biomatter", 0.0, 100.0, 10.0, key="new_bio")
        new_chemicals = st.number_input("Chemicals", 0.0, 100.0, 10.0, key="new_chemicals")
        
        resource_sum = new_metals + new_synthetic + new_tech + new_energy + new_bio + new_chemicals
        if abs(resource_sum - 100.0) > 0.1:
            st.warning(f"Resource distribution sums to {resource_sum:.1f}%, should be 100%")
        
        if st.button("Add Item", use_container_width=True) and new_item_name:
            if abs(resource_sum - 100.0) <= 0.1:
                resource_dist = {
                    'metals_alloys': new_metals,
                    'synthetic_materials': new_synthetic,
                    'tech_components': new_tech,
                    'energy_sources': new_energy,
                    'biomatter': new_bio,
                    'chemicals': new_chemicals
                }
                calculated_cost = calculate_cost(new_success_rate, new_efficiency, resource_dist, st.session_state["cost_multiplier"])
                
                new_item = {
                    "item_name": new_item_name,
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
                st.success(f"Added {new_item_name}!")
                st.rerun()
            else:
                st.error("Resource distribution must sum to 100%")

    # Separator
    st.divider()

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
                resource_dist = {
                    'metals_alloys': row['metals_alloys'],
                    'synthetic_materials': row['synthetic_materials'],
                    'tech_components': row['tech_components'],
                    'energy_sources': row['energy_sources'],
                    'biomatter': row['biomatter'],
                    'chemicals': row['chemicals']
                }
                row['calculated_cost'] = calculate_cost(row['success_rate'], row['efficiency'], resource_dist, st.session_state["cost_multiplier"])
                updated_items.append(row.to_dict())
            st.session_state["items"] = updated_items
            st.rerun()
    else:
        st.info("No items added yet. Use the form above to add your first item.")

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
