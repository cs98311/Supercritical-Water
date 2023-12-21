#!/usr/bin/env python3

import sys
import os
from subprocess import run, CalledProcessError
from re import search


def extract_coordinates(
    timestep, xtc_file, gro_file, results_dir="results/coordinates"
):
    h1_coordinates_file = os.path.join(results_dir, "h1.txt")
    h2_coordinates_file = os.path.join(results_dir, "h2.txt")
    ow_coordinates_file = os.path.join(results_dir, "ow.txt")
    all_gro_file = os.path.join(results_dir, "all.gro")

    try:
        # Create results directory if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)

        # Print progress of iterations
        print(f"Timestep: {timestep}")

        # Generate .gro file with input=0 at each iteration
        generate_gro_command = [
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
            all_gro_file,
        ]
        run(
            generate_gro_command,
            input="0\n",
            capture_output=True,
            text=True,
            check=True,
        )

        # Extract coordinates for each element from the .gro files
        with open(all_gro_file, "r") as fCood, open(
            h1_coordinates_file, "w"
        ) as fH1, open(h2_coordinates_file, "w") as fH2, open(
            ow_coordinates_file, "w"
        ) as fOW:
            for line in fCood:
                tokens = line.split()
                if len(tokens) < 4:
                    continue
                if tokens[1].startswith("HW"):
                    print(" ".join(tokens[3:6]), file=fH1 if "HW1" in line else fH2)
                elif tokens[1] == "OW":
                    print(" ".join(tokens[3:6]), file=fOW)

    except CalledProcessError as e:
        print(f"Error during subprocess in coordinates.py: {e}")
        raise
    except FileNotFoundError as e:
        print(f"Error in coordinates.py: {e}. Make sure the paths are correct.")
        raise
    except IndexError as e:
        print(f"An index error occurred in coordinates.py: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred in coordinates.py: {e}")
        raise
    finally:
        # Remove .gro file to avoid pileup
        os.remove(all_gro_file)


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
