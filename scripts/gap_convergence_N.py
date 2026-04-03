"""
Gap convergence vs N (Fourier truncation) — S154-M1 cont.24

Critical question: does gap(QW_even) converge as N increases?
If the gap shrinks to 0 with N, the discretization was lying.
If it converges to a positive value, the gap is real.

Also check: does ||Pi_even|| grow with N? (It should, since the
continuum ||Pi|| = O(lambda).)
"""

import numpy as np
import math
from mpmath import mp, mpf, mpc, log, pi, im, loggamma
from sympy import nextprime

mp.dps = 30


def theta_prime(t):
    t = mpf(str(t))
    if abs(t) < 0.01:
        t = mpf('0.01')
    h = mpf('1e-10')
    theta = lambda x: -x / 2 * mp.log(mp.pi) + im(loggamma(mpf('0.25') + mpc(0, x / 2)))
    return float((theta(t + h) - theta(t - h)) / (2 * h))


def build_operators(lam_sq, N):
    """Build A, Pi, P in Fourier basis V_n, |n| <= N."""
    lam = math.sqrt(lam_sq)
    log_lam = math.log(lam)
    L = 2 * log_lam
    dim = 2 * N + 1

    A = np.zeros((dim, dim))
    for idx in range(dim):
        n = idx - N
        t_n = n * float(pi) / log_lam
        if abs(t_n) < 0.01:
            t_n = 0.01
        tp = theta_prime(t_n)
        A[idx, idx] = 2 * tp / (2 * float(pi))

    v_hat_plus = np.zeros(dim, dtype=complex)
    v_hat_minus = np.zeros(dim, dtype=complex)
    for idx in range(dim):
        n = idx - N
        alpha = 0.5 + 2j * np.pi * n / L
        if abs(alpha) < 1e-15:
            v_hat_plus[idx] = lam ** (-0.5) * L
        else:
            v_hat_plus[idx] = lam ** (-0.5) * (np.exp(alpha * L) - 1) / alpha
        beta = -0.5 + 2j * np.pi * n / L
        if abs(beta) < 1e-15:
            v_hat_minus[idx] = lam ** (-0.5) * L
        else:
            v_hat_minus[idx] = lam ** (-0.5) * (np.exp(beta * L) - 1) / beta

    Pi = np.zeros((dim, dim), dtype=complex)
    for m in range(dim):
        for n in range(dim):
            Pi[m, n] = v_hat_plus[m] * np.conj(v_hat_minus[n])
    Pi = (Pi + Pi.conj().T) / 2
    Pi = Pi.real

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
                    phase_n_inv = -phase_n
                    contrib_inv = weight * np.exp(1j * phase_n_inv) * np.conj(integral_val)
                    P[m_idx, n_idx] += (contrib + contrib_inv)
            k += 1
        p = int(nextprime(p))
    P = (P + P.conj().T) / 2
    P = P.real
    return A, Pi, P


def project_even_sector(M, N):
    dim = 2 * N + 1
    even_dim = N + 1
    S = np.zeros((dim, even_dim))
    S[N, 0] = 1.0
    for k in range(1, N + 1):
        S[N + k, k] = 1.0 / np.sqrt(2)
        S[N - k, k] = 1.0 / np.sqrt(2)
    return S.T @ M @ S


def main():
    print("=" * 90)
    print("GAP CONVERGENCE VS N (Fourier truncation)")
    print("=" * 90)

    # Test at several lambda^2 values
    for lam_sq in [67, 163, 307, 499, 997]:
        print(f"\n--- lambda^2 = {lam_sq} ---")
        print(f"{'N':>4} | {'dim':>5} | {'gap(QW)':>10} | {'gap(QW_e)':>10} | {'||Pi||':>10} | {'||Pi_e||':>10} | {'gap(P_e)':>10} | {'ratio':>8}")
        print("-" * 85)

        for N in [6, 8, 10, 12, 15, 18, 22]:
            try:
                A, Pi, P = build_operators(lam_sq, N)
                QW = A + Pi - P
                QW = (QW + QW.T) / 2

                eigs = np.sort(np.linalg.eigvalsh(QW))
                gap_full = eigs[1] - eigs[0]

                # Even sector
                QW_e = project_even_sector(QW, N)
                P_e = project_even_sector(P, N)
                Pi_e = project_even_sector(Pi, N)

                eigs_qw_e = np.sort(np.linalg.eigvalsh(QW_e))
                gap_qw_e = eigs_qw_e[1] - eigs_qw_e[0]

                eigs_p_e = np.sort(np.linalg.eigvalsh(P_e))[::-1]
                gap_p_e = eigs_p_e[0] - eigs_p_e[1]

                pi_norm = np.linalg.norm(Pi, ord=2)
                pi_e_norm = np.linalg.norm(Pi_e, ord=2)

                A_e = project_even_sector(A, N)
                c = np.trace(A_e) / A_e.shape[0]
                a_nonscalar = np.linalg.norm(A_e - c * np.eye(A_e.shape[0]), ord=2)
                ratio = (pi_e_norm + a_nonscalar) / gap_p_e if gap_p_e > 1e-10 else float('inf')

                print(f"{N:>4} | {2*N+1:>5} | {gap_full:>10.4f} | {gap_qw_e:>10.4f} | {pi_norm:>10.3f} | {pi_e_norm:>10.3f} | {gap_p_e:>10.3f} | {ratio:>8.4f}")
            except Exception as e:
                print(f"{N:>4} | ERROR: {e}")


if __name__ == "__main__":
    main()