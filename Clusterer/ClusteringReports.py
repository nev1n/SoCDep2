# Copyright (C) 2015 Siavoosh Payandeh Azad


import networkx
import matplotlib.pyplot as plt

def ReportCTG(CTG, filename):
    print "==========================================="
    print "      REPORTING CLUSTERED TASK GRAPH"
    print "==========================================="
    ClusterTaskListDicForDraw = {}
    ClusterWeightDicForDraw = {}
    for node in CTG.nodes():
        print ("\tCLUSTER #: "+str(node)+"\tTASKS:"+str(CTG.node[node]['TaskList'])+"\tUTILIZATION: "+
               str(CTG.node[node]['Utilization']))
        ClusterTaskListDicForDraw[node] = CTG.node[node]['TaskList']
    for edge in CTG.edges():
        print ("\tEDGE #: "+str(edge)+"\tWEIGHT: "+str(CTG.edge[edge[0]][edge[1]]['Weight']))
        ClusterWeightDicForDraw[edge] = CTG.edge[edge[0]][edge[1]]['Weight']
    print ("PREPARING GRAPH DRAWINGS...")
    pos = networkx.shell_layout(CTG)
    networkx.draw_networkx_nodes(CTG, pos, node_size=2200)
    networkx.draw_networkx_edges(CTG, pos)
    networkx.draw_networkx_edge_labels(CTG, pos, edge_labels=ClusterWeightDicForDraw)
    networkx.draw_networkx_labels(CTG, pos, labels=ClusterTaskListDicForDraw)
    plt.savefig("GraphDrawings/"+filename)
    plt.clf()
    print ("\033[35m* VIZ::\033[0mGRAPH DRAWINGS DONE, CHECK \"GraphDrawings/"+filename+"\"")
    return None


def VizClusteringOpt():
    """
    Visualizes the cost of solutions during clustering optimization process
    :return: None
    """
    print ("===========================================")
    print ("GENERATING CLUSTERING OPTIMIZATION VISUALIZATIONS...")

    try:
        ClusteringCostFile = open('Generated_Files/Internal/ClusteringCost.txt', 'r')
        Cost = []
        line = ClusteringCostFile.readline()
        Cost.append(float(line))
        MinCost = float(line)
        MinCostList = []
        MinCostList.append(MinCost)
        while line != "":
            Cost.append(float(line))
            if float(line) < MinCost:
                MinCost = float(line)
            MinCostList.append(MinCost)
            line = ClusteringCostFile.readline()
        SolutionNum = range(0, len(Cost))
        ClusteringCostFile.close()

        plt.plot(SolutionNum, Cost, 'b', SolutionNum, MinCostList, 'r')
        plt.savefig("GraphDrawings/CTG_Opt_Process.png")
        plt.clf()
        print ("\033[35m* VIZ::\033[0mCLUSTERING OPTIMIZATION PROCESS CREATED AT: GraphDrawings/CTG_Opt_Process.png")
    except IOError:
        print ('CAN NOT OPEN ClusteringCost.txt')
    return None