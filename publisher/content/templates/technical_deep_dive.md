# [Title: the decision or problem, not the solution]
*Copy this into the piece's folder under `publisher/content/`. Delete italicized instructions as you fill each section. Format rules: `docs/strategy/PUBLISHING.md`.*

**ID:** 
**Format:** Technical Deep Dive
**Stream:** Technical posts (gated; see `docs/strategy/PUBLISHING.md`)
**Audience:** Civic tech practitioners, data engineers, analysts who build similar systems
**Status:** In Progress

---

## The decision
*One sentence. What specific build decision, architectural choice, or methodology tradeoff is this piece about? Name it precisely — "whether to use GMM vs. k-means for cluster assignment" not "our clustering approach."*

---

## Why it's worth explaining
*Not for the piece — for you. What makes this decision non-obvious? What would a practitioner get wrong if they hadn't made this mistake or worked through this tradeoff themselves?*

---

## GitHub artifact
*The piece must link to a real artifact. What is it?*

- Repo / file:
- What it contains:
- Link:

---

## The obvious approach and why it doesn't work
*What would most practitioners do by default? What's wrong with it in this context — or what did you try first that failed? Be specific about the failure mode.*

---

## The approach taken
*What did you actually do? This section carries the code, SQL, or schema. Keep code to the essential decision — full implementation lives on GitHub.*

```
[code or SQL block]
```

*Explanation of what the code does and why the key lines matter:*

---

## What it enabled
*One paragraph. What does this approach make possible that the obvious approach wouldn't? Tie it back to the data product — not just "it's cleaner" but "it let us do X, which powers Y."*

---

## What you'd do differently
*Honest retrospective. What are the limitations of this approach? What would you change with a second pass or more time? This section is what separates a Technical Deep Dive from documentation.*

---

## Outline

1. **The problem** — what decision or constraint the piece is about
2. **Why the obvious approach doesn't work** — the failure mode, specifically
3. **The approach taken** — with code or schema; annotated at the decision points
4. **What it enabled** — tied back to the data product
5. **What you'd do differently** — honest retrospective

---

## Draft
*Write here or link to the piece's `post_draft.md`.*

---

## Ship checklist
- [ ] Names a real decision, not a tutorial
- [ ] Code or schema present and annotated
- [ ] GitHub artifact linked in the piece
- [ ] "What I'd do differently" section is honest — not a victory lap
- [ ] 1,200–2,000 words
- [ ] GitHub artifact polished and README updated
- [ ] Substack published
- [ ] LinkedIn post (one surprising decision or finding from the build — not the code)

---

## Retrospective
*Fill in after publishing.*

- Time to write:
- What worked:
- What didn't:
- Practitioner feedback worth noting:
- Next technical piece candidate:
