#! /usr/bin/env python3

import subprocess

# Open files for coordinates at each iteration

# File stores system info like box length, no. of water, TFSI, Li, Zn
file0 = open("SysInfo.txt", "w")

file1 = open("Coordinates/H1.txt", "w")
file2 = open("Coordinates/H2.txt", "w")
file3 = open("Coordinates/OW.txt", "w")


# Takes input the iteration number from main file
# Print progress of iterations
num = input()
print(num)


# Generate .gro file for H2O, TFSI, Li, Zn at each iteration

subprocess.run(
    "gmx trjconv -f MDSfiles/prod2.xtc -s MDSfiles/prod2.gro -b {} -e {} -o all.gro".format(
        num, num
    ),
    shell=True,
    input="0\n",
    capture_output=True,
    text=True,
)

# Generate coordinate files for each element from the .gro files
# Also keep count of water, TFSI, cations for the system info file

countW = 0

f = open("all.gro", "r")
for line in f:
    if line[12:15] == "HW1":
        countW += 1
        print(line[23:44], file=file1)
    if line[12:15] == "HW2":
        print(line[23:44], file=file2)
    if line[13:15] == "OW":
        print(line[23:44], file=file3)
    if line[4] == ".":
        print(line[3:11], file=file0)


print(countW, file=file0)


# Remove the .gro file at the end of iteration to avoid pileup
subprocess.run("rm all.gro", shell=True)


# Close the opened files
file0.close()
file1.close()
file2.close()
file3.close()
f.close()
