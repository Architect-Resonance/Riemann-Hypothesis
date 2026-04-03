# Spectral Simplicity of the Weil Quadratic Form via Krein-Rutman Positivity

## Summary

We address the two missing conditions identified by Connes, Consani, and Moscovici ([arXiv:2511.22755](https://arxiv.org/abs/2511.22755)) for their spectral approach to the Riemann Hypothesis:

1. **(S1) Spectral simplicity**: the smallest eigenvalue of the Weil quadratic form QW_λ is simple with even eigenfunction.
2. **(S2) Convergence**: the eigenfunction converges to Riemann's Ξ function.

The key observation is that the prime sum operator P_λ in the decomposition QW_λ = A + Π − P is a Krein-Rutman operator (positive, compact, irreducible), and that the polar term Π_λ has even-sector operator norm O(log λ) — not O(λ) as the naive bound suggests — due to a cancellation in the Fourier matrix elements forced by the functional equation of ζ.

## Paper

- **[siche_riemann_hypothesis_2026.pdf](paper/siche_riemann_hypothesis_2026.pdf)** — full paper (12 pages)

## Verification Scripts

All numerical claims in the paper are reproducible. Scripts require Python 3.10+, NumPy, mpmath, and SymPy.

| Script | Verifies |
|--------|----------|
| `connes_exact_weil.py` | Full QW_λ construction (archimedean + polar + prime sum) |
| `even_sector_scaling.py` | Even-sector spectral gap to λ² = 7993 |
| `polar_norm_scaling.py` | Polar cancellation: ‖Π^{++}‖ = O(log λ) |
| `gap_convergence_N.py` | Convergence under Fourier truncation refinement |
| `diagonal_dominance_test.py` | σ₂(P) bounded (trace bound verification) |
| `rayleigh_orthogonal_test.py` | Rayleigh quotient decomposition for second eigenvector |
| `krein_rutman_test.py` | Positivity, compactness, irreducibility of P_λ |
| `commutator_test.py` | Spectral alignment: [P, Π] → 0 |

## References

- A. Connes, C. Consani, H. Moscovici, *Zeta Spectral Triples*, [arXiv:2511.22755](https://arxiv.org/abs/2511.22755) (2025)
- A. Connes, *The Riemann Hypothesis: past, present and a letter through time*, [arXiv:2602.04022](https://arxiv.org/abs/2602.04022) (2026)
- M.G. Krein, M.A. Rutman, *Linear operators leaving invariant a cone in a Banach space*, Uspekhi Mat. Nauk **3**(1) (1948), 3–95

## Author

Brendan Siche — Independent Researcher