/** Preserve every effect while packing non-overlapping moments into shared tracks. */
export function timelineLanes<T extends { start: number; end: number }>(
  effects: T[],
): T[][] {
  const lanes: T[][] = [];
  for (const effect of [...effects].sort(
    (a, b) => a.start - b.start || a.end - b.end,
  )) {
    const lane = lanes.find(
      (items) => items[items.length - 1].end <= effect.start,
    );
    if (lane) lane.push(effect);
    else lanes.push([effect]);
  }
  return lanes;
}
