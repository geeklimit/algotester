#!/usr/bin/python

#
# Recursive Tester
#	Created by Justin McCormick
#	(minivan)
#

import subprocess
from datetime import datetime
import re
import sys
import signal

# Changable Variables
algoname = "mvscalp"
variables = {
    'time' : [1,5,10],
    'short' : [5,6,7,8,9,10,11,12,13,14,15],
    'long' : [20,21,22,23,24,25,26,27,28,29,30,31,32,33,34],
    'stop' : [0.96,0.97,0.98,0.99],
    'take' : [1.01,1.02,1.03,1.04,1.05],
}

# Stores Output
results = {}

# Needed for Recursiveness
keys = variables.keys()
vals = variables.values()

# File Handling
filename = "results.txt"

def sig_handler(signal, frame):
    print('[-] Exiting due to Ctrl-C')
    sys.exit(0)

def call_process(strtorun):
    processtorun = 'node gekko.js -b -c config.js'
    result = subprocess.check_output(processtorun.split())
    # Search for Percentage & Win/Loss
    m = re.search('.*simulated profit\:.*\((.*)\%\)', result)
    if m: percent = m.group(1)
    # Sharpe Ratio
    m = re.search('.*sharpe ratio:[\s]*(.*)', result)
    if m: ratio = m.group(1)

    # Store into table as Percentage Key
    try:
        results[percent] = '{}'.format(percent)
        line = "\t" + str(percent)
        print(line)

        fh = open("results.txt","a")
        fh.write(strtorun + line + "\n")
        fh.close()
    except:
        print('Variable Not Defined')

def recurse_combos(strtorun, k_ind, v_ind):
    for item in vals[k_ind]:
        # Replace Key=Value if there is already one
        pat = re.compile('{}: '.format(keys[k_ind]))
        if pat.search(strtorun):
            strtorun = re.sub('({}: [^\s]+)'.format(keys[k_ind]), '{}: {},'.format(keys[k_ind], item), strtorun)
        else:
            strtorun = strtorun + ' {}: {},'.format(keys[k_ind], item)

        if k_ind < (len(keys) - 1):
            recurse_combos(strtorun, k_ind + 1, 0) # Next Item In Variables
        else:
            # Format Process to Run String
            processtorun = 'node gekko.js -b -c config.js'
            linetoreplace = ('config.%s = { ' % algoname) + strtorun + ' };'
            print(linetoreplace)
            with open('configbk.js', 'r') as input_file, open('config.js', 'w') as output_file:
                for line in input_file:
                    if ('config.%s' % algoname) in line.strip():
                        output_file.write(linetoreplace)
                    else:
                        output_file.write(line)

            # Run Process Here
            call_process(linetoreplace)

def sort_results():
    print("\n[+] Printing Sorted Results\n")
    keylist = results.keys()
    keylist.sort()

    for key in keylist:
        line = '{}'.format(results[key])
        print(line)
    print("\n[-] Wrote Results to results.txt")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sig_handler)
    fh = open(filename,"w")
    fh.close()

    print('[+] Beginning Algorithm Tester: {}'.format(str(datetime.now())))
    recurse_combos('', 0, 0)
    sort_results()
    print('[+] Ended Algorithm Tester: {}'.format(str(datetime.now())))
