"""
This file contains the code for the model of each house the scenario 2. 
"""

import pyomo.environ as pyo 

model = pyo.AbstractModel(name="model for each house in scenario 2")

############################################################################
######################## Setting parameters: ###############################
############################################################################
model.T = pyo.RangeSet(1, 48, 1)
model.H = pyo.RangeSet(1, 3, 1)

# electric power demand of the house in kW
model.d = pyo.Param(model.H, model.T, mutable=True)

# electricity import price in p/kWh
model.pi_import = pyo.Param(model.T, mutable=True)

# electricity export price in p/kWh
model.pi_export = pyo.Param(model.T, mutable=True)

# Energy storage params:
model.c = pyo.Param(model.H)
model.eta_c = pyo.Param(model.H)
model.eta_d = pyo.Param(model.H)
model.epsilon = pyo.Param(model.H) # Self-discharge rate
model.E_min = pyo.Param(model.H)
model.E_max = pyo.Param(model.H)
model.E_init = pyo.Param(model.H)
model.p_c_min = pyo.Param(model.H) 
model.p_c_max = pyo.Param(model.H)
model.p_d_min = pyo.Param(model.H)
model.p_d_max = pyo.Param(model.H)
model.delta_t = pyo.Param()

# PV generation in kW
model.q_pv = pyo.Param(model.H, model.T, mutable=True)

# P2P market params:
model.q_min = pyo.Param()
model.q_max = pyo.Param()

############################################################################
######################## Setting decision variables: ####################### 
############################################################################

# Energy storage vars:
model.p_c = pyo.Var(model.H, model.T)
model.p_d = pyo.Var(model.H, model.T)
model.E = pyo.Var(model.H, model.T)
model.gamma_c = pyo.Var(model.H, model.T, within=pyo.Boolean)
model.gamma_d = pyo.Var(model.H, model.T, within=pyo.Boolean)

# electricity volume imported from the grid in kWh
model.q_import = pyo.Var(model.H, model.T, within=pyo.NonNegativeReals)

# electricity volume exported to the grid in kWh
model.q_export = pyo.Var(model.H, model.T, within=pyo.NonNegativeReals)

# electricity volume bought from the P2P market in kWh
model.q_buy = pyo.Var(model.H, model.T, within=pyo.NonNegativeReals)

# electricity volume sold to the P2P market in kWh
model.q_sell = pyo.Var(model.H, model.T, within=pyo.NonNegativeReals)

# binary variable to indicate if the house is buying electricity from the P2P market
model.sigma_buy = pyo.Var(model.H, model.T, within=pyo.Boolean)
model.sigma_sell = pyo.Var(model.H, model.T, within=pyo.Boolean)

############################################################################
######################## Setting constraints: ############################## 
############################################################################

# Energy storage constraints:
def energyConstr(model, h, t):
    if t == 1:
        return model.E[h, t] == model.E_init[h] + model.eta_c[h] * model.p_c[h, t] * model.delta_t - (1/model.eta_d[h]) * model.p_d[h, t] * model.delta_t - model.epsilon[h] * model.delta_t
    else:
        return model.E[h, t] == model.E[h, t-1] + model.eta_c[h] * model.p_c[h, t] * model.delta_t - (1/model.eta_d[h]) * model.p_d[h, t] * model.delta_t - model.epsilon[h] * model.delta_t

model.constr1 = pyo.Constraint(model.H, model.T, rule=energyConstr)

def energyMax(model, h, t):
    return model.E[h, t] <= model.E_max[h] 

model.constr2 = pyo.Constraint(model.H, model.T, rule=energyMax)

def energyMin(model, h, t):
    return model.E[h, t] >= model.E_min[h] 

model.constr3 = pyo.Constraint(model.H, model.T, rule=energyMin)

def energyEquivalence(model, h):
    return model.E_init[h] == model.E[h, 48]

model.constr4 = pyo.Constraint(model.H, rule=energyEquivalence)

def powerChargeMax(model, h, t):
    return model.p_c[h, t] <= model.gamma_c[h, t] * model.p_c_max[h] 

model.constr5 = pyo.Constraint(model.H, model.T, rule=powerChargeMax)

def powerChargeMin(model, h, t):
    return model.p_c[h, t] >= model.gamma_c[h, t] * model.p_c_min[h] 

model.constr6 = pyo.Constraint(model.H, model.T, rule=powerChargeMin)

def powerDischargeMax(model, h, t):
    return model.p_d[h, t] <= model.gamma_d[h, t] * model.p_d_max[h] 

model.constr7 = pyo.Constraint(model.H, model.T, rule=powerDischargeMax)

def powerDischargeMin(model, h, t):
    return model.p_d[h, t] >= model.gamma_d[h, t] * model.p_d_min[h] 

model.constr8 = pyo.Constraint(model.H, model.T, rule=powerDischargeMin)

def gammaConstr(model, h, t):
    return model.gamma_c[h, t] + model.gamma_d[h, t] <= 1 

model.constr9 = pyo.Constraint(model.H, model.T, rule=gammaConstr)

def p2pBuyMin(model, h, t):
    return model.q_buy[h, t] >= model.sigma_buy[h, t] * model.q_min * model.delta_t

model.constr10 = pyo.Constraint(model.H, model.T, rule=p2pBuyMin)

def p2pBuyMax(model, h, t):
    return model.q_buy[h, t] <= model.sigma_buy[h, t] * model.q_max * model.delta_t

model.constr11 = pyo.Constraint(model.H, model.T, rule=p2pBuyMax) 

def p2pSellMin(model, h, t):
    return model.q_sell[h, t] >= model.sigma_sell[h, t] * model.q_min * model.delta_t

model.constr12 = pyo.Constraint(model.H, model.T, rule=p2pSellMin)

def p2pSellMax(model, h, t):
    return model.q_sell[h, t] <= model.sigma_sell[h, t] * model.q_max * model.delta_t

model.constr13 = pyo.Constraint(model.H, model.T, rule=p2pSellMax) 

def sigmaConstr(model, h, t):
    return model.sigma_buy[h, t] + model.sigma_sell[h, t] <= 1

model.constr14 = pyo.Constraint(model.H, model.T, rule=sigmaConstr)

# Power balance constraints:
def powerBalance(model, h, t):
    return model.d[h, t] * model.delta_t + model.p_c[h, t] * model.delta_t + model.q_export[h, t] + model.q_sell[h, t] == model.p_d[h, t] * model.delta_t + model.q_pv[h, t] * model.delta_t + model.q_import[h, t] + model.q_buy[h, t]

model.constr15 = pyo.Constraint(model.H, model.T, rule=powerBalance)

# P2P market constraints:
def p2pMarket(model, t):
    return sum(model.q_buy[h, t] for h in model.H) == sum(model.q_sell[h, t] for h in model.H)

model.constr16 = pyo.Constraint(model.T, rule=p2pMarket)


############################################################################
######################## Setting objective function: ####################### 
############################################################################

def ObjectiveFuction(model):
    total = 0 
    for h in model.H:
        for t in model.T:
            total += model.pi_import[t] * model.q_import[h, t] - model.pi_export[t] * model.q_export[h, t] + model.c[h] * (model.p_c[h, t] + model.p_d[h, t]) * model.delta_t
    return total

model.obj = pyo.Objective(rule=ObjectiveFuction, sense=pyo.minimize)


# Add a suffix for duals
model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT_EXPORT)