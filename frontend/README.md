# Frontend Development

## Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── layout/        # Layout, Sidebar, Header
│   ├── pages/             # Page components
│   ├── services/          # API client services
│   ├── theme/             # Material-UI theme
│   ├── App.tsx            # Main app component
│   └── index.tsx          # Entry point
├── package.json
└── vite.config.ts
```

## Features Implemented

- ✅ Databricks theme (Material-UI)
- ✅ Layout with sidebar navigation
- ✅ Dashboard/Analytics page
- ✅ Customers list and detail pages
- ✅ Campaigns list and builder
- ✅ API service layer with React Query
- ✅ Responsive design

## API Integration

The frontend uses React Query for data fetching and caching. All API calls go through the `apiClient` which:
- Automatically adds `X-Tenant-ID` header
- Handles authentication tokens
- Provides error handling

## Environment Variables

Create `.env` file:
```
VITE_API_URL=http://localhost:8000/api
```

## Building for Production

```bash
npm run build
```

Output will be in `frontend/dist/` directory.

