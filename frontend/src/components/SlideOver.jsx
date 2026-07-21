export default function SlideOver({ open, title, subtitle, onClose, children }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div
        className="absolute inset-0 bg-ink/30 backdrop-blur-[1px]"
        onClick={onClose}
      />
      <div className="relative flex h-full w-full max-w-md flex-col bg-panel shadow-xl">
        <div className="border-b border-line px-6 py-5">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="font-display text-xl font-semibold text-ink">
                {title}
              </h2>
              {subtitle && (
                <p className="mt-0.5 text-sm text-ink-soft">{subtitle}</p>
              )}
            </div>
            <button
              onClick={onClose}
              aria-label="Close panel"
              className="rounded-md p-1 text-ink-soft hover:bg-paper hover:text-ink"
            >
              ✕
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-5">{children}</div>
      </div>
    </div>
  );
}
