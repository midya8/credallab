# One belief, different decision rules

CredalLab 0.2 adds one-shot decisions over the same supplied finite probability polytope as the probability inspector. It compares classical criteria. It does not choose a criterion, learn preferences, recommend a financial action or implement sequential decisions. Utilities share a state-independent cardinal scale; larger is better.

## A declared menu

```json
{"version":1,"worlds":2,"constraints":[],"utilities":[[3,0],[0,3],[1,1]]}
```

Each utility row is one action. Each column is one explicit world. One probability distribution must apply to every action. Assessments use the original unconditional interval schema. Utility entries are signed integers or `[numerator,denominator]`, not JSON decimal numbers.

```sh
credallab decisions examples/decisions/maximal_never_best.json > decisions.json
credallab verify-decisions decisions.json
python -m credallab demo-decisions > decisions.json
```

```python
from credallab import analyze_decisions, verify_decisions
r = analyze_decisions({"version": 1, "worlds": 2, "constraints": [],
                       "utilities": [[3, 0], [0, 3], [1, 1]]})
assert verify_decisions(r)
assert r["choices"]["e_admissible"] == [0, 1]
assert r["choices"]["maximal"] == [0, 1, 2]
assert r["actions"][2]["exclusion"]["guaranteed_advantage"] == [1, 2]
```

Serve `docs/` and open `decisions.html`. Native and browser implementations produce identical complete exact reports over the developed grid. Every report contains its input, feasibility proof, all action bounds, every ordered-pair lower difference, all shared-belief margin proofs, exclusion mixtures when needed, and the resulting choice sets. An infeasible probability model returns no choice set, not vacuous decision conclusions.

## Exact conventions

Let `K = {p : A p <= b, 1·p = 1}` include all nonnegativity constraints. Define `L(v) = min[p in K] p·v` and `U(v) = max[p in K] p·v`. For a nonempty `K`:

| Field | Rule, with all ties retained |
|---|---|
| `e_admissible` | There exists one `p in K` such that `p·u_i >= p·u_j` for every action `j` |
| `maximal` | There is no pure rival `j` with `L(u_j - u_i) > 0` |
| `interval_undominated` | There is no pure rival `j` with `L(u_j) > U(u_i)` |
| `gamma_maximin` | Pure actions attaining the largest `L(u_i)` |
| `gamma_maximax` | Pure actions attaining the largest `U(u_i)` |

This follows the strict lower-expectation convention in Nakharutai, Troffaes and Caiado (2019), Definitions 2-5. There is **no pointwise-admissibility prefilter**. Some older presentations, including the 2007 comparison paper, restrict decision sets by pointwise admissibility first; those reported sets can differ at boundaries. A rival that is weakly better everywhere but tied at an allowed zero-mass boundary does not strictly dominate here. In `strict_endpoint_tie`, `(1,0)` and `(0,0)` both remain E-admissible and maximal because `p=(0,1)` ties them. This is deliberate, not numerical tolerance.

With these definitions, `E-admissible ⊆ maximal ⊆ interval-undominated`. The proof is direct: a common best belief defends each pair; a rival's lower expectation above an action's upper implies positive lower pairwise difference. Maximin is not a substitute for E-admissibility. It can select a pure action that is never best against the entire menu. No mixed-action maximin optimization is performed.

## Why pairwise defenses are insufficient

For the declared menu `(3,0), (0,3), (1,1)`, let the first-world probability be `t`. Expectations are `3t`, `3(1-t)`, and `1`. The third action can defend itself against the first at `t=0`, and against the second at `t=1`. But to beat both simultaneously it would need `t<=1/3` and `t>=2/3`. There is no such belief.

Its best shared-belief margin is `-1/2`, attained at `t=1/2`. A half-and-half randomization over the first two actions has utility `3/2` in each world, beating the third by `1/2` everywhere. Nevertheless, the third is the unique **pure-action** maximin choice: its lower utility is `1`, while each other pure action has lower utility `0`. These statements ask different questions.

Change the third action to `(3/2,3/2)` and it is E-admissible only at the interior belief `t=1/2`. Testing only vertices of the original credal set would miss it. The margin LP adds the menu comparisons and finds the new intersection.

## The shared-belief margin LP

For each selected action `i`, maximize `z` subject to:

```text
A p <= b
1·p = 1
z <= p·(u_i-u_j)    for every j, including i
```

`z` is free below. It is not a probability or nonnegative variable. Including self gives `z<=0`. The optimum is zero exactly when the action is E-admissible, including ties. A negative optimum certifies exclusion. The polyhedron is unbounded downward in `z`, but its objective is bounded above and attained: `K` is nonempty compact, and the objective equals the maximum over `K` of a continuous minimum of finitely many utility differences. The polyhedron is pointed because its `p` recession direction must be zero and only downward `z` remains; an optimal vertex exists. The finite exact enumerator checks candidate active sets of the equality and inequalities. This is exponential enumeration, not a new efficient decision algorithm.

## Replaying the proof without solving again

Every certificate uses the existing maximization convention:

```text
h·x = 1, A·x <= b
lambda >= 0
c = eta h + A^T lambda
c·x = eta + b·lambda
```

Thus the supplied primal witness attains the supplied dual upper bound exactly. Lower expectations maximize the negative utility. The margin dual splits into original-constraint multipliers `alpha` and menu weights `w`. Its last coordinate proves `sum(w)=1`; its probability coordinates give:

```text
u_i - sum_j w_j u_j = eta 1 + A^T alpha
```

For an excluded action, complementary slackness at the strict self-row yields `w_i=0`; the implementation and checker require it. Projecting the optimal witness onto `p`, retaining `alpha` and `eta`, and using the objective `u_i - sum(w_j u_j)` gives an independent ordinary-polytope certificate with value `z*<0`. Hence that fixed randomized rival has expected advantage at least `-z*` under every `p in K`, with equality at the supplied belief. Pointwise utility differences can be negative when `K` constrains beliefs; the guarantee is over `K`, not over each world individually. This is one optimal exclusion mixture, not every mixture or a recommendation to randomize.

`verify_decisions` imports schema/matrix construction and certificate arithmetic, not the solver, enumerator or decision generator. It validates all range, pairwise, margin and exclusion certificates, then recomputes every choice set from the proved values. It accepts alternative valid attaining witnesses rather than matching a preferred serialization. Shared parsing and matrix construction remain a common failure surface; independent input-built HiGHS and visible-row reconstructions address some, not all, of that risk. This is not machine-checked formal verification.

## Limits and failure surfaces

- 1-6 worlds, 1-6 actions, at most six interval assessments. The existing phase-I limit and the additional margin candidate-basis limit are each 20,000. Some combinations within the dimension caps are therefore rejected.
- Raw rational components have magnitude at most 1,000,000 and denominators are positive. Probability-bound denominator LCM and utility denominator LCM each have a separate 1,000,000 cap. Signed utilities are allowed. Bounds themselves must lie in `[0,1]`.
- Strict JSON parsing rejects duplicate keys, booleans as integers, decimals, nonfinite constants, unknown fields, unsorted/repeated event indices and malformed shapes. CLI model reads and browser input are limited to 65,536 bytes; CLI verification report reads allow 8 MiB. API verification is separate.
- Certificates use exact rational arithmetic but witness bit lengths are not separately budgeted by the API. API callers should bound untrusted report size and computation. No denial-of-service hardening, formal proof, large-scale speed or real-world calibration claim is made.
- Utilities, world universe and probability bounds are supplied assumptions, not measurements validated by this tool. No independence, causal interpretation, preference learning, dynamic consistency, conditional utility or continuous-state integration is inferred.

## Developed evidence

These are finite, original teaching/development cases, not held-out experiments:

| Check | Observed scope |
|---|---|
| Native decision tests | 15 additional tests; quantifier counterexample, interior-only tie, strict boundary, tiny `1/1,000,000` exclusion, permutations, common positive-affine transform, duplicate actions, credal restriction, alternate witnesses, schema and import checks |
| Decision reports | 96 complete reports: 16 controls, 48 deterministic two-world menus, 32 seeded menus; 75 feasible reports, 56 excluded actions |
| Decision forgery tests | 824 primitive report modifications rejected across three controls |
| BigInt parity | All 96 complete reports equal Python; browser-produced reports replayed by native checker |
| Floating cross-check | 1,420 independently input-built HiGHS LPs, including projected-mixture guarantees; absolute tolerance `1e-8`, largest observed error `2.220446049250313e-16` |
| Installed decision wheel | 10 module origins outside checkout, 16 controls, two entry points, 32 CLI forgery rejections |
| Actual Chrome decision UI | 48 control-width views at 1280/390/320, 129 action views, 855 certificate selections, 2,784 inequality rows, 1,884 variable rows, 16 downloaded reports natively checked, 44 visual captures |

The independent browser-row oracle constructs every inequality, objective, mixture, action expectation and dual coefficient using Python Fraction arithmetic directly from input and report witnesses. Chrome also checks stale-output clearing, invalid input, horizontal table scrolling, no page overflow, enabled control target heights and trusted-pointer downloads. Old probability tests remain in CI unchanged apart from the installed distribution version assertion.

```sh
python -m unittest discover -s tests -v
node --test --test-concurrency=1 tests/test_engine.cjs tests/test_browser.cjs tests/test_decisions.cjs tests/test_decision_browser.cjs
python tools/check_installed.py
python tools/check_decisions_installed.py
python -m pip install scipy==1.15.3
python tools/check_highs.py
python tools/check_decisions_highs.py
```

Use Node 22+ and Chrome; set `CHROME_BIN` if needed. `CREDAL_DECISION_SCREEN_DIR=/tmp/decision-captures` saves decision UI states. `CREDAL_DECISION_URL` can point the same complete browser checks at a deployed decision inspector.

## Sources and attribution

1. [Nakharutai, Troffaes and Caiado (2019), Improving and benchmarking of algorithms for decision making with lower previsions](https://arxiv.org/html/1906.12215). Primary definitions 2-5, explicit omission of pointwise dominance, inclusion relationships and lower-expectation LPs. The project does not reproduce or claim the paper's speed benchmarks or specialized algorithms.
2. [Troffaes (2007), Decision making under uncertainty using imprecise probabilities](https://durham-repository.worktribe.com/OutputFile/1576906). Primary comparison of E-admissibility, maximality, maximin/maximax and randomized decisions. Its pointwise-admissibility convention differs from this project's stated strict-only convention.
3. [Troffaes, SSIPTA 2018 tutorial](https://bellman.ciencias.uniovi.es/~ssipta18/Material/Matthias.pdf). Teaching context for lower expectations and decision criteria.
4. [Utkin and Augustin (2005), Powerful algorithms for decision making under partial prior information and general ambiguity attitudes](https://isipta05.sipta.org/proceedings/046.html). Primary proceedings page on LP-based E-admissibility. Prior art, not an algorithm claimed as this implementation's invention.
5. [Boyd and Vandenberghe, Stanford EE364a duality notes](https://web.stanford.edu/class/ee364a/lectures/duality.pdf). Weak/strong duality and optimality certificates.
6. [SciPy `linprog(method='highs')` documentation](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html). Floating reference API; the margin variable explicitly has bounds `(None,None)` rather than the default nonnegative bound.
7. [Python Fraction documentation](https://docs.python.org/3/library/fractions.html). Native exact rational arithmetic, also used in the existing probability implementation.

Code, control menus, browser UI, exact certificate format and test harnesses are original project work. The decision criteria, LP duality and randomized-domination mathematics are classical and attributed.
