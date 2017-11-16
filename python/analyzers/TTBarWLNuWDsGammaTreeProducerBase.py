from PhysicsTools.Heppy.analyzers.core.TreeAnalyzerNumpy import TreeAnalyzerNumpy
from CMGTools.ExclusiveW.analyzers.TreeVariables import event_vars, WDsGamma_vars

class TTBarWLNuWDsGammaTreeProducerBase(TreeAnalyzerNumpy):

    '''
    '''

    def __init__(self, *args):
        super(TTBarWLNuWDsGammaTreeProducerBase, self).__init__(*args)
        self.skimFunction = 'True'
        if hasattr(self.cfg_ana, 'skimFunction'):
            self.skimFunction = self.cfg_ana.skimFunction

    def var(self, tree, varName, type=float):
        tree.var(varName, type)

    def vars(self, tree, varNames, type=float):
        for varName in varNames:
            self.var(tree, varName, type)

    def fill(self, tree, varName, value):
        tree.fill(varName, value)

    def fillVars(self, tree, varNames, obj):
        '''Fills vars that are attributes of the passed object.
        Fills -999. if object doesn't have attribute'''
        for varName in varNames:
            tree.fill(varName, getattr(obj, varName, -999.))

    def fillTree(self, event):
        if eval(self.skimFunction):
            self.tree.tree.Fill()

    def bookGeneric(self, tree, var_list, obj_name=None):
        for var in var_list:
            names = [obj_name, var.name] if obj_name else [var.name]
            self.var(tree, '_'.join(names), var.type)

    def fillGeneric(self, tree, var_list, obj, obj_name=None):
        for var in var_list:
            names = [obj_name, var.name] if obj_name else [var.name]
            try:
                self.fill(tree, '_'.join(names), var.function(obj))
            except TypeError:
                print 'Problem in filling value into tree'
                print var.name, var.function(obj), obj
                raise

    def declareVariables(self, setup):
        ''' Declare all variables here in derived calss
        '''
        pass

    def process(self, event):
        ''' Fill variables here in derived class

        End implementation with self.fillTree(event)
        '''
        # needed when doing handle.product(), goes back to
        # PhysicsTools.Heppy.analyzers.core.Analyzer
        self.tree.reset()

        if not eval(self.skimFunction):
            return False

        # self.fillTree(event)

    # event
    def bookEvent(self, tree):
        self.bookGeneric(tree, event_vars)

    def fillEvent(self, tree, event):
        self.fillGeneric(tree, event_vars, event)

    # WDsGamma
    def bookWDsGamma(self, tree, p_name):
        self.bookGeneric(tree, WDsGamma_vars, p_name)

    def fillWDsGamma(self, tree, p_name, particle):
        self.fillGeneric(tree, WDsGamma_vars, particle, p_name)
