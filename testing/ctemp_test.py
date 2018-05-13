import sys
sys.path.append('../')
import firemodels.continuous.temperature as ctemp
import numpy as np
import matplotlib.pyplot as plt

def temperatureFocus(M, N):
    x = np.linspace(0, 1, N)
    y = np.linspace(0, 1, M)
    X, Y = np.meshgrid(x, y)
    return 1e3*np.exp(-1000*((X-.5)**2 + (Y-.5)**2))
  
# The resolution have to be lower than discrete version for computation of F
M, N = 50, 50  

# Initial conditions
initial = temperatureFocus(M, N)


# Parameters
mu = 1/5 
T = 10
dt = 1e-3

# We have to include border conditions, for now only 
# use dirichlet f(x,y) = u(x,y) for (x,y) \in \partial\Omega
ct = ctemp.new(initial, mu, dt, T)
#pde1 = ct.solvePDE()
pde1 = ct.solveSPDE1()
#pde1 = ct.solveSPDE2()

for i in range(T):
  ct.plotTemperatures(i, pde1)
