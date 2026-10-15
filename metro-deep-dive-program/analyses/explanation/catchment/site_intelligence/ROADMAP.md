# Site Intelligence Roadmap

**Status:** Active

**Updated:** 2026-10-07

## Now

- Freeze the site-artifact adapter contract and build the internal workbook.
- Establish the client-ready section registry before designing final report
  layout, so incomplete sections remain visible to analysts without leaking
  into client delivery.

## Next

- Build the static client brief from the same adapters and add HTML/PDF
  rendering QA.
- Migrate one validated Jacksonville bundle, then prove a second-site render.

## Deferred but retained in the workbook

| Workbook section | Client status | Promotion gate |
|---|---|---|
| Traffic trend | withheld | current and historical frontage series render and reconcile to FDOT inputs |
| Barrier and water reach | withheld | method is approved beyond an explanatory companion view; it must not claim routing/access |
| GDP mix | withheld | source, units, coverage, and displayed shares reconcile to an approved market contract |
| Housing/rent trend | withheld | non-empty series reconcile to the selected CBSA and stated annual method |
| Dasymetric weights | method candidate | buildings source, sensitivity comparison, and method decision are approved |
| Routed reach | method candidate | declared routing source, travel mode, threshold, coverage, and validation plan are approved |

`withheld` means the internal workbook renders the section's explicit status,
source dependency, and promotion gate. It does not mean the section vanishes
from planning or is represented as zero/unavailable evidence in a client brief.
