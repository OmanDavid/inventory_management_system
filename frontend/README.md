# Stockline — React Frontend

React (Vite) admin UI for the [inventory_management_system](../) Flask API.
Talks to the API over HTTP/CORS as a separate app — two servers, one for the
API and one for the frontend.

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # adjust VITE_API_URL if your API isn't on :5000
npm run dev
```

Runs at http://localhost:5173. Make sure the Flask API is running first
(`python run.py` from the project root, on port 5000) — the app needs it to
load data.

## What it does

- Lists inventory items in a table (product, barcode, category, price, stock, source)
- Add / edit / delete items, backed by `POST /inventory`, `PATCH /inventory/<id>`, `DELETE /inventory/<id>`
- Preview + import products from OpenFoodFacts via `GET /inventory/lookup` and `POST /inventory/import`,
  by barcode or product name, with price/stock set before importing
- Client-side search across name, brand, barcode, category
- Shows API connection status (health-checks `GET /health`)

## Structure

```
frontend/
  src/
    api.js                    API client — wraps every Flask endpoint
    App.jsx                   Top-level state and layout
    components/
      Header.jsx               Wordmark + live API health pill
      InventoryTable.jsx        Item list
      ItemFormPanel.jsx         Add/edit slide-over form
      LookupImportPanel.jsx     OpenFoodFacts lookup/import slide-over
      SlideOver.jsx             Reusable slide-over panel
      StockPill.jsx             In stock / low stock / out of stock badge
      Toast.jsx                 Success/error notifications
```

## Build for production

```bash
npm run build
```

Outputs static files to `dist/`. Since this setup keeps the frontend and
API as separate servers, `dist/` would need its own static host (Netlify,
Vercel, `serve`, etc.) pointed at the deployed API via `VITE_API_URL`.
