import math

import numpy as np
from itertools import combinations, product
# from copy import deepcopy as dc

from PhysicsTools.HeppyCore.utils.deltar import deltaR, deltaPhi
from PhysicsTools.Heppy.physicsobjects.PhysicsObjects import Muon
from CMGTools.ExclusiveW.physicsobjects.Ds import Ds
from ROOT import TVector3, Math

class WDsGamma(object):
    ''' 
    '''
    def __init__(self, ds, gamma):
        self.Ds = ds
        self.Gamma  = gamma    
        
    def charge(self):
        return self.ds.charge()
    
    def ds(self):
        return self.Ds

    def kappa_even(self):
        return self.ds().kappa_even()
        
    def kappa_odd(self):
        return self.ds().kappa_odd()

    def pi(self):
        return self.ds().pi()

    def gamma(self):
        return self.Gamma

    def p4(self):
        # specify which gamma p4 is needed, it turns out it should be regression1
        # http://cmsdoxygen.web.cern.ch/cmsdoxygen/CMSSW_9_4_0_pre1/doc/html/d5/d35/classreco_1_1Photon.html#a2c53313bb6dfc43fa1d97c0a92b8d970
        # https://github.com/cms-analysis/flashgg/blob/master/DataFormats/interface/Photon.h#L76
        return self.ds().p4() + self.gamma().p4(2)

    def pt(self):
        return self.p4().pt()

    def eta(self):
        return self.p4().eta()

    def phi(self):
        return self.p4().phi()

    def mass(self):
        return self.p4().mass()

    def dPhiDsGamma(self):
        return deltaPhi(self.ds().phi(), self.gamma().phi())

    def dRDsGamma(self):
        return deltaR(self.ds().p4(), self.gamma().p4(2))














