import re
import ipaddress as ip
from datetime import datetime
from routes_class import routes, network


class ValueTooLargeError(Exception):
    """Raised when the input value is too large"""
    pass


overlaps = []
to_pop = []
to_del = []
index = 100
to_del_index = 0


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
list_all = get_routes_file("configs/avr03swg001-confg.txt")
addr_list = list_all[0]
mask_list = list_all[1]
gw_list = list_all[2]
id_list = list_all[3]
routes_list = list_all[4]
nw_list = list_all[5]

pairings = pair(nw_list)
y = 0
n_index = 0

for pair in pairings:
    x = ip.ip_network(pair[0].ip).overlaps(ip.ip_network(pair[1].ip))
    y += 1

    if x == True:
        if str(pair[0].gw) == str(pair[1].gw):
            overlaps.append([pair[0], pair[1]])
            n_index += 1

print("Teste feito a %d pares possíveis" % (y))
print("%d Overlaps" % (n_index))

with open("overlapped.txt", 'w+') as outFile:
    outFile.write("[a] overlaps [b]\n\n")
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

print("Consulte o ficheiro overlapped.txt para consultar os indexs de sobreposições\n")
prompt = "Introduza o index da rota [b] que pretende que seja eliminada ou pressione a letra 'q' para terminar: "
while index != 'q':
    while True:
        try:
            index = input(prompt)
            index = int(index)
            if index > (n_index - 1):
                raise ValueTooLargeError
            else:
                to_pop.append(index)
                prompt = "Introduza mais um index ou pressione a letra 'q' para terminar: "
                break
        except ValueError:
            if index == 'q':
                print("Terminado")
                break
            else:
                prompt = "O input não é um número, tente novamente: "
        except ValueTooLargeError:
            prompt = "O input excede o número de entradas, tente novamente: "

for ele in sorted(to_pop, reverse=True):
    to_del.append(overlaps[ele])
    to_del_index += 1

with open("delete_routes.txt", 'w+') as outFile:
    for x in range(to_del_index):
        delete_nw = ip.IPv4Network(to_del[x][1].ip)
        delete_ip = delete_nw.network_address
        delete_mask = delete_nw.netmask
        if to_del[x][1].name != "":
            delete_full = (
                        "no ip route %s %s %s name %s\n" % (delete_ip, delete_mask, to_del[x][1].gw, to_del[x][1].name))
        else:
            delete_full = ("no ip route %s %s %s\n" % (delete_ip, delete_mask, to_del[x][1].gw))
        outFile.write(delete_full)


end_time = datetime.now()

print('\nDuration: {}'.format(end_time - start_time))

