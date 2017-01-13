from numpy import loadtxt,meshgrid,sqrt,savetxt,vstack
import numpy.ma as ma

def get_data(xFileName,yFileName,jxbxFileName,jxbyFileName,baddata=-1.e4,rmin=1.5):
    x=loadtxt(xFileName)[::-1]; Nx = x.size   # note the axis flip to get ascending order
    y=loadtxt(yFileName); Ny = y.size
    jxbx=loadtxt(jxbxFileName).reshape(Ny,Nx)[:,::-1]
    jxby=loadtxt(jxbyFileName).reshape(Ny,Nx)[:,::-1]

    X,Y=meshgrid(x,y)
    r=sqrt(X**2+Y**2)

    jxbx = ma.masked_equal(jxbx,baddata)
    jxby = ma.masked_equal(jxby,baddata)

    jxbx = ma.masked_where(r<=1.5,jxbx)
    jxby = ma.masked_where(r<=1.5,jxby)

    return(X,Y,jxbx,jxby)

def save_data(outFile,x,y,data):
    header = 'Nr=%d, Nt=%d'%(x.shape)
    savedata = vstack((x.ravel(),y.ravel(),data.ravel())).T
    savetxt(outFile,savedata,delimiter='   ',fmt='%.3e',header=header)
