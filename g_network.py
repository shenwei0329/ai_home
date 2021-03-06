# -*- coding: UTF-8 -*-
#

import mongodb_class
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime, date, timedelta



def macs_graph(macs):

    _G = nx.Graph()
    nodes = {}
    edges = {}
    for _mac in macs:
        if _mac[0] not in nodes:
            _G.add_node(_mac[0])
            nodes[_mac[0]] = 0
        if _mac[1] not in nodes:
            _G.add_node(_mac[1])
            nodes[_mac[1]] = 0

        if _mac[0]+_mac[1] not in edges:
            edges[_mac[0] + _mac[1]] = 0
            _G.add_edge(_mac[0], _mac[1])

        nodes[_mac[0]] += 1
        nodes[_mac[1]] += 1
        edges[_mac[0]+_mac[1]] += 1

    _n = sorted(nodes, key=lambda x: nodes[x], reverse=True)
    if len(_n) > 200:
        _v1 = nodes[_n[32]]
        _max = float(_v1)/12.
        _min = float(nodes[_n[200]])/_max
    else:
        _min = 0.
        _max = float(nodes[len(_n)/3])/18.

    print _max, _min

    label = {}
    node_size = []
    node_color = []
    for _n in _G.nodes():
        try:
           _size = float(nodes[_n])/_max
        except Exception, e:
            print e
            _size = 0.5
        if _size > 12.:
            label[_n] = _n
            # print _size, _n
            node_color.append('red')
            node_size.append(_size)
        elif _size > _min:
            label[_n] = ""
            node_color.append('green')
            node_size.append(_size)
        else:
            _G.remove_node(_n)

    return _G, node_size, label, node_color


if __name__ == '__main__':

    db = mongodb_class.mongoDB()
    db.connect_db("wifi_probe")

    yesterday = date.today() + timedelta(days=-1)
    _bg_time = yesterday.strftime("%Y-%m-%d") + " 00:00:00"
    _now = str(datetime.now()).split(' ')[0] + " 00:00:00"

    print _bg_time, " --> ", _now

    _sql = {
            "type": "02",
            "$and": [{"tc": {"$gt": _bg_time}}, {"tc": {"$lte": _now}}]
            }

    _rec = db.handler("rec", "find", _sql)

    _macs = []

    print _rec.count()
    for _r in _rec:
        _mac = (_r['src'], _r['dst'], str(_r['RSSI'])[0:3])
        # print _mac
        _macs.append(_mac)

    G, _node_size, _label, _node_color = macs_graph(_macs)

    try:

        plt.figure(figsize=(12, 8))
        # with nodes colored by degree sized by population
        nx.draw(G,
                linewidths=0.01,
                node_shape='o',
                node_size=_node_size,
                node_color=_node_color,
                edge_size=0.1,
                alpha=0.6,
                edge_color='y',
                labels=_label,
                with_labels=True,
                # font_weight="bold",
                font_size=6,
                )

        plt.savefig("network.png")
    except Exception, e:
        print e
        pass

