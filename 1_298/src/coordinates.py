#!/usr/bin/env python3

from subprocess import run, CalledProcessError
import sys


def main(xtc_file, gro_file):
    try:
        # Open files for coordinates at each iteration
        fH1 = open("results/coordinates/h1.txt", "w")
        fH2 = open("results/coordinates/h2.txt", "w")
        fOW = open("results/coordinates/ow.txt", "w")

        # Takes input the iteration number from the main file
        # Print progress of iterations
        num = input("Timestep: ")
        print(f"{num}")

        # Generate .gro file at each iteration
        run(
            f"gmx trjconv -f {xtc_file} -s {gro_file} -b {num} -e {num} -o results/all.gro",
            shell=True,
            input="0\n",
            capture_output=True,
            text=True,
            check=True,  # Add check=True for error handling
        )

        # Generate coordinate files for each element from the .gro files
        with open("results/all.gro", "r") as fCood:
            for line in fCood:
                if line[12:15] == "HW1":
                    print(line[23:44], file=fH1)
                elif line[12:15] == "HW2":
                    print(line[23:44], file=fH2)
                elif line[13:15] == "OW":
                    print(line[23:44], file=fOW)

        # Remove the .gro file at the end of the iteration to avoid pileup
        run("rm results/all.gro", shell=True, check=True)

    except CalledProcessError as e:
        print(f"Error during subprocess: {e}")
        exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
    finally:
        # Close the opened files in a 'finally' block to ensure they are closed even if an exception occurs
        fH1.close()
        fH2.close()
        fOW.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 coordinates.py mds/filename.xtc mds/filename.gro")
        sys.exit(1)

    xtc_file = sys.argv[1]
    gro_file = sys.argv[2]

    main(xtc_file, gro_file)
