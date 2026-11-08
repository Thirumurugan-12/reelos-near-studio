# NEAR paid editing jobs

See ../SPEC-near-paid-jobs.md for the interface and acceptance conditions.
Build order: escrow -> testnet read adapter -> wallet flow -> rendering worker -> rehearsal.
Start with the financial state machine because authorization, transfer failures and refunds
are the greatest correctness risks. Keep each increment independently testable.
Existing Meta model credentials stay local. No paid calls are necessary for contract tests.
Deployment needs testnet accounts and a verified Wasm build; do not claim deployment from unit tests.
Track all tasks in near-todo.md.
