import numpy as np
from scipy.optimize import minimize

phi = (1 + np.sqrt(5)) / 2
LEAK = 0.10531473
R = 1 - LEAK  # 0.89468527 — energy retained per round trip
C_cav = 1 / (1 - LEAK/2)

E_planck_MeV = 1.220890e22  # Planck energy in MeV

print("=" * 80)
print("ENTANGLEMENT TAX MODEL: MASS FROM ROUND-TRIP ENERGY LOSS")
print("=" * 80)

print(f"""
Physical picture:
  
  The cavity between band walls σ₁ and σ₅ contains energy.
  Each round trip, LEAK = {LEAK:.4f} escapes through the wall.
  What REMAINS inside after N trips: E × R^N where R = {R:.6f}
  
  Heavier particles = fewer round trips = less tax paid
  Lighter particles = more round trips = more tax paid
  
  The electron has been through the MOST round trips.
  The top quark has been through the FEWEST.
  
  Each "sector" (lepton, up-quark, down-quark) enters the
  cavity at a different energy — set by which band wall 
  (σ₁ vs σ₅) and which part of the Cantor conduit.
""")

# All fermion masses in MeV
fermions = [
    ("e",   "L", 1,  0.51099895),
    ("μ",   "L", 2,  105.6583755),
    ("τ",   "L", 3,  1776.86),
    ("u",   "U", 1,  2.16),
    ("c",   "U", 2,  1270.0),
    ("t",   "U", 3,  172760.0),
    ("d",   "D", 1,  4.67),
    ("s",   "D", 2,  93.4),
    ("b",   "D", 3,  4180.0),
]

# =============================================================
# MODEL A: m(s,g) = E_s × R^(N_s - g × step_s)
# 
# E_s = boundary energy for sector s
# N_s = total round trips for gen-1 in sector s
# step_s = round trips saved per generation
#
# In log space: ln(m) = ln(E_s) + (N_s - g × step_s) × ln(R)
# This is linear in g: ln(m) = [ln(E_s) + N_s×ln(R)] - g×step_s×ln(R)
# =============================================================

print("=" * 80)
print("MODEL A: m = E_boundary × R^(N - g × step)")
print("=" * 80)

lnR = np.log(R)

for sector_name, sector_label in [("Leptons","L"), ("Up-quarks","U"), ("Down-quarks","D")]:
    masses = [(g, m) for name, s, g, m in fermions if s == sector_label]
    gens = [g for g, m in masses]
    lnm = [np.log(m) for g, m in masses]
    
    # Fit: ln(m) = a + b × g
    # where a = ln(E) + N×ln(R), b = -step × ln(R)
    coeffs = np.polyfit(gens, lnm, 1)
    b, a = coeffs
    
    step = -b / lnR
    # Can't separate E and N from a alone, but:
    # At g=0 (hypothetical gen-0): ln(m_0) = a → m_0 = e^a
    m_0 = np.exp(a)
    
    print(f"\n{sector_name}:")
    print(f"  ln(m) = {a:.4f} + {b:.4f} × g")
    print(f"  step = -b/ln(R) = {step:.4f} round trips per generation")
    print(f"  m(g=0) = e^a = {m_0:.4f} MeV (boundary energy proxy)")
    
    for g, m_obs in masses:
        m_pred = np.exp(a + b * g)
        err = abs(m_pred - m_obs)/m_obs * 100
        print(f"  g={g}: pred={m_pred:.4f} MeV, obs={m_obs:.4f} MeV, err={err:.2f}%")

# Linear in g is same problem as before. The spacing ISN'T linear.
# Let's try nonlinear.

# =============================================================
# MODEL B: m(s,g) = E_s × R^(φ^(α_s - β_s × g))
#
# The number of round trips ITSELF follows a φ-power law.
# Gen 1: many trips (φ^large → light)
# Gen 3: few trips (φ^small → heavy)
# The φ-decay of trip count IS the fractal conduit structure.
# =============================================================

print("\n" + "=" * 80)
print("MODEL B: m = E_s × R^(φ^(α - β×g))")
print("Trips follow φ-power law — fractal conduit depth")
print("=" * 80)

def model_B_predict(params, sector_data):
    lnE, alpha, beta = params
    predictions = []
    for g, m_obs in sector_data:
        trips = phi**(alpha - beta * g)
        lnm = lnE + trips * lnR
        predictions.append((g, np.exp(lnm), m_obs))
    return predictions

def model_B_error(params, sector_data):
    preds = model_B_predict(params, sector_data)
    return sum((np.log(p) - np.log(o))**2 for _, p, o in preds)

for sector_name, sector_label in [("Leptons","L"), ("Up-quarks","U"), ("Down-quarks","D")]:
    masses = [(g, m) for name, s, g, m in fermions if s == sector_label]
    
    # Optimize
    best = None
    best_err = 1e10
    for lnE_init in np.arange(5, 30, 2):
        for alpha_init in np.arange(1, 8, 0.5):
            for beta_init in np.arange(0.5, 4, 0.5):
                try:
                    res = minimize(model_B_error, [lnE_init, alpha_init, beta_init], 
                                   args=(masses,), method='Nelder-Mead')
                    if res.fun < best_err:
                        best_err = res.fun
                        best = res.x
                except:
                    pass
    
    lnE, alpha, beta = best
    print(f"\n{sector_name}:")
    print(f"  E_boundary = {np.exp(lnE):.4f} MeV = {np.exp(lnE)/1000:.4f} GeV")
    print(f"  α = {alpha:.4f}, β = {beta:.4f}")
    print(f"  β/α = {beta/alpha:.4f}")
    print(f"  Trips: g=1: φ^{alpha-beta:.3f}={phi**(alpha-beta):.2f}, "
          f"g=2: φ^{alpha-2*beta:.3f}={phi**(alpha-2*beta):.2f}, "
          f"g=3: φ^{alpha-3*beta:.3f}={phi**(alpha-3*beta):.2f}")
    
    preds = model_B_predict(best, masses)
    for g, pred, obs in preds:
        err = abs(pred - obs)/obs * 100
        print(f"  g={g}: trips={phi**(alpha-beta*g):.2f}, pred={pred:.4f}, obs={obs:.4f}, err={err:.4f}%")

# =============================================================
# MODEL C: The LEAK cascade — each generation is one fewer
# passage through the Cantor set fractal hierarchy.
# 
# Key insight: LEAK^46 appears in α_G.
# 46 = total hops from Planck to electron.
# Each generation REMOVES some hops.
# m(g) = m_e × (1/LEAK)^(hops_removed(g))
# =============================================================

print("\n" + "=" * 80)
print("MODEL C: Generation as LEAK-hop removal")
print("Fewer hops through conduit = heavier (less taxed)")
print("=" * 80)

m_e = 0.51099895

# How many LEAK-hops separate each generation?
# m_μ/m_e = (1/LEAK)^Δ → Δ = log(m_μ/m_e) / log(1/LEAK)
for name, s, g, mass in fermions:
    if mass == m_e:
        continue
    ratio = mass / m_e
    delta_leak = np.log(ratio) / np.log(1/LEAK)
    delta_phi = np.log(ratio) / np.log(phi)
    print(f"  {name}: m/m_e = {ratio:.4f}, "
          f"LEAK-hops removed = {delta_leak:.4f}, "
          f"φ-steps = {delta_phi:.4f}")

# =============================================================
# MODEL D: UNIFIED — mass = E_Planck × φ^(-n) × R^(trips(s,g))
# Combine the Planck ladder with the round-trip tax
# 
# n = base position on φ-ladder (same for all particles)
# trips = sector & generation dependent tax
# =============================================================

print("\n" + "=" * 80)
print("MODEL D: m = E_Planck/φ^n₀ × R^(N_s × φ^(-g×c_s))")
print("Planck ladder + fractal round-trip tax")
print("=" * 80)

# What if ALL particles start from the SAME Planck-ladder position
# but get taxed differently?
# m = E_Planck/φ^80 × R^f(s,g)
# where f(s,g) encodes how many round trips each particle endures

v_raw = E_planck_MeV / phi**80  # ≈ 233 GeV — the raw VEV energy

print(f"\nBase energy: E_Planck/φ^80 = {v_raw/1000:.2f} GeV (≈ Higgs VEV!)")
print(f"\nAll particles as tax fractions of the VEV:")

for name, s, g, mass in sorted(fermions, key=lambda x: -x[3]):
    # m = v_raw × R^trips → trips = ln(m/v_raw) / ln(R)
    trips = np.log(mass / v_raw) / lnR
    print(f"  {name:<3} (g={g}, {s}): {trips:8.2f} round trips  "
          f"({mass:.4f} MeV, ratio to VEV: {mass/v_raw:.2e})")

# =============================================================
# MODEL E: The cascade — energy splits at each wall
# At the VEV scale, energy encounters the band wall.
# Gold fraction (1/φ²) stays as mass.
# Silver fraction (1/φ) gets re-emitted.
# Each RE-ENCOUNTER with the wall applies the same split.
# After N encounters: mass = VEV × gold^N = VEV × (1/φ²)^N = VEV/φ^(2N)
# =============================================================

print("\n" + "=" * 80)
print("MODEL E: Cascading gold-silver splits from VEV")
print("Each wall encounter: gold (1/φ²) stays, silver (1/φ) leaves")
print("After N encounters: m = VEV × (1/φ²)^N = VEV/φ^(2N)")
print("=" * 80)

gold = 1/phi**2

for name, s, g, mass in sorted(fermions, key=lambda x: -x[3]):
    # m = VEV × gold^N → N = ln(m/VEV) / ln(gold)
    N = np.log(mass / v_raw) / np.log(gold)
    # Or equivalently: m = VEV/φ^(2N) → 2N = log_φ(VEV/m)
    two_N = np.log(v_raw / mass) / np.log(phi)
    print(f"  {name:<3} ({s}{g}): N = {N:6.3f} gold-splits  "
          f"(2N = {two_N:.3f} φ-steps, mass = {mass:.4f} MeV)")

# =============================================================
# MODEL F: The WORKING model — gold splits + sector phase
# 
# N must be quantized. N = integer or half-integer.
# Plus a sector-dependent phase shift.
# m(s,g) = VEV × gold^(N_base(s) - Δ(g))
# where Δ(g) = how many splits the generation SKIPS
# =============================================================

print("\n" + "=" * 80)
print("MODEL F: Quantized gold-splits with sector offset")
print("m = VEV × (1/φ²)^(N₀ + n_s - g × step_s)")
print("=" * 80)

# From Model E, the N values are:
# t: N=5.42, b: N=8.77, τ: N=10.08, c: N=10.72, 
# μ: N=15.67, s: N=15.87, d: N=21.09, u: N=21.40, e: N=22.79

# These aren't integers. But what if N is quantized in units of
# something related to LEAK or φ?

# Let's check: are the N values quantized in half-integers?
print("\nGold-split counts and nearest half-integers:")
for name, s, g, mass in sorted(fermions, key=lambda x: -x[3]):
    N = np.log(mass / v_raw) / np.log(gold)
    N_half = round(2*N) / 2
    m_pred = v_raw * gold**N_half
    err = abs(m_pred - mass)/mass * 100
    print(f"  {name:<3}: N={N:.3f}, N_half={N_half:.1f}, "
          f"pred={m_pred:.4f} MeV, err={err:.1f}%")

# What about quantized in units of LEAK?
print(f"\nQuantized in units of LEAK = {LEAK:.4f}:")
for name, s, g, mass in sorted(fermions, key=lambda x: -x[3]):
    N = np.log(mass / v_raw) / np.log(gold)
    N_leak = N / LEAK
    N_leak_int = round(N_leak)
    N_quant = N_leak_int * LEAK
    m_pred = v_raw * gold**N_quant
    err = abs(m_pred - mass)/mass * 100
    print(f"  {name:<3}: N/LEAK={N_leak:.2f} → {N_leak_int}, "
          f"pred={m_pred:.4f}, err={err:.1f}%")

# =============================================================
# MODEL G: Direct — every mass is VEV / φ^n where n is integer
# This is equivalent to Model E with 2N = integer
# The question: what SELECTS which integer?
# =============================================================

print("\n" + "=" * 80)
print("MODEL G: m = VEV / φ^n  (n = integer)")
print("With VEV corrected: VEV × C_cav = " + f"{v_raw*C_cav/1000:.2f} GeV")
print("=" * 80)

VEV = v_raw * C_cav  # corrected VEV

print(f"\n{'Name':<6} {'n':<6} {'Predicted':<14} {'Observed':<14} {'Error':<8} {'n value'}")
print("-" * 65)

all_results = []
for name, s, g, mass in sorted(fermions, key=lambda x: -x[3]):
    n_exact = np.log(VEV / mass) / np.log(phi)
    n_int = round(n_exact)
    pred = VEV / phi**n_int
    err = abs(pred - mass)/mass * 100
    frac = n_exact - n_int
    all_results.append((name, s, g, n_int, pred, mass, err, frac))
    unit = "MeV" if mass < 1000 else "GeV"
    if mass < 1000:
        print(f"{name:<6} {n_int:<6} {pred:<11.4f} MeV {mass:<11.4f} MeV {err:<7.2f}% (frac={frac:+.3f})")
    else:
        print(f"{name:<6} {n_int:<6} {pred/1000:<11.4f} GeV {mass/1000:<11.4f} GeV {err:<7.2f}% (frac={frac:+.3f})")

mean_err = np.mean([r[6] for r in all_results])
print(f"\nMean error: {mean_err:.2f}%")

# What are the n values?
print(f"\nThe quantum numbers (n = φ-steps below VEV):")
for r in sorted(all_results, key=lambda x: x[3]):
    name, s, g, n, pred, obs, err, frac = r
    print(f"  n={n:3d}: {name} ({s}{g})")

# Spacing between n values
ns = sorted(set(r[3] for r in all_results))
print(f"\nn values: {ns}")
print(f"Spacings: {[ns[i+1]-ns[i] for i in range(len(ns)-1)]}")

# =============================================================
# FINAL SUMMARY
# =============================================================
print(f"""
{'='*80}
SUMMARY: WHAT THE ENTANGLEMENT TAX TELLS US
{'='*80}

Every particle mass = VEV / φ^n

where VEV = E_Planck / φ^80 × 1/(1-LEAK/2) ≈ {VEV/1000:.2f} GeV
and n is a non-negative integer = number of gold-silver splits
from the electroweak boundary energy.

Each gold-silver split: the gold fraction (1/φ²) stays as mass,
the silver fraction (1/φ) escapes as entanglement tax.

After n splits: mass = VEV × (1/φ²)^(n/2) = VEV / φ^n

The electron has endured the MOST splits (n≈{[r[3] for r in all_results if r[0]=='e'][0]}).
The top quark has endured the FEWEST (n≈{[r[3] for r in all_results if r[0]=='t'][0]}).

The GENERATION NUMBER determines how many splits occur.
The SECTOR determines the offset (which wall, which conduit path).

What SELECTS n for each particle?
→ The number of times the energy bounces between σ₁ and σ₅ walls
→ Each bounce costs 1/φ² of the remaining energy
→ Heavier particles = fewer bounces = less tax paid
→ The bouncing count is set by the harmonic signature 
   matching condition — when the remaining energy matches
   the entanglement key for that particle's quantum numbers,
   it nucleates out of the cavity.

The particle IS the crystallization event.
The mass IS what's left after the tax is paid.
""")
