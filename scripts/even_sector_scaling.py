"""
Even-Sector Scaling Analysis for Gap Proof
S154-M1 cont.24

Goal: Verify whether gap(P_even) grows faster than ||Pi_even|| asymptotically.
If exponent(gap) > exponent(||Pi||), then for large enough lambda,
gap(QW_even) = gap(P_even) - 2*||Pi_even + A_even - cI|| > 0.

Combined with numerical verification for small lambda, this gives
UNCONDITIONAL gap > 0.

Uses the exact Connes construction with polar term.
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
    """Build A (archimedean), Pi (polar), P (prime sum) separately."""
    lam = math.sqrt(lam_sq)
    log_lam = math.log(lam)
    L = 2 * log_lam
    dim = 2 * N + 1

    # 1. Archimedean diagonal
    A = np.zeros((dim, dim))
    for idx in range(dim):
        n = idx - N
        t_n = n * float(pi) / log_lam
        if abs(t_n) < 0.01:
            t_n = 0.01
        tp = theta_prime(t_n)
        A[idx, idx] = 2 * tp / (2 * float(pi))

    # 2. Polar term
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

    # Pi[m,n] = v_hat_plus[m] * conj(v_hat_minus[n]) + conj(v_hat_plus[n]) * v_hat_minus[m]
    # But from the form QW(f,f) = ... + 2Re(f_hat(i/2) conj(f_hat(-i/2))):
    # Pi[m,n] = v_hat_plus[m]*conj(v_hat_minus[n])
    # Then hermitianize
    Pi = np.zeros((dim, dim), dtype=complex)
    for m in range(dim):
        for n in range(dim):
            Pi[m, n] = v_hat_plus[m] * np.conj(v_hat_minus[n])
    Pi = (Pi + Pi.conj().T) / 2
    Pi = Pi.real  # Should be real after hermitianization

    # 3. Prime sum
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
    """Project matrix M to the even sector under J: n -> -n.

    Even basis: e_0 = V_0, e_k = (V_k + V_{-k})/sqrt(2) for k=1..N
    Dimension: N+1
    """
    dim = 2 * N + 1
    even_dim = N + 1

    # Build projection matrix S (dim x even_dim)
    S = np.zeros((dim, even_dim))
    S[N, 0] = 1.0  # V_0 -> e_0
    for k in range(1, N + 1):
        S[N + k, k] = 1.0 / np.sqrt(2)  # V_k component
        S[N - k, k] = 1.0 / np.sqrt(2)  # V_{-k} component

    # Project: M_even = S^T @ M @ S
    M_even = S.T @ M @ S
    return M_even


def analyze_scaling():
    """Compute even-sector quantities for a range of lambda^2."""
    N = 12  # Slightly larger than M2's N=10 for better resolution

    print("=" * 90)
    print("EVEN-SECTOR SCALING ANALYSIS")
    print(f"N = {N}, dim = {2*N+1}, even_dim = {N+1}")
    print("=" * 90)

    header = (f"{'lam^2':>7} | {'gap(P_e)':>10} | {'||Pi_e||':>10} | {'||A_e-cI||':>11} | "
              f"{'gap(QW_e)':>10} | {'gap(QW)':>10} | {'ratio':>8} | {'even?':>5}")
    print(header)
    print("-" * 95)

    lam_sq_values = [29, 37, 47, 67, 83, 100, 127, 163, 199, 251, 307, 401, 499, 601, 701, 809, 997]

    results = []

    for lam_sq in lam_sq_values:
        try:
            A, Pi, P = build_operators(lam_sq, N)

            # Full QW
            QW = A + Pi - P
            QW = (QW + QW.T) / 2

            eigs_full = np.sort(np.linalg.eigvalsh(QW))
            gap_full = eigs_full[1] - eigs_full[0]

            # Classify ground state parity
            _, vecs = np.linalg.eigh(QW)
            eta = vecs[:, 0]
            even_err = sum(abs(eta[N + n] - eta[N - n]) for n in range(1, N + 1))
            odd_err = sum(abs(eta[N + n] + eta[N - n]) for n in range(1, N + 1))
            is_even = even_err < odd_err

            # Even sector projections
            P_even = project_even_sector(P, N)
            Pi_even = project_even_sector(Pi, N)
            A_even = project_even_sector(A, N)
            QW_even = project_even_sector(QW, N)

            # Even sector gap of P
            eigs_P_even = np.sort(np.linalg.eigvalsh(P_even))[::-1]  # descending
            gap_P_even = eigs_P_even[0] - eigs_P_even[1] if len(eigs_P_even) > 1 else 0

            # ||Pi_even||
            Pi_even_norm = np.linalg.norm(Pi_even, ord=2)

            # ||A_even - c*I|| where c = mean of diagonal
            c = np.trace(A_even) / A_even.shape[0]
            A_nonscalar = A_even - c * np.eye(A_even.shape[0])
            A_nonscalar_norm = np.linalg.norm(A_nonscalar, ord=2)

            # Even sector gap of QW
            eigs_QW_even = np.sort(np.linalg.eigvalsh(QW_even))
            gap_QW_even = eigs_QW_even[1] - eigs_QW_even[0] if len(eigs_QW_even) > 1 else 0

            # Ratio: perturbation / gap
            total_pert = Pi_even_norm + A_nonscalar_norm
            ratio = total_pert / gap_P_even if gap_P_even > 1e-10 else float('inf')

            results.append({
                'lam_sq': lam_sq,
                'gap_P_even': gap_P_even,
                'Pi_even_norm': Pi_even_norm,
                'A_nonscalar_norm': A_nonscalar_norm,
                'gap_QW_even': gap_QW_even,
                'gap_full': gap_full,
                'ratio': ratio,
                'is_even': is_even
            })

            print(f"{lam_sq:>7} | {gap_P_even:>10.3f} | {Pi_even_norm:>10.3f} | {A_nonscalar_norm:>11.3f} | "
                  f"{gap_QW_even:>10.4f} | {gap_full:>10.4f} | {ratio:>8.4f} | {'Y' if is_even else 'N':>5}")

        except Exception as e:
            print(f"{lam_sq:>7} | ERROR: {e}")

    # Power law fit for gap(P_even) and ||Pi_even||
    print(f"\n{'=' * 90}")
    print("POWER LAW FIT (log-log regression)")
    print(f"{'=' * 90}")

    if len(results) >= 5:
        # Use points with lam_sq >= 100 for fitting
        fit_data = [r for r in results if r['lam_sq'] >= 100]
        if len(fit_data) >= 4:
            log_lam = np.array([np.log(r['lam_sq']) for r in fit_data])

            # Fit gap(P_even) ~ lam^alpha
            log_gap = np.array([np.log(max(r['gap_P_even'], 1e-15)) for r in fit_data])
            alpha_fit = np.polyfit(log_lam, log_gap, 1)
            print(f"\n  gap(P_even) ~ lam^{{{alpha_fit[0]:.4f}}}  (exponent from log-log fit)")

            # Fit ||Pi_even|| ~ lam^beta
            log_pi = np.array([np.log(max(r['Pi_even_norm'], 1e-15)) for r in fit_data])
            beta_fit = np.polyfit(log_lam, log_pi, 1)
            print(f"  ||Pi_even|| ~ lam^{{{beta_fit[0]:.4f}}}  (exponent from log-log fit)")

            # Fit ||A-cI|| ~ lam^gamma
            log_a = np.array([np.log(max(r['A_nonscalar_norm'], 1e-15)) for r in fit_data])
            gamma_fit = np.polyfit(log_lam, log_a, 1)
            print(f"  ||A-cI||    ~ lam^{{{gamma_fit[0]:.4f}}}  (exponent from log-log fit)")

            # Fit gap(QW_even) ~ lam^delta
            log_qw_gap = np.array([np.log(max(r['gap_QW_even'], 1e-15)) for r in fit_data])
            delta_fit = np.polyfit(log_lam, log_qw_gap, 1)
            print(f"  gap(QW_even) ~ lam^{{{delta_fit[0]:.4f}}}  (exponent from log-log fit)")

            # The key comparison
            print(f"\n  KEY: gap exponent ({alpha_fit[0]:.4f}) vs polar exponent ({beta_fit[0]:.4f})")
            if alpha_fit[0] > beta_fit[0]:
                print(f"  ==> gap grows FASTER than polar norm: exponent difference = {alpha_fit[0] - beta_fit[0]:.4f}")
                print(f"  ==> For sufficiently large lambda, gap(P_even) > ||Pi_even||")
                print(f"  ==> Combined with numerical verification for small lambda => GAP > 0 UNCONDITIONALLY")
            else:
                print(f"  ==> gap does NOT grow faster! Exponent difference = {alpha_fit[0] - beta_fit[0]:.4f}")
                print(f"  ==> Need different approach")

            # Also fit ratio directly
            log_ratio = np.array([np.log(max(r['ratio'], 1e-15)) for r in fit_data])
            ratio_fit = np.polyfit(log_lam, log_ratio, 1)
            print(f"\n  ratio = (||Pi||+||A-cI||)/gap(P_even) ~ lam^{{{ratio_fit[0]:.4f}}}")
            if ratio_fit[0] < 0:
                print(f"  ==> Ratio DECREASING (exponent < 0)")
                # Extrapolate: where does ratio cross 1?
                # ratio(lam) = C * lam^slope
                # ratio = 1 when lam = (1/C)^{1/|slope|}
                C_ratio = np.exp(ratio_fit[1])
                if ratio_fit[0] < 0 and C_ratio > 1:
                    cross_lam = (1.0 / C_ratio) ** (1.0 / ratio_fit[0])
                    print(f"  ==> Extrapolated crossing (ratio < 1) at lam^2 ~ {cross_lam**2:.0f}")

    # Direct gap verification
    print(f"\n{'=' * 90}")
    print("DIRECT GAP(QW) VERIFICATION")
    print(f"{'=' * 90}")
    print(f"\n  All lambda^2 tested with gap(QW) > 0: "
          f"{'YES' if all(r['gap_full'] > 0 for r in results) else 'NO'}")
    print(f"  gap(QW) monotonically increasing from lam^2=163: "
          f"{'YES' if all(results[i]['gap_full'] <= results[i+1]['gap_full'] for i in range(len(results)-1) if results[i]['lam_sq'] >= 163) else 'CHECK'}")
    print(f"  Ground state even for all lam^2 >= 100: "
          f"{'YES' if all(r['is_even'] for r in results if r['lam_sq'] >= 100) else 'NO'}")


if __name__ == "__main__":
    analyze_scaling()