export default function StockPill({ stock }) {
  let tone = "shelf";
  let label = "In stock";
  if (stock <= 0) {
    tone = "danger";
    label = "Out of stock";
  } else if (stock <= 5) {
    tone = "alert";
    label = "Low stock";
  }

  const toneClasses = {
    shelf: "bg-shelf-soft text-shelf",
    alert: "bg-alert-soft text-alert",
    danger: "bg-danger-soft text-danger",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${toneClasses[tone]}`}
    >
      <span className="font-mono">{stock}</span>
      <span className="opacity-80">· {label}</span>
    </span>
  );
}
