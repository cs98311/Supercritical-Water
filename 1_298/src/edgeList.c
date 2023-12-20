// Each water Molecule H-bonds Analysis

/*

To Run:
gcc Codes/edgeListDA.c -o Codes/edgeListDA.out -lm
./Codes/edgeListDA.out
rm Codes/edgeListDA.out

*/

#include <stdio.h>
#include <math.h>

//////////////////////////////////////////////
// Defining Global Variables for System Info//
//////////////////////////////////////////////

// Box length of the cubic system
double box_length;

int numW;

///////////////////////
// DEFINING FUNCTIONS //
///////////////////////

// Function to get magnitude of 2 vectors(of size=3)
double get_magnitude(double m[3])
{
	double mag = 0;
	mag = sqrt(m[0] * m[0] + m[1] * m[1] + m[2] * m[2]);
	return mag;
}

// Function to get dot product of 2 vectors(of size=3)
double dot_product(double m[3], double n[3])
{

	double dt = 0.0;
	int i = 0;
	for (i = 0; i < 3; i++)
	{
		dt += m[i] * n[i];
	}
	return dt;
}

// Function to get angle between 2 vectors(of size=3)
double vector_angle(double v1[3], double v2[3])
{

	double dot = 0, mag1 = 0, mag2 = 0;
	dot = dot_product(v1, v2);
	mag1 = get_magnitude(v1);
	mag2 = get_magnitude(v2);
	return acos((dot) / (mag1 * mag2));
}

// Function to swap two numbers
void swap(int *xp, int *yp)
{
	int temp = *xp;
	*xp = *yp;
	*yp = temp;
}

// Function to apply selection sort to 1D array of size=n
void selectionSort(int arr[], int n)
{
	int i, j, min_idx;
	for (i = 0; i < n - 1; i++)
	{
		min_idx = i;
		for (j = i + 1; j < n; j++)
			if (arr[j] < arr[min_idx])
				min_idx = j;
		swap(&arr[min_idx], &arr[i]);
	}
}

// PBC(Periodic Boundary Condition)
void PBC(double vector[3])
{
	int j = 0;
	for (j = 0; j < 3; j++)
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
void Check_HB_water(double H1[numW][3], double OW[numW][3], int m, int noH, FILE *fEdges, int Donor[numW], int Acceptor[numW])
{

	int i = 0, j = 0;

	double distance = 0, v1[3], v2[3], angle = 0;
	double dL[3];

	// Calculating v1 vector
	for (j = 0; j < 3; j++)
	{
		v1[j] = H1[m][j] - OW[m][j];
	}
	PBC(v1);

	// Iteration Starts here
	for (i = 0; i < numW; i++)
	{

		// Avoiding the current water molecule for check
		if (i == m)
		{
			continue;
		}

		// Adjusting for PBC
		for (j = 0; j < 3; j++)
		{
			dL[j] = (OW[i][j] - H1[m][j]);

			if (dL[j] > box_length / 2)
			{
				dL[j] -= box_length;
			}
			else if (dL[j] < -box_length / 2)
			{
				dL[j] += box_length;
			}
		}

		for (j = 0; j < 3; j++)
		{
			v2[j] = v1[j] + dL[j];
		}
		PBC(v2);

		distance = sqrt(dL[0] * dL[0] + dL[1] * dL[1] + dL[2] * dL[2]);
		angle = vector_angle(v1, v2);
		angle *= 57.2958;

		// Applying the geometric check for HB
		if (distance < 0.22 && angle < 35)
		{
			fprintf(fEdges, "%d,%d\n", m, i);

			Donor[m] += 1;
			Acceptor[i] += 1;
		}
	}
	// Iteration over other water molecules ends here
}

//////////////////
// Main Function /
//////////////////

int main()
{

	// Opening the files for coordinates, System Info, Results,etc.//

	FILE *fI = fopen("results/systemInfo.txt", "r");

	FILE *fH1 = fopen("results/coordinates/h1.txt", "r");
	FILE *fH2 = fopen("results/coordinates/h2.txt", "r");
	FILE *fOW = fopen("results/coordinates/ow.txt", "r");

	// Results storage files
	FILE *fEdges = fopen("results/water/edges.csv", "w");

	// Defining and initializing any used variables
	int i = 0, j = 0, k = 0, m = 0;

	// Scanning the System Info into global variables
	fscanf(fI, "%lf %d", &box_length, &numW);

	// Defining arrays for all elements of the system
	double H1[numW][3], H2[numW][3], OW[numW][3];

	// Scanning the coordinates from respective files //

	for (i = 0; i < numW; i++)
	{
		for (j = 0; j < 3; j++)
		{
			fscanf(fH1, "%lf", &H1[i][j]);
			fscanf(fH2, "%lf", &H2[i][j]);
			fscanf(fOW, "%lf", &OW[i][j]);
		}
	}

	int Acceptor[numW], Donor[numW];

	for (i = 0; i < numW; i++)
	{
		Acceptor[i] = 0;
	}

	for (i = 0; i < numW; i++)
	{
		Donor[i] = 0;
	}

	///////////////////////
	// Starting Iterations//
	///////////////////////

	// Iteration checks for each water molecule for all
	// H-bonds with other water, TFSI and Coordination with Zn/Li

	for (m = 0; m < numW; m++)
	{

		// Check for H1 hydogen first
		Check_HB_water(H1, OW, m, 1, fEdges, Donor, Acceptor);

		// Check for H2 hydrogen
		Check_HB_water(H2, OW, m, 2, fEdges, Donor, Acceptor);
	}

	///////////////////////
	// Iterations Finished//
	///////////////////////

	FILE *fH2Oda = fopen("results/water/donorAcceptor.txt", "a");

	double d0a0 = 0, d0a1 = 0, d0a2 = 0, d1a0 = 0, d1a1 = 0, d1a2 = 0, d2a0 = 0, d2a1 = 0, d2a2 = 0, totda = 0;

	for (i = 0; i < numW; i++)
	{
		if (Donor[i] == 0 && Acceptor[i] == 0)
			d0a0 += 1;
		else if (Donor[i] == 0 && Acceptor[i] == 1)
			d0a1 += 1;
		else if (Donor[i] == 0 && Acceptor[i] == 2)
			d0a2 += 1;
		else if (Donor[i] == 1 && Acceptor[i] == 0)
			d1a0 += 1;
		else if (Donor[i] == 1 && Acceptor[i] == 1)
			d1a1 += 1;
		else if (Donor[i] == 1 && Acceptor[i] == 2)
			d1a2 += 1;
		else if (Donor[i] == 2 && Acceptor[i] == 0)
			d2a0 += 1;
		else if (Donor[i] == 2 && Acceptor[i] == 1)
			d2a1 += 1;
		else if (Donor[i] == 2 && Acceptor[i] == 2)
			d2a2 += 1;
	}

	totda = d0a0 + d0a1 + d0a2 + d1a0 + d1a1 + d1a2 + d2a0 + d2a1 + d2a2;

	fprintf(fH2Oda, "%.2lf %.2lf %.2lf %.2lf %.2lf %.2lf %.2lf %.2lf %.2lf\n", d0a0 * 100 / totda, d0a1 * 100 / totda, d0a2 * 100 / totda, d1a0 * 100 / totda, d1a1 * 100 / totda, d1a2 * 100 / totda, d2a0 * 100 / totda, d2a1 * 100 / totda, d2a2 * 100 / totda);

	fclose(fH2Oda);

	/////////////////////
	// CLOSING THE FILES//
	/////////////////////

	fclose(fH1);
	fclose(fH2);
	fclose(fOW);
	fclose(fI);
	fclose(fEdges);

	return 0;
}
