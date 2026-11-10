"""Finite probabilistic satisfiability and sharp probability bounds."""
__version__='0.1.0'
def __getattr__(name):
 if name=='analyze':
  from .engine import analyze
  return analyze
 if name=='verify':
  from .certificate import verify
  return verify
 raise AttributeError(name)
