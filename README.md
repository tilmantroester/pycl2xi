# pycl2xi

This is a Python wrapper for the FFTLog code in CCL. Specifically, it wraps the `fftlog_ComputeXi2D` function and tries to reproduce the behaviour of `ccl_tracer_corr_fftlog` by doing the same power law extrapolation of the Cl's at high ell. The agreement is very good for xi_minus but xi_plus seems to be dependent on the details of the interpolation, such that the agreement is only ~1e-3 at scales of 10 degrees.

## Installation
The usual
```
python setup.py install
```
should do the trick.

## Testing
There is currently one test in `test/` that compares the correlation functions of this module with that of CCL. Passing `--plot` to `test_against_ccl.py` creates a plot of the fractional difference.
