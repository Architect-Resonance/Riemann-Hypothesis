"""
Test Antigravity's claim: <f, Pf> is bounded for f perp constant.
Compute max_{f perp eta} <f, P_even f> / <f,f> = sigma_2(P_even).
Also decompose: how much comes from diagonal vs off-diagonal of P?
S154-M1 cont.24
"""
import numpy as np, math
from mpmath import mp, mpf, mpc, log, pi, im, loggamma
from sympy import nextprime
mp.dps = 20

def theta_prime(t):
    t = mpf(str(t))
    if abs(t) < 0.01: t = mpf('0.01')
    h = mpf('1e-10')
    theta = lambda x: -x/2*mp.log(mp.pi)+im(loggamma(mpf('0.25')+mpc(0,x/2)))
    return float((theta(t+h)-theta(t-h))/(2*h))

def build_P(lam_sq, N):
    lam=math.sqrt(lam_sq); L=2*math.log(lam); dim=2*N+1
    P=np.zeros((dim,dim),dtype=complex)
    p=2
    while p<=lam_sq:
        lp=float(log(p)); k=1
        while p**k<=lam_sq:
            lpk=k*lp; w=lp*(p**k)**(-0.5); ov=max(0,L-lpk)
            if ov<=0: k+=1; continue
            for mi in range(dim):
                for ni in range(dim):
                    mv=mi-N; nv=ni-N; ph=2*np.pi*nv*lpk/L; d=nv-mv
                    if d==0: iv=ov/L
                    else: iv=(np.exp(1j*2*np.pi*d*ov/L)-1)/(2j*np.pi*d/L)/L
                    P[mi,ni]+=w*(np.exp(1j*ph)*iv+np.exp(-1j*ph)*np.conj(iv))
            k+=1
        p=int(nextprime(p))
    P=(P+P.conj().T)/2
    return P.real

def project_even(M, N):
    dim=2*N+1; S=np.zeros((dim,N+1)); S[N,0]=1.0
    for k in range(1,N+1): S[N+k,k]=1/np.sqrt(2); S[N-k,k]=1/np.sqrt(2)
    return S.T@M@S

def main():
    N = 15
    print("RAYLEIGH QUOTIENT DECOMPOSITION FOR f perp eta (PF eigenvector)")
    print("=" * 85)
    print(f"{'lam^2':>7} | {'sigma_2':>8} | {'<psi2|P_diag|psi2>':>20} | {'<psi2|P_offdiag|psi2>':>22} | {'sum':>8}")
    print("-" * 85)

    for lam_sq in [29, 67, 163, 499, 997, 2003, 5003]:
        P = build_P(lam_sq, N)
        Pe = project_even(P, N)

        eigs, vecs = np.linalg.eigh(Pe)
        # Eigenvalues are ascending; we want the largest (PF) and second largest
        idx = np.argsort(eigs)[::-1]
        eigs = eigs[idx]
        vecs = vecs[:, idx]

        r_P = eigs[0]
        sigma_2 = eigs[1]
        psi2 = vecs[:, 1]  # second eigenvector

        # Decompose <psi2 | P | psi2> into diagonal and off-diagonal
        diag_contrib = psi2 @ np.diag(np.diag(Pe)) @ psi2
        offdiag_contrib = psi2 @ (Pe - np.diag(np.diag(Pe))) @ psi2

        print(f"{lam_sq:>7} | {sigma_2:>8.4f} | {diag_contrib:>20.4f} | {offdiag_contrib:>22.4f} | {diag_contrib+offdiag_contrib:>8.4f}")

    print(f"\n{'=' * 85}")
    print("KEY: If sigma_2 stays bounded while diagonal contribution grows,")
    print("     the off-diagonal is actively SUPPRESSING the second eigenvalue.")

if __name__ == "__main__": main()