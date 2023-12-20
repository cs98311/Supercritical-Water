#!/usr/bin/env python3

import subprocess


def main():
    try:
        # Open files for coordinates at each iteration
        fSys = open("results/systemInfo.txt", "w")
        fH1 = open("results/coordinates/h1.txt", "w")
        fH2 = open("results/coordinates/h2.txt", "w")
        fOW = open("results/coordinates/ow.txt", "w")

        # Takes input the iteration number from the main file
        # Print progress of iterations
        num = input("Timestep : ")
        print(f"{num}")

        # Generate .gro file for H2O, TFSI, Li, Zn at each iteration
        subprocess.run(
            f"gmx trjconv -f mds/prod2.xtc -s mds/prod2.gro -b {num} -e {num} -o results/all.gro",
            shell=True,
            input="0\n",
            capture_output=True,
            text=True,
            check=True,  # Add check=True for error handling
        )

        # Generate coordinate files for each element from the .gro files
        # Also keep count of water, TFSI, cations for the system info file
        countW = 0

        with open("results/all.gro", "r") as fCood:
            for line in fCood:
                if line[12:15] == "HW1":
                    countW += 1
                    print(line[23:44], file=fH1)
                elif line[12:15] == "HW2":
                    print(line[23:44], file=fH2)
                elif line[13:15] == "OW":
                    print(line[23:44], file=fOW)
                elif line[4] == ".":
                    print(line[3:11], file=fSys)

        print(countW, file=fSys)

        # Remove the .gro file at the end of the iteration to avoid pileup
        subprocess.run("rm results/all.gro", shell=True, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during subprocess: {e}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the opened files in a 'finally' block to ensure they are closed even if an exception occurs
        fSys.close()
        fH1.close()
        fH2.close()
        fOW.close()


if __name__ == "__main__":
    main()
