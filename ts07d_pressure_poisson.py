#! /usr/bin/env python

from pyTS07d import ts07d,solver,params
from numpy import linspace,meshgrid,sin,cos,pi,arctan2,sqrt,vstack
from scipy import interpolate
from matplotlib import pyplot as plt

to_center = lambda A: 0.25*(A[:-1,:-1]+A[1:,:-1]+A[:-1,1:]+A[1:,1:])

if __name__ == "__main__":
    args = params.read()

    # read the data in
    x,y,jxbx,jxby = ts07d.get_data(args.xfile,args.yfile,args.jxbxfile,args.jxbyfile,xflip=args.xflip)

    # this is the cylindrical grid to which we interpolate
    rc,tc=meshgrid(linspace(args.rmin,args.rmax,args.Nr),linspace(0,2*pi,args.Nt))
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
    s = solver.solver(args.Nr-1,args.Nt-1,rcc.T,dr,dt)  # note, size reduced to number or cell centers
    s.setStencilMatrixNp()
    s.setRHSNp(divJB.T)
    pressure = s.solve()
    pressure = pressure.reshape(args.Nr-1,args.Nt-1)
    
    # fix periodic boundary for plotting
    xcc = vstack((xcc,xcc[[0],:]))
    ycc = vstack((ycc,ycc[[0],:]))
    pressure = vstack((pressure.T,pressure.T[[0],:]))*6.4e-3   # convert to nPa: j[nA/m2], B[nT], x,y[Re]
    plt.figure()
    if args.red_blue_cb:
        cmap=plt.cm.RdBu_r 
    else:
        cmap=plt.cm.viridis

    plt.pcolormesh(xcc,ycc,pressure,cmap=cmap,vmin=args.vmin,vmax=args.vmax);
    plt.colorbar().set_label('Pressure, nPa')
    plt.xlabel('X, Re')
    plt.ylabel('Y, Re')
    plt.xlim(xcc.max(),xcc.min())
    plt.ylim(ycc.max(),ycc.min())
    plt.title('rmin=%.1f, rmax=%.1f'%(args.rmin,args.rmax))
    plt.savefig(args.outPlotFile)

    # dump data file
    ts07d.save_data(args.outDataFile,xcc,ycc,pressure)
    

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
    
