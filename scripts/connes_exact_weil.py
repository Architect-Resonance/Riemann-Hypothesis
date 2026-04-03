"""
Reproduce Connes' exact Weil quadratic form computation.
S154-M1 cont.21

Connes-Consani-Moscovici (2025), arXiv:2511.22755, eq. 3.7:

QW_lambda(f,f) = int |f_hat(t)|^2 * 2*theta'(t)/(2*pi) dt
                + 2*Re(f_hat(i/2) * conj(f_hat(-i/2)))
                - sum_{1 < n <= lambda^2} Lambda(n) <f|T(n)f>

where theta(t) = Riemann-Siegel angular function,
Lambda(n) = von Mangoldt function,
T(n) is the Hecke-type operator.

We build the matrix in the basis V_n(u) = exp(2*pi*i*n*log(lambda*u)/L)
where L = 2*log(lambda), restricted to |n| <= N.

Then: compare eigenvalues with zeta zeros.
Then: twist by chi_{-163} and compare.
"""

import numpy as np
from mpmath import mp, mpf, mpc, log, pi, euler, loggamma, im, re, cos, sin, exp, sqrt, fabs
from mpmath import mangoldt as mp_mangoldt

mp.dps = 50  # High precision like Connes

def riemann_siegel_theta(t):
    """Compute theta(t) = -t/2 * log(pi) + Im(log Gamma(1/4 + it/2))."""
    t = mpf(t)
    return -t/2 * log(pi) + im(loggamma(mpf('0.25') + mpc(0, t/2)))


def theta_prime(t):
    """Numerical derivative of theta(t)."""
    t = mpf(t)
    h = mpf('1e-10')
    return (riemann_siegel_theta(t + h) - riemann_siegel_theta(t - h)) / (2 * h)


def build_connes_matrix(lam, N, chi_func=None):
    """
    Build the Weil quadratic form matrix in the V_n basis.

    Parameters:
        lam: the cutoff parameter lambda (primes <= lambda^2 contribute)
        N: use basis functions V_n for |n| <= N (matrix size 2N+1)
        chi_func: optional function p -> chi(p) for twisting
    """
    L = 2 * float(log(lam))
    dim = 2 * N + 1

    # Basis: V_n(u) for n = -N, ..., N
    # In Fourier: V_hat_n(t) = delta(t - n*pi/log(lambda))
    # So <V_m | QW | V_n> has three contributions:

    QW = np.zeros((dim, dim), dtype=complex)

    # 1. Archimedean contribution:
    # <V_m|arch|V_n> = delta_{mn} * 2*theta'(n*pi/log(lam)) / (2*pi)
    log_lam = float(log(lam))
    for idx in range(dim):
        n = idx - N
        t_n = n * float(pi) / log_lam
        if abs(t_n) < 0.01:
            # theta'(0) = -log(pi)/2 + Re(psi(1/4))/2 where psi = digamma
            # Numerically: theta'(0) ~ -0.1856
            tp = float(theta_prime(mpf('0.01')))
        else:
            tp = float(theta_prime(mpf(str(t_n))))
        QW[idx, idx] += 2 * tp / (2 * float(pi))

    # 2. Polar contribution:
    # <V_m|polar|V_n> = 2*Re(V_hat_m(i/2) * conj(V_hat_n(-i/2)))
    # V_hat_n(s) = integral V_n(u) u^{-is} d*u
    #            = integral exp(2*pi*i*n*log(lam*u)/L) u^{-is} du/u
    #            = (on [lam^{-1}, lam]) this is a sinc-like integral
    # For the basis V_n: V_hat_n(t) concentrated at t = n*pi/log(lam)
    # V_hat_n(i/2) = integral_{lam^{-1}}^{lam} exp(2*pi*i*n*x/L) * exp(x/2) dx
    # where x = log(lam*u), u = lam^{-1}*exp(x), dx = du/u

    # Compute V_hat_n(i/2) for each n
    # V_hat_n(i/2) = integral_0^L exp(2*pi*i*n*x/L) * (lam^{-1}*exp(x))^{1/2} dx
    #              = lam^{-1/2} * integral_0^L exp(x/2 + 2*pi*i*n*x/L) dx
    #              = lam^{-1/2} * L * sinc-like
    v_hat_plus = np.zeros(dim, dtype=complex)
    v_hat_minus = np.zeros(dim, dtype=complex)

    for idx in range(dim):
        n = idx - N
        # V_hat_n(i/2) = lam^{-1/2} * int_0^L exp((1/2 + 2*pi*i*n/L)*x) dx
        alpha = 0.5 + 2j * np.pi * n / L
        if abs(alpha) < 1e-15:
            v_hat_plus[idx] = float(lam)**(-0.5) * L
        else:
            v_hat_plus[idx] = float(lam)**(-0.5) * (np.exp(alpha * L) - 1) / alpha

        # V_hat_n(-i/2) = lam^{-1/2} * int_0^L exp((-1/2 + 2*pi*i*n/L)*x) dx
        beta = -0.5 + 2j * np.pi * n / L
        if abs(beta) < 1e-15:
            v_hat_minus[idx] = float(lam)**(-0.5) * L
        else:
            v_hat_minus[idx] = float(lam)**(-0.5) * (np.exp(beta * L) - 1) / beta

    # Polar: QW[m,n] += 2*Re(v_hat_plus[m] * conj(v_hat_minus[n]))
    # But actually the form is QW(f,f) = ... + 2*Re(f_hat(i/2)*conj(f_hat(-i/2)))
    # For f = sum a_n V_n: f_hat(i/2) = sum a_n v_hat_plus[n]
    # So QW[m,n] += v_hat_plus[m]*conj(v_hat_minus[n]) + conj(v_hat_plus[n])*v_hat_minus[m]
    # (from the 2*Re)
    for m in range(dim):
        for n in range(dim):
            QW[m, n] += v_hat_plus[m] * np.conj(v_hat_minus[n])

    # 3. Prime sum:
    # QW[m,n] -= sum_{p^k <= lam^2} log(p) * p^{-k/2} * [V_m^* * V_n](p^k) + [V_m^* * V_n](p^{-k})
    # where [f^* * g](r) = integral f(u)^* g(ru) d*u (multiplicative convolution)
    # For V_m, V_n: [V_m^* * V_n](r) = integral exp(-2pi i m x/L) exp(2pi i n (x+log r)/L) dx * (1/L)
    #             = exp(2pi i n log(r)/L) * delta_{mn} * L  [if r = 1]
    # More generally: [V_m^* * V_n](p^k) = exp(2pi i n k log(p)/L) * integral exp(2pi i (n-m) x/L) dx / L
    #             = exp(2pi i n k log(p)/L) * delta_{mn}  [only if m=n]
    # Wait, this is wrong. Let me recompute.
    # <f|T(n)g> = n^{-1/2} * ((f^* * g)(n) + (f^* * g)(n^{-1}))
    # where (f^* * g)(r) = integral f(u)^* g(ru) d*u on [lam^{-1}, lam]
    # For V_m and V_n:
    # (V_m^* * V_n)(r) = integral_{max(lam^{-1}, lam^{-1}/r)}^{min(lam, lam/r)}
    #                    exp(-2pi i m log(lam*u)/L) * exp(2pi i n log(lam*ru)/L) d*u/u
    # = integral exp(2pi i (n-m) log(lam*u)/L + 2pi i n log(r)/L) d*u/u
    # = exp(2pi i n log(r)/L) * integral exp(2pi i (n-m) x/L) dx  [x = log(lam*u)]
    # The integral is over [0, L] intersected with [0, L - log(r)] (for r > 1)
    # For r = p^k with p^k <= lam^2: log(p^k) <= L, so the integration range is [0, L - k*log(p)]

    lam_sq = float(lam) ** 2

    # Iterate over prime powers
    from sympy import nextprime, isprime
    p = 2
    while p <= lam_sq:
        lp = float(log(p))
        chi_p = chi_func(p) if chi_func else 1

        k = 1
        while p ** k <= lam_sq:
            pk = p ** k
            lpk = k * lp
            weight = lp * pk ** (-0.5)

            if chi_func:
                weight *= chi_p ** k

            # Range of integration: [0, L - lpk] for T(p^k)
            # and [0, L - lpk] for T(p^{-k}) [by symmetry, same]
            overlap = max(0, L - lpk)

            if overlap <= 0:
                k += 1
                continue

            for m_idx in range(dim):
                for n_idx in range(dim):
                    m_val = m_idx - N
                    n_val = n_idx - N

                    # (V_m^* * V_n)(p^k) contribution
                    phase_n = 2 * np.pi * n_val * lpk / L
                    # Integral of exp(2pi i (n-m) x/L) over [0, overlap]
                    diff = n_val - m_val
                    if diff == 0:
                        integral_val = overlap / L
                    else:
                        arg = 2 * np.pi * diff * overlap / L
                        integral_val = (np.exp(1j * arg) - 1) / (2j * np.pi * diff) * (L / L)
                        # Correct: integral_0^{overlap} exp(2pi i diff x / L) dx / L
                        integral_val = (np.exp(1j * arg) - 1) / (2j * np.pi * diff / L) / L

                    contrib = weight * np.exp(1j * phase_n) * integral_val
                    # Add conjugate for T(p^{-k})
                    phase_n_inv = -2 * np.pi * n_val * lpk / L
                    contrib_inv = weight * np.exp(1j * phase_n_inv) * np.conj(integral_val)

                    QW[m_idx, n_idx] -= (contrib + contrib_inv)

            k += 1
        p = int(nextprime(p))

    # Make Hermitian
    QW = (QW + QW.conj().T) / 2

    return QW


def compare_with_zeta_zeros(lam, N):
    """Build QW, find eigenvalues, compare with zeta zeros."""
    print("=" * 70)
    print(f"CONNES' EXACT WEIL MATRIX: lambda={float(lam):.4f}, N={N}")
    print("=" * 70)

    QW = build_connes_matrix(lam, N)
    eigs = np.sort(np.linalg.eigvalsh(QW.real))  # Should be real for Hermitian

    print(f"\nMatrix size: {2*N+1} x {2*N+1}")
    print(f"Smallest 5 eigenvalues: {np.round(eigs[:5], 6)}")
    print(f"Spectral gap: {eigs[1]-eigs[0]:.6f}")

    # The eigenvalues of D_tilde (the spectral triple operator) correspond
    # to the zeros. We need the FULL operator, not just QW.
    # For now, just report the QW spectrum.

    # Also compute twisted version
    print(f"\n--- With chi_{{-163}} twist ---")

    def chi_163(p):
        if p == 2:
            r = (-163) % 8
            return {1: 1, 5: -1, 3: -1, 7: 1}.get(r, 0)
        if p == 163:
            return 0
        val = pow((-163) % p, (p - 1) // 2, p)
        return val if val <= 1 else -1

    QW_tw = build_connes_matrix(lam, N, chi_func=chi_163)
    eigs_tw = np.sort(np.linalg.eigvalsh(QW_tw.real))

    print(f"Smallest 5 eigenvalues: {np.round(eigs_tw[:5], 6)}")
    print(f"Spectral gap: {eigs_tw[1]-eigs_tw[0]:.6f}")
    print(f"Gap ratio (twisted/generic): {(eigs_tw[1]-eigs_tw[0])/(eigs[1]-eigs[0]):.3f}")

    # Check: is the ground state even (symmetric under u -> u^{-1})?
    _, vecs = np.linalg.eigh(QW.real)
    eta = vecs[:, 0]
    dim = len(eta)
    N_basis = (dim - 1) // 2
    # V_n(u^{-1}) = V_{-n}(u), so evenness means a_n = a_{-n}
    even_check = sum(abs(eta[N_basis + n] - eta[N_basis - n]) for n in range(1, N_basis + 1))
    print(f"\nGeneric ground state evenness: sum|a_n - a_{{-n}}| = {even_check:.6f}")

    _, vecs_tw = np.linalg.eigh(QW_tw.real)
    eta_tw = vecs_tw[:, 0]
    even_tw = sum(abs(eta_tw[N_basis + n] - eta_tw[N_basis - n]) for n in range(1, N_basis + 1))
    print(f"Twisted ground state evenness: sum|a_n - a_{{-n}}| = {even_tw:.6f}")


if __name__ == "__main__":
    # Start with lambda = sqrt(13) ~ 3.606 (primes <= 13)
    lam = mpf(13) ** mpf('0.5')

    # Small N first to verify
    for N in [5, 10, 20]:
        compare_with_zeta_zeros(lam, N)
        print()