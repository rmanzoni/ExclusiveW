# import dill # needed in order to serialise lambda functions, need to be installed by the user. See http://stackoverflow.com/questions/25348532/can-python-pickle-lambda-functions
import PhysicsTools.HeppyCore.framework.config as cfg
from PhysicsTools.HeppyCore.framework.config     import printComps
from PhysicsTools.HeppyCore.framework.heppy_loop import getHeppyOption
from PhysicsTools.Heppy.utils.cmsswPreprocessor  import CmsswPreprocessor
from CMGTools.RootTools.utils.splitFactor        import splitFactor

# import all analysers:
# Heppy analyzers
from PhysicsTools.Heppy.analyzers.core.JSONAnalyzer              import JSONAnalyzer
from PhysicsTools.Heppy.analyzers.core.SkimAnalyzerCount         import SkimAnalyzerCount
from PhysicsTools.Heppy.analyzers.core.EventSelector             import EventSelector
from PhysicsTools.Heppy.analyzers.objects.VertexAnalyzer         import VertexAnalyzer
from PhysicsTools.Heppy.analyzers.core.PileUpAnalyzer            import PileUpAnalyzer
from PhysicsTools.Heppy.analyzers.gen.GeneratorAnalyzer          import GeneratorAnalyzer
from PhysicsTools.Heppy.analyzers.gen.LHEWeightAnalyzer          import LHEWeightAnalyzer
         
# Tau-tau analysers         
from CMGTools.H2TauTau.proto.analyzers.TriggerAnalyzer           import TriggerAnalyzer
from CMGTools.H2TauTau.proto.analyzers.FileCleaner               import FileCleaner

# Exclusive W analysers
from CMGTools.ExclusiveW.analyzers.TTBarWLNuWDsGammaAnalyzer     import TTBarWLNuWDsGammaAnalyzer
from CMGTools.ExclusiveW.analyzers.TTBarWLNuWDsGammaTreeProducer import TTBarWLNuWDsGammaTreeProducer
from CMGTools.ExclusiveW.analyzers.LeptonSelector                import LeptonSelector
from CMGTools.ExclusiveW.analyzers.JetSelector                   import JetSelector
from CMGTools.ExclusiveW.analyzers.GammaSelector                 import GammaSelector

# import samples, signal
from CMGTools.RootTools.samples.samples_13TeV_RunIISummer16MiniAODv2 import TTJets_SingleLeptonFromTbar, TTJets_SingleLeptonFromTbar_ext, TTJets_SingleLeptonFromT, TTJets_SingleLeptonFromT_ext
from CMGTools.ExclusiveW.samples.mc_2016 import WtoDsGamma

puFileMC   = '$CMSSW_BASE/src/CMGTools/H2TauTau/data/MC_Moriond17_PU25ns_V1.root'
puFileData = '/afs/cern.ch/user/a/anehrkor/public/Data_Pileup_2016_271036-284044_80bins.root'

###################################################
###                   OPTIONS                   ###
###################################################
# Get all heppy options; set via "-o production" or "-o production=True"
# production = True run on batch, production = False (or unset) run locally
production         = getHeppyOption('production'        , False)
pick_events        = getHeppyOption('pick_events'       , False)

###################################################
###               HANDLE SAMPLES                ###
###################################################
samples = [WtoDsGamma] ##TTJets_SingleLeptonFromTbar, TTJets_SingleLeptonFromTbar_ext, TTJets_SingleLeptonFromT, TTJets_SingleLeptonFromT_ext]

for sample in samples:
    sample.triggers = ['HLT_IsoMu24_v%d'    %i for i in range(4, 5)]
    sample.triggers += ['HLT_IsoTkMu24_v%d' %i for i in range(4, 5)]

    # specify which muon should match to which filter. 
#     sample.trigger_filters = [
#         (lambda triplet : triplet.mu1(), ['hltTau3muTkVertexFilter']),
#         (lambda triplet : triplet.mu2(), ['hltTau3muTkVertexFilter']),
#         (lambda triplet : triplet.mu3(), ['hltTau3muTkVertexFilter']),
#     ]
    sample.splitFactor = splitFactor(sample, 1e5)
    sample.puFileData = puFileData
    sample.puFileMC   = puFileMC

selectedComponents = samples

###################################################
###                  ANALYSERS                  ###
###################################################
eventSelector = cfg.Analyzer(
    EventSelector,
    name='EventSelector',
    toSelect=[]
)

lheWeightAna = cfg.Analyzer(
    LHEWeightAnalyzer, name="LHEWeightAnalyzer",
    useLumiInfo=False
)

jsonAna = cfg.Analyzer(
    JSONAnalyzer,
    name='JSONAnalyzer',
)

skimAna = cfg.Analyzer(
    SkimAnalyzerCount,
    name='SkimAnalyzerCount'
)

triggerAna = cfg.Analyzer(
    TriggerAnalyzer,
    name='TriggerAnalyzer',
    addTriggerObjects=True,
    requireTrigger=True,
    usePrescaled=False
)

vertexAna = cfg.Analyzer(
    VertexAnalyzer,
    name='VertexAnalyzer',
    fixedWeight=1,
    keepFailingEvents=True,
    verbose=False
)

pileUpAna = cfg.Analyzer(
    PileUpAnalyzer,
    name='PileUpAnalyzer',
    true=True
)

genAna = GeneratorAnalyzer.defaultConfig
genAna.allGenTaus = True # save in event.gentaus *ALL* taus, regardless whether hadronic / leptonic decay

leptons = cfg.Analyzer(
    LeptonSelector,
    name='TTBarWLNuWDsGammaAnalyzer',
#     trigger_match=True,
    trigger_match=False,
#     useMVAmet=True,
)

treeProducer = cfg.Analyzer(
    TTBarWLNuWDsGammaTreeProducer,
    name='TTBarWLNuWDsGammaTreeProducer',
)

photons = cfg.Analyzer(
	GammaSelector	
)

# see SM HTT TWiki
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/SMTauTau2016#Jet_Energy_Corrections
jetAna = cfg.Analyzer(
    JetSelector,
    name              = 'JetAnalyzer',
    jetCol            = 'slimmedJets',
		toClean           = ['tightLeptons', 'gammas'],
    jerCorr           = False,
    puJetIDDisc       = 'pileupJetId:fullDiscriminant',
    recalibrateJets   = False, #True, #FIXME
    applyL2L3Residual = 'MC',
    mcGT              = '80X_mcRun2_asymptotic_2016_TrancheIV_v8',
    dataGT            = '80X_dataRun2_2016SeptRepro_v7',
    #jesCorr = 1., # Shift jet energy scale in terms of uncertainties (1 = +1 sigma)
)

fileCleaner = cfg.Analyzer(
    FileCleaner,
    name='FileCleaner'
)

###################################################
###                  SEQUENCE                   ###
###################################################
sequence = cfg.Sequence([
    lheWeightAna,
    jsonAna,
    skimAna,
    genAna,
    triggerAna, # First analyser that applies selections
    vertexAna,
    pileUpAna,
    leptons,
		photons,
    jetAna,
    treeProducer,
])

###################################################
###            SET BATCH OR LOCAL               ###
###################################################
if not production:
    comp                 = TTJets_SingleLeptonFromTbar
    selectedComponents   = [comp]
    comp.splitFactor     = 1
    comp.fineSplitFactor = 1
    comp.files           = comp.files[:1]
#     comp.files = [
#        'file:/afs/cern.ch/work/m/manzoni/diTau2015/CMSSW_9_2_2_minimal_recipe/src/RecoMET/METPUSubtraction/test/output.root',
# #        'root://xrootd.unl.edu//store/data/Run2016B/SingleMuon/MINIAOD/PromptReco-v1/000/272/760/00000/68B88794-7015-E611-8A92-02163E01366C.root',
#     ]

preprocessor = None

# the following is declared in case this cfg is used in input to the
# heppy.py script
from PhysicsTools.HeppyCore.framework.eventsfwlite import Events
config = cfg.Config(
    components   = selectedComponents,
    sequence     = sequence,
    services     = [],
    preprocessor = preprocessor,
    events_class = Events
)

printComps(config.components, True)
