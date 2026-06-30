# Ponzi scheme detection analysis on knowledge graph from KG_NODE and KG_EDGE tables
from snowflake.snowpark.context import get_active_session
import pandas as pd
import networkx as nx
from collections import defaultdict, Counter, deque
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import numpy as np

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
               props=row['PROPS'],
               effective_start=row['EFFECTIVE_START'])

print("="*100)
print("PONZI SCHEME DETECTION ANALYSIS")
print("="*100)
print("\nPonzi Scheme Indicators:")
print("  • Multi-level referral networks (pyramid structure)")
print("  • Early investors receiving payments from later investors")
print("  • High referral bonuses and recruitment incentives")
print("  • Unsustainable return patterns")
print("  • Rapid growth in participant base")
print("  • Funds flowing upward through referral chains")
print("  • Concentration of wealth at top of hierarchy\n")


def analyze_referral_networks(graph):
    """
    Analyze referral networks to identify pyramid/Ponzi structures.
    """
    referral_data = []
    
    # Find all REFERRED edges (customer -> customer referrals)
    referral_edges = [(u, v, d) for u, v, d in graph.edges(data=True) 
                      if d.get('edge_type') == 'REFERRED']
    
    print(f"Found {len(referral_edges)} referral relationships\n")
    
    # Build referral tree for each root customer
    for node in graph.nodes():
        if graph.nodes[node].get('node_type') == 'Customer':
            # Count direct referrals
            direct_referrals = [v for u, v, d in referral_edges if u == node]
            
            # Count total downstream referrals (BFS traversal)
            total_downstream = 0
            referral_levels = {}
            visited = set()
            queue = deque([(node, 0)])
            
            while queue:
                current, level = queue.popleft()
                if current in visited:
                    continue
                visited.add(current)
                
                if level > 0:  # Don't count the root
                    total_downstream += 1
                    referral_levels[level] = referral_levels.get(level, 0) + 1
                
                # Add referred customers to queue
                for u, v, d in referral_edges:
                    if u == current and v not in visited:
                        queue.append((v, level + 1))
            
            max_depth = max(referral_levels.keys()) if referral_levels else 0
            
            # Count upstream (who referred this customer)
            referrers = [u for u, v, d in referral_edges if v == node]
            
            referral_data.append({
                'customer_id': node,
                'customer_name': graph.nodes[node].get('name'),
                'direct_referrals': len(direct_referrals),
                'total_downstream': total_downstream,
                'max_referral_depth': max_depth,
                'referral_levels': referral_levels,
                'referrers': referrers,
                'direct_referral_ids': direct_referrals
            })
    
    return referral_data


# Pre-compute account ownership and transfers for faster lookups
print("Pre-computing account relationships...")
customer_accounts = defaultdict(list)
account_incoming_transfers = defaultdict(list)
account_outgoing_transfers = defaultdict(list)

for u, v, d in G.edges(data=True):
    edge_type = d.get('edge_type')
    if edge_type == 'OWNS':
        customer_accounts[u].append(v)
    elif edge_type == 'TRANSFERRED_TO':
        account_incoming_transfers[v].append((u, d))
        account_outgoing_transfers[u].append((v, d))

print("✅ Pre-computation complete!\n")


def calculate_payment_flows_fast(customer_id):
    """
    Analyze payment flows for a customer using pre-computed lookups.
    """
    accounts = customer_accounts.get(customer_id, [])
    
    total_received = 0
    total_sent = 0
    incoming_sources = set()
    outgoing_destinations = set()
    
    for account in accounts:
        # Incoming transfers
        for source_account, edge_data in account_incoming_transfers.get(account, []):
            props = edge_data.get('props', {})
            if isinstance(props, dict):
                total_received += props.get('total_amount', 0)
            incoming_sources.add(source_account)
        
        # Outgoing transfers
        for dest_account, edge_data in account_outgoing_transfers.get(account, []):
            props = edge_data.get('props', {})
            if isinstance(props, dict):
                total_sent += props.get('total_amount', 0)
            outgoing_destinations.add(dest_account)
    
    return {
        'total_received': total_received,
        'total_sent': total_sent,
        'net_position': total_received - total_sent,
        'incoming_sources_count': len(incoming_sources),
        'outgoing_destinations_count': len(outgoing_destinations)
    }


def detect_ponzi_patterns(referral_data):
    """
    Detect Ponzi scheme patterns based on referral networks and payment flows.
    """
    ponzi_suspects = []
    
    for ref_data in referral_data:
        customer_id = ref_data['customer_id']
        flags = []
        risk_score = 0
        
        # Pattern 1: Multi-level recruiting (pyramid structure)
        if ref_data['max_referral_depth'] >= 3:
            flags.append(f"Deep referral chain (depth: {ref_data['max_referral_depth']}) - pyramid structure")
            risk_score += 40
        
        # Pattern 2: High number of direct referrals (aggressive recruiting)
        if ref_data['direct_referrals'] >= 5:
            flags.append(f"High direct referrals ({ref_data['direct_referrals']}) - aggressive recruiting")
            risk_score += 35
        
        # Pattern 3: Large downstream network (potential Ponzi organizer)
        if ref_data['total_downstream'] >= 10:
            flags.append(f"Large downstream network ({ref_data['total_downstream']} people) - potential scheme organizer")
            risk_score += 50
        
        # Pattern 4: Top of pyramid (many referrals, no referrer)
        if ref_data['direct_referrals'] >= 3 and len(ref_data['referrers']) == 0:
            flags.append(f"Top of pyramid (no upstream referrer) - potential scheme founder")
            risk_score += 60
        
        # Pattern 5: Payment flow analysis
        payment_flow = calculate_payment_flows_fast(customer_id)
        
        # Early investors receiving more than they send (paid by later investors)
        if payment_flow['net_position'] > 50000:
            flags.append(f"High net inflow (${payment_flow['net_position']:,.2f}) - receiving from many sources")
            risk_score += 30
        
        # Receiving from many, sending to few (wealth concentration)
        if payment_flow['incoming_sources_count'] >= 5 and payment_flow['outgoing_destinations_count'] <= 2:
            flags.append(f"Receiving from {payment_flow['incoming_sources_count']} sources, sending to {payment_flow['outgoing_destinations_count']} - wealth concentration")
            risk_score += 35
        
        # Pattern 6: Rapid expansion indicator (wide at one level)
        if ref_data['referral_levels']:
            max_level_size = max(ref_data['referral_levels'].values())
            if max_level_size >= 5:
                flags.append(f"Rapid expansion at one level ({max_level_size} recruits) - unsustainable growth")
                risk_score += 25
        
        if flags:
            ponzi_suspects.append({
                'customer_id': customer_id,
                'customer_name': ref_data['customer_name'],
                'direct_referrals': ref_data['direct_referrals'],
                'total_downstream': ref_data['total_downstream'],
                'max_depth': ref_data['max_referral_depth'],
                'net_position': payment_flow['net_position'],
                'flags': flags,
                'risk_score': risk_score,
                'referral_levels': ref_data['referral_levels']
            })
    
    return ponzi_suspects


def analyze_referral_chains(graph):
    """
    Find and analyze the longest referral chains (potential Ponzi hierarchies).
    """
    referral_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                      if d.get('edge_type') == 'REFERRED']
    
    # Build referral subgraph
    referral_graph = nx.DiGraph()
    referral_graph.add_edges_from(referral_edges)
    
    # Find all paths and identify longest chains
    chains = []
    
    # Find root nodes (no incoming referral)
    roots = [n for n in referral_graph.nodes() if referral_graph.in_degree(n) == 0]
    
    # Limit analysis to avoid excessive computation
    for root in roots[:100]:  # Sample first 100 roots
        # Find all paths from this root
        descendants = list(nx.descendants(referral_graph, root))
        for target in descendants[:50]:  # Sample first 50 descendants per root
            try:
                # Get shortest path only to save time
                path = nx.shortest_path(referral_graph, root, target)
                chains.append({
                    'chain': path,
                    'length': len(path),
                    'root': root,
                    'leaf': target
                })
            except nx.NetworkXNoPath:
                pass
    
    return sorted(chains, key=lambda x: x['length'], reverse=True)


# Analyze referral networks
print("Analyzing referral networks and pyramid structures...")
referral_data = analyze_referral_networks(G)
referral_data_sorted = sorted(referral_data, key=lambda x: x['total_downstream'], reverse=True)
print("✅ Referral analysis complete!\n")

# Detect Ponzi patterns
print("Detecting Ponzi scheme patterns...")
ponzi_suspects = detect_ponzi_patterns(referral_data)
ponzi_suspects_sorted = sorted(ponzi_suspects, key=lambda x: x['risk_score'], reverse=True)
print("✅ Pattern detection complete!\n")

# Analyze referral chains
print("Analyzing referral chain structures...")
referral_chains = analyze_referral_chains(G)
print(f"✅ Found {len(referral_chains)} referral chains\n")


# RESULTS REPORTING
print("="*100)
print("REFERRAL NETWORK STATISTICS")
print("="*100)

customers_with_referrals = len([r for r in referral_data if r['direct_referrals'] > 0])
total_referrals = sum(r['direct_referrals'] for r in referral_data)
avg_referrals = total_referrals / len(referral_data) if referral_data else 0
max_downstream = max([r['total_downstream'] for r in referral_data]) if referral_data else 0
max_depth = max([r['max_referral_depth'] for r in referral_data]) if referral_data else 0

print(f"\n📊 Summary:")
print(f"  Total customers analyzed: {len(referral_data)}")
print(f"  Customers who made referrals: {customers_with_referrals}")
print(f"  Total referral relationships: {total_referrals}")
print(f"  Average referrals per customer: {avg_referrals:.2f}")
print(f"  Maximum downstream network size: {max_downstream}")
print(f"  Maximum referral chain depth: {max_depth}")


print(f"\n\n{'='*100}")
print("TOP REFERRAL NETWORK ORGANIZERS")
print(f"{'='*100}\n")

print(f"{'Rank':<6} {'Customer ID':<12} {'Name':<30} {'Direct':<8} {'Downstream':<12} {'Depth':<6}")
print("-" * 80)

for rank, ref in enumerate(referral_data_sorted[:15], 1):
    print(f"{rank:<6} {ref['customer_id']:<12} {ref['customer_name']:<30} "
          f"{ref['direct_referrals']:<8} {ref['total_downstream']:<12} {ref['max_referral_depth']:<6}")


print(f"\n\n{'='*100}")
print("🚨 PONZI SCHEME SUSPECTS")
print(f"{'='*100}\n")

print(f"Identified {len(ponzi_suspects_sorted)} customers with suspicious Ponzi-like patterns:\n")

for idx, suspect in enumerate(ponzi_suspects_sorted[:20], 1):
    severity = '🔴' if suspect['risk_score'] >= 100 else '🟠' if suspect['risk_score'] >= 60 else '🟡'
    
    print(f"{severity} SUSPECT #{idx} (Risk Score: {suspect['risk_score']})")
    print(f"   Customer: {suspect['customer_id']} - {suspect['customer_name']}")
    print(f"   Direct Referrals: {suspect['direct_referrals']}")
    print(f"   Total Downstream Network: {suspect['total_downstream']}")
    print(f"   Referral Chain Depth: {suspect['max_depth']}")
    print(f"   Net Payment Position: ${suspect['net_position']:,.2f}")
    print(f"   Red Flags:")
    for flag in suspect['flags']:
        print(f"     • {flag}")
    
    if suspect['referral_levels']:
        print(f"   Referral Hierarchy:")
        for level, count in sorted(suspect['referral_levels'].items()):
            print(f"     Level {level}: {count} recruits")
    print()

if len(ponzi_suspects_sorted) > 20:
    print(f"... and {len(ponzi_suspects_sorted) - 20} more suspects\n")


print(f"{'='*100}")
print("LONGEST REFERRAL CHAINS (Potential Ponzi Hierarchies)")
print(f"{'='*100}\n")

print(f"Analyzing top {min(10, len(referral_chains))} longest referral chains:\n")

for idx, chain in enumerate(referral_chains[:10], 1):
    print(f"Chain #{idx} - Length: {chain['length']} levels")
    print(f"  Root (Scheme Originator): {chain['root']}")
    print(f"  Path: {' → '.join(chain['chain'][:5])}", end='')
    if len(chain['chain']) > 5:
        print(f" → ... → {chain['chain'][-1]}")
    else:
        print()
    print()


print(f"{'='*100}")
print("PONZI RISK TIER CLASSIFICATION")
print(f"{'='*100}\n")

# Classify suspects by risk tier
critical_risk = [s for s in ponzi_suspects_sorted if s['risk_score'] >= 100]
high_risk = [s for s in ponzi_suspects_sorted if 60 <= s['risk_score'] < 100]
medium_risk = [s for s in ponzi_suspects_sorted if 40 <= s['risk_score'] < 60]
low_risk = [s for s in ponzi_suspects_sorted if s['risk_score'] < 40]

print(f"🔴 CRITICAL RISK (Score ≥ 100): {len(critical_risk)} suspects")
print(f"   Likely scheme organizers/founders with large downstream networks\n")

print(f"🟠 HIGH RISK (Score 60-99): {len(high_risk)} suspects")
print(f"   Major participants with significant recruiting activity\n")

print(f"🟡 MEDIUM RISK (Score 40-59): {len(medium_risk)} suspects")
print(f"   Active participants showing concerning patterns\n")

print(f"⚪ LOW RISK (Score < 40): {len(low_risk)} suspects")
print(f"   Minor participants or isolated suspicious activity\n")


# Network metrics
print(f"\n{'='*100}")
print("NETWORK TOPOLOGY ANALYSIS")
print(f"{'='*100}\n")

# Build referral-only subgraph
referral_edges = [(u, v) for u, v, d in G.edges(data=True) 
                  if d.get('edge_type') == 'REFERRED']
referral_graph = nx.DiGraph()
referral_graph.add_edges_from(referral_edges)

if len(referral_graph.nodes()) > 0:
    # Find weakly connected components (separate referral networks)
    components = list(nx.weakly_connected_components(referral_graph))
    
    print(f"📊 Referral Network Components:")
    print(f"  Number of separate referral networks: {len(components)}")
    print(f"  Largest network size: {len(max(components, key=len)) if components else 0} customers")
    print(f"  Average network size: {sum(len(c) for c in components) / len(components) if components else 0:.1f}")
    
    # Analyze largest component
    if components:
        largest_component = max(components, key=len)
        subgraph = referral_graph.subgraph(largest_component)
        
        print(f"\n  Largest Referral Network Details:")
        print(f"    Participants: {len(largest_component)}")
        print(f"    Referral relationships: {subgraph.number_of_edges()}")
        print(f"    Average referrals per person: {subgraph.number_of_edges() / len(largest_component):.2f}")
        
        # Find the root(s) of this network
        roots = [n for n in subgraph.nodes() if subgraph.in_degree(n) == 0]
        print(f"    Potential scheme originators: {len(roots)}")
        if roots:
            for root in roots[:3]:
                downstream = len(nx.descendants(subgraph, root))
                print(f"      - {root}: {downstream} downstream recruits")


# Visualization
print(f"\n\n{'='*100}")
print("GENERATING PONZI DETECTION VISUALIZATIONS")
print(f"{'='*100}\n")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Chart 1: Risk score distribution
ax1 = fig.add_subplot(gs[0, :2])
if ponzi_suspects_sorted:
    risk_scores = [s['risk_score'] for s in ponzi_suspects_sorted]
    bins = [0, 40, 60, 100, max(risk_scores)+10]
    colors_bins = ['#90EE90', '#FFD700', '#FF8C00', '#FF0000']
    
    ax1.hist(risk_scores, bins=20, color='#FF6B6B', alpha=0.7, edgecolor='black')
    ax1.axvline(x=40, color='yellow', linestyle='--', linewidth=2, alpha=0.7, label='Medium Risk')
    ax1.axvline(x=60, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='High Risk')
    ax1.axvline(x=100, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Critical Risk')
    ax1.set_xlabel('Risk Score', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Suspects', fontsize=12, fontweight='bold')
    ax1.set_title('Ponzi Risk Score Distribution', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

# Chart 2: Risk tier breakdown
ax2 = fig.add_subplot(gs[0, 2])
tier_counts = [len(critical_risk), len(high_risk), len(medium_risk), len(low_risk)]
tier_labels = ['Critical\n(≥100)', 'High\n(60-99)', 'Medium\n(40-59)', 'Low\n(<40)']
colors = ['#FF0000', '#FF8C00', '#FFD700', '#90EE90']

wedges, texts, autotexts = ax2.pie(tier_counts, labels=tier_labels, colors=colors, autopct='%1.1f%%',
                                     startangle=90, textprops={'fontsize': 9, 'fontweight': 'bold'})
ax2.set_title('Risk Tier Breakdown', fontsize=12, fontweight='bold')

# Chart 3: Top 15 suspects by risk score
ax3 = fig.add_subplot(gs[1, :])
top_15_suspects = ponzi_suspects_sorted[:15]
if top_15_suspects:
    names = [f"{s['customer_id']}\n({s['direct_referrals']}→{s['total_downstream']})" 
             for s in top_15_suspects]
    scores = [s['risk_score'] for s in top_15_suspects]
    bar_colors = ['#FF0000' if s >= 100 else '#FF8C00' if s >= 60 else '#FFD700' 
                  for s in scores]
    
    bars = ax3.barh(range(len(top_15_suspects)), scores, color=bar_colors)
    ax3.set_yticks(range(len(top_15_suspects)))
    ax3.set_yticklabels(names, fontsize=8)
    ax3.set_xlabel('Risk Score', fontsize=12, fontweight='bold')
    ax3.set_title('Top 15 Ponzi Suspects by Risk Score', fontsize=14, fontweight='bold')
    ax3.invert_yaxis()
    ax3.grid(axis='x', alpha=0.3)
    
    for i, (bar, score) in enumerate(zip(bars, scores)):
        ax3.text(score + 2, i, str(score), va='center', fontsize=9, fontweight='bold')

# Chart 4: Referral depth vs downstream size scatter
ax4 = fig.add_subplot(gs[2, 0])
if referral_data:
    depths = [r['max_referral_depth'] for r in referral_data if r['max_referral_depth'] > 0]
    downstreams = [r['total_downstream'] for r in referral_data if r['max_referral_depth'] > 0]
    
    ax4.scatter(depths, downstreams, alpha=0.6, c='#FF6B6B', s=50, edgecolors='black', linewidth=0.5)
    ax4.set_xlabel('Max Referral Depth', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Total Downstream Size', fontsize=11, fontweight='bold')
    ax4.set_title('Pyramid Structure Analysis', fontsize=12, fontweight='bold')
    ax4.grid(alpha=0.3)

# Chart 5: Direct referrals distribution
ax5 = fig.add_subplot(gs[2, 1])
if referral_data:
    direct_refs = [r['direct_referrals'] for r in referral_data if r['direct_referrals'] > 0]
    ax5.hist(direct_refs, bins=15, color='#4ECDC4', alpha=0.7, edgecolor='black')
    ax5.set_xlabel('Direct Referrals', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Number of Customers', fontsize=11, fontweight='bold')
    ax5.set_title('Direct Referral Distribution', fontsize=12, fontweight='bold')
    ax5.grid(axis='y', alpha=0.3)

# Chart 6: Network component sizes
ax6 = fig.add_subplot(gs[2, 2])
if components:
    component_sizes = sorted([len(c) for c in components], reverse=True)[:10]
    ax6.bar(range(len(component_sizes)), component_sizes, color='#45B7D1', edgecolor='black')
    ax6.set_xlabel('Network ID', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Network Size', fontsize=11, fontweight='bold')
    ax6.set_title('Top 10 Referral Networks', fontsize=12, fontweight='bold')
    ax6.grid(axis='y', alpha=0.3)

plt.suptitle('PONZI SCHEME DETECTION - COMPREHENSIVE ANALYSIS', 
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout()
plt.show()

print("Visualizations generated!\n")

print("="*100)
print("✅ PONZI SCHEME DETECTION ANALYSIS COMPLETE")
print("="*100)
print("\n⚠️  RECOMMENDATION:")
print("   Customers marked as CRITICAL or HIGH RISK should be:")
print("   • Immediately flagged for investigation")
print("   • Subject to enhanced due diligence")
print("   • Monitored for suspicious transaction patterns")
print("   • Reported to compliance and regulatory authorities if confirmed")
