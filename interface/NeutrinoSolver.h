/*
	NeutrinoSolver: guess the 3D momentum of the neutrino in semi-leptonic top events
	from the W and Top mass constrains.

	Almost verbatim transcript of
	B. A. Betchart, R. Demina, and A. Harel: "Analytic solutions for neutrino momenta in
	decay of top quarks" , Nucl. Instrum. Meth. A 736 (2014) 169,
	doi:10.1016/j.nima.2013.10.039, arXiv:1305.1878 

	Variable naming can be significantly improved
 */
#ifndef HNSOLVER
#define HNSOLVER
#include <TMatrixD.h>
#include <TVector3.h>
#include <TLorentzVector.h>
#include <iostream>

using namespace std;
using namespace TMath;

class NeutrinoSolver {
private:
	double Mt;
	double Mw;
	double Ml;
	double Mb;
	double Mn;

	bool ERROR;
	TMatrixD H;
	TMatrixD T;
	TMatrixD MET;
	TMatrixD VM;
	TMatrixD RotationX(double a);
	TMatrixD RotationY(double a);
	TMatrixD RotationZ(double a);

	void Solve(double t);
	TMatrixD GetPtSolution(double t);
	TLorentzVector GetSolution(double t);
	double Chi2(double t);
	pair<double, double> Extrem(double t, bool MIN = true);
public:
	NeutrinoSolver(
		const TLorentzVector* lep, 
		const TLorentzVector* bjet, 
		double MW = 80, 
		double MT = 173);

	NeutrinoSolver():
		Mt(0), Mw(0),
		Ml(0), Mb(0),
		Mn(0), ERROR(true),
		H(), T(), MET(), VM()
	{}

	TLorentzVector GetBest(double metx, double mety, double metxerr, double metyerr, double metxyrho, double& test, bool INFO = false);

};


#endif
