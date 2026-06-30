# Deep traversal (10-hop) analysis on knowledge graph from KG_NODE and KG_EDGE tables

from snowflake.snowpark.context import get_active_session
import pandas as pd
import networkx as nx
from collections import defaultdict, deque
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
print("T1 DEEP TRAVERSAL - 10 HOP ANALYSIS")
print("="*100)

def bfs_n_hop_traversal(graph, start_node, max_hops=10):
    """
    Perform breadth-first search up to N hops from start node.
    Returns nodes discovered at each hop level and paths.
    """
    if start_node not in graph:
        return None, None
    
    visited = {start_node: 0}  # node: hop_distance
    queue = deque([(start_node, 0, [start_node])])  # (node, distance, path)
    
    nodes_by_hop = defaultdict(list)
    paths_by_hop = defaultdict(list)
    
    nodes_by_hop[0].append(start_node)
    
    while queue:
        current_node, distance, path = queue.popleft()
        
        if distance >= max_hops:
            continue
        
        # Explore neighbors
        for neighbor in graph.successors(current_node):
            if neighbor not in visited or visited[neighbor] > distance + 1:
                visited[neighbor] = distance + 1
                new_path = path + [neighbor]
                
                queue.append((neighbor, distance + 1, new_path))
                nodes_by_hop[distance + 1].append(neighbor)
                paths_by_hop[distance + 1].append(new_path)
    
    return nodes_by_hop, paths_by_hop, visited


def analyze_path(graph, path):
    """Analyze a path and return detailed information."""
    path_info = []
    for i in range(len(path) - 1):
        src = path[i]
        dst = path[i + 1]
        edge_data = graph.get_edge_data(src, dst)
        
        src_data = graph.nodes[src]
        dst_data = graph.nodes[dst]
        
        path_info.append({
            'from': src,
            'from_type': src_data.get('node_type'),
            'from_name': src_data.get('name'),
            'to': dst,
            'to_type': dst_data.get('node_type'),
            'to_name': dst_data.get('name'),
            'relationship': edge_data.get('edge_type') if edge_data else 'Unknown'
        })
    
    return path_info


# Run traversal for each customer (common starting point for fraud analysis)
customers = [node for node, attr in G.nodes(data=True) if attr.get('node_type') == 'Customer']

print(f"\nPerforming 10-hop traversal from {len(customers)} customer nodes...\n")

all_results = {}

for customer_id in customers:
    customer_name = G.nodes[customer_id]['name']
    
    print(f"\n{'='*100}")
    print(f"STARTING NODE: {customer_id} ({customer_name})")
    print(f"{'='*100}")
    
    nodes_by_hop, paths_by_hop, visited = bfs_n_hop_traversal(G, customer_id, max_hops=10)
    
    if nodes_by_hop is None:
        print(f"  Node {customer_id} not found in graph.")
        continue
    
    # Summary statistics
    print(f"\n📊 REACHABILITY SUMMARY:")
    print(f"  Total nodes reached: {len(visited)}")
    print(f"  Maximum hops with connections: {max(nodes_by_hop.keys()) if nodes_by_hop else 0}")
    
    # Nodes discovered at each hop
    print(f"\n🔍 NODES DISCOVERED BY HOP:")
    for hop in sorted(nodes_by_hop.keys()):
        if hop == 0:
            continue
        
        nodes = list(set(nodes_by_hop[hop]))  # Remove duplicates
        print(f"\n  Hop {hop}: {len(nodes)} nodes")
        
        # Group by node type
        type_counts = defaultdict(int)
        for node in nodes:
            node_type = G.nodes[node].get('node_type', 'Unknown')
            type_counts[node_type] += 1
        
        for node_type, count in sorted(type_counts.items()):
            print(f"    - {node_type}: {count}")
        
        # Show sample nodes
        if len(nodes) <= 5:
            for node in nodes:
                node_data = G.nodes[node]
                print(f"      • {node} ({node_data.get('name')})")
    
    # Analyze interesting paths
    print(f"\n🛤️  SAMPLE PATHS TO HOP 3+:")
    max_hop_to_show = min(4, max(paths_by_hop.keys()) if paths_by_hop else 0)
    
    for hop in range(3, max_hop_to_show + 1):
        if hop in paths_by_hop and paths_by_hop[hop]:
            # Show first 3 paths at this hop
            sample_paths = paths_by_hop[hop][:3]
            print(f"\n  Paths to Hop {hop} (showing {len(sample_paths)} of {len(paths_by_hop[hop])}):")
            
            for idx, path in enumerate(sample_paths, 1):
                print(f"\n    Path #{idx}:")
                path_analysis = analyze_path(G, path)
                
                for step_idx, step in enumerate(path_analysis, 1):
                    print(f"      Step {step_idx}: {step['from']} ({step['from_type']}) "
                          f"--[{step['relationship']}]--> "
                          f"{step['to']} ({step['to_type']})")
    
    # Store results
    all_results[customer_id] = {
        'name': customer_name,
        'total_reachable': len(visited),
        'max_hop': max(nodes_by_hop.keys()) if nodes_by_hop else 0,
        'nodes_by_hop': {k: len(set(v)) for k, v in nodes_by_hop.items()}
    }

# Final summary
print(f"\n\n{'='*100}")
print("OVERALL TRAVERSAL SUMMARY")
print(f"{'='*100}\n")

print("Customer Connectivity Analysis:")
print(f"{'Customer ID':<15} {'Name':<25} {'Reachable Nodes':<20} {'Max Hop':<10}")
print("-" * 70)

for cust_id, data in all_results.items():
    print(f"{cust_id:<15} {data['name']:<25} {data['total_reachable']:<20} {data['max_hop']:<10}")

# Graph-level analysis
print(f"\n\n📈 GRAPH-LEVEL METRICS:")
print(f"  Graph Diameter (longest shortest path): {nx.diameter(G) if nx.is_strongly_connected(G) else 'N/A (not strongly connected)'}")

# Find weakly connected components
wcc = list(nx.weakly_connected_components(G))
print(f"  Weakly Connected Components: {len(wcc)}")
print(f"  Largest Component Size: {len(max(wcc, key=len))}")

# Average path length within largest component
# FIX: Check if the largest component is strongly connected before calculating average shortest path
largest_component = G.subgraph(max(wcc, key=len))
if len(largest_component) > 1:
    # For directed graphs, need to check strong connectivity
    if nx.is_strongly_connected(largest_component):
        avg_path = nx.average_shortest_path_length(largest_component)
        print(f"  Average Shortest Path Length (largest component): {avg_path:.2f}")
    else:
        # Use undirected version of the graph for average path calculation
        largest_component_undirected = largest_component.to_undirected()
        if nx.is_connected(largest_component_undirected):
            avg_path = nx.average_shortest_path_length(largest_component_undirected)
            print(f"  Average Shortest Path Length (largest component, treating as undirected): {avg_path:.2f}")
        else:
            print(f"  Average Shortest Path Length (largest component): N/A (component not connected)")

print("\n" + "="*100)
print("✅ T1 10-HOP DEEP TRAVERSAL ANALYSIS COMPLETE")
print("="*100)
