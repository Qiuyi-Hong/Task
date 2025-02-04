"""
This file contains the code for the model of each house the scenario 1. 
"""

import pyomo.environ as pyo 

model = pyo.AbstractModel(name="model for each house in scenario 1")

############################################################################
######################## Setting parameters: ###############################
############################################################################
model.T = pyo.RangeSet(1, 48, 1)

# electric power demand of the house in kW
model.d = pyo.Param(model.T, mutable=True)

# electricity import price in p/kWh
model.pi_import = pyo.Param(model.T, mutable=True)

# electricity export price in p/kWh
model.pi_export = pyo.Param(model.T, mutable=True)

# Energy storage params:
model.c = pyo.Param()
model.eta_c = pyo.Param()
model.eta_d = pyo.Param()
model.epsilon = pyo.Param() # Self-discharge rate
model.E_min = pyo.Param()
model.E_max = pyo.Param()
model.E_init = pyo.Param()
model.p_c_min = pyo.Param() 
model.p_c_max = pyo.Param()
model.p_d_min = pyo.Param()
model.p_d_max = pyo.Param()
model.delta_t = pyo.Param()

# PV generation in kW
model.q_pv = pyo.Param(model.T, mutable=True)

############################################################################
######################## Setting decision variables: ####################### 
############################################################################

# Energy storage vars:
model.p_c = pyo.Var(model.T)
model.p_d = pyo.Var(model.T)
model.E = pyo.Var(model.T)
model.gamma_c = pyo.Var(model.T, within=pyo.Boolean)
model.gamma_d = pyo.Var(model.T, within=pyo.Boolean)

# electricity volume imported from the grid in kWh
model.q_import = pyo.Var(model.T, within=pyo.NonNegativeReals)

# electricity volume exported to the grid in kWh
model.q_export = pyo.Var(model.T, within=pyo.NonNegativeReals)

############################################################################
######################## Setting constraints: ############################## 
############################################################################

# Energy storage constraints:
def energyConstr(model, t):
    if t == 1:
        return model.E[t] == model.E_init + model.eta_c * model.p_c[t] * model.delta_t - (1/model.eta_d) * model.p_d[t] * model.delta_t - model.epsilon * model.delta_t
    else:
        return model.E[t] == model.E[t-1] + model.eta_c * model.p_c[t] * model.delta_t - (1/model.eta_d) * model.p_d[t] * model.delta_t - model.epsilon * model.delta_t

model.constr1 = pyo.Constraint(model.T, rule=energyConstr)

def energyMax(model, t):
    return model.E[t] <= model.E_max 

model.constr2 = pyo.Constraint(model.T, rule=energyMax)

def energyMin(model, t):
    return model.E[t] >= model.E_min 

model.constr3 = pyo.Constraint(model.T, rule=energyMin)

def energyEquivalence(model):
    return model.E_init == model.E[48]

model.constr4 = pyo.Constraint(rule=energyEquivalence)

def powerChargeMax(model, t):
    return model.p_c[t] <= model.gamma_c[t] * model.p_c_max 

model.constr5 = pyo.Constraint(model.T, rule=powerChargeMax)

def powerChargeMin(model, t):
    return model.p_c[t] >= model.gamma_c[t] * model.p_c_min 

model.constr6 = pyo.Constraint(model.T, rule=powerChargeMin)

def powerDischargeMax(model, t):
    return model.p_d[t] <= model.gamma_d[t] * model.p_d_max 

model.constr7 = pyo.Constraint(model.T, rule=powerDischargeMax)

def powerDischargeMin(model, t):
    return model.p_d[t] >= model.gamma_d[t] * model.p_d_min 

model.constr8 = pyo.Constraint(model.T, rule=powerDischargeMin)

def gammaConstr(model, t):
    return model.gamma_c[t] + model.gamma_d[t] <= 1 

model.constr9 = pyo.Constraint(model.T, rule=gammaConstr)

# Power balance constraints:
def powerBalance(model, t):
    return model.d[t] * model.delta_t + model.p_c[t] * model.delta_t + model.q_export[t] == model.p_d[t] * model.delta_t + model.q_pv[t] * model.delta_t + model.q_import[t]

model.constr10 = pyo.Constraint(model.T, rule=powerBalance)

############################################################################
######################## Setting objective function: ####################### 
############################################################################

def ObjectiveFuction(model):
    total = 0 
    for t in model.T:
        total += model.pi_import[t] * model.q_import[t] - model.pi_export[t] * model.q_export[t] + model.c * (model.p_c[t] + model.p_d[t]) * model.delta_t
    return total

model.obj = pyo.Objective(rule=ObjectiveFuction, sense=pyo.minimize)