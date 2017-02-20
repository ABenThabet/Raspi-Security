import subprocess, signal
import sys
import os

p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
out, err = p.communicate()
for line in out.splitlines():
	if sys.argv[1] in line:
		pid = int(line.split(None, 1)[0])
		os.kill(pid, signal.SIGKILL)