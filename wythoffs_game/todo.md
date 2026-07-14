You're in much better shape than you feel — most of what's missing isn't math, it's a story that separates "proved" from "measured" from "open". Let me give you that separation, a script for the professor, and a concrete plan.

What you actually have, sorted by confidence
Proved (fully rigorous):

The x=0 sheet: it's Fraenkel's (2,1)-Wythoff, b_n = 2a_n + n, with your independence/coverage proof. Cite Fraenkel 1998 and move on.
The y=0 wall is a closed sub-game, so edge dots = partner(x), computable in O(log x).
The stepping law Δb = 2Δa + 1 given no collision — that's a cell-by-cell argument, done.
The two-equation fixed point: IF the line has a well-defined slope m and density λ, THEN m = 2+λ and λ = m/(m+1) force m = 1+√3. The algebra you did yourself is exactly this.
Measured, not proved:

Collisions are transient (the ~500× decay in bump_decay.py). This is the one empirical link in the slope chain.
Intercepts walk up ≈5 per level; increments in a small alphabet; core width ≈ 25x + 150.
Open:

Prove collisions die out. Prove/derive the ≈5 intercept spacing. Explain the core width.
That's a normal shape for a research writeup. Nobody expects the intercepts solved — Fraenkel himself lists the multipile extension as open/difficult.

How to explain the slope to your professor (5 sentences)
"Moves that don't touch pile x are the same on every sheet, and they're exactly the 2-pile game — so each sheet is the 2-pile game played on top of a background of cells already ruled out by moves down to lower sheets."
"Three facts hold on every sheet no matter what that background is: one loser per column, mirror symmetry across y=z, and each loser's threat region has a slope-2 edge."
"Fact 3 gives Δb = 2Δa + 1 per step, so slope = 2 + density; facts 1–2 give density = m/(m+1). Solving: m = 1+√3. Same two equations that solve the base game."
"The background can interfere — a step can land on an inherited winner and get bumped up. But we measured the bump rate along each line and it decays about 500-fold; each bump is a permanent +1 shift, so bumps move the intercept, not the slope."
"So the slope is exactly 1+√3 on every sheet, conditional on one empirical fact — transience of collisions — which we verify to 4 decimals out to sheet ~30 and state as a conjecture."
Being explicit that step 4 is empirical is not a weakness — it's exactly what a professor wants to hear, and it hands them a well-posed conjecture instead of a hand-wave.

Intercepts: reframe the goal
Stop trying to find a formula — the evidence says there isn't a simple one (the intercept integrates the whole history below it, unlike the edge dots which live in a sealed sub-game). The achievable and publishable goal is to characterize the intercept sequence:

Compute k(x) (mode of b − 2a − n) for all sheets you can reach cleanly (x ≲ 80 on the 12,000 grid) and tabulate the increments k(x+1) − k(x). You already believe the alphabet is {3,5}-ish — nail it down: what values occur, with what frequencies, is there a pattern in when 3 vs 5 occurs (like a Sturmian/Beatty-ish pattern)? If the increment sequence itself looks like ⌊nθ⌋ differences for some θ, that's a real theorem candidate.
You already have the lower bound (≥3 cells clearance). Try for an upper bound with the same style of argument: how far above the previous line can the first free cell be? Even "increment ≤ 7" bracketing the walk would be a result.
Report mean spacing ≈5 with error bars and mark the derivation as open. One heuristic worth 30 minutes: mean spacing should equal (lower bound 3) + (expected extra push from inherited winners near the line) — the winner strips sit 3d–4.5d below the line with spacing ~5/level, so the density of inherited winners in the line's corridor is computable in principle. If a back-of-envelope from that geometry lands near 5, that's a satisfying paragraph even without rigor.
The messy losers near the origin
Yes, exclude them from asymptotic measurements — that's completely standard (it's a boundary layer, like transients in a dynamical system). But don't ignore them: measure the core's width per sheet (your clean-window cutoff 25x + 150 is already an empirical answer) and report it as its own observation: "each sheet has a chaotic core of width growing roughly linearly in x, beyond which the line is exact." That turns an embarrassment into a stated phenomenon.

Suggested order for the remaining weeks
Increment table for k(x) up to x≈80 (one script, one afternoon) — this is the intercept deliverable.
Extend the bump-decay measurement to more sheets / longer lines to strengthen the transience conjecture (maybe a 20,000-wide grid for sheets up to 40).
Attempt the upper-bound clearance argument (pure thinking, no code).
Write the professor summary in the proved/measured/open structure above.
Want me to write the k(x)-increment script and run it on regenerated data as step 1?