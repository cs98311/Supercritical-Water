#!/usr/bin/env python3

from subprocess import run, CalledProcessError
import sys
from re import search


def extract_coordinates(timestep, xtc_file, gro_file):
    h1_coordinates_file = "results/coordinates/h1.txt"
    h2_coordinates_file = "results/coordinates/h2.txt"
    ow_coordinates_file = "results/coordinates/ow.txt"

    try:
        # Open files for coordinates at each iteration
        with open(h1_coordinates_file, "w") as fH1, open(
            h2_coordinates_file, "w"
        ) as fH2, open(ow_coordinates_file, "w") as fOW:
            # Print progress of iterations
            print(f"Timestep: {timestep}")

            # Generate .gro file with input=0 at each iteration
            run(
                [
                    "gmx",
                    "trjconv",
                    "-f",
                    xtc_file,
                    "-s",
                    gro_file,
                    "-b",
                    str(timestep),
                    "-e",
                    str(timestep),
                    "-o",
                    "results/all.gro",
                ],
                input="0\n",
                capture_output=True,
                text=True,
                check=True,
            )

            # Extract coordinates for each element from the .gro files
            with open("results/all.gro", "r") as fCood:
                for line in fCood:
                    if search(r"HW[12]", line):
                        print(line[23:44], file=fH1 if "HW1" in line else fH2)
                    elif search(r"OW", line):
                        print(line[23:44], file=fOW)

            # Remove .gro file to avoid pileup
            run(["rm", "results/all.gro"], check=True)

    except CalledProcessError as e:
        print(f"Error during subprocess: {e}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python3 coordinates.py timestep mds/filename.xtc mds/filename.gro"
        )
        sys.exit(1)

    try:
        timestep = int(sys.argv[1])
        xtc_file = sys.argv[2]
        gro_file = sys.argv[3]

        extract_coordinates(timestep, xtc_file, gro_file)

    except ValueError:
        print("Error: Timestep must be an integer.")
        sys.exit(1)


if __name__ == "__main__":
    main()
