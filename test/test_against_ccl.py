import numpy as np
import pyccl as ccl

import scipy.interpolate

import pycl2xi.fftlog as fftlog

def setup_data():
    """Set up data for test."""
    pi = np.pi

    # Set up ccl cosmology object
    cosmo = ccl.Cosmology(Omega_c=0.25, Omega_b=0.05, n_s=0.96, sigma8=0.8, h=0.7)

    # Set up a simple n(z)
    z = np.linspace(0., 1., 50)
    n = np.exp(-((z-0.5)/0.1)**2)

    lens_tracer = ccl.ClTracerLensing(cosmo, False, n=n, z=z)

    # Set up ell and get Cl's
    ell = np.arange(2, 4000, dtype=np.float64)
    Cl = ccl.angular_cl(cosmo, lens_tracer, lens_tracer, ell)

    # Set up theta
    theta_min = 0.6/60 # degree
    theta_max = 600.0/60 # degree
    n_theta = 100

    theta = np.logspace(np.log10(theta_min), np.log10(theta_max), n_theta, endpoint=True)

    # Get CCL xi's
    xi_plus = ccl.correlation(cosmo, ell, Cl, theta, corr_type="L+", method="fftlog")
    xi_minus = ccl.correlation(cosmo, ell, Cl, theta, corr_type="L-", method="fftlog")

    # Get FFTLog xi's
    xi_plus_fftlog = fftlog.Cl2xi(Cl, ell, theta, bessel_order=0)
    xi_minus_fftlog = fftlog.Cl2xi(Cl, ell, theta, bessel_order=4)

    return (xi_plus_fftlog, xi_minus_fftlog), (xi_plus, xi_minus), (theta, theta)

def test_cl2xi(plot=False):
    """Test FFTLog python binding against CCL."""
    
    (xi_plus_fftlog, xi_minus_fftlog), (xi_plus, xi_minus), (theta, _) = setup_data()

    np.testing.assert_allclose(xi_minus_fftlog, xi_minus, rtol=1.0e-4)
    np.testing.assert_allclose(xi_plus_fftlog, xi_plus, rtol=2.0e-3)

def plot_cl2xi():
    """Plot the comparison used for the test."""
    import matplotlib.pyplot as plt
    import os

    (xi_plus_fftlog, xi_minus_fftlog), (xi_plus, xi_minus), (theta, _) = setup_data()
    plt.plot(theta, xi_minus_fftlog/xi_minus-1, label=r"$\xi_-$")
    plt.plot(theta, xi_plus_fftlog/xi_plus-1, label=r"$\xi_+$")
    plt.legend()
    plt.xlabel(r"$\theta$ [deg]")
    plt.ylabel("Fractional difference")
    plt.title("Cl2xi vs CCL")
    plt.savefig(os.path.join(os.path.dirname(__file__), "test_cl2xi.png"))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--plot":
        plot_cl2xi()
    else:
        np.testing.run_module_suite()