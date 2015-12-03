__author__ = 'siavoosh'

import Scheduling_Functions_Links, Scheduling_Functions_Routers
from ConfigAndPackages import Config

def FindEdge_ASAP_Scheduling_Link(TG, AG, Edge, Link, batch, Prob, Report, logging):
    StartTime = max(Scheduling_Functions_Links.FindLastAllocatedTimeOnLinkForTask(TG, AG, Link, Edge,
                                                                                  Prob, logging),
                    FindEdgePredecessorsFinishTime(TG, AG, Edge, batch))
    EdgeExecutionOnLink = TG.edge[Edge[0]][Edge[1]]['ComWeight']
    if TG.edge[Edge[0]][Edge[1]]['Criticality'] == 'H':
        EndTime = StartTime+EdgeExecutionOnLink+Config.Communication_SlackCount*EdgeExecutionOnLink
    else:
        EndTime = StartTime+EdgeExecutionOnLink
    return StartTime, EndTime


def FindEdge_ASAP_Scheduling_Router(TG, AG, Edge, Node, batch, Prob, Report, logging):
    StartTime = max(Scheduling_Functions_Routers.FindLastAllocatedTimeOnRouterForTask(TG, AG, Node, Edge,
                                                                                  Prob, logging),
                    FindEdgePredecessorsFinishTime(TG, AG, Edge, batch))
    EdgeExecutionOnLink = TG.edge[Edge[0]][Edge[1]]['ComWeight']
    if TG.edge[Edge[0]][Edge[1]]['Criticality'] == 'H':
        EndTime = StartTime+EdgeExecutionOnLink+Config.Communication_SlackCount*EdgeExecutionOnLink
    else:
        EndTime = StartTime+EdgeExecutionOnLink
    return StartTime, EndTime


def FindTestEdge_ASAP_Scheduling(TG, AG, Edge, Link, batch, Prob, Report, logging):
    StartTime = max(Scheduling_Functions_Links.FindLastAllocatedTimeOnLinkForTask(TG, AG, Link, Edge,
                                                                                  Prob, logging),
                    FindEdgePredecessorsFinishTime(TG, AG, Edge, batch))
    EdgeExecutionOnLink = TG.edge[Edge[0]][Edge[1]]['ComWeight']
    EndTime = StartTime+EdgeExecutionOnLink

    return StartTime, EndTime



def FindEdge_ALAP_Scheduling(TG, AG, Edge, Link, batch, Prob, Report, logging):
    # todo: Implement ALAP
    return None


def FindEdgePredecessorsFinishTime(TG, AG, Edge, batch):
    FinishTime = 0
    SourceNode = TG.node[Edge[0]]['Node']
    if Edge[0] in AG.node[SourceNode]['PE'].Scheduling:
        FinishTime = max (AG.node[SourceNode]['PE'].Scheduling[Edge[0]][1], FinishTime)

    for Link in AG.edges():
            # if they are incoming links
            if Edge in AG.edge[Link[0]][Link[1]]['Scheduling']:
                for ScheduleAndBatch in AG.edge[Link[0]][Link[1]]['Scheduling'][Edge]:
                    if ScheduleAndBatch[2] == batch:
                        if ScheduleAndBatch[1] > FinishTime:
                            if Config.FlowControl == "Wormhole":
                                FinishTime = max (ScheduleAndBatch[0]+1,FinishTime)
                            elif Config.FlowControl == "StoreAndForward":
                                FinishTime = max (ScheduleAndBatch[1],FinishTime)
                            else:
                                raise ValueError("FlowControl is not supported")

    for Node in AG.nodes():
        if Edge in AG.node[Node]['Router'].Scheduling:
            for ScheduleAndBatch in AG.node[Node]['Router'].Scheduling[Edge]:
                if ScheduleAndBatch[2] == batch:
                    if ScheduleAndBatch[1] > FinishTime:
                        if Config.FlowControl == "Wormhole":
                            FinishTime = max (ScheduleAndBatch[0]+1,FinishTime)
                        elif Config.FlowControl == "StoreAndForward":
                            FinishTime = max (ScheduleAndBatch[1],FinishTime)
                        else:
                            raise ValueError("FlowControl is not supported")
    return FinishTime