__author__ = 'siavoosh'

import copy

from ConfigAndPackages import Config
from Mapper import Mapping, Mapping_Reports, Mapping_Animation
from Scheduler import Scheduling_Reports
from SystemHealthMonitoring import SystemHealthMonitor, SHM_Reports, SHM_Functions, TestSchedulingUnit
from TaskGraphUtilities import Task_Graph_Reports, TG_Functions, TG_Test
from RoutingAlgorithms import Routing, Calculate_Reachability, ReachabilityReports, RoutingGraph_Reports
from ArchGraphUtilities import Arch_Graph_Reports, AG_Functions, AG_Test
from Scheduler import TrafficTableGenerator


def InitializeSystem(logging):
    TG = copy.deepcopy(TG_Functions.GenerateTG())
    Task_Graph_Reports.ReportTaskGraph(TG, logging)
    Task_Graph_Reports.DrawTaskGraph(TG)
    TG_Test.CheckAcyclic(TG, logging)
    ####################################################################
    AG = copy.deepcopy(AG_Functions.GenerateAG(logging))
    AG_Functions.UpdateAGRegions(AG)
    AG_Test.AG_Test()
    Arch_Graph_Reports.DrawArchGraph(AG)
    ####################################################################
    SHM = SystemHealthMonitor.SystemHealthMonitor()
    SHM.SetUp_NoC_SystemHealthMap(AG, Config.TurnsHealth)
    # SHM_Reports.Report_NoC_SystemHealthMap()
    # Here we are injecting initial faults of the system
    SHM_Functions.ApplyInitialFaults(SHM)

    if Config.SetRoutingFromFile:
        NoCRG = Routing.GenerateNoCRouteGraphFromFile(AG, SHM, Config.RoutingFilePath, Config.DebugInfo, Config.DebugDetails)
    else:
        NoCRG = copy.deepcopy(Routing.GenerateNoCRouteGraph(AG, SHM, Config.UsedTurnModel, Config.DebugInfo, Config.DebugDetails))
    # Some visualization...
    RoutingGraph_Reports.DrawRG(NoCRG)
    ####################################################################
    # PMC-Graph
    # at this point we assume that the system health map knows about the initial faults from
    # the diagnosis process
    if Config.OneStepDiagonosable:
        PMCG = TestSchedulingUnit.GenerateOneStepDiagnosablePMCG(AG,SHM)
    else:
        PMCG = TestSchedulingUnit.GenerateSequentiallyDiagnosablePMCG(AG,SHM)
    TestSchedulingUnit.DrawPMCG(PMCG)
    TTG = TestSchedulingUnit.GenerateTestTGFromPMCG(PMCG)
    TestSchedulingUnit.DrawTTG(TTG)
    ####################################################################
    # in case of partitioning, we have to route based on different Route-graphs
    if Config.EnablePartitioning:
        CriticalRG, NonCriticalRG = Calculate_Reachability.CalculateReachabilityWithRegions(AG,SHM)
        ReachabilityReports.ReportGSNoCFriendlyReachabilityInFile(AG)
    else:
        # Reachability_Test.ReachabilityTest()
        CriticalRG, NonCriticalRG = None, None
        Calculate_Reachability.CalculateReachability(AG, NoCRG)
        Calculate_Reachability.OptimizeReachabilityRectangles(AG, Config.NumberOfRects)
        # ReachabilityReports.ReportReachability(AG)
        ReachabilityReports.ReportReachabilityInFile(AG, "ReachAbilityNodeReport")
        ReachabilityReports.ReportGSNoCFriendlyReachabilityInFile(AG)
    ####################################################################
    BestTG, BestAG = Mapping.Mapping(TG, AG, NoCRG, CriticalRG, NonCriticalRG, SHM, logging)
    if BestAG is not None and BestTG is not None:
        TG = copy.deepcopy(BestTG)
        AG = copy.deepcopy(BestAG)
        del BestTG, BestAG
        # SHM.AddCurrentMappingToMPM(TG)
    Mapping_Reports.DrawMappingDistribution(AG, SHM)
    Mapping_Reports.DrawMapping(TG, AG, SHM)
    print "==========================================="
    print "SYSTEM IS UP..."
    Scheduling_Reports.GenerateGanttCharts(TG, AG)
    TrafficTableGenerator.GenerateNoximTrafficTable()
    TrafficTableGenerator.GenerateGSNoCTrafficTable(AG, TG)
    if Config.GenMappingFrames:
        Mapping_Animation.GenerateFrames(TG, AG, SHM)
    return TG, AG, SHM, NoCRG, CriticalRG, NonCriticalRG, PMCG