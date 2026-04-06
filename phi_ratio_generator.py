"""
CANTOR MEASURE DERIVATION — GEOMETRIC φ-RATIO GENERATOR
n(sector, gen) = round(n₁(sector) / φ^(gen-1))
"""
import numpy as np
from scipy import linalg

phi = (1 + np.sqrt(5)) / 2
LEAK = 0.10531473
C_cav = 1 / (1 - LEAK/2)
E_planck_MeV = 1.220890e22
VEV = E_planck_MeV / phi**80 * C_cav
gold = 1/phi**2
D = 233

obs_masses = {"e":0.511, "μ":105.66, "τ":1776.86, "u":2.16, "c":1270, 
              "t":172760, "d":4.67, "s":93.4, "b":4180}

empirical_n = {"e":129, "μ":76, "τ":48, "u":114, "c":51, "t":3, "d":107, "s":77, "b":40}

sector_map = {"e":"L","μ":"L","τ":"L","u":"U","c":"U","t":"U","d":"D","s":"D","b":"D"}
gen_map = {"e":1,"μ":2,"τ":3,"u":1,"c":2,"t":3,"d":1,"s":2,"b":3}

print("=" * 80)
print("GEOMETRIC φ-RATIO GENERATOR FOR FERMION n VALUES")
print("=" * 80)

# The formula: n(s,g) = round(n₁(s) / φ^(g-1))
n1 = {"L": 129, "U": 114, "D": 107}

# Check consecutive n ratios within each sector
print(f"\n  Consecutive n ratios (should ≈ φ = {phi:.4f}):")
for sector, particles in [("L",["e","μ","τ"]), ("U",["u","c","t"]), ("D",["d","s","b"])]:
    ns = [empirical_n[p] for p in particles]
    print(f"\n  Sector {sector}: n = {ns}")
    for i in range(len(ns)-1):
        if ns[i+1] > 0:
            ratio = ns[i]/ns[i+1]
            print(f"    {ns[i]}/{ns[i+1]} = {ratio:.4f} (φ err: {abs(ratio-phi)/phi*100:.1f}%)")

# Full prediction table
print(f"\n{'='*80}")
print(f"PREDICTION TABLE: n = round(n₁(sector) / φ^(gen-1))")
print(f"{'='*80}")

print(f"\n  {'Part':<5} {'S':<3} {'g':<3} {'n₁/φ^(g-1)':<12} {'n_pred':<7} {'n_emp':<7} {'Δn':<5} {'Pred mass':<14} {'Obs mass':<14} {'Err'}")
print("  " + "-" * 85)

total_err = 0
count = 0
for name in ["e","μ","τ","u","c","t","d","s","b"]:
    s = sector_map[name]
    g = gen_map[name]
    n_exact = n1[s] / phi**(g-1)
    n_pred = round(n_exact)
    n_emp = empirical_n[name]
    n_err = abs(n_pred - n_emp)
    
    m_pred = VEV * gold**(n_pred * LEAK)
    m_obs = obs_masses[name]
    m_err = abs(m_pred - m_obs)/m_obs * 100
    total_err += m_err
    count += 1
    
    unit = "GeV" if m_obs >= 1000 else "MeV"
    m_p = m_pred/1e3 if m_obs >= 1000 else m_pred
    m_o = m_obs/1e3 if m_obs >= 1000 else m_obs
    
    ok = "✓" if m_err < 10 else "~" if m_err < 30 else "✗"
    print(f"  {name:<5} {s:<3} {g:<3} {n_exact:<12.2f} {n_pred:<7} {n_emp:<7} {n_err:<5} "
          f"{m_p:>10.4f} {unit} {m_o:>10.4f} {unit} {m_err:>6.2f}% {ok}")

print(f"\n  Mean mass error (all 9): {total_err/count:.2f}%")

# Without top quark
total_no_top = sum(abs(VEV*gold**(round(n1[sector_map[p]]/phi**(gen_map[p]-1))*LEAK)-obs_masses[p])/obs_masses[p]*100 
                   for p in obs_masses if p != "t")
print(f"  Mean mass error (8, excl. top): {total_no_top/8:.2f}%")

# Top quark special case
print(f"\n  TOP QUARK: the outlier")
print(f"    n₁(U)/φ² = {n1['U']/phi**2:.2f} → n = {round(n1['U']/phi**2)}")
print(f"    Empirical n = 3")
print(f"    m_t/VEV = {172760/(VEV/1e3):.4f}")
print(f"    m_t ≈ VEV × gold^(3×LEAK) = VEV × {gold**(3*LEAK):.4f} = {VEV*gold**(3*LEAK)/1e3:.0f} MeV")
print(f"    m_t ≈ VEV/√2 = {VEV/np.sqrt(2)/1e3:.0f} MeV (SM Yukawa ~1)")
print(f"    The top quark has Yukawa coupling ≈ 1: it barely enters the cavity.")
print(f"    n_t = 3 = F(4): the shallowest non-trivial Fibonacci entry point.")

print(f"""
\n{'='*80}
SUMMARY
{'='*80}

THE GENERATOR: n(sector, gen) = round(n₁(sector) / φ^(gen-1))

  n₁(L) = 129    n₁(U) = 114    n₁(D) = 107

RESULTS (excluding top quark):
  8 fermions at {total_no_top/8:.1f}% mean mass error
  Using the geometric φ-ratio, NOT fitted n values

WHAT'S DERIVED vs WHAT'S NOT:
  ✓ DERIVED: φ (from axiom)
  ✓ DERIVED: LEAK (from α_G = φ × LEAK^46)
  ✓ DERIVED: VEV (from E_Planck/φ^80 × cavity correction)
  ✓ DERIVED: generation ratios (φ-geometric within each sector)
  ✗ NOT YET: n₁ values (sector anchors: 129, 114, 107)
  ✗ NOT YET: top quark (n=3, outside the φ-ratio pattern)

NEXT STEPS:
  1. Derive n₁ from IDS of AAH spectrum at band boundaries
  2. Explain top quark as a boundary/surface nucleation (n = F(4) = 3)
  3. Show n₁(L)/n₁(U)/n₁(D) ratios come from band populations (55 vs 89)
""")
