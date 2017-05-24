#!/usr/bin/env python3

from subprocess import Popen, PIPE
from measure import db_filename, read
from time import time
from threading import Thread
import sqlite3
procnet = read('/proc/net/dev')
net = [x.split()[0].strip(':')
       for x in procnet.split('\n')[2:] if x]
# print(net)

tcpdump = {
    x: Popen(['sudo', 'tcpdump', '-vv', '-l', '-i', x], stdout=PIPE)
    for x in net if x
}


def inserter(key):
    def inserter_target():
        thread_conn = sqlite3.connect(db_filename)
        tmp = {}
        packet_start = False

        def save(tmp):
            print('saving {}'.format(tmp))
            if tmp:
                thread_conn.execute(
                    """
                    INSERT INTO "talkers"
                    (`time`, `interface`, `src`, `dst`, `proto`, `bytes`)
                    VALUES (?,?,?,?,?,?)
                    """, (int(time()), key, tmp['src'], tmp['dst'], tmp['proto'], tmp['bytes']))
                thread_conn.commit()
                del tmp
            return {}

        for line in iter(tcpdump[key].stdout.readline, b''):
            line = str(line)
            if not line:
                continue
            # print(line)
            spl = [str(x).strip().strip('()\\n\',')
                   for x in line.split() + ['']]
            print(spl)
            if not packet_start and not line.startswith('    '):  # start of packet
                tmp = save(tmp)
                if not('proto' in line and 'length' in line):
                    print('skipping')
                    print(line)
                    continue
                tmp = {
                    'interface': key,
                    'proto': spl[spl.index('proto') + 1],
                    'bytes': int(spl[spl.index('length') + 1].strip().strip('\\n)'))
                }
                packet_start = True
            elif packet_start:
                tmp['src'] = spl[spl.index('>') - 1]
                tmp['dst'] = spl[spl.index('>') + 1]
                packet_start = False
    return inserter_target

threads = [Thread(target=inserter(x), daemon=True) for x in tcpdump.keys()]
for thread in threads:
    thread.start()

print([x.join() for x in threads])
print([x.communicate for x in threads])
print("exiting o_O")
