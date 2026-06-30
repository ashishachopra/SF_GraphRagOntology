# Cycle detection (7-hop) analysis on knowledge graph from KG_NODE and KG_EDGE tables

from snowflake.snowpark.context import get_active_session
import pandas as pd
import networkx as nx
from collections import defaultdict, Counter
import json

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
print("CYCLE DETECTION - 7 HOP ANALYSIS")
print("="*100)


def detect_cycles_from_node(graph, start_node, max_depth=7):
    """
    Detect all cycles starting from a given node up to max_depth hops.
    Returns list of cycles (each cycle is a list of nodes forming the cycle).
    """
    cycles = []
    visited_in_path = set()
    
    def dfs(current, path, depth):
        if depth > max_depth:
            return
        
        # Check if we've returned to the start node (cycle found)
        if len(path) > 1 and current == start_node:
            cycles.append(path[:])
            return
        
        # Avoid revisiting nodes in the current path (except for closing the cycle)
        if current in visited_in_path:
            return
        
        visited_in_path.add(current)
        
        # Explore neighbors
        for neighbor in graph.successors(current):
            dfs(neighbor, path + [neighbor], depth + 1)
        
        visited_in_path.remove(current)
    
    # Start DFS from the start node
    dfs(start_node, [start_node], 0)
    
    return cycles


def analyze_cycle(graph, cycle):
    """
    Analyze a cycle and return detailed information about nodes and edges.
    """
    cycle_info = {
        'length': len(cycle) - 1,  # Exclude the repeated start node
        'nodes': cycle,
        'node_types': [],
        'edge_types': [],
        'path_details': []
    }
    
    for i in range(len(cycle) - 1):
        src = cycle[i]
        dst = cycle[i + 1]
        
        src_data = graph.nodes[src]
        dst_data = graph.nodes[dst]
        edge_data = graph.get_edge_data(src, dst)
        
        cycle_info['node_types'].append(src_data.get('node_type'))
        cycle_info['edge_types'].append(edge_data.get('edge_type') if edge_data else 'Unknown')
        
        cycle_info['path_details'].append({
            'from_id': src,
            'from_name': src_data.get('name'),
            'from_type': src_data.get('node_type'),
            'to_id': dst,
            'to_name': dst_data.get('name'),
            'to_type': dst_data.get('node_type'),
            'relationship': edge_data.get('edge_type') if edge_data else 'Unknown'
        })
    
    # Create a signature for the cycle (sorted to identify duplicates)
    cycle_info['signature'] = tuple(sorted(cycle[:-1]))
    
    return cycle_info


def get_cycle_type(cycle_info):
    """
    Classify the type of cycle based on node types involved.
    """
    node_types = set(cycle_info['node_types'])
    
    if node_types == {'Customer', 'Account'}:
        return 'Customer-Account Cycle'
    elif node_types == {'Customer', 'Device'}:
        return 'Customer-Device Cycle'
    elif 'Transaction' in node_types and 'Account' in node_types:
        return 'Transaction-Account Cycle'
    elif 'Customer' in node_types and 'Transaction' in node_types:
        return 'Customer-Transaction Cycle'
    elif len(node_types) >= 3:
        return 'Multi-Entity Cycle'
    else:
        return 'Other Cycle'


# Detect cycles from all nodes
print(f"\n🔍 Detecting cycles up to 7 hops from all {len(G.nodes())} nodes...\n")

all_cycles = []
cycles_by_start_node = {}

for node in G.nodes():
    node_cycles = detect_cycles_from_node(G, node, max_depth=7)
    if node_cycles:
        cycles_by_start_node[node] = node_cycles
        all_cycles.extend([(node, cycle) for cycle in node_cycles])

print(f"✅ Detection complete! Found {len(all_cycles)} cycle instances.\n")

# Analyze and deduplicate cycles
print("="*100)
print("CYCLE ANALYSIS")
print("="*100)

analyzed_cycles = []
unique_cycles = {}

for start_node, cycle in all_cycles:
    cycle_info = analyze_cycle(G, cycle)
    cycle_info['start_node'] = start_node
    analyzed_cycles.append(cycle_info)
    
    # Track unique cycles by signature
    sig = cycle_info['signature']
    if sig not in unique_cycles:
        unique_cycles[sig] = cycle_info

print(f"\n📊 CYCLE STATISTICS:")
print(f"  Total cycle instances found: {len(analyzed_cycles)}")
print(f"  Unique cycles (deduplicated): {len(unique_cycles)}")

# Group by cycle length
cycles_by_length = defaultdict(list)
for cycle_info in unique_cycles.values():
    cycles_by_length[cycle_info['length']].append(cycle_info)

print(f"\n📏 CYCLES BY LENGTH:")
for length in sorted(cycles_by_length.keys()):
    print(f"  {length}-hop cycles: {len(cycles_by_length[length])}")

# Group by cycle type
cycles_by_type = defaultdict(list)
for cycle_info in unique_cycles.values():
    cycle_type = get_cycle_type(cycle_info)
    cycles_by_type[cycle_type].append(cycle_info)

print(f"\n🏷️  CYCLES BY TYPE:")
for cycle_type in sorted(cycles_by_type.keys()):
    print(f"  {cycle_type}: {len(cycles_by_type[cycle_type])}")

# Edge type patterns in cycles
edge_patterns = Counter()
for cycle_info in unique_cycles.values():
    pattern = ' -> '.join(cycle_info['edge_types'])
    edge_patterns[pattern] += 1

print(f"\n🔗 TOP EDGE PATTERNS IN CYCLES:")
for pattern, count in edge_patterns.most_common(5):
    print(f"  {pattern}: {count} cycles")


# Detailed cycle report
print(f"\n\n{'='*100}")
print("DETAILED CYCLE REPORT (Showing unique cycles up to 5-hop)")
print(f"{'='*100}\n")

for length in sorted(cycles_by_length.keys()):
    if length > 5:  # Only show up to 5-hop in detail
        continue
    
    cycles = cycles_by_length[length]
    print(f"\n{'─'*100}")
    print(f"📍 {length}-HOP CYCLES ({len(cycles)} unique cycles)")
    print(f"{'─'*100}")
    
    for idx, cycle_info in enumerate(cycles[:5], 1):  # Show first 5 of each length
        cycle_type = get_cycle_type(cycle_info)
        print(f"\n  Cycle #{idx} - {cycle_type}")
        print(f"  Cycle length: {length} hops")
        print(f"  Nodes: {' → '.join(cycle_info['nodes'])}")
        print(f"\n  Path details:")
        
        for step_idx, step in enumerate(cycle_info['path_details'], 1):
            print(f"    Step {step_idx}: {step['from_id']} ({step['from_type']}: {step['from_name']})")
            print(f"            --[{step['relationship']}]-->")
            print(f"            {step['to_id']} ({step['to_type']}: {step['to_name']})")
        
        if idx < len(cycles):
            print()
    
    if len(cycles) > 5:
        print(f"\n  ... and {len(cycles) - 5} more {length}-hop cycles")


# Fraud detection insights
print(f"\n\n{'='*100}")
print("🚨 FRAUD DETECTION INSIGHTS")
print(f"{'='*100}\n")

# Look for suspicious cycle patterns
suspicious_cycles = []

for cycle_info in unique_cycles.values():
    # Check for cycles involving flagged/blocked transactions
    path_str = ' -> '.join([step['from_id'] for step in cycle_info['path_details']])
    
    # Check if cycle involves suspicious nodes
    suspicious = False
    reasons = []
    
    for step in cycle_info['path_details']:
        if 'TXN004' in step['from_id'] or 'TXN007' in step['from_id']:  # Flagged/blocked transactions
            suspicious = True
            reasons.append(f"Contains flagged/blocked transaction: {step['from_id']}")
        
        if 'CUST005' in step['from_id']:  # High-risk customer
            suspicious = True
            reasons.append(f"Contains high-risk customer: CUST005")
    
    # Check for rapid round-trip patterns (money laundering indicator)
    if 'Account' in cycle_info['node_types'] and cycle_info['length'] <= 4:
        if 'FROM_ACCOUNT' in cycle_info['edge_types'] and 'TO_ACCOUNT' in cycle_info['edge_types']:
            suspicious = True
            reasons.append("Rapid account round-trip detected (possible layering)")
    
    if suspicious:
        suspicious_cycles.append({
            'cycle_info': cycle_info,
            'reasons': reasons
        })

print(f"Found {len(suspicious_cycles)} cycles with suspicious patterns:\n")

for idx, item in enumerate(suspicious_cycles[:10], 1):  # Show first 10
    cycle_info = item['cycle_info']
    reasons = item['reasons']
    
    print(f"  🔴 Suspicious Cycle #{idx}")
    print(f"     Length: {cycle_info['length']} hops")
    print(f"     Nodes: {' → '.join(cycle_info['nodes'])}")
    print(f"     Reasons:")
    for reason in reasons:
        print(f"       - {reason}")
    print()

if len(suspicious_cycles) > 10:
    print(f"  ... and {len(suspicious_cycles) - 10} more suspicious cycles")


# Node involvement in cycles
print(f"\n\n{'='*100}")
print("📊 NODE INVOLVEMENT IN CYCLES")
print(f"{'='*100}\n")

node_cycle_count = Counter()
for cycle_info in unique_cycles.values():
    for node in cycle_info['nodes'][:-1]:  # Exclude the repeated end node
        node_cycle_count[node] += 1

print(f"Top 10 nodes by cycle involvement:\n")
print(f"{'Node ID':<15} {'Name':<30} {'Type':<15} {'Cycle Count':<15}")
print("-" * 75)

for node_id, count in node_cycle_count.most_common(10):
    node_data = G.nodes[node_id]
    print(f"{node_id:<15} {node_data.get('name'):<30} {node_data.get('node_type'):<15} {count:<15}")


print(f"\n\n{'='*100}")
print("✅ CYCLE DETECTION 7-HOP ANALYSIS COMPLETE")
print(f"{'='*100}")
