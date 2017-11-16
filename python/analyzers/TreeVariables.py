import ROOT

from PhysicsTools.HeppyCore.utils.deltar import deltaR, deltaPhi

class Variable():
    def __init__(self, name, function=None, type=float):
        self.name = name
        self.function = function
        if function is None:
            # Note: works for attributes, not member functions
            self.function = lambda x : getattr(x, self.name, -999.) 
        self.type = type

def default():
    return -999.

# event variables
event_vars = [
    Variable('run'                                    , type=int                                                                                                  ),
    Variable('lumi'                                   , type=int                                                                                                  ),
    Variable('event'                                  , lambda ev : ev.eventId, type=int                                                                          ),
    Variable('bx'                                     , lambda ev : (ev.input.eventAuxiliary().bunchCrossing() * ev.input.eventAuxiliary().isRealData()), type=int),
    Variable('orbit_number'                           , lambda ev : (ev.input.eventAuxiliary().orbitNumber() * ev.input.eventAuxiliary().isRealData()), type=int  ),
    Variable('is_data'                                , lambda ev : ev.input.eventAuxiliary().isRealData(), type=int                                              ),
    Variable('nPU'                                    , lambda ev : -99 if getattr(ev, 'nPU', -1) is None else getattr(ev, 'nPU', -1)                             ),
    Variable('rho'                                    , lambda ev : ev.rho                                                                                        ),
    Variable('Flag_HBHENoiseFilter'                   , type=int                                                                                                  ),
    Variable('Flag_HBHENoiseIsoFilter'                , type=int                                                                                                  ),
    Variable('Flag_EcalDeadCellTriggerPrimitiveFilter', type=int                                                                                                  ),
    Variable('Flag_goodVertices'                      , type=int                                                                                                  ),
    Variable('Flag_eeBadScFilter'                     , type=int                                                                                                  ),
    Variable('Flag_globalTightHalo2016Filter'         , type=int                                                                                                  ),
    Variable('passBadMuonFilter'                      , type=int                                                                                                  ),
    Variable('passBadChargedHadronFilter'             , type=int                                                                                                  ),
    Variable('n_vtx'                                  , lambda ev : len(ev.goodVertices), type=int                                                                ),
    Variable('weight'                                 , lambda ev : ev.eventWeight, type=float                                                                    ),
    Variable('puweight'                               , lambda ev : ev.eventWeight, type=float                                                                    ),
]

# WDsGamma variables
WDsGamma_vars = [
    Variable('pt'                                , lambda cand : cand.pt()                              ),
    Variable('eta'                               , lambda cand : cand.eta()                             ),
    Variable('phi'                               , lambda cand : cand.phi()                             ),
    Variable('mass'                              , lambda cand : cand.mass()                            ),
    Variable('dphi_ds_gamma'                     , lambda cand : cand.dPhiDsGamma()                     ),
    Variable('dr_ds_gamma'                       , lambda cand : cand.dRDsGamma()                       ),
    Variable('ds_pt'                             , lambda cand : cand.ds().pt()                         ),
    Variable('ds_eta'                            , lambda cand : cand.ds().eta()                        ),
    Variable('ds_phi'                            , lambda cand : cand.ds().phi()                        ),
    Variable('ds_mass'                           , lambda cand : cand.ds().mass()                       ),
    Variable('ds_has_phi'                        , lambda cand : cand.ds().has_phi()          , type=int),
    Variable('gamma_pt'                          , lambda cand : cand.gamma().pt()                      ),
    Variable('gamma_eta'                         , lambda cand : cand.gamma().eta()                     ),
    Variable('gamma_phi'                         , lambda cand : cand.gamma().phi()                     ),
    Variable('gamma_mass'                        , lambda cand : cand.gamma().mass()                    ),
]

