```markdown
# GetDist Documentation Summary (Release 1.6.2)

**Author:** Antony Lewis
**Source:** https://github.com/cmbant/getdist
**Homepage:** https://getdist.readthedocs.io
**Reference:** https://arxiv.org/abs/1910.13970

## Overview

GetDist is a Python package for analysing and plotting Monte Carlo (or other) samples, including correlated samples from Markov Chain Monte Carlo (MCMC).

**Key Features:**

*   **Point and click GUI:** select chain files, view plots, marginalized constraints, LaTeX tables and more.
*   **Plotting library:** make custom publication-ready 1D, 2D, 3D-scatter, triangle and other plots.
*   **Named parameters:** simple handling of many parameters using parameter names, including LaTeX labels and prior bounds.
*   **Optimized Kernel Density Estimation:** automated optimal bandwidth choice for 1D and 2D densities (Botev et al. Improved Sheather-Jones method), with boundary and bias correction.
*   **Convergence diagnostics:** including correlation length and diagonalized Gelman-Rubin statistics.
*   **LaTeX tables:** for marginalized 1D constraints.

See the Plot Gallery and tutorial (run online) and GetDist Documentation.

## Getting Started

### Installation

Install getdist using pip:

```bash
$ pip install getdist
```

or from source files using:

```bash
$ pip install -e /path/to/source/
```

### Dependencies

*   Python 3.8+
*   matplotlib
*   scipy
*   PySide6 - optional, only needed for GUI
*   Working LaTeX installation (not essential, only for some plotting/table functions)

Python distributions like Anaconda have most of what you need (except for LaTeX).
To use the GUI you need PySide. See the GUI docs for suggestions on how to install.

### Testing

You can test if things are working using the unit test by running:

```bash
$ python -m unittest getdist.tests.getdist_test
```

### Algorithm Details

Details of kernel density estimation (KDE) algorithms and references are give in the GetDist notes arXiv:1910.13970.

## Samples File Format

GetDist can be used in scripts and interactively with standard numpy arrays. Scripts and the GetDist GUI can also read parameter sample/chain files in plain text format (or in the format output by the Cobaya sampling program). In general plain text files of the form:

```
xxx_1.txt
xxx_2.txt
...
xxx.paramnames
xxx.ranges
```

where “xxx” is some root file name.

*   **`.txt` files:** Separate chain files (can be just one `xxx.txt`). Each row is:
    `weight like param1 param2 param3 ...`
    *   `weight`: number of samples (or importance weight).
    *   `like`: -log(likelihood).
    *   `param1`, `param2`...: parameter values.
    *   The first two columns (`weight`, `like`) can be 1 and 0 if not known or used.
*   **`.paramnames` file:** Lists parameter names, one per line, optionally followed by a LaTeX label. Names cannot include spaces. Names ending in `*` are interpreted as derived parameters.
    Example:
    ```
    x1 x_1
    y1 y_1
    x2 x_2
    xy* x_1+y_1
    ```
*   **`.ranges` file:** Gives hard prior bounds for parameters. `N` denotes an unbounded limit. Used for density estimation and plot bounds near boundaries.
    Example:
    ```
    x1 -5 5
    x2 0 N
    ```
*   **`.properties.ini` file (optional):** Can specify `burn_removed=T` (ensure no burn-in is removed) or `ignore_rows=x` (ignore the first fraction `x` or first `x` rows if `x>1`).

## Loading Samples

Use `loadMCSamples` to load an `MCSamples` object from text files:

```python
from getdist import loadMCSamples
samples = loadMCSamples('/path/to/xxx', settings={'ignore_rows':0.3})
```

The `MCSamples` object can be passed to plot functions or used for analysis.

Example plotting:

```python
from getdist import plots
g = plots.get_single_plotter()
g.plot_2d(samples, ['x1', 'x2'])

# Compare chains from different roots in the same directory
g = plots.get_single_plotter(chain_dir='/path/to/', analysis_settings={'ignore_rows':0.3})
g.plot_2d(['xxx','yyy'], ['x', 'y'])
```

`MCSamples` objects can also be constructed directly from numpy arrays.

## Command-Line Interface (CLI)

### `getdist` Script

Calculates convergence and marginalized statistics from chain files on disk.

```bash
usage: getdist [-h] [--ignore_rows IGNORE_ROWS] [-V] [ini_file] [chain_root]

GetDist sample analyser

positional arguments:
  ini_file         .ini file with analysis settings (optional, if omitted uses defaults
  chain_root       Root name of chain to analyse (e.g. chains/test), required unless file_root specified in ini_file

optional arguments:
  -h, --help            show this help message and exit
  --ignore_rows IGNORE_ROWS
                        set initial fraction of chains to cut as burn in (fraction of total rows, or >1 number of rows); overrides any value in ini_file if set
  --make_param_file MAKE_PARAM_FILE
                        Produce a sample distparams.ini file that you can edit and use when running GetDist
  -V, --version         show program’s version number and exit
```

Example:

```bash
getdist distparams.ini chains/test_chain
```

Produces files: `.margestats`, `.likestats`, `.converge`, `.covmat`, `.corr`, and optional plotting scripts.

To customize settings:

```bash
getdist --make_param_file distparams.ini
# Edit distparams.ini, then run:
getdist distparams.ini chains/test_chain
```

### `getdist-gui` Script

Runs the graphical user interface. Requires PySide. Runs on Windows, Linux, Mac. Allows opening chain folders, selecting, plotting, comparing chains, viewing outputs and tables.

## GetDist GUI

Run `getdist-gui` to launch. Requires PySide.

*   **Functionality:** Open chain folders (plain text, paramgrid, Cobaya grids), select chain roots, drag-and-drop to reorder, select parameters to plot.
*   **Plot Types:** 1D, 2D (line/filled), 3D scatter (color by third param), triangle, rectangle plots.
*   **Script Preview:** Export plots to files (PDF etc.) or export the generating script for customization.
*   **Statistics & Tables:** View `.margestats`, LaTeX tables, convergence stats, PCA constraints. Requires LaTeX for rendered tables.
*   **Settings:** Customize analysis limits, lines, contours, plot options via Options menu. "Plot module config" allows using custom plotting modules.

### GUI Installation

Requires PySide6 (not installed by default):

```bash
pip install PySide6
```

Or using conda-forge:

```bash
conda create -n myenv -c conda-forge scipy matplotlib PyYAML PySide6
```

After installing PySide, (re)install getdist. The `getdist-gui` script should be available. On Mac, a GetDist GUI app is also created.

## Usage with CosmoMC and Cobaya

GetDist is developed alongside CosmoMC and Cobaya. It's included in a full CosmoMC installation and installed as a dependency by Cobaya. See the GetDist Readme for details on plotting Planck chains and using CosmoMC parameter grids.

## Citation

```bibtex
@article{Lewis:2019xzd,
author = "Lewis, Antony",
title = "{GetDist: a Python package for analysing Monte Carlo samples}",
year = "2019",
eprint = "1910.13970",
archivePrefix = "arXiv",
primaryClass = "astro-ph.IM",
SLACcitation = "%%CITATION = ARXIV:1910.13970;%%",
url = "https://getdist.readthedocs.io"
}
```

## Analysis Settings

Analysis settings are specified via `.ini` files or dictionaries. Defaults are in `analysis_defaults.ini`.

Key default settings:

*   `ignore_rows = 0`: Fraction or number of rows to discard as burn-in.
*   `min_weight_ratio = 1e-30`: Minimum sample weight relative to maximum.
*   `contours = 0.68 0.95 0.99`: Confidence levels for marginalized constraints/plots.
*   `credible_interval_threshold = 0.05`: Threshold for using equal-probability vs equal-density tails for skewed distributions.
*   `range_ND_contour = -1`: Which contour to use for N-D bounds (-1 uses 1D marginalized bounds).
*   `range_confidence = 0.001`: 1D confidence limit for determining parameter ranges.
*   `converge_test_limit = 0.95`: Confidence limit for convergence tests.
*   `fine_bins = 1024`: Binning for 1D plots.
*   `smooth_scale_1D = -1`: 1D smoothing bandwidth (-1 for automatic).
*   `boundary_correction_order=1`: Order of boundary correction kernel.
*   `mult_bias_correction_order = 1`: Order of multiplicative bias correction.
*   `smooth_scale_2D = -1`: 2D smoothing bandwidth (-1 for automatic).
*   `max_corr_2D = 0.99`: Max correlation ellipticity for 2D kernels.
*   `fine_bins_2D = 256`: Binning for 2D plotting.
*   `use_effective_samples_2D = F`: Whether to use 2D-specific effective sample size estimate.
*   `max_scatter_points = 2000`: Max points for 3D scatter plots.
*   `num_bins = 100`: Output bins for 1D getdist file output.
*   `num_bins_2D = 40`: Output bins for 2D getdist file output.

The default analysis settings file can be changed via the `GETDIST_CONFIG` environment variable.

## Python Module Index

*   `getdist.chains` (Page 81)
*   `getdist.covmat` (Page 95)
*   `getdist.densities` (Page 97)
*   `getdist.gaussian_mixtures` (Page 101)
*   `getdist.inifile` (Page 107)
*   `getdist.mcsamples` (Page 13)
*   `getdist.paramnames` (Page 111)
*   `getdist.parampriors` (Page 115)
*   `getdist.plots` (Page 41)
*   `getdist.types` (Page 117)

## `getdist.mcsamples`

### `loadMCSamples`

```python
getdist.mcsamples.loadMCSamples(file_root: str, ini: None | str | IniFile = None, jobItem=None, no_cache=False, settings: Mapping[str, Any] | None = None, chain_exclude=None) → MCSamples
```

Loads a set of samples from a file or files. Sample files are plain text (`file_root.txt`) or a set (`file_root_1.txt`, `file_root_2.txt`, etc.). Auxiliary files `file_root.paramnames` and `file_root.ranges` provide parameter names and bounds.

*   **Parameters:**
    *   `file_root`: The root name of the files to read (no extension).
    *   `ini`: The name of a .ini file with analysis settings to use.
    *   `jobItem`: an optional grid jobItem instance for a CosmoMC grid output.
    *   `no_cache`: Indicates whether or not we should cache loaded samples in a pickle.
    *   `settings`: dictionary of analysis settings to override defaults.
    *   `chain_exclude`: A list of indexes to exclude, None to include all.
*   **Returns:** The `MCSamples` instance.

### `MCSamples`

```python
class getdist.mcsamples.MCSamples(root: str | None = None, jobItem=None, ini=None, settings: Mapping[str, Any] | None = None, ranges=None, samples: ndarray | Iterable[ndarray] | None = None, weights: ndarray | Iterable[ndarray] | None = None, loglikes: ndarray | Iterable[ndarray] | None = None, temperature: float | None = None, **kwargs)
```

The main high-level class for a collection of parameter samples. Derives from `chains.Chains`, adding high-level functions including Kernel Density estimates, parameter ranges and custom settings.

*   **Parameters:**
    *   `root`: A root file name when loading from file.
    *   `jobItem`: optional jobItem for parameter grid item. Should have `jobItem.chainRoot` and `jobItem.batchPath`.
    *   `ini`: a .ini file to use for custom analysis settings.
    *   `settings`: a dictionary of custom analysis settings.
    *   `ranges`: a dictionary giving any additional hard prior bounds for parameters, e.g. `{'x':[0, 1], 'y':[None,2]}`.
    *   `samples`: if not loading from file, array of parameter values for each sample, passed to `setSamples()`, or list of arrays if more than one chain.
    *   `weights`: array of weights for samples, or list of arrays if more than one chain.
    *   `loglikes`: array of -log(Likelihood) for samples, or list of arrays if more than one chain.
    *   `temperature`: temperature of the sample. If not specified will be read from the `root.properties.ini` file if it exists and otherwise default to 1.
    *   `**kwargs`: keyword arguments passed to inherited classes, e.g. to manually make a samples object from sample arrays in memory:
        *   `paramNamesFile`: optional name of .paramnames file with parameter names.
        *   `names`: list of names for the parameters, or list of arrays if more than one chain.
        *   `labels`: list of latex labels for the parameters.
        *   `renames`: dictionary of parameter aliases.
        *   `ignore_rows`:
            *   if int >=1: The number of rows to skip at the file in the beginning of the file.
            *   if float <1: The fraction of rows to skip at the beginning of the file.
        *   `label`: a latex label for the samples.
        *   `name_tag`: a name tag for this instance.
        *   `sampler`: string describing the type of samples; if “nested” or “uncorrelated” the effective number of samples is calculated using uncorrelated approximation. If not specified will be read from the `root.properties.ini` file if it exists and otherwise default to “mcmc”.

*   **Methods:**
    *   `PCA(params, param_map=None, normparam=None, writeDataToFile=False, filename=None, conditional_params=(), n_best_only=None)`: Perform principal component analysis (PCA).
        *   `params`: List of names of the parameters to use.
        *   `param_map`: A transformation to apply to parameter values; A list or string containing either N (no transformation) or L (for log transform) for each parameter. By default, uses log if no parameter values cross zero.
        *   `normparam`: optional name of parameter to normalize result (i.e. this parameter will have unit power).
        *   `writeDataToFile`: True to write the output to file.
        *   `filename`: The filename to write, by default `root_name.PCA`.
        *   `conditional_params`: optional list of parameters to treat as fixed, i.e. for PCA conditional on fixed values of these parameters.
        *   `n_best_only`: return just the short summary constraint for the tightest `n_best_only` constraints.
        *   **Returns:** a string description of the output of the PCA.
    *   `addDerived(paramVec, name, label='', comment='', range=None)`: Adds a new derived parameter.
        *   `paramVec`: The vector of parameter values to add. For example a combination of parameter arrays from `MCSamples.getParams()`.
        *   `name`: The name for the new parameter.
        *   `label`: optional latex label for the parameter.
        *   `comment`: optional comment describing the parameter.
        *   `range`: if specified, a tuple of min, max values for the new parameter hard prior bounds (either can be None for one-side bound).
        *   **Returns:** The added parameter’s `ParamInfo` object.
    *   `changeSamples(samples)`: Sets the samples without changing weights and loglikes.
        *   `samples`: The samples to set.
    *   `confidence(paramVec, limfrac, upper=False, start=0, end=None, weights=None)`: Calculate sample confidence limits, not using kernel densities just counting samples in the tails.
        *   `paramVec`: array of parameter values or int index of parameter to use.
        *   `limfrac`: fraction of samples in the tail, e.g. 0.05 for a 95% one-tail limit, or 0.025 for a 95% two-tail limit.
        *   `upper`: True to get upper limit, False for lower limit.
        *   `start`: Start index for the vector to use.
        *   `end`: The end index, use None to go all the way to the end of the vector.
        *   `weights`: numpy array of weights for each sample, by default `self.weights`.
        *   **Returns:** confidence limit (parameter value when limfac of samples are further in the tail).
    *   `cool(cool=None)`: Cools the samples, i.e. multiplies log likelihoods by cool factor and re-weights accordingly.
        *   `cool`: cool factor, optional if the sample has a temperature specified.
    *   `copy(label=None, settings=None) → MCSamples`: Create a copy of this sample object.
        *   `label`: optional lable for the new copy.
        *   `settings`: optional modified settings for the new copy.
        *   **Returns:** copyied `MCSamples` instance.
    *   `corr(pars=None)`: Get the correlation matrix.
        *   `pars`: If specified, list of parameter vectors or int indices to use.
        *   **Returns:** The correlation matrix.
    *   `cov(pars=None, where=None)`: Get parameter covariance.
        *   `pars`: if specified, a list of parameter vectors or int indices to use.
        *   `where`: if specified, a filter for the samples to use (where x>=5 would mean only process samples with x>=5).
        *   **Returns:** The covariance matrix.
    *   `deleteFixedParams()`: Delete parameters that are fixed (the same value in all samples).
    *   `deleteZeros()`: Removes samples with zero weight.
    *   `filter(where)`: Filter the stored samples to keep only samples matching filter.
        *   `where`: list of sample indices to keep, or boolean array filter (e.g. x>5 to keep only samples where x>5).
    *   `get1DDensity(name, **kwargs)`: Returns a `Density1D` instance for parameter with given name. Result is cached.
        *   `name`: name of the parameter.
        *   `kwargs`: arguments for `get1DDensityGridData()`.
        *   **Returns:** A `Density1D` instance for parameter with given name.
    *   `get1DDensityGridData(j, paramConfid=None, meanlikes=False, **kwargs)`: Low-level function to get a `Density1D` instance for the marginalized 1D density of a parameter. Result is not cached.
        *   `j`: a name or index of the parameter.
        *   `paramConfid`: optional cached `ParamConfidenceData` instance.
        *   `meanlikes`: include mean likelihoods.
        *   `**kwargs`: optional settings to override instance settings (see `analysis_settings`): `smooth_scale_1D`, `boundary_correction_order`, `mult_bias_correction_order`, `fine_bins`, `num_bins`.
        *   **Returns:** A `Density1D` instance.
    *   `get2DDensity(x, y, normalized=False, **kwargs)`: Returns a `Density2D` instance with marginalized 2D density.
        *   `x`: index or name of x parameter.
        *   `y`: index or name of y parameter.
        *   `normalized`: if False, is normalized so the maximum is 1, if True, density is normalized.
        *   `kwargs`: keyword arguments for the `get2DDensityGridData()` function.
        *   **Returns:** `Density2D` instance.
    *   `get2DDensityGridData(j, j2, num_plot_contours=None, get_density=False, meanlikes=False, mask_function: callable = None, **kwargs)`: Low-level function to get 2D plot marginalized density and optional additional plot data.
        *   `j`: name or index of the x parameter.
        *   `j2`: name or index of the y parameter.
        *   `num_plot_contours`: number of contours to calculate and return in density.contours.
        *   `get_density`: only get the 2D marginalized density, don’t calculate confidence level members.
        *   `meanlikes`: calculate mean likelihoods as well as marginalized density (returned as array in density.likes).
        *   `mask_function`: optional function, `mask_function(minx, miny, stepx, stepy, mask)`, which which sets mask to zero for values of parameters that are excluded by prior. Note this is not needed for standard min, max bounds aligned with axes, as they are handled by default.
        *   `**kwargs`: optional settings to override instance settings (see `analysis_settings`): `fine_bins_2D`, `boundary_correction_order`, `mult_bias_correction_order`, `smooth_scale_2D`.
        *   **Returns:** a `Density2D` instance.
    *   `getAutoBandwidth1D(bins, par, param, mult_bias_correction_order=None, kernel_order=1, N_eff=None)`: Get optimized kernel density bandwidth (in units of the range of the bins).
        *   `bins`: numpy array of binned weights for the samples.
        *   `par`: A `ParamInfo` instance for the parameter to analyse.
        *   `param`: index of the parameter to use.
        *   `mult_bias_correction_order`: order of multiplicative bias correction (0 is basic Parzen kernel); by default taken from instance settings.
        *   `kernel_order`: order of the kernel (0 is Parzen, 1 does linear boundary correction, 2 is a higher-order kernel).
        *   `N_eff`: effective number of samples. If not specified estimated using weights, autocorrelations, and fiducial bandwidth.
        *   **Returns:** kernel density bandwidth (in units the range of the bins).
    *   `getAutoBandwidth2D(bins, parx, pary, paramx, paramy, corr, rangex, rangey, base_fine_bins_2D, mult_bias_correction_order=None, min_corr=0.2, N_eff=None, use_2D_Neff=False)`: Get optimized kernel density bandwidth matrix in parameter units.
        *   `bins`: 2D numpy array of binned weights.
        *   `parx`: A `ParamInfo` instance for the x parameter.
        *   `pary`: A `ParamInfo` instance for the y parameter.
        *   `paramx`: index of the x parameter.
        *   `paramy`: index of the y parameter.
        *   `corr`: correlation of the samples.
        *   `rangex`: scale in the x parameter.
        *   `rangey`: scale in the y parameter.
        *   `base_fine_bins_2D`: number of bins to use for re-binning in rotated parameter space.
        *   `mult_bias_correction_order`: multiplicative bias correction order (0 is Parzen kernel); by default taken from instance settings.
        *   `min_corr`: minimum correlation value at which to bother de-correlating the parameters.
        *   `N_eff`: effective number of samples. If not specified, uses rough estimate that accounts for weights and strongly-correlated nearby samples (see notes).
        *   `use_2D_Neff`: if `N_eff` not specified, whether to use 2D estimate of effective number, or approximate from the 1D results (default from `use_effective_samples_2D` setting).
        *   **Returns:** kernel density bandwidth matrix in parameter units.
    *   `getAutocorrelation(paramVec, maxOff=None, weight_units=True, normalized=True)`: Gets auto-correlation of an array of parameter values (e.g. for correlated samples from MCMC).
        *   `paramVec`: an array of parameter values, or the int index of the parameter in stored samples to use.
        *   `maxOff`: maximum autocorrelation distance to return.
        *   `weight_units`: False to get result in sample point (row) units; `weight_units=True` gives standard definition for raw chains.
        *   `normalized`: Set to False to get covariance (note even if normalized, `corr[0]<>1` in general unless weights are unity).
        *   **Returns:** zero-based array giving auto-correlations.
    *   `getBestFit(max_posterior=True)`: Returns a `BestFit` object with best-fit point stored in `.minimum` or `.bestfit` file.
        *   `max_posterior`: whether to get maximum posterior (from `.minimum` file) or maximum likelihood (from `.bestfit` file).
    *   `getBounds()`: Returns the bounds in the form of a `ParamBounds` instance, for example for determining plot ranges. Bounds are not the same as `self.ranges`.
        *   **Returns:** a `ParamBounds` instance.
    *   `getCombinedSamplesWithSamples(samps2, sample_weights=(1, 1))`: Make a new `MCSamples` instance by appending samples from `samps2` for parameters which are in common.
        *   `samps2`: `MCSamples` instance to merge.
        *   `sample_weights`: relative weights for combining the samples. Set to None to just directly append samples.
        *   **Returns:** a new `MCSamples` instance with the combined samples.
    *   `getConvergeTests(test_confidence=0.95, writeDataToFile=False, what=('MeanVar', 'GelmanRubin', 'SplitTest', 'RafteryLewis', 'CorrLengths'), filename=None, feedback=False)`: Do convergence tests.
        *   `test_confidence`: confidence limit to test for convergence (two-tail, only applies to some tests).
        *   `writeDataToFile`: True to write output to a file.
        *   `what`: The tests to run. List of: 'MeanVar' (Gelman-Rubin per parameter), 'GelmanRubin' (worst orthogonalized), 'SplitTest' (variation in limits on subsets), 'RafteryLewis', 'CorrLengths'.
        *   `filename`: The filename to write to, default is `file_root.converge`.
        *   `feedback`: If set to True, Prints the output as well as returning it.
        *   **Returns:** text giving the output of the tests.
    *   `getCorrelatedVariable2DPlots(num_plots=12, nparam=None)`: Gets a list of most correlated variable pair names.
        *   `num_plots`: The number of plots.
        *   `nparam`: maximum number of pairs to get.
        *   **Returns:** list of `[x,y]` pair names.
    *   `getCorrelationLength(j, weight_units=True, min_corr=0.05, corr=None)`: Gets the auto-correlation length for parameter j.
        *   `j`: The index of the parameter to use.
        *   `weight_units`: False to get result in sample point (row) units; `weight_units=True` gives standard definition for raw chains.
        *   `min_corr`: specifies a minimum value of the autocorrelation to use.
        *   `corr`: The auto-correlation array to use, calculated internally by default using `getAutocorrelation()`.
        *   **Returns:** the auto-correlation length.
    *   `getCorrelationMatrix()`: Get the correlation matrix of all parameters.
        *   **Returns:** The correlation matrix.
    *   `getCov(nparam=None, pars=None)`: Get covariance matrix of the parameters. By default, uses all parameters, or can limit to max number or list.
        *   `nparam`: if specified, only use the first `nparam` parameters.
        *   `pars`: if specified, a list of parameter indices (0,1,2..) to include.
        *   **Returns:** covariance matrix.
    *   `getCovMat()`: Gets the `CovMat` instance containing covariance matrix for all the non-derived parameters.
        *   **Returns:** A `CovMat` object holding the covariance.
    *   `getEffectiveSamples(j=0, min_corr=0.05)`: Gets effective number of samples N_eff so that the error on mean of parameter j is sigma_j/N_eff.
        *   `j`: The index of the param to use.
        *   `min_corr`: the minimum value of the auto-correlation to use when estimating the correlation length.
    *   `getEffectiveSamplesGaussianKDE(paramVec, h=0.2, scale=None, maxoff=None, min_corr=0.05)`: Roughly estimate an effective sample number for use in the leading term for the MISE of a Gaussian-kernel KDE.
        *   `paramVec`: parameter array, or int index of parameter to use.
        *   `h`: fiducial assumed kernel scale.
        *   `scale`: a scale parameter to determine fiducial kernel width, by default the parameter standard deviation.
        *   `maxoff`: maximum value of auto-correlation length to use.
        *   `min_corr`: ignore correlations smaller than this auto-correlation.
        *   **Returns:** A very rough effective sample number for leading term for the MISE of a Gaussian KDE.
    *   `getEffectiveSamplesGaussianKDE_2d(i, j, h=0.3, maxoff=None, min_corr=0.05)`: Roughly estimate an effective sample number for use in the leading term for the 2D MISE.
        *   `i`: parameter array, or int index of first parameter to use.
        *   `j`: parameter array, or int index of second parameter to use.
        *   `h`: fiducial assumed kernel scale.
        *   `maxoff`: maximum value of auto-correlation length to use.
        *   `min_corr`: ignore correlations smaller than this auto-correlation.
        *   **Returns:** A very rough effective sample number for leading term for the MISE of a Gaussian KDE.
    *   `getFractionIndices(weights, n)`: Calculates the indices of weights that split the weights into sets of equal 1/n fraction of the total weight.
        *   `weights`: array of weights.
        *   `n`: number of groups to split into.
        *   **Returns:** array of indices of the boundary rows in the weights array.
    *   `getGelmanRubin(nparam=None, chainlist=None)`: Assess convergence using the maximum var(mean)/mean(var) of orthogonalized parameters.
        *   `nparam`: The number of parameters, by default uses all.
        *   `chainlist`: list of `WeightedSamples`, the samples to use. Defaults to all the separate chains in this instance.
        *   **Returns:** The worst var(mean)/mean(var) for orthogonalized parameters. Should be <<1 for good convergence.
    *   `getGelmanRubinEigenvalues(nparam=None, chainlist=None)`: Assess convergence using var(mean)/mean(var) in the orthogonalized parameters.
        *   `nparam`: The number of parameters (starting at first), by default uses all of them.
        *   `chainlist`: list of `WeightedSamples`, the samples to use. Defaults to all the separate chains in this instance.
        *   **Returns:** array of var(mean)/mean(var) for orthogonalized parameters.
    *   `getInlineLatex(param, limit=1, err_sig_figs=None)`: Get snippet like: `A=x\pm y`.
        *   `param`: The name of the parameter.
        *   `limit`: which limit to get, 1 is the first (default 68%), 2 is the second (limits array specified by `self.contours`).
        *   `err_sig_figs`: significant figures in the error.
        *   **Returns:** The tex snippet.
    *   `getLabel()`: Return the latex label for the samples.
        *   **Returns:** the label.
    *   `getLatex(params=None, limit=1, err_sig_figs=None)`: Get tex snippet for constraints on a list of parameters.
        *   `params`: list of parameter names, or a single parameter name.
        *   `limit`: which limit to get, 1 is the first (default 68%), 2 is the second (limits array specified by `self.contours`).
        *   `err_sig_figs`: significant figures in the error.
        *   **Returns:** labels, texs: a list of parameter labels, and a list of tex snippets, or for a single parameter, the latex snippet.
    *   `getLikeStats()`: Get best fit sample and n-D confidence limits, and various likelihood based statistics.
        *   **Returns:** a `LikeStats` instance.
    *   `getLower(name)`: Return the lower limit of the parameter with the given name.
        *   `name`: parameter name.
        *   **Returns:** The lower limit if name exists, None otherwise.
    *   `getMargeStats(include_bestfit=False)`: Returns a `MargeStats` object with marginalized 1D parameter constraints.
        *   `include_bestfit`: if True, set best fit values by loading from `root_name.minimum` file (assuming it exists).
        *   **Returns:** A `MargeStats` instance.
    *   `getMeans(pars=None)`: Gets the parameter means, from saved array if previously calculated.
        *   `pars`: optional list of parameter indices to return means for.
        *   **Returns:** numpy array of parameter means.
    *   `getName()`: Returns the name tag of these samples.
        *   **Returns:** The name tag.
    *   `getNumSampleSummaryText()`: Returns a summary text describing numbers of parameters and samples, and various measures of the effective numbers of samples.
        *   **Returns:** The summary text as a string.
    *   `getParamBestFitDict(best_sample=False, want_derived=True, want_fixed=True, max_posterior=True)`: Gets a dictionary of parameter values for the best fit point, assuming calculated results from minimization runs in `.minimum` (max posterior) `.bestfit` (max likelihood) files exists.
        *   `best_sample`: load from global minimum files (False, default) or using maximum posterior sample (True).
        *   `want_derived`: include derived parameters.
        *   `want_fixed`: also include values of any fixed parameters.
        *   `max_posterior`: whether to get maximum posterior (from `.minimum` file) or maximum likelihood (from `.bestfit` file).
        *   **Returns:** dictionary of parameter values.
    *   `getParamNames()`: Get `ParamNames` object with names for the parameters.
        *   **Returns:** `ParamNames` object giving parameter names and labels.
    *   `getParamSampleDict(ix, want_derived=True, want_fixed=True)`: Gets a dictionary of parameter values for sample number ix.
        *   `ix`: index of the sample to return (zero based).
        *   `want_derived`: include derived parameters.
        *   `want_fixed`: also include values of any fixed parameters.
        *   **Returns:** dictionary of parameter values.
    *   `getParams()`: Creates a `ParSamples` object, with variables giving vectors for all the parameters.
        *   **Returns:** A `ParSamples` object.
    *   `getRawNDDensity(xs, normalized=False, **kwargs)`: Returns a `DensityND` instance with marginalized ND density.
        *   `xs`: indices or names of x_i parameters.
        *   `kwargs`: keyword arguments for the `getNDDensityGridData()` function.
        *   `normalized`: if False, is normalized so the maximum is 1, if True, density is normalized.
        *   **Returns:** `DensityND` instance.
    *   `getRawNDDensityGridData(js, writeDataToFile=False, num_plot_contours=None, get_density=False, meanlikes=False, maxlikes=False, **kwargs)`: Low-level function to get unsmooth ND plot marginalized density and optional additional plot data.
        *   `js`: vector of names or indices of the x_i parameters.
        *   `writeDataToFile`: save outputs to file.
        *   `num_plot_contours`: number of contours to calculate and return in density.contours.
        *   `get_density`: only get the ND marginalized density, no additional plot data, no contours.
        *   `meanlikes`: calculate mean likelihoods as well as marginalized density (returned as array in density.likes).
        *   `maxlikes`: calculate the profile likelihoods in addition to the others (returned as array in density.maxlikes).
        *   `kwargs`: optional settings to override instance settings (see `analysis_settings`).
        *   **Returns:** a `DensityND` instance.
    *   `getRenames()`: Gets dictionary of renames known to each parameter.
    *   `getSeparateChains() → List[WeightedSamples]`: Gets a list of samples for separate chains.
        *   **Returns:** The list of `WeightedSamples` for each chain.
    *   `getSignalToNoise(params, noise=None, R=None, eigs_only=False)`: Returns w, M, where w is the eigenvalues of the signal to noise (small y better constrained).
        *   `params`: list of parameters indices to use.
        *   `noise`: noise matrix.
        *   `R`: rotation matrix, defaults to inverse of Cholesky root of the noise matrix.
        *   `eigs_only`: only return eigenvalues.
        *   **Returns:** w, M, where w is the eigenvalues of the signal to noise.
    *   `getTable(columns=1, include_bestfit=False, **kwargs)`: Creates and returns a `ResultTable` instance. See also `getInlineLatex()`.
        *   `columns`: number of columns in the table.
        *   `include_bestfit`: True to include the bestfit parameter values (assuming set).
        *   `kwargs`: arguments for `ResultTable` constructor.
        *   **Returns:** A `ResultTable` instance.
    *   `getUpper(name)`: Return the upper limit of the parameter with the given name.
        *   `name`: parameter name.
        *   **Returns:** The upper limit if name exists, None otherwise.
    *   `getVars()`: Get the parameter variances.
        *   **Returns:** A numpy array of variances.
    *   `get_norm(where=None)`: gets the normalization, the sum of the sample weights: sum_i w_i.
        *   `where`: if specified, a filter for the samples to use (where x>=5 would mean only process samples with x>=5).
        *   **Returns:** normalization.
    *   `initParamConfidenceData(paramVec, start=0, end=None, weights=None)`: Initialize cache of data for calculating confidence intervals.
        *   `paramVec`: array of parameter values or int index of parameter to use.
        *   `start`: The sample start index to use.
        *   `end`: The sample end index to use, use None to go all the way to the end of the vector.
        *   `weights`: A numpy array of weights for each sample, defaults to `self.weights`.
        *   **Returns:** `ParamConfidenceData` instance.
    *   `initParameters(ini)`: Initializes settings. Gets parameters from `IniFile`.
        *   `ini`: The `IniFile` to be used.
    *   `loadChains(root, files_or_samples: Sequence, weights=None, loglikes=None, ignore_lines=None)`: Loads chains from files.
        *   `root`: Root name.
        *   `files_or_samples`: list of file names or list of arrays of samples, or single array of samples.
        *   `weights`: if loading from arrays of samples, corresponding list of arrays of weights.
        *   `loglikes`: if loading from arrays of samples, corresponding list of arrays of -log(likelihood).
        *   `ignore_lines`: Amount of lines at the start of the file to ignore, None not to ignore any.
        *   **Returns:** True if loaded successfully, False if none loaded.
    *   `makeSingle()`: Combines separate chains into one samples array.
        *   **Returns:** self.
    *   `makeSingleSamples(filename='', single_thin=None, random_state=None)`: Make file of unit weight samples by choosing samples with probability proportional to their weight.
        *   `single_thin`: factor to thin by; if not set generates as many samples as it can up to `self.max_scatter_points`.
        *   `random_state`: random seed or Generator.
        *   **Returns:** numpy array of selected weight-1 samples if no filename.
    *   `mean(paramVec, where=None)`: Get the mean of the given parameter vector.
        *   `paramVec`: array of parameter values or int index of parameter to use.
        *   `where`: if specified, a filter for the samples to use.
        *   **Returns:** parameter mean.
    *   `mean_diff(paramVec, where=None)`: Calculates an array of differences between a parameter vector and the mean parameter value.
        *   `paramVec`: array of parameter values or int index of parameter to use.
        *   `where`: if specified, a filter for the samples to use.
        *   **Returns:** array of p_i - mean(p_i).
    *   `mean_diffs(pars: None | int | Sequence = None, where=None) → Sequence`: Calculates a list of parameter vectors giving distances from parameter means.
        *   `pars`: if specified, list of parameter vectors or int parameter indices to use.
        *   `where`: if specified, a filter for the samples to use.
        *   **Returns:** list of arrays p_i-mean(p-i) for each parameter.
    *   `parLabel(i)`: Gets the latex label of the parameter.
        *   `i`: The index or name of a parameter.
        *   **Returns:** The parameter’s label.
    *   `parName(i, starDerived=False)`: Gets the name of i’th parameter.
        *   `i`: The index of the parameter.
        *   `starDerived`: add a star at the end of the name if the parameter is derived.
        *   **Returns:** The name of the parameter (string).
    *   `random_single_samples_indices(random_state=None, thin: float | None = None, max_samples: int | None = None)`: Returns an array of sample indices that give a list of weight-one samples, by randomly selecting samples depending on the sample weights.
        *   `random_state`: random seed or Generator.
        *   `thin`: additional thinning factor (>1 to get fewer samples).
        *   `max_samples`: optional parameter to thin to get a specified mean maximum number of samples.
        *   **Returns:** array of sample indices.
    *   `readChains(files_or_samples, weights=None, loglikes=None)`: Loads samples from a list of files or array(s), removing burn in, deleting fixed parameters, and combining into one `self.samples` array.
        *   `files_or_samples`: The list of file names to read, samples or list of samples.
        *   `weights`: array of weights if setting from arrays.
        *   `loglikes`: array of -log(likelihood) if setting from arrays.
        *   **Returns:** self.
    *   `removeBurn(remove=0.3)`: removes burn in from the start of the samples.
        *   `remove`: fraction of samples to remove, or if int >1, the number of sample rows to remove.
    *   `removeBurnFraction(ignore_frac)`: Remove a fraction of the samples as burn in.
        *   `ignore_frac`: fraction of sample points to remove from the start of the samples, or each chain if not combined.
    *   `reweightAddingLogLikes(logLikes)`: Importance sample the samples, by adding logLike (array of -log(likelihood values)) to the currently stored likelihoods, and re-weighting accordingly.
        *   `logLikes`: array of -log(likelihood) for each sample to adjust.
    *   `saveAsText(root, chain_index=None, make_dirs=False)`: Saves the samples as text files, including parameter names as .paramnames file.
        *   `root`: The root name to use.
        *   `chain_index`: Optional index to be used for the filename, zero based, e.g. for saving one of multiple chains.
        *   `make_dirs`: True if this should (recursively) create the directory if it doesn’t exist.
    *   `savePickle(filename)`: Save the current object to a file in pickle format.
    *   `saveTextMetadata(root, properties=None)`: Saves metadata about the sames to text files with given file root.
        *   `root`: root file name.
        *   `properties`: optional dictiory of values to save in `root.properties.ini`.
    *   `setColData(coldata, are_chains=True)`: Set the samples given an array loaded from file.
        *   `coldata`: The array with columns of [weights, -log(Likelihoods)] and sample parameter values.
        *   `are_chains`: True if coldata starts with two columns giving weight and -log(Likelihood).
    *   `setDiffs()`: saves `self.diffs` array of parameter differences from the y, e.g. to later calculate variances etc.
        *   **Returns:** array of differences.
    *   `setMeans()`: Calculates and saves the means of the samples.
        *   **Returns:** numpy array of parameter means.
    *   `setMinWeightRatio(min_weight_ratio=1e-30)`: Removes samples with weight less than `min_weight_ratio` times the maximum weight.
        *   `min_weight_ratio`: minimum ratio to max to exclude.
    *   `setParamNames(names=None)`: Sets the names of the params.
        *   `names`: Either a `ParamNames` object, the name of a .paramnames file to load, a list of name strings, otherwise use default names (param1, param2...).
    *   `setParams(obj)`: Adds array variables obj.name1, obj.name2 etc., where obj.name1 is the vector of samples with name ‘name1’.
        *   `obj`: The object instance to add the parameter vectors variables.
        *   **Returns:** The obj after alterations.
    *   `setRanges(ranges)`: Sets the ranges parameters, e.g. hard priors on positivity etc. If a min or max value is None, then it is assumed to be unbounded.
        *   `ranges`: A list or a tuple of [min,max] values for each parameter, or a dictionary giving [min,max] values for specific parameter names.
    *   `setSamples(samples, weights=None, loglikes=None, min_weight_ratio=None)`: Sets the samples from numpy arrays.
        *   `samples`: The sample values, n_samples x n_parameters numpy array, or can be a list of parameter vectors.
        *   `weights`: Array of weights for each sample. Defaults to 1 for all samples if unspecified.
        *   `loglikes`: Array of -log(Likelihood) values for each sample.
        *   `min_weight_ratio`: remove samples with weight less than `min_weight_ratio` of the maximum.
    *   `std(paramVec, where=None)`: Get the standard deviation of the given parameter vector.
        *   `paramVec`: array of parameter values or int index of parameter to use.
        *   `where`: if specified, a filter for the samples to use.
        *   **Returns:** parameter standard deviation.
    *   `thin(factor: int)`: Thin the samples by the given factor, giving set of samples with unit weight.
        *   `factor`: The factor to thin by.
    *   `thin_indices(factor, weights=None)`: Indices to make single weight 1 samples. Assumes integer weights.
        *   `factor`: The factor to thin by, should be int.
        *   `weights`: The weights to thin, None if this should use the weights stored in the object.
        *   **Returns:** array of indices of samples to keep.
    *   `thin_indices_and_weights(factor, weights)` (static method): Returns indices and new weights for use when thinning samples.
        *   `factor`: thin factor.
        *   `weights`: initial weight (counts) per sample point.
        *   **Returns:** (unique index, counts) tuple of sample index values to keep and new weights.
    *   `twoTailLimits(paramVec, confidence)`: Calculates two-tail equal-area confidence limit by counting samples in the tails.
        *   `paramVec`: array of parameter values or int index of parameter to use.
        *   `confidence`: confidence limit to calculate, e.g. 0.95 for 95% confidence.
        *   **Returns:** min, max values for the confidence interval.
    *   `updateBaseStatistics()`: Updates basic computed statistics (y, covariance etc.), e.g. after a change in samples or weights.
        *   **Returns:** self.
    *   `updateRenames(renames)`: Updates the renames known to each parameter with the given dictionary of renames.
    *   `updateSettings(settings: Mapping[str, Any] | None = None, ini: None | str | IniFile = None, doUpdate=True)`: Updates settings from a .ini file or dictionary.
        *   `settings`: A dict containing settings to set, taking preference over any values in ini.
        *   `ini`: The name of .ini file to get settings from, or an `IniFile` instance; by default uses current settings.
        *   `doUpdate`: True if we should update internal computed values, False otherwise.
    *   `var(paramVec, where=None)`: Get the variance of the given parameter vector.
        *   `paramVec`: array of parameter values or int index of parameter to use.
        *   `where`: if specified, a filter for the samples to use.
        *   **Returns:** parameter variance.
    *   `weighted_sum(paramVec, where=None)`: Calculates the weighted sum of a parameter vector, sum_i w_i p_i.
        *   `paramVec`: array of parameter values or int index of parameter to use.
        *   `where`: if specified, a filter for the samples to use.
        *   **Returns:** weighted sum.
    *   `weighted_thin(factor: int)`: Thin the samples by the given factor, giving (in general) non-unit integer weights. This function also preserves separate chains.
        *   `factor`: The (integer) factor to thin by.
    *   `writeCorrelationMatrix(filename=None)`: Write the correlation matrix to a file. If none writes to `file_root.corr`.
    *   `writeCovMatrix(filename=None)`: Writes the covrariance matrix of non-derived parameters to a file. Default is `file_root.covmat`.
    *   `writeThinData(fname, thin_ix, cool=1)`: Writes samples at thin_ix to file.
        *   `thin_ix`: Indices of the samples to write.
        *   `cool`: if not 1, cools the samples by this factor.

*   **Exceptions:**
    *   `exception getdist.mcsamples.MCSamplesError`: Raised when there is an error inside the `MCSamples` class.
    *   `exception getdist.mcsamples.ParamError`: Indicates a bad parameter.
    *   `exception getdist.mcsamples.SettingError`: Indicates bad settings.

## `getdist.plots`

Module for making plots from samples. Use `get_single_plotter()` and `get_subplot_plotter()` to get a plotter instance. Parameters are referenced by name. Glob patterns (`x*`) can match subsets.

### Functions

*   `get_single_plotter(ratio: float | None = None, width_inch: float | None = None, scaling: bool | None = None, rc_sizes=False, style: str | None = None, **kwargs)`: Get a `GetDistPlotter` for making a single plot of fixed width.
    *   `ratio`: The ratio between height and width.
    *   `width_inch`: The width of the plot in inches (e.g., 3.464 for half-column).
    *   `scaling`: whether to scale down fonts and line widths for small subplot axis sizes.
    *   `rc_sizes`: set default font sizes from matplotlib’s current rcParams if no explicit settings passed in kwargs.
    *   `style`: name of a plotter style, otherwise uses active style.
    *   `kwargs`: arguments for `GetDistPlotter`.
    *   **Returns:** The `GetDistPlotter` instance.
*   `get_subplot_plotter(subplot_size: float | None = None, width_inch: float | None = None, scaling: bool | None = None, rc_sizes=False, subplot_size_ratio: float | None = None, style: str | None = None, **kwargs) → GetDistPlotter`: Get a `GetDistPlotter` for making an array of subplots.
    *   `subplot_size`: The size of each subplot in inches.
    *   `width_inch`: Optional total width in inches. If None, plot is made as big as needed for `subplot_size`.
    *   `scaling`: whether to scale down fonts and line widths for small sizes.
    *   `rc_sizes`: set default font sizes from matplotlib’s current rcParams if no explicit settings passed in kwargs.
    *   `subplot_size_ratio`: ratio of height to width for subplots.
    *   `style`: name of a plotter style, otherwise uses active style.
    *   `kwargs`: arguments for `GetDistPlotter`.
    *   **Returns:** The `GetDistPlotter` instance.
*   `add_plotter_style(name, cls, activate=False)`: Add a plotting style.
    *   `name`: name for the style.
    *   `cls`: a class inherited from `GetDistPlotter`.
    *   `activate`: whether to make it the active style.
*   `get_plotter(style: str | None = None, **kwargs)`: Creates a new plotter and returns it.
    *   `style`: name of a plotter style, otherwise uses active.
    *   `kwargs`: arguments for the style’s `GetDistPlotter`.
    *   **Returns:** The `GetDistPlotter` instance.
*   `set_active_style(name=None)`: Set an active style name. Supplied styles: 'default', 'tab10', 'planck'.
    *   `name`: name of the style, or none to revert to default.
    *   **Returns:** the previously active style name.

### `GetDistPlotter`

```python
class getdist.plots.GetDistPlotter(chain_dir: str | Iterable[str] | None = None, settings: GetDistPlotSettings | None = None, analysis_settings: str | dict | IniFile = None, auto_close=False)
```

Main class for making plots from one or more sets of samples.

*   **Variables:**
    *   `settings`: a `GetDistPlotSettings` instance with settings.
    *   `subplots`: a 2D array of `Axes` for subplots.
    *   `sample_analyser`: a `MCSampleAnalysis` instance for getting `MCSamples` and derived data from a given root name tag.
*   **Parameters:**
    *   `chain_dir`: Set this to a directory or grid directory hierarchy to search for chains (can also be a list of such, searched in order).
    *   `settings`: A `GetDistPlotSettings` instance.
    *   `analysis_settings`: The settings to be used by `MCSampleAnalysis` when analysing samples (str, dict, or IniFile).
    *   `auto_close`: whether to automatically close the figure whenever a new plot made or this instance released.
*   **Methods (Brief Summary):**
    *   `__init__(...)`: Initialize plotter.
    *   `add_1d(...)`: Add 1D marginalized density line.
    *   `add_2d_contours(...)`: Add 2D contours.
    *   `add_2d_covariance(...)`: Plot 2D Gaussian ellipse.
    *   `add_2d_density_contours(...)`: Add 2D contours from provided density.
    *   `add_2d_mixture_projection(...)`: (Internal/Advanced use)
    *   `add_2d_scatter(...)`: Add 2D sample scatter plot.
    *   `add_2d_shading(...)`: Add 2D density shading.
    *   `add_3d_scatter(...)`: Add 3D scatter plot (2D plot colored by 3rd param).
    *   `add_4d_scatter(...)`: (Internal/Advanced use)
    *   `add_bands(...)`: Add constraint band (e.g., 1/2 sigma) vs x.
    *   `add_colorbar(...)`: Add color bar.
    *   `add_colorbar_label(...)`: Add color bar label.
    *   `add_legend(...)`: Add legend to axes or figure.
    *   `add_line(...)`: Add a line using `Line2D`.
    *   `add_param_markers(...)`: Add vertical/horizontal lines marking parameter values on all subplots.
    *   `add_text(...)`: Add text to axis.
    *   `add_text_left(...)`: Add text to left of axis.
    *   `add_x_bands(...)`: Add vertical shaded bands (e.g., 1/2 sigma).
    *   `add_x_marker(...)`: Add vertical lines marking x values.
    *   `add_y_bands(...)`: Add horizontal shaded bands.
    *   `add_y_marker(...)`: Add horizontal lines marking y values.
    *   `default_col_row(...)`: Get default subplot layout.
    *   `export(...)`: Export figure to file.
    *   `finish_plot(...)`: Finish plot (adjust spacing, add legend).
    *   `get_axes(...)`: Get `Axes` instance for subplot/parameter.
    *   `get_axes_for_params(...)`: Get `Axes` for given parameters.
    *   `get_param_array(...)`: Get array of `ParamInfo` for named params.
    *   `get_single_plotter(...)`: Get a single plotter instance.
    *   `get_subplot_plotter(...)`: Get a subplot plotter instance.
    *   `make_figure(...)`: Make new figure with subplots.
    *   `new_plot(...)`: Reset plotter for new empty plot.
    *   `param_bounds_for_root(...)`: Get hard prior bounds for root.
    *   `param_latex_label(...)`: Get LaTeX label for parameter.
    *   `param_names_for_root(...)`: Get `ParamNames` instance for root.
    *   `plot_1d(...)`: Make single 1D marginalized density plot.
    *   `plot_2d(...)`: Make single 2D contour/filled/line plot.
    *   `plot_2d_scatter(...)`: Make 2D sample scatter plot.
    *   `plot_3d(...)`: Make 2D scatter plot colored by 3rd param.
    *   `plot_4d(...)`: Make 3D scatter plot colored by 4th param (can animate).
    *   `plots_1d(...)`: Make array of 1D subplots.
    *   `plots_2d(...)`: Make array of 2D subplots.
    *   `plots_2d_triplets(...)`: Make array of 2D plots with different samples/params per plot.
    *   `plots_3d(...)`: Make multiple 3D subplots.
    *   `plots_3d_z(...)`: Make set of scatter subplots colored by different z params.
    *   `rectangle_plot(...)`: Make grid of 2D plots.
    *   `rotate_xticklabels(...)`: Rotate x-tick labels.
    *   `rotate_yticklabels(...)`: Rotate y-tick labels.
    *   `samples_for_root(...)`: Get `MCSamples` instance for root name.
    *   `set_axes(...)`: Set axis labels, ticks, styles.
    *   `set_default_settings()`: (Internal use)
    *   `set_xlabel(...)`: Set x-axis label.
    *   `set_ylabel(...)`: Set y-axis label.
    *   `set_zlabel(...)`: Set z-axis label (for 3D plots).
    *   `show_all_settings()`: Print settings and library versions.
    *   `triangle_plot(...)`: Make triangle plot (corner plot).

*   **(Detailed methods documented below)**

### `GetDistPlotSettings`

```python
class getdist.plots.GetDistPlotSettings(subplot_size_inch: float = 2, fig_width_inch: float | None = None)
```

Settings class (colors, sizes, font, styles etc.).

*   **Variables (Selected):**
    *   `alpha_factor_contour_lines`: alpha factor for adding contour lines between filled contours.
    *   `alpha_filled_add`: alpha for adding filled contours to a plot.
    *   `axes_fontsize`: Size for axis font at reference axis size.
    *   `axes_labelsize`: Size for axis label font at reference axis size.
    *   `axis_marker_color`, `axis_marker_ls`, `axis_marker_lw`: Styles for axis markers.
    *   `axis_tick_powerlimits`, `axis_tick_max_labels`, `axis_tick_step_groups`: Axis tick settings.
    *   `axis_tick_x_rotation`, `axis_tick_y_rotation`: Tick label rotation.
    *   `colorbar_axes_fontsize`, `colorbar_label_pad`, `colorbar_label_rotation`, `colorbar_tick_rotation`: Colorbar settings.
    *   `colormap`, `colormap_scatter`: Matplotlib colormaps.
    *   `constrained_layout`: use matplotlib’s constrained-layout.
    *   `fig_width_inch`: The width of the figure in inches.
    *   `figure_legend_frame`, `figure_legend_loc`, `figure_legend_ncol`: Figure legend settings.
    *   `fontsize`: Default font size.
    *   `legend_colored_text`, `legend_fontsize`, `legend_frac_subplot_margin`, `legend_frame`, `legend_loc`, `legend_rect_border`: Legend appearance settings.
    *   `line_dash_styles`: dict mapping styles ('--', '-.') to dash patterns.
    *   `line_labels`: True to auto-add legends for multiple lines.
    *   `line_styles`: List of default styles/colors or colormap name.
    *   `linewidth`, `linewidth_contour`, `linewidth_meanlikes`: Linewidths.
    *   `no_triangle_axis_labels`: Whether triangle plots show axis labels only at edge.
    *   `norm_1d_density`, `norm_prob_label`: 1D density normalization settings.
    *   `num_plot_contours`: Number of contours to plot in 2D.
    *   `num_shades`: Number of colors for shaded 2D plots.
    *   `param_names_for_labels`: File to override parameter labels.
    *   `plot_args`: Dict or list of dicts for plot settings (color, ls, alpha).
    *   `plot_meanlikes`: Include mean likelihood lines in 1D plots.
    *   `prob_label`, `prob_y_ticks`: 1D density y-axis settings.
    *   `progress`: Write out status.
    *   `scaling`, `scaling_max_axis_size`, `scaling_factor`, `scaling_reference_size`, `direct_scaling`: Font/line scaling settings.
    *   `scatter_size`: Point size for 3D scatter plots.
    *   `shade_level_scale`: Scaling for shaded contour levels.
    *   `shade_meanlikes`: Use mean likelihoods for 2D shading.
    *   `solid_colors`: List of colors/tuples for filled 2D plots or colormap name.
    *   `solid_contour_palefactor`: Factor to make outer filled contours paler.
    *   `subplot_size_ratio`: Ratio of width and height of subplots.
    *   `tight_layout`: Use `tight_layout`.
    *   `title_limit`: Show parameter limits over 1D plots (1=68%, 2=95%).
    *   `title_limit_labels`: Include parameter label in title limits.
    *   `title_limit_fontsize`: Font size for title limits.

*   **Methods:**
    *   `__init__(subplot_size_inch: float = 2, fig_width_inch: float | None = None)`: Initialize settings.
        *   `subplot_size_inch`: Determines the size of subplots, and hence default font sizes.
        *   `fig_width_inch`: The width of the figure in inches, If set, forces fixed total size.
    *   `rc_sizes(axes_fontsize=None, lab_fontsize=None, legend_fontsize=None)`: Sets the font sizes by default from matplotlib.rcParams defaults.
        *   `axes_fontsize`: The font size for the plot axes tick labels (default: xtick.labelsize).
        *   `lab_fontsize`: The font size for the plot’s axis labels (default: axes.labelsize).
        *   `legend_fontsize`: The font size for the plot’s legend (default: legend.fontsize).
    *   `scaled_fontsize(ax_size, var[, default])`: (Internal use).
    *   `scaled_linewidth(ax_size, linewidth)`: (Internal use).
    *   `set_with_subplot_size(size_inch=3.5, size_mm=None, size_ratio=None)`: Sets the subplot's size, either in inches or in millimeters.
        *   `size_inch`: The size to set in inches; is ignored if size_mm is set.
        *   `size_mm`: None if not used, otherwise the size in millimeters we want to set for the subplot.
        *   `size_ratio`: ratio of height to width of subplots.

*   **Exceptions:**
    *   `exception getdist.plots.GetDistPlotError`: Raised when there is an error plotting.

### `GetDistPlotter` Methods (Detailed)

*(Selected common methods; refer to source/docs for full details)*

*   `add_1d(root, param, plotno=0, normalized=None, ax=None, title_limit=None, **kwargs)`: Low-level function to add a 1D marginalized density line to a plot.
    *   `root`: The root name of the samples.
    *   `param`: The parameter name.
    *   `plotno`: The index of the line being added to the plot.
    *   `normalized`: True if areas under the curves should match, False if normalized to unit maximum. Default from `settings.norm_1d_density`.
    *   `ax`: optional `Axes` instance (or y,x subplot coordinate) to add to.
    *   `title_limit`: if not None, a maginalized limit (1,2..) to print as the title of the plot.
    *   `kwargs`: arguments for `plot()`.
    *   **Returns:** min, max for the plotted density.
*   `add_2d_contours(root, param1=None, param2=None, plotno=0, of=None, cols=None, contour_levels=None, add_legend_proxy=True, param_pair=None, density=None, alpha=None, ax=None, mask_function: callable = None, **kwargs)`: Low-level function to add 2D contours to plot for samples.
    *   `root`: The root name of samples to use or a `MixtureND` gaussian mixture.
    *   `param1`: x parameter.
    *   `param2`: y parameter.
    *   `plotno`: The index of the contour lines being added.
    *   `of`: the total number of contours being added (this is line `plotno` of `of`).
    *   `cols`: optional list of colors to use for contours.
    *   `contour_levels`: levels at which to plot the contours.
    *   `add_legend_proxy`: True to add a proxy to the legend of this plot.
    *   `param_pair`: an [x,y] parameter name pair if you prefer to provide this rather than `param1` and `param2`.
    *   `density`: optional `Density2D` to plot rather than that computed automatically.
    *   `alpha`: alpha for the contours added.
    *   `ax`: optional `Axes` instance (or y,x subplot coordinate) to add to.
    *   `mask_function`: optional function `mask_function(minx, miny, stepx, stepy, mask)` to define prior boundaries.
    *   `kwargs`: optional keyword arguments: `filled`, `color`, plus kwargs for `contour()` and `contourf()`.
    *   **Returns:** bounds (from `bounds()`) for the 2D density plotted.
*   `add_2d_scatter(root, x, y, color='k', alpha=1, extra_thin=1, scatter_size=None, ax=None)`: Low-level function to add a 2D sample scatter plot.
    *   `root`: The root name of the samples to use.
    *   `x`: name of x parameter.
    *   `y`: name of y parameter.
    *   `color`: color to plot the samples.
    *   `alpha`: The alpha to use.
    *   `extra_thin`: thin the weight one samples by this additional factor before plotting.
    *   `scatter_size`: point size (default: `settings.scatter_size`).
    *   `ax`: optional `Axes` instance (or y,x subplot coordinate) to add to.
    *   **Returns:** (xmin, xmax), (ymin, ymax) bounds for the axes.
*   `add_3d_scatter(root, params, color_bar=True, alpha=1, extra_thin=1, scatter_size=None, ax=None, alpha_samples=False, **kwargs)`: Low-level function to add a 3D scatter plot (2D plot colored by 3rd param).
    *   `root`: The root name of the samples to use.
    *   `params`: list of parameters to plot [x, y, color].
    *   `color_bar`: True to add a colorbar for the plotted scatter color.
    *   `alpha`: The alpha to use.
    *   `extra_thin`: thin the weight one samples by this additional factor before plotting.
    *   `scatter_size`: point size (default: `settings.scatter_size`).
    *   `ax`: optional `Axes` instance (or y,x subplot coordinate) to add to.
    *   `alpha_samples`: use all samples, giving each point alpha corresponding to relative weight.
    *   `kwargs`: arguments for `add_colorbar()`.
    *   **Returns:** (xmin, xmax), (ymin, ymax) bounds for the axes.
*   `add_legend(legend_labels, legend_loc=None, line_offset=0, legend_ncol=None, colored_text=None, figure=False, ax=None, label_order=None, align_right=False, fontsize=None, figure_legend_outside=True, **kwargs)`: Add a legend to the axes or figure.
    *   `legend_labels`: The labels.
    *   `legend_loc`: The legend location, default from settings.
    *   `line_offset`: The offset of plotted lines to label (e.g. 1 to not label first line).
    *   `legend_ncol`: The number of columns in the legend, defaults to 1.
    *   `colored_text`: True: legend labels are colored; False: colored lines/boxes before black labels.
    *   `figure`: True if legend is for the figure rather than the selected axes.
    *   `ax`: if `figure == False`, the `Axes` instance to use; defaults to current axes.
    *   `label_order`: minus one for reverse order, or list giving specific order of line indices.
    *   `align_right`: True to align legend text at the right.
    *   `fontsize`: The size of the font, default from settings.
    *   `figure_legend_outside`: whether figure legend is outside or inside the subplots box.
    *   `kwargs`: optional extra arguments for legend function.
    *   **Returns:** a `matplotlib.legend.Legend` instance.
*   `export(fname=None, adir=None, watermark=None, tag=None, **kwargs)`: Exports given figure to a file.
    *   `adir`: The directory to save to.
    *   `watermark`: a watermark text.
    *   `tag`: A suffix to add to the filename.
*   `finish_plot(legend_labels=None, legend_loc=None, line_offset=0, legend_ncol=None, label_order=None, no_extra_legend_space=False, no_tight=False, **legend_args)`: Finish the current plot, adjusting subplot spacing and adding legend if required.
    *   `legend_labels`: The labels for a figure legend.
    *   `legend_loc`: The legend location, default from settings (`figure_legend_loc`).
    *   `line_offset`: The offset of plotted lines to label.
    *   `legend_ncol`: The number of columns in the legend, defaults to 1.
    *   `label_order`: minus one for reverse order, or list giving specific order.
    *   `no_extra_legend_space`: True to put figure legend inside the figure box.
    *   `no_tight`: don’t use `tight_layout()` to adjust subplot positions.
    *   `legend_args`: optional parameters for the legend.
*   `plot_1d(roots, param, marker=None, marker_color=None, label_right=False, title_limit=None, no_ylabel=False, no_ytick=False, no_zero=False, normalized=False, param_renames=None, ax=None, **kwargs)`: Make a single 1D plot with marginalized density lines.
    *   `roots`: root name or `MCSamples` instance (or list of these).
    *   `param`: the parameter name to plot.
    *   `marker`: If set, places a marker at given coordinate (or list of coordinates).
    *   `marker_color`: If set, sets the marker color.
    *   `label_right`: If True, label the y-axis on the right.
    *   `title_limit`: If not None, a maginalized limit (1,2..) of the first root to print as the title.
    *   `no_ylabel`: If True excludes the label on the y-axis.
    *   `no_ytick`: If True show no y ticks.
    *   `no_zero`: If true does not show tick label at zero on y-axis.
    *   `normalized`: plot normalized densities.
    *   `param_renames`: optional dictionary mapping input parameter names to equivalent names used by the samples.
    *   `ax`: optional `Axes` instance to add to.
    *   `kwargs`: additional optional keyword arguments: `lims`, `ls`, `colors`, `lws`, `alphas`, `line_args`, `marker_args`, arguments for `set_axes()`.
*   `plot_2d(roots, param1=None, param2=None, param_pair=None, shaded=False, add_legend_proxy=True, line_offset=0, proxy_root_exclude=(), ax=None, mask_function: callable = None, **kwargs)`: Create a single 2D line, contour or filled plot.
    *   `roots`: root name or `MCSamples` instance (or list of these).
    *   `param1`: x parameter name.
    *   `param2`: y parameter name.
    *   `param_pair`: An [x,y] pair of params; can be set instead of `param1` and `param2`.
    *   `shaded`: True or integer if plot should be a shaded density plot.
    *   `add_legend_proxy`: True to add to the legend proxy.
    *   `line_offset`: line_offset if not adding first contours to plot.
    *   `proxy_root_exclude`: any root names not to include when adding to the legend proxy.
    *   `ax`: optional `Axes` instance to add to.
    *   `mask_function`: Function `mask_function(minx, miny, stepx, stepy, mask)` defining prior boundaries.
    *   `kwargs`: additional optional arguments: `filled`, `lims`, `ls`, `colors`, `lws`, `alphas`, `line_args`, arguments for `set_axes()`.
    *   **Returns:** The xbounds, ybounds of the plot.
*   `plot_3d(roots, params=None, params_for_plots=None, color_bar=True, line_offset=0, add_legend_proxy=True, alpha_samples=False, ax=None, **kwargs)`: Make a 2D scatter plot colored by the value of a third parameter (a 3D plot).
    *   `roots`: root name or `MCSamples` instance (or list of these).
    *   `params`: list with the three parameter names to plot (x, y, color).
    *   `params_for_plots`: list of parameter triplets to plot for each root plotted; more general alternative to `params`.
    *   `color_bar`: True to include a color bar.
    *   `line_offset`: The line index offset for added contours (if multiple roots).
    *   `add_legend_proxy`: True to add a legend proxy.
    *   `alpha_samples`: if True, use alternative scatter style where all samples are plotted alphaed by their weights.
    *   `ax`: optional `Axes` instance to add to.
    *   `kwargs`: additional optional arguments: `filled`, `lims`, `ls`, `colors`, `lws`, `alphas`, `line_args`, arguments for `add_colorbar()`.
*   `plot_4d(roots, params, color_bar=True, colorbar_args: Mapping = ..., ax=None, lims=mappingproxy({}), azim: float | None = 15, elev: float | None = None, dist: float = 12, alpha: float | Sequence[float] = 0.5, marker='o', max_scatter_points: int | None = None, shadow_color=None, shadow_alpha=0.1, fixed_color=None, compare_colors=None, animate=False, anim_angle_degrees=360, anim_step_degrees=0.6, anim_fps=15, mp4_filename: str | None = None, mp4_bitrate=-1, **kwargs)`: Make a 3d x-y-z scatter plot colored by the value of a fourth parameter. Can animate rotation.
    *   `roots`: root name or `MCSamples` instance (or list of these).
    *   `params`: list with the three parameter names to plot and color (x, y, z, color); can also set `fixed_color` and specify just three parameters.
    *   `color_bar`: True if you want to include a color bar.
    *   `colorbar_args`: extra arguments for colorbar.
    *   `ax`: optional `Axes3D` instance to add to.
    *   `lims`: dictionary of optional limits, e.g. `{'param1':(min1, max1)}`.
    *   `azim`: azimuth for initial view.
    *   `elev`: elevation for initial view.
    *   `dist`: distance for view.
    *   `alpha`: alpha, or list of alphas for each root, to use for scatter samples.
    *   `marker`: marker, or list of markers for each root.
    *   `max_scatter_points`: if set, maximum number of points to plots from each root.
    *   `shadow_color`: if not None, color value(s) for axes-projected samples; True for gray.
    *   `shadow_alpha`: if not None, separate alpha or list of alpha for shadows.
    *   `fixed_color`: if not None, fixed color for the first-root scatter plot.
    *   `compare_colors`: if not None, fixed scatter color for second-and-higher roots.
    *   `animate`: if True, rotate the plot.
    *   `anim_angle_degrees`: total angle for animation rotation.
    *   `anim_step_degrees`: angle per frame.
    *   `anim_fps`: animation frames per second.
    *   `mp4_filename`: if animating, optional filename to produce mp4 video.
    *   `mp4_bitrate`: bitrate for mp4 video.
    *   `kwargs`: additional optional arguments for `scatter()`.
*   `triangle_plot(roots, params=None, legend_labels=None, plot_3d_with_param=None, filled=False, shaded=False, contour_args=None, contour_colors=None, contour_ls=None, contour_lws=None, line_args=None, label_order=None, legend_ncol=None, legend_loc=None, title_limit=None, upper_roots=None, upper_kwargs=mappingproxy({}), upper_label_right=False, diag1d_kwargs=mappingproxy({}), markers=None, marker_args=mappingproxy({}), param_limits=mappingproxy({}), **kwargs)`: Make a triangular array of 1D and 2D plots (corner plot).
    *   `roots`: root name or `MCSamples` instance (or list of these). Can also contain a theory `MixtureND`.
    *   `params`: list of parameters to plot (default: all).
    *   `legend_labels`: list of legend labels.
    *   `plot_3d_with_param`: for 2D plots, make scatter plot colored by this parameter name.
    *   `filled`: True for filled contours.
    *   `shaded`: plot shaded density for first root.
    *   `contour_args`: optional dict (or list) with arguments for each 2D plot.
    *   `contour_colors`: list of colors for plotting contours (for each root).
    *   `contour_ls`: list of Line styles for 2D unfilled contours (for each root).
    *   `contour_lws`: list of Line widths for 2D unfilled contours (for each root).
    *   `line_args`: dict (or list) with arguments for each 2D plot.
    *   `label_order`: minus one for reverse order, or list of indices.
    *   `legend_ncol`: Number of columns for the legend.
    *   `legend_loc`: Location for the legend.
    *   `title_limit`: limit (1,2..) to print as title on diagonal 1D plots.
    *   `upper_roots`: list of sample root names to fill the upper triangle.
    *   `upper_kwargs`: dict for same-named arguments for upper-triangle 2D plots.
    *   `upper_label_right`: when using `upper_roots`, label y axis on top-right axes.
    *   `diag1d_kwargs`: list of dict for arguments for 1D plots on diagonal.
    *   `markers`: optional dict giving marker values indexed by parameter, or list for each param.
    *   `marker_args`: dictionary of optional arguments for adding markers.
    *   `param_limits`: dictionary mapping parameter names to axis limits.
    *   `kwargs`: optional keyword arguments for `plot_2d()` or `plot_3d()` (lower triangle only).

### `MCSampleAnalysis`

```python
class getdist.plots.MCSampleAnalysis(chain_locations: str | Iterable[str], settings: str | dict | IniFile = None)
```

A class that loads and analyses samples, mapping root names to `MCSamples` objects with caching. Accessed via `plotter.sample_analyser`.

*   **Parameters:**
    *   `chain_locations`: either a directory or the path of a grid of runs; it can also be a list of such, which is searched in order.
    *   `settings`: Either an `IniFile` instance, the name of an .ini file, or a dict holding sample analysis settings.
*   **Methods:**
    *   `add_chain_dir(chain_dir)`: Adds a new chain directory or grid path for searching for samples.
    *   `add_root(file_root)`: Add a root file for some new samples.
        *   `file_root`: Either a file root name including path or a `RootInfo` instance.
        *   **Returns:** `MCSamples` instance for given root file.
    *   `add_roots(roots)`: Wrapper for `add_root` that adds multiple file roots.
        *   `roots`: An iterable containing filenames or `RootInfo` objects to add.
    *   `bounds_for_root(root)`: Returns an object with `get_upper`/`getUpper` and `get_lower`/`getLower` to get hard prior bounds for given root name.
        *   `root`: The root name to use.
    *   `get_density(root, param, likes=False)`: Get `Density1D` for given root name and parameter.
        *   `root`: The root name of the samples to use.
        *   `param`: name of the parameter.
        *   `likes`: whether to include mean likelihood in density.likes.
        *   **Returns:** `Density1D` instance.
    *   `get_density_grid(root, param1, param2, conts=2, likes=False)`: Get 2D marginalized density for given root name and parameters.
        *   `root`: The root name for samples to use.
        *   `param1`: x parameter.
        *   `param2`: y parameter.
        *   `conts`: number of contour levels.
        *   `likes`: whether to include mean likelihoods.
        *   **Returns:** `Density2D` instance.
    *   `load_single_samples(root)`: Gets a set of unit weight samples for given root name.
        *   `root`: The root name to use.
        *   **Returns:** array of unit weight samples.
    *   `params_for_root(root, label_params=None)`: Returns a `ParamNames` with names and labels for parameters used by samples with a given root name.
        *   `root`: The root name of the samples to use.
        *   `label_params`: optional name of .paramnames file containing labels to use for plots, overriding default.
        *   **Returns:** `ParamNames` instance.
    *   `remove_root(root)`: Remove a given root file (does not delete it).
        *   `root`: The root name to remove.
    *   `reset(settings=None, chain_settings_have_priority=True)`: Resets the caches, starting afresh optionally with new analysis settings.
        *   `settings`: Either an `IniFile` instance, the name of an .ini file, or a dict holding sample analysis settings.
        *   `chain_settings_have_priority`: whether to prioritize settings saved with the chain.
    *   `samples_for_root(root: str | MCSamples, file_root: str | None = None, cache=True, settings: Mapping[str, Any] | None = None)`: Gets `MCSamples` from root name (or just return root if it is already an `MCSamples` instance).
        *   `root`: The root name (without path, e.g. my_chains).
        *   `file_root`: optional full root path, by default searches in `self.chain_dirs`.
        *   `cache`: if True, return cached object if already loaded.
        *   `settings`: optional dictionary of settings to use.
        *   **Returns:** `MCSamples` for the given root name.

## `getdist.chains`

### `Chains`

```python
class getdist.chains.Chains(root=None, jobItem=None, paramNamesFile=None, names=None, labels=None, renames=None, sampler=None, **kwargs)
```

Holds one or more sets of weighted samples, e.g., a set of MCMC chains. Inherits from `WeightedSamples`.

*   **Variables:**
    *   `paramNames`: a `ParamNames` instance holding parameter names and labels.
*   **Parameters:**
    *   `root`: optional root name for files.
    *   `jobItem`: optional jobItem for parameter grid item.
    *   `paramNamesFile`: optional filename of a .paramnames files that holds parameter names.
    *   `names`: optional list of names for the parameters.
    *   `labels`: optional list of latex labels for the parameters.
    *   `renames`: optional dictionary of parameter aliases.
    *   `sampler`: string describing the type of samples (default :mcmc).
    *   `kwargs`: extra options for `WeightedSamples`'s constructor.
*   **Methods:** (Includes methods from `WeightedSamples` plus)
    *   `addDerived(paramVec, name, **kwargs)`: Adds a new parameter.
        *   `paramVec`: The vector of parameter values to add.
        *   `name`: The name for the new parameter.
        *   `kwargs`: arguments for `paramnames.ParamList.addDerived()`.
        *   **Returns:** The added parameter’s `ParamInfo` object.
    *   `deleteFixedParams()`: Delete parameters that are fixed. (Overrides `WeightedSamples` method).
    *   `getGelmanRubin(nparam=None, chainlist=None)`: Assess convergence using max var(mean)/mean(var).
    *   `getGelmanRubinEigenvalues(nparam=None, chainlist=None)`: Assess convergence using var(mean)/mean(var) eigenvalues.
    *   `getParamNames()`: Get `ParamNames` object.
    *   `getParamSampleDict(ix, want_derived=True)`: Returns a dictionary of parameter values for sample `ix`.
    *   `getParams()`: Creates a `ParSamples` object.
    *   `getRenames()`: Gets dictionary of renames.
    *   `getSeparateChains() → List[WeightedSamples]`: Gets a list of samples for separate chains.
    *   `loadChains(...)`: Loads chains from files. (Overrides `MCSamples` method).
    *   `makeSingle()`: Combines separate chains into one samples array.
    *   `removeBurnFraction(ignore_frac)`: Remove a fraction of samples as burn in.
    *   `saveAsText(...)`: Saves samples to text files.
    *   `savePickle(filename)`: Save object to pickle file.
    *   `saveTextMetadata(root)`: Saves metadata to text files.
    *   `setParamNames(names=None)`: Sets parameter names.
    *   `setParams(obj)`: Adds array variables to `obj`.
    *   `updateBaseStatistics()`: Updates basic statistics.
    *   `updateRenames(renames)`: Updates known renames.
    *   `weighted_thin(factor: int)`: Thins samples preserving weights.

### `WeightedSamples`

```python
class getdist.chains.WeightedSamples(filename=None, ignore_rows=0, samples=None, weights=None, loglikes=None, name_tag=None, label=None, files_are_chains=True, min_weight_ratio=1e-30)
```

Base class for a set of weighted parameter samples.

*   **Variables:**
    *   `weights`: array of weights for each sample (default: array of 1).
    *   `loglikes`: array of -log(Likelihoods) for each sample (default: array of 0).
    *   `samples`: n_samples x n_parameters numpy array of parameter values.
    *   `n`: number of parameters.
    *   `numrows`: number of samples positions (rows in the samples array).
    *   `name_tag`: name tag for the samples.
*   **Parameters:**
    *   `ignore_rows`: Number or fraction of rows to skip at start of file.
    *   `samples`: array of parameter values passed to `setSamples()`.
    *   `weights`: array of weights.
    *   `loglikes`: array of -log(Likelihood).
    *   `name_tag`: The name of this instance.
    *   `label`: latex label for these samples.
    *   `files_are_chains`: use False if the samples file does not start with weight and -logL columns.
    *   `min_weight_ratio`: remove samples with weight less than this times max weight.
*   **Methods:** (Core methods, many shared with `MCSamples`)
    *   `changeSamples(samples)`: Sets samples without changing weights/loglikes.
    *   `confidence(...)`: Calculate confidence limits by counting samples.
    *   `cool(cool: float)`: Cools samples by multiplying loglikes.
    *   `corr(pars=None)`: Get correlation matrix.
    *   `cov(pars=None, where=None)`: Get covariance matrix.
    *   `deleteFixedParams()`: Removes parameters that do not vary. Returns tuple (removed indices, fixed values).
    *   `deleteZeros()`: Remove samples with zero weight.
    *   `filter(where)`: Filter samples.
    *   `getAutocorrelation(...)`: Get auto-correlation array.
    *   `getCorrelationLength(...)`: Get auto-correlation length.
    *   `getCorrelationMatrix()`: Get correlation matrix.
    *   `getCov(...)`: Get covariance matrix.
    *   `getEffectiveSamples(...)`: Get effective number of samples for mean error.
    *   `getEffectiveSamplesGaussianKDE(...)`: Estimate effective samples for KDE MISE.
    *   `getEffectiveSamplesGaussianKDE_2d(...)`: Estimate 2D effective samples for KDE MISE.
    *   `getLabel()`: Get latex label.
    *   `getMeans(pars=None)`: Get parameter means.
    *   `getName()`: Get name tag.
    *   `getSignalToNoise(...)`: Get signal-to-noise eigenvalues.
    *   `getVars()`: Get parameter variances.
    *   `get_norm(where=None)`: Get sum of weights.
    *   `initParamConfidenceData(...)`: Initialize cache for confidence intervals.
    *   `mean(paramVec, where=None)`: Get mean of a parameter vector.
    *   `mean_diff(paramVec, where=None)`: Get differences from mean.
    *   `mean_diffs(...)`: Get list of difference vectors.
    *   `random_single_samples_indices(...)`: Get indices for weight-1 samples.
    *   `removeBurn(remove=0.3)`: Remove burn-in.
    *   `reweightAddingLogLikes(logLikes)`: Importance sample by adding logLikes.
    *   `saveAsText(...)`: Save samples to text file.
    *   `setColData(coldata, are_chains=True)`: Set samples from array.
    *   `setDiffs()`: Calculate and store differences from mean.
    *   `setMeans()`: Calculate and store means.
    *   `setMinWeightRatio(min_weight_ratio=1e-30)`: Remove low-weight samples.
    *   `setSamples(...)`: Set samples from numpy arrays.
    *   `std(paramVec, where=None)`: Get standard deviation.
    *   `thin(factor: int)`: Thin samples (unit weight output).
    *   `thin_indices(factor, weights=None)`: Get indices for thinning.
    *   `thin_indices_and_weights(factor, weights)` (static): Get indices and weights for thinning.
    *   `twoTailLimits(paramVec, confidence)`: Calculate two-tail confidence limits.
    *   `var(paramVec, where=None)`: Get variance.
    *   `weighted_sum(paramVec, where=None)`: Calculate weighted sum.
    *   `weighted_thin(factor: int)`: Thin samples preserving weights (non-unit output).

### Other Classes/Exceptions

*   `class getdist.chains.ParSamples`: Container for named parameter sample arrays.
*   `class getdist.chains.ParamConfidenceData(paramVec, norm, indexes, cumsum)`: Named tuple for confidence data.
*   `exception getdist.chains.ParamError`: Indicates a bad parameter.
*   `exception getdist.chains.WeightedSampleError`: Error in `WeightedSamples`.

### Module Functions

*   `chainFiles(root, chain_indices=None, ext='.txt', separator='_', first_chain=0, last_chain=-1, chain_exclude=None)`: Creates list of chain file names.
*   `covToCorr(cov, copy=True)`: Convert covariance matrix to correlation matrix.
*   `findChainFileRoot(chain_dir, root, search_subdirectories=True)`: Finds chain file root under directory hierarchy.
*   `getSignalToNoise(C, noise=None, R=None, eigs_only=False)`: Returns signal-to-noise eigenvalues.
*   `last_modified(files)`: Returns latest modification time for list of files.
*   `loadNumpyTxt(fname, skiprows=None)`: Utility to load numpy array from text file.

## `getdist.covmat`

### `CovMat`

```python
class getdist.covmat.CovMat(filename='', matrix=None, paramNames=None)
```

Class holding a covariance matrix for some named parameters.

*   **Variables:**
    *   `matrix`: the covariance matrix (square numpy array).
    *   `paramNames`: list of parameter name strings.
*   **Methods:**
    *   `correlation()`: Get the correlation matrix. Returns numpy array.
    *   `plot()`: Plot the correlation matrix as grid of colored squares.
    *   `rescaleParameter(name, scale)`: Used to rescale a covariance if a parameter is renormalized.
    *   `saveToFile(filename)`: Save the covariance matrix to a text file.

## `getdist.densities`

### `Density1D`

```python
class getdist.densities.Density1D(x, P=None, view_ranges=None)
```

Class for 1D marginalized densities, inheriting from `GridDensity`. Callable like `InterpolatedUnivariateSpline`.

*   **Parameters:**
    *   `x`: array of x values.
    *   `P`: array of densities at x values.
    *   `view_ranges`: optional range for viewing density.
*   **Methods:**
    *   `Prob(x, derivative=0)`: Calculate density at position x by interpolation.
        *   `x`: x value.
        *   `derivative`: optional order of derivative to calculate.
        *   **Returns:** P(x) density value.
    *   `bounds()`: Get min, max bounds (from `view_ranges` if set).
    *   `getLimits(p, interpGrid=None, accuracy_factor=None)`: Get parameter equal-density confidence limits.
        *   `p`: list of limits to calculate, e.g. `[0.68, 0.95]`.
        *   `interpGrid`: optional pre-computed cache.
        *   `accuracy_factor`: parameter to boost default accuracy for fine sampling.
        *   **Returns:** list of `(min, max, has_min, has_top)` values.

### `Density2D`

```python
class getdist.densities.Density2D(x, y, P=None, view_ranges=None, mask=None)
```

Class for 2D marginalized densities, inheriting from `GridDensity`. Callable like `RectBivariateSpline`.

*   **Parameters:**
    *   `x`: array of x values.
    *   `y`: array of y values.
    *   `P`: 2D array of density values at x, y.
    *   `view_ranges`: optional ranges for viewing density.
    *   `mask`: optional 2D boolean array for non-trivial mask.
*   **Methods:**
    *   `Prob(x, y, grid=False)`: Evaluate density at x,y using interpolation.
        *   `x`: x value or array.
        *   `y`: y value or array.
        *   `grid`: whether to make a grid. Default False.

### `DensityND`

```python
class getdist.densities.DensityND(xs, P=None, view_ranges=None)
```

Class for ND marginalized densities, inheriting from `GridDensity` and `LinearNDInterpolator`. (Not well tested).

*   **Parameters:**
    *   `xs`: list of arrays of x values.
    *   `P`: ND array of density values at xs.
    *   `view_ranges`: optional ranges for viewing density.
*   **Methods:**
    *   `Prob(xs)`: Evaluate density at x,y,z using interpolation.

### `GridDensity`

```python
class getdist.densities.GridDensity
```

Base class for probability density grids (normalized or not).

*   **Variables:**
    *   `P`: array of density values.
*   **Methods:**
    *   `bounds()`: Get bounds in order x, y, z... Returns list of (min,max) values.
    *   `getContourLevels(contours=(0.68, 0.95))`: Get contour levels.
        *   `contours`: list of confidence limits to get.
        *   **Returns:** list of contour levels.
    *   `normalize(by='integral', in_place=False)`: Normalize the density grid.
        *   `by`: 'integral' for standard normalization, or 'max' to normalize max value to unity.
        *   `in_place`: if True, normalize in place.
    *   `setP(P=None)`: Set the density grid values.

### Module Functions

*   `getContourLevels(inbins, contours=(0.68, 0.95), missing_norm=0, half_edge=True)`: Get contour levels enclosing fractions of probability for any dimension bins array.
    *   `inbins`: binned density.
    *   `contours`: list or tuple of confidence contours to calculate.
    *   `missing_norm`: accounts of any points not included in inbins.
    *   `half_edge`: If True, edge bins are only half integrated over in each direction.
    *   **Returns:** list of density levels.

### Exceptions

*   `exception getdist.densities.DensitiesError`

## `getdist.gaussian_mixtures`

### `Gaussian1D`

```python
class getdist.gaussian_mixtures.Gaussian1D(mean, sigma, **kwargs)
```

Simple 1D Gaussian. Inherits from `Mixture1D`.

### `Gaussian2D`

```python
class getdist.gaussian_mixtures.Gaussian2D(mean, cov, **kwargs)
```

Simple special case of a 2D Gaussian mixture model with only one component. Inherits from `Mixture2D`.

### `GaussianND`

```python
class getdist.gaussian_mixtures.GaussianND(mean, cov, is_inv_cov=False, **kwargs)
```

Simple special case of a Gaussian mixture model with only one component. Inherits from `MixtureND`.

### `Mixture1D`

```python
class getdist.gaussian_mixtures.Mixture1D(means, sigmas, weights=None, lims=None, name='x', xmin=None, xmax=None, **kwargs)
```

Gaussian mixture model in 1D with optional boundaries. Inherits from `MixtureND`.

*   **Methods:**
    *   `pdf(x)`: Calculate PDF.

### `Mixture2D`

```python
class getdist.gaussian_mixtures.Mixture2D(means, covs, weights=None, lims=None, names=('x', 'y'), xmin=None, xmax=None, ymin=None, ymax=None, **kwargs)
```

Gaussian mixture model in 2D with optional boundaries. Inherits from `MixtureND`.

*   **Methods:**
    *   `pdf(x, y=None)`: Calculate PDF. If `y` is None, returns 1D marginalized PDF for `x`.

### `MixtureND`

```python
class getdist.gaussian_mixtures.MixtureND(means, covs, weights=None, lims=None, names=None, label='', labels=None)
```

Gaussian mixture model with optional boundary ranges. Can plot theoretical contours.

*   **Parameters:**
    *   `means`: list of means for each Gaussian.
    *   `covs`: list of covariances for the Gaussians.
    *   `weights`: optional weight for each component (defaults to equal).
    *   `lims`: optional list of hard limits [[x1min,x1max], ...].
    *   `names`: list of parameter names (strings).
    *   `label`: name for labelling this mixture.
    *   `labels`: list of latex labels for each parameter.
*   **Methods:**
    *   `MCSamples(size, names=None, logLikes=False, random_state=None, **kwargs)`: Gets a set of independent samples as an `mcsamples.MCSamples` object.
    *   `conditionalMixture(fixed_params, fixed_param_values, label=None)`: Returns a reduced conditional mixture model.
    *   `density1D(index=0, num_points=1024, sigma_max=4, no_limit_marge=False)`: Get 1D marginalized density.
    *   `density2D(params=None, num_points=1024, xmin=None, xmax=None, ymin=None, ymax=None, sigma_max=5)`: Get 2D marginalized density.
    *   `marginalizedMixture(params, label=None, no_limit_marge=False) → MixtureND`: Calculates a reduced mixture model by marginalization.
    *   `pdf(x)`: Calculate the PDF. Assumes x is within boundaries.
    *   `pdf_marged(index, x, no_limit_marge=False)`: Calculate the 1D marginalized PDF.
    *   `sim(size, random_state=None)`: Generate an array of independent samples. Returns 2D array.

### `RandomTestMixtureND`

```python
class getdist.gaussian_mixtures.RandomTestMixtureND(ndim=4, ncomponent=1, names=None, weights=None, seed=None, label='RandomMixture')
```

Class for randomly generating an N-D gaussian mixture for testing.

### Module Functions

*   `randomTestMCSamples(ndim=4, ncomponent=1, nsamp=10009, nMCSamples=1, seed=10, names=None, labels=None)`: Get `MCSamples` instance(s) with random samples from random covariances.

## `getdist.inifile`

### `IniFile`

```python
class getdist.inifile.IniFile(settings=None, keep_includes=False, expand_environment_variables=True)
```

Class for storing option parameter values, reading/saving to file. Allows inheritance (`INCLUDE`, `DEFAULT`).

*   **Variables:**
    *   `params`: dictionary of name, values stored.
    *   `comments`: dictionary of optional comments for parameter names.
*   **Parameters:**
    *   `settings`: filename of .ini file or dictionary of name/values.
    *   `keep_includes`: False: load all files; True: store INCLUDE/DEFAULT entries separately.
    *   `expand_environment_variables`: whether to expand `$(var)` placeholders.
*   **Methods:**
    *   `array_bool(name, index=1, default=None)`: Get boolean value from `name(index)`.
    *   `array_float(name, index=1, default=None)`: Get float value from `name(index)`.
    *   `array_int(name, index=1, default=None)`: Get int value from `name(index)`.
    *   `array_string(name, index=1, default=None)`: Get str value from `name(index)`.
    *   `bool(name, default=False)`: Get boolean value.
    *   `bool_list(name, default=None)`: Get list of boolean values (e.g., from `name = T F T`).
    *   `expand_placeholders(s)`: Expand shell variables `$(var)`.
    *   `float(name, default=None)`: Get float value.
    *   `float_list(name, default=None)`: Get list of float values.
    *   `hasKey(name)`: Test if key name exists. Returns True or False.
    *   `int(name, default=None)`: Get int value.
    *   `int_list(name, default=None)`: Get list of int values.
    *   `isSet(name, allowEmpty=False)`: Tests whether value for name is set or is empty.
    *   `list(name, default=None, tp=None)`: Get list (from space-separated values). `tp` sets type.
    *   `ndarray(name, default=None, tp=<class 'numpy.float64'>)`: Get numpy array of values.
    *   `saveFile(filename=None)`: Save to a .ini file.
    *   `setAttr(name, instance, default=None, allowEmpty=False)`: Set attribute of an object to value of parameter.
    *   `split(name, default=None, tp=None)`: Gets a list of values, optionally cast to type `tp`.
    *   `string(name, default=None, allowEmpty=True)`: Get string value.

### Exceptions

*   `exception getdist.inifile.IniError`

## `getdist.paramnames`

### `ParamInfo`

```python
class getdist.paramnames.ParamInfo(line=None, name='', label='', comment='', derived=False, renames=None, number=None)
```

Parameter information object.

*   **Variables:**
    *   `name`: the parameter name tag (no spacing or punctuation).
    *   `label`: latex label (without enclosing $).
    *   `comment`: any descriptive comment describing the parameter.
    *   `isDerived`: True if a derived parameter, False otherwise (e.g. for MCMC parameters).

### `ParamList`

```python
class getdist.paramnames.ParamList(fileName=None, setParamNameFile=None, default=0, names=None, labels=None)
```

Holds an ordered list of `ParamInfo` objects describing a set of parameters.

*   **Variables:**
    *   `names`: list of `ParamInfo` objects.
*   **Parameters:**
    *   `fileName`: name of .paramnames file to load from.
    *   `setParamNameFile`: override specific parameter names’ labels using another file.
    *   `default`: set to int>0 to automatically generate default names/labels.
    *   `names`: a list of name strings to use.
*   **Methods:**
    *   `addDerived(name, **kwargs)`: adds a new parameter. Returns new `ParamInfo`.
    *   `getDerivedNames()`: Get names of all derived parameters.
    *   `getRenames(keep_empty=False)`: Gets dictionary of renames known to each parameter.
    *   `getRunningNames()`: Get names of all running (non-derived) parameters.
    *   `labels()`: Gets list of parameter labels.
    *   `list()`: Gets list of parameter name strings.
    *   `numberOfName(name)`: Gets parameter number (index) of given name tag. Returns -1 if not found.
    *   `parWithName(name, error=False, renames=None)`: Gets `ParamInfo` object for parameter name.
    *   `parsWithNames(names, error=False, renames=None)`: Gets list of `ParamInfo` instances for list of names (expands globs).
    *   `saveAsText(filename)`: Saves to a plain text .paramnames file.
    *   `updateRenames(renames)`: Updates renames known to each parameter.

### `ParamNames`

```python
class getdist.paramnames.ParamNames(fileName=None, setParamNameFile=None, default=0, names=None, labels=None)
```

Holds an ordered list of `ParamInfo` objects, inheriting from `ParamList`. Can load/save .paramnames files.

*   **Variables:**
    *   `names`: list of `ParamInfo` objects describing each parameter.
    *   `filenameLoadedFrom`: if loaded from file, the file name.
*   **Methods:**
    *   `loadFromFile(fileName)`: loads from plain text .paramnames file or "full" yaml file.

### Module Functions

*   `makeList(roots)`: Checks if input is list, if not, returns `[roots]`.
*   `mergeRenames(*dicts, **kwargs)`: Joins several dicts of renames.

## `getdist.parampriors`

### `ParamBounds`

```python
class getdist.parampriors.ParamBounds(fileName=None)
```

Class for holding list of parameter bounds (plotting or hard priors). Limit is None if not specified, 'N' if read from file.

*   **Variables:**
    *   `names`: list of parameter names.
    *   `lower`: dict of lower limits, indexed by parameter name.
    *   `upper`: dict of upper limits, indexed by parameter name.
*   **Methods:**
    *   `fixedValue(name)`: Returns fixed value if range has zero width, else None.
    *   `fixedValueDict()`: Returns dictionary of fixed parameter values.
    *   `getLower(name)`: Returns lower limit, or None if not specified.
    *   `getUpper(name)`: Returns upper limit, or None if not specified.
    *   `saveToFile(fileName)`: Save to a plain text file.

## `getdist.types`

### `BestFit`

```python
class getdist.types.BestFit(fileName=None, setParamNameFile=None, want_fixed=False, max_posterior=True)
```

Holds likelihood minimization result, inheriting from `ParamResults`. Reads `.minimum` or `.bestfit` file.

*   **Parameters:**
    *   `setParamNameFile`: optional .paramnames file for preferred labels.
    *   `want_fixed`: whether to include values of fixed parameters.
    *   `max_posterior`: True for max posterior (default, .minimum), False for max likelihood (.bestfit).

### `ConvergeStats`

```python
class getdist.types.ConvergeStats(fileName=None, setParamNameFile=None, default=0, names=None, labels=None)
```

Inherits from `ParamResults`. (Placeholder/TODO mentioned in docstring).

### `LikeStats`

```python
class getdist.types.LikeStats(fileName=None, setParamNameFile=None, default=0, names=None, labels=None)
```

Stores likelihood-related statistics (best-fit sample, N-D confidence region bounds), inheriting from `ParamResults`. (Save only, does not load full data).

### `MargeStats`

```python
class getdist.types.MargeStats(fileName=None, setParamNameFile=None, default=0, names=None, labels=None)
```

Stores marginalized 1D parameter statistics (mean, variance, confidence limits), inheriting from `ParamResults`. Values stored as attributes of `ParamInfo` objects in `self.names`.

*   Access `ParamInfo` via `par = margeStats.parWithName('xxx')`.
*   `par.mean`: parameter mean.
*   `par.err`: standard deviation.
*   `par.limits`: list of `ParamLimit` objects.
*   **Methods:**
    *   `loadFromFile(filename)`: Load from a plain text file.

### `ParamLimit`

```python
class getdist.types.ParamLimit(minmax, tag='two')
```

Class containing information about a marginalized parameter limit.

*   **Variables:**
    *   `lower`, `upper`: limits.
    *   `twotail`: True if two-tail limit.
    *   `onetail_upper`, `onetail_lower`: True if one-tail upper/lower limit.
*   **Parameters:**
    *   `minmax`: [min,max] tuple. Entries can be None.
    *   `tag`: text tag: 'two', '>', '<', 'none'.
*   **Methods:**
    *   `limitTag()`: Returns short text tag ('two', '>', '<', 'none').
    *   `limitType()`: Returns text description ('two tail', 'one tail upper/lower limit', 'none').

### `ParamResults`

```python
class getdist.types.ParamResults(fileName=None, setParamNameFile=None, default=0, names=None, labels=None)
```

Base class for parameter results, inheriting from `ParamList`. `self.names` is a list of `ParamInfo`.

### `ResultTable`

```python
class getdist.types.ResultTable(ncol, results, limit=2, tableParamNames=None, titles=None, formatter=None, numFormatter=None, blockEndParams=None, paramList=None, refResults=None, shiftSigma_indep=False, shiftSigma_subset=False)
```

Class for holding a latex table of parameter statistics.

*   **Parameters:**
    *   `ncol`: number of columns.
    *   `results`: a `MargeStats` or `BestFit` instance, or list for comparison, or `MCSamples` instance.
    *   `limit`: which limit to include (1=68%, 2=95%).
    *   `tableParamNames`: optional `ParamNames` instance listing parameters to include.
    *   `titles`: optional titles describing different results.
    *   `formatter`: a table formatting class.
    *   `numFormatter`: a number formatting class.
    *   `blockEndParams`: mark parameters in blocks, ending on this list of names.
    *   `paramList`: list of parameter names (strings) to include.
    *   `refResults`: reference `MargeStats` instance for showing parameter shifts.
    *   `shiftSigma_indep`: show shifts in sigma assuming independent data.
    *   `shiftSigma_subset`: show shifts in sigma assuming subset data.
*   **Methods:**
    *   `tablePNG(dpi=None, latex_preamble=None, filename=None, bytesIO=False)`: Get a .png image of the table (requires LaTeX).
    *   `tableTex(document=False, latex_preamble=None, packages=('amsmath', 'amssymb', 'bm'))`: Get the latex string for the table.
    *   `write(fname, **kwargs)`: Write the latex table to a file.

```