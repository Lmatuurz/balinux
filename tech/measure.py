#!/usr/bin/env python3
from subprocess import Popen, PIPE
from os import path
import sys
import sqlite3
from time import time, sleep

dirname = path.dirname(path.realpath(__file__))
db_filename = path.join(dirname, 'sqlite3.db')
db = sqlite3.connect(db_filename)

started = time()


def run(cmd):
    proc = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
    proc.wait()
    if proc.returncode:
        raise RuntimeError(
            'Process returned non-null:\n{}'.format(proc.communicate()))
    return proc.stdout.read().decode('utf-8')


def read(filename):
    with open(filename, 'r') as f:
        ret = f.read()
    return ret


def measure(mtime):
    procnet = read('/proc/net/dev')
    uptime = run('uptime')
    iostat = run('iostat')
    netstat = run(['netstat', '-apetu'])
    df = run('df')

    net = [[x[0].strip(':'), x[1], x[2], x[3], x[9], x[10], x[11]]
           for x in [y.split() for y in procnet.split('\n')[2:] if y]]
    # print(net)

    loadavg = [x.strip(',\n') for x in uptime.split(' ')[-3:]]
    # print(loadavg)
    disks = [x.split() for x in iostat.split('\n')[6:]]
    # print(disks)
    opened_sockets = [
        [
            x[0], x[1], x[2], x[3], x[4], x[5],
            # systemd-network opened_sockets do not contain this info
            x[8] if len(x) > 8 else '', x[6] if len(x) > 8 else ''
        ]
        for x in [y.split() for y in netstat.split('\n')[2:] if y]
    ]
    # print("\n".join([str(x) for x in opened_sockets]))
    cpu = iostat.split('\n')[3].split()
    # print(cpu)
    mountpoints = [
        [x[0], int(x[1]), int(x[2]), int(x[3]), int(x[4][:-1]), x[5]]
        for x in [y.split() for y in df.split('\n')[1:] if y]
        if not(x[5].startswith('/sys') or x[5].startswith('/proc') or x[5].startswith('/dev'))
    ]
    # print(mountpoints)
    return save(loadavg, disks, net, opened_sockets, cpu, mountpoints, mtime=mtime)


def save(loadavg, disks, net, opened_sockets, cpu, mountpoints, mtime):
    db.execute(
        """INSERT INTO "loadavg" (`time`, `1`, `5`, `15`) VALUES (?, ?, ?, ?)""",
        tuple([mtime] + loadavg)
    )
    db.executemany(
        """INSERT INTO "iostat" (`time`, `device`, `tps`, `r/s`, `w/s`, `r`, `w`) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [tuple([mtime] + x) for x in disks if x]
    )
    db.executemany(
        """INSERT INTO "net" (`time`, `interface`, `rb`, `rp`, `re`, `tb`, `tp`, `te`) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [tuple([mtime] + x) for x in net if x]
    )
    db.executemany(
        """INSERT INTO "opened_sockets" (`time`, `proto`, `recv-q`, `send-q`, `local`, `foreign`, `state`, `process`, `user`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [tuple([mtime] + x) for x in opened_sockets if x]
    )
    db.execute(
        """INSERT INTO "cpu" (`time`, `user`, `nice`, `system`, `iowait`, `steal`, `idle`) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        tuple([mtime] + cpu)
    )
    db.executemany(
        """INSERT INTO "fs" (`time`,`fs`,`blocks`,`used`,`available`,`use%`,`mountpoint`) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [tuple([mtime] + x) for x in mountpoints if x]
    )

    db.commit()
    return True


def main():
    # loadavg, disks, net, opened_sockets, cpu, mountpoints = measure()
    # 60 times a minute == every second
    if 'once' in sys.argv[1:]:
        return measure(int(time()))
    while True:
        time_start = time()
        print(measure(int(time_start)))
        sleep(time_start + 1 - time())


if __name__ == '__main__':
    main()
