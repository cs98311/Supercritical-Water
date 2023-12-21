// Water Molecule H-bond Edge List

/*
To Run:

gcc Codes/edgeListDA.c -o Codes/edgeListDA.out -lm
./Codes/edgeListDA.out
rm Codes/edgeListDA.out

*/

#include <stdio.h>
#include <math.h>
#include "globals.h"

double magnitude(double m[3]);
double dot_product(double m[3], double n[3]);
double angle_between_vectors(double v1[3], double v2[3]);
void pbc(double vector[3]);
void checkHB(double h1[NUM_H2O][3], double ow[NUM_H2O][3], int m, int noH, FILE *fEdges, int donor[NUM_H2O], int acceptor[NUM_H2O]);

int main()
{
	// Requires H1, H2 and OW coordinates as input
	FILE *fH1 = fopen("results/coordinates/h1.txt", "r");
	FILE *fH2 = fopen("results/coordinates/h2.txt", "r");
	FILE *fOW = fopen("results/coordinates/ow.txt", "r");
	FILE *fEdges = fopen("results/water/edges.csv", "w");

	if (!fH1 || !fH2 || !fOW || !fEdges)
	{
		fprintf(stderr, "Error: Unable to open files.\n");
		return 1;
	}

	// Defining arrays for all elements of the system
	double h1[NUM_H2O][3] = {{0}}, h2[NUM_H2O][3] = {0}, ow[NUM_H2O][3] = {0};

	// Scanning the coordinates from respective files //
	for (int i = 0; i < NUM_H2O; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			fscanf(fH1, "%lf", &h1[i][j]);
			fscanf(fH2, "%lf", &h2[i][j]);
			fscanf(fOW, "%lf", &ow[i][j]);
		}
	}

	fclose(fH1);
	fclose(fH2);
	fclose(fOW);

	int acceptor[NUM_H2O] = {0}, donor[NUM_H2O] = {0};

	// Starting Iterations
	for (int m = 0; m < NUM_H2O; m++)
	{
		// Check for h1 hydrogen
		checkHB(h1, ow, m, 1, fEdges, donor, acceptor);
		// Check for h2 hydrogen
		checkHB(h2, ow, m, 2, fEdges, donor, acceptor);
	}

	fclose(fEdges);

	FILE *fH2Oda = fopen("results/water/donorAcceptor.txt", "a");
	double d0a0 = 0, d0a1 = 0, d0a2 = 0, d1a0 = 0, d1a1 = 0, d1a2 = 0, d2a0 = 0, d2a1 = 0, d2a2 = 0, totda = 0;
	for (int i = 0; i < NUM_H2O; i++)
	{
		if (donor[i] == 0 && acceptor[i] == 0)
			d0a0 += 1;
		else if (donor[i] == 0 && acceptor[i] == 1)
			d0a1 += 1;
		else if (donor[i] == 0 && acceptor[i] == 2)
			d0a2 += 1;
		else if (donor[i] == 1 && acceptor[i] == 0)
			d1a0 += 1;
		else if (donor[i] == 1 && acceptor[i] == 1)
			d1a1 += 1;
		else if (donor[i] == 1 && acceptor[i] == 2)
			d1a2 += 1;
		else if (donor[i] == 2 && acceptor[i] == 0)
			d2a0 += 1;
		else if (donor[i] == 2 && acceptor[i] == 1)
			d2a1 += 1;
		else if (donor[i] == 2 && acceptor[i] == 2)
			d2a2 += 1;
	}
	totda = d0a0 + d0a1 + d0a2 + d1a0 + d1a1 + d1a2 + d2a0 + d2a1 + d2a2;

	fprintf(fH2Oda, "%.2lf %.2lf %.2lf %.2lf %.2lf %.2lf %.2lf %.2lf %.2lf\n", d0a0 * 100 / totda, d0a1 * 100 / totda, d0a2 * 100 / totda, d1a0 * 100 / totda, d1a1 * 100 / totda, d1a2 * 100 / totda, d2a0 * 100 / totda, d2a1 * 100 / totda, d2a2 * 100 / totda);

	fclose(fH2Oda);

	return 0;
}

// Get magnitude of a vector of size=3
double magnitude(double m[3])
{
	return sqrt(m[0] * m[0] + m[1] * m[1] + m[2] * m[2]);
}

// Get dot product of 2 vectors of size=3
double dot_product(double m[3], double n[3])
{
	return m[0] * n[0] + m[1] * n[1] + m[2] * n[2];
}

// Get angle between 2 vectors of size=3
double angle_between_vectors(double v1[3], double v2[3])
{
	return 57.2958 * acos((dot_product(v1, v2)) / (magnitude(v1) * magnitude(v2)));
}

// Periodic Boundary Condition
void pbc(double vector[3])
{
	for (int j = 0; j < 3; j++)
	{
		if (vector[j] > BOX_LENGTH / 2)
		{
			vector[j] -= BOX_LENGTH;
		}
		else if (vector[j] < -BOX_LENGTH / 2)
		{
			vector[j] += BOX_LENGTH;
		}
	}
}

// Function to check if H-bond is formed by current water molecule(m) being checked
// with another water oxygen(i) in the system
void checkHB(double h1[NUM_H2O][3], double ow[NUM_H2O][3], int m, int noH, FILE *fEdges, int donor[NUM_H2O], int acceptor[NUM_H2O])
{
	double v1[3] = {0}, v2[3] = {0}, dL[3] = {0};

	// v1 : O(donor)-->H(donor)
	for (int j = 0; j < 3; j++)
		v1[j] = h1[m][j] - ow[m][j];
	pbc(v1);

	// Iterate over all water molecules
	for (int i = 0; i < NUM_H2O; i++)
	{
		// Skip the current water molecule
		if (i == m)
			continue;

		// H-Bond vector : H(donor)-->O(acceptor)
		for (int j = 0; j < 3; j++)
			dL[j] = (ow[i][j] - h1[m][j]);
		pbc(dL);

		// v2 : O(donor)-->O(acceptor)
		for (int j = 0; j < 3; j++)
			v2[j] = v1[j] + dL[j];
		pbc(v2);

		// Geometric check for H-bond
		if (magnitude(dL) < DISTANCE_CUTOFF && angle_between_vectors(v1, v2) < ANGLE_CUTOFF)
		{
			fprintf(fEdges, "%d,%d\n", m, i);
			donor[m] += 1;
			acceptor[i] += 1;
		}
	}
}
