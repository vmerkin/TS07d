import ts07d,solver
from numpy import linspace,meshgrid,sin,cos,pi,arctan2,sqrt,vstack
from scipy import interpolate
from matplotlib import pyplot as plt

xfile = '/Users/merkivg1/work/TS07d_pressure/xOutputFile.txt'
yfile = '/Users/merkivg1/work/TS07d_pressure/yOutputFile.txt'
jxbxfile  = '/Users/merkivg1/work/TS07d_pressure/jxbxOutputFile.txt'
jxbyfile  = '/Users/merkivg1/work/TS07d_pressure/jxbyOutputFile.txt'
Nr = 100
Nt = 180
rmax = 9.9
rmin = 1.6

to_center = lambda A: 0.25*(A[:-1,:-1]+A[1:,:-1]+A[:-1,1:]+A[1:,1:])

if __name__ == "__main__":
    # read the data in
    x,y,jxbx,jxby = ts07d.get_data(xfile,yfile,jxbxfile,jxbyfile)

    # this is the cylindrical grid to which we interpolate
    rc,tc=meshgrid(linspace(rmin,rmax,Nr),linspace(0,2*pi,Nt))
    xc,yc = rc*cos(tc),rc*sin(tc)

    # will also need cell centers for these
    rcc = to_center(rc)
    tcc = to_center(tc)
    xcc = to_center(xc)
    ycc = to_center(yc)

    # interpolate
    fx = interpolate.RectBivariateSpline(y[:,0],x[0,:],jxbx,kx=1,ky=1)
    jxbx_c = fx.ev(yc,xc)

    fy = interpolate.RectBivariateSpline(y[:,0],x[0,:],jxby,kx=1,ky=1)
    jxby_c = fy.ev(yc,xc)

    # rotate to cylindrical
    jxbr_c = jxbx_c*cos(tc)+jxby_c*sin(tc)
    jxbt_c =-jxbx_c*sin(tc)+jxby_c*cos(tc)

    # divergence
    dr = rc[0,1]-rc[0,0] # FIXME: assuming uniform grid
    dt = tc[1,0]-tc[0,0] # FIXME: assuming uniform grid

    # r component
    tmp = rc*jxbr_c
    djr = 1/dr*(tmp[:,1:]-tmp[:,:-1])

    # t component
    djt = 1/dt*(jxbt_c[1:,:]-jxbt_c[:-1,:])
    
    # interpolate to cell centers
    djr = 0.5*(djr[:-1,:]+djr[1:,:])
    djt = 0.5*(djt[:,:-1]+djt[:,1:])

    # divergence
    divJB = 1/rcc*(djr+djt)
    
    # Poisson solver
    s = solver.solver(Nr-1,Nt-1,rcc.T,dr,dt)  # note, size reduced to number or cell centers
    s.setStencilMatrixNp()
    s.setRHSNp(divJB.T)
    pressure = s.solve()
    pressure = pressure.reshape(Nr-1,Nt-1)
    
    # fix periodic boundary for plotting
    xcc = vstack((xcc,xcc[[0],:]))
    ycc = vstack((ycc,ycc[[0],:]))
    pressure = vstack((pressure.T,pressure.T[[0],:]))
    plt.figure()
    plt.pcolormesh(xcc,ycc,pressure);plt.colorbar().set_label('Pressure')
    plt.xlabel('X, Re')
    plt.ylabel('Y, Re')
    

    # plotting 

    # plt.figure()
    # plt.pcolormesh(x,y,jxbx);plt.colorbar()

    # plt.figure()
    # plt.pcolormesh(xc,yc,jxbx_c);plt.colorbar()

    # plt.figure()
    # plt.pcolormesh(xc,yc,jxby_c);plt.colorbar()

    # plt.figure()
    # plt.pcolormesh(xc,yc,jxbr_c);plt.colorbar()

    # plt.figure()
    # plt.pcolormesh(xc,yc,jxbt_c);plt.colorbar()
    
