import subprocess
from subprocess import Popen, PIPE


while True:
    i = 0
    try:
        print("Starting instance")
        p = Popen(['./env/bin/python3', './main.py'],
                  stdin=PIPE,
                  stdout=open("/home/faruk/Desktop/test-out%d.txt" % i, "w+"),
                  stderr=PIPE)
        output, err = p.communicate(b"input data that is passed to subprocess' stdin")
        i += 1
    except KeyboardInterrupt:
        break