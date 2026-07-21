import StockPill from "./StockPill";

export default function InventoryTable({ items, loading, onEdit, onDelete }) {
  if (loading) {
    return (
      <div className="rounded-lg border border-line bg-panel p-10 text-center">
        <div className="barcode-strip dim mx-auto w-40" />
        <p className="mt-4 font-mono text-sm text-ink-soft">Loading inventory…</p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-line bg-panel p-12 text-center">
        <div className="barcode-strip dim mx-auto w-40" />
        <p className="mt-4 font-display text-lg font-medium text-ink">
          Shelf's empty
        </p>
        <p className="mt-1 text-sm text-ink-soft">
          Add an item manually, or import one from OpenFoodFacts.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-line bg-panel">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-line bg-paper/60">
            <th className="px-4 py-3 font-display text-xs font-semibold uppercase tracking-wide text-ink-soft">
              Product
            </th>
            <th className="px-4 py-3 font-display text-xs font-semibold uppercase tracking-wide text-ink-soft">
              Barcode
            </th>
            <th className="px-4 py-3 font-display text-xs font-semibold uppercase tracking-wide text-ink-soft">
              Category
            </th>
            <th className="px-4 py-3 font-display text-xs font-semibold uppercase tracking-wide text-ink-soft">
              Price
            </th>
            <th className="px-4 py-3 font-display text-xs font-semibold uppercase tracking-wide text-ink-soft">
              Stock
            </th>
            <th className="px-4 py-3 font-display text-xs font-semibold uppercase tracking-wide text-ink-soft">
              Source
            </th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.id}
              className="border-b border-line last:border-b-0 hover:bg-shelf-soft/40"
            >
              <td className="px-4 py-3">
                <p className="font-medium text-ink">{item.product_name}</p>
                <p className="text-xs text-ink-soft">{item.brand || "—"}</p>
              </td>
              <td className="px-4 py-3 font-mono text-xs text-ink-soft">
                {item.barcode || "—"}
              </td>
              <td className="px-4 py-3 text-ink-soft">{item.category || "—"}</td>
              <td className="px-4 py-3 font-mono text-ink">
                ${Number(item.price).toFixed(2)}
              </td>
              <td className="px-4 py-3">
                <StockPill stock={item.stock} />
              </td>
              <td className="px-4 py-3">
                <span className="rounded border border-line px-2 py-0.5 font-mono text-[11px] text-ink-soft">
                  {item.source}
                </span>
              </td>
              <td className="px-4 py-3 text-right">
                <button
                  onClick={() => onEdit(item)}
                  className="mr-2 rounded-md px-2.5 py-1 text-xs font-medium text-shelf hover:bg-shelf-soft"
                >
                  Edit
                </button>
                <button
                  onClick={() => onDelete(item)}
                  className="rounded-md px-2.5 py-1 text-xs font-medium text-danger hover:bg-danger-soft"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
