import random

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys  # 导入sys模块
sys.setrecursionlimit(10000000)  # 将默认的递归深度修改为3000

def create(file):
    G = nx.Graph()
    with open(file, "r") as f:  # 打开文件
         lines = f.readlines()  # 读取文件
         #data=[]
         for line in lines:
             data = line.split()
             if len(data)!=4:
                 print("以下行数据出错")
                 print(line)
             #下方负载为理论值
             #G.add_edge(int(data[0]),int(data[1]),D=float(data[2]),C0=int(data[3]),L0=0.9*int(data[3]))
             # 下方负载为实际值
             G.add_edge(int(data[0]), int(data[1]),  C0=float(data[2]), L0=float(data[3]))
             #武汉
             #G.add_edge(int(data[0]), int(data[1]), D=float(data[2]), C0=int(data[3]), L0=int(data[4]))
             #h=G.edges[(1857,1906)]['L0']
    be=nx.edge_betweenness_centrality(G)

    for edge in be:
        #be[edge]=G.edges[edge]['L0']
        #be[edge]=0.5*be[edge]/0.13861952605112599+0.5*G.edges[edge]['L0']/2000
        be[edge]=be[edge]
    be = sorted(be.items(), key=lambda x: x[1], reverse=True)
    for b in be:
        e,m = b
        G.add_edge(*e,M=m)
    # nx.draw(G, edge_color="g", with_labels=True, width=1)
    # plt.show()
    return G
'''
def create_b(file1,file2):
    G=create(file1)
    be = nx.edge_betweenness_centrality(G)
    be = sorted(be.items(), key=lambda x: x[1], reverse=True)
    for b in be:
        e, m = b
        G.add_edge(*e, B=m)
    new_lines=[]
    with open(file1, "r") as f:  # 打开文件
        lines = f.readlines()  # 读取文件
        for line in lines:
            data = line.split()
            line=line.replace('\n', '\t')+str(G.edges[(int(data[0]), int(data[1]))]['M'])+'\n'
            new_lines.append(line)
    with open(file2, "w") as f2:
        for line in new_lines:
            f2.writelines(line)'''



'''def get_HH(G):
    # 获取负载最高的节点
    for e in G.edges():
        edge = e
        break

    for e in G.edges():
        if G.edges[e]['M'] > G.edges[edge]['M']:
            edge = e
    return edge'''
def get_random(G):
    # 获取负载最高的节点
    edge = random.choice(list(G.edges()))
    return edge

def get_neighbors_edge(G,edge):
    a,b = edge
    an = [k for k in G.neighbors(a)]
    bn = [k for k in G.neighbors(b)]
    an.remove(b)
    an=[(k,a) for k in an]
    bn.remove(a)
    bn=[(k,b) for k in bn]
    return an+bn
def remove_edge(G,edge):
    # 移除该节点，并将负载按容量分配给相邻节点

    nb = get_neighbors_edge(G,edge) # node的相邻节点列表
    C_total_neighbors = sum([G.edges[k]['C0'] for k in nb]) # 相邻节点的容量总和
    if C_total_neighbors == 0:
        if len(nb) != 0:
            x = G.edges[edge]['L0']/len(nb)
            for k in nb:
                G.edges[k]['L0'] = x
    else:
        x = (G.edges[edge]['L0']-0.6*G.edges[edge]['C0'])  / (C_total_neighbors )
        for k in nb:
            G.edges[k]['L0'] += G.edges[k]['C0'] * x    # 将被毁节点的负载，按容量大小比例分配给相邻节点
    print(edge)
    G.remove_edge(*edge) # 从网络中移除被摧毁节点
    return nb

def is_ruin(G,nbb):
    # 递归，检查被摧毁节点的邻居是否过载，过载则被毁
    for n in nbb:
        if n in G.edges():
            if G.edges[n]['L0'] > G.edges[n]['C0']:
                nei = remove_edge(G,n)   # 过载则被毁
                is_ruin(G,nei)      # 检查被毁节点的邻居

def attack(G):
    graph = G.copy()
    steps = 1
    rps_ed=0
    rps = []
    reserve=[]
    len_edge0=len(G.edges)
    while len(graph.edges()) > 0:
        print("第"+str(steps)+"次删除路段，"+"删除随机路段"+str(get_random(graph)))
        nb=remove_edge(graph,get_random(graph))
        is_ruin(graph,nb)
        len_edge=len(graph.edges())
        reserve.append(len_edge/(len(G.edges)))
        print(len_edge0-len_edge)
        rps.append(len_edge0-len_edge-rps_ed)
        rps_ed=len_edge0-len_edge
        steps+=1
    print(rps)
    # 接下来开始画图
    x = []
    for i in range(steps-1):
        #x.append(str(100*i/len(graph))+"%")
        #x.append(i+1)
        x.append((i + 1)/len(G.edges))
    #plt.plot(x, rps, color='b')
    #plt.plot(x, reserve, color='r')
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    # 设置横轴的上下限
    plt.plot(x, reserve,color="r")
    '''plt.plot(x , reserve # x轴数据

             , alpha=0.5  # 线条透明度，0到1之间的浮点数，数值越小，透明度越高
             , linestyle="-"  # 设置线条样式，“--”表示虚线
             , linewidth=2.5  # 设置线条宽度，输入浮点数
             , color="b"  # 设置线条颜色，”b“表示蓝色
             , marker="*"  # 设置数据点的形状，“o”表示原型
             , markeredgecolor="g"  # 设置数据点边框的颜色，“g”表示绿色
             , markeredgewidth=1.2  # 设置数据点边框的宽度，输入浮点数
             , markerfacecolor="w"  # 设置数据点颜色，”w“表示白色
             , markersize=5.5  # 设置数据点形状的大小，输入浮点数
             )'''


    plt.xlim(0,(steps/len(G.edges)))
    #plt.savefig('方格结果.png', bbox_inches='tight')
    plt.show()
    return graph

'''def attack1(G,e):
    graph = G.copy()
    steps = 1
    rps_ed=0
    rps = []
    reserve=[]
    len_edge0=len(G.edges)

    print("当前删除节点，"+str(e))
    nb=remove_edge(graph,e)
    is_ruin(graph,nb)

    return graph'''

if __name__ == '__main__':
    #G=create_b("data/wuhan.txt","data/wuhan_b.txt")
    G = create("data/小规模方格.txt")
    attack(G)

    #print(len(G.edges))
    #print("中介中心性数值为：" + str(nx.edge_betweenness_centrality(G)))



    #下方函数是攻击特定边，改变e即可
    #e=(1134,1133)
    #attack1(G,e)
