import assert from "node:assert/strict";
import { test } from "node:test";
import { timelineLanes } from "../lib/timeline-lanes.ts";

test("overlapping effects use separate lanes while touching effects share a lane", () => {
  const effects = [
    { id: "later", start: 4, end: 6 },
    { id: "overlay", start: 1, end: 3 },
    { id: "opening", start: 0, end: 4 },
    { id: "touching", start: 3, end: 5 },
  ];
  const original = structuredClone(effects);
  const lanes = timelineLanes(effects);
  assert.deepEqual(
    lanes.map((lane) => lane.map((e) => e.id)),
    [
      ["opening", "later"],
      ["overlay", "touching"],
    ],
  );
  assert.deepEqual(effects, original);
  assert.deepEqual(
    lanes
      .flat()
      .map((e) => e.id)
      .sort(),
    effects.map((e) => e.id).sort(),
  );
});

test("all 48 sequential moments fit in one compact lane", () => {
  const effects = Array.from({ length: 48 }, (_, i) => ({
    id: String(i),
    start: i * 3,
    end: i * 3 + 2,
  }));
  assert.equal(timelineLanes(effects).length, 1);
  assert.deepEqual(timelineLanes([]), []);
});
