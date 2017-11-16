import ROOT
from itertools import product, combinations

from PhysicsTools.Heppy.analyzers.core.Analyzer   import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.HeppyCore.utils.deltar          import deltaR, deltaR2

from CMGTools.ExclusiveW.physicsobjects.TopEx     import TopEx


class TopFinderAnalyzer(Analyzer):
    '''
    '''
    
    def process(self, event):

        # create all the W - jet pairs
        event.topexs = [TopEx(it[0], it[1]) for it in product(event.wdsgs, event.cleanJets)]
        event.topexs.sort(key = lambda itop: abs(m_top - itop.mass()))
        
        event.topex = event.topexs[0]
        
        event.wdsg = event.topex.w()
        
        # find the other top
        
        return True
