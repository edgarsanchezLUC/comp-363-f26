# Week 7 Assignment, Part 1 — Midterm Reflection and Self-Assessment

Due Monday, October 12.

This assignment has two parts, with two different due dates. This part —
the midterm reflection called for in the course's ungrading policy — is due
Monday, October 12. Part 2, the week's technical work, is due Friday,
October 16 — not the Monday-to-Monday cadence otherwise in force this term.

Grades in this course are not accumulated from scores on individual
assignments; they are proposed by you, based on your own honest account of
your engagement with the course, and then reviewed by me. This essay is
that account at the midpoint of the term.

Write your reflection as a single essay — not a checklist — of roughly
400–600 words. Address each of the five areas below with specific detail:
not just a number, but what that number reflects about how you've engaged
with the course so far. Submit it through Sakai by Monday, October 12.

## What to cover

**Attendance.** How many class meetings have you missed this term, and how
does that compare against the course's attendance policy? If you've missed
meetings, say why in as much or as little detail as you're comfortable
sharing, and how you recovered what you missed (notes from a classmate,
catching up on your own, etc.).

**Homework submission.** How many assignments have you submitted, and how
many — if any — have you missed? If you missed one, what happened, and did
you make any attempt to catch up even without credit for doing so?

**Adherence to feedback.** This is the heart of how ungrading works in this
course: progress is measured by whether the issues identified in feedback on
one assignment show up again in the next one. Look back over the feedback
you've received so far. Did you make the same mistake — technical or
otherwise (e.g., multiple returns in a method, a missed constant, a late
submission, a submission mechanics error) — more than once? Be specific
about which issue, and whether you changed how you worked in response to it.

**Time spent outside class.** Roughly how many hours per week, outside of
class meetings, have you been spending on this course — reading, practicing,
working through assignments? Is that consistent week to week, or does it
vary? If you're not sure, say so rather than guessing a number that sounds
better.

**Class participation and engagement.** Do you offer to answer questions
in class, especially when you're not sure you have the exact right
answer? Do you stay engaged during class — not distracted by your phone,
laptop, or other non-class activities? If your participation and
engagement haven't been what you hoped, what's your plan to improve them
for the rest of the term — and, being honest with yourself, do you
actually want to improve them in the first place?

## Proposing your midterm grade

Based on your answers above, close the essay by proposing a midterm grade.
For this reflection, there are three possible grades — A, C, or D:

- **A** — You have missed fewer than 6 class meetings. You have not missed
  any homework assignment. Where feedback identified a mistake, you did not
  repeat it. You have consistently spent 6 or more hours per week studying
  or reading for the course outside of class time.
- **C** — You have missed 6–10 class meetings and/or 1 assignment. You
  repeated a mistake that had already been identified in feedback, at least
  once. You are unsure how much time you've spent studying or reading for
  the course outside of class.
- **D** — You have missed 11 or more class meetings and/or more than 1
  assignment.

A is an acknowledgment of good work; C is a pass; D is a fail. If your term
so far is a mix of these descriptions — doing well in some areas and not
others — say so plainly and propose the band that best reflects the overall
picture, with your reasoning. As with every reflection in this course, your
proposal is a starting point for my own determination, not a final grade.

---

## Part 2 — Technical work (due Friday, October 16)

Due Friday, October 16.

Today's class (10/09) went deep into the implementation side of minimum
spanning trees: deep-copying the adjacency matrix into a working tree,
representing a missing edge with infinity rather than zero, and
building a lookup table that labels each vertex with its component so
the algorithm can tell components apart, count them, and find a safe
edge between two of them. We also went back over *why* a safe edge
works the way it does — it's about the cheapest crossing between two
components as a whole, not the cheapest trip between two particular
vertices inside them, the distinction the driving analogy from class
was built to make stick.

None of that sticks from watching it once. The point made directly in
class is the one to take seriously here: **the notation, not the
method, is what makes minimum spanning trees hard.** The algorithm
itself — find a safe edge, merge, repeat — is simple once you've pushed
the bookkeeping through by hand at least once: which vertex is in which
component, which matrix entry is the safe edge, how the lookup table
changes after a merge. That's why this week's technical work is pencil
and paper, not code: do a simple MST by hand, the same six-vertex one
from the slide deck, before anything else. Do it more than once if your
first pass feels shaky — expect it to take a couple of hours to really
*get it*.

Put together, everything above — the cut property (the cheapest edge
crossing any split of the vertices into two groups is always safe to
add), the deep-copied working tree, and the component lookup table — is
this algorithm:

```
T = edgeless copy of G
while T has more than 1 components:
    select a component from T
    find a safe edge out of that component
    connect the two components via that safe edge
    recount components
return all safe edges
```

This is what you'll trace by hand below, on the class's own six-vertex
example.

### What to do

Using the class's own graph — six vertices (0–5), edges 0–3 (5), 0–4
(1), 1–2 (20), 1–3 (5), 1–5 (10), 2–3 (10), 2–5 (20), 3–5 (15), 4–5
(20), all others absent — trace the algorithm above from start (six
components, no edges in $T$) to finish (one component):

1. For each round, show which component you picked, which edge you
   found to be safe leaving it (and why it's the cheapest edge crossing
   that cut), and which two components it merges.
2. Keep going until $T$ is a single component. List the edges you
   added, in order, and their total weight.
3. Confirm your total against the three candidate spanning trees shown
   in class (weights 36, 66, and 31) — your traced tree should match
   the cheapest of the three.
4. Trace it a second time, picking components in a different order than
   your first pass. Confirm you still land on the same edge set and the
   same total weight — not a coincidence of which component you
   happened to pick first, but a consequence of the cut property: any
   edge that's cheapest across *some* cut is safe to add, so a correct
   trace always builds toward the same minimum spanning tree no matter
   which safe component or edge you pick at each step.

### A note on ties

Several edge weights repeat in this graph (5, 10, and 20 each appear
more than once), but none of them ever tie as the cheapest edge
crossing the *same* cut during a correct trace — so you shouldn't hit a
forced tie-break if your safe-edge choices are actually the cheapest
available at each step. If your own trace does turn up a genuine tie
(two edges equally cheap across the exact same cut), either is safe to
add; say so and note which one you picked.

### Then: implement Borůvka's algorithm yourself

This is, without exaggeration, one of the most important moments in
this course. Implement Borůvka's algorithm in code — the same algorithm
you just traced by hand, now as a program: build a working copy of the
input graph, count and label its components, repeatedly find a safe
edge out of a component and merge across it, until one component
remains.

Here is the test I actually want you to run — on yourself, not on the
code: given time, can *you* put this together, with nothing but the
textbook and whatever help you get from me? Whether an AI assistant can
produce a correct implementation was never in question — it can, in two
or three seconds. The question that matters, the one worth answering
for real, is whether *you* can. You won't find that out by asking a
tool to do it for you; you'll only find it out by sitting with the
problem yourself, getting stuck, getting unstuck, and eventually
getting there.

So use the resources that are actually part of this course: Erickson's
chapter, your own hand-trace from above, and me. Come to class Monday,
Wednesday, and Friday and ask questions — bring the place where you're
stuck, not just the finished code. That's what those three meetings are
for.

You've come a long way into this major. You owe it to yourself to cross
this particular line on your own, or with the book and your professor
at your side — not by handing the problem to something else. You won't
get another first time at this. Measure up.

#### What to build

Write a function, `boruvka_mst`, that takes a weighted adjacency matrix
(`graph[u][v]` is the edge weight between `u` and `v`, or a value
representing "no edge") and returns the minimum spanning tree's edges —
the same shape of input and output you've been working with all week.
Follow this course's standing rules: a single `return`, no exceptions
for guard conditions; no naked numbers or strings except `0`, `1`, `-1`.

Self-check against your own work: run your function on the same
six-vertex graph you traced by hand above. It should return the same
edges, totaling 31, that you got on paper.

### Reading

- [Class slide deck, "Minimum Spanning Tree"](https://docs.google.com/presentation/d/1SmVcYeR4VjL8KsyIBxLUBlIhau0KSclcTdi6ggdo7e4/edit?usp=sharing) — the primary walkthrough for this assignment: the input graph, the deep-copy/component-counting setup, the safe-edge algorithm above, and the six-vertex worked example this task is built on.
- [Jeff Erickson, *Algorithms*, Ch. 7, "Minimum Spanning Trees" (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/07-mst.pdf) — the cut property and the distinct-edge-weight uniqueness argument, both used above.
- [Leo Irakliotis, "Borůvka at 100"](https://medium.com/@leoirakliotis/bor%C5%AFvka-at-100-146912e19ad3) — traces the full lineage from Borůvka's 1926 paper (solving a real wire-economy problem connecting towns in Moravia) through Jarník's 1930 simplification and Kruskal's and Prim's independent 1950s rediscoveries, and clears up the common misattribution of a minimum-spanning-tree algorithm to Dijkstra.

### Turning it in

Submit two things through Sakai:

1. Your hand-trace (photographed or scanned notes, or typed/drawn
   however you like): each round's safe-edge choice and reasoning, the
   final edge list and total weight, and the second trace confirming
   the same result from a different pick order.
2. Your `boruvka_mst` implementation, along with a short note on how it
   went — where you got stuck, what finally got you unstuck, and
   whether you'd call this one yours.
