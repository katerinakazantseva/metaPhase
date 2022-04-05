import csv
import pysam
import pandas as pd
from collections import Counter
import sys,os,subprocess
import networkx as nx
import matplotlib.pyplot as plt
from build_adj_matrix import *
import pygraphviz as gv
import pylab
from community_detection import find_communities


def build_data(cl,SNP_pos, data):
    clusters = sorted(set(cl.loc[cl['Cluster'] != 'NA']['Cluster'].values))
    cons = {}
    for cluster in clusters:
       cons=cluster_consensuns(cl,cluster,SNP_pos, data, cons)
    return(cons)


def cluster_consensuns(cl,cluster,SNP_pos, data, cons):
    strange = 0
    val = {}
    clSNP = []
    for pos in SNP_pos:
        npos = []
        for read in cl.loc[cl['Cluster'] == cluster]['ReadName'].values:
            #print(read)
            try:
                npos.append(data[read][pos])
            except(KeyError):
                continue
        try:
            if len(npos)>=2:
                val[pos] = Counter(npos).most_common(1)[0][0]
            if int(Counter(npos).most_common(2)[1][1]) >= 2:
                strange = 1
                clSNP.append(pos)
        except(IndexError):
            continue
    if strange == 1:
        val["Strange"]=1
    else:
        val["Strange"] =0
    val["clSNP"]=clSNP
    cons[cluster] = val

    return(cons)


def split_cluster(cl,cluster, data,clSNP, bam, edge, child_clusters, R, I):
    print("Strange cluster detected")
    print(cluster)
    reads=sorted(set(cl.loc[cl['Cluster'] == cluster]['ReadName'].values))
    m=build_adj_matrix2(cl[cl['Cluster'] == cluster], data, clSNP, I, bam,edge,R)
    m = remove_edges(m, 1)
    m.columns=range(0,len(cl[cl['Cluster'] == cluster]['ReadName']))
    m.index=range(0,len(cl[cl['Cluster'] == cluster]['ReadName']))
    m = change_w(m, R)
    G = nx.from_pandas_adjacency(m)
    cluster_membership = find_communities(G)
    clN=0
    uncl=0
    reads = cl[cl['Cluster'] == cluster]['ReadName'].values
    for value in set(cluster_membership.values()):
        group = [k for k, v in cluster_membership.items() if v == value]
        if len(group) > 3:
            clN = clN + 1
            child_clusters.append(cluster+10000+clN)
            for i in group:
                cl.loc[cl['ReadName'] == reads[i], "Cluster"] =  cluster+10000+clN

        else:
            uncl = uncl + 1
            for i in group:
                cl.loc[cl['ReadName'] == reads[i], "Cluster"] = 'NA'

    print(str(clN)+" new clusters found")


def distance_clusters(first_cl,second_cl, cons,SNP_pos):
    d=-1
    print("distance "+str(first_cl)+" "+str(second_cl))
    firstSNPs=list(cons[first_cl].keys())
    firstSNPs.remove('clSNP')
    firstSNPs.remove('Strange')
    secondSNPs=list(cons[second_cl].keys())
    secondSNPs.remove('clSNP')
    secondSNPs.remove('Strange')
    commonSNP=sorted(set(firstSNPs).intersection(secondSNPs))
    #print(commonSNP)
    try:
        if abs(int(commonSNP[len(commonSNP)-1])-int(commonSNP[0]))>=1000:
            for snp in SNP_pos:
                try:
                    b1=cons[first_cl][snp]
                    b2=cons[second_cl][snp]
                    if b1 != b2 and len(b1)!=0 and  len(b2)!=0:
                        if d==-1:
                            d=0
                        d=d+1
                    elif b1 == b2:
                        if d==-1:
                            d=0
                        d=d
                except:
                    continue
                if d>=1:
                    d=1
                    break

                else:
                    continue
    except(IndexError):pass
    print(d)
    return (d)



def build_adj_matrix_clusters (cons, SNP_pos,cl):
    clusters = sorted(set(cl.loc[cl['Cluster'] != 'NA']['Cluster'].values))
    Y=[]
    X=[]
    #print(cons)
    for k,v in cons.items():
        X.append(k)
        Y.append(int(list(v.keys())[0]))

    from more_itertools import sort_together
    sorted_by_pos=sort_together([Y, X])[1]
    #sorted_by_pos = sorted(sorted_cl, key=sorted_cl.get)

    clusters=sorted(set(sorted_by_pos) & set(clusters), key=sorted_by_pos.index)
    #print(clusters)
    m = pd.DataFrame(-1, index=clusters, columns=clusters)
    for i in range(0,m.shape[1]):
        first_cl=m.index[i]
        for k in range(i+1,m.shape[1]):
            second_cl=m.index[k]
            #try:
            if m[second_cl][first_cl]==-1:
                m[second_cl][first_cl] = distance_clusters(first_cl,second_cl, cons,SNP_pos)
            #except: (KeyError)
    return (m)


def join_clusters(cons, SNP_pos, cl,R, edge):
    M = build_adj_matrix_clusters(cons, SNP_pos, cl)
    #print(M)

    M=change_w(M,R)
    #M.to_csv("output/adj_M/clusters_adj_M2_%s.csv" % edge)
    G_vis = nx.from_pandas_adjacency(M, create_using=nx.DiGraph)
    #to_remove = [(a, b) for a, b, attrs in G_vis.edges(data=True) if attrs["weight"] != 0.001]
    #G_vis.remove_edges_from(to_remove)
    G_vis.remove_edges_from(list(nx.selfloop_edges(G_vis)))
    #print(G_vis)
    to_remove = []
    #for node in G_vis.nodes():
        #print(node)

     #   if len(list(G_vis.successors(node)))>=2:
      #      for i in list(G_vis.successors(node)):
       #         #print(i)
        #        for k in list(G_vis.edges([node, i])):
         #           to_remove.append(k)


    #to_remove=list(to_remove)
    #print(to_remove)

    lis=list(nx.topological_sort(nx.line_graph(G_vis)))
    first=[]
    last=[]

    for i in lis:
        first.append(i[0])
        last.append(i[1])

    for i in lis:
        if first.count(i[0]) > 1 or last.count(i[1]) > 1:
            to_remove.append(i)

        #nx.draw(G_vis, nodelist=G_vis.nodes(), with_labels=True, width=0.1, node_size=3, font_size=5)
    #plt.savefig("output/graphs/cluster_GV_graph_%s_beforeremove.png" % (edge), format="PNG", dpi=300)
    G_vis_temp = nx.nx_agraph.to_agraph(G_vis)
    G_vis_temp.layout(prog="neato")
    G_vis_temp.draw("output/graphs/cluster_GV_graph_%s_beforeremove.png" % (edge))
    G_vis.remove_edges_from(ebunch=to_remove)
        #if len(list(G_vis.predecessor(node)))>=2:
         #   for i in list(G_vis.predecessor(node)):
          #      print(G.edges([node, i]))
           #     G_vis.remove_edges_from(G.edges([node,i ]))
    #print(G_vis)
    G_vis = nx.nx_agraph.to_agraph(G_vis)

    #print(G_vis)
    G_vis.layout(prog="neato")
    G_vis.draw("output/graphs/cluster_GV_graph_%s.png" % (edge))
    #G_vis.draw("output/graphs/cluster_GV_graph_%s.png" % (edge))
    #nx.draw(G_vis, nodelist=G_vis.nodes(), with_labels=True, width=0.1, node_size=3, font_size=5)
    #plt.savefig("output/graphs/cluster_graph_%s.png" % (edge), format="PNG", dpi=300)
    #plt.close()
    G = nx.from_pandas_adjacency(M)
    G.remove_edges_from(ebunch=to_remove)

    groups = list(nx.connected_components(G))

    print(groups)
    for group in groups:
        if len(group) > 0:
            for i in range(1, len(group)):
                cl.loc[cl['Cluster'] == list(group)[i], 'Cluster'] = list(group)[0]
    return (cl)

def postprocess (bam,cl,SNP_pos, data, edge, R, I):
    cons=build_data(cl, SNP_pos, data)
    print(cons)
    for key, val in cons.copy().items():
        if val["Strange"]==1:
            cluster=key
            clSNP=val["clSNP"]
            child_clusters=[]
            split_cluster(cl, cluster, data, clSNP, bam, edge,child_clusters, R, I)
            for child in child_clusters:
                cluster=child
                cluster_consensuns(cl,cluster,SNP_pos, data, cons)
    cl=join_clusters(cons, SNP_pos, cl,R, edge)
    return(cl)
