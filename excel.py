import matplotlib.pyplot as plt
import networkx as nx

G = nx.krackhardt_kite_graph()
#计算中介中心度
print("Betweenness centrality")
b = nx.betweenness_centrality(G)
for v in G.nodes():
    print("%0.2d %5.3f" % (v, b[v]))
