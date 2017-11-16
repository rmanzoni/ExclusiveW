import ROOT
from itertools import product, combinations

from PhysicsTools.Heppy.analyzers.core.Analyzer   import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.Heppy.physicsobjects.Photon     import Photon
from PhysicsTools.Heppy.physicsobjects.Muon       import Muon
from PhysicsTools.Heppy.physicsobjects.Electron   import Electron
from PhysicsTools.Heppy.physicsobjects.Photon     import Photon
from PhysicsTools.HeppyCore.utils.deltar          import deltaR, deltaR2

from CMGTools.ExclusiveW.physicsobjects.WDsGamma  import WDsGamma
from CMGTools.ExclusiveW.physicsobjects.Ds        import Ds, m_ds, m_phi

global m_w ; m_w = 80.385 # GeV

class TTBarWLNuWDsGammaAnalyzer(Analyzer):
    '''
    '''

    def declareHandles(self):
        super(TTBarWLNuWDsGammaAnalyzer, self).declareHandles()

        self.handles['electrons'] = AutoHandle(
            'slimmedElectrons',
            'std::vector<pat::Electron>'
        )

        self.handles['photons'] = AutoHandle(
            'slimmedPhotons',
            'std::vector<pat::Photon>'
        )

        self.handles['muons'] = AutoHandle(
            'slimmedMuons',
            'std::vector<pat::Muon>'
        )

        self.handles['losttracks'] = AutoHandle(
            'lostTracks',
            'std::vector<pat::PackedCandidate>'
        )

        self.handles['pfcands'] = AutoHandle(
            'packedPFCandidates',
            'std::vector<pat::PackedCandidate>'
        )

        self.mchandles['genParticles'] = AutoHandle(
            'prunedGenParticles',
            'std::vector<reco::GenParticle>'
        )

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


    def beginLoop(self, setup):
        super(TTBarWLNuWDsGammaAnalyzer, self).beginLoop(setup)
        self.counters.addCounter('Tau3Mu')
        count = self.counters.counter('Tau3Mu')
        count.register('all events')
        count.register('> 0 vertex')
        count.register('> 0 tri-muon')
        # count.register('pass resonance veto')
        count.register('m < 3 GeV')
        count.register('trigger matched')

    def buildMuons(self, muons, event):
        '''
        '''
        muons = map(Muon, muons)
        for mu in muons:
            mu.associatedVertex = event.vertices[0]
        muons = [mu for mu in muons if 
                 (mu.isMediumMuon()) and
                 mu.pt()>5. and
                 abs(mu.eta())<=2.5]          
        return muons

    def buildPhotons(self, photons, event):
        '''
        To be implemented.
        REMEMBER TO ADD RHO!
        '''
        photons = map(Photon, photons) 
        photons = [ph for ph in photons if
                   ph.pt()>1 and
                   abs(ph.eta())<2.5 and
                   ph.photonID('PhotonCutBasedIDLoose') and
                   abs(event.vertices[0].z() - ph.vertex().z())<1]
        return photons
        
        
    def buildElectrons(self, electrons, event):
        '''
        Used for veto
        '''
        electrons = map(Electron, electrons)
        for ele in electrons:
            ele.associatedVertex = event.vertices[0]
        electrons = [ele for ele in electrons if
                     ele.pt()>10 and
                     abs(ele.eta())<2.5 and
                     # ele.mvaIDRun2('Spring16', 'Veto') and # why?
                     ele.mvaIDRun2('NonTrigSpring15MiniAOD', 'POG90') and
                     self.testVertex(ele) and
                     ele.passConversionVeto() and
                     ele.physObj.gsfTrack().hitPattern().numberOfHits(ROOT.reco.HitPattern.MISSING_INNER_HITS) <= 1 and
                     ele.relIsoR(R=0.3, dBetaFactor=0.5, allCharged=0) < 0.3]
        return electrons
    
    def process(self, event):
        self.readCollections(event.input)

        if not len(event.vertices):
            return False
        
        self.counters.counter('Tau3Mu').inc('> 0 vertex')

        event.allpf      = list(self.handles['pfcands'   ].product())
        event.losttracks = list(self.handles['losttracks'].product())
        
        event.photons    = self.buildPhotons  (self.handles['photons'  ].product(), event)
        event.muons      = self.buildMuons    (self.handles['muons'    ].product(), event)
        event.electrons  = self.buildElectrons(self.handles['electrons'].product(), event)
        
        # useful for jet cross cleaning
        event.selectedLeptons = [lep for lep in event.muons + event.electrons if lep.pt()>10.] 

        # merge the track collections
        event.alltracks      = sorted([tt for tt in event.allpf + event.losttracks if tt.charge() != 0], key = lambda x : x.pt(), reverse = True)
        
        # select tracks byt pt, eta
        event.selectedtracks = [tt for tt in event.alltracks if tt.pt()>1 and abs(tt.eta())<2.5 and abs(tt.vz() - event.vertices[0].z()) < 0.3]

        # here you need to clean from selected leptons!
        toclean = []
        for tt in event.selectedtracks:
            for mm in event.selectedLeptons:
                if deltaR2(tt, mm) < 0.001:
                    toclean.append(tt)
        
        event.selectedtracks = [tt for tt in event.selectedtracks if tt not in toclean]
                     
        # create all possible 3-track combinations out of the selected tracks
        triplets = []
        for triplet in combinations(event.selectedtracks, 3):
            if abs(sum([tt.charge() for tt in triplet]))==1:
                triplets.append(triplet)

        # create the Ds candidates 
        event.dss = [Ds(triplet) for triplet in triplets]
        
        # the 3-body mass must be within 200 MeV from the PDG value (pretty loose)
        event.dss = [ds for ds in event.dss if abs(ds.p4().mass() - m_ds) < 0.2]
        
        if not len(event.dss):
            return False
 
        # pick the best Ds, not used for now
        event.ds = self.bestDs(event.dss)
        
        if not len(event.photons):
            return False
        
        # create all the possible the W -> Ds gamma candidates  
        event.wdsgs = [WDsGamma(iw[0], iw[1]) for iw in product(event.dss, event.photons)]

        # keep only those whose mass is not totally off (+/- 15 GeV) 
        event.wdsgs = [iw for iw in event.wdsgs if abs(iw.mass() - m_w) < 15.]

        if not len(event.wdsgs):
            return False

        # pick the best W Ds Gamma, might change your mind later on
        event.wdsg = self.bestWDsGamma(event.wdsgs)
        
        return True

    def selectionSequence(self, event):

        return True


    def bestDs(self, dss):
        '''
        '''
        dss.sort(key=lambda ds : abs(ds.p4().mass() - m_ds), reverse=False)    
        return dss[0]

    def bestWDsGamma(self, wdsgs):
        '''
        Find a better idea!
        '''
        wdsgs.sort(key=lambda iw : iw.pt(), reverse=True)    
        return wdsgs[0]
        
    def testVertex(self, lepton):
        '''Tests vertex constraints, for mu'''
        return abs(lepton.dxy()) < 0.045 and abs(lepton.dz()) < 0.2
        
    def testTauVertex(self, tau):
        '''Tests vertex constraints, for tau'''
        # Just checks if the primary vertex the tau was reconstructed with
        # corresponds to the one used in the analysis
        # isPV = abs(tau.vertex().z() - tau.associatedVertex.z()) < 0.2
        isPV = abs(tau.leadChargedHadrCand().dz()) < 0.2
        return isPV

    
