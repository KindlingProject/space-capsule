# -*- coding: utf-8 -*-

import fcntl
import json
import os
import select
import signal
import subprocess
import sys
import time

import psutil

args = ""


class Daemon(object):
    def __init__(self, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.ver = "0.1.23"  # version
        self.waitToHardKill = 3
        self.processName = os.path.basename(sys.argv[0])
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def _makeDaemon(self):
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent.
                sys.exit(0)
        except OSError as e:
            m = f"Fork #1 failed: {e}"
            print(m)
            sys.exit(1)

        # Decouple from the parent environment.
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork.
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent.
                sys.exit(0)
        except OSError as e:
            m = f"Fork #2 failed: {e}"
            print(m)
            sys.exit(1)

        m = "The daemon process is going to background."
        print(m)

        # Redirect standard file descriptors.
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'w+')
        se = open(self.stderr, 'w+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def _getProces(self):
        procs = []

        for p in psutil.process_iter():
            if self.processName in [part.split('/')[-1] for part in p.cmdline()]:
                # Skip  the current process
                if p.pid != os.getpid():
                    procs.append(p)

        return procs

    def start(self):
        # Handle signals
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGHUP, self.stop)

        # Check if the daemon is already running.
        procs = self._getProces()

        if procs:
            pids = ",".join([str(p.pid) for p in procs])
            status = {
                "status": "started",
                "pid": pids
            }
            print(json.dumps(status))
            sys.exit(1)

        # Daemonize the main process
        self._makeDaemon()
        # Start a infinitive loop that periodically runs run() method
        self.run()

    def status(self):
        procs = self._getProces()

        if procs:
            pids = ",".join([str(p.pid) for p in procs])
            status = {
                'status': "started",
                'pid': pids
            }
        else:
            status = {
                'status': "stopped",
            }
        print(json.dumps(status))

    def stop(self):
        procs = self._getProces()

        def on_terminate(process):
            status = {
                'status': "stopped",
                'pid': process.pid
            }
            print(json.dumps(status))

        if procs:
            for p in procs:
                p.terminate()

            gone, alive = psutil.wait_procs(procs, timeout=self.waitToHardKill, callback=on_terminate)

            for p in alive:
                p.kill()
        else:
            status = {
                'status': "not_find",
            }
            print(json.dumps(status))

    # this method you have to override
    def run(self):
        pass


class Toda(Daemon):
    def __init__(self, cmd, stdout='/dev/null', stderr='/dev/null'):
        Daemon.__init__(self, stdout=stdout, stderr=stderr)
        self.cmd = cmd
        self.args = ""

    def start(self, pid, path, args):
        self.cmd = self.cmd.format(pid, pid, path)
        self.args = args
        Daemon.start(self)
        # self.cmd += "pid"

    def run(self):
        global process
        print(self.cmd)
        process = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        flags = fcntl.fcntl(process.stdout, fcntl.F_GETFL)
        fcntl.fcntl(process.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self.send(self.args)
        status = self.recv()
        print(status)
        signal.signal(signal.SIGTERM, signal_handler)
        process.wait()

    def send(self, data, tail='\n'):
        b = data + tail
        process.stdin.write(bytes(b, encoding='utf-8'))
        process.stdin.flush()

    def recv(self, t=.1, stderr=0):
        r = ''
        pr = process.stdout
        if stderr:
            pr = process.stdout
        while True:
            if not select.select([pr], [], [], 0)[0]:
                time.sleep(t)
                continue
            r = pr.read()
            return r.rstrip()
        return r.rstrip()


def signal_handler(signal, frame):
    process.kill()
    sys.exit(0)


if __name__ == "__main__":
    process = None
    daemon = Toda(
        "/opt/nsexec/release/nsexec -l -p /proc/{}/ns/pid -m /proc/{}/ns/mnt --library-path /opt/nsexec/release/libnsenter.so -- /opt/toda/release/toda --path {} --verbose info",
        "/stdout", "/stderr")
    # daemon = Toda("/home/nejan/space-capsule/simpledaemon/{}", "args", "/stdout", "/stderr")
    usageMessage = f"Usage: {sys.argv[0]} (start |stop|status)"

    choice = sys.argv[1]

    if choice == "start":
        if len(sys.argv) == 5:
            choice = sys.argv[1]
            pid = sys.argv[2]
            path = sys.argv[3]
            args = sys.argv[4]
            daemon.start(pid, path, args)
        else:
            print(f"Usage: {sys.argv[0]} start $pid $path $args")
    elif choice == "stop":
        daemon.stop()
    elif choice == "status":
        daemon.status()
    else:
        print("Unknown command.")
        print(usageMessage)
        sys.exit(1)
