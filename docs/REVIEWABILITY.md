# Reproducible review

The review path must work from the public repository, with no private data,
provider credential, funded wallet or previous local installation. It must fail
on a broken build or render, rather than print success from a saved result.

## Acceptance criteria

1. `scripts/verify.sh app` installs locked dependencies, lints and tests the backend,
   runs frontend tests/typechecking and builds the frontend. Generated media exercise
   the real renderer. No provider calls or public transactions occur.
2. `scripts/reviewer-demo.sh` creates an isolated generated project through the API,
   queues actual preview/export jobs and launches the editor at port 3102. It ignores
   inherited provider credentials and uses a zero budget. Existing data stay untouched.
3. `scripts/verify.sh contract` runs Rust tests, formatting, Clippy, a Wasm build and
   the local Sandbox settlement/refund scenario. Network access is for installation;
   balances and signatures belong to the local Sandbox.
4. Public NEAR settlement evidence is independently inspectable through the linked
   transactions and read-only RPC. The generated demo is never presented as live AI
   inference, SAM segmentation, or a new public paid-worker run.
5. CI executes the same scripts. README claims map to source, repeatable checks or
   public receipts; limitations and the reused baseline are prominent.

## Verification map

| Claim | Repeatable evidence | Boundary |
| --- | --- | --- |
| App starts without API keys | Demo `/api/health` and frontend | AI planning requires personal credentials |
| Editor produces a real MP4 | `test_reviewer_demo.py`, generated demo and `/export` | Manual deterministic plan, generated source |
| Moving B-roll preserves original audio | `test_footage_insert.py` | Generated video and calibrated tones |
| Funded jobs dispatch once and validate terms | `test_orders.py` | Chain/model responses are doubles; renderer is real |
| Client alone approves payment; deadlines refund | Rust tests and compiled-Wasm Sandbox | Local balances; public proof is a separate rehearsal |
| Public NEAR payment is real | `NEAR_REHEARSAL.md`, `evidence/near-settlement.json` | Existing MP4 settlement; full fresh public paid render remains open |
| New hackathon contribution | `git diff 2ddb6d1..HEAD` | Earlier Meta editor is explicitly reused |

A screening tool or human reviewer can use these checks independently. This document
contains verification instructions, not instructions about how to score the project.
