"""
Test Antigravity's claim: [P, Pi] -> 0 as lambda -> infinity.
Also test: [P, Pi] / (r(P) * ||Pi||) -> 0 (normalized commutator).
S154-M1 cont.24
"""
import numpy as np
import math
from mpmath import mp, mpf, mpc, log, pi, im, loggamma
from sympy import nextprime
mp.dps = 20

def theta_prime(t):
    t = mpf(str(t))
    if abs(t) < 0.01: t = mpf('0.01')
    h = mpf('1e-10')
    theta = lambda x: -x/2*mp.log(mp.pi)+im(loggamma(mpf('0.25')+mpc(0,x/2)))
    return float((theta(t+h)-theta(t-h))/(2*h))

def build_operators(lam_sq, N):
    lam=math.sqrt(lam_sq); log_lam=math.log(lam); L=2*log_lam; dim=2*N+1
    A=np.zeros((dim,dim))
    for idx in range(dim):
        n=idx-N; t_n=n*float(pi)/log_lam
        if abs(t_n)<0.01: t_n=0.01
        A[idx,idx]=2*theta_prime(t_n)/(2*float(pi))
    v_p=np.zeros(dim,dtype=complex); v_m=np.zeros(dim,dtype=complex)
    for idx in range(dim):
        n=idx-N
        a=0.5+2j*np.pi*n/L
        v_p[idx]=lam**(-0.5)*(np.exp(a*L)-1)/a if abs(a)>1e-15 else lam**(-0.5)*L
        b=-0.5+2j*np.pi*n/L
        v_m[idx]=lam**(-0.5)*(np.exp(b*L)-1)/b if abs(b)>1e-15 else lam**(-0.5)*L
    Pi=np.zeros((dim,dim),dtype=complex)
    for m in range(dim):
        for n in range(dim): Pi[m,n]=v_p[m]*np.conj(v_m[n])
    Pi=(Pi+Pi.conj().T)/2; Pi=Pi.real
    P=np.zeros((dim,dim),dtype=complex)
    p=2
    while p<=lam_sq:
        lp=float(log(p)); k=1
        while p**k<=lam_sq:
            lpk=k*lp; weight=lp*(p**k)**(-0.5); overlap=max(0,L-lpk)
            if overlap<=0: k+=1; continue
            for mi in range(dim):
                for ni in range(dim):
                    mv=mi-N; nv=ni-N; phase=2*np.pi*nv*lpk/L; d=nv-mv
                    if d==0: iv=overlap/L
                    else:
                        arg=2*np.pi*d*overlap/L
                        iv=(np.exp(1j*arg)-1)/(2j*np.pi*d/L)/L
                    c1=weight*np.exp(1j*phase)*iv
                    c2=weight*np.exp(-1j*phase)*np.conj(iv)
                    P[mi,ni]+=(c1+c2)
            k+=1
        p=int(nextprime(p))
    P=(P+P.conj().T)/2; P=P.real
    return A, Pi, P

def project_even(M, N):
    dim=2*N+1; S=np.zeros((dim,N+1)); S[N,0]=1.0
    for k in range(1,N+1): S[N+k,k]=1/np.sqrt(2); S[N-k,k]=1/np.sqrt(2)
    return S.T@M@S

def main():
    N=15
    print("COMMUTATOR TEST: [P, Pi]")
    print(f"{'lam^2':>7} | {'||[P,Pi]||':>12} | {'r(P)*||Pi||':>12} | {'normalized':>12} | {'||[P,Pi]||/r(P)':>16}")
    print("-"*70)
    for lam_sq in [29, 67, 163, 499, 997, 2003, 5003]:
        A,Pi,P = build_operators(lam_sq, N)
        Pe=project_even(P,N); Pie=project_even(Pi,N)
        comm = Pe@Pie - Pie@Pe
        comm_norm = np.linalg.norm(comm, ord=2)
        rP = np.max(np.linalg.eigvalsh(Pe))
        pi_norm = np.linalg.norm(Pie, ord=2)
        normalized = comm_norm/(rP*pi_norm) if rP*pi_norm>0 else 0
        ratio_rP = comm_norm/rP if rP>0 else 0
        print(f"{lam_sq:>7} | {comm_norm:>12.4f} | {rP*pi_norm:>12.2f} | {normalized:>12.6f} | {ratio_rP:>16.6f}")

if __name__=="__main__": main()