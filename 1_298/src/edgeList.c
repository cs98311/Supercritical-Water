// Each water Molecule H-bonds Analysis

/*
To Run:

gcc Codes/edgeListDA.c -o Codes/edgeListDA.out -lm
./Codes/edgeListDA.out
rm Codes/edgeListDA.out

*/

#include <stdio.h>
#include <math.h>

double box_length;
int numW;

double get_magnitude(double m[3]);
double dot_product(double m[3], double n[3]);
double vector_angle(double v1[3], double v2[3]);
void PBC(double vector[3]);
void checkHB(double H1[numW][3], double OW[numW][3], int m, int noH, FILE *fEdges, int donor[numW], int acceptor[numW]);

int main()
{
	FILE *fSys = fopen("results/systemInfo.txt", "r");
	FILE *fH1 = fopen("results/coordinates/h1.txt", "r");
	FILE *fH2 = fopen("results/coordinates/h2.txt", "r");
	FILE *fOW = fopen("results/coordinates/ow.txt", "r");
	FILE *fEdges = fopen("results/water/edges.csv", "w");

	if (!fSys || !fH1 || !fH2 || !fOW || !fEdges)
	{
		fprintf(stderr, "Error: Unable to open files.\n");
		return 1;
	}

	// Scanning the System Info
	fscanf(fSys, "%lf %d", &box_length, &numW);

	// Defining arrays for all elements of the system
	double H1[numW][3], H2[numW][3], OW[numW][3];

	// Scanning the coordinates from respective files //
	for (int i = 0; i < numW; i++)
	{
		for (int j = 0; j < 3; j++)
		{
			fscanf(fH1, "%lf", &H1[i][j]);
			fscanf(fH2, "%lf", &H2[i][j]);
			fscanf(fOW, "%lf", &OW[i][j]);
		}
	}

	fclose(fH1);
	fclose(fH2);
	fclose(fOW);
	fclose(fSys);

	int acceptor[numW], donor[numW];
	for (int i = 0; i < numW; i++)
	{
		acceptor[i] = 0;
		donor[i] = 0;
	}

	// Starting Iterations

	for (int m = 0; m < numW; m++)
	{
		// Check for H1 hydrogen
		checkHB(H1, OW, m, 1, fEdges, donor, acceptor);
		// Check for H2 hydrogen
		checkHB(H2, OW, m, 2, fEdges, donor, acceptor);
	}

	fclose(fEdges);

	FILE *fH2Oda = fopen("results/water/donorAcceptor.txt", "a");
	double d0a0 = 0, d0a1 = 0, d0a2 = 0, d1a0 = 0, d1a1 = 0, d1a2 = 0, d2a0 = 0, d2a1 = 0, d2a2 = 0, totda = 0;
	for (int i = 0; i < numW; i++)
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
double get_magnitude(double m[3])
{
	return sqrt(m[0] * m[0] + m[1] * m[1] + m[2] * m[2]);
}

// Get dot product of 2 vectors of size=3
double dot_product(double m[3], double n[3])
{
	return m[0] * n[0] + m[1] * n[1] + m[2] * n[2];
}

// Get angle between 2 vectors of size=3
double vector_angle(double v1[3], double v2[3])
{
	return 57.2958 * acos((dot_product(v1, v2)) / (get_magnitude(v1) * get_magnitude(v2)));
}

// Periodic Boundary Condition
void PBC(double vector[3])
{
	for (int j = 0; j < 3; j++)
	{
		if (vector[j] > box_length / 2)
		{
			vector[j] -= box_length;
		}
		else if (vector[j] < -box_length / 2)
		{
			vector[j] += box_length;
		}
	}
}

// Function to check if H-bond is formed by current water molecule(m) being checked
// with another water oxygen(i) in the system
void checkHB(double H1[numW][3], double OW[numW][3], int m, int noH, FILE *fEdges, int donor[numW], int acceptor[numW])
{
	double distance = 0, v1[3], v2[3], angle = 0;
	double dL[3];

	// v1 vector : Om-->Hm
	for (int j = 0; j < 3; j++)
	{
		v1[j] = H1[m][j] - OW[m][j];
	}
	PBC(v1);

	// Iterate over all water molecules
	for (int i = 0; i < numW; i++)
	{
		// Avoiding the current water molecule for check
		if (i == m)
			continue;

		// H-Bond vector : Hm-->Oi
		for (int j = 0; j < 3; j++)
		{
			dL[j] = (OW[i][j] - H1[m][j]);
		}
		PBC(dL);

		// v2 vector : Om-->Oi
		for (int j = 0; j < 3; j++)
		{
			v2[j] = v1[j] + dL[j];
		}
		PBC(v2);

		distance = get_magnitude(dL);
		angle = vector_angle(v1, v2);

		// Geometric check for H-bond
		if (distance < 0.22 && angle < 35)
		{
			fprintf(fEdges, "%d,%d\n", m, i);
			donor[m] += 1;
			acceptor[i] += 1;
		}
	}
}
