import ROOT
from CMGTools.ExclusiveW.analyzers.TTBarWLNuWDsGammaTreeProducerBase import TTBarWLNuWDsGammaTreeProducerBase
from PhysicsTools.HeppyCore.utils.deltar import deltaR


class TTBarWLNuWDsGammaTreeProducer(TTBarWLNuWDsGammaTreeProducerBase):

    '''
    '''

    def declareVariables(self, setup):
        '''
        '''
        self.bookEvent(self.tree)
        self.bookWDsGamma(self.tree, 'wex')
        
    def process(self, event):
        '''
        '''
        self.readCollections(event.input)
        self.tree.reset()

        if not eval(self.skimFunction):
            return False

        self.fillEvent(self.tree, event)
        self.fillWDsGamma(self.tree, 'wex', event.wdsg)
        
        self.fillTree(event)

