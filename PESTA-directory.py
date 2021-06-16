import ipaddress as ip
import os
import re
import getpass
from datetime import datetime

from routes_class import routes, network


class ValueTooLargeError(Exception):
    """Raised when the input value is too large"""
    pass



directory = os.listdir("configs")
os.chdir("configs")

overlaps = []
to_pop = []
to_del = []
index = 100
to_del_index = 0
user = getpass.getuser()


def get_routes_file(file):
    lists = []
    addr_list = []
    mask_list = []
    gw_list = []
    id_list = []
    routes_list = []
    nw_list = []
    phrase = re.compile("ip route ")
    with open(file, 'r') as inFile, open("static_routes.txt", "w+") as outFile:
        for line in inFile:
            if phrase.match(line):
                line = line.replace(phrase.search(line)[0], '')
                outFile.write(line)
    with open("static_routes.txt", 'r') as inFile:
        for line in inFile:
            pattern_ip = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
            if pattern_ip.match(line):
                addr, mask, gw = re.findall(pattern_ip, line)
                addr_list.append(addr)
                mask_list.append(mask)
                gw_list.append(gw)
                id_list.append(str.rstrip(line.partition("name ")[2]))
        for i in range(len(addr_list)):
            x = routes(addr_list[i], mask_list[i], gw_list[i], id_list[i])
            routes_list.append(x)
            nw_str = str(routes_list[i].address + "/" + routes_list[i].mask)
            nw = ip.ip_network(nw_str)
            y = network(nw, gw_list[i], id_list[i])
            nw_list.append(y)

        lists.append(addr_list)
        lists.append(mask_list)
        lists.append(gw_list)
        lists.append(id_list)
        lists.append(routes_list)
        lists.append(nw_list)
    return lists


def pair(source):
    result = []
    for p1 in range(len(source)):
        for p2 in range(p1 + 1, len(source)):
            result.append([source[p1], source[p2]])
    return result


start_time = datetime.now()

for file in directory:
    os.chdir("C:\\Users\\%s\\PycharmProjects\\PESTA\\configs" % user)
    list_all = get_routes_file(file)
    addr_list = list_all[0]
    mask_list = list_all[1]
    gw_list = list_all[2]
    id_list = list_all[3]
    routes_list = list_all[4]
    nw_list = list_all[5]
    pairings = pair(nw_list)
    y = 0
    n_index = 0
    for par in pairings:
        x = ip.ip_network(par[0].ip).overlaps(ip.ip_network(par[1].ip))
        if x:
            if str(par[0].gw) == str(par[1].gw):
                overlaps.append([par[0], par[1]])
                n_index += 1
                y += 1

    file = "overlaps-" + file
    os.chdir("C:\\Users\\%s\\PycharmProjects\\PESTA\\overlaps" % user)
    with open(file, 'w') as outFile:
        outFile.write("[a] overlaps [b]\n")
        outFile.write("\n%d Rotas a analisar\n\n" % (y))
        for x in range(n_index):
            pair1_nw = ip.IPv4Network(overlaps[x][0].ip)
            pair1_ip = pair1_nw.network_address
            pair1_mask = pair1_nw.netmask
            pair2_nw = ip.IPv4Network(overlaps[x][1].ip)
            pair2_ip = pair2_nw.network_address
            pair2_mask = pair2_nw.netmask
            if overlaps[x][0].name != "":
                pair1_full = ("[a] ip route %s %s %s name %s" % (
                    pair1_ip, pair1_mask, overlaps[x][0].gw, overlaps[x][0].name))
            else:
                pair1_full = ("[a] ip route %s %s %s" % (pair1_ip, pair1_mask, overlaps[x][0].gw))

            if overlaps[x][1].name != "":
                pair2_full = ("[b] ip route %s %s %s name %s" % (
                    pair2_ip, pair2_mask, overlaps[x][1].gw, overlaps[x][1].name))
            else:
                pair2_full = ("[b] ip route %s %s %s" % (pair2_ip, pair2_mask, overlaps[x][1].gw))
            line1 = ("[%d] %s <--> %s" % (x, pair1_nw, pair2_nw))
            line2 = (pair1_full + "\n" + pair2_full)
            outFile.write(line1 + "\n" + line2 + "\n\n")

    overlaps.clear()
