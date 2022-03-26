import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from heapq import heappush, heappop
from itertools import count
import warnings

from networkx.utils import py_random_state
from networkx.utils.decorators import not_implemented_for

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


# 蓄意攻击
def attack(G, s, times):
    graph = G.copy()
    steps = 1
    effs = []
    print(graph.edges)
    effs.append(global_efficiency(G) / global_efficiency(G))
    edges = G.edges()
    while times > 0 and len(graph.edges()) > 0:
        i,j = s[steps-1]
        graph.remove_edge(i,j)
        eff = global_efficiency(graph)
        effs.append(eff / global_efficiency(G))
        print("去除边" + str(s[steps-1]) + "时效率为: " + str(eff))
        steps += 1
        times -= 1

    # 接下来开始画图
    x = []
    for i in range(steps):
        # x.append(str(100*i/len(graph))+"%")
        x.append(i / len(G.edges))
    plt.plot(x, effs, color='b')
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    # 设置横轴的上下限
    plt.xlim(0, (steps / len(G.edges)))
    plt.show()
    return graph


if __name__ == '__main__':
    file = "data/wuhan.txt"
    G = nx.Graph()
    with open(file, "r") as f:  # 打开文件
         lines = f.readlines()  # 读取文件
         #data=[]
         for line in lines:
             data = line.split()
             if len(data)!=5:
                 print("以下行数据出错")
                 print(line)
             G.add_edge(int(data[0]), int(data[1]), D=float(data[2]), C0=int(data[3]), L0=int(data[4]))


    betweenness = sorted(nx.edge_betweenness_centrality(G).items(), key=lambda x: x[1], reverse=True)
    for edge,bet in betweenness:
        print('边：'+str(edge)+' 介数：'+str(bet)+' 长度：'+str(G.edges[edge]['D']))
    #print(len(G.edges))

    s = []
    for i in betweenness:
        s.append(i[0])
    #G = attack(G, s,len(G.edges))

