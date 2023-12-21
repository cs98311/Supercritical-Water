#! /usr/bin/env python3

from subprocess import run, CalledProcessError
from sys import exit
from os.path import exists

# set cutoffs
distance_cutoff_nm = 0.22
angle_cutoff_deg = 35

# Timestep limits (ex : 0 to N+1)
start = 0
end = 3

# mds files
xtc_file = "mds/prod2.xtc"
trr_file = "mds/prod2.trr"
gro_file = "mds/prod2.gro"

if not exists(xtc_file):
    if exists(trr_file):
        try:
            run(
                f"gmx trjconv -f {trr_file} -o {xtc_file} > /dev/null 2>&1",
                shell=True,
                check=True,
            )
            print(f"Conversion successful: {trr_file} converted to {xtc_file}")
        except CalledProcessError as e:
            print(f"Error during conversion: {e}")
            exit(1)
    else:
        print("Error: No .xtc or .trr file found.")
        exit(1)

if not exists(gro_file):
    print("Error: No .gro file found.")
    exit(1)

# Empty the folders
run("find . -type f \( -name '*.txt' -o -name '*.csv' \) -delete", shell=True)

# Get number of water and box length
numH2O = 0
with open(f"{gro_file}", "r") as f:
    for line in f:
        if line[12:15] == "HW1":
            numH2O += 1
        elif line[4] == ".":
            box_length = line[3:10]

with open("results/systemInfo.txt", "w") as f:
    print(box_length, numH2O, sep="\n", file=f)

with open("src/globals.h", "w") as f:
    print("#define NUM_H2O " + str(numH2O), file=f)
    print("#define BOX_LENGTH " + str(box_length), file=f)
    print("#define DISTANCE_CUTOFF " + str(distance_cutoff_nm), file=f)
    print("#define ANGLE_CUTOFF " + str(angle_cutoff_deg), file=f)


run("gcc src/edgeList.c -o src/edgeList.out -lm", shell=True).check_returncode()

# Iterations begin
for i in range(start, end):
    # Extrct coordinates

    run(
        f"python3 src/coordinates.py {xtc_file} {gro_file}",
        shell=True,
        input=f"{i}",
        text=True,
    ).check_returncode()

    # Generate edge list
    run(
        "./src/edgeList.out", input=f"{i}", capture_output=True, text=True
    ).check_returncode()

    # Perform network analysis
    run("python3 src/network.py", shell=True).check_returncode()


# Remove unnecessary file
run("rm src/*.out", shell=True)
