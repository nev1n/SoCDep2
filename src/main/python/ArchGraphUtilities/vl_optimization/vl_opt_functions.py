# Copyright (C) Siavoosh Payandeh Azad

from ConfigAndPackages import Config
from ArchGraphUtilities.AG_Functions import return_node_number, return_node_location
from RoutingAlgorithms import Calculate_Reachability
import random
import copy


def find_all_vertical_links(ag):
    vertical_link_list = []
    for link in ag.edges():
        # if these nodes are on different layers
        if return_node_location(link[0])[2] != return_node_location(link[1])[2]:
            if link not in vertical_link_list:
                vertical_link_list.append(link)
    return vertical_link_list


def remove_all_vertical_links(shm, ag):
    vertical_link_list = find_all_vertical_links(ag)
    for VLink in vertical_link_list:
        shm.break_link(VLink, False)
    return None


def find_feasible_ag_vertical_link_placement(ag, shmu):
    new_vertical_link_lists = []
    for i in range(0, Config.VerticalLinksNum):
        source_x = random.randint(0, Config.Network_X_Size-1)
        source_y = random.randint(0, Config.Network_Y_Size-1)
        source_z = random.randint(0, Config.Network_Z_Size-1)
        source_node = return_node_number(source_x, source_y, source_z)
        possible_z = []
        if source_z+1 <= Config.Network_Z_Size-1:
            possible_z.append(source_z+1)
        if 0 <= source_z-1:
            possible_z.append(source_z-1)
        destination_node = return_node_number(source_x, source_y, random.choice(possible_z))
        while shmu.SHM.edge[source_node][destination_node]['LinkHealth']:
            source_x = random.randint(0, Config.Network_X_Size-1)
            source_y = random.randint(0, Config.Network_Y_Size-1)
            source_z = random.randint(0, Config.Network_Z_Size-1)
            source_node = return_node_number(source_x, source_y, source_z)
            possible_z = []
            if source_z + 1 <= Config.Network_Z_Size-1:
                possible_z.append(source_z+1)
            if 0 <= source_z-1:
                possible_z.append(source_z-1)
            destination_node = return_node_number(source_x, source_y, random.choice(possible_z))

        # here we have a candidate to restore
        shmu.restore_broken_link((source_node, destination_node), False)
        new_vertical_link_lists.append((source_node, destination_node))
    return new_vertical_link_lists


def return_to_solution(ag, shm, vertical_link_list):
    remove_all_vertical_links(shm, ag)
    for link in vertical_link_list:
        shm.restore_broken_link(link, False)
    return None


def move_to_new_vertical_link_configuration(ag, shmu, vertical_link_lists):
    new_vertical_link_lists = copy.deepcopy(vertical_link_lists)
    chosen_link_to_fix = random.choice(new_vertical_link_lists)
    new_vertical_link_lists.remove(chosen_link_to_fix)
    shmu.break_link(chosen_link_to_fix, False)

    source_x = random.randint(0, Config.Network_X_Size-1)
    source_y = random.randint(0, Config.Network_Y_Size-1)
    source_z = random.randint(0, Config.Network_Z_Size-1)
    source_node = return_node_number(source_x, source_y, source_z)
    possible_z = []
    if source_z + 1 <= Config.Network_Z_Size-1:
        possible_z.append(source_z + 1)
    if 0 <= source_z - 1:
        possible_z.append(source_z - 1)
    destination_node = return_node_number(source_x, source_y, random.choice(possible_z))

    while source_node == destination_node or \
            shmu.SHM.edge[source_node][destination_node]['LinkHealth']:
        source_x = random.randint(0, Config.Network_X_Size-1)
        source_y = random.randint(0, Config.Network_Y_Size-1)
        source_z = random.randint(0, Config.Network_Z_Size-1)
        source_node = return_node_number(source_x, source_y, source_z)
        possible_z = []
        if source_z+1 <= Config.Network_Z_Size-1:
            possible_z.append(source_z+1)
        if 0 <= source_z-1:
            possible_z.append(source_z-1)
        destination_node = return_node_number(source_x, source_y, random.choice(possible_z))
    # here we have a candidate to restore
    shmu.restore_broken_link((source_node, destination_node), False)
    new_vertical_link_lists.append((source_node, destination_node))
    return new_vertical_link_lists


def cleanup_ag(ag, shmu):
    for link in shmu.SHM.edges():
        if not shmu.SHM.edge[link[0]][link[1]]['LinkHealth']:
            ag.remove_edge(link[0], link[1])
    return None


def vl_cost_function(ag, routing_graph):
    return Calculate_Reachability.reachability_metric(ag, routing_graph, False)