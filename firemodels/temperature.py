import numpy as np
import matplotlib.pyplot as plt
#from scipy.integrate import odeint
from scipy.interpolate import interp2d

class discrete:
  
  def __init__(self, c, T0, timesteps, A0=None, Y0=None, V0=None, b=None, maxTemp=None, Ea=None, Z=None, H=None):
    self.c = c
    self.T0 = T0
    self.timesteps = timesteps
    self.A0 = A0
    self.Y0 = Y0
    self.V0 = V0
    self.b = b
    self.maxTemp = maxTemp
    self.Ea = Ea
    self.Z = Z
    self.H = H
    
  def propagate(self, sigma1=None, sigma2=None):
    T = np.zeros((self.timesteps, self.T0.shape[0], self.T0.shape[1]))
    T[0] = self.T0    
    
    if self.A0 is None:
      for t in range(1, self.timesteps):
        grid = T[t-1]
        
        # Noises
        n1, n2 = 0, 0
      
        if sigma1 is not None: n1 = sigma1 * np.random.normal(0, 1, size=grid.shape)
        if sigma2 is not None: n2 = sigma2 * np.random.normal(0, 1, size=grid.shape)
        
        
        # Diffusion
        T[t] = (self.c + n1)*(np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) \
                + np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) - 4*grid) + grid + n2      

        # Convection
        if self.V0 is not None:
          v1, v2 = self.V0
          
          if v1 >= 0:
            T[t] -= v1*(grid - np.roll(grid, 1, axis=1)) 
          else:
            T[t] -= v1*(np.roll(grid, -1, axis=1) - grid) 
              
          if v2 >= 0:
            T[t] -= v2*(grid - np.roll(grid, 1, axis=0)) 
          else:
            T[t] -= v2*(np.roll(grid, -1, axis=0) - grid) 
        
      return T
    
    else:
      A = np.zeros((self.timesteps, self.A0.shape[0], self.A0.shape[1]))
      A[0] = self.A0
      
      Y = np.zeros((self.timesteps, self.Y0.shape[0], self.Y0.shape[1]))
      Y[0] = self.Y0
      
      fv = np.zeros_like(self.A0) 
      
      for t in range(1, self.timesteps):
        grid = T[t-1]
        east = np.roll(grid, 1, axis=0) 
        west = np.roll(grid, -1, axis=0)
        north = np.roll(grid, -1, axis=1)
        south = np.roll(grid, 1, axis=1)
        
        # Noises
        n1, n2 = 0, 0
      
        if sigma1 is not None: n1 = np.random.normal(0, sigma1, size=grid.shape)
        if sigma2 is not None: n2 = np.random.normal(0, sigma2, size=grid.shape)   

        if self.Z is not None:
    
          r = self.Z * np.exp(-self.Ea/(1e-14+T[t-1]))
      
          fv = A[t-1] * r * Y[t-1]
      
          Y[t] = Y[t-1] - fv
          
          
          T[t] = (self.c + n1)*(east + west + north + south - 4*grid) + grid \
            + fv * self.H + n2
        else:
          T[t] = (1 - A[t-1])*((self.c + n1)*(east + west + north + south - 4*grid) + grid)\
            + A[t-1]*(grid*(self.maxTemp - grid)/self.b + grid) + n2

                
        # Convection
        if self.V0 is not None:
          v1, v2 = self.V0
          
          if v1 >= 0:
            T[t] -= v1*(grid - np.roll(grid, 1, axis=1)) 
          else:
            T[t] -= v1*(np.roll(grid, -1, axis=1) - grid) 
              
          if v2 >= 0:
            T[t] -= v2*(grid - np.roll(grid, 1, axis=0)) 
          else:
            T[t] -= v2*(np.roll(grid, -1, axis=0) - grid) 
                
        tmp = np.zeros_like(self.A0)
        tmp[T[t] >= 400] = 1 # Burn trees
        tmp[Y[t] <= 1e-2] = 0 # Remove fuel burnt
        A[t] = tmp
        
        
      return T, A, Y
  
  def plotSimulation(self, t, temperatures, fuels, trees):
    plt.figure(figsize=(10, 8))
    plt.subplot(1, 3, 1)
    temp = plt.imshow(temperatures[t], origin='lower', cmap=plt.cm.jet)
    plt.title("Temperature")
    plt.colorbar(temp, fraction=0.046, pad=0.04)
    
    plt.subplot(1, 3, 2)
    tree = plt.imshow(trees[t], origin='lower', cmap=plt.cm.afmhot)
    plt.title("Burning trees")
    plt.colorbar(tree, fraction=0.046, pad=0.04)
    
    plt.subplot(1, 3, 3)
    fuel = plt.imshow(fuels[t], origin='lower', cmap=plt.cm.Oranges)
    plt.title("Fuel available")
    plt.colorbar(fuel, fraction=0.046, pad=0.04)
    
    plt.tight_layout()
    
    plt.show()
      
  def plotSimulation2(self, temperatures, fuels, trees):
    T = len(temperatures)
    for t in range(T):
      if t % 10 == 0:
        plt.figure(figsize=(10, 8))
        plt.subplot(1, 3, 1)
        temp = plt.imshow(temperatures[t], origin='lower', cmap=plt.cm.jet, 
                          vmin=np.min(temperatures), vmax=np.max(temperatures))
        plt.title("Temperature")
        plt.colorbar(temp, fraction=0.046, pad=0.04)
        
        plt.subplot(1, 3, 2)
        tree = plt.imshow(trees[t], origin='lower', cmap=plt.cm.afmhot,
                          vmin=np.min(trees), vmax=np.max(trees))
        plt.title("Burning trees")
        plt.colorbar(tree, fraction=0.046, pad=0.04)
        
        plt.subplot(1, 3, 3)
        fuel = plt.imshow(fuels[t], origin='lower', cmap=plt.cm.Oranges,
                          vmin=np.min(fuels), vmax=np.max(fuels))
        plt.title("Fuel available")
        plt.colorbar(fuel, fraction=0.046, pad=0.04)
        
        plt.tight_layout()
        
        plt.show()    
      
  
  def plotTemperatures(self, t, temperatures):
    plt.imshow(temperatures[t], origin='lower', cmap=plt.cm.jet)#, vmin=0)#, 
               #vmin=0, vmax=np.max(np.array(self.temperatures)))
    plt.colorbar()
    plt.show()
    
    

class continuous:
  
  def __init__(self, u0, mu, dt, T, b=None, maxTemp=None, A=None):
    self.u0 = u0
    self.mu = mu
    self.dt = dt
    self.T = T
    self.M, self.N = u0.shape
    self.x = np.linspace(0, 1, self.M)
    self.y = np.linspace(0, 1, self.N)
    self.t = np.linspace(0, dt*T, self.T)
    self.dx = self.x[1] - self.x[0]
    self.dy = self.y[1] - self.y[0]
    self.dt = self.t[1] - self.t[0]
    self.b = b
    self.maxTemp = maxTemp
    self.A = A
    #print("here2")
    
  
  def F(self, U, t, mu):    
    #U = U.reshape((self.M, self.N))
    W = np.zeros_like(U)
    
    # Laplacian
    #W[1:-1,1:-1] = mu*(np.diff(U[:,1:-1], n=2, axis=0) / self.dx**2 + \
    # np.diff(U[1:-1,:], n=2, axis=1) / self.dy**2)
    dx = self.dx
    dy = self.dy
    #W = mu * (np.gradient(np.gradient(U, dx, axis=0), dx, axis=0)+ \
    #  np.gradient(np.gradient(U, dy, axis=1), dy, axis=1))
    
    W = (np.roll(U,1,axis=0) + np.roll(U,-1,axis=0) +\
              np.roll(U,-1,axis=1) + np.roll(U,1,axis=1) - 4*U)/dx**2
    
    #return W.flatten() # Flatten for odeint
    return W
    
    
  # Solve PDE
  def solvePDE(self, sigma1 = None, sigma2 = None):
    
    # Method of lines
    #U = odeint(self.F, self.u0.flatten(), self.t, args=(self.mu,)) 
    
    #return U
    
    #U = np.zeros((self.T+1, self.u0.flatten().shape[0]))
    #U[0,:] = self.u0.flatten()
    #A = A.flatten()
            
    U = np.zeros((self.T+1, self.M, self.N))
    U[0] = self.u0
    
    if self.A is None:
      
      for i in range(1, self.T + 1):
          
        # Noises
        n1, n2 = 0, 0

        if sigma1 is not None: n1 = sigma1 * np.random.normal(0, self.dt, size=self.u0.shape)
        if sigma2 is not None: n2 = sigma2 * np.random.normal(0, self.dt, size=self.u0.shape)
        
        W =  self.F(U[i-1], self.t, self.mu)
        U[i] = U[i-1] + (self.mu *self.dt + np.sqrt(self.dt)*n1 ) * W + np.sqrt(self.dt)*n2
        
      return U, U
    
    else:
      A = np.zeros((self.T+1, self.M, self.N))
      A[0] = self.A
      
      for i in range(1, self.T+1):
        tmp = np.zeros((self.M, self.N))
        tmp[U[i-1] >= 400] = 1
        
        A[i] = tmp 
        
        # Noises
        n1, n2 = 0, 0

        if sigma1 is not None: n1 = sigma1 * np.random.normal(0, np.sqrt(self.dt), size=self.u0.shape)
        if sigma2 is not None: n2 = sigma2 * np.random.normal(0, np.sqrt(self.dt), size=self.u0.shape)
        
        #if sigma1 is not None: n1 = sigma1 *np.sqrt(self.dt)* np.random.normal(0, 1, size=self.u0.shape)
        #if sigma2 is not None: n2 = sigma2 * np.sqrt(self.dt)*np.random.normal(0, 1, size=self.u0.shape)
        
        W = self.F(U[i-1], self.t, self.mu)
          
        U[i] = U[i-1] + (1 - A[i])*((self.mu *self.dt + np.sqrt(self.dt)*n1 ) * W \
         + n2) + A[i]*(self.maxTemp - U[i-1])*U[i-1]*self.dt/self.b   
        
      return U, A, W
        
        

  def solveSPDE1(self, sigma):
    # Solve
    U = np.zeros((self.T+1, self.M, self.N))
    U[0] = self.u0
    
    for i in range(1, self.T+1):
        W =  self.F(U[i-1], self.t, self.mu)
        U[i] = U[i-1] + W*self.dt + sigma*np.random.normal(0, self.dt, W.shape)
    
    return U
    

  def solveSPDE2(self, sigma):
    # Solve
    U = np.zeros((self.T+1, self.M, self.N))
    U[0] = self.u0
    for i in range(1, self.T+1):
        W =  self.F(U[i-1], self.t, self.mu)
        U[i] = U[i-1] + W*self.dt + self.dt*sigma*np.random.normal(0, 1, W.shape)*W/self.mu
    
    return U
    

  def plotTemperatures(self, t, temperatures):
    fine = np.linspace(0, 1, 2*self.N)
    fu = interp2d(self.x, self.y, temperatures[t], kind='cubic')
    U = fu(fine, fine)
    #U = temperatures[t]
    plt.imshow(U, origin='lower', cmap=plt.cm.jet)
    plt.colorbar()
    plt.show()
    