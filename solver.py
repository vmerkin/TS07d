from numpy import sin,cos,arccos,mat,dot,repeat,multiply,tan,pi,sqrt,append,linspace,meshgrid,zeros,arange,ones_like,array,roll,hstack,newaxis,isscalar,ones,vstack,zeros_like
import scipy
from scipy import interpolate
from scipy.sparse import linalg
from scipy.sparse import coo_matrix

class solver():
    def __init__(self,Nr,Nt,r,dr,dt):
        (self.Nr,self.Nt) = Nr,Nt
        self.r = r
        self.dr = dr
        self.dt = dt

    def _K(self,I,J):
        # Clean, elegant and pythonic
        return I[:,newaxis]*self.Nt+J if not isscalar(I) else I*self.Nt+J
        
    def _defineInnerBlock(self,Nr,Nt):
        return arange(1,Nr-1),arange(0,Nt)

    def setStencilMatrixNp(self):
        # some aliases for brevity
        K = self._K
        Nr = self.Nr
        Nt = self.Nt
        dt = self.dt
        dr = self.dr
        r  = self.r

        ############ inner block ############
        (I,J) = self._defineInnerBlock(Nr,Nt)

        ijij   = -2.*(1/dr**2 + 1./(r[I,:]*dt)**2)*ones_like(r[I,:])
        ijip1j = 1/dr*(1/dr+1/2./r[I,:])*ones_like(r[I,:])
        ijim1j = 1/dr*(1/dr-1/2./r[I,:])*ones_like(r[I,:])
        ijijp1 = 1/(r[I,:]*dt)**2*ones_like(r[I,:])
        ijijm1 = 1/(r[I,:]*dt)**2*ones_like(r[I,:])
    
        Kij   = K(I,J)
        Kip1j = K(I+1,J)
        Kim1j = K(I-1,J)
        Kijp1 = K(I,(J+1)%Nt)
        Kijm1 = K(I,(J-1)%Nt)
        ############ inner block ############

        data = hstack(
            (ijij.ravel(),
             ijip1j.ravel(),
             ijim1j.ravel(),
             ijijp1.ravel(),
             ijijm1.ravel(),
             ones(Nt),    # inner boundary
             ones(Nt))    # outer boundary
        )
        
        II = hstack(
            (Kij.ravel(),
             Kij.ravel(),
             Kij.ravel(),
             Kij.ravel(),
             Kij.ravel(),
             K(0,J),     # inner boundary
             K(Nr-1,J),  # outer boundary
         )
        )

        JJ = hstack(
            (Kij.ravel(),
             Kip1j.ravel(),
             Kim1j.ravel(),
             Kijp1.ravel(),
             Kijm1.ravel(),
             K(0,J),    # inner boundary
             K(Nr-1,J), # low lat boundary
         )
        )
        
        self.data = data
        self.I = II
        self.J = JJ

    def setRHSNp(self,S):
        """ Set the RHS for the matrix equation.
        
        Parameters:
        S -- the source term (i.e., radial current)
        """
        Nt = self.Nt
        Nr = self.Nr
        (I,J) = self._defineInnerBlock(Nr,Nt)

        # Right hand side
        RHS = zeros(Nt*Nr)
        RHS[self._K(I,J)] = S[I,:] # inner block
        # the rest are zeros

        self.RHS = RHS

    def solve(self):
        Nr = self.Nr
        Nt = self.Nt
        M = coo_matrix( (self.data,(self.I,self.J)),shape=(Nr*Nt,Nr*Nt) )
        p=scipy.sparse.linalg.spsolve(M.tocsc(),self.RHS)
        return (p)
