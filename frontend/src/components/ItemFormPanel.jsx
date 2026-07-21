import { useEffect, useState } from "react";
import SlideOver from "./SlideOver";

const EMPTY = {
  product_name: "",
  brand: "",
  barcode: "",
  category: "",
  price: "",
  stock: "",
  ingredients_text: "",
  image_url: "",
};

export default function ItemFormPanel({ open, item, onClose, onSubmit, error }) {
  const [form, setForm] = useState(EMPTY);
  const isEdit = Boolean(item);

  useEffect(() => {
    if (item) {
      setForm({
        product_name: item.product_name || "",
        brand: item.brand || "",
        barcode: item.barcode || "",
        category: item.category || "",
        price: item.price ?? "",
        stock: item.stock ?? "",
        ingredients_text: item.ingredients_text || "",
        image_url: item.image_url || "",
      });
    } else {
      setForm(EMPTY);
    }
  }, [item, open]);

  const set = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      price: form.price === "" ? 0 : Number(form.price),
      stock: form.stock === "" ? 0 : Number(form.stock),
    };
    onSubmit(payload, item?.id);
  };

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit item" : "Add item"}
      subtitle={
        isEdit
          ? `Updating "${item.product_name}"`
          : "Add a product manually to the shelf"
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <p className="rounded-md bg-danger-soft px-3 py-2 text-sm text-danger">
            {error}
          </p>
        )}
        <Field label="Product name" required>
          <input
            required
            value={form.product_name}
            onChange={set("product_name")}
            className="field"
            placeholder="Organic Almond Milk"
          />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Brand">
            <input value={form.brand} onChange={set("brand")} className="field" />
          </Field>
          <Field label="Category">
            <input
              value={form.category}
              onChange={set("category")}
              className="field"
            />
          </Field>
        </div>
        <Field label="Barcode">
          <input
            value={form.barcode}
            onChange={set("barcode")}
            className="field font-mono"
          />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Price (USD)">
            <input
              type="number"
              step="0.01"
              min="0"
              value={form.price}
              onChange={set("price")}
              className="field font-mono"
            />
          </Field>
          <Field label="Stock (units)">
            <input
              type="number"
              min="0"
              value={form.stock}
              onChange={set("stock")}
              className="field font-mono"
            />
          </Field>
        </div>
        <Field label="Ingredients">
          <textarea
            value={form.ingredients_text}
            onChange={set("ingredients_text")}
            className="field h-20 resize-none"
          />
        </Field>
        <Field label="Image URL">
          <input
            value={form.image_url}
            onChange={set("image_url")}
            className="field"
          />
        </Field>

        <div className="flex gap-2 pt-2">
          <button type="submit" className="btn-primary flex-1">
            {isEdit ? "Save changes" : "Add to inventory"}
          </button>
          <button type="button" onClick={onClose} className="btn-ghost">
            Cancel
          </button>
        </div>
      </form>
    </SlideOver>
  );
}

function Field({ label, required, children }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-ink-soft">
        {label} {required && <span className="text-danger">*</span>}
      </span>
      {children}
    </label>
  );
}
