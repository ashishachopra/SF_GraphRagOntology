# Knowledge graph visualization from KG_NODE and KG_EDGE tables

from snowflake.snowpark.context import get_active_session
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches

# Get Snowpark session
session = get_active_session()

# Read data from KG_NODE and KG_EDGE tables
print("Loading node and edge data from Snowflake...")
nodes_df = session.table("A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE").to_pandas()
edges_df = session.table("A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE").to_pandas()

print(f"Loaded {len(nodes_df)} nodes and {len(edges_df)} edges")

# Create directed graph
G = nx.DiGraph()

# Add nodes with attributes
for _, row in nodes_df.iterrows():
    G.add_node(row['NODE_ID'], 
               node_type=row['NODE_TYPE'],
               name=row['NAME'],
               props=row['PROPS'])

# Add edges with attributes
for _, row in edges_df.iterrows():
    G.add_edge(row['SRC_ID'], 
               row['DST_ID'],
               edge_type=row['EDGE_TYPE'],
               weight=row['WEIGHT'],
               props=row['PROPS'])

print(f"\nGraph Statistics:")
print(f"  Nodes: {G.number_of_nodes()}")
print(f"  Edges: {G.number_of_edges()}")
print(f"  Node Types: {nodes_df['NODE_TYPE'].unique().tolist()}")
print(f"  Edge Types: {edges_df['EDGE_TYPE'].unique().tolist()}")

# Set up visualization
fig, ax = plt.subplots(figsize=(20, 16))

# Define colors for different node types
node_colors = {
    'Customer': '#FF6B6B',
    'Account': '#4ECDC4',
    'Transaction': '#45B7D1',
    'Device': '#FFA07A'
}

# Define edge colors for different relationship types
edge_colors = {
    'OWNS': '#2E86AB',
    'FROM_ACCOUNT': '#A23B72',
    'TO_ACCOUNT': '#F18F01',
    'USES_DEVICE': '#C73E1D',
    'INITIATED_FROM': '#6A994E',
    'RELATED_TO': '#BC4749'
}

# Use spring layout for better visualization
pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

# Draw nodes by type
for node_type, color in node_colors.items():
    node_list = [node for node, attr in G.nodes(data=True) if attr.get('node_type') == node_type]
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=node_list,
                          node_color=color,
                          node_size=2000,
                          alpha=0.9,
                          ax=ax)

# Draw edges by type
for edge_type, color in edge_colors.items():
    edge_list = [(u, v) for u, v, attr in G.edges(data=True) if attr.get('edge_type') == edge_type]
    nx.draw_networkx_edges(G, pos,
                          edgelist=edge_list,
                          edge_color=color,
                          width=2,
                          alpha=0.6,
                          arrows=True,
                          arrowsize=20,
                          arrowstyle='->',
                          connectionstyle='arc3,rad=0.1',
                          ax=ax)

# Draw labels
labels = {node: G.nodes[node]['name'] for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold', ax=ax)

# Draw edge labels (relationship types)
edge_labels = {(u, v): attr['edge_type'] for u, v, attr in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6, ax=ax)

# Create legend for node types
node_legend = [mpatches.Patch(color=color, label=node_type) 
               for node_type, color in node_colors.items()]

# Create legend for edge types
edge_legend = [mpatches.Patch(color=color, label=edge_type) 
               for edge_type, color in edge_colors.items()]

# Combine legends
all_legend = node_legend + edge_legend
ax.legend(handles=all_legend, loc='upper left', fontsize=10, 
         title='Node & Edge Types', title_fontsize=12)

ax.set_title('Financial Crime Knowledge Graph\nCustomers, Accounts, Transactions & Devices', 
            fontsize=16, fontweight='bold', pad=20)
ax.axis('off')
plt.tight_layout()
plt.show()

# Print detailed node information
print("\n" + "="*80)
print("NODE DETAILS")
print("="*80)
for node_type in nodes_df['NODE_TYPE'].unique():
    type_nodes = nodes_df[nodes_df['NODE_TYPE'] == node_type]
    print(f"\n{node_type} ({len(type_nodes)} nodes):")
    for _, node in type_nodes.head(3).iterrows():
        print(f"  • {node['NODE_ID']}: {node['NAME']}")

# Print detailed edge information
print("\n" + "="*80)
print("EDGE DETAILS")
print("="*80)
for edge_type in edges_df['EDGE_TYPE'].unique():
    type_edges = edges_df[edges_df['EDGE_TYPE'] == edge_type]
    print(f"\n{edge_type} ({len(type_edges)} edges):")
    for _, edge in type_edges.head(3).iterrows():
        print(f"  • {edge['SRC_ID']} → {edge['DST_ID']}")

print("\n" + "="*80)
print("Graph visualization complete!")
print("="*80)
