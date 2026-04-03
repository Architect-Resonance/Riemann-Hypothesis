"""
Diagonal Dominance Test — S154-M1 cont.24

Question: Is the prime sum operator P approximately diagonal in the
Fourier basis? If so, the gap is controlled by the ratio of diagonal
elements, which are exponential sums over primes.

Specifically: P_{kk}/P_{00} for k >= 1 should be bounded away from 1
(by Vinogradov-Korobov bounds on exponential sums over primes).

Also test: ||P - diag(P)||_op / r(P) — is the off-diagonal part small?
"""

import numpy as np
import math
from mpmath import mp, mpf, mpc, log, pi, im, loggamma
from sympy import nextprime

mp.dps = 20


def theta_prime(t):
    t = mpf(str(t))
    if abs(t) < 0.01:
        t = mpf('0.01')
    h = mpf('1e-10')
    theta = lambda x: -x / 2 * mp.log(mp.pi) + im(loggamma(mpf('0.25') + mpc(0, x / 2)))
    return float((theta(t + h) - theta(t - h)) / (2 * h))


def build_P(lam_sq, N):
    lam = math.sqrt(lam_sq)
    log_lam = math.log(lam)
    L = 2 * log_lam
    dim = 2 * N + 1

    P = np.zeros((dim, dim), dtype=complex)
    p = 2
    while p <= lam_sq:
        lp = float(log(p))
        k = 1
        while p ** k <= lam_sq:
            lpk = k * lp
            weight = lp * (p ** k) ** (-0.5)
            overlap = max(0, L - lpk)
            if overlap <= 0:
                k += 1
                continue
            for m_idx in range(dim):
                for n_idx in range(dim):
                    m_val = m_idx - N
                    n_val = n_idx - N
                    phase_n = 2 * np.pi * n_val * lpk / L
                    diff = n_val - m_val
                    if diff == 0:
                        integral_val = overlap / L
                    else:
                        arg = 2 * np.pi * diff * overlap / L
                        integral_val = (np.exp(1j * arg) - 1) / (2j * np.pi * diff / L) / L
                    contrib = weight * np.exp(1j * phase_n) * integral_val
                    contrib_inv = weight * np.exp(-1j * phase_n) * np.conj(integral_val)
                    P[m_idx, n_idx] += (contrib + contrib_inv)
            k += 1
        p = int(nextprime(p))
    P = (P + P.conj().T) / 2
    P = P.real
    return P


def project_even(M, N):
    dim = 2 * N + 1
    S = np.zeros((dim, N + 1))
    S[N, 0] = 1.0
    for k in range(1, N + 1):
        S[N + k, k] = 1.0 / np.sqrt(2)
        S[N - k, k] = 1.0 / np.sqrt(2)
    return S.T @ M @ S


def main():
    N = 15
    print("=" * 95)
    print("DIAGONAL DOMINANCE OF P IN EVEN-SECTOR FOURIER BASIS")
    print("=" * 95)

    for lam_sq in [29, 67, 163, 499, 997, 2003, 5003]:
        lam = math.sqrt(lam_sq)
        P = build_P(lam_sq, N)
        P_e = project_even(P, N)

        diag_P = np.diag(np.diag(P_e))
        offdiag = P_e - diag_P

        eigs = np.sort(np.linalg.eigvalsh(P_e))[::-1]
        r_P = eigs[0]
        sigma2 = eigs[1]
        gap = r_P - sigma2

        diag_vals = np.diag(P_e)
        offdiag_norm = np.linalg.norm(offdiag, ord=2)

        print(f"\nlambda^2 = {lam_sq}, lambda = {lam:.2f}")
        print(f"  r(P_even) = {r_P:.3f},  sigma_2 = {sigma2:.3f},  gap = {gap:.3f}")
        print(f"  gap/r(P) = {gap/r_P:.4f},  sigma_2/r(P) = {sigma2/r_P:.4f}")
        print(f"  P_00 = {diag_vals[0]:.3f}")
        print(f"  Diag ratios P_kk/P_00: ", end="")
        for k in range(1, min(6, len(diag_vals))):
            print(f"k={k}: {diag_vals[k]/diag_vals[0]:.4f}  ", end="")
        print()
        print(f"  ||offdiag||_op = {offdiag_norm:.3f},  ||offdiag||/r(P) = {offdiag_norm/r_P:.4f}")
        print(f"  Max |offdiag entry| = {np.max(np.abs(offdiag)):.3f}")


if __name__ == "__main__":
    main()