import ROOT
from itertools import product, combinations

from PhysicsTools.Heppy.analyzers.core.Analyzer   import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.Heppy.physicsobjects.Muon       import Muon
from PhysicsTools.Heppy.physicsobjects.Electron   import Electron
from PhysicsTools.HeppyCore.utils.deltar          import deltaR, deltaR2

global m_w ; m_w = 80.385 # GeV
from pdb import set_trace

class LeptonSelector(Analyzer):
	'''
	'''

	def declareHandles(self):
		super(LeptonSelector, self).declareHandles()

		self.handles['electrons'] = AutoHandle(
			'slimmedElectrons',
			'std::vector<pat::Electron>'
		)

		self.handles['muons'] = AutoHandle(
			'slimmedMuons',
			'std::vector<pat::Muon>'
		)

	def beginLoop(self, setup):
		super(LeptonSelector, self).beginLoop(setup)
		self.counters.addCounter('ExclusiveW')
		count = self.counters.counter('ExclusiveW')
		count.register('all events')
		count.register('> 0 vertex')
		count.register('> 0 tri-muon')
		# count.register('pass resonance veto')
		count.register('m < 3 GeV')
		count.register('trigger matched')

	def buildMuons(self, muons, event):
		'''Make all muons'''
		muons = map(Muon, muons)
		for mu in muons:
			mu.associatedVertex = event.vertices[0]
		return muons
		
	def buildElectrons(self, electrons, event):
		'''Make all electrons'''
		electrons = map(Electron, electrons)
		for ele in electrons:
			ele.associatedVertex = event.vertices[0]
			ele.etaSC = ele.superCluster().eta()
			ele.ipCut = (abs(ele.dxy()) < 0.05 and abs(ele.dz()) < 0.10) \
				 if ele.etaSC < 1.479 else \
				 (abs(ele.dxy()) < 0.1 and abs(ele.dz()) < 0.20)
		return electrons
	
	def process(self, event):
		self.readCollections(event.input)

		if not len(event.vertices):
			return False
		
		self.counters.counter('ExclusiveW').inc('> 0 vertex')

				#TODO: put trigger requirements
		all_muons	  = self.buildMuons	(self.handles['muons'	].product(), event)
		all_electrons  = self.buildElectrons(self.handles['electrons'].product(), event)
		
		set_trace()
		tight_muons = []
		veto_muons  = []
		for mu in all_muons:
			if mu.pt() > 26 and abs(mu.eta()) < 2.4 and \
					 mu.isTightMuon(mu.associatedVertex) and \
					 mu.relIso() < .15:
				tight_muons.append(mu)
			elif mu.pt() > 10 and abs(mu.eta()) < 2.4 and \
					 mu.isLooseMuon() and mu.relIso() < .25:
				veto_muons.append(mu)
		event.tightMuons = tight_muons
		event.vetoMuons = veto_muons

		tight_electrons = []
		veto_electrons  = []
		for el in all_electrons:
			if el.pt() > 30 and abs(el.etaSC) < 2.1 and \
					 (abs(el.etaSC) <= 1.4442 or abs(el.etaSC) >= 1.5660) and \
					 el.ipCut and el.electronID('cutBasedElectronID-Spring15-25ns-V1-standalone-tight'): #TODO Check if makes sense
				tight_electrons.append(el)
			elif el.pt() > 20 and abs(el.etaSC) < 2.5 and \
					 el.electronID('cutBasedElectronID-Spring15-25ns-V1-standalone-veto'):
				veto_electrons.append(el)
		event.tightElectrons = tight_electrons
		event.vetoElectrons  = veto_electrons
			
		# useful for jet cross cleaning
		event.tightLeptons = tight_muons+tight_electrons
		event.vetoLeptons  = veto_muons+veto_electrons

		return not bool(event.vetoLeptons) and event.tightLeptons

	def selectionSequence(self, event):
		return True


