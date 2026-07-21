import { useEffect, useState, useCallback } from "react";
import Header from "./components/Header";
import InventoryTable from "./components/InventoryTable";
import ItemFormPanel from "./components/ItemFormPanel";
import LookupImportPanel from "./components/LookupImportPanel";
import Toast from "./components/Toast";
import { api, ApiError } from "./api";

export default function App() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [healthy, setHealthy] = useState(false);
  const [search, setSearch] = useState("");

  const [formOpen, setFormOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formError, setFormError] = useState("");

  const [lookupOpen, setLookupOpen] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listItems();
      setItems(data);
      setHealthy(true);
    } catch (err) {
      setHealthy(false);
      if (!(err instanceof ApiError && err.status === 0)) {
        showToast(err.message, "error");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    api
      .health()
      .then(() => setHealthy(true))
      .catch(() => setHealthy(false));
  }, [refresh]);

  const openAdd = () => {
    setEditingItem(null);
    setFormError("");
    setFormOpen(true);
  };

  const openEdit = (item) => {
    setEditingItem(item);
    setFormError("");
    setFormOpen(true);
  };

  const handleFormSubmit = async (payload, id) => {
    setFormError("");
    try {
      if (id) {
        await api.updateItem(id, payload);
        showToast("Item updated");
      } else {
        await api.createItem(payload);
        showToast("Item added");
      }
      setFormOpen(false);
      refresh();
    } catch (err) {
      setFormError(err.message);
    }
  };

  const handleDelete = async (item) => {
    if (!window.confirm(`Delete "${item.product_name}"?`)) return;
    try {
      await api.deleteItem(item.id);
      showToast("Item deleted");
      refresh();
    } catch (err) {
      showToast(err.message, "error");
    }
  };

  const handleImported = () => {
    showToast("Product imported");
    refresh();
  };

  const filtered = items.filter((item) => {
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return (
      item.product_name?.toLowerCase().includes(q) ||
      item.brand?.toLowerCase().includes(q) ||
      item.barcode?.toLowerCase().includes(q) ||
      item.category?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="min-h-screen pb-20">
      <Header healthy={healthy} itemCount={items.length} />

      <main className="mx-auto max-w-6xl px-6 py-8">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, brand, barcode, category…"
            className="field max-w-sm"
          />
          <div className="flex gap-2">
            <button onClick={() => setLookupOpen(true)} className="btn-ghost">
              Import from OpenFoodFacts
            </button>
            <button onClick={openAdd} className="btn-primary">
              + Add item
            </button>
          </div>
        </div>

        <InventoryTable
          items={filtered}
          loading={loading}
          onEdit={openEdit}
          onDelete={handleDelete}
        />
      </main>

      <ItemFormPanel
        open={formOpen}
        item={editingItem}
        error={formError}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
      />

      <LookupImportPanel
        open={lookupOpen}
        onClose={() => setLookupOpen(false)}
        onImported={handleImported}
      />

      <Toast toast={toast} />
    </div>
  );
}
