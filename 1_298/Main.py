#! /usr/bin/env python3

import subprocess
from os.path import exists


# Emptying the folders
subprocess.run("rm Coordinates/*", shell=True)
subprocess.run("rm SysInfo.txt", shell=True)
subprocess.run("rm Plots/*", shell=True)
subprocess.run("rm Water/*", shell=True)


### .TRR TO .XTC ###
if exists("MDSfiles/prod2.xtc") == False:
    subprocess.run(
        "gmx trjconv -f MDSfiles/prod2.trr -o MDSfiles/prod2.xtc", shell=True
    )


### ITERATION LIMITS ###

start = 0
end = 5

n = end - start


####################
# ITERATIONS BEGIN #
####################

subprocess.run("gcc Codes/EdgeListDA.c -o Codes/EdgeListDA -lm", shell=True)

for i in range(start, end):
    subprocess.run(
        "python3 Codes/Coordinates.py", shell=True, input="{}".format(i), text=True
    )

    subprocess.run(
        "./Codes/EdgeListDA", input="{}".format(i), capture_output=True, text=True
    )

    # subprocess.run("python3 Codes/CompiledHBdata.py",shell=True)

    subprocess.run("python3 Codes/Network.py", shell=True)


#######################
# ITERATIONS END HERE #
#######################

# subprocess.run("python3 Codes/RTadder.py",shell=True)

# subprocess.run("python3 Codes/TableCreateLi.py",shell=True)


### 3D PLOTTING ###


def Plot():
    # Print oxygen to oxygen H-bond vectors file ([Starting Point],[Direction])
    subprocess.run("gcc Codes/HBvectors.c -o Codes/HBvectors -lm", shell=True)
    subprocess.run("./Codes/HBvectors")

    # Save the 3D plots as images (.svg, .eps, .jpg)
    subprocess.run("python3 Codes/3DplotsLi.py", shell=True)

    subprocess.run("rm Codes/HBvectors", shell=True)


# Plot()


### REMOVE UNNECESSARY FILES ###
subprocess.run("rm Codes/EdgeListDA", shell=True)
