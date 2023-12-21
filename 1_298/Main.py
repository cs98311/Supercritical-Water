#!/usr/bin/env python3

from subprocess import run, CalledProcessError
from sys import exit
from os.path import exists
from re import search

# Set cutoffs
distance_cutoff_nm = 0.22
angle_cutoff_deg = 35

# Timestep limits (e.g., 0 to N+1)
start_time = 0
end_time = 3

# MDS files
xtc_file = "mds/prod2.xtc"
trr_file = "mds/prod2.trr"
gro_file = "mds/prod2.gro"


# Function to handle subprocess calls with error checking
def run_command(command, error_message):
    try:
        run(command, shell=True, check=True)
    except CalledProcessError as e:
        print(f"Error: {error_message}: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Check and convert trr_file to xtc_file if necessary
if not exists(xtc_file):
    if exists(trr_file):
        run_command(
            f"gmx trjconv -f {trr_file} -o {xtc_file} > /dev/null 2>&1",
            "Conversion error",
        )
        print(f"Conversion successful: {trr_file} converted to {xtc_file}")
    else:
        print("Error: No .xtc or .trr file found.")
        exit(1)

# Check for the existence of gro_file
if not exists(gro_file):
    print("Error: No .gro file found.")
    exit(1)

# Empty the folders
run_command(
    "find . -type f \( -name '*.txt' -o -name '*.csv' \) -delete",
    "Error deleting files",
)

# Get number of water and box length
numH2O = 0
box_length = 0

with open(f"{gro_file}", "r") as f:
    for line in f:
        if search(r"HW1", line):
            numH2O += 1
        elif search(r".", line[:10]):
            box_length = line[3:10]

with open("results/systemInfo.txt", "w") as f:
    print(box_length, numH2O, sep="\n", file=f)

with open("src/globals.h", "w") as f:
    print("#define NUM_H2O " + str(numH2O), file=f)
    print("#define BOX_LENGTH " + str(box_length), file=f)
    print("#define DISTANCE_CUTOFF " + str(distance_cutoff_nm), file=f)
    print("#define ANGLE_CUTOFF " + str(angle_cutoff_deg), file=f)

run_command("gcc src/edgeList.c -o src/edgeList.out -lm", "Compilation error")

# Iterations begin
for timestep in range(start_time, end_time):
    # Extract coordinates
    run_command(
        f"python3 src/coordinates.py {timestep} {xtc_file} {gro_file}",
        f"Error extracting coordinates for timestep {timestep}",
    )

    # Generate edge list
    run_command(
        "./src/edgeList.out", f"Error generating edge list for timestep {timestep}"
    )

    # Perform network analysis
    run_command(
        "python3 src/network.py",
        f"Error during network analysis for timestep {timestep}",
    )

# Remove unnecessary files
run_command("rm src/*.out", "Error removing unnecessary files")
