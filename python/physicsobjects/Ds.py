import math

import numpy as np
from itertools import combinations, product
# from copy import deepcopy as dc

from PhysicsTools.HeppyCore.utils.deltar import deltaR, deltaPhi
from ROOT import TVector3, Math

global m_k   ; m_k   = 0.493677   # GeV
global m_pi  ; m_pi  = 0.13957061 # GeV
global m_ds  ; m_ds  = 1.96828    # GeV
global m_phi ; m_phi = 1.0195     # GeV

class Ds(object):
    ''' 
    '''
    def __init__(self, tracks):
        self.tracks = tracks
        self._assignHypothesis()

    def _assignHypothesis(self):
        '''
        Find the track with odd sign, that must be one of the K,
        then try the two pi K, K pi combination and choose the one that returns the mass
        closest to the Ds.
        '''
        try:
            self.k_odd = [tt for tt in self.tracks if np.sign(tt.charge())!=np.sign(self.charge())][0]
        except:
            import pdb ; pdb.set_trace()
        
        self.k_odd.setMass(m_k)
        
        others = [tt for tt in self.tracks if tt != self.k_odd]
    
        pi1         = others[0]
        kappa_even1 = others[1]
        
        pi1        .setMass(m_pi)    
        kappa_even1.setMass(m_k )    
        
        deltaMass1 = abs(m_ds - (self.k_odd.p4() + kappa_even1.p4() + pi1.p4()).M()) 

        pi2         = others[1]
        kappa_even2 = others[0]
        
        pi2        .setMass(m_pi)    
        kappa_even2.setMass(m_k )    
        
        deltaMass2 = abs(m_ds - (self.k_odd.p4() + kappa_even2.p4() + pi2.p4()).M()) 
                  
        if deltaMass1 < deltaMass2:
            self.k_even = kappa_even1
            self.pion   = pi1

        else:
            self.k_even = kappa_even2
            self.pion   = pi2

    
    def p4(self):
        return self.kappa_even().p4() + self.kappa_odd().p4() + self.pi().p4()
    
    def kappa_even(self):
        return self.k_even
        
    def kappa_odd(self):
        return self.k_odd

    def pi(self):
        return self.pion
 
    def phi_resonance(self):
        return self.kappa_even().p4() + self.kappa_odd().p4()
    
    def has_phi(self, width=20):
        '''
        delta mass < widths (in MeV)
        '''
        return abs(self.phi_resonance().mass() - m_phi) < 0.001 * width
        
    def charge(self):
        return sum([tt.charge() for tt in self.tracks])

    def pt(self):
        return self.p4().pt()

    def eta(self):
        return self.p4().eta()

    def phi(self):
        return self.p4().phi()

    def mass(self):
        return self.p4().mass()
