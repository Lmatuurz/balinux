#!/usr/bin/env python3
import sqlite3
from os import path
from time import time
from json import dumps


def load_data():
    def group(iterable):
        ret = {}
        for i in iterable:
            if i[1] not in ret:
                ret[i[1]] = []
            ret[i[1]].append(i)
        return ret

    def get(table):
        return db.execute("SELECT * FROM \"" + table + "\" WHERE (`time` > ?)", (ts - 60,)).fetchall()

    def avgload(arr):
        ret = [0, 0, 0]
        for i in arr:
            ret[0] += i[1]
            ret[1] += i[2]
            ret[2] += i[3]
        # ret = [arr[0][0], arr[-1][0], ret]
        # ret = [ret[0] / len(arr), ret[1] / len(arr), ret[2] / len(arr)]
        ret[0] /= len(arr)
        ret[1] /= len(arr)
        ret[2] /= len(arr)
        return ret

    def avgdl(arr):
        ret = {}
        for i in arr:
            if i[1] not in ret:
                ret[i[1]] = [0, 0, 0, 0, 0]
            ret[i[1]] = [x + y for x, y in zip(ret[i[1]], i[2:])]
        return [[x] + y for x, y in ret.items()]

    def format_talkers(arr):
        # ret = {'bytes': 0, 'by-proto': {}, 'sessions': {}}
        ret = {}
        for i in arr:
            if i[1] not in ret:
                ret[i[1]] = {'bytes': 0, 'by-proto': {}, 'sessions': {}}
            ret[i[1]]['bytes'] += i[5]
            if i[4] not in ret[i[1]]['by-proto']:
                ret[i[1]]['by-proto'][i[4]] = []
            ret[i[1]]['by-proto'][i[4]].append(i)
            if i[2] in ret[i[1]]['sessions']:
                if i[3] not in ret[i[1]]['sessions'][i[2]]:
                    ret[i[1]]['sessions'][i[2]][i[3]] = []
                ret[i[1]]['sessions'][i[2]][i[3]].append(i)
            elif i[3] in ret[i[1]]['sessions']:
                if i[2] not in ret[i[1]]['sessions'][i[3]]:
                    ret[i[1]]['sessions'][i[3]][i[2]] = []
                ret[i[1]]['sessions'][i[3]][i[2]].append(i)
            else:
                ret[i[1]]['sessions'][i[2]] = {i[3]: [i]}
        return ret

    def format_sockets(arr):
        last_time = max(arr, key=lambda x: x[0])[0]
        ret = {'listen': {}, 'states': {},
               'max': last_time
               }
        for i in arr:
            if i[0] < last_time:
                continue
            if i[6] == 'LISTEN':
                if i[1] not in ret['listen']:
                    ret['listen'][i[1]] = []
                ret['listen'][i[1]].append(i)
            if i[6] not in ret['states']:
                ret['states'][i[6]] = 0
            ret['states'][i[6]] += 1
        return ret

    def format_cpu(arr):
        ret = [0, 0, 0, 0, 0, 0]
        for i in arr:
            ret = [x + y for x, y in zip(ret, i[1:])]
        return [x / len(arr) for x in ret]

    def format_net(arr):
        ret = {}
        for i in arr:
            if i[1] not in ret:
                ret[i[1]] = [0, 0, 0, 0, 0, 0, 0]
            if i[0] > ret[i[1]][0]:
                ret[i[1]] = [i[0]] + list(i[2:])
        # return {x: [a / y[0] for a in y[1:]] for x, y in ret.items()}
        return {x: y[1:] for x, y in ret.items()}

    def format_df(arr):
        ret = {}
        for i in arr:
            if i[-1] not in ret:
                ret[i[-1]] = [0, 0, 0, 0, 0, 0]
            ret[i[-1]] = [ret[i[-1]][0] + 1] + \
                [x + y for x, y in zip(ret[i[-1]][1:-1], i[2:-1])] + [i[1]]
        return {x: [y[-1]] + [a / y[0] for a in y[1:-1]] for x, y in ret.items()}

        # ts = int(time())
    ts = 1495571197
    dirname = path.dirname(path.realpath(__file__))
    db_filename = path.join(dirname, 'sqlite3.db')
    db = sqlite3.connect(db_filename)

    loadavg = get("loadavg")
    iostat = get("iostat")
    talkers = get("talkers")
    cpu = get("cpu")
    net = get("net")
    fs = get("fs")
    tables = {
        "avg Load average": avgload(loadavg),
        "avg Load average(30s)": avgload(loadavg[len(loadavg) // 2:]),
        "avg Disk loadage": avgdl(iostat),
        "avg Disk loadage(30s)": avgdl(iostat[len(iostat) // 2:]),
        # "Network usage": group(get("net")),
        "Talkers": format_talkers(talkers),
        "Open sockets": format_sockets(get("opened_sockets")),
        "avg CPU": format_cpu(cpu),
        "avg CPU(30s)": format_cpu(cpu[len(cpu) // 2:]),
        "Network usage": format_net(net),
        "Network usage(30s)": format_net(net[len(net) // 2:]),
        "FileSystem data": format_df(fs)
    }

    return tables


def application(environ, start_response):
    status = '200 OK'
    try:
        result = dumps(load_data(), indent=2)
    except Exception as e:
        result = str(e)
    # output = b'<html><body style="color:red">Deer World!<br/>{}</body></html>'.format(
        # load_data())
       # '<pre>' +  result + '</pre>')
    output = b'{}'.format(
        result)

    response_headers = [('Content-type', 'application/json'),
                        # response_headers=[('Content-type', 'text/html'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]

# from paste.exceptions.errormiddleware import ErrorMiddleware
# application = ErrorMiddleware(application, debug=True)
