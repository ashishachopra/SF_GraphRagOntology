# Fan-in detection analysis on knowledge graph from KG_NODE and KG_EDGE tables

from snowflake.snowpark.context import get_active_session
import pandas as pd
import networkx as nx
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Get Snowpark session
session = get_active_session()

# Read data from KG_NODE and KG_EDGE tables
print("Loading node and edge data from Snowflake...")
nodes_df = session.table("A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE").to_pandas()
edges_df = session.table("A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE").to_pandas()

print(f"Loaded {len(nodes_df)} nodes and {len(edges_df)} edges\n")

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

print("="*100)
print("FAN-IN DETECTION ANALYSIS")
print("="*100)
print("\nFan-in = Number of incoming edges to a node")
print("High fan-in nodes may indicate:")
print("  • Money mule accounts (receiving from many sources)")
print("  • Compromised/shared devices")
print("  • Central hub entities in fraud networks")
print("  • High-traffic transaction endpoints\n")


def calculate_fan_in_metrics(graph):
    """
    Calculate comprehensive fan-in metrics for all nodes.
    """
    fan_in_data = []
    
    for node in graph.nodes():
        node_data = graph.nodes[node]
        
        # Get all incoming edges
        predecessors = list(graph.predecessors(node))
        in_degree = len(predecessors)
        
        # Analyze incoming edge types
        incoming_edge_types = []
        incoming_node_types = []
        
        for pred in predecessors:
            edge_data = graph.get_edge_data(pred, node)
            pred_data = graph.nodes[pred]
            
            if edge_data:
                incoming_edge_types.append(edge_data.get('edge_type', 'Unknown'))
            incoming_node_types.append(pred_data.get('node_type', 'Unknown'))
        
        fan_in_data.append({
            'node_id': node,
            'node_type': node_data.get('node_type'),
            'node_name': node_data.get('name'),
            'fan_in_count': in_degree,
            'incoming_nodes': predecessors,
            'incoming_edge_types': incoming_edge_types,
            'incoming_node_types': incoming_node_types,
            'edge_type_counts': Counter(incoming_edge_types),
            'source_type_counts': Counter(incoming_node_types)
        })
    
    return fan_in_data


def get_fan_out_count(graph, node):
    """Get fan-out (outgoing edges) for comparison."""
    return len(list(graph.successors(node)))


# Calculate fan-in metrics
print("Calculating fan-in metrics for all nodes...")
fan_in_data = calculate_fan_in_metrics(G)

# Sort by fan-in count
fan_in_data_sorted = sorted(fan_in_data, key=lambda x: x['fan_in_count'], reverse=True)

print(f"✅ Analysis complete!\n")


# Overall statistics
print("="*100)
print("OVERALL FAN-IN STATISTICS")
print("="*100)

total_nodes = len(fan_in_data)
nodes_with_fan_in = len([d for d in fan_in_data if d['fan_in_count'] > 0])
avg_fan_in = sum(d['fan_in_count'] for d in fan_in_data) / total_nodes if total_nodes > 0 else 0
max_fan_in = max(d['fan_in_count'] for d in fan_in_data) if fan_in_data else 0

print(f"\n📊 Summary:")
print(f"  Total nodes: {total_nodes}")
print(f"  Nodes with incoming edges: {nodes_with_fan_in} ({nodes_with_fan_in/total_nodes*100:.1f}%)")
print(f"  Nodes with no incoming edges: {total_nodes - nodes_with_fan_in}")
print(f"  Average fan-in: {avg_fan_in:.2f}")
print(f"  Maximum fan-in: {max_fan_in}")


# Fan-in distribution by node type
print(f"\n\n📈 FAN-IN BY NODE TYPE:")
print(f"{'Node Type':<15} {'Avg Fan-In':<15} {'Max Fan-In':<15} {'Total Nodes':<15}")
print("-" * 60)

fan_in_by_type = defaultdict(list)
for data in fan_in_data:
    fan_in_by_type[data['node_type']].append(data['fan_in_count'])

# Filter out None keys and sort
valid_node_types = [nt for nt in fan_in_by_type.keys() if nt is not None]
for node_type in sorted(valid_node_types):
    counts = fan_in_by_type[node_type]
    avg = sum(counts) / len(counts) if counts else 0
    max_val = max(counts) if counts else 0
    print(f"{node_type:<15} {avg:<15.2f} {max_val:<15} {len(counts):<15}")

# Handle None node types separately if they exist
if None in fan_in_by_type:
    counts = fan_in_by_type[None]
    avg = sum(counts) / len(counts) if counts else 0
    max_val = max(counts) if counts else 0
    print(f"{'(Unknown)':<15} {avg:<15.2f} {max_val:<15} {len(counts):<15}")


# Top nodes by fan-in
print(f"\n\n{'='*100}")
print("TOP NODES BY FAN-IN (Potential High-Risk Entities)")
print(f"{'='*100}\n")

print(f"{'Rank':<6} {'Node ID':<12} {'Type':<12} {'Name':<30} {'Fan-In':<10} {'Fan-Out':<10}")
print("-" * 90)

for rank, data in enumerate(fan_in_data_sorted[:15], 1):
    node_id = data['node_id']
    fan_out = get_fan_out_count(G, node_id)
    node_type_display = data['node_type'] if data['node_type'] is not None else 'Unknown'
    
    print(f"{rank:<6} {node_id:<12} {node_type_display:<12} {data['node_name']:<30} "
          f"{data['fan_in_count']:<10} {fan_out:<10}")


# Detailed analysis of high fan-in nodes
print(f"\n\n{'='*100}")
print("DETAILED HIGH FAN-IN ANALYSIS")
print(f"{'='*100}")

# Define threshold for "high" fan-in (top 20% or minimum of 3)
fan_in_counts = [d['fan_in_count'] for d in fan_in_data if d['fan_in_count'] > 0]
if fan_in_counts:
    threshold = max(3, sorted(fan_in_counts, reverse=True)[min(len(fan_in_counts)//5, len(fan_in_counts)-1)])
else:
    threshold = 3

high_fan_in_nodes = [d for d in fan_in_data_sorted if d['fan_in_count'] >= threshold]

print(f"\nAnalyzing {len(high_fan_in_nodes)} nodes with fan-in >= {threshold}\n")

for idx, data in enumerate(high_fan_in_nodes[:10], 1):  # Show top 10 in detail
    node_id = data['node_id']
    fan_out = get_fan_out_count(G, node_id)
    node_type_display = data['node_type'] if data['node_type'] is not None else 'Unknown'
    
    print(f"\n{'─'*100}")
    print(f"🔍 High Fan-In Node #{idx}")
    print(f"{'─'*100}")
    print(f"  Node ID: {node_id}")
    print(f"  Type: {node_type_display}")
    print(f"  Name: {data['node_name']}")
    print(f"  Fan-In Count: {data['fan_in_count']}")
    print(f"  Fan-Out Count: {fan_out}")
    print(f"  Fan-In/Fan-Out Ratio: {data['fan_in_count']/fan_out if fan_out > 0 else 'N/A (no outgoing)'}")
    
    # Incoming edge type breakdown
    print(f"\n  Incoming Edge Types:")
    for edge_type, count in data['edge_type_counts'].most_common():
        print(f"    • {edge_type}: {count}")
    
    # Source node type breakdown
    print(f"\n  Source Node Types:")
    for source_type, count in data['source_type_counts'].most_common():
        print(f"    • {source_type}: {count}")
    
    # List incoming connections
    print(f"\n  Incoming Connections (showing first 8):")
    for i, pred in enumerate(data['incoming_nodes'][:8], 1):
        pred_data = G.nodes[pred]
        edge_data = G.get_edge_data(pred, node_id)
        edge_type = edge_data.get('edge_type') if edge_data else 'Unknown'
        pred_type_display = pred_data.get('node_type', 'Unknown')
        
        print(f"    {i}. {pred} ({pred_type_display}) --[{edge_type}]--> {node_id}")
    
    if len(data['incoming_nodes']) > 8:
        print(f"    ... and {len(data['incoming_nodes']) - 8} more incoming connections")

if len(high_fan_in_nodes) > 10:
    print(f"\n... and {len(high_fan_in_nodes) - 10} more high fan-in nodes")


# Fraud detection insights
print(f"\n\n{'='*100}")
print("🚨 FRAUD DETECTION INSIGHTS")
print(f"{'='*100}\n")

suspicious_patterns = []

for data in fan_in_data:
    node_id = data['node_id']
    node_type = data['node_type']
    fan_in = data['fan_in_count']
    fan_out = get_fan_out_count(G, node_id)
    
    flags = []
    risk_score = 0
    
    # Pattern 1: High fan-in Account (potential money mule)
    if node_type == 'Account' and fan_in >= 3:
        flags.append(f"High fan-in account ({fan_in} incoming connections) - potential money mule")
        risk_score += 30
    
    # Pattern 2: Device used by multiple customers
    if node_type == 'Device' and fan_in >= 2:
        customer_sources = [t for t in data['incoming_node_types'] if t == 'Customer']
        if len(customer_sources) >= 2:
            flags.append(f"Device used by {len(customer_sources)} customers - potential compromise/sharing")
            risk_score += 40
    
    # Pattern 3: High fan-in, low fan-out (accumulation pattern)
    if fan_in >= 3 and fan_out == 0:
        flags.append(f"High fan-in ({fan_in}) with no outgoing - accumulation pattern")
        risk_score += 25
    
    # Pattern 4: Asymmetric transaction pattern
    if node_type == 'Account':
        to_account_count = data['edge_type_counts'].get('TO_ACCOUNT', 0)
        from_account_count = sum(1 for e in G.out_edges(node_id) if G.get_edge_data(*e).get('edge_type') == 'FROM_ACCOUNT')
        
        if to_account_count >= 3 and from_account_count == 0:
            flags.append(f"Receiving account with {to_account_count} deposits, no withdrawals - potential money mule")
            risk_score += 35
    
    # Pattern 5: Device involved in flagged/blocked transactions
    if node_type == 'Device':
        for pred in data['incoming_nodes']:
            if pred in ['TXN004', 'TXN007']:  # Flagged/blocked transactions
                flags.append(f"Device used in flagged/blocked transaction ({pred})")
                risk_score += 50
    
    # Pattern 6: Connection to high-risk customer
    if 'CUST005' in data['incoming_nodes']:
        flags.append("Connected to high-risk customer (CUST005)")
        risk_score += 20
    
    if flags:
        suspicious_patterns.append({
            'node_id': node_id,
            'node_type': node_type if node_type is not None else 'Unknown',
            'node_name': data['node_name'],
            'fan_in': fan_in,
            'fan_out': fan_out,
            'flags': flags,
            'risk_score': risk_score
        })

# Sort by risk score
suspicious_patterns.sort(key=lambda x: x['risk_score'], reverse=True)

print(f"Found {len(suspicious_patterns)} nodes with suspicious fan-in patterns:\n")

for idx, pattern in enumerate(suspicious_patterns[:15], 1):
    print(f"  {'🔴' if pattern['risk_score'] >= 50 else '🟡'} Suspicious Node #{idx} (Risk Score: {pattern['risk_score']})")
    print(f"     Node: {pattern['node_id']} ({pattern['node_type']}: {pattern['node_name']})")
    print(f"     Fan-In: {pattern['fan_in']}, Fan-Out: {pattern['fan_out']}")
    print(f"     Flags:")
    for flag in pattern['flags']:
        print(f"       - {flag}")
    print()

if len(suspicious_patterns) > 15:
    print(f"  ... and {len(suspicious_patterns) - 15} more suspicious patterns")


# Visualization
print(f"\n{'='*100}")
print("GENERATING FAN-IN VISUALIZATION")
print(f"{'='*100}\n")

fig, axes = plt.subplots(1, 2, figsize=(18, 7))

# Chart 1: Fan-in distribution by node type
ax1 = axes[0]
# Use only valid node types (exclude None)
valid_types = [t for t in fan_in_by_type.keys() if t is not None]
node_types = sorted(valid_types)
avg_fan_ins = [sum(fan_in_by_type[t])/len(fan_in_by_type[t]) for t in node_types]
max_fan_ins = [max(fan_in_by_type[t]) for t in node_types]

x = range(len(node_types))
width = 0.35

bars1 = ax1.bar([i - width/2 for i in x], avg_fan_ins, width, label='Average Fan-In', color='#4ECDC4')
bars2 = ax1.bar([i + width/2 for i in x], max_fan_ins, width, label='Max Fan-In', color='#FF6B6B')

ax1.set_xlabel('Node Type', fontsize=12, fontweight='bold')
ax1.set_ylabel('Fan-In Count', fontsize=12, fontweight='bold')
ax1.set_title('Fan-In Distribution by Node Type', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(node_types, rotation=45, ha='right')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=9)

# Chart 2: Top 10 nodes by fan-in
ax2 = axes[1]
top_10 = fan_in_data_sorted[:10]
node_labels = [f"{d['node_id']}\n({d['node_type'] if d['node_type'] is not None else 'Unknown'})" for d in top_10]
fan_in_values = [d['fan_in_count'] for d in top_10]

# Color by node type
colors = {'Customer': '#FF6B6B', 'Account': '#4ECDC4', 'Transaction': '#45B7D1', 'Device': '#FFA07A'}
bar_colors = [colors.get(d['node_type'], '#CCCCCC') for d in top_10]

bars = ax2.barh(range(len(top_10)), fan_in_values, color=bar_colors)
ax2.set_yticks(range(len(top_10)))
ax2.set_yticklabels(node_labels, fontsize=9)
ax2.set_xlabel('Fan-In Count', fontsize=12, fontweight='bold')
ax2.set_title('Top 10 Nodes by Fan-In', fontsize=14, fontweight='bold')
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, fan_in_values)):
    ax2.text(val + 0.1, i, str(val), va='center', fontsize=10, fontweight='bold')

# Add legend for node types
legend_elements = [mpatches.Patch(color=color, label=node_type) 
                   for node_type, color in colors.items()]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=9)

plt.tight_layout()
plt.show()

print("Visualization generated!\n")

print("="*100)
print("✅ FAN-IN DETECTION ANALYSIS COMPLETE")
print("="*100)
