import test from "node:test";
import assert from "node:assert/strict";
import { initialVersion } from "../lib/initial-version.ts";

test("retains the durable current version when a later render failed", () => {
  assert.equal(
    initialVersion({
      current_version_id: "good",
      versions: [{ id: "good" }, { id: "failed" }],
      jobs: [{ version_id: "failed" }],
    }),
    "good",
  );
});
test("opens a first failed render plan for layout recovery after reload", () => {
  assert.equal(
    initialVersion({
      current_version_id: null,
      versions: [{ id: "failed" }],
      jobs: [{ version_id: "failed" }],
    }),
    "failed",
  );
  assert.equal(
    initialVersion({
      current_version_id: null,
      versions: [],
      jobs: [{ version_id: "missing" }],
    }),
    "",
  );
  assert.equal(
    initialVersion({ current_version_id: null, versions: [], jobs: [] }),
    "",
  );
});
