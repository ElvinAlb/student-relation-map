import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl

mpl.rcParams['figure.dpi'] = 250 

def create_single_color_node(ax, pos, color, node_size=250):
    """Create a simple node with a single color."""
    radius = node_size / 10000
    circle = plt.Circle(pos, radius, color=color, zorder=2)
    ax.add_patch(circle)


def create_bicolor_node(ax, pos, node, colors, node_size=250):
    """Create a node that can have up to two colors."""
    radius = node_size / 10000
    if len(colors) == 1:
        # Single color node
        circle = plt.Circle(pos, radius, color=colors[0],zorder=2)
        ax.add_patch(circle)
    else:
        # Bicolor node - split into two semicircles using Wedge patches
        left_semicircle = patches.Wedge(pos, radius, 90, 270, color=colors[0], zorder=2)
        right_semicircle = patches.Wedge(pos, radius, -90, 90, color=colors[1], zorder=2)
        ax.add_patch(left_semicircle)
        ax.add_patch(right_semicircle)

def create_directed_graph(sector_or_type, nodes_data, edges_data, edge_colors=None, edge_weights=None, colorlist=None, show_labels=True, edge_width=2, node_positions=None):
    """Create and visualize a directed graph with bicolor nodes."""
    G = nx.DiGraph()

    # Add nodes and edges
    G.add_nodes_from(nodes_data.keys())
    if edge_weights is not None:
        edge_list = [(edge[0], edge[1], {'weight': weight}) for edge, weight in zip(edges_data, edge_weights)]
        G.add_edges_from(edge_list)
    else:
        G.add_edges_from(edges_data)

    # G_rev = nx.DiGraph().reverse(G)

    # Calculate layout using Fruchterman-Reingold if no positions are provided
    if node_positions is None:
        pos = nx.spring_layout(G, k=0.3, iterations=50, scale = 1)
    else:
        pos = node_positions

    # Create figure and axis
    plt.figure(figsize=(20, 20), dpi=250)

    ax = plt.gca()


    # Draw nodes
    if sector_or_type == "sector":
        for node, sectors in nodes_data.items():
            node_colors = [colorlist[sector] for sector in sectors if sector in colorlist]
            create_bicolor_node(ax, pos[node], node, node_colors)
    elif sector_or_type == "simple":
        for node, types in nodes_data.items():
            node_color = 'lightblue'
            create_single_color_node(ax, pos[node], node_color)
    else:
        for node, types in nodes_data.items():
            node_colors = [colorlist[type] for type in types if type in colorlist]
            create_bicolor_node(ax, pos[node], node, node_colors)

    # Draw edges with colors and weights
    if edge_colors is not None:
        for (u, v), color in zip(edges_data, edge_colors):
            nx.draw_networkx_edges(
                G, pos, edgelist=[(u, v)], edge_color=color,
                arrows=True, arrowsize=10, width=edge_width, arrowstyle='-|>', node_size=250, connectionstyle="arc3,rad=0.1", min_target_margin=15
            )
    else:
        nx.draw_networkx_edges(
            G, pos, edge_color='gray', arrows=True,
            arrowsize=10, width=edge_width, arrowstyle='-|>', node_size=250, connectionstyle="arc3,rad=0.1", min_target_margin=15
        )

    # Add labels if requested
    if show_labels:
        nx.draw_networkx_labels(G, pos, font_size=8)

    # Add legend for node colors
    if colorlist:
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label)
                          for label, color in colorlist.items()]
        ax.legend(handles=legend_handles, loc='upper right', title="Node Colors")

    # Set axis properties
    ax.set_aspect('equal')
    plt.axis('off')

    return plt.gcf(), pos