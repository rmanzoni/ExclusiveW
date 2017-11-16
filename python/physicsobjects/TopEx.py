import math

import numpy as np
from itertools import combinations, product
# from copy import deepcopy as dc

from PhysicsTools.HeppyCore.utils.deltar import deltaR, deltaPhi
from ROOT import TVector3, Math

global m_top ; m_top = 173.1 # GeV

class TopEx(object):
    ''' 
    '''
    def __init__(self, w, jet):
        self.Jet = jet
        self.W   = w

    def jet(self):
        return self.Jet

    def w(self):
        return self.W
           
    def p4(self):
        return self.jet().p4() + self.w().p4()
                
    def pt(self):
        return self.p4().pt()

    def eta(self):
        return self.p4().eta()

    def phi(self):
        return self.p4().phi()

    def mass(self):
        return self.p4().mass()

    def dRWJet(self):
        return deltaR(self.jet().p4(), self.w().p4())

    def dPhiWJet(self):
        return deltaPhi(self.jet().phi(), self.w().phi())
