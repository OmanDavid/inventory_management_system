export default function Header({ healthy, itemCount }) {
  return (
    <header>
      <div className="mx-auto max-w-6xl px-6 pt-8">
        <div className="flex items-end justify-between">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.25em] text-ink-soft">
              admin console
            </p>
            <h1 className="font-display text-4xl font-bold tracking-tight text-ink">
              Stockline
            </h1>
          </div>
          <div className="flex items-center gap-4 pb-1">
            <span className="font-mono text-xs text-ink-soft">
              {itemCount} item{itemCount === 1 ? "" : "s"} tracked
            </span>
            <span
              className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${
                healthy
                  ? "border-shelf/30 bg-shelf-soft text-shelf"
                  : "border-danger/30 bg-danger-soft text-danger"
              }`}
            >
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  healthy ? "bg-shelf" : "bg-danger"
                }`}
              />
              {healthy ? "API online" : "API unreachable"}
            </span>
          </div>
        </div>
      </div>
      <div className="mt-6 barcode-strip" />
    </header>
  );
}
