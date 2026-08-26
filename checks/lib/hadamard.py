"""
Exact-arithmetic primitives for complex Hadamard matrices.  [D]

No floating point anywhere. Every predicate returns an exact verdict or raises.
Entries are sympy expressions; roots of unity stay symbolic through to the end.

Three things live here:

  is_hadamard(H)      -- H H* = n I and every entry unimodular
  defect(H)           -- Tadej-Zyczkowski defect: 0 means isolated
  haagerup(H)         -- equivalence invariant; the adversarial track's discriminator

The defect and the Haagerup set are the two mechanical checks that carry most of
the classification's weight. If a claimed family has the wrong defect, the family
is wrong. If a candidate's Haagerup set is absent from the claimed list, the
classification is wrong.

is_hadamard() and defect() are three-valued. Each runs a sound field-coordinate
path (exact algebraic-field arithmetic, no simplify) alongside the original
simplify-based computation, kept only as a cross-check. The sound path is
authoritative whenever it decides; a disagreement between the two is printed
loudly to stderr, never resolved silently, and the sound value always wins
(slag/harness-defects.md H6-H4). When the sound path's field construction
itself fails, the verdict is the UNDECIDED sentinel -- never False, never a
guessed int -- because a lib verdict of "not Hadamard" is a MECH refutation
of the paper under adjudication, and this predicate must not manufacture one
by accident (slag/harness-defects.md H6-H5). See checks/README.md: a MECH
node that observes UNDECIDED is exit 2 (reclassify ARG), never exit 1
(refuted).
"""

import signal
import sys
from itertools import combinations

import sympy as sp
from sympy.polys.matrices import DomainMatrix


# -------------------------------------------------------------- verdict values

class _Undecided:
    """Falsy sentinel: neither path reached a decided verdict. Deliberately
    falsy (unlike a truthy string would be) so legacy code that still treats
    a verdict as a bare bool degrades toward "not confirmed", never toward a
    silent pass. Deliberately compares unequal to True, False, and every int
    (no __eq__ override -- falls back to identity), so `defect(H) == 4`-style
    and `verdict == True`-style comparisons already in use elsewhere stay
    correctly False rather than accidentally matching. See
    slag/harness-defects.md H6-H4, H6-H5."""

    def __bool__(self):
        return False

    def __repr__(self):
        return "UNDECIDED"


UNDECIDED = _Undecided()
TRUE, FALSE = True, False


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


# ------------------------------------------------ field coordinates (sound path)
#
# Adapted -- not imported -- from counterexample/lib/numfield.py and
# counterexample/lib/invariants.py::is_hadamard_K (Track B's files, read-only
# reference; never imported here, since checks/lib/ must not runtime-couple to
# counterexample/ while Track B may still be writing to it).
#
# Hardened relative to the original: numfield.py's degree-budget check fires
# *after* the (potentially unbounded) sp.QQ.algebraic_field(...) call, which
# can hang rather than escalate given enough independent algebraic generators.
# The first fix attempted here was a cheap pre-check -- reject upfront if the
# PRODUCT of each generator's own minimal-polynomial degree exceeds budget --
# but measurement during implementation showed that estimate is not just
# imprecise, it is actively backwards: B6(2*pi/3)'s 12 generators produce a
# naive product estimate of 65536, yet all 12 are algebraically related and
# the actual compositum has degree 4 (built in well under a second) -- the
# estimate would have escalated the exact motivating H6-H5 case. Conversely,
# 6 genuinely independent quadratic surds (degree 64, exactly at budget) took
# over 45s to even attempt, while 5 of them (degree 32) took 0.4s -- cost here
# tracks wall-clock time, not the resulting degree or any product of input
# degrees. So the guard is a wall-clock timeout around the actual
# construction call (the only thing that reliably correlates with the real
# cost, confirmed directly), not a degree estimate.

_DEGREE_BUDGET = 64
_FIELD_BUILD_TIMEOUT_SECONDS = 20
_field_cache = {}


class _EscalateError(Exception):
    """Field construction failed, timed out, or is too large; caller must
    degrade to UNDECIDED, never guess. Private: callers should trust
    is_hadamard()'s and defect()'s UNDECIDED contract rather than catching
    this directly."""


def _re_im(e):
    x, y = sp.expand_complex(e).as_real_imag()
    return sp.expand(x), sp.expand(y)


def _build_algebraic_field(gens):
    """sp.QQ.algebraic_field(*gens), bounded by a wall-clock timeout instead
    of a degree estimate (see module-level note above for why the estimate
    doesn't work). SIGALRM-based: only fires in the main thread of the main
    interpreter on a Unix-like OS, which matches how these check scripts
    actually run (standalone `python3 checks/*.py`); anywhere else, this is
    best-effort with no timeout rather than a hard failure."""
    if not hasattr(signal, "SIGALRM"):
        return sp.QQ.algebraic_field(*gens)

    def _on_timeout(signum, frame):
        raise _EscalateError(
            f"field construction exceeded {_FIELD_BUILD_TIMEOUT_SECONDS}s for "
            f"{len(gens)} generator(s) -- refusing to wait longer"
        )

    try:
        previous = signal.signal(signal.SIGALRM, _on_timeout)
    except ValueError:
        return sp.QQ.algebraic_field(*gens)   # not the main thread; best effort

    try:
        signal.alarm(_FIELD_BUILD_TIMEOUT_SECONDS)
        return sp.QQ.algebraic_field(*gens)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def _real_field_for(entries):
    """QQ.algebraic_field containing re/im of every entry, degree-budgeted
    and wall-clock-bounded. Raises _EscalateError (never a raw sympy
    exception, never an unbounded hang) on any failure."""
    gens, seen = [], set()
    for e in entries:
        for part in _re_im(e):
            if part.is_Rational:
                continue
            key = sp.srepr(part)
            if key not in seen:
                seen.add(key)
                gens.append(part)
    if not gens:
        return sp.QQ
    gkey = tuple(sorted(sp.srepr(g) for g in gens))
    if gkey in _field_cache:
        return _field_cache[gkey]

    try:
        K = _build_algebraic_field(gens)
    except _EscalateError:
        raise
    except Exception as exc:
        raise _EscalateError(f"algebraic_field construction failed: {exc}") from exc
    if K.mod.degree() > _DEGREE_BUDGET:
        raise _EscalateError(f"field degree {K.mod.degree()} exceeds budget {_DEGREE_BUDGET}")
    _field_cache[gkey] = K
    return K


def _to_K(K, expr):
    try:
        return K.from_sympy(expr)
    except Exception as exc:
        raise _EscalateError(f"cannot embed {expr} in field: {exc}") from exc


def _entry_pairs(H, K=None):
    """(K, n x n list of (x, y) K-element pairs) for a sympy matrix."""
    H = sp.Matrix(H)
    if K is None:
        K = _real_field_for(list(H))
    pairs = []
    for i in range(H.rows):
        row = []
        for j in range(H.cols):
            x, y = _re_im(H[i, j])
            row.append((_to_K(K, x), _to_K(K, y)))
        pairs.append(row)
    return K, pairs


# ------------------------------------------------------------------ predicates

def is_unimodular(H):
    H = sp.Matrix(H)
    for e in H:
        if sp.simplify(sp.Abs(e) ** 2 - 1) != 0:
            return False
    return True


def _sound_is_hadamard(H):
    """Exact Hadamard check in field coordinates: no simplify anywhere, so
    equality is exact once the field is built. Raises _EscalateError if the
    field can't be built -- the caller must treat that as UNDECIDED, never
    False. No `n` parameter: H H* = nI only makes sense for square H, so n is
    always H.rows here (unlike is_hadamard()'s heuristic cross-check, which
    keeps the original n override for backward compatibility even though
    nothing in the repo calls it non-default). Adapted from
    counterexample/lib/invariants.py::is_hadamard_K."""
    H = sp.Matrix(H)
    n = H.rows
    K, pairs = _entry_pairs(H)
    one, zero = K.one, K.zero
    for i in range(n):
        for j in range(n):
            x, y = pairs[i][j]
            if x * x + y * y != one:
                return False, f"entry ({i},{j}) not unimodular"
    for j in range(n):
        for l in range(j + 1, n):
            sx = zero
            sy = zero
            for k in range(n):
                a, b = pairs[j][k]
                c, d = pairs[l][k]
                sx += a * c + b * d
                sy += b * c - a * d
            if sx != zero or sy != zero:
                return False, f"rows {j},{l} not orthogonal"
    return True, "ok"


def _heuristic_is_hadamard(H, n):
    """Today's original is_hadamard: Gram residual decided by sp.simplify.
    Kept only as a cross-check -- this is the predicate H6-H5 found unsound
    (a true zero that simplify fails to normalize reads as nonzero). Never
    authoritative; see is_hadamard()."""
    if not is_unimodular(H):
        return False, "non-unimodular entry"
    residual = (H * H.conjugate().T - n * sp.eye(n)).applyfunc(
        lambda e: sp.simplify(sp.expand_complex(e))
    )
    # NB: compare elementwise. sp.simplify() on a Matrix returns an immutable
    # matrix, and `immutable == sp.zeros(n, n)` is False even when every entry
    # is zero. That comparison silently failed both self-tests on first run.
    return all(e == 0 for e in residual), residual


def is_hadamard(H, n=None):
    """H H* = n I, exactly. Returns (verdict, residual): verdict is True,
    False, or UNDECIDED -- never a bare bool masking an undecidable case.

    Runs both the sound field-coordinate path and the original heuristic
    path on every call. The sound path is authoritative whenever it decides;
    a disagreement with the heuristic is printed loudly to stderr and the
    sound verdict wins regardless -- never a silent tiebreak
    (slag/harness-defects.md H6-H4 protocol). If the sound path's field
    construction fails for any reason, the verdict is UNDECIDED regardless
    of what the heuristic says (slag/harness-defects.md H6-H5: UNDECIDED
    must never silently become False).
    """
    H = sp.Matrix(H)
    n = n or H.rows

    try:
        ok_sound, why_sound = _sound_is_hadamard(H)
        sound_exc = None
    except Exception as exc:
        ok_sound = why_sound = None
        sound_exc = exc

    try:
        ok_heur, why_heur = _heuristic_is_hadamard(H, n)
        heur_exc = None
    except Exception as exc:
        ok_heur = why_heur = None
        heur_exc = exc

    if sound_exc is not None:
        reason = f"sound path escalated: {sound_exc}"
        if heur_exc is not None:
            reason += f"; heuristic also failed: {heur_exc}"
        else:
            reason += f"; heuristic said {ok_heur} ({why_heur}) -- not authoritative"
        return UNDECIDED, reason

    if heur_exc is None and ok_heur != ok_sound:
        print(
            f"LOUD: is_hadamard disagreement -- sound={ok_sound} "
            f"heuristic={ok_heur} ({why_heur}); sound wins "
            f"(see slag/harness-defects.md H6-H5)",
            file=sys.stderr,
        )
        why_sound = f"{why_sound} [LOUD: heuristic disagreed, see stderr, H6-H5]"

    return ok_sound, why_sound


# ---------------------------------------------------------------------- defect

def _defect_system_K(K, pairs, n):
    """The Tadej-Zyczkowski system, entries in K. Same construction as
    _heuristic_defect's symbolic version below, but exact ring arithmetic
    over K -- no simplify, no heuristic zero test."""
    zero = K.zero
    rows = []
    for j, l in combinations(range(n), 2):
        re_row = [zero] * (n * n)
        im_row = [zero] * (n * n)
        for k in range(n):
            a, b = pairs[j][k]
            c, d = pairs[l][k]
            cr = a * c + b * d          # Re((a+bi)(c-di))
            ci = b * c - a * d          # Im((a+bi)(c-di))
            re_row[j * n + k] += cr
            re_row[l * n + k] -= cr
            im_row[j * n + k] += ci
            im_row[l * n + k] -= ci
        rows.append(re_row)
        rows.append(im_row)
    return rows


def _sound_defect(H):
    """Exact defect via DomainMatrix rank over an explicit real algebraic
    field. Raises _EscalateError if the field can't be built. Adapted from
    counterexample/lib/numfield.py::fast_defect / defect_system."""
    H = sp.Matrix(H)
    n = H.rows
    K, pairs = _entry_pairs(H)
    rows = _defect_system_K(K, pairs, n)
    dm = DomainMatrix(rows, (len(rows), n * n), K)
    r = dm.rank()
    d = (n * n - r) - (2 * n - 1)
    return d, r


def _heuristic_defect(H):
    """Today's original defect: symbolic rank via sp.simplify + Matrix.rank().
    Kept only as a cross-check per H6-H4 -- pivot-zero decisions inside
    Matrix.rank() are heuristic. Never authoritative; see defect()."""
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
    return d, r


def defect(H, verbose=False, return_detail=False):
    """
    Tadej-Zyczkowski defect. Returns a bare int when decided -- backward
    compatible with every existing `defect(H) == k` caller -- or the
    UNDECIDED sentinel when the sound path can't decide. UNDECIDED never
    compares equal to any int, so old callers stay safe.

    Real solution space of
        sum_k H[j,k] conj(H[l,k]) (R[j,k] - R[l,k]) = 0   for all j < l
    minus the (2n-1)-dimensional trivial subspace from dephasing.

    d(H) = 0  ==>  H is isolated. The CONVERSE IS NOT A THEOREM (H6-H3):
    d(H) = 4 does NOT certify that a continuum passes through H. Known generic
    6x6 families happen to sit at d = 4; Tao's S6 is the isolated point.

    Runs both paths on every call, same discipline as is_hadamard() (H6-H4).
    The sound path (DomainMatrix rank over an explicit algebraic field) is
    authoritative. The original simplify-based rank is kept as a
    cross-check; a disagreement is printed loudly to stderr and the sound
    value wins, never a silent tiebreak. return_detail=True additionally
    returns a dict with both paths' (defect, rank, error) and an `agree`
    flag -- used by the self-test to check both paths' ranks explicitly.
    """
    H = sp.Matrix(H)

    try:
        d_sound, r_sound = _sound_defect(H)
        sound_exc = None
    except Exception as exc:
        d_sound = r_sound = None
        sound_exc = exc

    try:
        d_heur, r_heur = _heuristic_defect(H)
        heur_exc = None
    except Exception as exc:
        d_heur = r_heur = None
        heur_exc = exc

    agree = None
    if sound_exc is None and heur_exc is None:
        agree = d_sound == d_heur
        if not agree:
            print(
                f"LOUD: defect disagreement -- sound={d_sound} (rank {r_sound}) "
                f"heuristic={d_heur} (rank {r_heur}); sound wins "
                f"(see slag/harness-defects.md H6-H4)",
                file=sys.stderr,
            )

    if verbose:
        sound_note = "ok" if sound_exc is None else f"ESCALATED: {sound_exc}"
        heur_note = "ok" if heur_exc is None else f"FAILED: {heur_exc}"
        print(f"  sound:     rank {r_sound}  defect {d_sound}  [{sound_note}]")
        print(f"  heuristic: rank {r_heur}  defect {d_heur}  [{heur_note}]")

    value = UNDECIDED if sound_exc is not None else d_sound
    if not return_detail:
        return value

    detail = {
        "sound": {"defect": d_sound, "rank": r_sound,
                  "error": None if sound_exc is None else str(sound_exc)},
        "heuristic": {"defect": d_heur, "rank": r_heur,
                      "error": None if heur_exc is None else str(heur_exc)},
        "agree": agree,
    }
    return value, detail


# ------------------------------------------------------- equivalence invariant

def haagerup(H):
    """
    Haagerup set: { H[i,j] H[k,l] conj(H[i,l]) conj(H[k,j]) }.

    Invariant under the full equivalence group (row/column permutations and
    unimodular diagonal scalings).

    !! H6-H1 -- UNSOUND AS A CROSS-MATRIX DISCRIMINATOR AS WRITTEN.
    This returns a Python set of sympy expressions, so equality between two
    matrices' sets compares SPELLINGS, not numbers. exp(2*pi*I/3) and
    (-1+I*sqrt(3))/2 are the same number and compare unequal; haagerup(C6)
    returns 16 values with mixed radical spellings. Comparing raw sets can
    therefore report equivalent matrices as inequivalent -- a false positive in
    the direction that matters. Use canonical labels (normalized minimal
    polynomial + isolating box) before comparing across matrices.

    !! H6-H2 -- BLIND TO TRANSPOSE AND CONJUGATION. The defining quadruple is
    invariant under H -> H^T and H -> conj(H) by index bijection, so this cannot
    separate F6 from F6^T. Four-variant checks must rest on fingerprint
    multiplicities, defect, and an equivalence decider instead.

    Converse also fails: equal sets do NOT imply equivalence.
    See slag/harness-defects.md. Behavior deliberately unchanged while tracks
    are running against this file.
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


def B6_y(y):
    """Beauchamp-Nicoara self-adjoint family at y = exp(i theta), exact y.
    [BN] math/0609076v1. The H6-H5 witness is B6(2*pi/3), i.e. y = root(1, 3).

    Ported from checks/lib/catalogue.py::B6_y rather than imported:
    catalogue.py does `from hadamard import fourier, tao_S6`, so the reverse
    import would be circular.

    sqrt(1+2y+2y^3+y^4) is rewritten as y*sqrt(y^-2+2/y+2y+y^2) -- the inner
    argument is real for |y| = 1 (sum of conjugate pairs), which keeps all
    entries in a radical real/imag-splittable field.
    """
    r = sp.expand(y ** -2 + 2 / y + 2 * y + y ** 2)
    num = 1 + 2 * y + y ** 2 - sp.sqrt(2) * y * sp.sqrt(r)
    x = num / (1 + 2 * y - y ** 2)
    t = num / (-1 + 2 * y + y ** 2)
    z = (1 + 2 * y - y ** 2) / (y * (-1 + 2 * y + y ** 2))
    xb, yb, zb, tb = (sp.conjugate(v) for v in (x, y, z, t))
    return sp.Matrix([
        [1,  1,   1,   1,   1,   1],
        [1, -1,  xb, -y, -xb,   y],
        [1,  x,  -1,   t,  -t,  -x],
        [1, -yb, tb,  -1,  yb, -tb],
        [1, -x, -tb,   y,   1,  zb],
        [1,  yb, -xb, -t,   z,   1],
    ])


def B6(theta):
    """B6 at the given exact theta (e.g. 2*sp.pi/3, the H6-H5 witness)."""
    return B6_y(sp.exp(sp.I * theta))


# ------------------------------------------------------------------- self-test

def scramble(H, rp, cp, dph, eph, q=12):
    """Apply a fixed (non-random) row permutation rp, column permutation cp,
    and two diagonal unimodular phase scalings dph, eph (multiples of
    2*pi/q), to H. Equivalence-preserving: used for the self-test's identity
    round trips. Ported verbatim from counterexample/selftest.py."""
    H = sp.Matrix(H)
    z = lambda k: sp.exp(2 * sp.pi * sp.I * sp.Rational(k, q))
    n = H.rows
    D1 = sp.diag(*[z(k) for k in dph])
    D2 = sp.diag(*[z(k) for k in eph])
    P1 = sp.zeros(n, n)
    P2 = sp.zeros(n, n)
    for i, r in enumerate(rp):
        P1[i, r] = 1
    for j, c in enumerate(cp):
        P2[c, j] = 1
    return D1 * P1 * H * P2 * D2


if __name__ == "__main__":
    _FAILURES = []

    def _check(name, ok, detail=""):
        status = "OK  " if ok else "FAIL"
        print(f"{status} {name}" + (f" -- {detail}" if detail and not ok else ""))
        if not ok:
            _FAILURES.append(name)

    F6, S6 = fourier(6), tao_S6()

    # Ground truth first (README.md: "F6 defect 4, S6 defect 0, before
    # anything else"), now via both paths -- the anchor this file has always
    # claimed to check, but the both-paths ranks are new (H6-H4).
    dF, detF = defect(F6, verbose=True, return_detail=True)
    _check("F6 defect == 4", dF == 4)
    _check("F6 sound rank == 21", detF["sound"]["rank"] == 21)
    _check("F6 heuristic rank == 21", detF["heuristic"]["rank"] == 21)

    dS, detS = defect(S6, verbose=True, return_detail=True)
    _check("S6 defect == 0", dS == 0)
    _check("S6 sound rank == 25", detS["sound"]["rank"] == 25)
    _check("S6 heuristic rank == 25", detS["heuristic"]["rank"] == 25)

    okF, _ = is_hadamard(F6)
    okS, _ = is_hadamard(S6)
    _check("F6 is_hadamard", okF is True)
    _check("S6 is_hadamard", okS is True)

    # H6-H5 identity anchor: the literal witness lib is_hadamard() used to
    # get wrong (heuristic path said False; two independent sound methods
    # said True). Must now certify TRUE.
    b6 = B6(2 * sp.pi / 3)
    okB, whyB = is_hadamard(b6)
    _check("B6(2pi/3) is_hadamard == TRUE (was FALSE, H6-H5)", okB is True, whyB)
    _check("B6(2pi/3) defect == 4", defect(b6) == 4)

    # Identity anchors: monomial-scramble round trips. This is the gap that
    # let H6-H1..H6-H3 through -- a self-test built only from distinctness
    # anchors cannot catch a soundness bug in an equality/decision predicate.
    for name, H, args in [
        ("F6", F6, ([3, 0, 5, 1, 4, 2], [2, 4, 0, 5, 3, 1], [1, 7, 2, 11, 5, 0], [3, 0, 9, 4, 8, 6])),
        ("S6", S6, ([2, 5, 1, 0, 3, 4], [4, 1, 3, 2, 0, 5], [0, 2, 4, 6, 8, 10], [5, 3, 1, 11, 9, 7])),
    ]:
        M = scramble(H, *args)
        okM, whyM = is_hadamard(M)
        _check(f"{name} scramble: is_hadamard still TRUE", okM is True, whyM)
        _check(f"{name} scramble: defect invariant", defect(M) == defect(H))

    # Out of scope for this fix (haagerup() is H6-H1/H2/H3, untouched); keep
    # the existing anchor, now wired into the same pass/fail gate instead of
    # a bare print with no verdict.
    _check("F6 vs S6 inequivalent by Haagerup", inequivalent(F6, S6))

    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} FAILURE(S): {', '.join(_FAILURES)}")
        sys.exit(1)
    print("ALL SELF-TEST CHECKS PASSED")
    sys.exit(0)
