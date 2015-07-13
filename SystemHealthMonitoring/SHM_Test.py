# Copyright (C) 2015 Siavoosh Payandeh Azad
import SystemHealthMonitor
from ConfigAndPackages import Config

def TestSHM(AG):
    print "==========================================="
    print "STARTING SYSTEM HEALTH MAP TESTS..."
    SHM4Test = SystemHealthMonitor.SystemHealthMonitor()
    SHM4Test.SetUp_NoC_SystemHealthMap(AG, Config.TurnsHealth)
    TestBreaking(SHM4Test)
    # todo: needs restoring test etc...
    del SHM4Test
    print "ALL SHM TESTS PASSED..."
    return None


def TestBreaking(SHM):
    for Node in SHM.SHM.nodes():
        SHM.BreakNode(Node,False)
        if SHM.SHM.node[Node]['NodeHealth']:
            raise ValueError('SHM BreakNode DID NOT WORK FOR NODE', Node)
        for Turn in SHM.SHM.node[Node]['TurnsHealth']:
            SHM.BreakTurn(Node, Turn, False)
            if SHM.SHM.node[Node]['TurnsHealth'][Turn]:
                raise ValueError('SHM BreakTurn DID NOT WORK FOR NODE:', Node, 'TURN:', Turn)
    for link in SHM.SHM.edges():
        SHM.BreakLink(link,False)
        if SHM.SHM.edge[link[0]][link[1]]['LinkHealth']:
            raise ValueError('SHM BreakNode DID NOT WORK FOR LINK', link)

