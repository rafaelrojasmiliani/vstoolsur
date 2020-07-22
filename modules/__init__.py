import sys
import os

modpath = os.path.dirname(os.path.abspath(__file__))+'/vsdk'
sys.path.append(str(modpath))
import vsdk.vsdk
import vsurt.urmsgs.urmsgs 
import vsurt.urdk.urdksym
#
#modpath = pathlib.Path(pwd, 'modules', 'trjserver', 'src')
#sys.path.append(str(modpath))
#
#modpath = pathlib.Path(pwd, 'modules', 'vstoolsur')
#sys.path.append(str(modpath))
#
#modpath = pathlib.Path(pwd, 'modules', 'vstoolsur', 'vsdk')
#sys.path.append(str(modpath))
#
#from vsurt.urdk.urdk import cUrdk
#
#from gsplines.gspline import cSplineCalc
#from gsplines.linspline import cSplineCalc_2 as cBrokenLines
#from gsplines.basis1010 import cBasis1010
#from gsplines.basis1000 import cBasis1000
#from opttrj.cost1010 import cCost1010
#from opttrj.opttrj1010 import opttrj1010
#from constraints.constraintscontainer import cCostraintsContainer
#from constraints.constraints import cAffineBilateralConstraint
#import matplotlib.pyplot as plt
#import numpy as np
