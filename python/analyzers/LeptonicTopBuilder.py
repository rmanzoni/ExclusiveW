import ROOT
ROOT.gSystem.Load("libCMGToolsExclusiveW")
from ROOT import NeutrinoSolver

from itertools import product, combinations

from PhysicsTools.Heppy.analyzers.core.Analyzer   import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.Heppy.physicsobjects.Muon       import Muon
from PhysicsTools.Heppy.physicsobjects.Electron   import Electron
from PhysicsTools.HeppyCore.utils.deltar          import deltaR, deltaR2
from CMGTools.ExclusiveW.physicsobjects.compositeobject import CompositeObject

global m_w ; m_w = 80.385 # GeV
from pdb import set_trace

class LeptonicTopBuilder(Analyzer):
	'''
	'''
	def declareHandles(self):
		super(LeptonicTopBuilder, self).declareHandles()
		
		self.handles['puppimet'] = AutoHandle(
			'slimmedMETsPuppi',
			'std::vector<pat::MET>'
			)
		
		self.handles['pfmet'] = AutoHandle(
			'slimmedMETs',
			'std::vector<pat::MET>'
			)
		
		self.handles['mvamets'] = AutoHandle(
			('MVAMET', 'MVAMET', 'MVAMET'),
			'std::vector<pat::MET>',
			mayFail = True # not guaranteed MVA MET is always available
			)

	def process(self, event):
		#pre-requisite, might not be true as previous modules are non-blocking
		if len(event.tightLeptons) != 1: 
			event.lepTop = None
			event.spareBjet = None
			return True #still non-blocking

		self.readCollections(event.input)
				
		lepton = event.tightLeptons[0]
		met = self.handles['pfmet'].product()[0] #FIXME MVA MET?
		candidate  = None
		other_bjet = None
		set_trace()
		for bjet, other in zip(event.bJets, event.bJets[::-1]):
			solver = NeutrinoSolver(lepton, bjet)
			nu_chi2 = ROOT.Double()
			nu = solver.GetBest( 
				met.px(),
				met.py(),
				1, 1, 0., #Add MET Uncetainty
				nu_chi2
				)
			#check if we have a valid solution and a better candidate
			if nu_chi2 != -1 and \
					 (candidate is None or candidate.chi2nu > nu_chi2): 
				candidate = CompositeObject(
					lep = lepton,
					bjet = bjet,
					nu = nu
					)
				candidate.chi2nu = float(nu_chi2)
				other_bjet = other
		
		event.spareBjet = other_bjet
		event.lepTop    = candidate
		return True

	def selectionSequence(self, event):
		return True

