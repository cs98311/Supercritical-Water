#!/usr/bin/env python3

from os.path import exists
from os.path import join
from subprocess import run, CalledProcessError
from sys import exit
from re import search

# Constants
DISTANCE_CUTOFF_NM = 0.22
ANGLE_CUTOFF_DEG = 35
START_TIMESTEP = 0
END_TIMESTEP = 3
XTCTRR_FOLDER = "mds"
XTC_FILE = join(XTCTRR_FOLDER, "prod2.xtc")
TRR_FILE = join(XTCTRR_FOLDER, "prod2.trr")
GRO_FILE = join(XTCTRR_FOLDER, "prod2.gro")
RESULTS_FOLDER = "results"
SYSTEM_INFO_FILE = join(RESULTS_FOLDER, "systemInfo.txt")
SRC_FOLDER = "src"
GLOBALS_FILE = join(SRC_FOLDER, "globals.h")
EDGELIST_SOURCE = join(SRC_FOLDER, "edgeList.c")
EDGELIST_BINARY = join(SRC_FOLDER, "edgeList.out")


def run_command(command, error_message):
    try:
        run(command, shell=True, check=True)
    except CalledProcessError as e:
        print(f"Error: {error_message}: {e.returncode}\n{e.stderr}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def convert_trr_to_xtc():
    if not exists(XTC_FILE):
        if exists(TRR_FILE):
            run_command(
                f"gmx trjconv -f {TRR_FILE} -o {XTC_FILE} > /dev/null 2>&1",
                "Conversion error",
            )
            print(f"Conversion successful: {TRR_FILE} converted to {XTC_FILE}")
        else:
            print("Error: No .xtc or .trr file found.")
            exit(1)


def check_gro_file():
    if not exists(GRO_FILE):
        print("Error: No .gro file found.")
        exit(1)


def clean_folders():
    try:
        command = f"find . -type f \( -name '*.txt' -o -name '*.csv' -o -name '*.out' -o -name '*#' \) -delete"
        run(command, shell=True, check=True)
    except FileNotFoundError as e:
        print(f"Error deleting files: {e}\nPlease check file paths and permissions.")
    except PermissionError as e:
        print(
            f"Error: Insufficient permissions to delete files: {e}\nPlease adjust permissions or run with appropriate privileges."
        )
    except CalledProcessError as e:
        print(f"Error: Error deleting files: {e.returncode}\n{e.stderr}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def get_system_info():
    numH2O = 0
    box_length = 0
    with open(GRO_FILE, "r") as f:
        box_length_pattern = r"^\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)$"
        for line in f:
            if search(r"HW1", line):
                numH2O += 1
            match = search(box_length_pattern, line)
            if match:
                box_length = float(match.group(1))
                break
    with open(SYSTEM_INFO_FILE, "w") as f:
        print(box_length, numH2O, sep="\n", file=f)
    return numH2O, box_length


def update_globals_file(numH2O, box_length):
    with open(GLOBALS_FILE, "w") as f:
        print(f"#define NUM_H2O {numH2O}", file=f)
        print(f"#define BOX_LENGTH {box_length}", file=f)
        print(f"#define DISTANCE_CUTOFF {DISTANCE_CUTOFF_NM}", file=f)
        print(f"#define ANGLE_CUTOFF {ANGLE_CUTOFF_DEG}", file=f)


def compile_edgelist_source():
    run_command(f"gcc {EDGELIST_SOURCE} -o {EDGELIST_BINARY} -lm", "Compilation error")


def extract_coordinates(i):
    run_command(
        f"python3 {join(SRC_FOLDER, 'coordinates.py')} {i} {XTC_FILE} {GRO_FILE}",
        f"Error extracting coordinates for timestep {i}",
    )


def generate_edge_list(i):
    run_command(f"./{EDGELIST_BINARY}", f"Error generating edge list for timestep {i}")


def perform_network_analysis():
    run_command(
        f"python3 {join(SRC_FOLDER, 'network.py')}",
        "Error during network analysis",
    )


def remove_unnecessary_files():
    run_command(f"rm {join(SRC_FOLDER, '*.out')}", "Error removing unnecessary files")


# Main script
convert_trr_to_xtc()
check_gro_file()
clean_folders()

# Get number of water and box length
numH2O, box_length = get_system_info()

# Update globals.h
update_globals_file(numH2O, box_length)

# Compile edgeList.c
compile_edgelist_source()

# Iterations begin
for i in range(START_TIMESTEP, END_TIMESTEP):
    # Extract coordinates
    extract_coordinates(i)

    # Generate edge list
    generate_edge_list(i)

    # Perform network analysis
    perform_network_analysis()

# Remove unnecessary files
remove_unnecessary_files()
