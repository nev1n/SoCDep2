# Copyright (C) 2015 Siavoosh Payandeh Azad 
import copy, random
from TaskGraphUtilities import TG_Functions
from ArchGraphUtilities import AG_Functions
from Scheduler import Scheduler
from Mapper import Mapping_Functions
from RoutingAlgorithms import Calculate_Reachability

def NMap (TG, AG, NoCRG, CriticalRG, NonCriticalRG, SHM, logging):
    print "==========================================="
    print "STARTING N-MAP MAPPING...\n"

    if len(TG.nodes()) > len(AG.nodes()):
        raise ValueError("Number of tasks should be smaller or equal to number of PEs")

    MappedTasks = []
    UnmappedTasks = copy.deepcopy(TG.nodes())
    AllocatedNodes =[]
    UnAllocatedNodes = copy.deepcopy(AG.nodes())

    # remove all broken nodes from UnAllocatedNodes list
    for node in UnAllocatedNodes:
        if not SHM.SHM.node[node]['NodeHealth']:
            UnAllocatedNodes.remove(node)
            print "REMOVED BROKEN NODE", node, "FROM UN-ALLOCATED NODES"

    print "------------------"
    print "STEP 1:"
    #step 1: find the task with highest weighted communication volume
    TasksComDict = TG_Functions.TasksCommunicationWeight(TG)
    SortedTasksCom = sorted(TasksComDict, key=TasksComDict.get, reverse=True)
    print "\t SORTED TASKS BY COMMUNICATION WEIGHT:\n", "\t ", SortedTasksCom
    print "\t -------------"
    ChosenTask = SortedTasksCom[0]
    print "\t CHOSEN TASK:", ChosenTask
    MappedTasks.append(ChosenTask)
    print "\t ADDED TASK", ChosenTask, "TO MAPPED TASKS LIST"
    UnmappedTasks.remove(ChosenTask)
    print "\t REMOVED TASK", ChosenTask, "FROM UN-MAPPED TASKS LIST"

    print "------------------"
    print "STEP 2:"
    NodeNeighborsDict = AG_Functions.NodeNeighbors(AG, SHM)
    SortedNodeNeighbors = sorted(NodeNeighborsDict, key=NodeNeighborsDict.get, reverse=True)
    MaxNeighborsNode = AG_Functions.MaxNodeNeighbors(NodeNeighborsDict, SortedNodeNeighbors)
    print "\t SORTED NODES BY NUMBER OF NEIGHBOURS:\n", "\t ", SortedNodeNeighbors
    print "\t -------------"
    print "\t NODES WITH MAX NEIGHBOURS:\t", MaxNeighborsNode
    ChosenNode = random.choice(MaxNeighborsNode)

    print "\t CHOSEN NODE:", ChosenNode
    AllocatedNodes.append(ChosenNode)
    print "\t ADDED NODE", ChosenNode, "TO ALLOCATED NODES LIST"
    UnAllocatedNodes.remove(ChosenNode)
    print "\t REMOVED NODE", ChosenNode, "FROM UN-ALLOCATED NODES LIST"
    # Map Chosen Task on Chosen Node...
    if Mapping_Functions.MapTaskToNode(TG, AG, SHM, NoCRG, CriticalRG,
                                            NonCriticalRG, ChosenTask, ChosenNode, logging):
        print "\t \033[32m* NOTE::\033[0mTASK", ChosenTask, "MAPPED ON NODE", ChosenNode
    else:
        raise ValueError("Mapping task on node failed...")

    print "------------------"
    print "STEP 3:"
    while len(UnmappedTasks)>0:
        print "  UN-MAPPED TASKS #:", len(UnmappedTasks)
        print "\t -------------"
        print "\t STEP 3.1:"
        # find the unmapped task which communicates most with MappedTasks
        MaxCom = 0
        UnmappedTasksCom = {}
        TasksWithMaxComToMapped =[]
        for Task in UnmappedTasks:
            TaskWeight = 0
            for MappedTask in MappedTasks:
                if (Task, MappedTask) in TG.edges():
                    TaskWeight += TG.edge[Task][MappedTask]["ComWeight"]
                if (MappedTask, Task) in TG.edges() :
                    TaskWeight += TG.edge[MappedTask][Task]["ComWeight"]
            UnmappedTasksCom[Task]=TaskWeight
            if MaxCom < TaskWeight:
                MaxCom = TaskWeight
                TasksWithMaxComToMapped = [Task]
            elif MaxCom == TaskWeight:
                TasksWithMaxComToMapped.append(Task)
        print "\t MAX COMMUNICATION WITH THE MAPPED TASKS:", MaxCom
        print "\t TASK(S) WITH MAX COMMUNICATION TO MAPPED TASKS:",TasksWithMaxComToMapped
        if len(TasksWithMaxComToMapped) > 1:
            # multiple tasks with same comm to mapped
            # Find the one that communicate most with Un-mapped takss...
            CandidTaskWithMaxComToUnMapped =[]
            MaxCom = 0
            for CandidateTask in TasksWithMaxComToMapped:
                TaskWeight = 0
                for UnMappedTask in UnmappedTasks:
                    if (Task, UnMappedTask) in TG.edges():
                        TaskWeight += TG.edge[Task][UnMappedTask]["ComWeight"]
                    if (UnMappedTask, Task) in TG.edges() :
                        TaskWeight += TG.edge[UnMappedTask][Task]["ComWeight"]
                if TaskWeight > MaxCom:
                    CandidTaskWithMaxComToUnMapped = [CandidateTask]
                elif TaskWeight == MaxCom:
                    CandidTaskWithMaxComToUnMapped.append(CandidateTask)
            print "\t CANDIDATE TASK(S) THAT COMMUNICATE MOST WITH UN_MAPPED:",CandidTaskWithMaxComToUnMapped
            if len(CandidTaskWithMaxComToUnMapped) > 1:
                # if multiple tasks with the same com to unmmaped also,
                # choose randomly
                ChosenTask = random.choice(CandidTaskWithMaxComToUnMapped)
            else:
                ChosenTask = CandidTaskWithMaxComToUnMapped[0]
        else:
            ChosenTask = TasksWithMaxComToMapped[0]

        print "\t CHOSEN TASK:", ChosenTask

        # Find the unallocated tile with lowest communication cost to/from the allocated_tiles_set.
        print "\t -------------"
        print "\t STEP 3.2:"
        MinCost = float("inf")
        NodeCandidates=[]
        for UnAllocatedNode in UnAllocatedNodes:
            Cost = 0
            Reachable = True
            for MappedTask in MappedTasks:
                ComWeight = 0
                if (ChosenTask, MappedTask) in TG.edges():
                    # print "TASK CONNECTED TO MAPPED TASK:", MappedTask
                    ComWeight += TG.edge[ChosenTask][MappedTask]["ComWeight"]
                    DestNode = TG.node[MappedTask]['Node']
                    # here we check if this node is even reachable from the chosen node?
                    if Calculate_Reachability.IsDestReachableFromSource(NoCRG, UnAllocatedNode, DestNode):
                        ManhatanDistance = AG_Functions.ManhattanDistance(UnAllocatedNode,DestNode)
                        Cost += ManhatanDistance * ComWeight
                    else:
                        Reachable = False
                elif (MappedTask, ChosenTask) in TG.edges() :
                    # print "TASK CONNECTED TO MAPPED TASK:", MappedTask
                    ComWeight += TG.edge[MappedTask][ChosenTask]["ComWeight"]
                    DestNode = TG.node[MappedTask]['Node']
                    # here we check if this node is even reachable from the chosen node?
                    if Calculate_Reachability.IsDestReachableFromSource(NoCRG, DestNode, UnAllocatedNode):
                        ManhatanDistance = AG_Functions.ManhattanDistance(UnAllocatedNode,DestNode)
                        Cost += ManhatanDistance * ComWeight
                    else:
                        Reachable = False
            if Reachable:
                if Cost < MinCost:
                    NodeCandidates = [UnAllocatedNode]
                    MinCost = Cost
                elif Cost == MinCost:
                    NodeCandidates.append(UnAllocatedNode)
            else:
                # print  "NODE ", UnAllocatedNode, "NOT REACHABLE..."
                pass
        print "\t CANDIDATE NODES:", NodeCandidates, "MIN COST:", MinCost

        if len(NodeCandidates) == 0:
            raise ValueError("COULD NOT FIND A REACHABLE CANDIDATE NODE...")
        elif len(NodeCandidates)>1:
            ChosenNode = random.choice(NodeCandidates)
        elif len(NodeCandidates) == 1:
            ChosenNode = NodeCandidates[0]
        else:
            # this means that the chosen task is not connected to any other task... so its cost is infinity
            ChosenNode = random.choice(UnAllocatedNodes)

        MappedTasks.append(ChosenTask)
        print "\t ADDED TASK", ChosenTask, "TO MAPPED TASKS LIST"
        UnmappedTasks.remove(ChosenTask)
        print "\t REMOVED TASK", ChosenTask, "FROM UN-MAPPED TASKS LIST"

        AllocatedNodes.append(ChosenNode)
        print "\t ADDED NODE", ChosenNode, "TO ALLOCATED NODES LIST"
        UnAllocatedNodes.remove(ChosenNode)
        print "\t REMOVED NODE", ChosenNode, "FROM UN-ALLOCATED NODES LIST"

        if Mapping_Functions.MapTaskToNode(TG, AG, SHM, NoCRG, CriticalRG,
                                            NonCriticalRG, ChosenTask, ChosenNode, logging):
            print "\t \033[32m* NOTE::\033[0mTASK", ChosenTask, "MAPPED ON NODE", ChosenNode
        else:
            raise ValueError("Mapping task on node failed...")

    Scheduler.ScheduleAll(TG,AG,SHM,True,False)
    return TG, AG