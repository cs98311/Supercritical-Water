#!/usr/bin/env python3

from subprocess import run, CalledProcessError
import sys
from re import search


def main(timestep, xtc_file, gro_file):
    try:
        h1_coordinates_file = "results/coordinates/h1.txt"
        h2_coordinates_file = "results/coordinates/h2.txt"
        ow_coordinates_file = "results/coordinates/ow.txt"

        # Open files for coordinates at each iteration
        fH1 = open(h1_coordinates_file, "w")
        fH2 = open(h2_coordinates_file, "w")
        fOW = open(ow_coordinates_file, "w")

        # Print progress of iterations
        print(f"Timestep: {timestep}")

        # Generate .gro file with input=0 at each iteration
        run(
            f"gmx trjconv -f {xtc_file} -s {gro_file} -b {timestep} -e {timestep} -o results/all.gro",
            shell=True,
            input="0\n",
            capture_output=True,
            text=True,
            check=True,
        )

        # Extract coordinates for each element from the .gro files
        with open("results/all.gro", "r") as fCood:
            for line in fCood:
                if search(r"HW1", line):
                    print(line[23:44], file=fH1)
                elif search(r"HW2", line):
                    print(line[23:44], file=fH2)
                elif search(r"OW", line):
                    print(line[23:44], file=fOW)

        # Remove .gro file to avoid pileup
        run("rm results/all.gro", shell=True, check=True)

    except CalledProcessError as e:
        print(f"Error during subprocess: {e}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        fH1.close()
        fH2.close()
        fOW.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python3 coordinates.py timestep mds/filename.xtc mds/filename.gro"
        )
        sys.exit(1)

    timestep = int(sys.argv[1])
    xtc_file = sys.argv[2]
    gro_file = sys.argv[3]

    main(timestep, xtc_file, gro_file)
