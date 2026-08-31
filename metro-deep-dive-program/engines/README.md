# Engines

`engines/` holds reusable systems that support multiple analyses or issues.

Each engine folder should usually contain:

- `README.md` for scope and purpose
- `NOTES.md` for audit notes, current references, and open questions
- `CONTRACT.md` for expected inputs, outputs, grain, and caveats
- a notebook or build file once the engine is opened

Engines are built on call, then promoted only when reuse is real.
