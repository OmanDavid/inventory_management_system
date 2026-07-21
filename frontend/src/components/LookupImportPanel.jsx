import { useState } from "react";
import SlideOver from "./SlideOver";
import { api, ApiError } from "../api";

export default function LookupImportPanel({ open, onClose, onImported }) {
  const [mode, setMode] = useState("barcode"); // barcode | name
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | error | importing
  const [error, setError] = useState("");

  const reset = () => {
    setQuery("");
    setResult(null);
    setPrice("");
    setStock("");
    setStatus("idle");
    setError("");
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleLookup = async (e) => {
    e.preventDefault();
    setStatus("loading");
    setError("");
    setResult(null);
    try {
      const params = mode === "barcode" ? { barcode: query } : { name: query };
      const product = await api.lookupExternal(params);
      setResult(product);
      setPrice(product.price || "");
      setStock(product.stock || "");
      setStatus("idle");
    } catch (err) {
      setStatus("error");
      setError(err instanceof ApiError ? err.message : "Lookup failed");
    }
  };

  const handleImport = async () => {
    setStatus("importing");
    setError("");
    try {
      const payload =
        mode === "barcode" ? { barcode: query } : { name: query };
      if (price !== "") payload.price = Number(price);
      if (stock !== "") payload.stock = Number(stock);
      const created = await api.importExternal(payload);
      onImported(created);
      handleClose();
    } catch (err) {
      setStatus("error");
      setError(err instanceof ApiError ? err.message : "Import failed");
    }
  };

  return (
    <SlideOver
      open={open}
      onClose={handleClose}
      title="OpenFoodFacts lookup"
      subtitle="Preview a product before adding it to inventory"
    >
      <form onSubmit={handleLookup} className="space-y-4">
        <div className="flex gap-2 rounded-md bg-paper p-1 text-sm">
          {["barcode", "name"].map((m) => (
            <button
              type="button"
              key={m}
              onClick={() => {
                setMode(m);
                setResult(null);
              }}
              className={`flex-1 rounded px-3 py-1.5 font-medium capitalize transition ${
                mode === m
                  ? "bg-panel text-ink shadow-sm"
                  : "text-ink-soft hover:text-ink"
              }`}
            >
              {m}
            </button>
          ))}
        </div>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={mode === "barcode" ? "e.g. 0025293001473" : "e.g. peanut butter"}
          className={`field ${mode === "barcode" ? "font-mono" : ""}`}
          required
        />

        <button
          type="submit"
          disabled={status === "loading"}
          className="btn-primary w-full"
        >
          {status === "loading" ? "Looking up…" : "Preview product"}
        </button>
      </form>

      {error && (
        <p className="mt-4 rounded-md bg-danger-soft px-3 py-2 text-sm text-danger">
          {error}
        </p>
      )}

      {result && (
        <div className="mt-5 rounded-lg border border-line bg-white p-4">
          <div className="flex gap-3">
            {result.image_url ? (
              <img
                src={result.image_url}
                alt=""
                className="h-16 w-16 rounded-md border border-line object-cover"
              />
            ) : (
              <div className="flex h-16 w-16 items-center justify-center rounded-md border border-dashed border-line text-xs text-ink-soft">
                no image
              </div>
            )}
            <div>
              <p className="font-display font-semibold text-ink">
                {result.product_name}
              </p>
              <p className="text-xs text-ink-soft">
                {result.brand || "Unknown brand"} · {result.category || "Uncategorized"}
              </p>
              <p className="mt-1 font-mono text-xs text-ink-soft">
                {result.barcode}
              </p>
            </div>
          </div>

          {result.ingredients_text && (
            <p className="mt-3 text-xs text-ink-soft line-clamp-3">
              {result.ingredients_text}
            </p>
          )}

          <div className="mt-4 grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-ink-soft">
                Price to set
              </span>
              <input
                type="number"
                step="0.01"
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                className="field font-mono"
                placeholder="0.00"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-ink-soft">
                Stock to set
              </span>
              <input
                type="number"
                min="0"
                value={stock}
                onChange={(e) => setStock(e.target.value)}
                className="field font-mono"
                placeholder="0"
              />
            </label>
          </div>
          <p className="mt-2 text-xs text-ink-soft">
            OpenFoodFacts doesn't provide pricing — set price/stock here, or
            leave blank to import at 0.
          </p>

          <button
            onClick={handleImport}
            disabled={status === "importing"}
            className="btn-primary mt-4 w-full"
          >
            {status === "importing" ? "Importing…" : "Import into inventory"}
          </button>
        </div>
      )}
    </SlideOver>
  );
}
