import networkx as nx
import math

def retiming(node, G):
    in_edges = list(G.in_edges(node, data=True))
    out_edges = list(G.edges(node, data=True))
    
    for in_edge in in_edges:
        if in_edge[2]["weight"] == 0 :
            retiming(in_edge[0], G)
            
    for in_edge in in_edges:
        edge_data = G.get_edge_data(*in_edge)
        edge_data["weight"] -= 1
        
    for out_edge in out_edges:
        edge_data = G.get_edge_data(*out_edge)
        edge_data["weight"] += 1
    
    G.nodes[node]["rt"] += 1

def max_path(source_node, target_node, G):
    # 找出兩節點間所有路徑
    all_paths = list(nx.all_simple_paths(G, source=source_node, target=target_node))
    # 排除中間有D的路徑
    for i in range(len(all_paths)):
        have_D = 0
        for y in range(len(all_paths[i])-1):
            edge_data = G.get_edge_data(all_paths[i][y], all_paths[i][y+1])
            if edge_data["weight"]!=0:
                have_D = 1
                break
        if have_D:
            all_paths[i] = []
    max = 0
    max_path = []
    for path in all_paths:
        sum = 0
        for node in path:
            sum += G.nodes[node]["value"]
        if sum>=max : 
            max = sum
            max_path = path
    return [max_path, max]

def p(path):
    if path == [] : return "no path"
    str = path[0]
    for i in range(len(path)-1):
        str += " -> " + path[i+1]
    return str

def critical(G):
    # 找出有D的edge
    all_edges = list(G.edges(data=True))  
    D_edge = []
    for edge in all_edges:
        if edge[2]["weight"]!=0 : D_edge.append(edge)
    max = 0
    critical = []
    for i in range(len(D_edge)):
        for x in range(len(D_edge)):
            m = max_path(D_edge[i][1], D_edge[x][0], G)
            if m[1]>=max:
                max = m[1]
                critical = m[0]

    return [critical, max]

def iter_b(G):
    # 找出所有loop
    all_cycles = list(nx.simple_cycles(G))
    iter_bound = 0
    iter_path = []
    for cycle in all_cycles:
        sum = G.nodes[cycle[0]]["value"]
        d_num = 0

        for i in range(len(cycle)-1):
            edge_data = G.get_edge_data(cycle[i], cycle[i+1])
            d_num += edge_data["weight"]
            sum += G.nodes[cycle[i+1]]["value"]

        # 算最後一點到第一個點的D
        edge_data = G.get_edge_data(cycle[-1], cycle[0])
        d_num += edge_data["weight"]

        
        iter = sum/d_num if d_num!=0 else 0
        if(iter >= iter_bound) : 
            iter_bound = iter
            iter_path = cycle
        
        iter_path = iter_path if iter!=0 else []
        
    return [iter_bound,iter_path]

def floyd_warshall(G):
    matrix = {}
    #create start matrix
    for n in G.nodes:
        matrix[n]={}
        for m in G.nodes:
            matrix[n][m]=999
        
    for edge in G.edges(data=True):
        matrix[edge[0]][edge[1]]=edge[2]["weight"]

    for i in range(len(G.nodes())+1):
        for k in G.nodes:
            for v in G.nodes:
                for u in G.nodes:
                    if matrix[u][v] > matrix[u][k] + matrix[k][v]:
                        matrix[u][v] = matrix[u][k] + matrix[k][v]

    return(matrix)

def solve_ineq(G):
    # add new graph
    G1 = nx.DiGraph()
    for node in G.nodes(data=True):
        G1.add_node(node[0],value=node[1]["value"],rt=node[1]["rt"])
    # change direction of edge 
    for edge in G.edges(data=True):
        G1.add_edge(edge[1],edge[0],weight=edge[2]["weight"])

    # add dummy node
    G1.add_node("dummy",value=0,rt=0)
    # add dummy edge
    for node in G1.nodes():
        if node != "dummy":
            G1.add_edge("dummy", node, weight=0)
    
    matrix = floyd_warshall(G1)
    # check if negitive loop exit
    for node in matrix:
        if matrix[node][node] < 0:
            #print("negitive loop exit")
            return {}

    del matrix["dummy"]["dummy"]

    return(matrix["dummy"])

def clk_minimize(G):
    # new graph
    G1 = nx.DiGraph()
    n = len(G.nodes())
    tmax = 0

    for node in G.nodes(data=True):
        G1.add_node(node[0],value=node[1]["value"],rt=node[1]["rt"])
        if node[1]["value"] > tmax:
            tmax = node[1]["value"]
    M = n*tmax

    if(M==0):
        return[0,0,[]]

    for edge in G.edges(data=True):
        weight_ = M*edge[2]["weight"]-G.nodes[edge[0]]["value"]
        G1.add_edge(edge[0],edge[1],weight=weight_)
    
    # solve G1
    matrix = floyd_warshall(G1)
    W={}
    D={}
    for u in matrix:
        W[u]={}
        D[u]={}
        for v in matrix[u]:
            if u==v:
                W[u][v] = 0
                D[u][v] = G.nodes[u]["value"]
            else:
                W[u][v] = math.ceil(matrix[u][v]/M)
                D[u][v] = M*W[u][v]-matrix[u][v]+G.nodes[v]["value"]
    
    iter_bound = iter_b(G)[0]
    clk_list=[]
    # find possible clk in D
    for u in D:
        for v in D[u]:
            if D[u][v] >= iter_bound and not(D[u][v] in clk_list):
                clk_list.append(D[u][v])
                clk_list.sort()

    # add inequalities in graph
    found = 0
    for clk in clk_list:
        G2 = nx.DiGraph()
        G2 = G1.copy()
        # search D for edge that bigger than clk
        for u in D:
            for v in D[u]:
                if D[u][v] > clk:
                    G2.add_edge(u,v,weight=W[u][v]-1)
        # solve G2
        matrix2 = solve_ineq(G2)
        if matrix2!={}:
            found = 1
            #print("minimun clk = ",clk)
            ans=[]
            for node in matrix2:
                ans.append("r("+node+")"+" = "+str(matrix2[node]))
            return[found,clk,ans]
            break
    
    if found == 0:
        return[found,0,[]]