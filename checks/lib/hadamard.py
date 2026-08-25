"""
Exact-arithmetic primitives for complex Hadamard matrices.  [D]

No floating point anywhere. Every predicate returns an exact verdict or raises.
Entries are sympy expressions; roots of unity stay symbolic through to the end.

  is_hadamard(H)      -- H H* = n I and every entry unimodular
  defect(H)           -- Tadej-Zyczkowski defect: 0 means isolated
  haagerup(H)         -- equivalence invariant; the adversarial track's discriminator

The defect and the Haagerup set are the two mechanical checks that carry most of
the classification's weight. If a claimed family has the wrong defect, the family
is wrong. If a candidate's Haagerup set is absent from the claimed list, the
classification is wrong.
"""

from itertools import combinations

import sympy as sp


# ---------------------------------------------------------------- construction

def root(k, n):
    """Primitive n-th root of unity to the k-th power, exact."""
    return sp.exp(2 * sp.pi * sp.I * sp.Rational(k, n))


def butson(exponents, n):
    """Butson-type matrix from a table of exponents over Z_n."""
    return sp.Matrix([[root(e, n) for e in row] for row in exponents])


def dephase(H):
    """Normalise so the first row and column are all ones. Equivalence-preserving."""
    H = sp.Matrix(H)
    n = H.rows
    H = sp.Matrix(n, n, lambda i, j: sp.simplify(H[i, j] / H[0, j]))
    H = sp.Matrix(n, n, lambda i, j: sp.simplify(H[i, j] / H[i, 0]))
    return H


# ------------------------------------------------------------------ predicates

def is_unimodular(H):
    H = sp.Matrix(H)
    for e in H:
        if sp.simplify(sp.Abs(e) ** 2 - 1) != 0:
            return False
    return True


def is_hadamard(H, n=None):
    """H H* = n I, exactly. Returns (verdict, residual) so failures are legible."""
    H = sp.Matrix(H)
    n = n or H.rows
    if not is_unimodular(H):
        return False, "non-unimodular entry"
    residual = (H * H.conjugate().T - n * sp.eye(n)).applyfunc(
        lambda e: sp.simplify(sp.expand_complex(e))
    )
    # NB: compare elementwise. sp.simplify() on a Matrix returns an immutable
    # matrix, and `immutable == sp.zeros(n, n)` is False even when every entry
    # is zero. That comparison silently failed both self-tests on first run.
    return all(e == 0 for e in residual), residual


# ---------------------------------------------------------------------- defect

def defect(H, verbose=False):
    """
    Tadej-Zyczkowski defect.

    Real solution space of
        sum_k H[j,k] conj(H[l,k]) (R[j,k] - R[l,k]) = 0   for all j < l
    minus the (2n-1)-dimensional trivial subspace from dephasing.

    d(H) = 0  <=>  H is isolated.
    Generic 6x6 families sit at d = 4; Tao's S6 is the isolated point.
    """
    H = sp.Matrix(H)
    n = H.rows
    rows = []

    for j, l in combinations(range(n), 2):
        re_row = [0] * (n * n)
        im_row = [0] * (n * n)
        for k in range(n):
            c = sp.expand(H[j, k] * sp.conjugate(H[l, k]))
            cr, ci = sp.simplify(sp.re(c)), sp.simplify(sp.im(c))
            re_row[j * n + k] += cr
            re_row[l * n + k] -= cr
            im_row[j * n + k] += ci
            im_row[l * n + k] -= ci
        rows.append(re_row)
        rows.append(im_row)

    M = sp.Matrix(rows)
    r = M.rank()
    dim = n * n - r
    d = dim - (2 * n - 1)

    if verbose:
        print(f"  system {M.rows}x{M.cols}  rank {r}  soln dim {dim}  defect {d}")
    return d


# ------------------------------------------------------- equivalence invariant

def haagerup(H):
    """
    Haagerup set: { H[i,j] H[k,l] conj(H[i,l]) conj(H[k,j]) }.

    Invariant under the full equivalence group (row/column permutations and
    unimodular diagonal scalings). Two matrices with different Haagerup sets are
    inequivalent -- this is the discriminator the counterexample track needs.

    Note the converse fails: equal Haagerup sets do NOT imply equivalence.
    A hit here is evidence, not proof.
    """
    H = sp.Matrix(H)
    n = H.rows
    out = set()
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for l in range(n):
                    v = sp.simplify(
                        H[i, j] * H[k, l] * sp.conjugate(H[i, l]) * sp.conjugate(H[k, j])
                    )
                    out.add(sp.nsimplify(v))
    return out


def inequivalent(H1, H2):
    """Sufficient (not necessary) inequivalence test via Haagerup sets."""
    return haagerup(H1) != haagerup(H2)


# ------------------------------------------------------------------- catalogue

def fourier(n):
    """F_n, the DFT matrix."""
    return sp.Matrix(n, n, lambda i, j: root(i * j, n))


def tao_S6():
    """Tao's isolated 6x6 matrix. Defect 0."""
    e = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 2, 2],
        [0, 1, 0, 2, 2, 1],
        [0, 1, 2, 0, 1, 2],
        [0, 2, 2, 1, 0, 1],
        [0, 2, 1, 2, 1, 0],
    ]
    return butson(e, 3)


# ------------------------------------------------------------------- self-test

if __name__ == "__main__":
    import sys

    failures = 0
    for name, H, expect in [("F6", fourier(6), 4), ("S6", tao_S6(), 0)]:
        ok, _ = is_hadamard(H)
        d = defect(H, verbose=True)
        good = ok and d == expect
        failures += 0 if good else 1
        print(f"{name}: hadamard={ok}  defect={d}  "
              f"{'OK' if good else f'MISMATCH (expected {expect})'}\n")

    ineq = inequivalent(fourier(6), tao_S6())
    print("F6 vs S6 inequivalent by Haagerup:", ineq)
    failures += 0 if ineq else 1

    sys.exit(1 if failures else 0)
