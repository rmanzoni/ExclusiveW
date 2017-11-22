import ROOT
import math

class CompositeObject(object):
	def __init__(self, **components):
		super(self, CompositeObject).__init__()
		self._components_ = components
		#cache p4, can be expensive because ROOT
		self._p4_ = reduce( #sum does not work
			lambda x, y: x+y,
			[i.p4() for i in self._components_.itervalues()]
			)

	def __getattr__(self, attr):
		if attr in self._components_:
			return self._components_[attr]
		else:
			return super(self, CompositeObject).__getattr__(attr)

	@property
	def p4(self):
		return self._p4_
		
	@property
	def pt(self):
		return self._p4_.pt()
	
	@property
	def eta(self):
		return self._p4_.eta()
	
	@property
	def phi(self):
		return self._p4_.phi()
