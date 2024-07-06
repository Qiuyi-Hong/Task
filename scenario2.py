"""
This file contains the code for the model of each house the scenario 2. 
"""

import pyomo.environ as pyo 

model = pyo.AbstractModel(name="model for each house in scenario 2")

############################################################################
######################## Setting parameters: ###############################
############################################################################
model.T = pyo.RangeSet(1, 24, 1)


