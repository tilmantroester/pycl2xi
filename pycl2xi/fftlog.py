import ctypes
import numpy as np
import scipy.interpolate

def _get_lib():
    import os
    import sys
    import glob

    globable_libname = os.path.join(
                                os.path.dirname(__file__),
                                "_fftlog.cpython-{}{}*-{}.so".format(
                                                            sys.version_info[0], 
                                                            sys.version_info[1], 
                                                            sys.platform)
                                    )
    libname = glob.glob(globable_libname)
    if len(libname) < 1:
        raise ImportError("Can't find fftlog C library. Check that this is not executed from the package directory.")
    else:
        libname = libname[0]
    
    libpath, libname = os.path.split(libname)
    lib = np.ctypeslib.load_library(libname, libpath)
    return lib

_fftlib = _get_lib()

def fftlog_cl2xi(Cl, ell, bessel_order=0):
    n = Cl.size

    if Cl.shape != ell.shape:
        raise RuntimeError("Shape mismatch between Cl and ell!")

    xi = np.zeros(n, dtype=np.float64)
    theta = np.zeros(n, dtype=np.float64)

    Cl2xi_c_func = _fftlib.fftlog_ComputeXi2D
    Cl2xi_c_func.argtypes = [ctypes.c_double,
                             ctypes.c_int,
                             np.ctypeslib.ndpointer(dtype=np.float64,
                                                    ndim=1,
                                                    shape=(n,),
                                                    flags="C_CONTIGUOUS"),
                             np.ctypeslib.ndpointer(dtype=np.float64,
                                                    ndim=1,
                                                    shape=(n,),
                                                    flags="C_CONTIGUOUS"),
                             np.ctypeslib.ndpointer(dtype=np.float64,
                                                    ndim=1,
                                                    shape=(n,),
                                                    flags="C_CONTIGUOUS"),
                             np.ctypeslib.ndpointer(dtype=np.float64,
                                                    ndim=1,
                                                    shape=(n,),
                                                    flags="C_CONTIGUOUS")]

    Cl2xi_c_func(bessel_order, n, ell, Cl, theta, xi)
    return xi, theta

def Cl2xi(Cl, ell, theta, bessel_order=0, 
          ell_min_fftlog=0.01,
          ell_max_fftlog=60000,
          n_ell_fftlog=5000):
    """Calculate correlation functions from angular power spectrum using FFTlog.

    This extrapolates the Cl's at high ell using a power law."""
    
    ell_fftlog = np.logspace(np.log10(ell_min_fftlog), np.log10(ell_max_fftlog), n_ell_fftlog, endpoint=True)
    
    # Cubic spline interpolation of the input Cl's
    log_Cl_intp = scipy.interpolate.InterpolatedUnivariateSpline(ell, np.log(Cl), k=3, ext=2)
    
    ell_min = ell[0]
    ell_max = ell[-1]
    Cl_ell_max = Cl[-1]
    # The powerlaw index for the high-ell extrapolation
    tilt = np.log(Cl[-1]/Cl[-2])/np.log(ell[-1]/ell[-2])
    
    # For ell < ell_min, use the boundary value (Cl[0])
    # For ell_min <= ell <= ell_max, interpolate the input Cl's
    # For ell > ell_max, extrapolate using a powerlaw
    Cl_fftlog = np.piecewise(ell_fftlog, [ell_fftlog < ell_min,
                                          (ell_fftlog >= ell_min) & (ell_fftlog <= ell_max),
                                          ell_fftlog > ell_max],
                                         [Cl[0],
                                          lambda ell: np.exp(log_Cl_intp(ell)), 
                                          lambda ell: Cl[-1]*(ell/ell_max)**tilt])
    
    xi_fftlog, theta_fftlog = fftlog_cl2xi(Cl_fftlog, ell_fftlog, bessel_order=bessel_order)
    # Convert from radian to degree
    theta_fftlog *= 180/np.pi

    # Interpolate to the requested theta values
    xi_fftlog_intp = scipy.interpolate.InterpolatedUnivariateSpline(theta_fftlog, xi_fftlog, ext=2)(theta)
    return xi_fftlog_intp
