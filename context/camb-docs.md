```markdown
# CAMB Python Documentation Summary (Release 1.5.9)

## Library Purpose

CAMB (Code for Anisotropies in the Microwave Background) is a cosmology code for calculating CMB, lensing, galaxy count, dark-age 21cm power spectra, matter power spectra, and transfer functions. It also provides general utility functions for cosmological calculations such as background expansion, distances, etc. The main code is Python with numerical calculations implemented efficiently in Python-wrapped modern Fortran.

## Installation and Setup

**Standard Installation:**

```bash
pip install camb [--user]
```
*(The `--user` flag is optional and only required if you don't have write permission to your main python installation.)*

**Installation from GitHub (for development):**

```bash
git clone --recursive https://github.com/cmbant/CAMB.git
pip install -e /path/to/CAMB [--user]
```

**Conda Installation:**

```bash
conda create -n camb -c conda-forge python=3.11 camb
activate camb
```
*(Check that conda installs the latest version; if not, try installing in a new clean conda environment.)*

**Dependencies:**

*   A Fortran compiler is required if installing from source or modifying the Fortran code. Pre-compiled binaries are included in standard pip/conda installs.
*   Recommended compilers:
    *   gfortran version 6.3 or higher
    *   Intel Fortran (ifort), version 18.0.1 or higher (some things may work with version 14+)
*   Getting Compilers:
    *   **Mac:** Download the binary installation (likely refers to standard Python wheels not needing a separate Fortran install).
    *   **Windows:** Download gfortran as part of MinGW-w64 (select x86\_64 option) or get latest from niXman on GitHub (e.g., x86\_64-13.2.0-release-win32-seh-msvcrt-rt\_v11-rev1). MinGW-w64 should be installed under Program Files for `python setup.py make` to work easily.
    *   **Linux:** `sudo apt-get update; sudo apt-get install gfortran`
*   Alternatively, use a container like CosmoBox.

**Building/Updating from Source:**

In the main CAMB source root directory:

```bash
python setup.py make
```
*(You may need to close/restart Python instances or Jupyter kernels to load the updated library).*

To automatically rebuild from Jupyter:

```python
import IPython
IPython.Application.instance().kernel.do_shutdown(True) # Or similar kernel restart
```

Or use subprocess to build before importing:

```python
import subprocess
import sys
import os
src_dir = '/path/to/git/CAMB'
try:
    subprocess.check_output(r'python "%s" make'%os.path.join(src_dir, 'setup.py'),
                            stderr=subprocess.STDOUT)
    sys.path.insert(0,src_dir)
    import camb
    print('Using CAMB %s installed at %s'%(camb.__version__,
                                           os.path.dirname(camb.__file__)))
except subprocess.CalledProcessError as E:
    print(E.output.decode())

```

**Basic Usage:**

*   Import: `import camb`
*   Load parameters from INI: `camb.read_ini(ini_filename)`
*   Run from command line: `camb inifiles/planck_2018.ini`

## Basic Functions

*   Modules are wrapped Fortran 2003 but usable entirely from Python.

### `camb.get_age(params)`

*   **Purpose:** Get age of universe for given set of parameters.
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
*   **Returns:** Age of universe in Julian gigayears.

### `camb.get_background(params, no_thermo=False)`

*   **Purpose:** Calculate background cosmology for specified parameters and return `CAMBdata`, ready to get derived parameters and use background functions like `angular_diameter_distance()`.
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
    *   `no_thermo`: set True if thermal and ionization history not required.
*   **Returns:** `CAMBdata` instance.

### `camb.get_matter_power_interpolator(params, zmin=0, zmax=10, nz_step=100, zs=None, kmax=10, nonlinear=True, var1=None, var2=None, hubble_units=True, k_hunit=True, return_z_k=False, k_per_logint=None, log_interp=True, extrap_kmax=None)`

*   **Purpose:** Return a 2D spline interpolation object to evaluate matter power spectrum as function of z and k/h (or k). Recalculates results from scratch. See `Matter power spectrum and matter transfer function variables`.
*   **Example:**
    ```python
    from camb import get_matter_power_interpolator
    PK = get_matter_power_interpolator(params);
    print('Power spectrum at z=0.5, k/h=0.1/Mpc is %s (Mpc/h)^3 '%(PK.P(0.5, 0.1)))
    ```
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
    *   `zmin`: minimum z (use 0 or smaller than you want for good interpolation).
    *   `zmax`: maximum z (use larger than you want for good interpolation).
    *   `nz_step`: number of steps to sample in z (default max allowed is 100).
    *   `zs`: instead of zmin,zmax, nz\_step, can specific explicit array of z values to spline from.
    *   `kmax`: maximum k.
    *   `nonlinear`: include non-linear correction from halo model.
    *   `var1`: variable i (index, or name of variable; default delta\_tot).
    *   `var2`: variable j (index, or name of variable; default delta\_tot).
    *   `hubble_units`: if true, output power spectrum in (Mpc/h)³ units, otherwise Mpc³.
    *   `k_hunit`: if true, matter power is a function of k/h, if false, just k (both Mpc⁻¹ units).
    *   `return_z_k`: if true, return interpolator, z, k where z, k are the grid used.
    *   `k_per_logint`: specific uniform sampling over log k (if not set, uses optimized irregular sampling).
    *   `log_interp`: if true, interpolate log of power spectrum (unless any values are negative in which case ignored).
    *   `extrap_kmax`: if set, use power law extrapolation beyond kmax to extrap\_kmax (useful for tails of integrals).
*   **Returns:** An object PK based on `RectBivariateSpline`, callable with `PK.P(z,kh)` or `PK(z,log(kh))`. If `return_z_k=True`, returns (interpolator, z, k).

### `camb.get_results(params)`

*   **Purpose:** Calculate results for specified parameters and return `CAMBdata` instance for getting results.
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
*   **Returns:** `CAMBdata` instance.

### `camb.get_transfer_functions(params, only_time_sources=False)`

*   **Purpose:** Calculate transfer functions for specified parameters and return `CAMBdata` instance for getting results and subsequently calculating power spectra.
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
    *   `only_time_sources`: does not calculate the CMB l,k transfer functions and does not apply any non-linear correction scaling. Results with `only_time_sources=True` can therefore be used with different initial power spectra to get consistent non-linear lensed spectra.
*   **Returns:** `CAMBdata` instance.

### `camb.get_valid_numerical_params(transfer_only=False, **class_names)`

*   **Purpose:** Get numerical parameter names that are valid input to `set_params()`.
*   **Parameters:**
    *   `transfer_only`: if True, exclude parameters that affect only initial power spectrum or non-linear model.
    *   `class_names`: class name parameters that will be used by `model.CAMBparams.set_classes()`.
*   **Returns:** Set of valid input parameter names for `set_params()`.

### `camb.get_zre_from_tau(params, tau)`

*   **Purpose:** Get reionization redshift given optical depth tau.
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
    *   `tau`: optical depth.
*   **Returns:** Reionization redshift (or negative number if error).

### `camb.read_ini(ini_filename, no_validate=False)`

*   **Purpose:** Get a `model.CAMBparams` instance using parameters specified in a .ini parameter file.
*   **Parameters:**
    *   `ini_filename`: path of the .ini file to read, or a full URL to download from.
    *   `no_validate`: do not pre-validate the ini file (faster, but may crash kernel if error).
*   **Returns:** `model.CAMBparams` instance.

### `camb.run_ini(ini_filename, no_validate=False)`

*   **Purpose:** Run the command line camb from a .ini file (producing text files as with the command line program). Does the same as the command line program, except global config parameters are not read and set.
*   **Parameters:**
    *   `ini_filename`: .ini file to use.
    *   `no_validate`: do not pre-validate the ini file (faster, but may crash kernel if error).

### `camb.set_feedback_level(level=1)`

*   **Purpose:** Set the feedback level for internal CAMB calls.
*   **Parameters:**
    *   `level`: zero for nothing, >1 for more.

### `camb.set_params(cp=None, verbose=False, **params)`

*   **Purpose:** Set all CAMB parameters at once, including parameters which are part of the `CAMBparams` structure, as well as global parameters. Calls underlying methods like `set_cosmology`, `set_accuracy`, etc.
*   **Example:**
    ```python
    cp = camb.set_params(ns=1, H0=67, ombh2=0.022, omch2=0.1, w=-0.95, Alens=1.2,
                         lmax=2000,
                         WantTransfer=True, dark_energy_model='DarkEnergyPPF')
    ```
*   **Parameters:**
    *   `cp`: use this `CAMBparams` instead of creating a new one.
    *   `verbose`: print out the equivalent set of commands.
    *   `**params`: the values of the parameters.
*   **Returns:** `model.CAMBparams` instance.

### `camb.set_params_cosmomc(p, num_massive_neutrinos=1, neutrino_hierarchy='degenerate', halofit_version='mead', dark_energy_model='ppf', lmax=2500, lens_potential_accuracy=1, inpars=None)`

*   **Purpose:** Get `CAMBParams` for dictionary of cosmomc-named parameters assuming Planck 2018 defaults.
*   **Parameters:**
    *   `p`: dictionary of cosmomc parameters (e.g. from `getdist.types.BestFit`'s `getParamDict()` function).
    *   `num_massive_neutrinos`: usually 1 if fixed mnu=0.06 eV, three if mnu varying.
    *   `neutrino_hierarchy`: hierarchy ('degenerate', 'normal', 'inverted').
    *   `halofit_version`: name of the specific Halofit model to use for non-linear modelling.
    *   `dark_energy_model`: 'ppf' or 'fluid' dark energy model.
    *   `lmax`: lmax for accuracy settings.
    *   `lens_potential_accuracy`: lensing accuracy parameter.
    *   `inpars`: optional input `CAMBParams` to set.
*   **Returns:** `model.CAMBparams` instance.

## Input Parameter Model

### `class camb.model.CAMBparams(*args, **kwargs)`

*   **Purpose:** Object storing the parameters for a CAMB calculation, including cosmological parameters and settings for what to calculate. Default parameters are set automatically on instantiation. Can be saved/restored using `repr`/`eval` or `pickle`.
*   **Adding Parameters:** Modify the `CAMBparams` type in `model.f90`, edit the `_fields_` list in `model.py`, and rebuild.
*   **Setting Parameters:** Use `set_cosmology()` and similar methods, or the convenience function `camb.set_params()`.
*   **Variables:**
    *   `WantCls` (boolean): Calculate C\_L.
    *   `WantTransfer` (boolean): Calculate matter transfer functions and matter power spectrum.
    *   `WantScalars` (boolean): Calculates scalar modes.
    *   `WantTensors` (boolean): Calculate tensor modes.
    *   `WantVectors` (boolean): Calculate vector modes.
    *   `WantDerivedParameters` (boolean): Calculate derived parameters.
    *   `Want_cl_2D_array` (boolean): For the C\_L, include NxN matrix of all possible cross-spectra between sources.
    *   `Want_CMB` (boolean): Calculate the temperature and polarization power spectra.
    *   `Want_CMB_lensing` (boolean): Calculate the lensing potential power spectrum.
    *   `DoLensing` (boolean): Include CMB lensing.
    *   `NonLinear` (integer/string): One of: `NonLinear_none`, `NonLinear_pk`, `NonLinear_lens`, `NonLinear_both`. Controls non-linear corrections.
    *   `Transfer` (`camb.model.TransferParams`): Parameters for matter power spectrum calculation.
    *   `want_zstar` (boolean): Calculate zstar (recombination redshift).
    *   `want_zdrag` (boolean): Calculate zdrag (drag epoch redshift).
    *   `min_l` (integer): l\_min for the scalar C\_L (1 or 2, L=1 dipoles are Newtonian Gauge).
    *   `max_l` (integer): l\_max for the scalar C\_L.
    *   `max_l_tensor` (integer): l\_max for the tensor C\_L.
    *   `max_eta_k` (float64): Maximum k\*eta\_0 for scalar C\_L.
    *   `max_eta_k_tensor` (float64): Maximum k\*eta\_0 for tensor C\_L.
    *   `ombh2` (float64): Omega\_baryon h^2.
    *   `omch2` (float64): Omega\_cdm h^2.
    *   `omk` (float64): Omega\_K.
    *   `omnuh2` (float64): Omega\_massive\_neutrino h^2.
    *   `H0` (float64): Hubble parameter is km/s/Mpc units.
    *   `TCMB` (float64): CMB temperature today in Kelvin (default 2.7255).
    *   `YHe` (float64): Helium mass fraction. If `None` in `set_cosmology`, uses BBN prediction.
    *   `num_nu_massless` (float64): Effective number of massless neutrinos (N_eff, use `standard_neutrino_neff` in `set_cosmology` for standard value).
    *   `num_nu_massive` (integer): Total physical (integer) number of massive neutrino species.
    *   `nu_mass_eigenstates` (integer): Number of non-degenerate mass eigenstates.
    *   `share_delta_neff` (boolean): Share the non-integer part of `num_nu_massless` between the eigenstates.
    *   `nu_mass_degeneracies` (float64 array): Degeneracy of each distinct eigenstate.
    *   `nu_mass_fractions` (float64 array): Mass fraction in each distinct eigenstate.
    *   `nu_mass_numbers` (integer array): Number of physical neutrinos per distinct eigenstate.
    *   `InitPower` (`camb.initialpower.InitialPower`): Initial power spectrum model instance.
    *   `Recomb` (`camb.recombination.RecombinationModel`): Recombination model instance.
    *   `Reion` (`camb.reionization.ReionizationModel`): Reionization model instance.
    *   `DarkEnergy` (`camb.dark_energy.DarkEnergyModel`): Dark energy model instance.
    *   `NonLinearModel` (`camb.nonlinear.NonLinearModel`): Non-linear model instance.
    *   `Accuracy` (`camb.model.AccuracyParams`): Accuracy parameters instance.
    *   `SourceTerms` (`camb.model.SourceTermParams`): Source term parameters instance.
    *   `z_outputs` (float64 array): Redshifts to always calculate BAO output parameters.
    *   `scalar_initial_condition` (integer/string): One of: `initial_vector`, `initial_adiabatic`, `initial_iso_CDM`, `initial_iso_baryon`, `initial_iso_neutrino`, `initial_iso_neutrino_vel`.
    *   `InitialConditionVector` (float64 array): If `scalar_initial_condition` is `initial_vector`, the vector of initial condition amplitudes.
    *   `OutputNormalization` (integer): If non-zero, multipole to normalize the C\_L at.
    *   `Alens` (float64): Non-physical scaling amplitude for the CMB lensing spectrum power.
    *   `MassiveNuMethod` (integer/string): One of: `Nu_int`, `Nu_trunc`, `Nu_approx`, `Nu_best`. Method for massive neutrinos.
    *   `DoLateRadTruncation` (boolean): If true, use smooth approx to radiation perturbations after decoupling on small scales.
    *   `Evolve_baryon_cs` (boolean): Evolve a separate equation for the baryon sound speed rather than using background approximation.
    *   `Evolve_delta_xe` (boolean): Evolve ionization fraction perturbations.
    *   `Evolve_delta_Ts` (boolean): Evolve the spin temperature perturbation (for 21cm).
    *   `Do21cm` (boolean): 21cm is not yet implemented via the python wrapper.
    *   `transfer_21cm_cl` (boolean): Get 21cm C\_L at a given fixed redshift.
    *   `Log_lvalues` (boolean): Use log spacing for sampling in L.
    *   `use_cl_spline_template` (boolean): When interpolating use a fiducial spectrum shape to define ratio to spline.
    *   `min_l_logl_sampling` (integer): Minimum L to use log sampling for L.
    *   `SourceWindows` (array of `camb.sources.SourceWindow`): List of source window function instances.
    *   `CustomSources` (`camb.model.CustomSources`): Custom compiled source functions.
*   **Properties:**
    *   `N_eff`: Effective number of degrees of freedom in relativistic species at early times.
*   **Methods:**
    *   `copy()`: Make an independent copy of this object. Returns a deep copy of self.
    *   `classmethod dict(state)`: Make an instance from a dictionary of field values.
        *   `state`: dictionary of values.
        *   Returns: new instance.
    *   `diff(params)`: Print differences between this set of parameters and `params`.
        *   `params`: another `CAMBparams` instance.
    *   `get_DH(ombh2=None, delta_neff=None)`: Get deuterium ratio D/H by interpolation using the `bbn.BBNPredictor` instance passed to `set_cosmology()`.
        *   `ombh2`: Ωbh² (default: value passed to `set_cosmology()`).
        *   `delta_neff`: additional Neff relative to standard value (of 3.044) (default: from values passed to `set_cosmology()`).
        *   Returns: BBN helium nucleon fraction D/H.
    *   `get_Y_p(ombh2=None, delta_neff=None)`: Get BBN helium nucleon fraction (Y\_p, not mass fraction Y\_He) using the `bbn.BBNPredictor` instance.
        *   `ombh2`: Ωbh² (default: value passed to `set_cosmology()`).
        *   `delta_neff`: additional Neff relative to standard value (of 3.044) (default: from values passed to `set_cosmology()`).
        *   Returns: Yp BBN helium nucleon fraction predicted by BBN.
    *   `replace(instance)`: Replace the content of this class with another instance (deep copy in Fortran).
        *   `instance`: instance of the same class to replace this instance with.
    *   `scalar_power(k)`: Get the primordial scalar curvature power spectrum at k.
        *   `k`: wavenumber k (in Mpc⁻¹ units).
        *   Returns: power spectrum at k.
    *   `set_H0_for_theta(theta, cosmomc_approx=False, theta_H0_range=(10, 100), est_H0=67.0, iteration_threshold=8, setter_H0=None)`: Set H0 to give a specified value of the acoustic angular scale parameter theta.
        *   `theta`: value of rs/DM at redshift z\*.
        *   `cosmomc_approx`: if true, use approximate fitting formula for z\*, if false do full numerical calculation.
        *   `theta_H0_range`: min, max interval to search for H0 (in km/s/Mpc).
        *   `est_H0`: an initial guess for H0 in km/s/Mpc, used in the case `cosmomc_approx=False`.
        *   `iteration_threshold`: difference in H0 from `est_H0` for which to iterate, used for `cosmomc_approx=False` to correct for small changes in zstar when H0 changes.
        *   `setter_H0`: if specified, a function `func(pars: CAMBParams, H0: float)` to call to set H0 for each iteration. Can be used e.g. when DE model needs to be changed for each H0.
    *   `set_accuracy(AccuracyBoost=1.0, lSampleBoost=1.0, lAccuracyBoost=1.0, DoLateRadTruncation=True, min_l_logl_sampling=None)`: Set parameters determining overall calculation accuracy.
        *   `AccuracyBoost`: increase `AccuracyBoost` to decrease integration step size, increase density of k sampling, etc.
        *   `lSampleBoost`: increase `lSampleBoost` to increase density of L sampling for CMB.
        *   `lAccuracyBoost`: increase `lAccuracyBoost` to increase the maximum L included in the Boltzmann hierarchies.
        *   `DoLateRadTruncation`: If True, use approximation to radiation perturbation evolution at late times.
        *   `min_l_logl_sampling`: at L>`min_l_logl_sampling` uses sparser log sampling for L interpolation; increase above 5000 for better accuracy at L > 5000.
        *   Returns: `self`.
    *   `set_classes(dark_energy_model=None, initial_power_model=None, non_linear_model=None, recombination_model=None, reionization_model=None)`: Change the classes used to implement parts of the model.
        *   `dark_energy_model`: ‘fluid’, ‘ppf’, or name of a `DarkEnergyModel` class.
        *   `initial_power_model`: name of an `InitialPower` class.
        *   `non_linear_model`: name of a `NonLinearModel` class.
        *   `recombination_model`: name of `RecombinationModel` class.
        *   `reionization_model`: name of `ReionizationModel` class.
    *   `set_cosmology(H0: float | None = None, ombh2=0.022, omch2=0.12, omk=0.0, cosmomc_theta: float | None = None, thetastar: float | None = None, neutrino_hierarchy: str | int = 'degenerate', num_massive_neutrinos=1, mnu=0.06, nnu=3.044, YHe: float | None = None, meffsterile=0.0, standard_neutrino_neff=3.044, TCMB=2.7255, tau: float | None = None, zrei: float | None = None, Alens=1.0, bbn_predictor: None | str | BBNPredictor = None, theta_H0_range=(10, 100), setter_H0=None)`: Sets cosmological parameters in terms of physical densities.
        *   `H0`: Hubble parameter today in km/s/Mpc. Can leave unset and instead set `thetastar` or `cosmomc_theta`.
        *   `ombh2`: physical density in baryons.
        *   `omch2`: physical density in cold dark matter.
        *   `omk`: Omega\_K curvature parameter.
        *   `cosmomc_theta`: The approximate CosmoMC theta parameter θMC. Uses numerical DM(z\*) but approximate fitting formula for z\*. Leave unset to use H0 or `thetastar`.
        *   `thetastar`: The angular acoustic scale parameter θ\* = rs(z\*)/DM(z\*). Numerically calculated. Leave unset to use H0 or `cosmomc_theta`.
        *   `neutrino_hierarchy`: ‘degenerate’, 'normal', or 'inverted' (1 or 2 eigenstate approximation).
        *   `num_massive_neutrinos`: number of massive neutrinos.
        *   `mnu`: sum of neutrino masses (in eV). Defines Omega\_nu assuming non-relativistic today.
        *   `nnu`: N\_eff, effective relativistic degrees of freedom. Use `standard_neutrino_neff` for the standard value accounting for heating/QED.
        *   `YHe`: Helium mass fraction. If None, set from BBN consistency.
        *   `meffsterile`: effective mass of sterile neutrinos.
        *   `standard_neutrino_neff`: default value for N\_eff in standard cosmology (default 3.044).
        *   `TCMB`: CMB temperature (in Kelvin).
        *   `tau`: optical depth; if None and `zrei` is None, current Reion settings are not changed.
        *   `zrei`: reionization mid-point optical depth (set tau=None to use this).
        *   `Alens`: (non-physical) scaling of the lensing potential compared to prediction.
        *   `bbn_predictor`: `bbn.BBNPredictor` instance used to get `YHe` from BBN consistency if `YHe` is None, or name of a BBN predictor class, or file name of an interpolation table.
        *   `theta_H0_range`: if `thetastar` or `cosmomc_theta` is specified, the min, max interval of H0 values to map to.
        *   `setter_H0`: if specified, a function `func(pars: CAMBParams, H0: float)` to update the model for each H0 iteration used to search for `thetastar`.
    *   `set_custom_scalar_sources(custom_sources, source_names=None, source_ell_scales=None, frame='CDM', code_path=None)`: Set custom sources for angular power spectrum using `camb.symbolic` sympy expressions.
        *   `custom_sources`: list of sympy expressions for the angular power spectrum sources.
        *   `source_names`: optional list of string names for the sources.
        *   `source_ell_scales`: list or dictionary of scalings for each source name. Integer `n` scales by `sqrt((l+n)!/(l-n)!)`.
        *   `frame`: if the source is not gauge invariant, frame in which to interpret result.
        *   `code_path`: optional path for output of source code for CAMB f90 source function.
    *   `set_dark_energy(w=-1.0, cs2=1.0, wa=0, dark_energy_model='fluid')`: Set dark energy parameters. Assign class instance to `DarkEnergy` field for custom model.
        *   `w`: w = Pde/rhode, assumed constant.
        *   `wa`: evolution of w (for `dark_energy_model='ppf'`).
        *   `cs2`: rest-frame sound speed squared of dark energy fluid.
        *   `dark_energy_model`: model to use ('fluid' or 'ppf'), default is 'fluid'.
        *   Returns: `self`.
    *   `set_dark_energy_w_a(a, w, dark_energy_model='fluid')`: Set the dark energy equation of state from tabulated values (cubic spline interpolated).
        *   `a`: array of sampled a = 1/(1+z) values.
        *   `w`: array of w(a).
        *   `dark_energy_model`: model to use ('fluid' or 'ppf'), default is 'fluid'.
        *   Returns: `self`.
    *   `set_for_lmax(lmax, max_eta_k=None, lens_potential_accuracy=0, lens_margin=150, k_eta_fac=2.5, lens_k_eta_reference=18000.0, nonlinear=None)`: Set parameters to get CMB power spectra accurate to a specific `lmax`.
        *   `lmax`: lmax you want accuracy up to.
        *   `max_eta_k`: maximum value of k\*eta0 ≈ k\*chi\* to use, indirectly sets k\_max. If None, sensible value set automatically.
        *   `lens_potential_accuracy`: Set to 1 or higher for accurate lensing potential (1 is Planck-level accuracy).
        *   `lens_margin`: the Delta lmax to use to ensure lensed Cl are correct at `lmax`.
        *   `k_eta_fac`: default factor for setting `max_eta_k = k_eta_fac*lmax` if `max_eta_k`=None.
        *   `lens_k_eta_reference`: value of `max_eta_k` to use when `lens_potential_accuracy`>0; use `k_eta_max = lens_k_eta_reference*lens_potential_accuracy`.
        *   `nonlinear`: use non-linear power spectrum; if None, sets nonlinear if `lens_potential_accuracy`>0 otherwise preserves current setting.
        *   Returns: `self`.
    *   `set_initial_power(initial_power_params)`: Set the `InitialPower` primordial power spectrum parameters.
        *   `initial_power_params`: `initialpower.InitialPowerLaw` or `initialpower.SplinedInitialPower` instance.
        *   Returns: `self`.
    *   `set_initial_power_function(P_scalar, P_tensor=None, kmin=1e-06, kmax=100.0, N_min=200, rtol=5e-05, effective_ns_for_nonlinear=None, args=())`: Set initial power spectrum from a function `P_scalar(k, *args)`.
        *   `P_scalar`: function returning normalized initial scalar curvature power vs k (Mpc⁻¹).
        *   `P_tensor`: optional function returning normalized initial tensor power spectrum.
        *   `kmin`: minimum wavenumber to compute.
        *   `kmax`: maximum wavenumber to compute.
        *   `N_min`: minimum number of spline points for the pre-computation.
        *   `rtol`: relative tolerance for deciding how many points are enough.
        *   `effective_ns_for_nonlinear`: an effective n\_s for use with approximate non-linear corrections.
        *   `args`: optional list of arguments passed to `P_scalar` (and `P_tensor`).
        *   Returns: `self`.
    *   `set_initial_power_table(k, pk=None, pk_tensor=None, effective_ns_for_nonlinear=None)`: Set a general initial power spectrum from tabulated values.
        *   `k`: array of k values (Mpc⁻¹).
        *   `pk`: array of primordial curvature perturbation power spectrum values P(k\_i).
        *   `pk_tensor`: array of tensor spectrum values.
        *   `effective_ns_for_nonlinear`: an effective n\_s for use with approximate non-linear corrections.
    *   `set_matter_power(redshifts=(0.0,), kmax=1.2, k_per_logint=None, nonlinear=None, accurate_massive_neutrino_transfers=False, silent=False)`: Set parameters for calculating matter power spectra and transfer functions.
        *   `redshifts`: array of redshifts to calculate.
        *   `kmax`: maximum k to calculate (where k is just k, not k/h).
        *   `k_per_logint`: minimum number of k steps per log k. Set to zero to use default optimized spacing.
        *   `nonlinear`: if None, uses existing setting, otherwise boolean for whether to use non-linear matter power.
        *   `accurate_massive_neutrino_transfers`: if you want the massive neutrino transfers accurately.
        *   `silent`: if True, don't give warnings about sort order.
        *   Returns: `self`.
    *   `set_nonlinear_lensing(nonlinear)`: Settings for whether or not to use non-linear corrections for the CMB lensing potential.
        *   `nonlinear`: true to use non-linear corrections.
    *   `tensor_power(k)`: Get the primordial tensor curvature power spectrum at k.
        *   `k`: wavenumber k (in Mpc⁻¹ units).
        *   Returns: tensor power spectrum at k.
    *   `validate()`: Do some quick tests for sanity. Returns: True if OK.

### `class camb.model.AccuracyParams`

*   **Purpose:** Structure with parameters governing numerical accuracy. `AccuracyBoost` scales most parameters. Not intended to be separately instantiated. Access via `CAMBparams.Accuracy`. Set fields like `'Accuracy.xxx':yyy` in `camb.set_params()`.
*   **Variables:**
    *   `AccuracyBoost` (float64): general accuracy setting.
    *   `lSampleBoost` (float64): accuracy for sampling in ell for interpolation for the C\_l (if >=50, all ell are calculated).
    *   `lAccuracyBoost` (float64): Boosts number of multipoles integrated in Boltzmann hierarchy.
    *   `AccuratePolarization` (boolean): Do you care about the accuracy of the polarization Cls?
    *   `AccurateBB` (boolean): Do you care about BB accuracy (e.g. in lensing)?
    *   `AccurateReionization` (boolean): Do you care about percent level accuracy on EE signal from reionization?
    *   `TimeStepBoost` (float64): Sampling time steps.
    *   `BackgroundTimeStepBoost` (float64): Number of time steps for background thermal history and source window interpolation.
    *   `IntTolBoost` (float64): Tolerances for integrating differential equations.
    *   `SourcekAccuracyBoost` (float64): Accuracy of k sampling for source time integration.
    *   `IntkAccuracyBoost` (float64): Accuracy of k sampling for integration.
    *   `TransferkBoost` (float64): Accuracy of k sampling for transfer functions.
    *   `NonFlatIntAccuracyBoost` (float64): Accuracy of non-flat time integration.
    *   `BessIntBoost` (float64): Accuracy of bessel integration truncation.
    *   `LensingBoost` (float64): Accuracy of the lensing of CMB power spectra.
    *   `NonlinSourceBoost` (float64): Accuracy of steps and kmax used for the non-linear correction.
    *   `BesselBoost` (float64): Accuracy of bessel pre-computation sampling.
    *   `LimberBoost` (float64): Accuracy of Limber approximation use.
    *   `SourceLimberBoost` (float64): Scales when to switch to Limber for source windows.
    *   `KmaxBoost` (float64): Boost max k for source window functions.
    *   `neutrino_q_boost` (float64): Number of momenta integrated for neutrino perturbations.

### `class camb.model.TransferParams`

*   **Purpose:** Object storing parameters for the matter power spectrum calculation. Part of `CAMBparams`.
*   **Variables:**
    *   `high_precision` (boolean): True for more accuracy.
    *   `accurate_massive_neutrinos` (boolean): True if you want neutrino transfer functions accurate (false by default).
    *   `kmax` (float64): k\_max to output (no h in units).
    *   `k_per_logint` (integer): number of points per log k interval. If zero, set an irregular optimized spacing.
    *   `PK_num_redshifts` (integer): number of redshifts to calculate.
    *   `PK_redshifts` (float64 array): redshifts to output for the matter transfer and power.

### `class camb.model.SourceTermParams`

*   **Purpose:** Structure with parameters determining how galaxy/lensing/21cm power spectra and transfer functions are calculated. Part of `CAMBparams`.
*   **Variables:**
    *   `limber_windows` (boolean): Use Limber approximation where appropriate.
    *   `limber_phi_lmin` (integer): When `limber_windows=True`, the minimum L to use Limber approximation for the lensing potential and other sources.
    *   `counts_density` (boolean): Include the density perturbation source.
    *   `counts_redshift` (boolean): Include redshift distortions.
    *   `counts_lensing` (boolean): Include magnification bias for number counts.
    *   `counts_velocity` (boolean): Non-redshift distortion velocity terms.
    *   `counts_radial` (boolean): Radial displacement velocity term; subset of `counts_velocity`.
    *   `counts_timedelay` (boolean): Include time delay terms \* 1 / (H \* chi).
    *   `counts_ISW` (boolean): Include tiny ISW terms.
    *   `counts_potential` (boolean): Include tiny terms in potentials at source.
    *   `counts_evolve` (boolean): Account for source evolution.
    *   `line_phot_dipole` (boolean): Dipole sources for 21cm.
    *   `line_phot_quadrupole` (boolean): Quadrupole sources for 21cm.
    *   `line_basic` (boolean): Include main 21cm monopole density/spin temperature sources.
    *   `line_distortions` (boolean): Redshift distortions for 21cm.
    *   `line_extra` (boolean): Include other sources.
    *   `line_reionization` (boolean): Replace the E modes with 21cm polarization.
    *   `use_21cm_mK` (boolean): Use mK units for 21cm.

### `class camb.model.CustomSources`

*   **Purpose:** Structure containing symbolic-compiled custom CMB angular power spectrum source functions. Set via `model.CAMBparams.set_custom_scalar_sources()`.
*   **Variables:**
    *   `num_custom_sources` (integer): number of sources set.
    *   `c_source_func` (pointer): Fortran function pointer (don't change directly).
    *   `custom_source_ell_scales` (integer array): scaling in L for outputs.

## Calculation Results

### `class camb.results.CAMBdata(*args, **kwargs)`

*   **Purpose:** An object for storing calculational data, parameters and transfer functions. Returned by `camb.get_background()`, `camb.get_transfer_functions()` or `camb.get_results()`. Use `camb.get_results()` to create a fully calculated instance.
*   **Variables:**
    *   `Params` (`camb.model.CAMBparams`): The input parameters used.
    *   `ThermoDerivedParams` (float64 array): Array of derived parameters (see `get_derived_params()`).
    *   `flat` (boolean): True if flat universe.
    *   `closed` (boolean): True if closed universe.
    *   `grhocrit` (float64): kappa\*a^2\*rho\_c(0)/c^2 in Mpc**(-2).
    *   `grhog` (float64): kappa/c^2\*4\*sigma\_B/c^3 T\_CMB^4.
    *   `grhor` (float64): 7/8\*(4/11)^(4/3)\*grhog (per massless neutrino species).
    *   `grhob` (float64): baryon contribution.
    *   `grhoc` (float64): CDM contribution.
    *   `grhov` (float64): Dark energy contribution.
    *   `grhornomass` (float64): grhor\*number of massless neutrino species.
    *   `grhok` (float64): curvature contribution to critical density.
    *   `taurst` (float64): time at start of recombination.
    *   `dtaurec` (float64): time step in recombination.
    *   `taurend` (float64): time at end of recombination.
    *   `tau_maxvis` (float64): time at peak visibility.
    *   `adotrad` (float64): da/d tau in early radiation-dominated era.
    *   `omega_de` (float64): Omega for dark energy today.
    *   `curv` (float64): curvature K.
    *   `curvature_radius` (float64): 1/sqrt(|K|).
    *   `Ksign` (float64): Ksign = 1, 0 or -1.
    *   `tau0` (float64): conformal time today.
    *   `chi0` (float64): comoving angular diameter distance of big bang.
    *   `scale` (float64): relative to flat. e.g. for scaling L sampling.
    *   `akthom` (float64): sigma\_T \* (number density of protons now).
    *   `fHe` (float64): n\_He\_tot / n\_H\_tot.
    *   `Nnow` (float64): number density today.
    *   `z_eq` (float64): matter-radiation equality redshift assuming all neutrinos relativistic.
    *   `grhormass` (float64 array): Massive neutrino contributions?
    *   `nu_masses` (float64 array): Masses of neutrinos?
    *   `num_transfer_redshifts` (integer): Number of calculated redshift outputs for the matter transfer.
    *   `transfer_redshifts` (float64 array): Calculated output redshifts.
    *   `PK_redshifts_index` (integer array): Indices of the requested PK\_redshifts.
    *   `OnlyTransfers` (boolean): Only calculating transfer functions, not power spectra.
    *   `HasScalarTimeSources` (boolean): calculate and save time source functions, not power spectra.
*   **Methods:**
    *   `angular_diameter_distance(z)`: Get (non-comoving) angular diameter distance to redshift z. Prerequisite: `calc_background`, `calc_background_no_thermo`, or transfers/power calculated.
        *   `z`: redshift or array of redshifts.
        *   Returns: angular diameter distances.
    *   `angular_diameter_distance2(z1, z2)`: Get angular diameter distance between two redshifts. Prerequisite: background/transfers/power calculated.
        *   `z1`: redshift 1, or array of redshifts.
        *   `z2`: redshift 2, or array of redshifts.
        *   Returns: result (scalar or array of distances between pairs).
    *   `calc_background(params)`: Calculate the background evolution and thermal history.
        *   `params`: `CAMBparams` instance to use.
    *   `calc_background_no_thermo(params, do_reion=False)`: Calculate background evolution without thermal/ionization history.
        *   `params`: `CAMBparams` instance to use.
        *   `do_reion`: whether to initialize the reionization model.
    *   `calc_power_spectra(params=None)`: Calculates transfer functions and power spectra.
        *   `params`: optional `CAMBparams` instance with parameters to use.
    *   `calc_transfers(params, only_transfers=True, only_time_sources=False)`: Calculate the transfer functions.
        *   `params`: `CAMBparams` instance with parameters to use.
        *   `only_transfers`: only calculate transfer functions, no power spectra.
        *   `only_time_sources`: only calculate time transfer functions, no (p,l,k) transfer functions or non-linear scaling.
        *   Returns: non-zero if error, zero if OK.
    *   `comoving_radial_distance(z, tol=0.0001)`: Get comoving radial distance from us to redshift z in Mpc. Prerequisite: background/transfers/power calculated.
        *   `z`: redshift.
        *   `tol`: numerical tolerance parameter.
        *   Returns: comoving radial distance (Mpc).
    *   `conformal_time(z, presorted=None, tol=None)`: Conformal time from hot big bang to redshift z in Megaparsec.
        *   `z`: redshift or array of redshifts.
        *   `presorted`: if True, redshifts sorted ascending; if False, descending; if None, unsorted. No checks if True/False.
        *   `tol`: integration tolerance.
        *   Returns: eta(z)/Mpc.
    *   `conformal_time_a1_a2(a1, a2)`: Get conformal time between two scale factors.
        *   `a1`: scale factor 1.
        *   `a2`: scale factor 2.
        *   Returns: eta(a2)-eta(a1) in Megaparsec.
    *   `copy()`: Make an independent copy of this object. Returns: a deep copy of self.
    *   `cosmomc_theta()`: Get θMC, an approximation of the ratio of the sound horizon to the angular diameter distance at recombination. Returns: θMC.
    *   `classmethod dict(state)`: Make an instance from a dictionary of field values.
        *   `state`: dictionary of values.
        *   Returns: new instance.
    *   `get_BAO(redshifts, params)`: Get BAO parameters at given redshifts.
        *   `redshifts`: list of redshifts.
        *   `params`: optional `CAMBparams` instance to use.
        *   Returns: array of rs/DV, H, DA, F\_AP for each redshift as 2D array.
    *   `get_Omega(var, z=0)`: Get density relative to critical density of variable `var`.
        *   `var`: one of 'K', 'cdm', 'baryon', 'photon', 'neutrino' (massless), 'nu' (massive neutrinos), 'de'.
        *   `z`: redshift.
        *   Returns: Ωi(a).
    *   `get_background_densities(a, vars=['tot', 'K', 'cdm', 'baryon', 'photon', 'neutrino', 'nu', 'de'], format='dict')`: Get individual densities vs scale factor. Returns 8πGa⁴ρi in Mpc units.
        *   `a`: scale factor or array of scale factors.
        *   `vars`: list of variables to output (default all).
        *   `format`: 'dict' or 'array'.
        *   Returns: n\_a x len(vars) 2D numpy array or dict of 1D arrays.
    *   `get_background_outputs()`: Get BAO values for redshifts set in `Params.z_outputs`. Returns: rs/DV, H, DA, F\_AP for each requested redshift (as 2D array).
    *   `get_background_redshift_evolution(z, vars=[...], format='dict')`: Get evolution of background variables vs redshift. (a and H only via `get_time_evolution`).
        *   `z`: array of requested redshifts to output.
        *   `vars`: list of variable names to output (e.g., 'x\_e', 'opacity', 'visibility', etc.).
        *   `format`: 'dict' or 'array'.
        *   Returns: n\_eta x len(vars) 2D numpy array or dict of 1D arrays.
    *   `get_background_time_evolution(eta, vars=[...], format='dict')`: Get evolution of background variables vs conformal time. (a and H only via this method for now).
        *   `eta`: array of requested conformal times to output.
        *   `vars`: list of variable names to output.
        *   `format`: 'dict' or 'array'.
        *   Returns: n\_eta x len(vars) 2D numpy array or dict of 1D arrays.
    *   `get_cmb_correlation_functions(params=None, lmax=None, spectrum='lensed_scalar', xvals=None, sampling_factor=1)`: Get CMB correlation functions from power spectra.
        *   `params`: optional `CAMBparams` instance. If None, uses previously set parameters and assumes `calc_power_spectra` was called.
        *   `lmax`: optional maximum L to use from the cls arrays.
        *   `spectrum`: type of CMB power spectrum to get; default 'lensed\_scalar', one of ['total', 'unlensed\_scalar', 'unlensed\_total', 'lensed\_scalar', 'tensor'].
        *   `xvals`: optional array of cos(θ) values at which to calculate correlation function. If None, uses Legendre roots.
        *   `sampling_factor`: multiple of lmax for the Gauss-Legendre order if `xvals` not given (default 1).
        *   Returns: if `xvals` not given: (corrs, xvals, weights); if `xvals` specified: just corrs. `corrs` is 2D array corrs[i, ix] (ix=0,1,2,3 for T, Q+U, Q-U, cross).
    *   `get_cmb_power_spectra(params=None, lmax=None, spectra=('total', ...), CMB_unit=None, raw_cl=False)`: Get CMB power spectra.
        *   `params`: optional `CAMBparams` instance. If None, uses previous params and assumes `calc_power_spectra` called.
        *   `lmax`: maximum L. If None, uses appropriate `lmax` for lensed spectra.
        *   `spectra`: list/tuple of names of spectra to get (e.g., 'total', 'unlensed\_scalar', 'lensed\_scalar', 'tensor', 'lens\_potential').
        *   `CMB_unit`: scale results. 'muK' for μK² units (CMB Cl) / μK units (lensing cross).
        *   `raw_cl`: return Cl rather than l(l+1)Cl/2π.
        *   Returns: dictionary of power spectrum arrays (shape [0..lmax, 0..3] for TT, EE, BB, TE), indexed by names. Lens potential is deflection power.
    *   `get_cmb_transfer_data(tp='scalar')`: Get Cl transfer functions. Returns: `ClTransferData` instance.
    *   `get_cmb_unlensed_scalar_array_dict(params=None, lmax=None, CMB_unit=None, raw_cl=False)`: Get all unlensed auto and cross power spectra, including custom sources.
        *   `params`: optional `CAMBparams` instance. If None, assumes `calc_power_spectra` called.
        *   `lmax`: maximum l.
        *   `CMB_unit`: scale results ('muK').
        *   `raw_cl`: return Cl rather than l(l+1)Cl/2π.
        *   Returns: dictionary of power spectrum arrays, index as TxT, TxE, PxW1, etc. P is lensing deflection, Wx are lensing convergence windows.
    *   `get_dark_energy_rho_w(a)`: Get dark energy density (relative to today) and equation of state parameter w.
        *   `a`: scalar factor or array of scale factors.
        *   Returns: rho, w arrays or scalars.
    *   `get_derived_params()`: Returns: dictionary of derived parameter values, indexed by name ('kd', 'age', etc..).
    *   `get_fsigma8()`: Get fσ8 growth values. Prerequisite: `calc_power_spectra`. Definition follows Planck 2015. Returns: array of f\*sigma\_8 values (increasing time/decreasing redshift).
    *   `get_lens_potential_cls(lmax=None, CMB_unit=None, raw_cl=False)`: Get lensing deflection potential power spectrum and cross-correlation with T, E. Prerequisite: power spectra calculated. Power is [L(L+1)]²CφL / 2π.
        *   `lmax`: lmax to output to.
        *   `CMB_unit`: scale results ('muK' for μK units).
        *   `raw_cl`: return lensing potential CL rather than [L(L+1)]²CL/2π.
        *   Returns: numpy array CL[0:lmax+1, 0:3], where 0..2 indexes PP, PT, PE.
    *   `get_lensed_cls_with_spectrum(clpp, lmax=None, CMB_unit=None, raw_cl=False)`: Get lensed CMB power spectra using a provided lensing spectrum `clpp`.
        *   `clpp`: array of [L(L+1)]²CφL / 2π lensing potential power spectrum (zero based).
        *   `lmax`: lmax to output to.
        *   `CMB_unit`: scale results ('muK').
        *   `raw_cl`: return Cl rather than l(l+1)Cl/2π.
        *   Returns: numpy array CL[0:lmax+1, 0:4] (TT, EE, BB, TE).
    *   `get_lensed_gradient_cls(lmax=None, CMB_unit=None, raw_cl=False, clpp=None)`: Get lensed gradient scalar CMB power spectra (flat sky approx, arXiv:1101.2234). Prerequisite: lensed power spectra calculated.
        *   `lmax`: lmax to output to.
        *   `CMB_unit`: scale results ('muK').
        *   `raw_cl`: return Cl rather than l(l+1)Cl/2π.
        *   `clpp`: custom array of [L(L+1)]²CφL / 2π lensing potential power spectrum.
        *   Returns: numpy array CL[0:lmax+1, 0:8]. Indices correspond to TVT, EVE, B∇B, PP⊥, TVE, TP⊥, (∇T)², ∇T∇T.
    *   `get_lensed_scalar_cls(lmax=None, CMB_unit=None, raw_cl=False)`: Get lensed scalar CMB power spectra. Prerequisite: power spectra calculated. Returns: numpy array CL[0:lmax+1, 0:4] (TT, EE, BB, TE).
    *   `get_linear_matter_power_spectrum(var1=None, var2=None, hubble_units=True, k_hunit=True, have_power_spectra=True, params=None, nonlinear=False)`: Calculates linear Pxy(k). Output k not regularly spaced. See `Matter power spectrum... variables`.
        *   `var1`, `var2`: variable index or name (default `delta_tot`).
        *   `hubble_units`: if true, output in (Mpc/h)³ units, else Mpc³.
        *   `k_hunit`: if true, power is function of k/h, else k (Mpc⁻¹).
        *   `have_power_spectra`: set to False if not already computed.
        *   `params`: if `have_power_spectra=False`, optional `CAMBparams` instance.
        *   `nonlinear`: include non-linear correction (Halofit).
        *   Returns: (k/h or k, z, PK), where PK[i,j] is value at z[i], k[j].
    *   `get_matter_power_interpolator(nonlinear=True, ..., silent=False)`: Return 2D spline interpolation object for matter power spectrum P(z, k/h or k). Prerequisite: transfers calculated. Uses `self.Params.Transfer.PK_redshifts`.
        *   (See `camb.get_matter_power_interpolator` for parameters `nonlinear` to `silent`).
        *   Returns: `RectBivariateSpline`-based object PK callable as PK.P(z,kh). If `return_z_k=True`, returns (interpolator, z, k).
    *   `get_matter_power_spectrum(minkh=0.0001, maxkh=1.0, npoints=100, var1=None, var2=None, have_power_spectra=False, params=None)`: Calculates Pxy(k/h). Output k regularly log spaced and interpolated. If `NonLinear` set, result is non-linear.
        *   `minkh`: minimum value of k/h for output grid.
        *   `maxkh`: maximum value of k/h.
        *   `npoints`: number of points equally spaced in log k.
        *   `var1`, `var2`: variable index or name (default `delta_tot`).
        *   `have_power_spectra`: set to True if already computed.
        *   `params`: if `have_power_spectra=False`, optional `CAMBparams` instance.
        *   Returns: (kh, z, PK), where PK[i,j] is value at z[i], k/h[j].
    *   `get_matter_transfer_data()`: Get matter transfer function data and sigma8. Returns: `MatterTransferData` instance.
    *   `get_nonlinear_matter_power_spectrum(var1=None, ..., params=None)`: Calculates non-linear Pxy(k/h). Output k not regularly spaced. See `Matter power spectrum... variables`.
        *   (See `get_linear_matter_power_spectrum` for parameters `var1` to `params`).
        *   Returns: (k/h or k, z, PK), where PK[i,j] is value at z[i], k[j].
    *   `get_partially_lensed_cls(Alens, lmax=None, CMB_unit=None, raw_cl=False)`: Get lensed CMB Cls using true lensing spectrum scaled by `Alens`.
        *   `Alens`: scaling of lensing (scalar or array vs L). `Alens=1` is standard.
        *   `lmax`: lmax to output to.
        *   `CMB_unit`: scale results ('muK').
        *   `raw_cl`: return Cl rather than l(l+1)Cl/2π.
        *   Returns: numpy array CL[0:lmax+1, 0:4] (TT, EE, BB, TE).
    *   `get_redshift_evolution(q, z, vars=[...], lAccuracyBoost=4)`: Get mode evolution vs redshift for given k values.
        *   `q`: wavenumber value(s) to calculate (Mpc⁻¹).
        *   `z`: array of redshifts to output.
        *   `vars`: list of variable names or `camb.symbolic` expressions.
        *   `lAccuracyBoost`: boost factor for ell accuracy.
        *   Returns: nd array A\_{qti}, size(q) x size(z) x len(vars).
    *   `get_sigma8()`: Get σ8 values at `Params.PK_redshifts`. Prerequisite: power spectra calculated. Returns: array of σ8 values (increasing time/decreasing redshift).
    *   `get_sigma8_0()`: Get σ8 value today. Prerequisite: power spectra calculated. Returns: σ8 today (scalar).
    *   `get_sigmaR(R, z_indices=None, var1=None, var2=None, hubble_units=True, return_R_z=False)`: Calculate σR, RMS linear matter fluctuation in spheres of radius R.
        *   `R`: radius in Mpc or h⁻¹ Mpc units (scalar or array).
        *   `z_indices`: indices of redshifts in `Params.Transfer.PK_redshifts` (default None=all, -1=redshift 0).
        *   `var1`, `var2`: variable index or name (default `delta_tot`).
        *   `hubble_units`: if true, R is in h⁻¹ Mpc, otherwise Mpc.
        *   `return_R_z`: if true, return tuple of (R, z, sigmaR) where R is always Mpc.
        *   Returns: array of σR values, or 2D array indexed by (redshift, R).
    *   `get_source_cls_dict(params=None, lmax=None, raw_cl=False)`: Get all source window function + CMB lensing cross power spectra. Does not include CMB spectra. Note P is deflection angle, lensing windows Wx return kappa power.
        *   `params`: optional `CAMBparams` instance. If None, assumes `calc_power_spectra` called.
        *   `lmax`: maximum l.
        *   `raw_cl`: return Cl rather than l(l+1)Cl/2π.
        *   Returns: dictionary of power spectrum arrays, index as PxP, PxW1, W1xW2, etc.
    *   `get_tensor_cls(lmax=None, CMB_unit=None, raw_cl=False)`: Get tensor CMB power spectra. Prerequisite: power spectra calculated. Returns: numpy array CL[0:lmax+1, 0:4] (TT, EE, BB, TE).
    *   `get_time_evolution(q, eta, vars=[...], lAccuracyBoost=4, frame='CDM')`: Get mode evolution vs conformal time for given k values.
        *   `q`: wavenumber value(s) to calculate (Mpc⁻¹).
        *   `eta`: array of requested conformal times to output.
        *   `vars`: list of variable names or `camb.symbolic` expressions.
        *   `lAccuracyBoost`: factor to increase l\_max in hierarchies.
        *   `frame`: for symbolic expressions, frame name if variable is not gauge invariant.
        *   Returns: nd array A\_{qti}, size(q) x size(times) x len(vars).
    *   `get_total_cls(lmax=None, CMB_unit=None, raw_cl=False)`: Get lensed-scalar + tensor CMB power spectra. Prerequisite: power spectra calculated. Returns: numpy array CL[0:lmax+1, 0:4] (TT, EE, BB, TE).
    *   `get_unlensed_scalar_array_cls(lmax=None)`: Get array of all unlensed cross power spectra (dimensionless, not scaled). Prerequisite: power spectra calculated. Returns: numpy array CL[0:, 0:, 0:lmax+1], indices T, E, lensing potential, source windows.
    *   `get_unlensed_scalar_cls(lmax=None, CMB_unit=None, raw_cl=False)`: Get unlensed scalar CMB power spectra. Prerequisite: power spectra calculated. Returns: numpy array CL[0:lmax+1, 0:4] (TT, EE, BB, TE), BB is zero.
    *   `get_unlensed_total_cls(lmax=None, CMB_unit=None, raw_cl=False)`: Get unlensed CMB power spectra (scalar + tensor if relevant). Prerequisite: power spectra calculated. Returns: numpy array CL[0:lmax+1, 0:4] (TT, EE, BB, TE).
    *   `h_of_z(z)`: Get Hubble rate H(z) in Mpc⁻¹ units. Prerequisite: background/transfers/power calculated. Returns: H(z).
    *   `hubble_parameter(z)`: Get Hubble rate H(z) in km/s/Mpc units. Prerequisite: background/transfers/power calculated. Returns: H(z).
    *   `luminosity_distance(z)`: Get luminosity distance to redshift z. Prerequisite: background/transfers/power calculated.
        *   `z`: redshift or array of redshifts.
        *   Returns: luminosity distance.
    *   `physical_time(z)`: Get physical time from hot big bang to redshift z in Julian Gigayears. Returns: t(z)/Gigayear.
    *   `physical_time_a1_a2(a1, a2)`: Get physical time between two scale factors in Julian Gigayears. Prerequisite: background/transfers/power calculated. Returns: (age(a2)-age(a1))/Gigayear.
    *   `power_spectra_from_transfer(initial_power_params=None, silent=False)`: Re-calculate power spectra using a new initial power spectrum, reusing existing transfer functions. Faster but potentially inaccurate for non-linear lensing. Prerequisite: `calc_transfers` or `calc_power_spectra` called.
        *   `initial_power_params`: `InitialPower` instance or None (use current).
        *   `silent`: suppress warnings about non-linear corrections.
    *   `redshift_at_comoving_radial_distance(chi)`: Convert comoving radial distance to redshift.
        *   `chi`: comoving radial distance (in Mpc), scalar or array.
        *   Returns: redshift at chi.
    *   `redshift_at_conformal_time(eta)`: Convert conformal time to redshift. Prerequisite: background calculated with `no_thermo=False`.
        *   `eta`: conformal time from big bang (in Mpc), scalar or array.
        *   Returns: redshift at eta.
    *   `replace(instance)`: Replace content with another instance (deep copy in Fortran).
        *   `instance`: instance of the same class.
    *   `save_cmb_power_spectra(filename, lmax=None, CMB_unit='muK')`: Save CMB power to a plain text file. Output: lensed total l(l+1)Cl/2π then lensing potential/cross.
        *   `lmax`: lmax to save.
        *   `CMB_unit`: units ('muK').
    *   `set_params(params)`: Set parameters from `params`. Does not recompute. Call `calc_transfers()` if needed.
        *   `params`: a `CAMBparams` instance.
    *   `sound_horizon(z)`: Get comoving sound horizon rs(z) in Megaparsecs.
        *   `z`: redshift or array of redshifts.
        *   Returns: r\_s(z).

### `class camb.results.MatterTransferData`

*   **Purpose:** Base class for storing matter power transfer function data. Get instance via `results.CAMBdata.get_matter_transfer_data()`. See `Matter power spectrum... variables`.
*   **Variables:**
    *   `nq` (int): Number of q modes calculated.
    *   `q` (array): Array of q values calculated (k in flat universe).
    *   `sigma_8` (array): Array of σ8 values for each redshift.
    *   `sigma2_vdelta_8` (array): Array of v-delta8 correlation.
    *   `transfer_data` (numpy array): T[entry, q\_index, z\_index] storing transfer functions. `entry+1` corresponds to `Transfer_xxx` indices (1=k/h, 2=cdm, etc.).
*   **Methods:**
    *   `transfer_z(name, z_index=0)`: Get transfer function T(q) by name for a given redshift index.
        *   `name`: parameter name (`'delta_cdm'`, etc.).
        *   `z_index`: which redshift index.
        *   Returns: array of transfer function values for each calculated k (q).

### `class camb.results.ClTransferData`

*   **Purpose:** Base class for storing CMB power transfer functions T(q, l). Get instance via `results.CAMBdata.get_cmb_transfer_data()`.
*   **Variables:**
    *   `NumSources` (int): Number of sources calculated (size of p index).
    *   `q` (array): Array of q values calculated (=k in flat universe).
    *   `L` (int array): Int array of l values calculated.
    *   `delta_p_l_k` (array): Transfer functions, indexed by (source, L, q).
*   **Methods:**
    *   `get_transfer(source=0)`: Return Cl transfer functions T(l, q).
        *   `source`: index of source (0=T, 1=E, 2=lensing potential).
        *   Returns: (array of L, array of q, transfer functions T(L,q)).

## Symbolic Manipulation (`camb.symbolic`)

*   **Purpose:** Defines scalar linear perturbation equations for standard LCDM using sympy. Uses covariant notation, projections (Newtonian, synchronous), gauge invariant quantities. Conformal time variable is `t`. Provides functions to convert expressions to CAMB Fortran source code. See ScalEqs notebook.

### `camb.symbolic.LinearPerturbation(name, species=None, camb_var=None, camb_sub=None, frame_dependence=None, description=None)`

*   **Purpose:** Returns a linear perturbation variable as a sympy Function of conformal time `t`.
*   **Parameters:**
    *   `name`: sympy name for the Function.
    *   `species`: tag for the species if relevant (not used).
    *   `camb_var`: relevant CAMB fortran variable.
    *   `camb_sub`: if not equal to `camb_var`, string giving the expression in CAMB variables.
    *   `frame_dependence`: the change in the perturbation when frame 4-velocity u changes to u + delta\_frame (numpy expression involving delta\_frame).
    *   `description`: string describing variable.
*   **Returns:** sympy Function instance with attributes set to arguments.

### `camb.symbolic.camb_fortran(expr, name='camb_function', frame='CDM', expand=False)`

*   **Purpose:** Convert symbolic sympy expression to CAMB fortran code using CAMB variable notation. Handles Newtonian gauge variables (Psi\_N) and derivatives up to second order.
*   **Parameters:**
    *   `expr`: symbolic sympy expression using `camb.symbolic` variables/functions.
    *   `name`: lhs variable string to assign result to.
    *   `frame`: frame ('CDM'/'synchronous' default) in which to interpret non gauge-invariant expressions.
    *   `expand`: do a sympy expand before generating code.
*   **Returns:** fortran code snippet.

### `camb.symbolic.cdm_gauge(x)`

*   **Purpose:** Evaluates expression `x` in the CDM frame (vc = 0, A = 0), equivalent to synchronous gauge with covariant variables.
*   **Parameters:** `x`: expression.
*   **Returns:** expression evaluated in CDM frame.

### `camb.symbolic.compile_source_function_code(code_body, file_path='', compiler=None, fflags=None, cache=True)`

*   **Purpose:** Compile fortran code into function pointer in shared library for passing back to CAMB.
*   **Parameters:**
    *   `code_body`: fortran code to do calculation and assign `sources(i)` output array.
    *   `file_path`: optional output path for generated f90 code.
    *   `compiler`: compiler executable (usually on path).
    *   `fflags`: options for compiler.
    *   `cache`: whether to cache the result.
*   **Returns:** function pointer for compiled code.

### `class camb.symbolic.f_K(*args)`

*   **Purpose:** Represents the curvature-dependent factor K in perturbation equations.

### `camb.symbolic.get_hierarchies(lmax=5)`

*   **Purpose:** Get Boltzmann hierarchies up to `lmax` for photons (J), E polarization, massless neutrinos (G).
*   **Parameters:** `lmax`: maximum multipole.
*   **Returns:** list of equations.

### `camb.symbolic.get_scalar_temperature_sources(checks=False)`

*   **Purpose:** Derives terms in line-of-sight source after integration by parts (integrated against Bessel function).
*   **Parameters:** `checks`: True to do consistency checks on result.
*   **Returns:** (monopole\_source, ISW, doppler, quadrupole\_source).

### `camb.symbolic.make_frame_invariant(expr, frame='CDM')`

*   **Purpose:** Makes the quantity `expr` gauge invariant, assuming it's currently evaluated in `frame`.
*   **Parameters:**
    *   `expr`: expression to make invariant.
    *   `frame`: string frame name ('CDM', 'Newtonian', etc.) or a variable that is zero in the current frame (e.g., `Delta_g` for constant photon density frame).

### `camb.symbolic.newtonian_gauge(x)`

*   **Purpose:** Evaluates expression `x` in the Newtonian gauge (zero shear, sigma=0). Converts to conventional metric perturbation variables Psi\_N, Phi\_N.
*   **Parameters:** `x`: expression.
*   **Returns:** expression evaluated in the Newtonian gauge.

### `camb.symbolic.synchronous_gauge(x)`

*   **Purpose:** Evaluates expression `x` in the synchronous gauge, using conventional synchronous-gauge variables.
*   **Parameters:** `x`: expression.
*   **Returns:** synchronous gauge variable expression.

## BBN Models (`camb.bbn`)

### `class camb.bbn.BBNIterpolator(x, y, z, bbox=[None, None, None, None], kx=3, ky=3, s=0)`

*   Base class for BBN interpolation, likely uses `scipy.interpolate.RectBivariateSpline`.

### `class camb.bbn.BBNPredictor`

*   **Purpose:** Abstract base class for making BBN predictions for Helium abundance.
*   **Methods:**
    *   `Y_He(ombh2, delta_neff=0.0)`: Get BBN helium mass fraction (Y\_He) for CMB code.
        *   `ombh2`: Ωbh².
        *   `delta_neff`: additional N\_eff relative to standard value (of 3.044).
        *   Returns: Y\_He helium mass fraction predicted by BBN.
    *   `Y_p(ombh2, delta_neff=0.0)`: Get BBN helium nucleon fraction (Y\_p). Must be implemented by extensions.
        *   `ombh2`: Ωbh².
        *   `delta_neff`: additional N\_eff relative to standard value (of 3.044).
        *   Returns: Y\_p helium nucleon fraction predicted by BBN.

### `class camb.bbn.BBN_fitting_parthenope(tau_neutron=None)`

*   **Purpose:** Old BBN predictions using fitting formulae based on Parthenope (pre 2015).
*   **Methods:**
    *   `Y_p(ombh2, delta_neff=0.0, tau_neutron=None)`: Get BBN helium nucleon fraction (Y\_p). Uses Planck 2015 paper fits.
        *   `ombh2`: Ωbh².
        *   `delta_neff`: additional N\_eff relative to standard value (of 3.046 for consistency with Planck).
        *   `tau_neutron`: neutron lifetime.
        *   Returns: Yp BBN helium nucleon fraction predicted by BBN.

### `class camb.bbn.BBN_table_interpolator(interpolation_table='PRIMAT_Yp_DH_ErrorMC_2021.dat', function_of=('ombh2', 'DeltaN'))`

*   **Purpose:** BBN predictor based on interpolation from a numerical table (e.g., Parthenope 2017, PRIMAT).
*   **Parameters:**
    *   `interpolation_table`: filename of interpolation table to use. Supplied tables include PArthENoPE\_880.2\_{standard,marcucci}.dat, PRIMAT\_Yp\_DH\_Error{,MC}\_2021.dat.
    *   `function_of`: two variables determining the interpolation grid (x,y) in the table, matching column labels.
*   **Methods:**
    *   `DH(ombh2, delta_neff=0.0, grid=False)`: Get deuterium ratio D/H by interpolation.
        *   `ombh2`: Ωbh² (or value of `function_of[0]`).
        *   `delta_neff`: additional N\_eff (or value of `function_of[1]`).
        *   `grid`: parameter for `RectBivariateSpline` (evaluate on grid or at points).
        *   Returns: D/H.
    *   `Y_p(ombh2, delta_neff=0.0, grid=False)`: Get BBN helium nucleon fraction (Y\_p) by interpolation. Call `Y_He()` for mass fraction.
        *   `ombh2`: Ωbh² (or value of `function_of[0]`).
        *   `delta_neff`: additional N\_eff (or value of `function_of[1]`).
        *   `grid`: parameter for `RectBivariateSpline`.
        *   Returns: Y\_p helium nucleon fraction predicted by BBN.
    *   `get(name, ombh2, delta_neff=0.0, grid=False)`: Get value for variable `name` by interpolation from table column header comment. Example: `get('sig(D/H)', 0.0222, 0)`.
        *   `name`: string name of the parameter in header.
        *   `ombh2`: Ωbh² (or value of `function_of[0]`).
        *   `delta_neff`: additional N\_eff (or value of `function_of[1]`).
        *   `grid`: parameter for `RectBivariateSpline`.
        *   Returns: Interpolated value (or grid).

### `camb.bbn.get_predictor(predictor_name=None)`

*   **Purpose:** Get instance of default `BBNPredictor` class. Currently numerical table interpolation as Planck 2018 analysis.
*   **Parameters:** `predictor_name`: name of predictor (optional).
*   **Returns:** Instance of the default BBN predictor.

## Dark Energy Models (`camb.dark_energy`)

### `class camb.dark_energy.DarkEnergyModel(*args, **kwargs)`

*   **Purpose:** Abstract base class for dark energy model implementations.

### `class camb.dark_energy.DarkEnergyEqnOfState(*args, **kwargs)`

*   **Purpose:** Base class for models using w and wa parameterization (`w(a) = w + (1-a)*wa`) or tabulated `w(a)`.
*   **Bases:** `DarkEnergyModel`
*   **Variables:**
    *   `w` (float64): w(0).
    *   `wa` (float64): -dw/da(0).
    *   `cs2` (float64): fluid rest-frame sound speed squared.
    *   `use_tabulated_w` (boolean): using an interpolated tabulated w(a) rather than w, wa above.
*   **Methods:**
    *   `set_params(w=-1.0, wa=0, cs2=1.0)`: Set parameters for `w(a) = w + (1-a)*wa`.
        *   `w`: w(0).
        *   `wa`: -dw/da(0).
        *   `cs2`: fluid rest-frame sound speed squared.
    *   `set_w_a_table(a, w)`: Set w(a) from numerical values (uses cubic spline).
        *   `a`: array of scale factors.
        *   `w`: array of w(a).
        *   Returns: `self`.

### `class camb.dark_energy.DarkEnergyFluid(*args, **kwargs)`

*   **Purpose:** Implements w, wa or splined w(a) using constant sound-speed single fluid model (like single-field quintessence).
*   **Bases:** `DarkEnergyEqnOfState`
*   **Methods:**
    *   `set_w_a_table(a, w)`: Set w(a) from numerical values (uses cubic spline). Returns: `self`.

### `class camb.dark_energy.DarkEnergyPPF(*args, **kwargs)`

*   **Purpose:** Implements w, wa or splined w(a) using the PPF perturbation approximation (arXiv:0808.3125). Allows w crossing -1 smoothly but is not physical.
*   **Bases:** `DarkEnergyEqnOfState`

### `class camb.dark_energy.Quintessence(*args, **kwargs)`

*   **Purpose:** Abstract base class for single scalar field quintessence models. Requires defining a new derived class in Fortran.
*   **Bases:** `DarkEnergyModel`
*   **Variables:**
    *   `DebugLevel` (integer).
    *   `astart` (float64).
    *   `integrate_tol` (float64).
    *   `sampled_a` (float64 array).
    *   `phi_a` (float64 array).
    *   `phidot_a` (float64 array).

### `class camb.dark_energy.EarlyQuintessence(*args, **kwargs)`

*   **Purpose:** Example early quintessence (axion-like, arXiv:1908.06995) with potential V(phi) = m²f²(1 - cos(phi/f))^n + Lambda.
*   **Bases:** `Quintessence`
*   **Variables:**
    *   `n` (float64): power index for potential.
    *   `f` (float64): f/Mpl (sqrt(8piG)f); only used for initial search value when `use_zc` is True.
    *   `m` (float64): mass parameter in reduced Planck units; only used for initial search value when `use_zc` is True.
    *   `theta_i` (float64): phi/f initial field value.
    *   `frac_lambda0` (float64): fraction of dark energy in cosmological constant today (approximated as 1).
    *   `use_zc` (boolean): solve for f, m to get specific critical redshift zc and fde\_zc.
    *   `zc` (float64): redshift of peak fractional early dark energy density.
    *   `fde_zc` (float64): fraction of early dark energy density to total at peak.
    *   `npoints` (integer): number of points for background integration spacing.
    *   `min_steps_per_osc` (integer): minimum number of steps per background oscillation scale.
    *   `fde` (float64 array): after initialized, the calculated background early dark energy fractions at `sampled_a`.

### `class camb.dark_energy.AxionEffectiveFluid(*args, **kwargs)`

*   **Purpose:** Example implementation of a specific (early) dark energy fluid model (arXiv:1806.10608).
*   **Bases:** `DarkEnergyModel`
*   **Variables:**
    *   `w_n` (float64): effective equation of state parameter.
    *   `fde_zc` (float64): energy density fraction at z=zc.
    *   `zc` (float64): decay transition redshift (not same as peak of energy density fraction).
    *   `theta_i` (float64): initial condition field value.

## Initial Power Spectra (`camb.initialpower`)

### `class camb.initialpower.InitialPower(*args, **kwargs)`

*   **Purpose:** Abstract base class for initial power spectrum classes.

### `class camb.initialpower.InitialPowerLaw(*args, **kwargs)`

*   **Purpose:** Object storing parameters for the primordial power spectrum in the standard power law expansion.
*   **Bases:** `InitialPower`
*   **Variables:**
    *   `tensor_parameterization` (integer/string): one of: `tensor_param_indeptilt`, `tensor_param_rpivot`, `tensor_param_AT`.
    *   `ns` (float64): Scalar spectral index n\_s.
    *   `nrun` (float64): Running of scalar spectral index dn\_s/dlogk.
    *   `nrunrun` (float64): Running of running d²n\_s/d(logk)².
    *   `nt` (float64): Tensor spectral index n\_t.
    *   `ntrun` (float64): Running of tensor spectral index.
    *   `r` (float64): Tensor to scalar ratio at pivot.
    *   `pivot_scalar` (float64): Pivot scale for scalar spectrum.
    *   `pivot_tensor` (float64): Pivot scale for tensor spectrum.
    *   `As` (float64): Comoving curvature power at k=pivot\_scalar (A\_s).
    *   `At` (float64): Tensor amplitude at k=pivot\_tensor (A\_t).
*   **Methods:**
    *   `has_tensors()`: Do these settings have non-zero tensors? Returns: True if non-zero tensor amplitude.
    *   `set_params(As=2e-09, ns=0.96, nrun=0, nrunrun=0.0, r=0.0, nt=None, ntrun=0.0, pivot_scalar=0.05, pivot_tensor=0.05, parameterization='tensor_param_rpivot')`: Set parameters using standard power law parameterization. If `nt=None`, uses inflation consistency relation.
        *   Parameters: `As`, `ns`, `nrun`, `nrunrun`, `r`, `nt`, `ntrun`, `pivot_scalar`, `pivot_tensor`, `parameterization`.
        *   Returns: `self`.

### `class camb.initialpower.SplinedInitialPower(*args, **kwargs)`

*   **Purpose:** Object to store a generic primordial spectrum set from tabulated k\_i, P(k\_i) values.
*   **Bases:** `InitialPower`
*   **Variables:**
    *   `effective_ns_for_nonlinear` (float64): Effective n\_s to use for approximate non-linear correction models.
*   **Methods:**
    *   `has_tensors()`: Is the tensor spectrum set? Returns: True if tensors.
    *   `set_scalar_log_regular(kmin, kmax, PK)`: Set log-regular cubic spline interpolation for P(k).
        *   `kmin`: minimum k value (not minimum log(k)).
        *   `kmax`: maximum k value (inclusive).
        *   `PK`: array of scalar power spectrum values, with `PK[0]=P(kmin)` and `PK[-1]=P(kmax)`.
    *   `set_scalar_table(k, PK)`: Set arrays of k and P(k) values for cubic spline interpolation.
        *   `k`: array of k values (Mpc⁻¹).
        *   `PK`: array of scalar power spectrum values.
    *   `set_tensor_log_regular(kmin, kmax, PK)`: Set log-regular cubic spline interpolation for tensor spectrum P\_t(k).
        *   `kmin`: minimum k value.
        *   `kmax`: maximum k value (inclusive).
        *   `PK`: array of tensor power spectrum values, with `PK[0]=P_t(kmin)` and `PK[-1]=P_t(kmax)`.
    *   `set_tensor_table(k, PK)`: Set arrays of k and P\_t(k) values for cubic spline interpolation.
        *   `k`: array of k values (Mpc⁻¹).
        *   `PK`: array of tensor power spectrum values.

## Non-linear Models (`camb.nonlinear`)

### `class camb.nonlinear.NonLinearModel(*args, **kwargs)`

*   **Purpose:** Abstract base class for non-linear correction models.
*   **Variables:**
    *   `Min_kh_nonlinear` (float64): minimum k/h at which to apply non-linear corrections.

### `class camb.nonlinear.Halofit(*args, **kwargs)`

*   **Purpose:** Various specific approximate non-linear correction models based on HaloFit.
*   **Bases:** `NonLinearModel`
*   **Variables:**
    *   `halofit_version` (integer/string): one of: 'original', 'bird', 'peacock', 'takahashi', 'mead', 'halomodel', 'casarini', 'mead2015', 'mead2016', 'mead2020', 'mead2020\_feedback'.
    *   `HMCode_A_baryon` (float64): HMcode parameter A\_baryon.
    *   `HMCode_eta_baryon` (float64): HMcode parameter eta\_baryon.
    *   `HMCode_logT_AGN` (float64): HMcode parameter log10(T\_AGN/K).
*   **Methods:**
    *   `set_params(halofit_version='mead2020', HMCode_A_baryon=3.13, HMCode_eta_baryon=0.603, HMCode_logT_AGN=7.8)`: Set the halofit model for non-linear corrections.
        *   `halofit_version`: Name of the model (see Variables list for options and references).
        *   `HMCode_A_baryon`: HMcode parameter A\_baryon (Default 3.13, used only in mead2015/mead2016/mead).
        *   `HMCode_eta_baryon`: HMcode parameter eta\_baryon (Default 0.603, used only in mead2015/mead2016/mead).
        *   `HMCode_logT_AGN`: HMcode parameter logT\_AGN (Default 7.8, used only in mead2020\_feedback).

### `class camb.nonlinear.SecondOrderPK(*args, **kwargs)`

*   **Purpose:** Third-order Newtonian perturbation theory results for non-linear correction. Intended for high redshift (z>10). Mainly an example implementation. See Appendix F of astro-ph/0702600.
*   **Bases:** `NonLinearModel`

## Reionization Models (`camb.reionization`)

### `class camb.reionization.ReionizationModel(*args, **kwargs)`

*   **Purpose:** Abstract base class for reionization models.
*   **Variables:**
    *   `Reionization` (boolean): Is there reionization?

### `class camb.reionization.BaseTauWithHeReionization(*args, **kwargs)`

*   **Purpose:** Abstract class for models that map z\_re to tau, and include second reionization of Helium.
*   **Bases:** `ReionizationModel`
*   **Variables:**
    *   `use_optical_depth` (boolean): Whether to use the optical depth or redshift parameters.
    *   `redshift` (float64): Reionization redshift (xe=0.5) if `use_optical_depth=False`.
    *   `optical_depth` (float64): Optical depth if `use_optical_depth=True`.
    *   `fraction` (float64): Reionization fraction when complete, or -1 for full ionization of H and first of He.
    *   `include_helium_fullreion` (boolean): Whether to include second reionization of helium.
    *   `helium_redshift` (float64): Redshift for second reionization of helium.
    *   `helium_delta_redshift` (float64): Width in redshift for second reionization of helium.
    *   `helium_redshiftstart` (float64): Include second helium reionization below this redshift.
    *   `tau_solve_accuracy_boost` (float64): Accuracy boosting parameter for solving for z\_re from tau.
    *   `timestep_boost` (float64): Accuracy boosting parameter for the minimum number of time sampling steps through reionization.
    *   `max_redshift` (float64): Maximum redshift allowed when mapping tau into reionization redshift.
*   **Methods:**
    *   `get_zre(params, tau=None)`: Get the midpoint redshift of reionization.
        *   `params`: `model.CAMBparams` instance.
        *   `tau`: if set, calculate redshift for this optical depth, else use current parameters.
        *   Returns: reionization mid-point redshift.
    *   `set_extra_params(max_zrei=None)`: Set extra parameters (not tau or zrei).
        *   `max_zrei`: maximum redshift allowed when mapping tau into reionization redshift.
    *   `set_tau(tau)`: Set the optical depth.
        *   `tau`: optical depth.
        *   Returns: `self`.
    *   `set_zrei(zrei)`: Set the mid-point reionization redshift.
        *   `zrei`: mid-point redshift.
        *   Returns: `self`.

### `class camb.reionization.TanhReionization(*args, **kwargs)`

*   **Purpose:** Default (unphysical) tanh x\_e parameterization (Appendix B of arXiv:0804.3865).
*   **Bases:** `BaseTauWithHeReionization`
*   **Variables:**
    *   `delta_redshift` (float64): Duration of reionization.
*   **Methods:**
    *   `set_extra_params(deltazrei=None, max_zrei=None)`: Set extra parameters.
        *   `deltazrei`: delta z for reionization.
        *   `max_zrei`: maximum redshift allowed when mapping tau into reionization.

### `class camb.reionization.ExpReionization(*args, **kwargs)`

*   **Purpose:** Ionization fraction decreases exponentially at high z, saturating to fully ionized at fixed redshift. Has minimum tau ~0.04 for `reion_redshift_complete=6.1`. Similar to arXiv:1509.02785, arXiv:2006.16828.
*   **Bases:** `BaseTauWithHeReionization`
*   **Variables:**
    *   `reion_redshift_complete` (float64): end of reionization redshift.
    *   `reion_exp_smooth_width` (float64): redshift scale to smooth exponential.
    *   `reion_exp_power` (float64): power in exponential decay `exp(-lambda(z-redshift_complete)^exp_power)`.
*   **Methods:**
    *   `set_extra_params(reion_redshift_complete=None, reion_exp_power=None, reion_exp_smooth_width=None, max_zrei=None)`: Set extra parameters.
        *   `reion_redshift_complete`: redshift at which reionization complete (e.g. around 6).
        *   `reion_exp_power`: power in exponential decay with redshift.
        *   `reion_exp_smooth_width`: smoothing parameter to keep derivative smooth.
        *   `max_zrei`: maximum redshift allowed when mapping tau into reionization.

## Recombination Models (`camb.recombination`)

### `class camb.recombination.RecombinationModel(*args, **kwargs)`

*   **Purpose:** Abstract base class for recombination models.
*   **Variables:**
    *   `min_a_evolve_Tm` (float64): minimum scale factor at which to solve matter temperature perturbation if evolving sound speed or ionization fraction perturbations.

### `class camb.recombination.Recfast(*args, **kwargs)`

*   **Purpose:** RECFAST recombination model.
*   **Bases:** `RecombinationModel`
*   **Variables:**
    *   `RECFAST_fudge` (float64).
    *   `RECFAST_fudge_He` (float64).
    *   `RECFAST_Heswitch` (integer).
    *   `RECFAST_Hswitch` (boolean).
    *   `AGauss1` (float64).
    *   `AGauss2` (float64).
    *   `zGauss1` (float64).
    *   `zGauss2` (float64).
    *   `wGauss1` (float64).
    *   `wGauss2` (float64).

### `class camb.recombination.CosmoRec(*args, **kwargs)`

*   **Purpose:** CosmoRec recombination model. Requires CosmoRec library installed and Makefile configured. Needs `-fPIC` flag for CosmoRec compilation.
*   **Bases:** `RecombinationModel`
*   **Variables:**
    *   `runmode` (integer): Default 0 (with diffusion); 1 (without diffusion); 2 (RECFAST++); 3 (RECFAST++ with correction).
    *   `fdm` (float64): Dark matter annihilation efficiency.
    *   `accuracy` (float64): 0-normal, 3-most accurate.

### `class camb.recombination.HyRec(*args, **kwargs)`

*   **Purpose:** HyRec recombination model. Requires HyRec library installed and Makefile configured.
*   **Bases:** `RecombinationModel`

## Source Windows Functions (`camb.sources`)

### `class camb.sources.SourceWindow(*args, **kwargs)`

*   **Purpose:** Abstract base class for number count/lensing/21cm source window function. Assign list to `SourceWindows` field of `model.CAMBparams`. Currently only usable in flat models.
*   **Variables:**
    *   `source_type` (integer/string): one of: '21cm', 'counts', 'lensing'.
    *   `bias` (float64): Bias parameter.
    *   `dlog10Ndm` (float64): Evolution parameter?

### `class camb.sources.GaussianSourceWindow(*args, **kwargs)`

*   **Purpose:** A Gaussian W(z) source window function.
*   **Bases:** `SourceWindow`
*   **Variables:**
    *   `redshift` (float64): Mean redshift.
    *   `sigma` (float64): Standard deviation in redshift.

### `class camb.sources.SplinedSourceWindow(*args, **kwargs)`

*   **Purpose:** A numerical W(z) source window function constructed by interpolation from a table.
*   **Bases:** `SourceWindow`
*   **Methods:**
    *   `set_table(z, W, bias_z=None, k_bias=None, bias_kz=None)`: Set arrays for spline interpolation. W(z) is total count distribution.
        *   `z`: array of redshift values (monotonically increasing).
        *   `W`: array of window function values.
        *   `bias_z`: optional array of bias values at each z (scale-independent).
        *   `k_bias`: optional array of k values for bias (Mpc⁻¹).
        *   `bias_kz`: optional 2D contiguous array for space-dependent bias(k, z).

## Correlation Functions (`camb.correlations`)

*   **Purpose:** Transform CMB Cls <-> correlation functions, calculate lensed power spectra. Pure python/scipy. Operate on Cls including `l(l+1)/2pi` (CMB) or `[L(L+1)]²/2pi` (lensing) factors.

### `camb.correlations.cl2corr(cls, xvals, lmax=None)`

*   **Purpose:** Get correlation function from power spectra at points `cos(theta) = xvals`. Use Legendre roots for `xvals` for accurate back-integration.
*   **Parameters:**
    *   `cls`: 2D array `cls(L,ix)` (L=ell starting at 0, ix=0,1,2,3 for TT, EE, BB, TE). Must include `l(l+1)/2pi` factors.
    *   `xvals`: array of `cos(theta)` values.
    *   `lmax`: optional maximum L to use.
*   **Returns:** 2D array of `corrs[i, ix]` (ix=0,1,2,3 for T, Q+U, Q-U, cross).

### `camb.correlations.corr2cl(corrs, xvals, weights, lmax)`

*   **Purpose:** Transform correlation functions to power spectra. Accurate if `xvals`, `weights` are from `np.polynomial.legendre.leggauss(lmax+1)`.
*   **Parameters:**
    *   `corrs`: 2D array `corrs[i, ix]` (ix=0,1,2,3 for T, Q+U, Q-U, cross).
    *   `xvals`: values of `cos(theta)` where `corrs` stores values.
    *   `weights`: weights for integrating each point in `xvals` (Typically from `leggauss`).
    *   `lmax`: maximum l to calculate Cl.
*   **Returns:** array of power spectra `cl[L, ix]` (L starts at 0, ix=0,1,2,3 for TT, EE, BB, TE). Includes `l(l+1)/2pi` factors.

### `camb.correlations.gauss_legendre_correlation(cls, lmax=None, sampling_factor=1)`

*   **Purpose:** Transform Cls into correlation functions evaluated at Gauss-Legendre quadrature roots.
*   **Parameters:**
    *   `cls`: 2D array `cls(L,ix)` including `l(l+1)/2pi` factors.
    *   `lmax`: optional maximum L to use.
    *   `sampling_factor`: uses Gauss-Legendre with degree `lmax*sampling_factor+1`.
*   **Returns:** (corrs, xvals, weights). `corrs[i, ix]` is 2D array (ix=0,1,2,3 for T, Q+U, Q-U, cross).

### `camb.correlations.legendre_funcs(lmax, x, m=(0, 2), lfacs=None, lfacs2=None, lrootfacs=None)`

*   **Purpose:** Utility function to return Legendre (P_l) and Wigner dmn functions up to `lmax`. Note `dmn` arrays start at `lmin = max(m, n)`.
*   **Parameters:**
    *   `lmax`: maximum l.
    *   `x`: scalar value of `cos(theta)`.
    *   `m`: m values to calculate d_mn, etc. as relevant.
    *   `lfacs`: optional pre-computed `l(l+1)` float array.
    *   `lfacs2`: optional pre-computed `(l+2)*(l-1)` float array.
    *   `lrootfacs`: optional pre-computed `sqrt(lfacs*lfacs2)` array.
*   **Returns:** (P, P'), (d11, d−1,1), (d20, d22, d2,−2) as requested. P starts at l=0, spin functions start at l=lmin.

### `camb.correlations.lensed_cl_derivative_unlensed(clpp, lmax=None, theta_max=0.098..., apodize_point_width=10, sampling_factor=1.4)`

*   **Purpose:** Get derivative `d(lensed Cl) / d(unlensed Cl)`. Uses curved-sky results from astro-ph/0601594 (Eqs 9.12, 9.16-9.18) to second order in C_gl,2. Difference is `dCL[ix, :, :].dot(cl)`.
*   **Parameters:**
    *   `clpp`: array of `[L(L+1)]²CφL / 2π` lensing potential power spectrum (zero based).
    *   `lmax`: optional maximum L to use from `clpp` array.
    *   `theta_max`: maximum angle (radians) to keep in correlations.
    *   `apodize_point_width`: if `theta_max` set, apodize cut using half Gaussian of approx width `apodize_point_width/lmax*pi`.
    *   `sampling_factor`: npoints = `int(sampling_factor*lmax)+1`.
*   **Returns:** array `dCL[ix, ell, L]`, where ix=0,1,2,3 are TT, EE, BB, TE; result is `d(Delta D^ix) / d(D^unlens,j)` where j[ix] are TT, EE, EE, TE.

### `camb.correlations.lensed_cl_derivatives(cls, clpp, lmax=None, theta_max=0.098..., apodize_point_width=10, sampling_factor=1.4)`

*   **Purpose:** Get derivative `d(lensed Cl) / d(log Cl)`. Uses curved-sky results from astro-ph/0601594 (Eqs 9.12, 9.16-9.18) to second order in C_gl,2.
*   **Parameters:**
    *   `cls`: 2D array of unlensed `cls(L,ix)` including `l(l+1)/2pi` factors.
    *   `clpp`: array of `[L(L+1)]²CφL / 2π` lensing potential power spectrum.
    *   `lmax`: optional maximum L to use from `cls` array.
    *   `theta_max`: maximum angle (radians) to keep in correlations.
    *   `apodize_point_width`: if `theta_max` set, apodize cut.
    *   `sampling_factor`: npoints = `int(sampling_factor*lmax)+1`.
*   **Returns:** array `dCL[ix, ell, L]`, where ix=0,1,2,3 are T, EE, BB, TE; result is `d[D^ix] / d(log Cl^j)`.

### `camb.correlations.lensed_cls(cls, clpp, lmax=None, lmax_lensed=None, sampling_factor=1.4, delta_cls=False, theta_max=0.098..., apodize_point_width=10, leggaus=True, cache=True)`

*   **Purpose:** Get lensed power spectra from unlensed Cls and lensing potential power. Uses curved-sky results (astro-ph/0601594) to second order in C_gl,2. Compare to `get_lensed_cls_with_spectrum` for speed. Accuracy notes regarding `lmax` padding.
*   **Parameters:**
    *   `cls`: 2D array of unlensed `cls(L,ix)` including `l(l+1)/2pi` factors.
    *   `clpp`: array of `[L(L+1)]²CφL / 2π` lensing potential power spectrum.
    *   `lmax`: optional maximum L to use from `cls` array.
    *   `lmax_lensed`: optional maximum L for the returned cl array (`lmax_lensed <= lmax`).
    *   `sampling_factor`: npoints = `int(sampling_factor*lmax)+1`. Needs ~2x larger if `leggaus=False`.
    *   `delta_cls`: if true, return difference between lensed and unlensed (default False).
    *   `theta_max`: maximum angle (radians) to keep in correlations (default pi/32). Set `None` for full range.
    *   `apodize_point_width`: if `theta_max` set, apodize cut.
    *   `leggaus`: whether to use Gauss-Legendre integration (default True, slower first time).
    *   `cache`: if `leggaus=True`, save x values and weights between calls.
*   **Returns:** 2D array of lensed `cls[L, ix]` including `l(l+1)/2pi` factors.

### `camb.correlations.lensed_correlations(cls, clpp, xvals, weights=None, lmax=None, delta=False, theta_max=None, apodize_point_width=10)`

*   **Purpose:** Get lensed correlation function from unlensed power spectra. Uses curved-sky results (astro-ph/0601594) to second order in C_gl,2. Can return lensed Cls efficiently if `weights` provided.
*   **Parameters:**
    *   `cls`: 2D array of unlensed `cls(L,ix)` including `l(l+1)/2pi` factors.
    *   `clpp`: array of `[L(L+1)]²CφL / 2π` lensing potential power spectrum.
    *   `xvals`: array of `cos(theta)` values to evaluate at.
    *   `weights`: if given, also return lensed Cl.
    *   `lmax`: optional maximum L to use from `cls` arrays.
    *   `delta`: if true, calculate difference between lensed and unlensed (default False).
    *   `theta_max`: maximum angle (radians) to keep in correlations.
    *   `apodize_point_width`: smoothing scale for apodization at truncation.
*   **Returns:** 2D array of `corrs[i, ix]`. If `weights` is not None, returns (corrs, lensed\_cls).

### `camb.correlations.lensing_R(clpp, lmax=None)`

*   **Purpose:** Get R = <|∇φ|²>.
*   **Parameters:**
    *   `clpp`: array of `[L(L+1)]²CφL / 2π` lensing potential power spectrum.
    *   `lmax`: optional maximum L to use.
*   **Returns:** R.

### `camb.correlations.lensing_correlations(clpp, xvals, lmax=None)`

*   **Purpose:** Get the σ²(x) and Cgl,2(x) functions from the lensing power spectrum.
*   **Parameters:**
    *   `clpp`: array of `[L(L+1)]²CφL / 2π` lensing potential power spectrum.
    *   `xvals`: array of `cos(theta)` values.
    *   `lmax`: optional maximum L to use.
*   **Returns:** (array of σ²(x), array of Cgl,2(x)).

## Post-Born Lensing (`camb.postborn`)

*   Calculates B-mode power from post-born field rotation.

### `camb.postborn.get_field_rotation_BB(params, lmax=None, acc=1, CMB_unit='muK', raw_cl=False, spline=True)`

*   **Purpose:** Get B-mode power spectrum from field rotation (perturbative, Limber approx). Ref: arXiv:1605.05662.
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
    *   `lmax`: maximum l.
    *   `acc`: accuracy setting.
    *   `CMB_unit`: units for output ('muK').
    *   `raw_cl`: return CBB rather than l²CBB/(2π).
    *   `spline`: return `InterpolatedUnivariateSpline`, else tuple of (l, Cl).
*   **Returns:** `InterpolatedUnivariateSpline` (or tuple) for l²CBB/(2π) (or CBB if `raw_cl`).

### `camb.postborn.get_field_rotation_power(params, kmax=100, lmax=20000, non_linear=True, z_source=None, k_per_logint=None, acc=1, lsamp=None)`

*   **Purpose:** Get field rotation power spectrum CΩL. Ref: arXiv:1605.05662. Uses lowest Limber approximation.
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
    *   `kmax`: maximum k (Mpc⁻¹).
    *   `lmax`: maximum L.
    *   `non_linear`: include non-linear corrections.
    *   `z_source`: redshift of source. If None, use peak of CMB visibility.
    *   `k_per_logint`: sampling to use in k.
    *   `acc`: accuracy setting.
    *   `lsamp`: array of L values to compute output at. If None, set for interpolation.
*   **Returns:** (L, CΩL): L sample values and corresponding rotation power.

## Lensing Emission Angle (`camb.emission_angle`)

*   **Purpose:** Calculates corrections to lensed CMB spectra due to time delay and emission angle (arXiv:1706.02673). Combine with `postborn` for leading lensing B-mode corrections. T, E corrections negligible.

### `camb.emission_angle.get_emission_angle_powers(camb_background, PK, chi_source, lmax=3000, acc=1, lsamp=None)`

*   **Purpose:** Get power spectrum of ψa (emission angle potential) and cross with standard lensing. Uses Limber approximation (assumes flat universe).
*   **Parameters:**
    *   `camb_background`: a `CAMBdata` results object for background functions.
    *   `PK`: a matter power spectrum interpolator object (`camb.get_matter_power_interpolator`).
    *   `chi_source`: comoving radial distance of source in Mpc.
    *   `lmax`: maximum L.
    *   `acc`: accuracy parameter.
    *   `lsamp`: L sampling for the result.
*   **Returns:** `InterpolatedUnivariateSpline` object containing L(L+1)CL.

### `camb.emission_angle.get_emission_delay_BB(params, kmax=100, lmax=3000, non_linear=True, CMB_unit='muK', raw_cl=False, acc=1, lsamp=None, return_terms=False, include_reionization=True)`

*   **Purpose:** Get B modes from emission angle and time delay effects. Uses full-sky result (appendix of arXiv:1706.02673).
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
    *   `kmax`: maximum k (Mpc⁻¹).
    *   `lmax`: maximum l.
    *   `non_linear`: include non-linear corrections.
    *   `CMB_unit`: normalization for result ('muK').
    *   `raw_cl`: if true return Cl, else l(l+1)Cl/2π.
    *   `acc`: accuracy setting.
    *   `lsamp`: array of l values to compute output at. If None, set for interpolation.
    *   `return_terms`: return the three sub-terms separately rather than total.
    *   `include_reionization`: approximately include reionization terms by second scattering surface.
*   **Returns:** `InterpolatedUnivariateSpline` for CBB.

### `camb.emission_angle.get_source_cmb_cl(params, CMB_unit='muK')`

*   **Purpose:** Get angular power spectra of emission angle/time delay sources (ψτ, ψr), perpendicular velocity, E polarization (1 and 2 versions for recombination/reionization). Destroys current custom sources.
*   **Parameters:**
    *   `params`: `model.CAMBparams` instance.
    *   `CMB_unit`: scale results from dimensionless ('muK' for μK² units).
*   **Returns:** dictionary of power spectra, with L(L+1)/2π factors.

## Matter Power Spectrum and Matter Transfer Function Variables

*   Functions like `get_matter_power_interpolator()` use these variables.
*   **Variables (Standard):**
    *   `k/h` (1): k/h
    *   `delta_cdm` (2): Δc, CDM density (synchronous gauge)
    *   `delta_baryon` (3): Δb, baryon density (synchronous gauge)
    *   `delta_photon` (4): Δγ, photon density (synchronous gauge)
    *   `delta_neutrino` (5): Δr, for massless neutrinos (synchronous gauge)
    *   `delta_nu` (6): Δν for massive neutrinos (synchronous gauge)
    *   `delta_tot` (7): (ρcΔc + ρbΔb + ρνΔν) / (ρc+ρb+ρν), CDM+baryons+massive neutrino density
    *   `delta_nonu` (8): (ρcΔc + ρbΔb) / (ρc+ρb), CDM+baryon density
    *   `delta_tot_de` (9): numerator of (ρcΔc + ... + ρdeΔde) / (ρc+...), CDM+baryons+massive neutrinos+ dark energy density perturbation
    *   `Weyl` (10): k²Ψ = k²(φ + ψ)/2, Weyl potential scaled by k²
    *   `v_newtonian_cdm` (11): Newtonian velcity
    *   `v_newtonian_bary` (12): -vN,b k/H, Newtonian-gauge baryon velocity vN,b
    *   `v_baryon_cdm` (13): vb - vc, relative baryon-CDM velocity (synchronous gauge)
*   **Normalization:** Transfer function variables (from `get_matter_transfer_data()`) are normalized to unit primordial curvature perturbation on super-horizon scales and divided by k². Matter power spectra are calculated from these.
*   **21cm Variables (when `do21cm` is set):**
    *   `Transfer_kh` (1): k/h
    *   `Transfer_cdm` (2): Δc, CDM density
    *   `Transfer_b` (3): Δb, baryon density
    *   `Transfer_monopole` (4): ΔT₀ + (rγ - 1)(Δb - ΔT₀), 21cm monopole source
    *   `Transfer_vnewt` (5): rγ k vN,b / H, 21cm Newtonian-gauge velocity source
    *   `Transfer_Tmat` (6): ΔTm, matter temperature perturbation
    *   `Transfer_tot` (7): (ρcΔc + ρbΔb + ρνΔν) / (ρc+ρb+ρν), CDM+baryons+massive neutrino density
    *   `Transfer_nonu` (8): (ρcΔc + ρbΔb) / (ρc+ρb), CDM+baryon density
    *   `Transfer_tot_de` (9): Numerator of (ρcΔc + ... + ρdeΔde) / (ρc+...), CDM+baryons+massive neutrinos+ dark energy density perturbation
    *   `Transfer_Weyl` (10): k²Ψ = k²(φ + ψ)/2, Weyl potential scaled by k²
    *   `Transfer_Newt_vel_cdm` (11): -vN,c k/H, Newtonian-gauge CDM velocity
    *   `Transfer_Newt_vel_baryon` (12): -vN,b k/H, Newtonian-gauge baryon velocity
    *   `Transfer_vel_baryon_cdm` (13): vb - vc, relative baryon-CDM velocity
*   **Units:** If `use_21cm_mK` is set, the 21cm results are multiplied by Tb to give results in mK units.

## Modifying the Code

*   Changes often require modifying the code, except for simple cases like DE fluids with constant sound speed, different initial power spectra, or different BBN mappings (pure Python).

### 16.1 Defining new classes

*   Changes to DE, initial power, reionization, recombination, or non-linear corrections usually involve defining new classes inheriting from standard bases in both Python and Fortran.
*   Keep variable definitions in the same order.
*   **Python:** Uses the `@fortran_class` decorator for mapping F2008 Fortran types to Python classes.
    *   Requires class variables:
        *   `_fields_`: A list of tuples `(python_name, ctypes_type, description)` mapping Fortran components to Python attributes. Order matters; can omit trailing variables.
        *   `_fortran_class_name_`: String name of the corresponding Fortran type.
        *   `_fortran_class_module_`: String name of the Fortran module containing the type definition.
    *   Example (`AxionEffectiveFluid`):
        ```python
        @fortran_class
        class AxionEffectiveFluid(DarkEnergyModel):
            _fields_ = [
                ("w_n", c_double, "effective equation of state parameter"),
                ("fde_zc", c_double, "energy density fraction at z=zc"),
                ("zc", c_double, "decay transition redshift (not the same as peak of energy..density fraction)"),
                ("theta_i", c_double, "initial condition field value")
            ]
            _fortran_class_name_ = 'TAxionEffectiveFluid'
            _fortran_class_module_ = 'DarkEnergyFluid'
        ```
*   **Fortran:**
    *   Define the corresponding `type`:
        ```fortran
        type, extends(TDarkEnergyModel) :: TAxionEffectiveFluid
            real(dl) :: w_n = 1._dl ! Effective equation of state when oscillating
            real(dl) :: fde_zc = 0._dl ! Energy density fraction at a_c (not the same as peak...)
            real(dl) :: zc ! Transition redshift (scale factor a_c)
            real(dl) :: theta_i = const_pi/2 ! Initial value
            ! ... other private variables ...
        contains
            procedure :: ReadParams => TAxionEffectiveFluid_ReadParams
            procedure, nopass :: PythonClass => TAxionEffectiveFluid_PythonClass
            procedure, nopass :: SelfPointer => TAxionEffectiveFluid_SelfPointer
            procedure :: Init => TAxionEffectiveFluid_Init
            procedure :: w_de => TAxionEffectiveFluid_w_de
            procedure :: grho_de => TAxionEffectiveFluid_grho_de
            procedure :: PerturbedStressEnergy => TAxionEffectiveFluid_PerturbedStressEnergy
            procedure :: PerturbationEvolve => TAxionEffectiveFluid_PerturbationEvolve
        end type TAxionEffectiveFluid
        ```
    *   Must include a `SelfPointer` function (for Python mapping via `iso_c_binding`):
        ```fortran
        subroutine TMyClass_SelfPointer(cptr, P)
            use iso_c_binding
            Type(c_ptr) :: cptr
            Type (TMyClass), pointer :: PType
            class (TPythonInterfacedClass), pointer :: P ! Assuming base class TMyClass derives from this

            call c_f_pointer(cptr, PType)
            P => PType

        end subroutine TMyClass_SelfPointer
        ```
    *   Implement necessary methods (`Init`, `w_de`, etc.).
    *   `ReadParams` method is needed only for loading from `.ini` files.
    *   `PythonClass` method is not strictly needed.

### 16.2 Other code changes

*   For new quintessence potentials, modify Fortran (`Quintessence` class, `DarkEnergyQuintessence.f90`). May need complex changes to map inputs to initial conditions.
*   General changes often involve modifying background/perturbation equations in `equations.f90`. Refer to CAMB notes for conventions.

### 16.3 Code updates, testing, and gotchas

*   **Recompile Fortran:** After changes, run `python setup.py make`.
*   **Version Check:** Changing version numbers in Python/Fortran enables automatic run-time matching checks.
*   **Accuracy:** Default parameters are for Simons Observatory-like precision. Check stability by increasing `AccuracyBoost` and `lAccuracyBoost`. Specific parameter changes might be more efficient.
*   **Gotchas:**
    *   Types derived directly from `CAMB_Structure` (like `AccuracyParams`) map directly via `ctypes` and shouldn't be instantiated directly in Python (will be zeroed). They are sub-components.
    *   Classes inheriting `F2003Class` map to Fortran class types. If they are allocatable subcomponents, modifying *only* the Python class instance might lead to unexpected behavior (e.g., attribute assignment failing silently) because the Python instance might be recreated on access, losing the change. Define fields in both Fortran and Python (`_fields_`) or only use Python variables in container classes like `CAMBparams`.
    *   When setting `thetastar` for dark energy models, ensure the dark energy model/parameters are set *first*.
    *   Accessing array-like members (e.g., `CAMBparams.z_outputs`) might require explicit casting to `list` to view elements.

### 16.4 Interfacing with Cobaya

*   Cobaya uses introspection to find supported CAMB variables.
*   New variables added to `CAMBparams` or as arguments to `set_cosmology` or class `set_params` methods should be automatically usable.
*   Other new variables might require modifying `get_valid_numerical_params()`.
*   Test examples show supporting new primordial power spectra/bins and using `get_class_options` for dynamic parameter definition.
*   Only scalar parameters can be directly sampled. Map vector parameters (e.g., for dark energy) by defining functions that take scalar inputs. Cobaya automatically identifies numerical arguments to custom class `set_params` functions; define vector parameters with default `None` to be picked up for sampling.
*   See CosmoCoffee discussion forum for questions.

## Fortran Compilers

*   CAMB uses modern object-oriented Fortran 2008.
*   **Recommended Compilers:**
    *   gfortran >= 6.3
    *   Intel Fortran (ifort) >= 18.0.1 (some parts might work with 14+)
*   **Check version:** `gfortran --version`
*   **Getting Compilers:**
    *   **Mac:** Binary installation usually sufficient (bundled?).
    *   **Windows:** Use MinGW-w64 (select x86\_64 option during install) or get from niXman on GitHub. Install under `Program Files`.
    *   **Linux:** Standard repository: `sudo apt-get update; sudo apt-get install gfortran`
*   **Containers:** Can compile/run in containers like CosmoBox.
    ```bash
    # Example shell in docker (run from camb directory)
    docker run -v /local/git/path/CAMB:/camb -i -t cmbant/cosmobox
    ```

### 17.1 Updating modified Fortran code

*   In the main CAMB source root directory, rebuild the Fortran binary:
    ```bash
    python setup.py make
    ```
    (Works on Windows if MinGW-w64 is installed under Program Files).
*   **Reloading:** Close all Python instances using CAMB or restart Jupyter kernel.
    ```python
    # In Jupyter to restart kernel
    import IPython
    IPython.Application.instance().kernel.do_shutdown(True)
    ```
*   **Automatic Rebuild (e.g., from Jupyter):**
    ```python
    import subprocess
    import sys
    import os
    src_dir = '/path/to/git/CAMB' # Adjust path
    try:
        subprocess.check_output(r'python "%s" make'%os.path.join(src_dir, 'setup.py'),
                                stderr=subprocess.STDOUT)
        sys.path.insert(0, src_dir)
        # Optional: Force reload if already imported (may require importlib)
        # import importlib
        # if 'camb' in sys.modules:
        #     importlib.reload(sys.modules['camb'])
        # else:
        #     import camb
        import camb # Re-import or initial import
        print('Using CAMB %s installed at %s'%(camb.__version__,
                                               os.path.dirname(camb.__file__)))
    except subprocess.CalledProcessError as E:
        print("Build failed:")
        print(E.output.decode())
    except ImportError:
        print("Import failed after potential build.")

    ```

## Maths Utils (`camb.mathutils`)

*   Fast utility functions, independent of the main CAMB code.

### `camb.mathutils.chi_squared(covinv, x)`

*   **Purpose:** Efficiently calculate x^T covinv x.
*   **Parameters:**
    *   `covinv`: symmetric inverse covariance matrix.
    *   `x`: vector.
*   **Returns:** `covinv.dot(x).dot(x)`, parallelized and using symmetry.

### `camb.mathutils.pcl_coupling_matrix(P, lmax, pol=False)`

*   **Purpose:** Get Pseudo-Cl coupling matrix from mask power spectrum `P`. Uses multiple threads. Ref: Eq A31 of astro-ph/0105302.
*   **Parameters:**
    *   `P`: power spectrum of mask.
    *   `lmax`: lmax for the matrix.
    *   `pol`: whether to calculate TE, EE, BB couplings.
*   **Returns:** coupling matrix (square but not symmetric), or list of TT, TE, EE, BB if `pol`.

### `camb.mathutils.scalar_coupling_matrix(P, lmax)`

*   **Purpose:** Get scalar Pseudo-Cl coupling matrix from mask power spectrum `P` (or array of `P`). Uses multiple threads. Ref: Eq A31 of astro-ph/0105302.
*   **Parameters:**
    *   `P`: power spectrum of mask, or list of mask power spectra.
    *   `lmax`: lmax for the matrix (assumed square).
*   **Returns:** coupling matrix (square but not symmetric), or list of couplings for different masks.

### `camb.mathutils.threej(l2, l3, m2, m3)`

*   **Purpose:** Convenience wrapper around standard 3j function, returning array for all allowed l1 values.
*   **Parameters:**
    *   `l2`: L\_2.
    *   `l3`: L\_3.
    *   `m2`: M\_2.
    *   `m3`: M\_3.
*   **Returns:** array of 3j values from `l1 = max(abs(l2-l3),abs(m2+m3))` .. `l2+l3`.

### `camb.mathutils.threej_coupling(W, lmax, pol=False)`

*   **Purpose:** Calculate symmetric coupling matrix Ξ (`Xi`) for given weights Wl. Relates observed Pseudo-Cl <Čl> to true Cl via `<Čl> = Σl' Ξll' (2l'+1) Cl'`. Weights `Wl = (2l+1)Pl / 4π` where P is mask power. Ref: Eq D16 of arxiv:0801.0554.
*   **Parameters:**
    *   `W`: 1d array of Weights for each L (zero based), or list of arrays (if `pol=True`, needs 1 or 3 for TT, TE, EE, EB).
    *   `lmax`: lmax for the output matrix (assumed symmetric).
    *   `pol`: if True, produce TT, TE, EE, EB couplings (needs 1 or 3 input mask weights).
*   **Returns:** symmetric coupling matrix or array of matrices.

### `camb.mathutils.threej_pt(l1, l2, l3, m1, m2, m3)`

*   **Purpose:** Convenience testing function to get 3j for specific arguments. Use `threej` for efficiency.
*   **Parameters:** `l1`, `l2`, `l3`, `m1`, `m2`, `m3`.
*   **Returns:** Wigner 3j value (integer zero if outside triangle constraints).


## Python Module Index

*   `camb`
*   `camb.bbn`
*   `camb.correlations`
*   `camb.emission_angle`
*   `camb.mathutils`
*   `camb.postborn`
*   `camb.symbolic`

```