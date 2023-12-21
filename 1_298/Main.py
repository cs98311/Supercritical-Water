#! /usr/bin/env python3

import subprocess
import sys
from os.path import exists

# mds files
xtc_file = "mds/prod2.xtc"
trr_file = "mds/prod2.trr"
gro_file = "mds/prod2.gro"

if not exists(xtc_file):
    if exists(trr_file):
        try:
            subprocess.run(
                f"gmx trjconv -f {trr_file} -o {xtc_file} > /dev/null 2>&1",
                shell=True,
                check=True,
            )
            print(f"Conversion successful: {trr_file} converted to {xtc_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e}")
            sys.exit(1)
    else:
        print("Error: No .xtc or .trr file found.")
        sys.exit(1)

if not exists(gro_file):
    print("Error: No .gro file found.")
    sys.exit(1)

# Empty the folders
subprocess.run(
    "find . -type f \( -name '*.txt' -o -name '*.csv' \) -delete", shell=True
)

# Get number of water and box length
numW = 0
box_length = 0
with open(f"{gro_file}", "r") as f:
    for line in f:
        if line[12:15] == "HW1":
            numW += 1
        elif line[4] == ".":
            box_length = line[3:10]

with open("results/systemInfo.txt", "w") as f:
    print(box_length, numW, sep="\n", file=f)

with open("src/size.h", "w") as f:
    print("#define NUM_W " + str(numW), file=f)

# Iteration limits
start = 0
end = 3

subprocess.run("gcc src/edgeList.c -o src/edgeList.out -lm", shell=True)

# Iterations begin
for i in range(start, end):
    subprocess.run(
        f"python3 src/coordinates.py {xtc_file} {gro_file}",
        shell=True,
        input="{}".format(i),
        text=True,
    )
    subprocess.run(
        "./src/edgeList.out", input="{}".format(i), capture_output=True, text=True
    )
    subprocess.run("python3 src/network.py", shell=True)

# Remove unnecessary file
subprocess.run("rm src/*.out", shell=True)
