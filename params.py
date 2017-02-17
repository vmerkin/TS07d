import argparse
import os,os.path,sys

def read():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xfile',help='X coordinate file',nargs='?',default='xOutputFile.txt')
    parser.add_argument('--yfile',help='Y coordinate file',nargs='?',default='yOutputFile.txt')
    parser.add_argument('--jxbxfile',help='jxb X component file',nargs='?',default='jxbxOutputFile.txt')
    parser.add_argument('--jxbyfile',help='jxb Y component file',nargs='?',default='jxbyOutputFile.txt')
    parser.add_argument('--Nr',help='Number of points in the radial direction.',nargs='?',default=100,type=int)
    parser.add_argument('--Nt',help='Number of points in the angular direction.',nargs='?',default=180,type=int)
    parser.add_argument('--rmin',help='Minimum radius of the domain (Re)',nargs='?',default=1.6,type=float)
    parser.add_argument('--rmax',help='Maximum radius of the domain (Re)',nargs='?',default=9.9,type=float)
    parser.add_argument('--outDataFile',help='File to output the results.',nargs='?',default='ts07d_pressure.dat')
    parser.add_argument('--outPlotFile',help='File to output the results.',nargs='?',default='ts07d_pressure.png')
    parser.add_argument('--xflip',help='Flip X axis in input files? Default is False.',action="store_false")
    args = parser.parse_args()

    if not (os.path.exists(args.xfile) and
            os.path.exists(args.yfile) and 
            os.path.exists(args.jxbxfile) and
            os.path.exists(args.jxbyfile) ):
        sys.exit('One or more input files do not exist. Quitting.')

    return(args.xfile,args.yfile,args.jxbxfile,args.jxbyfile,args.Nr,args.Nt,args.rmax,args.rmin,args.outDataFile,args.outPlotFile,args.xflip)


        




