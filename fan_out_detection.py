# Fan-out detection analysis on knowledge graph from KG_NODE and KG_EDGE tables
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
print("FAN-OUT DETECTION ANALYSIS")
print("="*100)
print("\nFan-out = Number of outgoing edges from a node")
print("High fan-out nodes may indicate:")
print("  • Money laundering hubs (distributing funds to many destinations)")
print("  • Compromised customer accounts (initiating many transactions)")
print("  • Bot/automated transaction sources")
print("  • High-volume transaction originators")
print("  • Phishing/scam accounts spreading to multiple victims\n")


def calculate_fan_out_metrics(graph):
    """
    Calculate comprehensive fan-out metrics for all nodes.
    """
    fan_out_data = []
    
    for node in graph.nodes():
        node_data = graph.nodes[node]
        
        # Get all outgoing edges
        successors = list(graph.successors(node))
        out_degree = len(successors)
        
        # Analyze outgoing edge types
        outgoing_edge_types = []
        destination_node_types = []
        
        for succ in successors:
            edge_data = graph.get_edge_data(node, succ)
            succ_data = graph.nodes[succ]
            
            if edge_data:
                outgoing_edge_types.append(edge_data.get('edge_type', 'Unknown'))
            destination_node_types.append(succ_data.get('node_type', 'Unknown'))
        
        fan_out_data.append({
            'node_id': node,
            'node_type': node_data.get('node_type'),
            'node_name': node_data.get('name'),
            'fan_out_count': out_degree,
            'outgoing_nodes': successors,
            'outgoing_edge_types': outgoing_edge_types,
            'destination_node_types': destination_node_types,
            'edge_type_counts': Counter(outgoing_edge_types),
            'destination_type_counts': Counter(destination_node_types)
        })
    
    return fan_out_data


def get_fan_in_count(graph, node):
    """Get fan-in (incoming edges) for comparison."""
    return len(list(graph.predecessors(node)))


# Calculate fan-out metrics
print("Calculating fan-out metrics for all nodes...")
fan_out_data = calculate_fan_out_metrics(G)

# Sort by fan-out count
fan_out_data_sorted = sorted(fan_out_data, key=lambda x: x['fan_out_count'], reverse=True)

print(f"✅ Analysis complete!\n")


# Overall statistics
print("="*100)
print("OVERALL FAN-OUT STATISTICS")
print("="*100)

total_nodes = len(fan_out_data)
nodes_with_fan_out = len([d for d in fan_out_data if d['fan_out_count'] > 0])
avg_fan_out = sum(d['fan_out_count'] for d in fan_out_data) / total_nodes if total_nodes > 0 else 0
max_fan_out = max(d['fan_out_count'] for d in fan_out_data) if fan_out_data else 0

print(f"\n📊 Summary:")
print(f"  Total nodes: {total_nodes}")
print(f"  Nodes with outgoing edges: {nodes_with_fan_out} ({nodes_with_fan_out/total_nodes*100:.1f}%)")
print(f"  Nodes with no outgoing edges: {total_nodes - nodes_with_fan_out}")
print(f"  Average fan-out: {avg_fan_out:.2f}")
print(f"  Maximum fan-out: {max_fan_out}")


# Fan-out distribution by node type
print(f"\n\n📈 FAN-OUT BY NODE TYPE:")
print(f"{'Node Type':<15} {'Avg Fan-Out':<15} {'Max Fan-Out':<15} {'Total Nodes':<15}")
print("-" * 60)

fan_out_by_type = defaultdict(list)
for data in fan_out_data:
    fan_out_by_type[data['node_type']].append(data['fan_out_count'])

# Filter out None keys and sort
valid_node_types = [nt for nt in fan_out_by_type.keys() if nt is not None]
for node_type in sorted(valid_node_types):
    counts = fan_out_by_type[node_type]
    avg = sum(counts) / len(counts) if counts else 0
    max_val = max(counts) if counts else 0
    print(f"{node_type:<15} {avg:<15.2f} {max_val:<15} {len(counts):<15}")

# Handle None node types separately if they exist
if None in fan_out_by_type:
    counts = fan_out_by_type[None]
    avg = sum(counts) / len(counts) if counts else 0
    max_val = max(counts) if counts else 0
    print(f"{'(Unknown)':<15} {avg:<15.2f} {max_val:<15} {len(counts):<15}")


# Top nodes by fan-out
print(f"\n\n{'='*100}")
print("TOP NODES BY FAN-OUT (Potential High-Risk Distributors)")
print(f"{'='*100}\n")

print(f"{'Rank':<6} {'Node ID':<12} {'Type':<12} {'Name':<30} {'Fan-Out':<10} {'Fan-In':<10}")
print("-" * 90)

for rank, data in enumerate(fan_out_data_sorted[:15], 1):
    node_id = data['node_id']
    fan_in = get_fan_in_count(G, node_id)
    node_type_display = data['node_type'] if data['node_type'] is not None else 'Unknown'
    
    print(f"{rank:<6} {node_id:<12} {node_type_display:<12} {data['node_name']:<30} "
          f"{data['fan_out_count']:<10} {fan_in:<10}")


# Detailed analysis of high fan-out nodes
print(f"\n\n{'='*100}")
print("DETAILED HIGH FAN-OUT ANALYSIS")
print(f"{'='*100}")

# Define threshold for "high" fan-out (top 20% or minimum of 3)
fan_out_counts = [d['fan_out_count'] for d in fan_out_data if d['fan_out_count'] > 0]
if fan_out_counts:
    threshold = max(3, sorted(fan_out_counts, reverse=True)[min(len(fan_out_counts)//5, len(fan_out_counts)-1)])
else:
    threshold = 3

high_fan_out_nodes = [d for d in fan_out_data_sorted if d['fan_out_count'] >= threshold]

print(f"\nAnalyzing {len(high_fan_out_nodes)} nodes with fan-out >= {threshold}\n")

for idx, data in enumerate(high_fan_out_nodes[:10], 1):  # Show top 10 in detail
    node_id = data['node_id']
    fan_in = get_fan_in_count(G, node_id)
    node_type_display = data['node_type'] if data['node_type'] is not None else 'Unknown'
    
    print(f"\n{'─'*100}")
    print(f"🔍 High Fan-Out Node #{idx}")
    print(f"{'─'*100}")
    print(f"  Node ID: {node_id}")
    print(f"  Type: {node_type_display}")
    print(f"  Name: {data['node_name']}")
    print(f"  Fan-Out Count: {data['fan_out_count']}")
    print(f"  Fan-In Count: {fan_in}")
    print(f"  Fan-Out/Fan-In Ratio: {data['fan_out_count']/fan_in if fan_in > 0 else 'N/A (no incoming)'}")
    
    # Outgoing edge type breakdown
    print(f"\n  Outgoing Edge Types:")
    for edge_type, count in data['edge_type_counts'].most_common():
        print(f"    • {edge_type}: {count}")
    
    # Destination node type breakdown
    print(f"\n  Destination Node Types:")
    for dest_type, count in data['destination_type_counts'].most_common():
        print(f"    • {dest_type}: {count}")
    
    # List outgoing connections
    print(f"\n  Outgoing Connections (showing first 8):")
    for i, succ in enumerate(data['outgoing_nodes'][:8], 1):
        succ_data = G.nodes[succ]
        edge_data = G.get_edge_data(node_id, succ)
        edge_type = edge_data.get('edge_type') if edge_data else 'Unknown'
        succ_type_display = succ_data.get('node_type', 'Unknown')
        
        print(f"    {i}. {node_id} --[{edge_type}]--> {succ} ({succ_type_display})")
    
    if len(data['outgoing_nodes']) > 8:
        print(f"    ... and {len(data['outgoing_nodes']) - 8} more outgoing connections")

if len(high_fan_out_nodes) > 10:
    print(f"\n... and {len(high_fan_out_nodes) - 10} more high fan-out nodes")


# Fraud detection insights
print(f"\n\n{'='*100}")
print("🚨 FRAUD DETECTION INSIGHTS")
print(f"{'='*100}\n")

suspicious_patterns = []

for data in fan_out_data:
    node_id = data['node_id']
    node_type = data['node_type']
    fan_out = data['fan_out_count']
    fan_in = get_fan_in_count(G, node_id)
    
    flags = []
    risk_score = 0
    
    # Pattern 1: High fan-out Customer (potential compromised account or money launderer)
    if node_type == 'Customer' and fan_out >= 5:
        flags.append(f"High fan-out customer ({fan_out} outgoing connections) - potential compromised or laundering account")
        risk_score += 40
    
    # Pattern 2: Account with many outgoing transfers (potential layering)
    if node_type == 'Account' and fan_out >= 5:
        transfer_count = data['edge_type_counts'].get('TRANSFERRED_TO', 0)
        if transfer_count >= 3:
            flags.append(f"Account with {transfer_count} outgoing transfers - potential layering activity")
            risk_score += 45
    
    # Pattern 3: High fan-out, low/no fan-in (funds originating pattern)
    if fan_out >= 5 and fan_in <= 1:
        flags.append(f"High fan-out ({fan_out}) with low/no incoming - funds originating pattern")
        risk_score += 30
    
    # Pattern 4: Device initiating many transactions
    if node_type == 'Device' and fan_out >= 5:
        flags.append(f"Device initiating {fan_out} transactions - potential bot/automated activity")
        risk_score += 35
    
    # Pattern 5: Customer referring many others (potential fraud ring recruiter)
    if node_type == 'Customer':
        referral_count = data['edge_type_counts'].get('REFERRED', 0)
        if referral_count >= 5:
            flags.append(f"Customer referred {referral_count} others - potential fraud ring recruiter")
            risk_score += 50
    
    # Pattern 6: Transaction spreading to multiple accounts
    if node_type == 'Transaction' and fan_out >= 3:
        flags.append(f"Transaction connected to {fan_out} accounts - potential split transaction for structuring")
        risk_score += 40
    
    # Pattern 7: Asymmetric transaction pattern (disbursement)
    if node_type == 'Account':
        transacted_count = data['edge_type_counts'].get('TRANSACTED', 0)
        if transacted_count >= 5 and fan_in <= 1:
            flags.append(f"Account with {transacted_count} outgoing transactions, minimal incoming - rapid disbursement pattern")
            risk_score += 35
    
    # Pattern 8: Rapid fan-out from new customer
    if node_type == 'Customer' and fan_out >= 3:
        # Check if owns multiple accounts
        owns_count = data['edge_type_counts'].get('OWNS', 0)
        if owns_count >= 3:
            flags.append(f"New customer owns {owns_count} accounts - potential money mule setup")
            risk_score += 40
    
    if flags:
        suspicious_patterns.append({
            'node_id': node_id,
            'node_type': node_type if node_type is not None else 'Unknown',
            'node_name': data['node_name'],
            'fan_out': fan_out,
            'fan_in': fan_in,
            'flags': flags,
            'risk_score': risk_score
        })

# Sort by risk score
suspicious_patterns.sort(key=lambda x: x['risk_score'], reverse=True)

print(f"Found {len(suspicious_patterns)} nodes with suspicious fan-out patterns:\n")

for idx, pattern in enumerate(suspicious_patterns[:20], 1):
    print(f"  {'🔴' if pattern['risk_score'] >= 50 else '🟡'} Suspicious Node #{idx} (Risk Score: {pattern['risk_score']})")
    print(f"     Node: {pattern['node_id']} ({pattern['node_type']}: {pattern['node_name']})")
    print(f"     Fan-Out: {pattern['fan_out']}, Fan-In: {pattern['fan_in']}")
    print(f"     Flags:")
    for flag in pattern['flags']:
        print(f"       - {flag}")
    print()

if len(suspicious_patterns) > 20:
    print(f"  ... and {len(suspicious_patterns) - 20} more suspicious patterns")


# Fan-out/Fan-in ratio analysis
print(f"\n{'='*100}")
print("FAN-OUT/FAN-IN RATIO ANALYSIS")
print(f"{'='*100}\n")

print("Analyzing nodes by their distribution vs accumulation patterns...\n")

high_ratio_nodes = []
for data in fan_out_data:
    node_id = data['node_id']
    fan_out = data['fan_out_count']
    fan_in = get_fan_in_count(G, node_id)
    
    if fan_in > 0 and fan_out > 0:
        ratio = fan_out / fan_in
        if ratio >= 2.0:  # Significant distribution pattern
            high_ratio_nodes.append({
                'node_id': node_id,
                'node_type': data['node_type'] if data['node_type'] is not None else 'Unknown',
                'node_name': data['node_name'],
                'fan_out': fan_out,
                'fan_in': fan_in,
                'ratio': ratio
            })

high_ratio_nodes.sort(key=lambda x: x['ratio'], reverse=True)

print(f"Found {len(high_ratio_nodes)} nodes with fan-out/fan-in ratio >= 2.0 (strong distribution pattern)\n")
print(f"{'Rank':<6} {'Node ID':<12} {'Type':<12} {'Fan-Out':<10} {'Fan-In':<10} {'Ratio':<10}")
print("-" * 70)

for rank, node in enumerate(high_ratio_nodes[:15], 1):
    print(f"{rank:<6} {node['node_id']:<12} {node['node_type']:<12} {node['fan_out']:<10} "
          f"{node['fan_in']:<10} {node['ratio']:<10.2f}")


# Visualization
print(f"\n\n{'='*100}")
print("GENERATING FAN-OUT VISUALIZATION")
print(f"{'='*100}\n")

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Chart 1: Fan-out distribution by node type
ax1 = axes[0, 0]
valid_types = [t for t in fan_out_by_type.keys() if t is not None]
node_types = sorted(valid_types)
avg_fan_outs = [sum(fan_out_by_type[t])/len(fan_out_by_type[t]) for t in node_types]
max_fan_outs = [max(fan_out_by_type[t]) for t in node_types]

x = range(len(node_types))
width = 0.35

bars1 = ax1.bar([i - width/2 for i in x], avg_fan_outs, width, label='Average Fan-Out', color='#FF6B6B')
bars2 = ax1.bar([i + width/2 for i in x], max_fan_outs, width, label='Max Fan-Out', color='#4ECDC4')

ax1.set_xlabel('Node Type', fontsize=12, fontweight='bold')
ax1.set_ylabel('Fan-Out Count', fontsize=12, fontweight='bold')
ax1.set_title('Fan-Out Distribution by Node Type', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(node_types, rotation=45, ha='right')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=9)

# Chart 2: Top 10 nodes by fan-out
ax2 = axes[0, 1]
top_10 = fan_out_data_sorted[:10]
node_labels = [f"{d['node_id']}\n({d['node_type'] if d['node_type'] is not None else 'Unknown'})" for d in top_10]
fan_out_values = [d['fan_out_count'] for d in top_10]

colors = {'Customer': '#FF6B6B', 'Account': '#4ECDC4', 'Transaction': '#45B7D1', 'Device': '#FFA07A'}
bar_colors = [colors.get(d['node_type'], '#CCCCCC') for d in top_10]

bars = ax2.barh(range(len(top_10)), fan_out_values, color=bar_colors)
ax2.set_yticks(range(len(top_10)))
ax2.set_yticklabels(node_labels, fontsize=9)
ax2.set_xlabel('Fan-Out Count', fontsize=12, fontweight='bold')
ax2.set_title('Top 10 Nodes by Fan-Out', fontsize=14, fontweight='bold')
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

for i, (bar, val) in enumerate(zip(bars, fan_out_values)):
    ax2.text(val + 0.1, i, str(val), va='center', fontsize=10, fontweight='bold')

legend_elements = [mpatches.Patch(color=color, label=node_type) 
                   for node_type, color in colors.items()]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=9)

# Chart 3: Fan-out vs Fan-in scatter
ax3 = axes[1, 0]
scatter_data = []
for data in fan_out_data:
    node_id = data['node_id']
    fan_out = data['fan_out_count']
    fan_in = get_fan_in_count(G, node_id)
    node_type = data['node_type']
    if fan_out > 0 or fan_in > 0:
        scatter_data.append({'fan_out': fan_out, 'fan_in': fan_in, 'node_type': node_type})

for node_type, color in colors.items():
    type_data = [d for d in scatter_data if d['node_type'] == node_type]
    if type_data:
        x_vals = [d['fan_in'] for d in type_data]
        y_vals = [d['fan_out'] for d in type_data]
        ax3.scatter(x_vals, y_vals, c=color, label=node_type, alpha=0.6, s=30)

ax3.set_xlabel('Fan-In (Incoming)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Fan-Out (Outgoing)', fontsize=12, fontweight='bold')
ax3.set_title('Fan-Out vs Fan-In Distribution', fontsize=14, fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(alpha=0.3)

# Add diagonal line (fan-out = fan-in)
max_val = max(ax3.get_xlim()[1], ax3.get_ylim()[1])
ax3.plot([0, max_val], [0, max_val], 'k--', alpha=0.3, linewidth=1, label='Fan-Out = Fan-In')

# Chart 4: Risk score distribution
ax4 = axes[1, 1]
if suspicious_patterns:
    risk_scores = [p['risk_score'] for p in suspicious_patterns]
    ax4.hist(risk_scores, bins=20, color='#FF6B6B', alpha=0.7, edgecolor='black')
    ax4.axvline(x=50, color='red', linestyle='--', linewidth=2, label='High Risk Threshold (50)')
    ax4.set_xlabel('Risk Score', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Number of Nodes', fontsize=12, fontweight='bold')
    ax4.set_title('Distribution of Risk Scores', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print("Visualization generated!\n")

print("="*100)
print("✅ FAN-OUT DETECTION ANALYSIS COMPLETE")
print("="*100)
