// g++ -Wal -O gen_marketshare.cpp -o gen_marketshare

/** Generate markshare instances, see
 *  G. Cornuéjols, M. Dawande
 *  "A Class of Hard Small 0-1 Programs"
 *  IPCO VI, 1998, pp. 285-293
 *
 *  Input: m, D, seed
 *  Output: 
 *  instances of the form $Ax = b, x_i \in \{0,1\}$ in CPLEX-LP format, where
 *  - there are m inequalities
 *  - and $n = 10 (m - 1)$ variables.
 *  - Each integer coefficient $a_{ij}$ is randomly picket from the range between 0 and D-1,
 *  - the rhs is defined by $b_i = \lfloor \tfrac{1}{2} \sum_{j=1}^n a_{ij} \rfloor$,
 *  - and the objective is 0.
 *  - 'seed' is used to initialize the (pseudo) random number generator.
 *
 * The problem is written to 'markshare_<m>_<seed>.lp'.
 *
 *  Related to this are optimization versions (see Cornuéjols and Dawande and the markshare
 *  instances in MIPLIB 2003).
 *
 *  The resulting (feasibility and optimization) instances are considered hard. Currently,
 *  the largest instances that can be solved have m = 7 inequalities (see Aardal et al. below).
 *
 *  Note that with larger m  (e.g. $m > 7$) the probability to obtain a feasible instance
 *  increases (one has to take slightly fewer variables than $10 (m - 1)$), see
 *
 *  K. Aardal, R.E. Bixby, C.A.J. Hurkens, A.K. Lenstra, and J.W. Smeltink
 *  "Market split and basis reduction: towards a solution of the Cornuéjols-Dawande instances"
 *  INFORMS J. Comput. 12, No. 3, pp. 192-202, 2000.
 *
 *
 *  May 2005
 *  Marc Pfetsch
 *  Konrad-Zuse-Zentrum fuer Informationstechnik Berlin
 *
 *  Changed to pure number output 
 *  May 2024
 *  Thorsten Koch
 *  Zuse-Institute Berlin
 */


#include <iostream>
#include <cmath>
#include <fstream>
#include <sstream>
#include <stdlib.h>
#include <cassert>


// returns integer value in [0,d]
int random(int d)
{
   double rnd = drand48() * double(d+1);
   return int(rnd);
}


/** Generate markshare instance
 *
 * Parameters = m, D, seed
 * - m     number of inequalities
 * - D     the numbers are picked at random from [0,D-1]
 * - seed  to initialize random number generator
 *
 * The problem is written to 'markshare_<m>_<seed>.lp'.
 */
int main(int argc, const char** argv)
{
   if (argc != 4)
   {
      std::cerr << "Usage: " << argv[0] << "  <m> <D> <seed>" << std::endl;
      abort();
   }

   int m = atoi(argv[1]);     // number of inequalities
   int D = atoi(argv[2]);     // range for random numbers
   int seed = atoi(argv[3]);  // seed for random number generator

   srand48(seed);    // initialize random number generator

   int n = 10 * (m-1);        // number of variables

   // set up coefficient matrix and rhs
   int** matrix = new int* [m];
   for (int i = 0; i < m; ++i)
      matrix[i] = new int [n];
   int* b = new int [m];

   // generate problem:
   for (int i = 0; i < m; ++i)
   {
      int sum = 0;
      for (int j = 0; j < n; ++j)
      {
	 int value = random(D);
	 matrix[i][j] = value;
	 sum += value;
      }
      b[i] = int(sum/2);
   }
  
   // output problem
   std::stringstream filename;
   filename << "markshare_" << m << "_" << D << "_" << seed << ".dat" << std::ends;
   std::ofstream file(filename.str().c_str());
  
   //file << "Minimize" << std::endl;
   //file << " obj:" << std::endl;

   // to generate an artificial objective function uncomment the following
   /*
   file << "x1 ";
   for (int i = 1; i < n; ++i)
      file << "+ x" << i+1 << " ";
   file << std::endl;
   */
   //int slack = 0;
   
   //file << "Subject To" << std::endl;
   for (int i = 0; i < m; ++i)
   {
      for (int j = 0; j < n; ++j)
      {
	 if (matrix[i][j] != 0)
	 {
	    //if (j > 0)
	    //{
	    //   if (matrix[i][j] > 0)
            //  file << "+ ";
	    //}
	    assert( matrix[i][j] >= 0);
	    //file << matrix[i][j] << " x" << j+1 << " ";
            file << i + 1 << " " << j + 1 << " " << matrix[i][j] << std::endl;
	 }
      }
#if 0
      int sval = b[i];

      int p2 = 0;

      for(; sval > (1 << (p2 + 1)); p2++)
      {
         slack++;
         
         file << i + 1 << " " << -slack << " " << (1 << p2) << std::endl;
      }
      int rest = sval - ((1 << p2) - 1);

      for(int k = 0; k < 30; k++)
      {
         if ((rest & (1 << k)) == 0)
            continue;

         slack++;
         
         file << i + 1 << " " << -slack << " " << (1 << k) << std::endl;
      }
#endif
      // file << " = ";
      file << i + 1 << " 0 " << b[i] << std::endl;
   }

#if 0
   file << "Binary" << std::endl;
   for (int i = 0; i < n; ++i)
      file << "x" << i+1 << " ";
   file << std::endl;
   file << "End" << std::endl;
#endif
   std::cout << "Problem written to: " << filename.str() << std::endl;

   for (int i = 0; i < m; ++i)
      delete [] matrix[i];
   delete [] matrix;
   delete [] b;
}
