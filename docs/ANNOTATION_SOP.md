# Annotation SOP

## The task

You'll watch a first-person (egocentric) video of someone doing a
procedural task (cooking, crafts, assembly, etc.). The tool shows you the
person's high-level goal (their `query`, e.g. "How do I make a blue
cheese dip?") above the video.

As you watch, **mark the moments where you think a proactive AI assistant
watching alongside the person should speak up** — confirm a step is done,
warn about a mistake, or offer timely guidance for what's next. You are
not writing what the assistant *should say*, just marking *when* it
should say something.

## Two granularities, marked in this order

Each video gets marked **twice**, once per granularity.
Do them **in this order**, and ideally **with some time between passes**
(a different day, or at least a break) — the point is to judge each pass
fresh, not let your coarse-pass judgment quietly shape your fine-pass
judgment (or vice versa).

1. **`coarse`** — mark only when a **major step** or **big action**
   finishes (main step transitions — e.g. "the dip is now mixed," not
   "one more stir"). This should be sparse — a handful of points per
   video, not dozens.
2. **`fine`** — mark every time an **identifiable sub-action** finishes,
   even small ones (e.g. "picked up the spoon," "added the salt," "wiped
   the counter"). This should be noticeably denser than `coarse`.

Use the granularity switch in the tool (coarse / fine buttons) —
each is stored and tracked separately, and the tool remembers which
video+granularity combinations you've marked "complete" so you can see
what's left.

## Chinese notes (optional)

After marking a point, a small box lets you jot a quick note in Chinese
about what's happening at that moment — this is just a memory aid for
you, translated to English automatically for storage. Totally optional;
leave it blank, or type directly in English instead, whichever is faster
for you.

## The most important rule: annotate independently

**Do not discuss your answers with other annotators, and do not try to
match what you think someone else marked.** If you and another annotator
mark a video very differently, that is not an error to fix — **it's the
data this project needs.**

Why: the whole point of this project is to measure how much people
genuinely disagree about the right moment to interrupt, and whether that
disagreement changes with granularity. If annotators compare notes and
converge on "the right answer," that disagreement — the actual signal —
disappears from the data. Please resist the urge to check "am I doing
this right" against someone else's marks. There isn't a right answer
being hidden from you; your honest independent judgment *is* the
correct output.

## How to judge the moment

Mark at the point where **the current step has visibly progressed to
where a comment would be most useful and least disruptive** — usually
right as an action completes or a clear state change is visible, not
mid-motion and not long after.

If you're not sure exactly where: **go with your first instinct and move
on.** Don't scrub back and forth hunting for the "perfect" frame — a
half-second of imprecision doesn't matter here, but a lot of second-
guessing will slow you down and may start to look like it's converging
toward "what would be defensible" rather than your genuine read of the
moment, which is exactly what we don't want.
