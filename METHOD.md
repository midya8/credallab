# CredalLab method and trust boundary

## 1. A finite logical universe

Input worlds are explicit indices. The model does not generate truth assignments, recover missing worlds or infer independence. An event is a sorted list of distinct world indices. If a logically possible world is absent, it has been excluded by the supplied model. This is an assumption, not a discovered fact.

Let `p` be nonnegative world masses with `1·p=1`. Each interval `lower <= P(E) <= upper` becomes two inequalities:

```
 indicator(E) · p <= upper
-indicator(E) · p <= -lower
```

The unconditional feasible set is a bounded polytope. All arithmetic is Python Fraction or normalized JavaScript BigInt numerator/denominator pairs. No decimal optimization occurs in either implementation.

## 2. Exact bounded enumeration

In `d` variables with one equality, enumerate all selections of `d-1` inequalities, solve the resulting square system by exact Gauss-Jordan elimination, discard singular or infeasible systems, and deduplicate feasible vertices. Retain every feasible active basis for dual recovery. Degenerate vertices may have many bases.

A linear objective attains its optimum at a vertex of this nonempty compact polytope. At an optimal vertex, the implementation searches its retained bases for a dual solution with nonnegative inequality multipliers. Failure to find a certificate raises an error; it does not emit an uncertified bound.

This enumerates candidate bases, not just vertices. The 20,000 candidate phase-I-basis cap limits a single enumeration, not total arithmetic, bit complexity, runtime or memory. Degenerate rational systems can still be slow. There is no scalability claim.

## 3. A consistency certificate, not an edit recommendation

Introduce one common slack `t` and solve:

```
maximize -t
subject to sum(p)=1, p>=0, 0<=t<=1
           event_row·p - t <= upper
          -event_row·p - t <= -lower
```

The relaxed problem is always feasible for valid intervals: `t=1` covers every assessment while keeping normalized nonnegative masses. Its optimum is nonpositive.

- Objective zero gives a compatible distribution for the original assessments.
- A strictly negative optimum proves no original compatible distribution exists.
- The reported minimum common relaxation is the negative of that objective.

This is a uniform additive relaxation of all assessment inequalities. It is not a minimum number of changed statements, a minimal inconsistent subset, a weighted repair, a calibrated noise model or a user-approved change to beliefs.

For the triangle control, the three event indicators sum to at most two in every supplied world. Requiring each probability to be one contradicts that inequality. The minimum slack is `1/3`; this special control has a short hand derivation as well as the general exact certificate.

## 4. Sharp event bounds

On a feasible original polytope, maximize the query indicator for its upper bound and maximize its negative for its lower bound. Do the same independently for the given event. Every endpoint carries an attaining distribution and a dual upper-bound certificate. These ranges are implied by supplied assumptions. They are not confidence intervals, samples, learned beliefs or estimates of frequency.

## 5. Conditional endpoints and zero events

Write `N(p)=P(query ∩ given)` and `G(p)=P(given)`. The query asks for `N(p)/G(p)` only when `G(p)>0`.

Every feasible distribution is a convex combination of vertices. Vertices with zero `G` also have zero `N`, because the numerator event is a subset of the denominator event. Thus for every positive-`G` mixture the ratio is a weighted average of the ratios at its positive-`G` vertices, using weights proportional to mixture weight times `G`. The minimum and maximum are attained at positive-`G` vertices whenever such vertices exist.

For a candidate lower ratio `r`, certify that `rG-N <= 0` over the entire original polytope, with a positive-`G` witness attaining zero. For an upper ratio, certify `N-rG <= 0` in the same way. These linear certificates cover even zero-`G` vertices, where both quantities vanish, and the positive witness proves attainment on the stated domain.

If the maximum possible `G` is zero, the conditional answer is null. If only the minimum `G` is zero, conditional bounds are still reported on the positive-mass domain and that restriction is shown separately. This is not de Finetti conditional coherence or a convention for assigning probabilities on null events. It does not accept conditional assessments as constraints.

The independent floating reference uses Charnes-Cooper: scale masses by reciprocal given-event mass, require `G(y)=1`, `sum(y)=s` and each original row `A y <= b s`, with `y,s>=0`. It optimizes the numerator in these transformed variables. Zero-denominator cases are handled before transformation. The native exact engine does not depend on this numerical reference.

## 6. Primal-dual certificate convention

Every certificate concerns `maximize c·x` subject to `h·x=1` and `A x<=b`. It supplies:

- the primal point `x`;
- a free equality multiplier `η`;
- nonnegative inequality multipliers `λ`;
- one claimed objective value.

Replay checks all dimensions and canonical rational pairs, then verifies:

```
h·x = 1
A x <= b
λ >= 0
c = η h + λ A
c·x = value = η + λ·b
```

Weak duality gives an upper bound for every feasible point; equality with a feasible witness proves optimality. Lower event certificates maximize the negated indicator, so their internal objective is the negative of the displayed lower probability. Conditional certificates have objective zero and require a positive given-event witness.

`credallab/certificate.py` imports the schema/matrix convention from `model.py`, not the engine, linear solver, basis enumeration or certificate generator. Replay accepts any valid witness, including nonvertex attainers, rather than requiring the generator's chosen point. Its trust boundary includes the Python interpreter, integer/Fraction arithmetic, shared input validation, shared matrix construction and checker implementation. It is not a formally verified proof kernel. An incorrect shared matrix convention could fool both generation and replay; the separately rebuilt HiGHS reference and hand-derived controls reduce, but do not eliminate, that risk.

A certificate validates the supplied input embedded in its report. It does not authenticate who supplied that input or prove that the input matches an external intended model. Users must compare the report input with the model they meant to analyze.

## 7. Strict schema and limits

Exactly these top-level input keys are required:

```json
{
  "version": 1,
  "worlds": 3,
  "constraints": [
    {"event": [0, 1], "lower": [1, 3], "upper": [2, 3]}
  ],
  "query": {"event": [0], "given": [0, 1]}
}
```

No extra keys, duplicate JSON object keys, floats, exponents, NaN or Infinity. Booleans are not integers. Input rationals are integers or `[numerator, positive_denominator]`; raw components and reduced components are limited to absolute numerator and denominator at most 1,000,000. Bounds satisfy `0 <= lower <= upper <= 1`, with a combined reduced-denominator LCM at most 1,000,000.

There are 1-6 worlds, at most six interval assessments, and `comb(worlds + 2*assessments + 2, worlds) <= 20000`. Thus not every six-world/six-assessment combination is accepted. Events must be sorted, distinct, valid indices; the empty event is allowed. Duplicate assessments are allowed within the limits and do not add independence assumptions.

The CLI accepts at most 65,536 input bytes and 8,388,608 report bytes. Browser input has the same UTF-8 input limit. Direct Python API calls do not impose serialized-byte limits. Report fractions are canonical positive-denominator pairs and may be larger than the input component bound, since exact elimination can enlarge integers. Byte limits are not a complete computational denial-of-service defense for adversarial reports. Do not expose this checker as an untrusted public server without stronger resource isolation.

`run`, `demo` and `verify` write compact JSON on success. Invalid input or a rejected report exits with status 2, writes an error to stderr, and emits no partial JSON on stdout. `verify` returns `{"valid":true}` only after every required certificate and report field passes.

## 8. Developed controls and checks

Sixteen original teaching controls cover the incompatible triangle, its boundary, unconstrained dependence, informative conditioning, vanishing and forced-zero denominators, fixed joint distributions, no assessments, empty/certain events, a single world, duplicate bounds, a tiny positive given-event mass and an impossible empty-event assessment. `tools/cases.py` adds deterministic developed cases. There is no held-out benchmark.

Native tests include exact expected controls, 120 full reports, 505 primitive mutations across three reports, valid alternate witnesses, strict parsing, import independence, world permutation, duplicate assessments and monotone tightening. Mutation coverage is finite, not an adversarial completeness claim. Actual Chrome checks the rendered tables against a separately reconstructed Fraction audit, the complete JSON, responsive states, stale clearing and trusted downloads. The browser solver and Python solver implement the same algorithm, so agreement is not an independent proof of the theory.

The optional SciPy 1.15.3 HiGHS check rebuilds LPs directly from model input and compares feasibility, common relaxation, event ranges and transformed conditional ranges at tolerance `1e-8`. It checks 690 LPs, including 138 conditional LPs, on the developed grid. A floating reference can miss distinctions below its tolerances. Its result is supporting evidence, not authority over exact certificates.

The installed-wheel check creates a fresh environment, removes PYTHONPATH, works outside the checkout, checks six installed module origins and exercises both console and module entry points on all controls, including forged-report rejection. CI runs native tests and wheel reproduction across Python 3.10-3.13, plus independent reference and actual Chrome jobs.

## 9. Classical sources and provenance

The code, controls and UI are original project work. The theory is classical:

1. [ISIPTA 1999 probability/coherence survey](https://isipta99.sipta.org/proc/041.pdf): finite probabilistic satisfiability, linear-programming formulations and distinctions around conditional coherence. This project deliberately implements the narrower unconditional finite-world constraints described above.
2. [Research paper on compatibility of marginal scenarios](https://ar5iv.labs.arxiv.org/html/1112.4788): compatible local assessments do not automatically imply a global joint model. Used as conceptual background, not a claim that this project implements its full framework.
3. [Stanford EE364a duality notes](https://web.stanford.edu/class/ee364a/lectures/duality.pdf): primal-dual bounds and certificates. The signs and normalized equality convention here are stated explicitly in section 6.
4. [UCLA linear-fractional programming notes](http://www.seas.ucla.edu/~vandenbe/ee236a/lectures/lfp.pdf): positive-denominator transformation used only in the optional independent numerical reference.
5. [Python Fraction documentation](https://docs.python.org/3/library/fractions.html): native exact rational representation.
6. [SciPy HiGHS documentation](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html): optional floating LP reference and solver tolerances.

No copied library solver, private dataset, empirical training data or paid API is included. This project does not claim to solve general continuous probability, implicit exponential truth spaces, graphical-model inference, conditional coherence on null events or large probabilistic satisfiability instances.
