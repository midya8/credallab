"""Finite probabilistic satisfiability and sharp probability bounds."""
__version__='0.2.0'
def __getattr__(name):
 if name=='analyze':
  from .engine import analyze
  return analyze
 if name=='verify':
  from .certificate import verify
  return verify
 if name=='analyze_decisions':
  from .decisions import analyze_decisions
  return analyze_decisions
 if name=='verify_decisions':
  from .decision_certificate import verify_decisions
  return verify_decisions
 raise AttributeError(name)
