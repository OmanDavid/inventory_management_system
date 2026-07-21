export default function Toast({ toast }) {
  if (!toast) return null;
  const isError = toast.type === "error";
  return (
    <div
      role="status"
      className={`fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-lg border px-4 py-2.5 text-sm font-medium shadow-lg ${
        isError
          ? "border-danger/30 bg-danger-soft text-danger"
          : "border-shelf/30 bg-shelf-soft text-shelf"
      }`}
    >
      {toast.message}
    </div>
  );
}
