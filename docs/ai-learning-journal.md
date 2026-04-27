# CSEN 174: AI learning journal

Hey. This is for a software engineering class, but you really **do not need to know what our app is** to get something out of it. We are mostly figuring out **how to work with AI** in a sane way: where it actually saves time, where it sounds sure of itself and is not, and what little habits make the whole thing less messy.

**For our team:** Each week we drop a new section above the template. Three real chats with the assistant, plus a quick note on what each one taught us **about using AI** (not about our feature list). Then one thing that felt like a win and one that felt like a trap. If anyone needs proof, the raw threads live under `.cursor/projects/home-quire-git-mumble-tts-sst/agent-transcripts/`. The main parent chat we have been using is [Cursor chat transcript](c59d74d4-4202-4baf-aa36-3751da37ef1a).

---

## Week of March 31, 2026

**What we were doing:** We were still in that fuzzy early phase. We dumped a full project idea in one message, then asked the tool to read the actual assignment HTML and tell us if we were on track, then we changed our mind about a couple tools and asked it to roll that into the plan.

### Three back-and-forths

1. **What I asked:** Basically “here is the whole product picture at once, react to it.”
  **What I took away:** If you only feed the model one crumb at a time, it cannot push back on the whole thing. A single chunky prompt gets you a better sanity check.
2. **What I asked:** “Does this match the official requirements, and if not, what would we change?”
  **What I took away:** Pasting or pointing at the **real** assignment beats paraphrasing from memory. I stopped caring about a simple yes or no; the useful part was the list of gaps I could walk through myself.
3. **What I asked:** “Scratch that vendor, we were only name-dropping it; use these other defaults instead.”
  **What I took away:** Once there is already a plan on the table, short blunt follow-ups work great. The model is pretty good at **rewriting the doc** to match, as long as your decision is spelled out.

### One opportunity

Running the rubric past AI **before** crunch time turns “are we about to fail?” into something you can do on a random Tuesday whenever the spec shifts.

### One challenge or risk

It will talk about grading like it went to faculty meetings. It did not. We still owe the humans on staff a real check. I try to treat anything it says about policy as a **draft** list, not a verdict.

---

## Week of April 1, 2026

**What we were doing:** Still shaping things, not rehearsing a demo. We asked how we might lay out the repo so graders can tell what is ours, what we should tackle first while everything still moves, and what knobs users might reasonably get without the UI turning into a spaceship cockpit.

### Three back-and-forths

1. **What I asked:** “Is there a cleaner way to structure this that still hits the requirements we care about?”
  **What I took away:** Nice for tossing around **folder stories and who owns what**, if you say what has to stay true (like: people grading us need to see our code clearly). We still pick the layout; it just throws patterns at us.
2. **What I asked:** “We have not committed to much yet. What matters most, in what order, if we want simple and compliant?”
  **What I took away:** Asking for **order and tradeoffs** went over better than asking for “the best stack.” Easier to gut-check, easier to rip up next week if we were wrong.
3. **What I asked:** “Users should tweak more than a preset; what kinds of sliders even make sense?”
  **What I took away:** Handy for **brainstorming around a requirement you already believe in.** I still throw away ideas that sound clever but do not match real users.

### One opportunity

Having a casual “if we reorganize now, what breaks?” chat with AI is basically free. That same conversation hurts more once everyone is used to a tangled repo.

### One challenge or risk

It really likes drawing file trees and naming tools. You can **drift from planning into fake implementation** without noticing. The skill I am trying to build is to stop when our team needs to decide something, not when the model runs out of tokens.

---

## Week of April 7, 2026

**What we were doing:** We sharpened **who this is really for**, tried the same core idea on a **different surface** people already live in (same rough backend story, different front door), and cleaned public docs so a random visitor does not see two conflicting stories.

### Three back-and-forths

1. **What I asked:** “Scrub the old product names out of our docs everywhere.” **What I took away:** Great for a **boring consistency pass** when the rule is simple. I still `grep` the repo myself because it will miss a stray line sometimes.
2. **What I asked:** “Make the ‘who’ line about accessibility and real life: hearing, speech, noisy rooms, not a vague audience label.”
  **What I took away:** Strong for **rewriting with new constraints.** Weak if you let it invent user interviews. We tried to keep it tied to what we actually think is true.
3. **What I asked:** “Same idea, but ship it through Discord instead of a from-scratch client.”
  **What I took away:** Good for a **‘what stays, what moves’** summary. It will not know every platform rule, so feasibility is still on us.

### One opportunity

Using AI while you rewrite docs for someone who does not live in your head (prof, teammate, you in six months) nudges you toward plain English. That carries to every project.

### One challenge or risk

Big platforms have weird rules. The model will hand-wave. **It helps you wordsmith the question; it does not replace reading the real docs** when you mean to ship something.

---

## Template (copy for a new week)

- **What we were doing:** a short paragraph in normal words, no deep product lore.
- **Three back-and-forths:** each with **What I asked** and **What I took away** (one sentence about AI teamwork, not feature trivia).
- **One opportunity** and **One challenge or risk** in the same spirit.

### Syllabus reminder (CSEN 174)

Three prompts with a short reflection each, one opportunity, one challenge. It is completion graded, so a messy honest week still beats a shiny empty one.