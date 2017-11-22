import ROOT
from itertools import product, combinations

from PhysicsTools.Heppy.analyzers.core.Analyzer   import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.Heppy.physicsobjects.Photon     import Photon
from PhysicsTools.HeppyCore.utils.deltar          import deltaR, deltaR2

from pdb import set_trace

class GammaSelector(Analyzer):
	'''
	Selects (isolated/ID) photons
	'''

	def declareHandles(self):
		super(GammaSelector, self).declareHandles()

		self.handles['photons'] = AutoHandle(
			'slimmedPhotons',
			'vector<pat::Photon>'
		)

	def beginLoop(self, setup):
		super(GammaSelector, self).beginLoop(setup)
		self.counters.addCounter('gammas')
		count = self.counters.counter('gammas')
		count.register('all events')
		count.register('> 0 vertex')
		count.register('> 0 tri-muon')
		# count.register('pass resonance veto')
		count.register('m < 3 GeV')
		count.register('trigger matched')

	def buildPhotons(self, photons, event):
		'''Make all muons'''
		gammas = map(Photon, photons)
		for gamma in gammas:
			gamma.associatedVertex = event.vertices[0]
		return gammas
		
	
	def process(self, event):
		self.readCollections(event.input)

		if not len(event.vertices):
			return False
		
		#TODO: put trigger requirements
		all_gammas  = self.buildPhotons(
			self.handles['photons'].product(), 
			event
			)
		event.gammas = [
			i for i in all_gammas
			if i.photonID('mvaPhoID-Spring15-25ns-nonTrig-V2p1-wp90')
			if i.pt() > 20 #FIXME GUESSING
			if abs(i.eta()) < 2.4 #FIXME GUESSING
			]

		return True

	def selectionSequence(self, event):
		return True


