import os

from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.Heppy.physicsobjects.PhysicsObjects import Jet, GenJet

from PhysicsTools.HeppyCore.utils.deltar import cleanObjectCollection, matchObjectCollection

# from PhysicsTools.Heppy.physicsutils.BTagSF import BTagSF
from CMGTools.H2TauTau.proto.physicsobjects.BTagSF import BTagSF
from PhysicsTools.Heppy.physicsutils.JetReCalibrator import JetReCalibrator

# JAN: Kept this version of the jet analyzer in the tau-tau sequence
# for now since it has all the agreed-upon features used in the tau-tau group,
# in particular the SF seeding for b-tagging.
# In the long run, it might be a good idea to switch to the generic jet analyzer
# in heppy and possibly add b-tagging in another step or add it to the generic
# jet analyzer

def pippo():
	pass

class JetSelector(Analyzer):
	"""Analyze jets.

	Copied from heppy examples and edit to not rely on heppy examples.

	This analyzer filters the jets that do not correspond to the leptons
	stored in event.selectedLeptons, and puts in the event:
	- jets: all jets passing the pt and eta cuts
	- cleanJets: the collection of jets away from the leptons
	- cleanBJets: the jets passing testBJet, and away from the leptons

	Example configuration:

	jetAna = cfg.Analyzer(
	  'JetSelector',
	  jetCol = 'slimmedJets'
	  # cmg jet input collection
	  # pt threshold
	  jetPt = 30,
	  # eta range definition
	  jetEta = 5.0,
	  # seed for the btag scale factor
	  btagSFseed = 0xdeadbeef,
	  # if True, the PF and PU jet ID are not applied, and the jets get flagged
	  relaxJetId = False,
	  relaxPuJetId = False,
	)
	"""

	def __init__(self, cfg_ana, cfg_comp, looperName):
		super(JetSelector, self).__init__(cfg_ana, cfg_comp, looperName)
		self.btagSF = BTagSF(0, wp='medium')
		self.recalibrateJets = getattr(cfg_ana, 'recalibrateJets', False)

		mcGT = getattr(cfg_ana, 'mcGT', 'Spring16_25nsV6_MC')
		dataGT = getattr(cfg_ana, 'dataGT', 'Spring16_25nsV6_DATA')

		if self.recalibrateJets:
			doResidual = getattr(cfg_ana, 'applyL2L3Residual', 'Data')
			if doResidual == "MC":
				doResidual = self.cfg_comp.isMC
			elif doResidual == "Data":
				doResidual = not self.cfg_comp.isMC
			elif doResidual not in [True, False]:
				raise RuntimeError, "If specified, applyL2L3Residual must be any of { True, False, 'MC', 'Data'(default)}"
			GT = getattr(cfg_comp, 'jecGT', mcGT if self.cfg_comp.isMC else dataGT)

			# instantiate the jet re-calibrator
			self.jetReCalibrator = JetReCalibrator(
				GT, 'AK4PFchs', doResidual, 
				jecPath="%s/src/CMGTools/RootTools/data/jec" % os.environ['CMSSW_BASE']
				)


	def declareHandles(self):
		super(JetSelector, self).declareHandles()

		self.handles['jets'] = AutoHandle(
			self.cfg_ana.jetCol,
			'std::vector<pat::Jet>'
			)

		if self.cfg_comp.isMC:
			self.mchandles['genParticles'] = AutoHandle(
				'packedGenParticles',
				'std::vector<pat::PackedGenParticle>'
				)
			self.mchandles['genJets'] = AutoHandle(
				'slimmedGenJets',
				'std::vector<reco::GenJet>'
				)

	def beginLoop(self, setup):
		super(JetSelector, self).beginLoop(setup)
		self.counters.addCounter('jets')
		count = self.counters.counter('jets')
		count.register('all events')
		count.register('at least 2 good jets')
		count.register('at least 2 clean jets')
		count.register('at least 1 b jet')
		count.register('at least 2 b jets')

	def process(self, event):

		self.counters.counter('jets').inc('all events')
		self.readCollections(event.input)
		miniaodjets = self.handles['jets'].product()

		allJets = []

		leptons = []
		if hasattr(self.cfg_ana, 'toClean'):
			leptons = getattr(event, self.cfg_ana.toClean)

		genJets = None
		if self.cfg_comp.isMC:
			genJets = map(GenJet, self.mchandles['genJets'].product())

		allJets = [Jet(jet) for jet in miniaodjets]

		if self.recalibrateJets:
			self.jetReCalibrator.correctAll(
				allJets, event.rho, delta=0., 
				addCorr=True, addShifts=True
				)

		for jet in allJets:
			if genJets:
				# Use DeltaR = 0.25 matching like JetMET
				pairs = matchObjectCollection([jet], genJets, 0.25 * 0.25)
				if pairs[jet] is None:
					pass
				else:
					jet.matchedGenJet = pairs[jet]
			# Add JER correction for MC jets. Requires gen-jet matching.
			if self.cfg_comp.isMC and hasattr(self.cfg_ana, 'jerCorr') and self.cfg_ana.jerCorr:
				self.jerCorrection(jet)
			# Add JES correction for MC jets.
			if self.cfg_comp.isMC and hasattr(self.cfg_ana, 'jesCorr'):
				self.jesCorrection(jet, self.cfg_ana.jesCorr)
			jet.btagMVA = jet.btag('pfCombinedInclusiveSecondaryVertexV2BJetTags') #TODO switch to deepCSV
			jet.btagged = self.btagSF.isBTagged(
				pt=jet.pt(),
				eta=jet.eta(),
				csv=jet.btag("pfCombinedInclusiveSecondaryVertexV2BJetTags"),
				jetflavor=abs(jet.hadronFlavour()),
				is_data=not self.cfg_comp.isMC,
				csv_cut=csv_cut
				)
			## if self.testJet(jet):
			## 	event.jets.append(jet)
			## if self.testBJet(jet):
			## 	event.bJets.append(jet)

		allJets = [
			jet for jet in allJets 
			if bool(jet.jetID("POG_PFID_Loose"))
			if jet.pt() > 20.
			if abs(jet.eta()) < 2.4
			]		
		if len(allJets) < 2: return False
		self.counters.counter('jets').inc('at least 2 good jets')

		event.jets, dummy = cleanObjectCollection(
			event.jets,
			masks=leptons,
			deltaRMin=0.5
			)
		if len(event.jets) < 2: return False
		self.counters.counter('jets').inc('at least 2 clean jets')

		event.bJets = [
			jet for jet in event.jets
			if jet.btagged
			]
		if len(event.bJets) != 2: return False
		self.counters.counter('jets').inc('exactly 2 b jets')			
	
		# save HTs
		event.HT_jets	 = sum([jet.pt() for jet in event.jets	   ])
		event.HT_bJets = sum([jet.pt() for jet in event.bJets	  ])
		
		return True

	def jerCorrection(self, jet):
		''' Adds JER correction according to first method at
		https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution

		Requires some attention when genJet matching fails.
		'''
		if not hasattr(jet, 'matchedGenJet'):
			return
		#import pdb; pdb.set_trace()
		corrections = [0.052, 0.057, 0.096, 0.134, 0.288]
		maxEtas = [0.5, 1.1, 1.7, 2.3, 5.0]
		eta = abs(jet.eta())
		for i, maxEta in enumerate(maxEtas):
			if eta < maxEta:
				pt = jet.pt()
				deltaPt = (pt - jet.matchedGenJet.pt()) * corrections[i]
				totalScale = (pt + deltaPt) / pt

				if totalScale < 0.:
					totalScale = 0.
				jet.scaleEnergy(totalScale)
				break

	def jesCorrection(self, jet, scale=0.):
		''' Adds JES correction in number of sigmas (scale)
		'''
		# Do nothing if nothing to change
		if scale == 0.:
			return
		unc = jet.uncOnFourVectorScale()
		totalScale = 1. + scale * unc
		if totalScale < 0.:
			totalScale = 0.
		jet.scaleEnergy(totalScale)

