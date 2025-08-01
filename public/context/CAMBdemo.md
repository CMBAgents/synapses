**CAMB Python example notebook**

Run it online yourself in [Binder](https://mybinder.org/v2/gh/cmbant/camb/master?filepath=docs%2FCAMBdemo.ipynb).


```python
%matplotlib inline
%config InlineBackend.figure_format = 'retina'
import sys, platform, os
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import camb
from camb import model, initialpower
print('Using CAMB %s installed at %s'%(camb.__version__,os.path.dirname(camb.__file__)))
# make sure the version and path is what you expect
```


```python
#Set up a new set of parameters for CAMB
#The defaults give one massive neutrino and helium set using BBN consistency
pars = camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, mnu=0.06, omk=0, tau=0.06,  
                       As=2e-9, ns=0.965, halofit_version='mead', lmax=3000)
```


```python
#calculate results for these parameters
results = camb.get_results(pars)
```


```python
#get dictionary of CAMB power spectra
powers =results.get_cmb_power_spectra(pars, CMB_unit='muK')
for name in powers: print(name)
```


```python
#plot the total lensed CMB power spectra versus unlensed, and fractional difference
totCL=powers['total']
unlensedCL=powers['unlensed_scalar']
print(totCL.shape)
#Python CL arrays are all zero based (starting at L=0), Note L=0,1 entries will be zero by default.
#The different CL are always in the order TT, EE, BB, TE (with BB=0 for unlensed scalar results).
ls = np.arange(totCL.shape[0])
fig, ax = plt.subplots(2,2, figsize = (12,12))
ax[0,0].plot(ls,totCL[:,0], color='k')
ax[0,0].plot(ls,unlensedCL[:,0], color='C2')
ax[0,0].set_title(r'$TT\, [\mu K^2]$')
ax[0,1].plot(ls[2:], 1-unlensedCL[2:,0]/totCL[2:,0]);
ax[0,1].set_title(r'Fractional TT lensing')
ax[1,0].plot(ls,totCL[:,1], color='k')
ax[1,0].plot(ls,unlensedCL[:,1], color='C2')
ax[1,0].set_title(r'$EE\, [\mu K^2]$')
ax[1,1].plot(ls,totCL[:,3], color='k')
ax[1,1].plot(ls,unlensedCL[:,3], color='C2')
ax[1,1].set_title(r'$TE\, [\mu K^2]$');
for ax in ax.reshape(-1): 
    ax.set_xlim([2,3000])
    ax.set_xlabel(r'$\ell$');
```


```python
# The lensing B modes are non-linear, so need to be calculated carefully if you want them accurate (even at low ell)
# Need both high lmax, non-linear lensing and high k 
# lens_potential_accuracy=1 turns on the latter, and can be increased to check precision

pars.set_for_lmax(2500, lens_potential_accuracy=1)
results = camb.get_results(pars)
lmax2500CL = results.get_lensed_scalar_cls(CMB_unit='muK')
ls = np.arange(lmax2500CL.shape[0])

pars.set_for_lmax(4000, lens_potential_accuracy=1)
results = camb.get_results(pars)
lmax4000CL = results.get_lensed_scalar_cls(CMB_unit='muK')

pars.set_for_lmax(4000, lens_potential_accuracy=2)
results = camb.get_results(pars)
accCL = results.get_lensed_scalar_cls(CMB_unit='muK')

pars.set_for_lmax(6000, lens_potential_accuracy=4)
results = camb.get_results(pars)
refCL = results.get_lensed_scalar_cls(CMB_unit='muK')

fig, ax = plt.subplots(1,2, figsize = (12,4))
ax[0].plot(ls,totCL[:len(ls),2], color='C0')
ax[0].plot(ls,lmax2500CL[:len(ls),2], color='C1')
ax[0].plot(ls,lmax4000CL[:len(ls),2], color='C2')
ax[0].plot(ls,accCL[:len(ls),2], color='C3')
ax[0].plot(ls,refCL[:len(ls),2], color='k')

ax[0].set_xlim([2,2500])
ax[0].set_xlabel(r'$\ell$',fontsize=13)
ax[0].set_ylabel(r'$\ell(\ell+1)C_\ell^{BB}/2\pi\,[\mu {\rm K}^2]$', fontsize=13)

ax[1].plot(ls[2:],totCL[2:len(ls),2]/refCL[2:len(ls),2]-1, color='C0')
ax[1].plot(ls[2:],lmax2500CL[2:len(ls),2]/refCL[2:len(ls),2]-1, color='C1')
ax[1].plot(ls[2:],lmax4000CL[2:len(ls),2]/refCL[2:len(ls),2]-1, color='C2')
ax[1].plot(ls[2:],accCL[2:len(ls),2]/refCL[2:len(ls),2]-1, color='C3')

ax[1].axhline(0,color='k')
ax[1].set_xlim([2,2500])
ax[1].set_xlabel(r'$\ell$',fontsize=13)
ax[1].set_ylabel('fractional error', fontsize=13);
ax[1].legend(['Default accuracy','lmax=2500, lens_potential_accuracy=1',
           'lmax=4000, lens_potential_accuracy=1','lmax=4000, lens_potential_accuracy=2']);

```


```python
#You can calculate spectra for different primordial power spectra without recalculating everything
#for example, let's plot the BB spectra as a function of r
pars.set_for_lmax(4000, lens_potential_accuracy=1)
pars.WantTensors = True
results = camb.get_transfer_functions(pars)
lmax=2000
rs = np.linspace(0,0.2,6)
for r in rs:
    inflation_params = initialpower.InitialPowerLaw()
    inflation_params.set_params(ns=0.96, r=r)
    results.power_spectra_from_transfer(inflation_params) #warning OK here, not changing scalars
    cl = results.get_total_cls(lmax, CMB_unit='muK')
    plt.loglog(np.arange(lmax+1),cl[:,2])
plt.xlim([2,lmax])
plt.legend(["$r = %s$"%r for r in  rs], loc='lower right');
plt.ylabel(r'$\ell(\ell+1)C_\ell^{BB}/ (2\pi \mu{\rm K}^2)$')
plt.xlabel(r'$\ell$');
```


```python
# Now get matter power spectra and sigma8 at redshift 0 and 0.8
# parameters can all be passed as a dict as above, or you can call 
# separate functions to set up the parameter object
pars =  camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, ns=0.965)
#Note non-linear corrections couples to smaller scales than you want
pars.set_matter_power(redshifts=[0., 0.8], kmax=2.0)

#Linear spectra
pars.NonLinear = model.NonLinear_none
results = camb.get_results(pars)
kh, z, pk = results.get_matter_power_spectrum(minkh=1e-4, maxkh=1, npoints = 200)
s8 = np.array(results.get_sigma8())

#Non-Linear spectra (Halofit)
pars.NonLinear = model.NonLinear_both
results.calc_power_spectra(pars)
kh_nonlin, z_nonlin, pk_nonlin = results.get_matter_power_spectrum(minkh=1e-4, maxkh=1, npoints = 200)

```


```python
print(results.get_sigma8())
```


```python
for i, (redshift, line) in enumerate(zip(z,['-','--'])):
    plt.loglog(kh, pk[i,:], color='k', ls = line)
    plt.loglog(kh_nonlin, pk_nonlin[i,:], color='r', ls = line)
plt.xlabel('k/h Mpc');
plt.legend(['linear','non-linear'], loc='lower left');
plt.title('Matter power at z=%s and z= %s'%tuple(z));
```


```python
# If you want to use sigma8 (redshift zero) as an input parameter, have to scale the input primordial amplitude As:

As = 2e-9 # fiducial amplitude guess to start with
pars =  camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, ns=0.965, As=As)
pars.set_matter_power(redshifts=[0.], kmax=2.0)
results = camb.get_results(pars)
s8_fid = results.get_sigma8_0()
# now set correct As using As \propto sigma8**2.
sigma8 = 0.81 # value we want
pars.InitPower.set_params(As=As*sigma8**2/s8_fid**2, ns=0.965)

# check result
results = camb.get_results(pars)
print(sigma8, results.get_sigma8_0()) 

```


```python
# Plot CMB lensing potential power for various values of w at fixed H0

pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122)
pars.InitPower.set_params(As=2e-9, ns=0.965)
pars.set_for_lmax(2000, lens_potential_accuracy=1)

ws = np.linspace(-1.5, -0.6, 5)
for w in ws:
    pars.set_dark_energy(w=w, wa=0, dark_energy_model='fluid') 
    results = camb.get_results(pars)
    cl = results.get_lens_potential_cls(lmax=2000)
    plt.loglog(np.arange(2001), cl[:,0])

plt.legend([f'$w = {w:.3f}$' for w in ws])
plt.ylabel('$[L(L+1)]^2C_L^{\phi\phi}/2\pi$')
plt.xlabel('$L$')
plt.xlim([2,2000]);

```


```python
# Same for varying w at fixed thetastar rather than fixed H0 
# When using thetastar you must instead call set_cosmology() *after* setting the dark energy parameters
# or use camb.set_params to set everything at once as in this example
ws = np.linspace(-1.5, -0.6, 5)
for w in ws:
    pars = camb.set_params(w=w, wa=0, dark_energy_model='fluid',
                           thetastar=0.0104, ombh2=0.022, omch2=0.12,As=2e-9, 
                           ns=0.96, lmax=2000, lens_potential_accuracy=2)
    results = camb.get_results(pars)
    cl = results.get_lens_potential_cls(lmax=2000)
    plt.loglog(np.arange(2001), cl[:,0])

plt.legend([f'$w = {w:.3f}$' for w in ws])
plt.ylabel('$[L(L+1)]^2C_L^{\phi\phi}/2\pi$')
plt.xlabel('$L$')
plt.xlim([2,2000]);

```

---
You can view the parameters (as used by fortran CAMB internals) by just printing the parameter object.
See the [docs](https://camb.readthedocs.io/en/latest/model.html) for parameter and structure descriptions


```python
# parameters can also be read from text .ini files, for example this sets up a best-fit 
# Planck 2018 LCDM cosmology (base_plikHM_TTTEEE_lowl_lowE_lensing). 
# [Use planck_2018_acc.ini if you need high-ell and/or accurate BB and CMB lensng spectra at beyond-Planck accuracy]
pars = camb.read_ini('https://raw.githubusercontent.com/cmbant/CAMB/master/inifiles/planck_2018.ini')
# for a local github installation you can just do 
# pars=camb.read_ini(os.path.join(camb_path,'inifiles','planck_2018.ini'))
# view parameter objects using print(), or use pickle or repr to save and restore
print(pars)
```


```python
#The dark energy model can be changed as in the previous example, or by assigning to pars.DarkEnergy.
# ** Note that if using thetastar as a parameter, you *must* set dark energy before calling set_cosmology
# or use the camb.set_params() function setting everything at once from a dict **

#e.g. use the PPF model
from camb.dark_energy import DarkEnergyPPF, DarkEnergyFluid
pars.DarkEnergy = DarkEnergyPPF(w=-1.2, wa=0.2)
print('w, wa model parameters:\n\n', pars.DarkEnergy)
results = camb.get_background(pars)

#or can also use a w(a) numerical function 
#(note this will slow things down; make your own dark energy class in fortran for best performance)
a = np.logspace(-5, 0, 1000)
w = -1.2 + 0.2 * (1 - a)
pars.DarkEnergy= DarkEnergyPPF()
pars.DarkEnergy.set_w_a_table(a, w)
print('Table-interpolated parameters (w and wa are set to estimated values at 0):\n\n' 
      ,pars.DarkEnergy)
results2 = camb.get_background(pars)

rho, _ = results.get_dark_energy_rho_w(a)
rho2, _ = results2.get_dark_energy_rho_w(a)
plt.plot(a, rho, color='k')
plt.plot(a, rho2, color='r', ls='--')
plt.ylabel(r'$\rho/\rho_0$')
plt.xlabel('$a$')
plt.xlim(0,1)
plt.title('Dark enery density');

```


```python
#Get various background functions and derived parameters
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122)
results = camb.get_background(pars)
print('Derived parameter dictionary: %s'%results.get_derived_params())
```


```python
z = np.linspace(0,4,100)
DA = results.angular_diameter_distance(z)
plt.plot(z, DA)
plt.xlabel('$z$')
plt.ylabel(r'$D_A /\rm{Mpc}$')
plt.title('Angular diameter distance')
plt.ylim([0,2000])
plt.xlim([0,4]);
```


```python
print('CosmoMC theta_MC parameter: %s'%results.cosmomc_theta())
```


```python
#You can also directly access some lower level quantities, for example the CMB transfer functions:
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122)
data = camb.get_transfer_functions(pars)
transfer = data.get_cmb_transfer_data()
print('Number of sources (T, E, phi..): %s; number of ell: %s; number of k: %s '%tuple(transfer.delta_p_l_k.shape))
```


```python
#Plot the transfer functions as a function of k for various ell
fig, axs = plt.subplots(2,2, figsize=(12,8), sharex = True)
for ix, ax in zip([3, 20, 40, 60],axs.reshape(-1)):
    ax.plot(transfer.q,transfer.delta_p_l_k[0,ix,:])
    ax.set_title(r'$\ell = %s$'%transfer.L[ix])
    if ix>1: ax.set_xlabel(r'$k \rm{Mpc}$')
```


```python
#Note that internal samplings can be quite sparsely sampled, e.g. look at l=2 transfer function
def plot_cmb_transfer_l(trans, ix):
    _, axs = plt.subplots(1,2, figsize=(12,6))
    for source_ix, (name, ax) in enumerate(zip(['T', 'E'], axs)):
        ax.semilogx(trans.q,trans.delta_p_l_k[source_ix,ix,:])
        ax.set_xlim([1e-5, 0.05])
        ax.set_xlabel(r'$k \rm{Mpc}$')
        ax.set_title(r'%s transfer function for $\ell = %s$'%(name, trans.L[ix]))
plot_cmb_transfer_l(transfer,0)
```


```python
#So if you want to make nice plots, either interpolate or do things at higher than default accuracy
pars.set_accuracy(AccuracyBoost=2) #higher accuracy, so higher sampling density
data = camb.get_transfer_functions(pars)
plot_cmb_transfer_l(data.get_cmb_transfer_data(),0)
pars.set_accuracy(AccuracyBoost=1); #re-set default
```


```python
#Similarly for tensor transfer function 
#e.g. see where various C_L^BB come from in k by plotting normalized transfer**2 (C_l is ~ integral over log k P(k) T(k)^2)
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122)
pars.WantScalars = False
pars.WantTensors = True
pars.set_accuracy(AccuracyBoost=2)
data = camb.get_transfer_functions(pars)
transfer = data.get_cmb_transfer_data('tensor')
print(r'Calculated L: %s'%transfer.L)
plt.figure(figsize=(14,3))
ixs=[13,19,21]
ls = [transfer.L[i] for i in ixs]
cols=['b','r','c']
for ix,col in zip(ixs, cols):
    k_weight = transfer.delta_p_l_k[2,ix,:]**2
    k_weight /= np.sum(k_weight)
    plt.semilogx(transfer.q,k_weight, color=col)
plt.xlim([1e-3, 0.1])
plt.legend(ls)
plt.xlabel(r'$k \rm{Mpc}$')
plt.title(r'Contribution to B from primordial tensor power spectrum for various $\ell$')
#compare with k_* = l/chi*, note DAstar is in GPc, so multiply by 1000 to get standard Mpc units used for k
derived = data.get_derived_params()
for l,col in zip(ls,cols):
    plt.axvline(l/(1000*derived['DAstar']), color=col, ls=':', lw=2)
```


```python
#if you want to combine the transfer functions with the primordial power spectra, you can get the latter via
k=10**np.linspace(-5, 1, 50)
pars.InitPower.set_params(ns=0.96, r=0.2) #this functions imposes inflation consistency relation by default
scalar_pk= pars.scalar_power(k)
tensor_pk= pars.tensor_power(k)
plt.semilogx(k,scalar_pk);
plt.semilogx(k,tensor_pk);
plt.xlabel(r'$k \rm{Mpc}$')
plt.ylabel(r'${\cal P}(k)$')
plt.legend(['scalar', 'tensor']);
```


```python
#set_params is a shortcut routine for setting many things at once
pars = camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, As=2e-9, ns=0.95)
data= camb.get_background(pars)
```


```python
#There are functions get plot evolution of variables, e.g. for the background as a function of conformal time:
# (there is an example changing the reionization history later)
eta = 10**(np.linspace(1, 4,300))
back_ev = data.get_background_time_evolution(eta, ['x_e', 'visibility'])
fig, axs= plt.subplots(1,2, figsize=(12,5))
axs[0].semilogx(eta, back_ev['x_e'])
axs[1].loglog(eta, back_ev['visibility'])
axs[0].set_xlabel(r'$\eta/\rm{Mpc}$')
axs[0].set_ylabel('$x_e$')
axs[1].set_xlabel(r'$\eta/\rm{Mpc}$')
axs[1].set_ylabel('Visibility');
fig.suptitle('Ionization history, including both hydrogen and helium recombination and reionization');
```


```python
#or as a function of redshift
z = 10**np.linspace(2, 4, 300)
back_ev = data.get_background_redshift_evolution(z, ['x_e', 'visibility'], format='array')
fig, axs= plt.subplots(1,2, figsize=(12,5))
for i, (ax, label), in enumerate(zip(axs, ['$x_e$','Visibility'])):
    ax.semilogx(z, back_ev[:,i])
    ax.set_xlabel('$z$')
    ax.set_ylabel(label)
    ax.set_xlim([500,1e4])
```


```python
# ..and perturbation transfer functions, e.g. for k=0.1. Note that quantities are synchronous gauge unless otherwise specified
# Also note v_newtonian_cdm, v_newtonian_baryon include a factor of -k/H, and Weyl a factor of k^2 -
# see https://camb.readthedocs.io/en/latest/transfer_variables.html
print('Available variables are %s'%camb.model.evolve_names)
```


```python
eta = np.linspace(1, 400, 300)
ks = [0.02,0.1]
ev = data.get_time_evolution(ks, eta, ['delta_baryon','delta_photon'])
_, axs= plt.subplots(1,2, figsize=(12,5))
for i, ax in enumerate(axs):
    ax.plot(eta,ev[i,:, 0])
    ax.plot(eta,ev[i,:, 1])
    ax.set_title('$k= %s$'%ks[i])
    ax.set_xlabel(r'$\eta/\rm{Mpc}$');
plt.legend([r'$\Delta_b$', r'$\Delta_\gamma$'], loc = 'upper left');

```


```python
#or as a function of redshift
z = np.linspace(500,5000,300)
ks = [0.02,0.1]
ev = data.get_redshift_evolution(ks, z, ['delta_baryon','delta_cdm', 'delta_photon'])
_, axs= plt.subplots(1,2, figsize=(12,5))
for i, ax in enumerate(axs):
    ax.plot(z,ev[i,:, 0])
    ax.plot(z,ev[i,:, 1])
    ax.plot(z,ev[i,:, 2])
    ax.set_title(r'$k= %s/\rm{Mpc}$'%ks[i])
    ax.set_xlabel('$z$');
plt.legend([r'$\Delta_b$', r'$\Delta_c$', r'$\Delta_\gamma$'], loc = 'upper right');
```


```python
#Here you can see oscillation of delta_photon, subsequent decay of the potential and change to Mezsaroz growth in delta_cdm
eta = 10**(np.linspace(0, 3, 500))
def plot_ev(ev, k):
    plt.figure(figsize=(8,6))
    plt.loglog(eta,ev[:,0])
    plt.loglog(eta,np.abs(ev[:,1]))
    plt.loglog(eta,-ev[:,2]/k**2)  # Weyl is k^2*phi
    plt.title(r'$k= %s/\rm{Mpc}$'%k)
    plt.xlabel(r'$\eta/\rm{Mpc}$');
    plt.legend([r'$\Delta_c$', r'$|\Delta_\gamma|$', r'$-(\Phi+\Psi)/2$'], loc = 'upper left');

k=0.3
plot_ev(data.get_time_evolution(k, eta, ['delta_cdm','delta_photon', 'Weyl']),k)

```


```python
#Note that time evolution can be visually quite sensitive to accuracy. By default it is boosted, but you can change this. e.g.
plot_ev(data.get_time_evolution(k, eta, ['delta_cdm','delta_photon', 'Weyl'],lAccuracyBoost=1),k)
plot_ev(data.get_time_evolution(k, eta, ['delta_cdm','delta_photon', 'Weyl'],lAccuracyBoost=10),k)
```


```python
#It's also possible to plot quantities in other gauges, or arbitrary symbolic expressions,
#using camb.symbolic.
#For example, this plots the Newtonian gauge density compared to the synchronous gauge one
import camb.symbolic as cs
Delta_c_N = cs.make_frame_invariant(cs.Delta_c, 'Newtonian')
ev=data.get_time_evolution(k, eta, ['delta_cdm',Delta_c_N])
plt.figure(figsize=(6,4))
plt.loglog(eta,ev[:,0])
plt.loglog(eta,ev[:,1])
plt.title(r'$k= %s/\rm{Mpc}$'%k)
plt.xlabel(r'$\eta/\rm{Mpc}$');
plt.legend([r'$\Delta_c^{\rm synchronous}$', r'$\Delta_c^{\rm Newtonian}$'], fontsize=14);
```


```python
# Or see that the Newtonian-gauge CDM peculiar velocity decays roughly propto 1/a on sub-horizon 
# scales during radiation domination after the potentials have decayed so there is no driving force
# (leading to logarithmic Meszaros growth of the CDM density perturbation)
k=4
vc_N = cs.make_frame_invariant(cs.v_c, 'Newtonian')
ev=data.get_time_evolution(k, eta, [Delta_c_N, vc_N, 'a'])
plt.figure(figsize=(6,4))
plt.loglog(eta,ev[:,0])
plt.loglog(eta,-ev[:,1])
eta_ln=6*np.sqrt(3)*np.pi/4/k
horizon_index =  np.searchsorted(eta, eta_ln, side='right')
plt.loglog(eta,-ev[horizon_index,1]*ev[horizon_index,2]/ev[:,2], ls='--')
plt.ylim([1e-4,5e2])
plt.title(r'$k= %s/\rm{Mpc}$'%k)
plt.xlabel(r'$\eta/\rm{Mpc}$');
plt.legend([r'$\Delta_c^{\rm Newtonian}$',r'$-v_c^{\rm Newtonian}$',r'$v_c^{\rm Newtonian}\propto 1/a$'], fontsize=14);
```

For further details of camb.symbolic and examples of what can be done see the [CAMB symbolic ScalEqs notebook](https://camb.readthedocs.io/en/latest/ScalEqs.html) (run now in [Binder](https://mybinder.org/v2/gh/cmbant/camb/master?filepath=docs%2FScalEqs.ipynb)). This also serves as documentation for the scalar equations implemented in CAMB.


```python
#For calculating large-scale structure and lensing results yourself, get a power spectrum
#interpolation object. In this example we calculate the CMB lensing potential power
#spectrum using the Limber approximation, using PK=camb.get_matter_power_interpolator() function.
#calling PK(z, k) will then get power spectrum at any k and redshift z in range.

nz = 100 #number of steps to use for the radial/redshift integration
kmax=10  #kmax to use
#First set up parameters as usual
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122)
pars.InitPower.set_params(ns=0.965)

#For Limber result, want integration over \chi (comoving radial distance), from 0 to chi_*.
#so get background results to find chistar, set up a range in chi, and calculate corresponding redshifts
results= camb.get_background(pars)
chistar = results.conformal_time(0)- results.tau_maxvis
chis = np.linspace(0,chistar,nz)
zs=results.redshift_at_comoving_radial_distance(chis)
#Calculate array of delta_chi, and drop first and last points where things go singular
dchis = (chis[2:]-chis[:-2])/2
chis = chis[1:-1]
zs = zs[1:-1]

#Get the matter power spectrum interpolation object (based on RectBivariateSpline). 
#Here for lensing we want the power spectrum of the Weyl potential.
PK = camb.get_matter_power_interpolator(pars, nonlinear=True, 
    hubble_units=False, k_hunit=False, kmax=kmax,
    var1=model.Transfer_Weyl,var2=model.Transfer_Weyl, zmax=zs[-1])

#Have a look at interpolated power spectrum results for a range of redshifts
#Expect linear potentials to decay a bit when Lambda becomes important, and change from non-linear growth
plt.figure(figsize=(8,5))
k=np.exp(np.log(10)*np.linspace(-4,2,200))
zplot = [0, 0.5, 1, 4 ,20]
for z in zplot:
    plt.loglog(k, PK.P(z,k))
plt.xlim([1e-4,kmax])
plt.xlabel(r'k Mpc')
plt.ylabel('$P_\Psi\, Mpc^{-3}$')
plt.legend(['z=%s'%z for z in zplot]);

```

Now do integral to get convergence power spectrum, using Limber approximation ($k\approx (l+0.5)/\chi$)
$$
C_l^\kappa \approx  [l(l+1)]^2\int_0^{\chi_*} d\chi \left( \frac{\chi_*-\chi}{\chi^2\chi_*}\right)^2 P_\Psi\left(\frac{l+0.5}{\chi}, z(\chi)\right)
$$
where $P_\Psi $ is obtained from the interpolator.


```python
#Get lensing window function (flat universe)
win = ((chistar-chis)/(chis**2*chistar))**2
#Do integral over chi
ls = np.arange(2,2500+1, dtype=np.float64)
cl_kappa=np.zeros(ls.shape)
w = np.ones(chis.shape) #this is just used to set to zero k values out of range of interpolation
for i, l in enumerate(ls):
    k=(l+0.5)/chis
    w[:]=1
    w[k<1e-4]=0
    w[k>=kmax]=0
    cl_kappa[i] = np.dot(dchis, w*PK.P(zs, k, grid=False)*win/k**4)
cl_kappa*= (ls*(ls+1))**2
```


```python
#Compare with CAMB's calculation:
#note that to get CAMB's internal calculation accurate at the 1% level at L~2000, 
#need lens_potential_accuracy=2. Increase to 4 for accurate match to the Limber calculation here
pars.set_for_lmax(2500,lens_potential_accuracy=2)
results = camb.get_results(pars)
cl_camb=results.get_lens_potential_cls(2500) 
#cl_camb[:,0] is phi x phi power spectrum (other columns are phi x T and phi x E)

#Make plot. Expect difference at very low-L from inaccuracy in Limber approximation, and
#very high L from differences in kmax (lens_potential_accuracy is only 2, though good by eye here)
cl_limber= 4*cl_kappa/2/np.pi #convert kappa power to [l(l+1)]^2C_phi/2pi (what cl_camb is)
plt.loglog(ls,cl_limber, color='b')
plt.loglog(np.arange(2,cl_camb[:,0].size),cl_camb[2:,0], color='r')
plt.xlim([1,2000])
plt.legend(['Limber','CAMB hybrid'])
plt.ylabel('$[L(L+1)]^2C_L^{\phi}/2\pi$')
plt.xlabel('$L$');

```


```python
#The non-linear model can be changed like this:
pars.set_matter_power(redshifts=[0.], kmax=2.0)
pars.NonLinearModel.set_params(halofit_version='takahashi')
kh_nonlin, _, pk_takahashi = results.get_nonlinear_matter_power_spectrum(params=pars)
pars.NonLinearModel.set_params(halofit_version='mead')
kh_nonlin, _, pk_mead = results.get_nonlinear_matter_power_spectrum(params=pars)

fig, axs=plt.subplots(2,1, sharex=True, figsize=(8,8))
axs[0].loglog(kh_nonlin, pk_takahashi[0])
axs[0].loglog(kh_nonlin, pk_mead[0])
axs[1].semilogx(kh_nonlin, pk_mead[0]/pk_takahashi[0]-1)
axs[1].set_xlabel(r'$k/h\, \rm{Mpc}$')    
axs[1].legend(['Mead/Takahashi-1'], loc='upper left');
```


```python
#Get angular power spectrum for galaxy number counts and lensing
from camb.sources import GaussianSourceWindow, SplinedSourceWindow

pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122)
pars.InitPower.set_params(As=2e-9, ns=0.965)
pars.set_for_lmax(lmax, lens_potential_accuracy=1)
#set Want_CMB to true if you also want CMB spectra or correlations
pars.Want_CMB = False 
#NonLinear_both or NonLinear_lens will use non-linear corrections
pars.NonLinear = model.NonLinear_both
#Set up W(z) window functions, later labelled W1, W2. Gaussian here.
pars.SourceWindows = [
    GaussianSourceWindow(redshift=0.17, source_type='counts', bias=1.2, sigma=0.04, dlog10Ndm=-0.2),
    GaussianSourceWindow(redshift=0.5, source_type='lensing', sigma=0.07)]

results = camb.get_results(pars)
cls = results.get_source_cls_dict()

#Note that P is CMB lensing, as a deflection angle power (i.e. PxP is [l(l+1)]^2C_l\phi\phi/2\pi)
#lensing window functions are for kappa (and counts for the fractional angular number density)
ls=  np.arange(2, lmax+1)
for spectrum in ['W1xW1','W2xW2','W1xW2',"PxW1", "PxW2"]:
    plt.loglog(ls, cls[spectrum][2:lmax+1], label=spectrum)
plt.xlabel(r'$\ell$')
plt.ylabel(r'$\ell(\ell+1)C_\ell/2\pi$')
plt.legend();

```


```python
#You can also use window functions from numerical table of W(z). It must be well enough sampled to interpolate nicely.
#e.g. reproduce Gaussian this way..
zs = np.arange(0, 0.5, 0.02)
W = np.exp(-(zs - 0.17) ** 2 / 2 / 0.04 ** 2) / np.sqrt(2 * np.pi) / 0.04
pars.SourceWindows = [SplinedSourceWindow(bias=1.2, dlog10Ndm=-0.2, z=zs, W=W)]
results = camb.get_results(pars)
cls2 = results.get_cmb_unlensed_scalar_array_dict()
plt.loglog(ls, cls["W1xW1"][2:lmax+1], label=spectrum)
plt.loglog(ls, cls2["W1xW1"][2:lmax+1],ls='--')
plt.xlabel(r'$\ell$')
plt.ylabel(r'$\ell(\ell+1)C_\ell/2\pi$');

```


```python
#Sources can include various terms using these options (line_xx refers to 21cm)
print(pars.SourceTerms)
```


```python
#Results above include redshift distortions but not magnification bias (counts_lensing). 
#Try turning off redshift distortions:
pars.SourceTerms.counts_redshift = False
results = camb.get_results(pars)
cls3 = results.get_source_cls_dict()

plt.loglog(ls, cls["W1xW1"][2:lmax+1])
plt.loglog(ls, cls3["W1xW1"][2:lmax+1])
plt.legend(['With redshift distortions', 'Without'])
plt.xlabel(r'$\ell$')
plt.ylabel(r'$\ell(\ell+1)C_\ell/2\pi$')
plt.xlim(2,lmax);
```


```python
# For number counts you can give a redshift-dependent bias (the underlying code supports general b(z,k))
# toy model for single-bin LSST/Vera Rubin [using numbers from 1705.02332]
z0=0.311
zs = np.arange(0, 10, 0.02)
W = np.exp(-zs/z0)*(zs/z0)**2/2/z0
bias = 1 + 0.84*zs
pars.SourceWindows = [SplinedSourceWindow(dlog10Ndm=0, z=zs, W=W, bias_z = bias)]
lmax=3000
pars.set_for_lmax(lmax, lens_potential_accuracy=5)
results = camb.get_results(pars)

#e.g. plot the cross-correlation with CMB lensing
cls = results.get_cmb_unlensed_scalar_array_dict()

nbar = 40/(np.pi/180/60)**2 # Poission noise
ls= np.arange(2,lmax+1)
Dnoise = 1/nbar*ls*(ls+1)/2/np.pi

correlation=cls["PxW1"][2:lmax+1]/np.sqrt(cls["PxP"][2:lmax+1]*(cls["W1xW1"][2:lmax+1]+Dnoise))
plt.plot(np.arange(2,lmax+1), correlation)
plt.xlabel(r'$L$')
plt.ylabel('correlation')
plt.xlim(2,lmax)
plt.title('CMB lensing - LSST correlation (single redshift bin)');
```


```python
#Let's look at some non-standard primordial power spectrum, e.g. with wavepacket oscillation

#Define our custom  power spectrum function (here power law with one wavepacket)
def PK(k, As, ns, amp, freq, wid, centre, phase):
    return As*(k/0.05)**(ns-1)*(1+ np.sin(phase+k*freq)*amp*np.exp(-(k-centre)**2/wid**2))

#Check how this looks compared to power law
ks = np.linspace(0.02,1,1000)
pk1 = 2e-9*(ks/0.05)**(0.96-1)
pk2 = PK(ks,2e-9, 0.96,0.0599, 280, 0.08, 0.2,0)
plt.semilogx(ks,pk1)
plt.semilogx(ks,pk2)
plt.ylabel('$P(k)$')
plt.xlabel(r'$k\, {\rm Mpc}$')
plt.legend(['Power law','Custom'])
plt.title('Scalar initial power spectrum');
```


```python
#Now compute C_l and compare
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122, tau=0.06)
lmax=2500
pars.set_for_lmax(lmax,lens_potential_accuracy=1)

#For comparison, standard power law
pars.InitPower.set_params(As=2e-9, ns=0.96)
results = camb.get_results(pars)
cl_unlensed=results.get_unlensed_scalar_cls(CMB_unit ='muK')
cl=results.get_lensed_scalar_cls(CMB_unit ='muK')

#Now get custom spectrum (effective_ns_for_nonlinear is used for halofit if required)
pars.set_initial_power_function(PK, args=(2e-9, 0.96,0.0599, 280, 0.08, 0.2,0), 
                                effective_ns_for_nonlinear=0.96)

results2 = camb.get_results(pars)
cl2=results2.get_lensed_scalar_cls(CMB_unit ='muK')

ls = np.arange(2,lmax)
plt.plot(ls,(cl2[2:lmax,0]-cl[2:lmax,0]))
plt.xlabel(r'$\ell$');
plt.ylabel(r'$\ell(\ell+1)\Delta C_\ell/2\pi\, [\mu K^2]$')
plt.title(r'$C_\ell$ difference to power law');

```


```python
#Note that if you have sharp features or fine oscillations, you may need 
#increase accuracy to sample them well. e.g. let's try increasing the frequency

#Default accuracy
pars.Accuracy.lSampleBoost = 1
pars.Accuracy.IntkAccuracyBoost =1
pars.Accuracy.SourcekAccuracyBoost =1

freq = 1000
ks = np.linspace(0.02,1,1000)
pk1 = 2e-9*(ks/0.05)**(0.96-1)
pk2 = PK(ks,2e-9, 0.96,0.0599,freq, 0.08, 0.2,0)
plt.semilogx(ks,pk1)
plt.semilogx(ks,pk2)
plt.ylabel('$P(k)$')
plt.xlabel(r'$k\, {\rm Mpc}$');
plt.title('Scalar power spectrum')
plt.figure()

pars.set_initial_power_function(PK, args=(2e-9, 0.96,0.0599, freq, 0.08, 0.2,0),
                               effective_ns_for_nonlinear=0.96)

results2 = camb.get_results(pars)
cl_unlensed2=results2.get_unlensed_scalar_cls(CMB_unit ='muK')

#need to increase default sampling in ell to see features smaller than peaks reliably
pars.Accuracy.lSampleBoost = 2
#may also need to sample k more densely when computing C_l from P(k)
pars.Accuracy.IntkAccuracyBoost = 2 

results3 = camb.get_results(pars)
cl_unlensed3=results3.get_unlensed_scalar_cls(CMB_unit ='muK')
cl3=results3.get_lensed_scalar_cls(CMB_unit ='muK')

ls = np.arange(2,lmax)
plt.plot(ls,(cl_unlensed2[2:lmax,0]/cl_unlensed[2:lmax,0]-1))
plt.plot(ls,(cl_unlensed3[2:lmax,0]/cl_unlensed[2:lmax,0]-1))

plt.xlabel(r'$\ell$')
plt.ylabel(r'$\Delta C_\ell/C_\ell$')
plt.title(r'Fractional $C_\ell$ difference to power law')
plt.legend(['Default accuracy','Boosted accuracy']);

```


```python
#Note that lensing washes out small features on small scales
plt.plot(ls,(cl_unlensed3[2:lmax,0]/cl_unlensed[2:lmax,0]-1))
plt.plot(ls,(cl3[2:lmax,0]/cl[2:lmax,0]-1))
plt.xlabel(r'$\ell$')
plt.ylabel(r'$\Delta C_\ell/C_\ell$')
plt.legend(['Unlensed','Lensed'])
plt.title(r'Fractional $C_\ell$ difference to power law');
```


```python
#Now look at the (small!) effect of neutrino mass splittings on the matter power spectrum (in linear theory)
#The "neutrino_hierarchy" parameter uses a two eigenstate approximation to the full hierarchy (which is very accurate for cosmology)
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122, mnu=0.11, neutrino_hierarchy='normal')
pars.InitPower.set_params(ns=0.965)
pars.set_matter_power(redshifts=[0.], kmax=2.0)
results = camb.get_results(pars)
kh, z, pk = results.get_matter_power_spectrum(minkh=1e-4, maxkh=2, npoints = 200)

pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122, mnu=0.11, neutrino_hierarchy='inverted')
results = camb.get_results(pars)
kh2, z2, pk2 = results.get_matter_power_spectrum(minkh=1e-4, maxkh=2, npoints = 200)

plt.semilogx(kh, pk2[0,:]/pk[0,:]-1)
plt.ylabel('$\Delta$ PK/PK')
plt.xlabel(r'$k\, [h \,\rm{Mpc}^{-1}]$')
plt.title(r'Normal vs Inverted for $\sum m_\nu=0.11 \rm{eV}$');
```


```python
#Matter power functions can get other variables than the total density.
#For example look at the relative baryon-CDM velocity by using the power spectrum of
#model.Transfer_vel_baryon_cdm

kmax=10 
k_per_logint = 30
zs = [200, 500,800, 1090]

pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122)
pars.InitPower.set_params(ns=0.965)
pars.WantTransfer = True
pars.set_matter_power(redshifts=zs, kmax=kmax, k_per_logint=k_per_logint, silent=True)
results = camb.get_results(pars)

PKint = results.get_matter_power_interpolator(nonlinear=False, 
    hubble_units=False, k_hunit=False, 
    var1=model.Transfer_vel_baryon_cdm, var2=model.Transfer_vel_baryon_cdm)
```


```python
#Make plot like Fig 1 of https://arxiv.org/abs/1005.2416
#showing contribution to the CDM-baryon relative velocity variance per log k

plt.figure(figsize=(8,5))
ks = np.logspace(-3, np.log10(kmax), 300)
for i, z in enumerate(zs):
     curlyP = PKint.P(z,ks)*ks**3/(2*np.pi**2)
     plt.semilogx(ks, curlyP)
     rms = np.sqrt(curlyP[1:-1].dot((ks[2:]-ks[:-2])/2/ks[1:-1]))
     print('rms velocity at z=%s: %.3g'%(z,rms), '(%.3g km/s)'%(rms*299792))
    
plt.xlim([1e-3,kmax])
plt.xlabel('k Mpc', fontsize=16)
plt.ylabel(r'$\mathcal{P}_v(k)$', fontsize=16)
plt.legend(['$z = %s$'%z for z in zs]);
```


```python
#You can also get the matter transfer functions
#These are synchronous gauge and normalized to unit primordial curvature perturbation
#The values stored in the array are quantities like Delta_x/k^2, and hence
#are nearly independent of k on large scales. 
#Indices in the transfer_data array are the variable type, the k index, and the redshift index

pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122)
pars.InitPower.set_params(ns=0.965)
pars.set_matter_power(redshifts=[0], kmax=kmax)
results= camb.get_results(pars)

trans = results.get_matter_transfer_data()
#get kh - the values of k/h at which they are calculated
kh = trans.transfer_data[0,:,0]
#transfer functions for different variables, e.g. CDM density and the Weyl potential
#CDM perturbations have grown, Weyl is O(1) of primordial value on large scales
delta = trans.transfer_data[model.Transfer_cdm-1,:,0]
W = trans.transfer_data[model.Transfer_Weyl-1,:,0]
plt.plot(kh,delta)
plt.loglog(kh,-W)
plt.xlabel(r'$k/h\, [\rm Mpc]^{-1}$', fontsize=16);
plt.title('Matter transfer functions')
plt.legend([r'$\Delta_c/k^2$',r'Weyl potential $\Psi$'], fontsize=14);
```


```python
#Check we can get the matter power spectrum from the transfer function as expected
k = kh*results.Params.h
transfer = trans.transfer_data[model.Transfer_tot-1,:,0]
primordial_PK = results.Params.scalar_power(k)
matter_power = primordial_PK*transfer**2*k**4 / (k**3/(2*np.pi**2))

#compare with CAMB's explicit output for the matter power spectrum
kh2,zs,PK = results.get_linear_matter_power_spectrum(hubble_units=False)

plt.loglog(kh,matter_power)
plt.loglog(kh, PK[0,:]);
plt.xlabel(r'$k\, [h Mpc^{-1}]$');
```


```python
# It is also possible to get the real-space linear perturbation variance in spheres, i.e. \sigma_R.
# Using R=8 and hubble_units=T would return the standard definition of \sigma_8
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122)
pars.InitPower.set_params(ns=0.965)
pars.set_matter_power(redshifts=[0,1], kmax=kmax)
results= camb.get_results(pars)
R, z, sigma_R = results.get_sigmaR(R=np.arange(1,20,0.5), 
                                 hubble_units=False, return_R_z=True)
plt.plot(R, sigma_R[1,:], label='z = %s'%z[1])
plt.plot(R, sigma_R[0,:], label='z = %s'%z[0])
plt.ylabel(r'$\sigma_R$', fontsize=14)
plt.xlabel(r'$R/{\rm Mpc}$', fontsize=14)
plt.legend()
# To get the non-linear scale where sigma_R=1, e.g. at z=0
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.optimize import brentq
sR = InterpolatedUnivariateSpline(R, sigma_R[-1,:]-1)
R_nonlin = brentq(sR, R[0], R[-1])
print(r'R giving \sigma_R=1 at z=0 is at R=%.2f Mpc (or %.2f Mpc/h)'
                         %(R_nonlin, R_nonlin * pars.h))
```


```python
# the above is for the default density variable delta_tot, without including
# massive neutrinos the result would be very slightly different
sigma_R_nonu = results.get_sigmaR(R=np.arange(1,20,0.5), 
                                 var1='delta_nonu', var2='delta_nonu',
                                 hubble_units=False)
plt.plot(R, sigma_R_nonu[0,:]/ sigma_R[0,:]-1, label='z = %s'%z[0])
plt.plot(R, sigma_R_nonu[1,:]/ sigma_R[1,:]-1, label='z = %s'%z[1])
plt.ylabel(r'$\Delta\sigma_R/\sigma_R$', fontsize=14)
plt.xlabel(r'$R/{\rm Mpc}$', fontsize=14)
plt.legend();
```


```python
# results for power spectra using different initial power spectra 
# can be computed without  recomputing the transfer functions

pars = camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, redshifts=[0], kmax=5, 
                       As=2e-9, ns=0.96, halofit_version='mead')
results= camb.get_transfer_functions(pars)
kref,_,PKref = results.get_linear_matter_power_spectrum(hubble_units=False, k_hunit=False)
kref,_,PKnl = results.get_nonlinear_matter_power_spectrum(hubble_units=False, k_hunit=False)

ns_arr = np.arange(0.94, 0.981, 0.01)
fig, axs = plt.subplots(1,2, figsize=(14,5), sharey=True)

for ns in ns_arr:
    results.Params.InitPower.set_params(As=2e-9, ns=ns)
    results.calc_power_spectra()
    k,_,PK = results.get_linear_matter_power_spectrum(hubble_units=False, k_hunit=False)
    np.testing.assert_allclose(k,kref)
    axs[0].semilogx(k, PK[0,:]/PKref[0,:]-1);
    k,_,PK = results.get_nonlinear_matter_power_spectrum(hubble_units=False, k_hunit=False)
    axs[1].semilogx(k, PK[0,:]/PKnl[0,:]-1);

for ax, t in zip(axs,['Linear', 'Nonlinear']):
    ax.set_title('%s spectrum'%t)
    ax.set_xlim(1e-3,5)
    #ax.set_ylim([-0.1,0.1])
    ax.set_xlabel(r'$k\, [Mpc^{-1}]$');
plt.legend(['$n_s = %.2f$'%ns for ns in ns_arr], ncol=2, loc='lower left');
axs[0].set_ylabel(r'$\Delta P(k)/P(k)$', fontsize=16);
```


```python
# The non-linear model parameters can also be varied without recomputing the transfer functions
# eg. look at the effect of the HMcode baryonic feedback parameter
results= camb.get_transfer_functions(pars)

kref,_,PKnl = results.get_nonlinear_matter_power_spectrum(hubble_units=False, k_hunit=False)
feedbacks= np.arange(2, 4.1, 0.5)
for baryfeed in feedbacks:
    results.Params.NonLinearModel.set_params(halofit_version='mead', HMCode_A_baryon=baryfeed)
    results.calc_power_spectra()
    k,_,PK = results.get_nonlinear_matter_power_spectrum(hubble_units=False, k_hunit=False)
    np.testing.assert_allclose(k,kref)
    plt.semilogx(k, PK[0,:]/PKnl[0,:]-1)
    plt.xlim(1e-2,5)
plt.ylabel(r'$\Delta P(k)/P(k)$', fontsize=16)
plt.xlabel(r'$k\, [Mpc^{-1}]$')
plt.legend([r'$A_{\rm baryon} = %.2f$'%b for b in feedbacks]);
```


```python
# However non-linear lensing or other sources, or non-linearly lensed CMB requires 
# recalculation from the time transfer functions. This is a bit slower but faster than recomputing everything.
# e.g. look at the impact of the baryon feedback parameter on the lensing potential power spectrum

pars = camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, ns=0.965, lens_potential_accuracy=1, lmax=3000)
results= camb.get_transfer_functions(pars, only_time_sources=True)
results.calc_power_spectra()
ref = results.get_lens_potential_cls()[:,0]

feedbacks= np.arange(2, 4.1, 0.5)
for baryfeed in feedbacks:
    results.Params.NonLinearModel.set_params(halofit_version='mead', HMCode_A_baryon=baryfeed)
    results.calc_power_spectra()
    CL = results.get_lens_potential_cls()[:,0]
    plt.semilogx(np.arange(2,CL.shape[0]),CL[2:]/ref[2:]-1);

plt.legend([r'$A_{\rm baryon} = %.2f$'%b for b in feedbacks])
plt.ylabel(r'$\Delta C_L/C_L$', fontsize=16)
plt.xlabel('$L$')
plt.title('Impact of baryonic feedback on the lensing potential');
```


```python
# CAMB has a basic scalar field quintessence dark energy model
# EarlyQuintessence is a specific example implementation that implements early dark energy
# (axion-like, as arXiv:1908.06995) with potential V(\phi) = m^2f^2 (1 - cos(\phi/f))^2 + \Lambda
# AxionEffectiveFluid is an approximate model that does not evolve the quintessence equations
# To implement other models you'd need to make your own new subclass.
# Note that this is not as well tested as most of the rest of CAMB.

# Use n=3 and keep theta_* angular distance parameter fixed to roughly fit CMB data
thetastar= 0.01044341764253 
n=3

fig, axs = plt.subplots(3,1, figsize=(10,8))
zs = np.logspace(1,5,500)
pars = camb.set_params( ombh2=0.022, omch2=0.122, thetastar=thetastar) #
results = camb.get_results(pars)
print('LCDM: h0=', results.Params.H0)
cl_LCDM = results.get_lensed_scalar_cls(CMB_unit='muK')
axs[1].plot(cl_LCDM[2:,0])

# Set dark energy fraction 0.1 at z=1e4
pars = camb.set_params( ombh2=0.022, omch2=0.122, 
                       w_n=(n-1.)/(n+1.),  theta_i=np.pi/2, zc = 1e4, fde_zc = 0.1,
                       dark_energy_model='AxionEffectiveFluid', thetastar=thetastar) #
results = camb.get_results(pars)
print('AxionEffectiveFluid: h0 = ', results.Params.H0)
axs[0].semilogx(zs,results.get_Omega('de',z=zs))
cl = results.get_lensed_scalar_cls(CMB_unit='muK')
axs[0].set_ylabel(r'$\Omega_{\rm de}$')
axs[2].plot(cl[2:,0]/cl_LCDM[2:,0]-1)

pars = camb.set_params( ombh2=0.022, omch2=0.122, 
                       m=8e-53, f =0.05,n=n,  theta_i=3.1,use_zc = True, zc = 1e4, fde_zc = 0.1,
                       dark_energy_model='EarlyQuintessence', thetastar=thetastar) #
results = camb.get_results(pars)
print('EarlyQuintessence: h0 = ', results.Params.H0)
cl = results.get_lensed_scalar_cls(CMB_unit='muK')
axs[0].semilogx(zs,results.get_Omega('de',z=zs))
axs[0].set_xlabel(r'$z$')
axs[1].plot(cl[2:,0])
axs[2].plot(cl[2:,0]/cl_LCDM[2:,0]-1)
axs[1].set_ylabel(r'$D_l [\mu {\rm K}^2]$')
axs[2].set_ylabel(r'$\Delta D_l [\mu {\rm K}^2]$')
axs[1].set_xlabel(r'$\ell$')
axs[2].set_xlabel(r'$\ell$')
plt.tight_layout()

print('m = ',results.Params.DarkEnergy.m,'f = ',results.Params.DarkEnergy.f )
```


```python
# You can also calculate CMB correlation functions
# (the correlations module also has useful functions for the inverse transform,
# CMB lensing and derivatives of the lensed spectra - see docs)
from camb import correlations

pars = camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, As=2e-9, ns=0.96)
pars.set_for_lmax(4000, lens_potential_accuracy=1)
results = camb.get_results(pars)
lensed_cl = results.get_lensed_scalar_cls()
corrs, xvals, weights = correlations.gauss_legendre_correlation(lensed_cl)

r=np.arccos(xvals)*180/np.pi # sampled theta values in degrees
fig, axs= plt.subplots(2,2, figsize=(12,8))
for ix, (cap, ax) in enumerate(zip(['TT','+','-',r'\times'], axs.reshape(4))):
    ax.plot(r, corrs[:,ix])
    ax.axhline(0,color='k')
    ax.set_xlim([0,10])
    ax.set_xlabel(r'$\theta$ [degrees]')
    ax.set_ylabel(r'$\zeta_{%s}(\theta)$'%(cap), fontsize=14)
    ax.set_xlim(0,4)
plt.suptitle('Correlation functions');        
```


```python
# For partially-delensed or Alens-scaled spectra, power spectra can be computed using 
# a custom or scaled lensing potential power spectrum. There's a pure-python 
# interface in the correlation module, or can use the result object functions 
# (faster).
# Here just plot results for scaled lensing spectrum, can use 
# get_lensed_cls_with_spectrum to calculate lensed spectrum with specific 
# lensing power if needed. For BB the scaling is fairly linear, but less so for
# other spectra.

pars = camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, As=2e-9, ns=0.96)
pars.set_for_lmax(3500, lens_potential_accuracy=1)
results = camb.get_results(pars)
for Alens in [1,0.9, 0.5, 0.1]:
    plt.plot(np.arange(2,2501),
             results.get_partially_lensed_cls(Alens, lmax=2500)[2:,2],
            label='$A_L = %s$'%Alens)
plt.ylabel(r'$C_\ell^{BB}$')
plt.xlabel(r'$\ell$')   
plt.xlim([2,2500])
plt.legend();
```


```python
# For CMB lensing reconstruction, the non-perturbative response functions depend on the 
# `gradient' C_l, which can be calculated in the flat sky approximation using CAMB
# On large scales similar to lensed CMB spectrum, but important difference esp for TT on small scales
# see arXiv:1906.08760, 1101.2234 
c_lensed = results.get_lensed_scalar_cls()
c_lens_response = results.get_lensed_gradient_cls()
plt.plot(np.arange(2,3501), c_lens_response[2:3501,0]/c_lensed[2:3501,0]-1)
plt.ylabel(r'$\Delta C_l/C_l$')
plt.xlabel('$l$')  
plt.xlim(2,3500)
plt.title(r'Lensing gradient response vs lensed $C_l$');
```

CAMB also supports dark-age 21cm (see [astro-ph/0702600](https://arxiv.org/abs/astro-ph/0702600))


```python
# Get 21cm transfer functions, similar to Fig 4 of astro-ph/0702600
pars=camb.set_params(cosmomc_theta=0.0104, ombh2= 0.022, omch2= 0.12, tau = 0.053,
                     As= 2.08e-09, ns= 0.968, num_massive_neutrinos=1)

pars.Do21cm  =True

pars.Evolve_delta_xe =True # ionization fraction perturbations
pars.Evolve_baryon_cs  = True # accurate baryon perturbations
pars.WantCls =False
pars.SourceTerms.use_21cm_mK = False # Use dimensionless rather than mK units
redshifts=[50]
pars.set_matter_power(kmax=1000, redshifts=redshifts)

# get transfer functions
results= camb.get_results(pars)
trans = results.get_matter_transfer_data()
#get kh - the values of k/h at which they are calculated
k = trans.transfer_data[0,:,0]* results.Params.h

for zix, z in enumerate(redshifts,):
    # see https://camb.readthedocs.io/en/latest/transfer_variables.html

    delta_c = trans.transfer_data[model.Transfer_cdm-1,:,zix]
    delta_b = trans.transfer_data[model.Transfer_b-1,:,zix]
    T_g = trans.transfer_data[model.Transfer_Tmat-1,:,zix]
    mono = trans.transfer_data[model.Transfer_monopole-1,:,zix]

    plt.loglog(k,mono*k**2, color='k', ls='-', lw=2)   
    plt.plot(k,delta_b*k**2, color='gray', ls='-')
    plt.plot(k,T_g*k**2, color='b', ls='--')
    plt.plot(k,delta_c*k**2, color='C0', ls='-.')
    
plt.xlabel(r'$k\, \rm Mpc$', fontsize=16);
plt.title(f'Transfer functions, z={redshifts}')
plt.legend([r'21cm monopole', r'$\Delta_b$',r'$\Delta_{T_g}$', r'$\Delta_c$'], fontsize=14)
plt.ylabel(r'$T_\chi$')
plt.xlim(1e-4, 1e3)
plt.ylim(1e-3, 1e4);
```


```python
# Reionization models can be changed using the reionization_model parameter (new in v1.5.1). 
# The default tanh model is not very physical, there is a sample exponential model included as an alternative
# To define a new model inherit from the ReionizationModel classes already defined (in Fortran and Python)

# Plot the reionization histories and corresponding EE/BB spectra for various parameters
pdf_file=''
pdf = None
if pdf_file:
    from matplotlib.backends.backend_pdf import PdfPages
    pdf = PdfPages(pdf_file)
z = np.logspace(-2,3,1000)
for exp_pow in [1, 1.2, 1.5, 2]:
    fig, axs = plt.subplots(1,2,figsize=(14,6))
    ax= axs[0]
    for tau, c in zip((0.04, 0.055, 0.08, 0.12),('k','C0','C1','C2')):
        As = 1.8e-9*np.exp(2*tau)
        pars2 = camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, As=As, ns=0.95, r=0.001, reionization_model='ExpReionization', 
                                tau=tau, reion_exp_power = exp_pow, **{'Reion.timestep_boost':1})
        data2= camb.get_results(pars2)    
        pars = camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, As=As, ns=0.95, tau=tau, r=0.001)
        data= camb.get_results(pars)
    
        eta = data.conformal_time(z)
        eta2 = data2.conformal_time(z)
    
        back_ev= data.get_background_time_evolution(eta, ['x_e', 'visibility'])
        back_ev2 = data2.get_background_time_evolution(eta2, ['x_e', 'visibility'])
        
        ax.plot(z, back_ev['x_e'], ls='--', color=c,label =r'Tanh, $\tau =%.3f, z_{0.5} = %.3f$'%(tau,data.Params.Reion.redshift))
        ax.plot(z, back_ev2['x_e'], color=c, label = r'Exp, $\tau =%.3f, z_{0.5} = %.3f$'%(tau,data2.Params.Reion.redshift))
       
        cl=data.get_total_cls()
        cl2=data2.get_total_cls()
        axs[1].loglog(cl[2:,1],ls='--',color=c)
        axs[1].loglog(cl2[2:,1],ls='-',color=c)

        cl=data.get_lensed_scalar_cls()
        cl2=data2.get_lensed_scalar_cls()
        axs[1].loglog(cl[2:,2],ls=':',color=c)
        axs[1].loglog(cl2[2:,2],ls='-.',color=c)
        
        cl=data.get_tensor_cls()
        cl2=data2.get_tensor_cls()
        axs[1].loglog(cl[2:,2],ls='--',color=c)
        axs[1].loglog(cl2[2:,2],ls='-',color=c)
        
        axs[1].set_xlim((2,250))
        axs[1].set_title(r'$EE$/$BB$: $r=0.001$, $A_s e^{-2\tau}=1.8\times 10^{-9}$')
        axs[1].set_xlabel(r'$\ell$')
        axs[1].set_ylabel(r'$D_\ell$')            
        
    ax.set_xlim(0, 30)
    ax.set_xlabel('$z$')
    ax.set_ylabel('$x_e$')
    ax.legend(fontsize=9)
    ax.axvline(6.1,color='g',ls=':')
    ax.set_title(r'$x_e(z>z_c) \propto e^{-\lambda (z-z_c)^p}$, $p=%s$'%exp_pow)
    if pdf:
        pdf.savefig() 
```

### Animations

Going back to standard CMB, here is an example of how to make an animation of the evolution of 
the transfer functions.


```python
# A potential issue here is that with large dynamic range, you may wish to plot modes where
# k*eta << 1 (long way outside horizon). Evolution is not normally calculated in the code a long
# way outside the horizon, starting instead with the series solution. So for results which are numerically
# unstable, you may need to replace the numerical result with the series result.

# Use widget to see animation in notebook rather than just saving (with "pip install ipympl")
# %matplotlib widget 

pars = camb.read_ini('https://raw.githubusercontent.com/cmbant/CAMB/master/inifiles/planck_2018.ini')
data= camb.get_results(pars)

# get ranges to plot, evolving until recombination
zstar=data.get_derived_params()['zstar']
etastar=data.conformal_time(zstar)
# stop time evolution (eta) at recombination
eta = np.logspace(-1.7,np.log10(etastar),400)
# wide range of k
k=10**np.linspace(-3,1,1200)

# get some background quantities
z = data.redshift_at_conformal_time(eta)
back_ev = data.get_background_time_evolution(eta, ['x_e', 'visibility'])
x_e=back_ev['x_e']
vis=back_ev['visibility']
adotoa = data.h_of_z(z)/(1+z)  # comoving Hubble
# ratio of matter to radiation (neglecting neutrino mass)
rho=data.get_background_densities(1/(1+z))
Rmat=(rho['baryon']+rho['cdm'])/(rho['photon']+rho['neutrino']+rho['nu'])

# some quantities needed for superhorizon series solution -see series solutions in notes at
# https://cosmologist.info/notes/CAMB.pdf
grhonu=data.grhormass[0]+data.grhornomass
Rv=grhonu/(grhonu+data.grhog)
omega = (data.grhob+data.grhoc)/np.sqrt(3*(data.grhog+grhonu))
# initial value of super-horizon Psi for unit curvature
Psi_init = -10/(4*Rv+15)

# make evolution plot in Newtonian gauge. Use symbolic package to get right gauge-invariant quantities.
import camb.symbolic as cs

ev=data.get_time_evolution(k, eta, [cs.Psi_N, # Newtonian potential \Psi
                                    'delta_photon', # sychronous gauge photon perturbation
                                    cs.make_frame_invariant(cs.Delta_g, 'Newtonian'), #photon perturbation
                                    cs.make_frame_invariant(cs.v_b, 'Newtonian') # baryon velocity
                                   ], lAccuracyBoost=4)
Psi = ev[:,:,0]
Delta_g = ev[:,:,1]
Delta_g_N=ev[:,:,2]
v_b_N = ev[:,:,3]

# Now replace Psi results well outside horizon where numerically unstable with series solution
# Note Newtonian-gauge Delta_g does not start at zero, so is also unstable
for i, etai in enumerate(eta):
    for j, kj in enumerate(k):
        if etai*kj < 0.1 and etai*omega < 0.1:
            Psi[j,i]=Psi_init - 25/8*omega*etai *(8*Rv-3)/(4*Rv+15)/(2*Rv+15)
            # use Delta_g_N = Delta_g - 4H sigma/k (with adiabatic series result for sigma)
            Delta_g_N[j,i] = Delta_g[j,i] - 4*adotoa[i]*( Psi_init/2*etai - 15*omega*etai**2/8*(4*Rv-5)/(4*Rv+15)/(2*Rv+15))

```


```python
# output animation (must have ffmpeg installed)
import math
from matplotlib import animation

def latex_sci_format(num, dec=3):
    return "{:.{dec}f}\\times 10^{{{}}}".format(num / (10 ** int(math.floor(math.log10(abs(num))))), int(math.floor(math.log10(abs(num)))), dec=dec)

fig, ax = plt.subplots()

plot_vars = {r'$\Psi$':Psi, 
             r'$\frac{1}{4}\Delta^{\rm Newt}_\gamma +\Psi$': Delta_g_N/4+Psi, 
             r'$\frac{1}{\sqrt{3}}v_b^{\rm Newt}$': v_b_N/np.sqrt(3) }

anim_fps=8

lines=[]
for lab in plot_vars.keys():
    line, = ax.semilogx([], [], label=lab)
    lines.append(line)
    
ax.axhline(0,color='k')
plt.legend(loc='upper left')

ax.set_xlim(k[0], k[-1])
ax.set_ylim(-1, 1)
ax.set_xlabel(r'$k\, {\rm Mpc}$')

# Define the update function
def update(i):
    ax.set_title( r'$z= %s, \eta/{\rm Mpc}= %.2f, x_e = %.2f, \rho_m/\rho_{\rm rad}=%.2f$' 
                  % (latex_sci_format(z[i]), eta[i], x_e[i], Rmat[i]))
    for line, var in zip(lines,plot_vars.values()):
        line.set_data(k, var[:, i])
    return lines

# Create the animation
transfer_anim =animation.FuncAnimation(fig, update, frames=range(len(eta)),  blit=True)
writer = animation.writers['ffmpeg'](fps=anim_fps, bitrate=-1)

# can save like this
transfer_anim.save(r'Newtonian_transfer_evolve_monopole_phi_vb.mp4', writer=writer, dpi=240)
```

```python
# or play inline using:
# from IPython.display import display, Video
# video = transfer_anim.to_html5_video()
# display(Video(data=video, embed=True, width = 600))
```


```python
# Animate the matter transfer and potential evolution up to today
# now use log scale and synchronous gauge as more relevant for the late-time matter

eta=np.logspace(-1.7,np.log10(data.tau0),500)[:-1]
k=10**np.linspace(-3,2,2000)
z = data.redshift_at_conformal_time(eta)
import camb.symbolic as cs
ev=data.get_time_evolution(k, eta, [cs.Psi_N,
                                    'delta_cdm', # sychronous gauge cdm perturbation
                                    'delta_photon', 
                                    'delta_baryon'], lAccuracyBoost=4)

Psi = ev[:,:,0]
Delta_c = ev[:,:,1]
Delta_g=ev[:,:,2]
Delta_b=ev[:,:,3]

x_e = data.get_background_time_evolution(eta, ['x_e'])['x_e']
adotoa = data.h_of_z(z)/(1+z)  # comoving Hubble
rho=data.get_background_densities(1/(1+z))
Rmat=(rho['baryon']+rho['cdm'])/(rho['photon']+rho['neutrino']+rho['nu'])
zstar=data.get_derived_params()['zstar']

# series for super-horizon Psi
grhonu=data.grhormass[0]+data.grhornomass
Rv=grhonu/(grhonu+data.grhog)
omega = (data.grhob+data.grhoc)/np.sqrt(3*(data.grhog+grhonu))
# initial value of super-horizon Psi for unit curvature and no isocurvature
Psi_init = -10/(4*Rv+15)
for i, etai in enumerate(eta):
    for j, kj in enumerate(k):
        if etai*kj < 0.1 and etai*omega < 0.1:
            Psi[j,i]=Psi_init - 25/8*omega*etai *(8*Rv-3)/(4*Rv+15)/(2*Rv+15)
```


```python
fig, ax = plt.subplots()
plot_vars = {r'$\Delta_c$': Delta_c, r'$\Delta_b$': Delta_b,
             r'$\Delta_g$': Delta_g,r'$\Psi$': Psi}             
anim_fps=8
lines=[]
for lab in plot_vars.keys():
    line, = ax.loglog([], [], label=lab)
    lines.append(line)

plt.axhline(0, ls='-', color='k')
plt.legend(loc='upper left')
ax.set_xlim(k[0], k[-1])
ax.set_xlabel(r'$k\, {\rm Mpc}$')

ax.set_ylim(1e-4, 2e5)
lines.append(ax.loglog([], [],ls='--', color='C1')[0])
lines.append(ax.loglog([], [],ls='--', color='C2')[0])
lines.append(ax.loglog([], [],ls='--', color='C3')[0])
    
# Define the update function
def update(i):
    ax.set_title( r'$z= %s, \eta/{\rm Mpc}= %.2f, x_e = %.2f, \rho_m/\rho_{\rm rad}=%.2f$' 
                  % (latex_sci_format(z[i],2), eta[i], x_e[i], Rmat[i]), fontsize=10)

    for line, var in zip(lines,plot_vars.values()):
        line.set_data(k, var[:, i])
    lines[-3].set_data(k,-Delta_b[:, i])
    lines[-2].set_data(k,-Delta_g[:, i])
    lines[-1].set_data(k,-Psi[:, i])
        
    if z[i] < zstar: # hide photons after recombination as irrelevant for matter
        lines[2].set_data([],[]) 
        lines[-2].set_data([],[])      
    return lines

# Create the animation
transfer_anim =animation.FuncAnimation(fig, update, frames=range(len(eta)),  blit=True, repeat = False)
writer = animation.writers['ffmpeg'](fps=anim_fps, bitrate=-1)
transfer_anim.save(r'matter_transfer_evolve_sync.mp4', writer=writer, dpi=240)
```
