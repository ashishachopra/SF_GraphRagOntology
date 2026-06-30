# Cluster detection analysis on knowledge graph from KG_NODE and KG_EDGE tables
from snowflake.snowpark.context import get_active_session
import pandas as pd
import networkx as nx
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime

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
print("CLUSTER DETECTION FOR FRAUD RING IDENTIFICATION")
print("="*100)
print("\nCluster Detection Objectives:")
print("  • Identify tightly-connected groups of entities (fraud rings)")
print("  • Detect money laundering networks")
print("  • Find organized crime syndicates")
print("  • Uncover synthetic identity fraud rings")
print("  • Analyze suspicious collusion patterns")
print("  • Map account takeover networks\n")


def detect_connected_components(graph):
    """
    Find connected components in the graph (both weakly and strongly connected).
    """
    print("Detecting connected components...")
    
    # Weakly connected components (ignoring edge direction)
    undirected_graph = graph.to_undirected()
    weak_components = list(nx.connected_components(undirected_graph))
    
    # Strongly connected components (respecting edge direction)
    strong_components = list(nx.strongly_connected_components(graph))
    
    print(f"  Found {len(weak_components)} weakly connected components")
    print(f"  Found {len(strong_components)} strongly connected components\n")
    
    return weak_components, strong_components


def analyze_cluster_characteristics(graph, cluster_nodes):
    """
    Analyze characteristics of a cluster to assess fraud risk.
    """
    if len(cluster_nodes) < 2:
        return None
    
    subgraph = graph.subgraph(cluster_nodes)
    
    # Node type composition
    node_types = Counter([graph.nodes[n].get('node_type') for n in cluster_nodes])
    
    # Edge type composition
    edge_types = Counter([d.get('edge_type') for u, v, d in subgraph.edges(data=True)])
    
    # Connectivity metrics
    num_nodes = len(cluster_nodes)
    num_edges = subgraph.number_of_edges()
    
    # Density: actual edges / possible edges
    possible_edges = num_nodes * (num_nodes - 1)
    density = num_edges / possible_edges if possible_edges > 0 else 0
    
    # Internal vs external connections
    internal_edges = num_edges
    external_edges = 0
    for node in cluster_nodes:
        # Count edges going outside the cluster
        for neighbor in graph.neighbors(node):
            if neighbor not in cluster_nodes:
                external_edges += 1
        # Count incoming edges from outside
        for predecessor in graph.predecessors(node):
            if predecessor not in cluster_nodes:
                external_edges += 1
    
    # Average degree
    avg_degree = sum(dict(subgraph.degree()).values()) / num_nodes if num_nodes > 0 else 0
    
    # Clustering coefficient (for undirected version)
    undirected_subgraph = subgraph.to_undirected()
    try:
        avg_clustering = nx.average_clustering(undirected_subgraph)
    except:
        avg_clustering = 0
    
    return {
        'size': num_nodes,
        'num_edges': num_edges,
        'density': density,
        'avg_degree': avg_degree,
        'avg_clustering': avg_clustering,
        'internal_edges': internal_edges,
        'external_edges': external_edges,
        'isolation_ratio': internal_edges / (internal_edges + external_edges) if (internal_edges + external_edges) > 0 else 0,
        'node_types': node_types,
        'edge_types': edge_types
    }


def detect_fraud_ring_patterns(graph, cluster_nodes, cluster_stats):
    """
    Analyze cluster for fraud ring indicators.
    """
    if not cluster_stats:
        return []
    
    flags = []
    risk_score = 0
    
    # Pattern 1: High density cluster (tightly connected fraud ring)
    if cluster_stats['density'] > 0.3 and cluster_stats['size'] >= 5:
        flags.append(f"High density ({cluster_stats['density']:.2f}) with {cluster_stats['size']} members - tightly connected fraud ring")
        risk_score += 50
    
    # Pattern 2: Isolated cluster (low external connections)
    if cluster_stats['isolation_ratio'] > 0.8 and cluster_stats['size'] >= 4:
        flags.append(f"Highly isolated cluster ({cluster_stats['isolation_ratio']:.2f}) - insular fraud network")
        risk_score += 40
    
    # Pattern 3: Device sharing across multiple customers
    if cluster_stats['node_types'].get('Device', 0) >= 1 and cluster_stats['node_types'].get('Customer', 0) >= 3:
        flags.append(f"{cluster_stats['node_types']['Customer']} customers sharing {cluster_stats['node_types']['Device']} device(s) - potential account takeover")
        risk_score += 45
    
    # Pattern 4: Circular transaction patterns
    subgraph = graph.subgraph(cluster_nodes)
    try:
        cycles = list(nx.simple_cycles(subgraph))
        if len(cycles) >= 2:
            flags.append(f"{len(cycles)} circular patterns detected - potential money laundering")
            risk_score += 55
    except:
        pass
    
    # Pattern 5: Multiple accounts owned by same customers
    customers_in_cluster = [n for n in cluster_nodes if graph.nodes[n].get('node_type') == 'Customer']
    accounts_in_cluster = [n for n in cluster_nodes if graph.nodes[n].get('node_type') == 'Account']
    
    if len(customers_in_cluster) >= 2 and len(accounts_in_cluster) >= 5:
        # Check if accounts are cross-owned
        ownership_edges = [e for e in subgraph.edges(data=True) if e[2].get('edge_type') == 'OWNS']
        if len(ownership_edges) >= 4:
            flags.append(f"{len(customers_in_cluster)} customers own {len(accounts_in_cluster)} accounts with cross-ownership - synthetic identity ring")
            risk_score += 60
    
    # Pattern 6: High clustering coefficient (everyone connected to everyone)
    if cluster_stats['avg_clustering'] > 0.7 and cluster_stats['size'] >= 4:
        flags.append(f"Very high clustering coefficient ({cluster_stats['avg_clustering']:.2f}) - organized network")
        risk_score += 35
    
    # Pattern 7: Rapid fund movement (many TRANSFERRED_TO edges)
    transfer_count = cluster_stats['edge_types'].get('TRANSFERRED_TO', 0)
    if transfer_count >= 5 and cluster_stats['size'] <= 10:
        flags.append(f"{transfer_count} internal transfers among {cluster_stats['size']} entities - rapid fund movement")
        risk_score += 40
    
    # Pattern 8: Referral ring (customers referring each other)
    referral_count = cluster_stats['edge_types'].get('REFERRED', 0)
    if referral_count >= 3 and len(customers_in_cluster) >= 3:
        flags.append(f"{referral_count} mutual referrals among {len(customers_in_cluster)} customers - potential Ponzi/MLM ring")
        risk_score += 45
    
    return {
        'flags': flags,
        'risk_score': risk_score
    }


def find_key_members(graph, cluster_nodes):
    """
    Identify key/central members of a cluster.
    """
    if len(cluster_nodes) < 2:
        return []
    
    subgraph = graph.subgraph(cluster_nodes)
    
    # Calculate centrality measures
    degree_centrality = nx.degree_centrality(subgraph)
    
    try:
        betweenness_centrality = nx.betweenness_centrality(subgraph)
    except:
        betweenness_centrality = {n: 0 for n in cluster_nodes}
    
    # Combine centrality scores
    key_members = []
    for node in cluster_nodes:
        total_centrality = degree_centrality.get(node, 0) + betweenness_centrality.get(node, 0)
        if total_centrality > 0:
            key_members.append({
                'node_id': node,
                'node_type': graph.nodes[node].get('node_type'),
                'node_name': graph.nodes[node].get('name'),
                'degree_centrality': degree_centrality.get(node, 0),
                'betweenness_centrality': betweenness_centrality.get(node, 0),
                'total_centrality': total_centrality
            })
    
    return sorted(key_members, key=lambda x: x['total_centrality'], reverse=True)


# Detect connected components
weak_components, strong_components = detect_connected_components(G)

# Filter out singleton components (single node)
weak_clusters = [c for c in weak_components if len(c) >= 2]
strong_clusters = [c for c in strong_components if len(c) >= 2]

print(f"Analyzing {len(weak_clusters)} non-trivial weakly connected clusters...")
print(f"Analyzing {len(strong_clusters)} non-trivial strongly connected clusters...\n")

# Analyze each weak cluster
weak_cluster_analysis = []
for idx, cluster_nodes in enumerate(weak_clusters, 1):
    stats = analyze_cluster_characteristics(G, cluster_nodes)
    if stats and stats['size'] >= 3:  # Focus on clusters with 3+ nodes
        fraud_analysis = detect_fraud_ring_patterns(G, cluster_nodes, stats)
        key_members = find_key_members(G, cluster_nodes)
        
        weak_cluster_analysis.append({
            'cluster_id': f"WC{idx:04d}",
            'nodes': list(cluster_nodes),
            'stats': stats,
            'fraud_analysis': fraud_analysis,
            'key_members': key_members[:5]  # Top 5 key members
        })

# Analyze each strong cluster
strong_cluster_analysis = []
for idx, cluster_nodes in enumerate(strong_clusters, 1):
    stats = analyze_cluster_characteristics(G, cluster_nodes)
    if stats and stats['size'] >= 3:
        fraud_analysis = detect_fraud_ring_patterns(G, cluster_nodes, stats)
        key_members = find_key_members(G, cluster_nodes)
        
        strong_cluster_analysis.append({
            'cluster_id': f"SC{idx:04d}",
            'nodes': list(cluster_nodes),
            'stats': stats,
            'fraud_analysis': fraud_analysis,
            'key_members': key_members[:5]
        })

# Sort by risk score
suspicious_weak_clusters = [c for c in weak_cluster_analysis if c['fraud_analysis']['flags']]
suspicious_weak_clusters.sort(key=lambda x: x['fraud_analysis']['risk_score'], reverse=True)

suspicious_strong_clusters = [c for c in strong_cluster_analysis if c['fraud_analysis']['flags']]
suspicious_strong_clusters.sort(key=lambda x: x['fraud_analysis']['risk_score'], reverse=True)

print("✅ Cluster analysis complete!\n")


# RESULTS REPORTING
print("="*100)
print("CLUSTER DETECTION SUMMARY")
print("="*100)

print(f"\n📊 Overall Statistics:")
print(f"  Total nodes in graph: {G.number_of_nodes()}")
print(f"  Total edges in graph: {G.number_of_edges()}")
print(f"  Weakly connected clusters (size ≥ 2): {len(weak_clusters)}")
print(f"  Strongly connected clusters (size ≥ 2): {len(strong_clusters)}")
print(f"  Analyzed clusters (size ≥ 3): {len(weak_cluster_analysis)}")
print(f"  Suspicious clusters identified: {len(suspicious_weak_clusters)}")

if weak_cluster_analysis:
    sizes = [c['stats']['size'] for c in weak_cluster_analysis]
    print(f"\n  Cluster Size Distribution:")
    print(f"    Smallest cluster: {min(sizes)} nodes")
    print(f"    Largest cluster: {max(sizes)} nodes")
    print(f"    Average cluster size: {sum(sizes)/len(sizes):.1f} nodes")
    print(f"    Median cluster size: {sorted(sizes)[len(sizes)//2]} nodes")


print(f"\n\n{'='*100}")
print("🚨 SUSPICIOUS CLUSTERS (POTENTIAL FRAUD RINGS)")
print(f"{'='*100}\n")

print(f"Identified {len(suspicious_weak_clusters)} suspicious clusters:\n")

for rank, cluster in enumerate(suspicious_weak_clusters[:25], 1):
    severity = '🔴' if cluster['fraud_analysis']['risk_score'] >= 100 else \
               '🟠' if cluster['fraud_analysis']['risk_score'] >= 60 else '🟡'
    
    print(f"{severity} CLUSTER #{rank} [{cluster['cluster_id']}] (Risk Score: {cluster['fraud_analysis']['risk_score']})")
    print(f"   Size: {cluster['stats']['size']} members, {cluster['stats']['num_edges']} connections")
    print(f"   Density: {cluster['stats']['density']:.3f} | Isolation Ratio: {cluster['stats']['isolation_ratio']:.3f}")
    print(f"   Node Composition: ", end='')
    for node_type, count in cluster['stats']['node_types'].most_common():
        if node_type:
            print(f"{count} {node_type}{'s' if count > 1 else ''}, ", end='')
    print()
    
    print(f"   🚩 Red Flags:")
    for flag in cluster['fraud_analysis']['flags']:
        print(f"      • {flag}")
    
    if cluster['key_members']:
        print(f"   👥 Key Members (Ringleaders):")
        for member in cluster['key_members'][:3]:
            node_type_display = member['node_type'] if member['node_type'] else 'Unknown'
            print(f"      • {member['node_id']} ({node_type_display}) - Centrality: {member['total_centrality']:.3f}")
    
    print()

if len(suspicious_weak_clusters) > 25:
    print(f"... and {len(suspicious_weak_clusters) - 25} more suspicious clusters\n")


print(f"{'='*100}")
print("LARGEST CLUSTERS")
print(f"{'='*100}\n")

largest_clusters = sorted(weak_cluster_analysis, key=lambda x: x['stats']['size'], reverse=True)[:10]

print(f"{'Rank':<6} {'Cluster ID':<12} {'Size':<8} {'Edges':<8} {'Density':<10} {'Risk Score':<12}")
print("-" * 70)

for rank, cluster in enumerate(largest_clusters, 1):
    risk = cluster['fraud_analysis']['risk_score'] if cluster['fraud_analysis']['flags'] else 0
    print(f"{rank:<6} {cluster['cluster_id']:<12} {cluster['stats']['size']:<8} "
          f"{cluster['stats']['num_edges']:<8} {cluster['stats']['density']:<10.3f} {risk:<12}")


print(f"\n\n{'='*100}")
print("HIGHEST DENSITY CLUSTERS (Most Tightly Connected)")
print(f"{'='*100}\n")

dense_clusters = sorted([c for c in weak_cluster_analysis if c['stats']['size'] >= 4], 
                        key=lambda x: x['stats']['density'], reverse=True)[:10]

print(f"{'Rank':<6} {'Cluster ID':<12} {'Size':<8} {'Density':<10} {'Avg Degree':<12} {'Risk Score':<12}")
print("-" * 75)

for rank, cluster in enumerate(dense_clusters, 1):
    risk = cluster['fraud_analysis']['risk_score'] if cluster['fraud_analysis']['flags'] else 0
    print(f"{rank:<6} {cluster['cluster_id']:<12} {cluster['stats']['size']:<8} "
          f"{cluster['stats']['density']:<10.3f} {cluster['stats']['avg_degree']:<12.2f} {risk:<12}")


print(f"\n\n{'='*100}")
print("MOST ISOLATED CLUSTERS (Suspicious Insularity)")
print(f"{'='*100}\n")

isolated_clusters = sorted([c for c in weak_cluster_analysis if c['stats']['size'] >= 3], 
                           key=lambda x: x['stats']['isolation_ratio'], reverse=True)[:10]

print(f"{'Rank':<6} {'Cluster ID':<12} {'Size':<8} {'Isolation':<12} {'Internal/External':<20} {'Risk':<12}")
print("-" * 80)

for rank, cluster in enumerate(isolated_clusters, 1):
    risk = cluster['fraud_analysis']['risk_score'] if cluster['fraud_analysis']['flags'] else 0
    ratio_str = f"{cluster['stats']['internal_edges']}/{cluster['stats']['external_edges']}"
    print(f"{rank:<6} {cluster['cluster_id']:<12} {cluster['stats']['size']:<8} "
          f"{cluster['stats']['isolation_ratio']:<12.3f} {ratio_str:<20} {risk:<12}")


print(f"\n\n{'='*100}")
print("CLUSTER RISK CLASSIFICATION")
print(f"{'='*100}\n")

# Classify by risk
critical_clusters = [c for c in suspicious_weak_clusters if c['fraud_analysis']['risk_score'] >= 100]
high_risk_clusters = [c for c in suspicious_weak_clusters if 60 <= c['fraud_analysis']['risk_score'] < 100]
medium_risk_clusters = [c for c in suspicious_weak_clusters if 40 <= c['fraud_analysis']['risk_score'] < 60]
low_risk_clusters = [c for c in suspicious_weak_clusters if c['fraud_analysis']['risk_score'] < 40]

print(f"🔴 CRITICAL RISK (Score ≥ 100): {len(critical_clusters)} clusters")
print(f"   Highly organized fraud rings requiring immediate investigation\n")

print(f"🟠 HIGH RISK (Score 60-99): {len(high_risk_clusters)} clusters")
print(f"   Significant fraud indicators present\n")

print(f"🟡 MEDIUM RISK (Score 40-59): {len(medium_risk_clusters)} clusters")
print(f"   Moderate suspicion, warrants monitoring\n")

print(f"⚪ LOW RISK (Score < 40): {len(low_risk_clusters)} clusters")
print(f"   Minor anomalies detected\n")


# Detailed view of top 3 critical clusters
if critical_clusters:
    print(f"\n{'='*100}")
    print("DETAILED ANALYSIS - TOP 3 CRITICAL CLUSTERS")
    print(f"{'='*100}\n")
    
    for idx, cluster in enumerate(critical_clusters[:3], 1):
        print(f"╔{'═'*98}╗")
        print(f"║ CRITICAL CLUSTER #{idx}: {cluster['cluster_id']:<82} ║")
        print(f"╚{'═'*98}╝\n")
        
        print(f"  📊 Cluster Metrics:")
        print(f"     Size: {cluster['stats']['size']} members")
        print(f"     Connections: {cluster['stats']['num_edges']} edges")
        print(f"     Density: {cluster['stats']['density']:.3f}")
        print(f"     Average Degree: {cluster['stats']['avg_degree']:.2f}")
        print(f"     Clustering Coefficient: {cluster['stats']['avg_clustering']:.3f}")
        print(f"     Isolation Ratio: {cluster['stats']['isolation_ratio']:.3f}")
        
        print(f"\n  🔍 Member Composition:")
        for node_type, count in cluster['stats']['node_types'].most_common():
            if node_type:
                print(f"     • {node_type}: {count}")
        
        print(f"\n  🔗 Connection Types:")
        for edge_type, count in cluster['stats']['edge_types'].most_common():
            if edge_type:
                print(f"     • {edge_type}: {count}")
        
        print(f"\n  🚩 Fraud Indicators (Risk Score: {cluster['fraud_analysis']['risk_score']}):")
        for flag in cluster['fraud_analysis']['flags']:
            print(f"     • {flag}")
        
        print(f"\n  👥 Key Members (Top 5 Ringleaders):")
        for member in cluster['key_members'][:5]:
            node_type_display = member['node_type'] if member['node_type'] else 'Unknown'
            print(f"     {member['node_id']:>12} ({node_type_display:<12}) | "
                  f"Degree: {member['degree_centrality']:.3f} | "
                  f"Betweenness: {member['betweenness_centrality']:.3f}")
        
        print(f"\n  📋 Cluster Members (first 10):")
        for i, node_id in enumerate(cluster['nodes'][:10], 1):
            node_type = G.nodes[node_id].get('node_type', 'Unknown')
            node_name = G.nodes[node_id].get('name', 'N/A')
            print(f"     {i:2d}. {node_id} ({node_type}) - {node_name}")
        
        if len(cluster['nodes']) > 10:
            print(f"     ... and {len(cluster['nodes']) - 10} more members")
        
        print("\n")


# Visualization
print(f"{'='*100}")
print("GENERATING CLUSTER DETECTION VISUALIZATIONS")
print(f"{'='*100}\n")

fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Chart 1: Cluster size distribution
ax1 = fig.add_subplot(gs[0, 0])
if weak_cluster_analysis:
    sizes = [c['stats']['size'] for c in weak_cluster_analysis]
    ax1.hist(sizes, bins=20, color='#4ECDC4', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Cluster Size (nodes)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Number of Clusters', fontsize=11, fontweight='bold')
    ax1.set_title('Cluster Size Distribution', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

# Chart 2: Risk score distribution
ax2 = fig.add_subplot(gs[0, 1])
if suspicious_weak_clusters:
    risk_scores = [c['fraud_analysis']['risk_score'] for c in suspicious_weak_clusters]
    ax2.hist(risk_scores, bins=15, color='#FF6B6B', alpha=0.7, edgecolor='black')
    ax2.axvline(x=40, color='yellow', linestyle='--', linewidth=2, alpha=0.7)
    ax2.axvline(x=60, color='orange', linestyle='--', linewidth=2, alpha=0.7)
    ax2.axvline(x=100, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax2.set_xlabel('Risk Score', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Number of Clusters', fontsize=11, fontweight='bold')
    ax2.set_title('Cluster Risk Score Distribution', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

# Chart 3: Risk tier breakdown
ax3 = fig.add_subplot(gs[0, 2])
tier_counts = [len(critical_clusters), len(high_risk_clusters), len(medium_risk_clusters), len(low_risk_clusters)]
tier_labels = ['Critical\n(≥100)', 'High\n(60-99)', 'Medium\n(40-59)', 'Low\n(<40)']
colors_pie = ['#FF0000', '#FF8C00', '#FFD700', '#90EE90']

wedges, texts, autotexts = ax3.pie(tier_counts, labels=tier_labels, colors=colors_pie, 
                                     autopct='%1.1f%%', startangle=90,
                                     textprops={'fontsize': 9, 'fontweight': 'bold'})
ax3.set_title('Risk Tier Distribution', fontsize=12, fontweight='bold')

# Chart 4: Top 15 suspicious clusters
ax4 = fig.add_subplot(gs[1, :])
top_15 = suspicious_weak_clusters[:15]
if top_15:
    labels = [f"{c['cluster_id']}\n({c['stats']['size']})" for c in top_15]
    scores = [c['fraud_analysis']['risk_score'] for c in top_15]
    bar_colors = ['#FF0000' if s >= 100 else '#FF8C00' if s >= 60 else '#FFD700' for s in scores]
    
    bars = ax4.barh(range(len(top_15)), scores, color=bar_colors)
    ax4.set_yticks(range(len(top_15)))
    ax4.set_yticklabels(labels, fontsize=8)
    ax4.set_xlabel('Risk Score', fontsize=12, fontweight='bold')
    ax4.set_title('Top 15 Suspicious Clusters', fontsize=14, fontweight='bold')
    ax4.invert_yaxis()
    ax4.grid(axis='x', alpha=0.3)
    
    for i, (bar, score) in enumerate(zip(bars, scores)):
        ax4.text(score + 2, i, str(score), va='center', fontsize=9, fontweight='bold')

# Chart 5: Density vs Size scatter
ax5 = fig.add_subplot(gs[2, 0])
if weak_cluster_analysis:
    sizes = [c['stats']['size'] for c in weak_cluster_analysis]
    densities = [c['stats']['density'] for c in weak_cluster_analysis]
    risk_colors = []
    for c in weak_cluster_analysis:
        risk = c['fraud_analysis']['risk_score'] if c['fraud_analysis']['flags'] else 0
        if risk >= 100:
            risk_colors.append('#FF0000')
        elif risk >= 60:
            risk_colors.append('#FF8C00')
        elif risk >= 40:
            risk_colors.append('#FFD700')
        else:
            risk_colors.append('#90EE90')
    
    ax5.scatter(sizes, densities, c=risk_colors, s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
    ax5.set_xlabel('Cluster Size', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Density', fontsize=11, fontweight='bold')
    ax5.set_title('Cluster Size vs Density', fontsize=12, fontweight='bold')
    ax5.grid(alpha=0.3)

# Chart 6: Isolation ratio distribution
ax6 = fig.add_subplot(gs[2, 1])
if weak_cluster_analysis:
    isolation_ratios = [c['stats']['isolation_ratio'] for c in weak_cluster_analysis]
    ax6.hist(isolation_ratios, bins=15, color='#45B7D1', alpha=0.7, edgecolor='black')
    ax6.axvline(x=0.8, color='red', linestyle='--', linewidth=2, label='High Isolation')
    ax6.set_xlabel('Isolation Ratio', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Number of Clusters', fontsize=11, fontweight='bold')
    ax6.set_title('Cluster Isolation Distribution', fontsize=12, fontweight='bold')
    ax6.legend()
    ax6.grid(axis='y', alpha=0.3)

# Chart 7: Node type composition in suspicious clusters
ax7 = fig.add_subplot(gs[2, 2])
if suspicious_weak_clusters:
    all_node_types = Counter()
    for cluster in suspicious_weak_clusters:
        all_node_types.update(cluster['stats']['node_types'])
    
    types = [t for t in all_node_types.keys() if t]
    counts = [all_node_types[t] for t in types]
    
    ax7.bar(range(len(types)), counts, color='#FF6B6B', edgecolor='black')
    ax7.set_xticks(range(len(types)))
    ax7.set_xticklabels(types, rotation=45, ha='right')
    ax7.set_ylabel('Total Count', fontsize=11, fontweight='bold')
    ax7.set_title('Node Types in Suspicious Clusters', fontsize=12, fontweight='bold')
    ax7.grid(axis='y', alpha=0.3)

plt.suptitle('CLUSTER DETECTION - FRAUD RING ANALYSIS', 
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout()
plt.show()

print("Visualizations generated!\n")

print("="*100)
print("✅ CLUSTER DETECTION ANALYSIS COMPLETE")
print("="*100)
print("\n⚠️  RECOMMENDATIONS:")
print("   Clusters marked as CRITICAL should be:")
print("   • Immediately investigated by fraud analysts")
print("   • All member accounts frozen pending investigation")
print("   • Cross-referenced with known fraud patterns")
print("   • Reported to law enforcement if confirmed")
print("   • Used to train fraud detection models")
print("\n   Key members (high centrality) are likely ringleaders and should be prioritized.")
