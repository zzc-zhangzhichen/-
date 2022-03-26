import networkx as nwx 
import matplotlib.pyplot as plt

a = 0.5
q = 0.5
def create_BA(N = 10, m = 2):
    #G = nwx.grid_2d_graph(10, 10)
    G = nwx.barabasi_albert_graph(N,m) # 生成BA无标度网络
    G = G.to_directed() # 转换成有向图。如需无向图，可将该行注释掉
    return G

def set_load0(BA, a = 0.5, q = 0.5):
    B = nwx.betweenness_centrality(BA, endpoints = True)      # 获取所有节点的介数
    # 设置节点的初始负载 L0_n = (1+q)*Bn^a 
    for n in BA.nodes():
        BA.add_node(n, L0 = (1+q)*(B[n]**a))

def set_cap(BA, beta = 0.25):
    # 设定节点的容量，即节点的最大负载 C0_n = (1+beta)*L0_n
    for n in BA.nodes():
        BA.add_node(n, C0 = (1+beta) * BA.nodes[n]['L0'])

def get_HH(BA):
    # 获取负载最高的节点
    node = 0
    for n in BA.nodes():
        if BA.nodes[n]['L0'] > BA.nodes[node]['L0']:
            node = n
    return node

def get_LL(BA):
    # 获取负载最小的点
    node = 0
    for n in BA.nodes():
        if BA.nodes[node]['L0'] == 0:
            node = n
        else:
            if BA.nodes[n]['L0'] < BA.nodes[node]['L0']:
                node = n
    return node

def show_BA(BA):
    # 显示网络图
    ps = nwx.spring_layout(BA)  #布置框架
    nwx.draw(
        G = BA,
        pos = ps,
        with_labels = True,
        font_size = 8,
        node_size = 10
        )
    plt.savefig('network.png',dpi=400)

def attack(G,node):
    # 移除该节点，并将负载按容量分配给相邻节点
    nb = [k for k in G.neighbors(node)] # node的相邻节点列表
    C_total_neighbors = sum([G.nodes[k]['C0'] for k in nb]) # 相邻节点的容量总和
    if C_total_neighbors == 0:
        if len(nb) != 0:
            x = G.nodes[node]['L0']/len(nb)
            for k in nb:
                G.nodes[k]['L0'] = x
    else:
        x = G.nodes[node]['L0'] / C_total_neighbors 
        for k in nb:
            G.nodes[k]['L0'] += G.nodes[k]['C0'] * x    # 将被毁节点的负载，按容量大小比例分配给相邻节点
    G.remove_node(node) # 从网络中移除被摧毁节点
    return nb

def is_ruin(G,nbb):
    # 递归，检查被摧毁节点的邻居是否过载，过载则被毁
    for n in nbb:
        if n in G.nodes():
            if G.nodes[n]['L0'] > G.nodes[n]['C0']:
                nei = attack(G,n)   # 过载则被毁
                is_ruin(G,nei)      # 检查被毁节点的邻居


if __name__ == '__main__':
    # 主函数
    N = 100 # 网络规模
    BA = create_BA(N,2)

    show_BA(BA) # 保存网络图
    plt.close(0)    # 清理图片
    set_load0(BA,a=1,q=0)   # 设置初始负载
    for n in BA.nodes():
        print(f'节点{n}的相邻节点 =',[k for k in BA.neighbors(n)],f'节点{n}的介数 =',BA.nodes[n]['L0']) # 显示所有节点数据，测试用，可注释掉

    beta_list = [0.02 * i for i in range(25)]   # β列表
    S_list = [[0 for i in range(25)] for k in range(4)] # 定义S空列表，用于存放抗毁性能结果

    # 第一个图
    param = [['HL',0.2],['HL',0.4],['LL',0.2],['LL',0.4]]   # 定义参数列表
    for j,a in enumerate(param):
        for i, beta in enumerate(beta_list):
            BA_copy = BA.copy() # 在网络的备份上操作，确保均在同一个网络上进行仿真，保证实验效果
            set_load0(BA_copy,a = param[j][1], q = 0.5) # 设置节点初始负载
            set_cap(BA_copy,beta = beta)    # 设置节点最大容量

            node_HL = get_HH(BA_copy)   # 获取最大负载点
            node_LL = get_LL(BA_copy)   # 获取最小负载点

            if param[j][0] == 'HL':
                node = node_HL
            else:
                node = node_LL

            neighbors = attack(BA_copy, node)   # 对第一个点进行攻击
            is_ruin(BA_copy, neighbors) # 对被攻击点的相邻节点进行递归检测

            N_bar = len(BA_copy.nodes())    # 存放幸存节点
            S_list[j][i] = N_bar/N  # 计算抗毁性能

    marker_list = ['o','h','p','s'] # 画图用的图例
    fig1 = plt.figure() # 新增画布
    ax1 = fig1.add_subplot(1,1,1)   # 指定图像位置
    for j in range(4):
        # 依次画四条曲线
        ax1.plot(
            beta_list, S_list[j], 
            marker = marker_list[j], 
            label = ','.join([param[j][0],f'a={param[j][1]}'])
        )
    ax1.legend(loc='best') # 显示图例

    # 第二个图
    param = [['HL',0.8],['HL',1],['LL',1],['LL',0.8]]
    for j,a in enumerate(param):
        for i, beta in enumerate(beta_list):
            BA_copy = BA.copy()
            set_load0(BA_copy,a = param[j][1], q = 0.5)
            set_cap(BA_copy,beta = beta)

            node_HL = get_HH(BA_copy)
            node_LL = get_LL(BA_copy)

            if param[j][0] == 'HL':
                node = node_HL
            else:
                node = node_LL

            neighbors = attack(BA_copy, node)
            is_ruin(BA_copy, neighbors)

            N_bar = len(BA_copy.nodes())

            S_list[j][i] = N_bar/N

    marker_list = ['o','h','p','s']
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(1,1,1)
    for j in range(4):
        ax2.plot(
            beta_list, S_list[j], 
            marker = marker_list[j], 
            label = ','.join([param[j][0],f'a={param[j][1]}'])
        )
    ax2.legend(loc='best')

    # 第三个图
    param = [['HL',0.6],['LL',0.6]]
    for j,a in enumerate(param):
        for i, beta in enumerate(beta_list):
            BA_copy = BA.copy()
            set_load0(BA_copy,a = param[j][1], q = 0.5)
            set_cap(BA_copy,beta = beta)

            node_HL = get_HH(BA_copy)
            node_LL = get_LL(BA_copy)

            if param[j][0] == 'HL':
                node = node_HL
            else:
                node = node_LL

            neighbors = attack(BA_copy, node)
            is_ruin(BA_copy, neighbors)

            N_bar = len(BA_copy.nodes())

            S_list[j][i] = N_bar/N

    marker_list = ['o','h']
    fig3 = plt.figure()
    ax3 = fig3.add_subplot(1,1,1)
    for j in range(2):
        ax3.plot(
            beta_list, S_list[j], 
            marker = marker_list[j], 
            label = ','.join([param[j][0],f'a={param[j][1]}'])
        )
    ax3.legend(loc='best')   

    # 显示图片
    plt.show()

