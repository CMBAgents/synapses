GetDist Jupyter Notebook Plot Gallery
===============
Demonstrates the types of plot you can make with [GetDist](https://getdist.readthedocs.io) and how to make them. 
You can also [run this notebook online](https://mybinder.org/v2/gh/cmbant/getdist/master?filepath=docs%2Fplot_gallery.ipynb).


```python
# Show plots inline, and load main getdist plot module and samples class
%matplotlib inline
%config InlineBackend.figure_format = 'retina'
import sys, os
sys.path.insert(0,os.path.realpath(os.path.join(os.getcwd(),'..')))
from getdist import plots, MCSamples
import getdist
import matplotlib.pyplot as plt
import IPython
print('GetDist Version: %s, Matplotlib version: %s'%(getdist.__version__, plt.matplotlib.__version__))
```


```python
# use this here *after* the above (instead of matplotlib inline) to use interactive plots
# %matplotlib notebook
```


```python
# Get some random samples for demonstration:
# make random covariance, then independent samples from Gaussian
import numpy as np
ndim = 4
nsamp = 10000
random_state = np.random.default_rng(10) # seed random generator
A = random_state.random((ndim,ndim))
cov = np.dot(A, A.T)
samps = random_state.multivariate_normal([0]*ndim, cov, size=nsamp)
A = random_state.random((ndim,ndim))
cov = np.dot(A, A.T)
samps2 = random_state.multivariate_normal([0]*ndim, cov, size=nsamp)
```


```python
# Get the getdist MCSamples objects for the samples, specifying same parameter
# names and labels; if not specified weights are assumed to all be unity
names = ["x%s"%i for i in range(ndim)]
labels =  ["x_%s"%i for i in range(ndim)]
samples = MCSamples(samples=samps,names = names, labels = labels)
samples2 = MCSamples(samples=samps2,names = names, labels = labels, label='Second set')
```


```python
# Triangle plot
g = plots.get_subplot_plotter()
g.triangle_plot([samples, samples2], filled=True)
```


```python
# Here we are using inline plots, but if you wanted to export to file you'd just do e.g.
# g.export('output_file.pdf')
```


```python
# 1D marginalized plot
g = plots.get_single_plotter(width_inch=4)
g.plot_1d(samples, 'x2')

```


```python
# 1D marginalized comparison plot
g = plots.get_single_plotter(width_inch=3)
g.plot_1d([samples, samples2], 'x1')
```


```python
# 1D normalized comparison plot
g = plots.get_single_plotter(width_inch=4)
g.plot_1d([samples, samples2], 'x1', normalized=True)
```


```python
# 2D line contour comparison plot with extra bands and markers
g = plots.get_single_plotter()
g.plot_2d([samples, samples2], 'x1', 'x2')
g.add_x_marker(0)
g.add_y_bands(0, 1)
```


```python
# Filled 2D comparison plot with legend
g = plots.get_single_plotter(width_inch=4, ratio=1)
g.plot_2d([samples, samples2], 'x1', 'x2', filled=True)
g.add_legend(['sim 1', 'sim 2'], colored_text=True);
```


```python
# Shaded 2D comparison plot
g = plots.get_single_plotter(width_inch=4)
g.plot_2d([samples, samples2], 'x1', 'x2', shaded=True);
```


```python
# Customized 2D filled comparison plot
g = plots.get_single_plotter(width_inch=6, ratio=3 / 5.)
g.settings.legend_fontsize = 12
g.plot_2d([samples, samples2], 'x1', 'x2', filled=True, 
    colors=['green', ('#F7BAA6', '#E03424')], lims=[-4, 7, -5, 5])
g.add_legend(['Sim ', 'Sim 2'], legend_loc='upper right');
```


```python
# Change the contours levels for marge stats and plots
# (note you need a lot of samples for 99% confidence contours to be accurate)
g = plots.get_single_plotter()
samples.updateSettings({'contours': [0.68, 0.95, 0.99]})
g.settings.num_plot_contours = 3
g.plot_2d(samples, 'x1', 'x2');
```


```python
# 2D scatter (3D) plot
g = plots.get_single_plotter(width_inch=5)
g.plot_3d(samples, ['x1', 'x2', 'x3'])
```


```python
# Multiple 1D subplots
g = plots.get_subplot_plotter(width_inch=5)
g.plots_1d(samples, ['x0', 'x1', 'x2', 'x3'], nx=2);
```


```python
# Multiple 2D subplots
g = plots.get_subplot_plotter(subplot_size=2.5)
g.settings.scaling = False # prevent scaling down font sizes even though small subplots
g.plots_2d(samples, param_pairs=[['x0', 'x1'], ['x2', 'x3']], 
           nx=2, filled=True);
```


```python
# Customized triangle plot
g = plots.get_subplot_plotter()
g.settings.figure_legend_frame = False
g.settings.alpha_filled_add=0.4
g.settings.title_limit_fontsize = 14
g.triangle_plot([samples, samples2], ['x0', 'x1', 'x2'], 
    filled=True, 
    legend_labels=['Simulation', 'Simulation 2'], 
    legend_loc='upper right', 
    line_args=[{'ls':'--', 'color':'green'},
               {'lw':2, 'color':'darkblue'}], 
    contour_colors=['green','darkblue'],
    title_limit=1, # first title limit (for 1D plots) is 68% by default
    markers={'x2':0}, marker_args={'lw': 1})
```

---
If you prefer to use one of the standard color series you can do that, using the matplotlib [named colormaps](https://matplotlib.org/examples/color/colormaps_reference.html) 



```python
# tab10 is the standard discrete color table (good for color blindness etc.)
g = plots.get_subplot_plotter(subplot_size=2)

# Set line style default
g.settings.line_styles = 'tab10'
g.plots_1d([samples, samples2], ['x1','x2', 'x3'], nx=3, legend_ncol=2, lws=[3,2])

# or set explicitly
g.plots_1d([samples, samples2], ['x1','x2', 'x3'], nx=3, legend_ncol=2,colors='Set1', ls=['-','--'])

# For filled contours set solid_colors setting (or set contour_colors argument as above)
g.settings.solid_colors='tab10'
g.triangle_plot([samples, samples2],  ['x1','x2'], filled=True, contour_lws=2) 
```


```python
# 3D (scatter) triangle plot
g = plots.get_subplot_plotter(width_inch=6)
# you can adjust the scaling factor if font sizes are too small when
# making many subplots in a fixed size (default=2 would give smaller fonts)
g.settings.scaling_factor = 1
g.triangle_plot([samples, samples2], ['x1', 'x2', 'x3'], 
                plot_3d_with_param='x0', legend_labels=['Simulation', 'Simulation 2'])
```


```python
# You can reference g.subplots for manual tweaking, 
# e.g. let's add a vertical axis line in the first column 
# (this can also be done directly via the markers argument to triangle_plot)
for ax in g.subplots[:,0]:
    ax.axvline(0, color='gray', ls='--')
IPython.display.display(g.fig)
```


```python
# Rectangle 2D comparison plots
g = plots.get_subplot_plotter()
g.settings.figure_legend_frame = False
g.rectangle_plot(['x0', 'x1'], ['x2', 'x3'], 
    roots=[samples, samples2], filled=True, 
    plot_texts=[['Test Label', None], ['Test 2', None]]);
```


```python
# Or join rows of 1D or 2D plots. 
from matplotlib import cm
g.settings.linewidth=2
g.plots_1d([samples,samples2], share_y=True, nx=2, legend_ncol=2, colors=cm.tab10)

g.rectangle_plot(['x1','x2','x3'],'x0', roots=[samples,samples2], colors=['k','C2']);
```


```python
# Example of how to handle boundaries (samples are restricted to x0 >-0.5)
cut_samps = samps[samps[:,0]>-0.5,:]
cut_samples = MCSamples(samples=cut_samps, names = names, labels = labels, 
                        ranges={'x0':(-0.5, None)}, label='Cut samples')
g = plots.get_subplot_plotter(subplot_size=2)
g.settings.title_limit_fontsize = 14 # reference size for 3.5 inch subplot
g.plots_1d(cut_samples,nx=4, title_limit=2) # title by 95% limit
g = plots.get_single_plotter(width_inch=4, ratio=1)
g.plot_2d(cut_samples, 'x0', 'x1', filled=True);
```


```python
# Add and plot a new derived parameter
# getParms gets p so that p.x0, p.x1.. are numpy vectors of sample values
# For individual parameters you can also just do samples['x0'] etc.
p = samples.getParams() 
assert np.all(p.x1 == samples['x1'])
samples.addDerived((5+p.x2)** 2, name='z', label='z_d')
g = plots.get_subplot_plotter(subplot_size=4)
g.plots_2d(samples,'x1',['x2','z'], nx=2);
```


```python
# Example of how to do importance sampling, modifying the samples by re-weighting by a new likelihood
# e.g. to modify samples to be from the original distribution times a Gaussian in x1 
# (centered on 1, with sigma=1.2)
# Using samples['x'] retrieves the vector of sample values for the parameter named 'x'
new_samples = samples.copy() # make a copy so don't change the original
new_loglike = (samples['x1']-1)**2/1.2**2/2
# code currently assumes existing loglikes are set, set to zero here
new_samples.loglikes = np.zeros(samples.numrows) 
# re-weight to account for the new likelihood
new_samples.reweightAddingLogLikes(new_loglike) 
g = plots.get_single_plotter(width_inch=4, ratio=1)
g.plot_2d([samples,new_samples], 'x0', 'x1', filled=True);
```


```python
# You can also account for general 2D prior boundary cuts that are not aligned with the axes
# (Note that the auto-smoothing kernel size does not account for non-trivial mask
# so may want to manually adjust the kernel smoothing width [smooth_scale_2D])

# e.g. consider cut that is linear function of two parameters with these parameters
y0 = -0.7; x0= -0.2; r = 0.3

def mask_function(minx, miny,  stepx, stepy, mask):
   # define function to tell getdist which 2D points are excluded by the prior
   # Note this should not include min, max parameter range cuts aligned with axes, which are handled as above.
    
    x = np.arange(mask.shape[1]) * stepx + minx
    y = np.arange(mask.shape[0]) * stepy + miny    
    # Create 2D coordinate grids
    X, Y = np.meshgrid(x, y)   
    # Zero out the array where prior excluded
    mask[Y < y0-r*(X-x0)  ] = 0   

cut_samps = samples.copy()
p = cut_samps.getParams()
cut_samps.filter(p.x1-y0+ (p.x0-x0)*r>0) # make test samples with hard prior cut

g=plots.get_single_plotter(width_inch=4, ratio=0.9)
# mass in the mask function so getdist knows about the prior cut
g.plot_2d(cut_samps, 'x0','x1', filled=True, mask_function=mask_function)
g.add_2d_contours(cut_samps, 'x0','x1', filled=False, color='g', ls='--')
x=np.linspace(-5, 5, 100)
plt.plot(x,y0-r*(x-x0), color='k',ls='--')
g.add_legend(['prior mask corrected','uncorrected']);
g.export('z:\\boundaries2D.pdf')
```


```python
# Many other things you can do besides plot, e.g. get latex
# Default limits are 1: 68%, 2: 95%, 3: 99% probability enclosed
# See  https://getdist.readthedocs.io/en/latest/analysis_settings.html
# and examples for below for changing analysis settings 
# (e.g. 2hidh limits, and how they are defined)
print(cut_samples.getInlineLatex('x0',limit=2))
print(samples.getInlineLatex('x0',limit=2))
```


```python
print(samples.getInlineLatex('x1',limit=1))
```


```python
print(samples.getTable().tableTex())
```


```python
# results from multiple chains
from getdist.types import ResultTable
print(ResultTable(ncol=1,results=[samples,new_samples],
                 paramList=['x0','x3'], limit=1, titles=['Samples','Weighted samples']).tableTex())
```


```python
print(samples.PCA(['x1','x2']))
```


```python
stats = cut_samples.getMargeStats()
lims0 = stats.parWithName('x0').limits
lims1 = stats.parWithName('x1').limits
for conf, lim0, lim1 in zip(samples.contours,lims0, lims1):
    print('x0 %s%% lower: %.3f upper: %.3f (%s)'%(conf, lim0.lower, lim0.upper, lim0.limitType()))
    print('x1 %s%% lower: %.3f upper: %.3f (%s)'%(conf, lim1.lower, lim1.upper, lim1.limitType()))
       
```


```python
# if samples have likelihood values, can also get best fit sample and extremal values of N-D confidence region
# Note in high dimensions best-fit sample is likely a long way from the best fit; N-D limits also often MC-noisy
print(new_samples.getLikeStats())
print('x0 95% n-D confidence extrema:', new_samples.paramNames.parWithName('x0').ND_limit_bot[1],
                                       new_samples.paramNames.parWithName('x0').ND_limit_top[1])
```


```python
# Save to file
import tempfile, os
tempdir = os.path.join(tempfile.gettempdir(),'testchaindir')
if not os.path.exists(tempdir): 
    os.makedirs(tempdir)
rootname = os.path.join(tempdir, 'testchain')
samples.saveAsText(rootname)
```


```python
# Load from file
from getdist import loadMCSamples
readsamps = loadMCSamples(rootname)
```


```python
# Make plots from chain files, loading automatically as needed by using root file name
g = plots.get_single_plotter(chain_dir=tempdir, width_inch=4)
g.plot_2d('testchain','x1', 'x2', shaded=True);
```


```python
# Custom settings for all loaded chains can be set as follows;
# for example to use custom contours and remove the first 20% of each chain as burn in
g = plots.get_single_plotter(chain_dir=tempdir, 
            analysis_settings={'ignore_rows': 0.2, 'contours':[0.2, 0.4, 0.6, 0.8]});
g.settings.num_plot_contours = 4
g.plot_2d('testchain', 'x1', 'x2', filled=False);

```


```python
# Silence messages about load
getdist.chains.print_load_details = False
```


```python
# Chains can be loaded by searching in multiple directories by giving a list as chain_dir
# (note chain names must be unique)

# make second test chain in new temp dir
temp2 = os.path.join(tempdir,'chaindir2')
cut_samples.saveAsText(os.path.join(temp2, 'testchain2'), make_dirs=True)
# Plot from chain files
g = plots.get_single_plotter(chain_dir=[tempdir, temp2])
g.plot_2d(['testchain','testchain2'], 'x1', 'x2', filled=True);
```


```python
# You can also load a samples object from the chain directories for further manipulation
read_samples = g.samples_for_root('testchain')
# e.g. add a new derived parameter
# Note our new variable is >0 by definition, so also need to define its finite range to 
# get correct densities near zero
p=read_samples.getParams()
read_samples.addDerived(np.abs(p.x1), name='modx1', label='|x_1|', range=[0,None])
g.new_plot()
g.plot_2d(read_samples, 'modx1', 'x2', filled=True);
```


```python
# cleanup test files
import shutil
shutil.rmtree(tempdir)
```


```python
# The plotting scripts also let you plot Gaussian (or Gaussian mixture) contours 
# This is useful for plotting smooth theory results, e.g. Fisher forecasts.
from getdist.gaussian_mixtures import GaussianND
covariance = [[0.001**2, 0.0006*0.05, 0], [0.0006*0.05, 0.05**2, 0.2**2], [0, 0.2**2, 2**2]]
mean = [0.02, 1, -2] 
gauss=GaussianND(mean, covariance)
g = plots.get_subplot_plotter()
g.triangle_plot(gauss,filled=True)

```


```python
# You can also explicitly name parameters so Gaussian mixtures can be plotted 
#in combination with samples
from getdist.gaussian_mixtures import Mixture2D
cov1 = [[0.001**2, 0.0006*0.05], [0.0006*0.05, 0.05**2]]
cov2 = [[0.001**2, -0.0006*0.05], [-0.0006*0.05, 0.05**2]]
mean1 = [0.02, 0.2]
mean2 = [0.023, 0.09]
mixture=Mixture2D([mean1, mean2], [cov1, cov2], names=['zobs','t'], labels=[r'z_{\rm obs}', 't'], label='Model')

# Generate samples from the mixture as simple example
mix_samples = mixture.MCSamples(3000, label='Samples')

g = plots.get_subplot_plotter()
# compare the analytic mixture to the sample density
g.triangle_plot([mix_samples, mixture], filled=False)

```


```python
# For long tick labels GetDist will space them intelligently so they don't overlap. 
# You can also rotate tick labels
p=mix_samples.getParams()
mix_samples.addDerived(10*p.zobs-p.t/10, name='xt', label='x_t')

g = plots.get_subplot_plotter(subplot_size=3)
g.settings.axes_fontsize=12
g.settings.axis_tick_x_rotation=45
g.settings.axis_tick_y_rotation=90
g.settings.colorbar_tick_rotation=90
g.triangle_plot(mix_samples,['t','zobs'], plot_3d_with_param='xt' , filled=True)

```


```python
# Double triangle plot
g = plots.get_subplot_plotter()
g.triangle_plot([samples,new_samples], ['x0', 'x1', 'x2'], filled=True, 
                upper_roots = [samples2],
                upper_kwargs = {'contour_colors':['green']}, 
                legend_labels=['Samples','Reweighted samples','Second samples']);
```


```python
# Variants
g = plots.get_subplot_plotter()
from matplotlib import cm
upper_kwargs = {'contour_colors': cm.tab10.colors[4:], 'contour_ls': ['-', '--'], 
                'filled': [True, False], 'show_1d': [True, True], 'contour_lws':[1,2]}
g.settings.solid_contour_palefactor = 0.9
g.settings.alpha_filled_add = 0.6
g.triangle_plot([samples,new_samples], ['x0', 'x1', 'x2'], filled=True, 
                contour_colors=['C3','green'], markers={'x0':-0.5},
                upper_roots = [samples2, cut_samples],
                upper_kwargs = upper_kwargs, 
                upper_label_right=True,
                legend_labels=['Samples','Reweighted','Second', 'Cut']);
```


```python
# Sets of 3D plots
g = plots.get_subplot_plotter(width_inch=8)
g.plots_3d(mix_samples,[['xt', 't','zobs'],['t', 'zobs','xt']], nx=2);
# and this is how to manually add contours only to a specific plot
g.add_2d_contours(mixture, 't','zobs', ax = [0,1]);
```


```python
# 4D x-y-z-color scatter plots:
# Use ""%matplotlib notebook" to interactively rotate etc.

g = plots.get_single_plotter()
g.plot_4d([samples, samples2], ['x0', 'x1', 'x2', 'x3'],
          cmap='viridis', color_bar=False, azim=75,
          alpha=[0.3, 0.1],  shadow_color=False, compare_colors=['k'])
```


```python
# with projection onto axes, colorbar, custom limits, colors, etc.
g = plots.get_single_plotter()
g.plot_4d(samples, ['x0', 'x1', 'x2', 'x3'], cmap='jet',
          alpha=0.4, shadow_alpha=0.05, shadow_color=True,
          max_scatter_points=6000,
          lims={'x2': (-3, 3), 'x3': (-3, 3)},
          colorbar_args={'shrink': 0.6})
```


```python
# use animate=True and mp4_filename option to export an rotation animation
# this shows example output

from IPython.display import Video
Video("https://cdn.cosmologist.info/antony/sample_rotation.mp4", html_attributes='controls loop', width=600)

```

---
**Using styles to change settings for consistent plot scripts**

If you want to change several default settings, you can make a module containing a new 
plotter class, which defines its own settings and behaviour, and then use it as a style. 
A couple of sample styles are included: getdist.styles.tab10 and getdist.styles.planck.
Using the same style in each script will then give consistent outputs without changing settings
each time.


```python
# use the 'tab10' style, which uses default matplotlib colourmaps
from getdist.styles.tab10 import style_name
plots.set_active_style(style_name)

g = plots.get_subplot_plotter(width_inch=6)
g.triangle_plot([samples, samples2], ['x1', 'x2', 'x3'], 
                plot_3d_with_param='x0', legend_labels=['Simulation', 'Simulation 2'])

```


```python
# getdist.styles.planck is a more complicated case which also changes matplotlib style 
# (to use latex rendering and different fonts). It also turns of scaling by default so all
# fonts are fixed size.

from getdist.styles.planck import style_name
plots.set_active_style(style_name)

g = plots.get_subplot_plotter(width_inch=6)
g.triangle_plot([samples, samples2], ['x1', 'x2', 'x3'], 
                plot_3d_with_param='x0', legend_labels=['Simulation', 'Simulation 2'])
```


```python
# Back to default style
plots.set_active_style();
```

**Getting consistent sizes for publication**

By default, font and line sizes are scaled for small plots, which is often necessary if making
figures with many subplots in. Setting parameters like settings.fontsizes, settings.axes_labelsize are specified at a reference axis size (defaul 3.5 inches); for smaller plots they are reduced.
For publication you may wish to have constent font sizes between figures, and hence specify fixed sizes and use a fixed figure size.


```python
# width_inch=3.5 is often good for a one-column figure.
# If we make one figure or multiple subplots, by deafult font sizes will 
# be different for smaller axis sizes
g = plots.get_single_plotter(width_inch=6)
g.plot_2d([samples, cut_samples],['x1','x2'])
g.add_legend(['Label 1', 'Label 2'], legend_loc='lower right')
# finish_plot will call tight_layout to make sure everything is 
# actually within the requested figure size, so plots saved at consistent size

g = plots.get_single_plotter(width_inch=3.5)
g.plot_2d([samples, cut_samples],['x1','x2'])
g.add_legend(['Label 1', 'Label 2'], legend_loc='lower right')
g.add_text('Text label',0.1,0.9)

g = plots.get_subplot_plotter(width_inch=3.5)
g.triangle_plot([samples, cut_samples],['x1','x2','x3'], legend_labels=['Label1', 'Label2'])
g.add_text('A',0.2, 0.8, ax=g.subplots[1,0], color='blue')
# finish_plot is not needed for commands which generate sets of subplots
```


```python
# The scaling_factor determines how quickly fonts shrink (default 2).
# Using scaling_factor=1 will give somewhat larger font sizes after scaling
g = plots.get_subplot_plotter(width_inch=3.5)
g.settings.scaling_factor = 1.5
g.triangle_plot([samples, cut_samples],['x1','x2','x3'], legend_labels=['Label1', 'Label2'])
g.add_text('A',0.2, 0.8, ax=g.subplots[1,0], color='blue')
```


```python
# Scaling is entirely disabled by setting settings.scaling=False or 
# getting the plotter instance using scaling=False. 
# Here font sizes and line widths are all consistent:

g = plots.get_single_plotter(width_inch=3.5, scaling=False)
g.plot_2d([samples, cut_samples],['x1','x2'])
g.add_text('Text label',0.1,0.9)
g.add_legend(['Label 1', 'Label 2'], legend_loc='lower right')
plt.suptitle('Default font sizes are tick labels:\n %.2g, labels: %.2g, legend: %.2g, text: %.2g'%
      (g.settings.axes_fontsize,g.settings.axes_labelsize,
       g.settings.legend_fontsize, g.settings.fontsize), va='bottom');

g.triangle_plot([samples, cut_samples],['x1','x2','x3'], legend_labels=['Label1', 'Label2'])
g.add_text('A',0.2, 0.8, ax=g.subplots[1,0], color='blue')
```


```python
# You can also set default font settings to the values set in your rcParams
g = plots.get_subplot_plotter(width_inch=3.5, scaling=False, rc_sizes=True)
g.triangle_plot([samples, cut_samples],['x1','x2','x3'], legend_labels=['Label1', 'Label2'])
g.add_text('A', 0.2, 0.8, ax=('x1','x2'), color='blue')
plt.suptitle('rc font sizes are tick labels:\n %.2g, labels: %.2g, legend: %.2g, fontsize: %.2g'%
      (g.settings.axes_fontsize,g.settings.axes_labelsize,
       g.settings.legend_fontsize, g.settings.fontsize), va='bottom');

```

---
**Controlling analysis settings**

The default kernel density estimation setting usually give good results, but note that contours can seem quite smooth even if the residual sampling noise is quite large. You can change the [analysis settings](https://getdist.readthedocs.io/en/latest/analysis_settings.html) from the default to visually inspect the stability of the result.


```python
ndim = 4
nsamp = 400
A = random_state.random((ndim,ndim))
cov = np.dot(A, A.T)
samps = random_state.multivariate_normal([0]*ndim, cov, size=nsamp)
names = ["x%s"%i for i in range(ndim)]
labels =  ["x_%s"%i for i in range(ndim)]

# default settings attempt to minimize sampling noise and bias
s1 = MCSamples(samples=samps, names=names, labels=labels, label='Default')

# Use standard lowest-order kernel density estimates the contours get visually more noisy
# (and more biased). Kernel widths are determined automatically.
s2 = MCSamples(samples=samps, names=names, labels=labels, 
               label='Lowest-order (Parzen) kernel',
               settings={'mult_bias_correction_order':0})

# manually set the smoothing scale in units of the standard deviation
# Can also use copy() to generate a copy of samples with new settings 
s3 = s2.copy(label=r'Lowest-order with $0.3\sigma$ smoothing', 
             settings={'mult_bias_correction_order':0,'smooth_scale_2D':0.3, 'smooth_scale_1D':0.3})

g = plots.get_subplot_plotter()
g.triangle_plot([s1, s2, s3], filled=False)

# Note that for some flat distributions the location of 2D equal-enclosed-probability contours can 
# be very unstable, e.g. a flat bounded distribution 0<x<1, 0<y<1 any contours drawn based on random
# samples will be completely dependent on sampling noise.
```


```python
# You can also change the boundary correction settings
# Note it is important to set ranges for any parameters with known hard prior cuts.
# Note also there's no guarantee in particular random samples that higher-order is better
random_state = np.random.default_rng(2)
samps = random_state.standard_normal(size=15000) #lots because cutting
xcut=1
samps = samps[samps>xcut]
plt.figure(figsize=(6,4))
plt.hist(samps, bins=50)
plt.title('Sample Histogram')

for mult_order in [0,1]:

    # Incorrectly set samples without specifying the prior range
    no_range = MCSamples(samples=samps, names=['x'],
                         settings = {'mult_bias_correction_order':mult_order})

    # For parameters with hard priors you must specify the range, here p>xcut by definition
    with_range = MCSamples(samples=samps, names=['x'],
                           settings = {'mult_bias_correction_order':mult_order}, 
                           ranges={'x':[xcut,None]})

    snone=with_range.copy(settings={'boundary_correction_order':-1, 
                                    'mult_bias_correction_order':mult_order})
    s0=with_range.copy(settings={'boundary_correction_order':0, 
                                 'mult_bias_correction_order':mult_order})

    g = plots.get_single_plotter(width_inch=6)
    g.settings.norm_prob_label = '$P(x)$'
    g.plot_1d([no_range, snone, s0, with_range], 'x', normalized=True)

    #Plot true distribution (normalized to peak 1)
    x=np.arange(xcut,5,0.01)
    dist=np.exp(-x**2/2+xcut**2/2)
    dist/=np.sum(dist)*0.01
    g.get_axes().plot(x,dist, ls='--', color='magenta')
    g.add_x_marker(xcut, lw=1)
    plt.title('Kernel densities, %s multiplicative boundary correction'%(
                                      'with' if mult_order else 'without'))
    g.add_legend(legend_labels=['No range, bad auto-bandwidth','No boundary correction',
                                '0th order boundary correction', '1st order correction (default)',
                                'True sampled distribution'], legend_loc='upper right');
```

***
**Further Reading**

See the full [documentation](https://getdist.readthedocs.io/en/latest/index.html) for further details and examples
