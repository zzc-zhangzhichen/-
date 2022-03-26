"""Betweenness centrality measures."""
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from heapq import heappush, heappop
from itertools import count
import warnings

from networkx.utils import py_random_state
from networkx.utils.decorators import not_implemented_for

__all__ = ["betweenness_centrality", "edge_betweenness_centrality", "edge_betweenness"]

#我又把别人算中介中心性的源代码弄过来了，好像还多粘了好多
@py_random_state(5)
@not_implemented_for("multigraph")
def betweenness_centrality(
    G, k=None, normalized=True, weight=None, endpoints=False, seed=None
):
    betweenness = dict.fromkeys(G, 0.0)  # b[v]=0 for v in G
    if k is None:
        nodes = G
    else:
        nodes = seed.sample(G.nodes(), k)
    for s in nodes:
        # single source shortest paths
        if weight is None:  # use BFS
            S, P, sigma = _single_source_shortest_path_basic(G, s)
        else:  # use Dijkstra's algorithm
            S, P, sigma = _single_source_dijkstra_path_basic(G, s, weight)
        # accumulation
        if endpoints:
            betweenness = _accumulate_endpoints(betweenness, S, P, sigma, s)
        else:
            betweenness = _accumulate_basic(betweenness, S, P, sigma, s)
    # rescaling
    betweenness = _rescale(
        betweenness,
        len(G),
        normalized=normalized,
        directed=G.is_directed(),
        k=k,
        endpoints=endpoints,
    )
    return betweenness



@py_random_state(4)
def edge_betweenness_centrality(G, k=None, normalized=True, weight=None, seed=None):

    betweenness = dict.fromkeys(G, 0.0)  # b[v]=0 for v in G
    # b[e]=0 for e in G.edges()
    betweenness.update(dict.fromkeys(G.edges(), 0.0))
    if k is None:
        nodes = G
    else:
        nodes = seed.sample(G.nodes(), k)
    for s in nodes:
        # single source shortest paths
        if weight is None:  # use BFS
            S, P, sigma = _single_source_shortest_path_basic(G, s)
        else:  # use Dijkstra's algorithm
            S, P, sigma = _single_source_dijkstra_path_basic(G, s, weight)
        # accumulation
        betweenness = _accumulate_edges(betweenness, S, P, sigma, s)
    # rescaling
    for n in G:  # remove nodes to only return edges
        del betweenness[n]
    betweenness = _rescale_e(
        betweenness, len(G), normalized=normalized, directed=G.is_directed()
    )
    betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
    return betweenness
# obsolete name
def edge_betweenness(G, k=None, normalized=True, weight=None, seed=None):
    warnings.warn(
        "edge_betweeness is replaced by edge_betweenness_centrality", DeprecationWarning
    )
    return edge_betweenness_centrality(G, k, normalized, weight, seed)


# helpers for betweenness centrality


def _single_source_shortest_path_basic(G, s):
    S = []
    P = {}
    for v in G:
        P[v] = []
    sigma = dict.fromkeys(G, 0.0)  # sigma[v]=0 for v in G
    D = {}
    sigma[s] = 1.0
    D[s] = 0
    Q = [s]
    while Q:  # use BFS to find shortest paths
        v = Q.pop(0)
        S.append(v)
        Dv = D[v]
        sigmav = sigma[v]
        for w in G[v]:
            if w not in D:
                Q.append(w)
                D[w] = Dv + 1
            if D[w] == Dv + 1:  # this is a shortest path, count paths
                sigma[w] += sigmav
                P[w].append(v)  # predecessors
    return S, P, sigma


def _single_source_dijkstra_path_basic(G, s, weight):
    # modified from Eppstein
    S = []
    P = {}
    for v in G:
        P[v] = []
    sigma = dict.fromkeys(G, 0.0)  # sigma[v]=0 for v in G
    D = {}
    sigma[s] = 1.0
    push = heappush
    pop = heappop
    seen = {s: 0}
    c = count()
    Q = []  # use Q as heap with (distance,node id) tuples
    push(Q, (0, next(c), s, s))
    while Q:
        (dist, _, pred, v) = pop(Q)
        if v in D:
            continue  # already searched this node.
        sigma[v] += sigma[pred]  # count paths
        S.append(v)
        D[v] = dist
        for w, edgedata in G[v].items():
            vw_dist = dist + edgedata.get(weight, 1)
            if w not in D and (w not in seen or vw_dist < seen[w]):
                seen[w] = vw_dist
                push(Q, (vw_dist, next(c), v, w))
                sigma[w] = 0.0
                P[w] = [v]
            elif vw_dist == seen[w]:  # handle equal paths
                sigma[w] += sigma[v]
                P[w].append(v)
    return S, P, sigma


def _accumulate_basic(betweenness, S, P, sigma, s):
    delta = dict.fromkeys(S, 0)
    while S:
        w = S.pop()
        coeff = (1 + delta[w]) / sigma[w]
        for v in P[w]:
            delta[v] += sigma[v] * coeff
        if w != s:
            betweenness[w] += delta[w]
    return betweenness


def _accumulate_endpoints(betweenness, S, P, sigma, s):
    betweenness[s] += len(S) - 1
    delta = dict.fromkeys(S, 0)
    while S:
        w = S.pop()
        coeff = (1 + delta[w]) / sigma[w]
        for v in P[w]:
            delta[v] += sigma[v] * coeff
        if w != s:
            betweenness[w] += delta[w] + 1
    return betweenness


def _accumulate_edges(betweenness, S, P, sigma, s):
    delta = dict.fromkeys(S, 0)
    while S:
        w = S.pop()
        coeff = (1 + delta[w]) / sigma[w]
        for v in P[w]:
            c = sigma[v] * coeff
            if (v, w) not in betweenness:
                betweenness[(w, v)] += c
            else:
                betweenness[(v, w)] += c
            delta[v] += c
        if w != s:
            betweenness[w] += delta[w]
    return betweenness


def _rescale(betweenness, n, normalized, directed=False, k=None, endpoints=False):
    if normalized:
        if endpoints:
            if n < 2:
                scale = None  # no normalization
            else:
                # Scale factor should include endpoint nodes
                scale = 1 / (n * (n - 1))
        elif n <= 2:
            scale = None  # no normalization b=0 for all nodes
        else:
            scale = 1 / ((n - 1) * (n - 2))
    else:  # rescale by 2 for undirected graphs
        if not directed:
            scale = 0.5
        else:
            scale = None
    if scale is not None:
        if k is not None:
            scale = scale * n / k
        for v in betweenness:
            betweenness[v] *= scale
    return betweenness


def _rescale_e(betweenness, n, normalized, directed=False, k=None):
    if normalized:
        if n <= 1:
            scale = None  # no normalization b=0 for all nodes
        else:
            scale = 1 / (n * (n - 1))
    else:  # rescale by 2 for undirected graphs
        if not directed:
            scale = 0.5
        else:
            scale = None
    if scale is not None:
        if k is not None:
            scale = scale * n / k
        for v in betweenness:
            betweenness[v] *= scale
    return betweenness

#算全局效率
def global_efficiency(G):
    n = len(G)
    denom = n * (n - 1)
    if denom != 0:
        lengths = nx.all_pairs_shortest_path_length(G)
        g_eff = 0
        for source, targets in lengths:
            for target, distance in targets.items():
                if distance > 0:
                    g_eff += 1 / distance
        g_eff /= denom
        # g_eff = sum(1 / d for s, tgts in lengths
        #                   for t, d in tgts.items() if d > 0) / denom
    else:
        g_eff = 0
    # TODO This can be made more efficient by computing all pairs shortest
    # path lengths in parallel.
    return g_eff
#蓄意攻击
def attack(G,s,times):
    graph = G.copy()
    steps = 1
    effs = []
    print(graph.edges())
    effs.append(global_efficiency(G) / global_efficiency(G))
    edges = G.edges()

    while times>0 and len(graph)>0:
        #print(edge)
        i,j = edge
        graph.remove_edge(i,j)
        eff=global_efficiency(graph)
        effs.append(eff/global_efficiency(G))
        print("去除"+str(steps)+"个节点时效率为: "+str(eff))
        steps += 1
        times-=1

    #接下来开始画图
    x=[]
    for i in range(steps):
        #x.append(str(100*i/len(graph))+"%")
        x.append( i / len(G))
    plt.plot(x,effs,color='b')
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    # 设置横轴的上下限
    plt.xlim(0, (steps/len(G)))
    plt.show()
    return graph




#建了个网
if __name__ == '__main__':
    G = nx.Graph()
    G.add_edges_from(
        [(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 7), (3, 8), (4, 9), (5, 10), (6, 11), (7, 12), (8, 13), (9, 14),
         (10, 15), (11, 16), (2, 3), (3, 4), (4, 5), (5, 6), (7, 8), (8, 9), (9, 10), (10, 11),
         (12, 13), (13, 14), (14, 15), (15, 16), (1, 17), (17, 2), (17, 6), (17, 18), (18, 19), (11, 18), (18, 7)
            , (19, 12), (19, 16), (19, 20), (20, 21), (21, 22), (22, 23), (22, 23), (23, 24), (24, 25), (12, 21),
         (13, 22), (14, 23), (15, 24), (16, 25), (20, 25)])
    pos = nx.spring_layout(G, iterations=1000)
    nx.draw(G, pos, edge_color="g", with_labels=True, width=1)
    plt.show()
    print("未去除节点时效率为： " + str(global_efficiency(G)))
    # pos.pop((0, 0))
    print(G.edges())

    G = attack(G, edge_betweenness_centrality(G), len(G))
    print(G.edges())
    # random_attack(G)
    nx.draw(G, pos, edge_color="g", with_labels=False, width=1)
    plt.show()