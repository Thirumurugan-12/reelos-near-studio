"use client";

import { useEffect, useState } from "react";
import {
  api,
  type Asset,
  type CatalogItem,
  type CatalogParams,
  type Version,
} from "../lib/api";

const names: Record<string, string> = {
  from: "Starting value",
  to: "Target value",
  look: "Style",
  pos: "Position",
  tc: "Starting timecode",
  ticks: "Event times in seconds (separate with |)",
  label_x: "Label horizontal position",
  lines_y: "Left text vertical position",
  right_y: "Right text vertical position",
  hl: "Highlighted word",
  kpi: "Metric value and label (value::label)",
  donut: "Donut value and label (%::label)",
  bars: "Bar values and label (3|2|1::label)",
  views: "View labels (separate with |)",
};
const listFields = new Set(["lines", "right", "others", "ticks", "views"]);
const caption = (key: string) =>
  names[key] || key.replaceAll("_", " ").replace(/^./, (s) => s.toUpperCase());

export function EffectBrowser({
  version,
  assets,
  busy,
  onApply,
  onDirection,
}: {
  version?: Version;
  assets: Asset[];
  busy: boolean;
  onApply: (
    params: CatalogParams,
    start: number,
    end: number,
  ) => Promise<boolean>;
  onDirection: () => void;
}) {
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<CatalogItem>();
  const [text, setText] = useState("");
  const [options, setOptions] = useState<Record<string, string | number>>({});
  const [media, setMedia] = useState<string[]>([]);
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(3);
  const [error, setError] = useState("");
  const duration = version
    ? version.plan.source_out - version.plan.source_in
    : 0;
  useEffect(() => {
    let live = true;
    api<{ effects: CatalogItem[] }>("/effects")
      .then((r) => {
        if (live) setItems(r.effects);
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, []);
  function choose(item: CatalogItem) {
    setSelected(item);
    setText(item.accepts_text ? item.example.text.replaceAll("|", "\n") : "");
    setOptions({});
    setMedia([]);
    setStart(0);
    setEnd(Math.min(3, duration || 3));
    setError("");
  }
  function option(key: string, value: string) {
    setOptions((old) => {
      const next = { ...old };
      if (value === "") delete next[key];
      else next[key] = value;
      return next;
    });
  }
  async function apply(e: React.FormEvent) {
    e.preventDefault();
    if (!selected || !version) return;
    if (
      !Number.isFinite(start) ||
      !Number.isFinite(end) ||
      start < 0 ||
      end <= start ||
      end > duration
    ) {
      setError("Choose a start and end within this edit.");
      return;
    }
    if (selected.requires_values && !options.to) {
      setError(
        "Enter your target value; example metrics are not applied automatically.",
      );
      return;
    }
    if (
      options.look === "bento" &&
      ["donut", "kpi", "bars"].some((k) => !options[k])
    ) {
      setError("Enter your donut, metric and bar values for the bento style.");
      return;
    }
    const params = {
      fx: selected.id,
      text: selected.multiline_text ? text.replaceAll("\n", "|") : text,
      options,
      media_ids: media,
    };
    setError("");
    await onApply(params, start, end);
  }
  const namedPreview = selected?.looks.find(
    (name) =>
      (
        ({
          "glitter-spotlight": "sparkle",
          "editorial-cover": "editorial",
          "glass-bento": "bento",
        }) as Record<string, string>
      )[name] === options.look,
  );
  const previewBase = namedPreview ? `/api/effects/${namedPreview}` : undefined;
  if (selected)
    return (
      <aside className="panel catalog-panel" aria-label="Effect settings">
        <button className="text-button" onClick={() => setSelected(undefined)}>
          ← All {items.length} effects
        </button>
        <h2>{selected.label}</h2>
        <p className="muted small">{selected.description}</p>
        {selected.preview_ready && (
          <video
            className="catalog-demo"
            key={previewBase || selected.id}
            src={previewBase ? `${previewBase}/preview` : selected.preview_url}
            poster={previewBase ? `${previewBase}/poster` : selected.poster_url}
            muted
            loop
            autoPlay
            playsInline
            controls
            aria-label={`${selected.label} illustrated preview`}
          />
        )}
        <p className="muted small">
          Illustrated preview with example data. Apply to see your footage and
          settings.
        </p>
        <form onSubmit={apply} className="catalog-form">
          {selected.accepts_text && (
            <label>
              {selected.multiline_text ? "Text items (one per line)" : "Text"}
              <textarea
                value={text}
                maxLength={480}
                rows={3}
                onChange={(e) => setText(e.target.value)}
              />
            </label>
          )}
          <div className="catalog-timing">
            <label>
              Start (seconds)
              <input
                type="number"
                min={0}
                max={duration}
                step={0.1}
                value={start}
                onChange={(e) => setStart(e.target.valueAsNumber)}
                required
              />
            </label>
            <label>
              End (seconds)
              <input
                type="number"
                min={0}
                max={duration}
                step={0.1}
                value={end}
                onChange={(e) => setEnd(e.target.valueAsNumber)}
                required
              />
            </label>
          </div>
          <p className="muted small">
            Times are relative to this edited video. Original speech continues
            through visual freezes.
          </p>
          {selected.requires_values && (
            <label>
              Target value
              {selected.id === "over-the-shoulder-zoom"
                ? "s (two, separated with |)"
                : ""}
              <input
                value={options.to ?? ""}
                placeholder={
                  selected.id === "over-the-shoulder-zoom"
                    ? "e.g. 10|20"
                    : "e.g. 59%"
                }
                onChange={(e) => option("to", e.target.value)}
                required
              />
            </label>
          )}
          {selected.uses_media && (
            <fieldset className="catalog-media">
              <legend>Supporting cards</legend>
              <p className="muted small">
                No selection uses still frames from your source video.
              </p>
              {assets
                .filter((a) => a.role === "supporting")
                .map((a) => (
                  <label key={a.id}>
                    <input
                      type="checkbox"
                      checked={media.includes(a.id)}
                      disabled={!media.includes(a.id) && media.length >= 9}
                      onChange={(e) =>
                        setMedia((old) =>
                          e.target.checked
                            ? [...old, a.id]
                            : old.filter((id) => id !== a.id),
                        )
                      }
                    />
                    {a.name}
                  </label>
                ))}
              {!assets.some((a) => a.role === "supporting") && (
                <p className="muted small">
                  Add images or clips in Assets to use your own cards.
                </p>
              )}
            </fieldset>
          )}
          <details>
            <summary>Adjust the look</summary>
            <div className="catalog-options">
              {selected.options
                .filter(
                  (k) =>
                    !(selected.requires_values && k === "to") &&
                    (!["donut", "kpi", "bars"].includes(k) ||
                      options.look === "bento"),
                )
                .map((key) => {
                  const bounds = selected.numeric_options[key];
                  const choices = selected.enum_options[key];
                  return (
                    <label key={key}>
                      {caption(key)}
                      {choices ? (
                        <select
                          value={String(options[key] ?? "")}
                          onChange={(e) => option(key, e.target.value)}
                        >
                          <option value="">Effect default</option>
                          {choices.map((v) => (
                            <option key={v} value={v}>
                              {v}
                            </option>
                          ))}
                        </select>
                      ) : listFields.has(key) ? (
                        <textarea
                          rows={2}
                          maxLength={480}
                          value={String(options[key] ?? "")}
                          placeholder="Use effect default"
                          onChange={(e) =>
                            option(key, e.target.value.replaceAll("\n", "|"))
                          }
                        />
                      ) : (
                        <input
                          type={bounds ? "number" : "text"}
                          min={bounds?.[0]}
                          max={bounds?.[1]}
                          step={key === "count" || key === "pick" ? 1 : "any"}
                          maxLength={480}
                          value={options[key] ?? ""}
                          placeholder="Effect default"
                          onChange={(e) => option(key, e.target.value)}
                        />
                      )}
                    </label>
                  );
                })}
            </div>
          </details>
          {error && (
            <p role="alert" className="catalog-error">
              {error}
            </p>
          )}
          {!version && (
            <p className="muted small">
              Create or select a subject-tracked edit first.{" "}
              <button
                type="button"
                className="text-button"
                onClick={onDirection}
              >
                Go to Direction
              </button>
            </p>
          )}
          <button
            className="primary wide"
            type="submit"
            disabled={busy || !version}
          >
            Apply and preview
          </button>
        </form>
      </aside>
    );
  const filtered = items.filter((r) =>
    (r.label + " " + r.description + " " + r.looks.join(" "))
      .toLowerCase()
      .includes(query.toLowerCase()),
  );
  return (
    <aside className="panel catalog-panel" aria-label="Effect catalog">
      <div className="panel-heading">
        <h2>Effects</h2>
        <span className="count">{items.length}</span>
      </div>
      <p className="muted small">
        Choose a treatment. Every effect has an illustrated preview; three extra
        styles are in the look controls.
      </p>
      <p className="muted small">
        Recipes adapted from{" "}
        <a
          href="https://github.com/Vibha-Ramprakash/claude-video-effects"
          target="_blank"
          rel="noreferrer"
        >
          Vibha Ramprakash · MIT
        </a>
        .
      </p>
      <label className="catalog-search">
        Find an effect
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Orbit, glass, zoom…"
        />
      </label>
      {error && <p role="alert">{error}</p>}
      {!items.length && !error && <p role="status">Loading effects…</p>}
      {!!items.length && !filtered.length && (
        <p>No matching effects. Try another name.</p>
      )}
      <div className="catalog-list">
        {filtered.map((item) => (
          <button
            className="catalog-tile"
            key={item.id}
            onClick={() => choose(item)}
            aria-label={item.label}
          >
            {item.preview_ready && (
              <img src={item.poster_url} alt="" loading="lazy" />
            )}
            <span>
              <strong>{item.label}</strong>
              <small>{item.description}</small>
            </span>
          </button>
        ))}
      </div>
    </aside>
  );
}
