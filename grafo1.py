import networkx as nx
import matplotlib.pyplot as plt

class DraggableGraph:
    def __init__(self, G, pos, original_G, original_pos):
        self.G = G
        self.pos = pos
        self.original_G = original_G.copy()
        self.original_pos = original_pos.copy()
        self.selected_node = None
        self.node_radius = 0.05
        self.merged_node = 0
        self.fig, self.ax = plt.subplots(figsize=(20, 14))
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.draw_graph()
        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def draw_graph(self):
        self.ax.clear()
        nx.draw(self.G, self.pos, with_labels=True, node_size=400, node_color='lightblue', 
                font_size=12, font_weight='bold', edge_color='gray', ax=self.ax)
        edge_labels = {(i, j): f'{self.G[i][j]["weight"]:.2f}' for i, j in self.G.edges()}
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=edge_labels, font_size=10, 
                                     font_color='red', ax=self.ax,
                                     bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.3'))
        self.fig.canvas.draw()

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        for node, (x, y) in self.pos.items():
            if (x - event.xdata) ** 2 + (y - event.ydata) ** 2 < self.node_radius ** 2:
                self.selected_node = node
                break

    def on_release(self, event):
        if self.selected_node is not None:
            for node, (x, y) in self.pos.items():
                if node != self.selected_node and (x - event.xdata) ** 2 + (y - event.ydata) ** 2 < self.node_radius ** 2:
                    self.merge_nodes(self.selected_node, node)
                    break
        self.selected_node = None

    def on_motion(self, event):
        if self.selected_node is not None and event.inaxes == self.ax:
            self.pos[self.selected_node] = (event.xdata, event.ydata)
            self.draw_graph()

    def on_key_press(self, event):
        if event.key == 'enter':
            self.fuse_max_edge_to_merged()
        elif event.key == 'escape':
            self.reset_graph()

    def fuse_max_edge_to_merged(self):
        if self.merged_node not in self.pos:
            return
        max_edge_node = self.find_max_edge_node(self.merged_node)
        if max_edge_node is not None:
            self.merge_nodes(self.merged_node, max_edge_node)
            self.merged_node = f"{self.merged_node},{max_edge_node}"

    def find_max_edge_node(self, target):
        max_weight = float('-inf')
        max_edge_node = None
        for neighbor in self.G.neighbors(target):
            weight = self.G[target][neighbor]["weight"]
            if weight > max_weight:
                max_weight = weight
                max_edge_node = neighbor
        return max_edge_node

    def merge_nodes(self, node1, node2):
        new_node = f"{node1},{node2}"
        edges = {}
        
        for neighbor in set(self.G.neighbors(node1)).union(set(self.G.neighbors(node2))):
            if neighbor not in {node1, node2}:
                weight = self.G.get_edge_data(node1, neighbor, {"weight": 0})["weight"] + \
                         self.G.get_edge_data(node2, neighbor, {"weight": 0})["weight"]
                edges[neighbor] = weight
        
        self.G.remove_nodes_from([node1, node2])
        self.G.add_node(new_node)
        for neighbor, weight in edges.items():
            self.G.add_edge(new_node, neighbor, weight=weight)
        
        self.pos[new_node] = ((self.pos[node1][0] + self.pos[node2][0]) / 2, 
                              (self.pos[node1][1] + self.pos[node2][1]) / 2)
        
        del self.pos[node1]
        del self.pos[node2]
        
        self.draw_graph()
    
    def reset_graph(self):
        self.G.clear()
        self.G.add_nodes_from(self.original_G.nodes())
        self.G.add_edges_from((u, v, d) for u, v, d in self.original_G.edges(data=True))
        self.pos = self.original_pos.copy()
        self.merged_node = 0
        self.draw_graph()


def read_graph_from_file(filename):
    with open(filename, 'r') as file:
        n = int(file.readline().strip())
        matrix = [list(map(float, line.strip().split())) for line in file]
    return n, matrix


def plot_graph(n, matrix):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] != 0:
                G.add_edge(i, j, weight=matrix[i][j])
    
    pos = nx.kamada_kawai_layout(G)
    draggable_graph = DraggableGraph(G, pos, G, pos)
    plt.show()


if __name__ == "__main__":
    filename = 'grafo.txt'
    n, matrix = read_graph_from_file(filename)
    plot_graph(n, matrix)
