# Abbanoa Dashboard Frontend

A modern, responsive frontend for the Abbanoa water management system, built with Next.js, TypeScript, and Tailwind CSS.

## Features

- 🚀 **Next.js 15** with App Router for optimal performance
- 📱 **Responsive Design** that works on all devices
- 🎨 **Tailwind CSS** for utility-first styling
- 🔒 **TypeScript** for type safety
- 🎣 **Custom Hooks** for data management
- 🏗️ **Modular Architecture** for scalability
- 🌙 **Dark Mode** support built-in
- 📊 **Dashboard Analytics** with real-time metrics
- 🚨 **Anomaly Detection** interface
- 📈 **Monitoring Tools** for system oversight

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Dashboard page
│   │   ├── monitoring/        # Monitoring pages
│   │   └── anomalies/         # Anomaly pages
│   ├── components/            # React components
│   │   ├── ui/                # Basic UI components
│   │   │   ├── Button.tsx
│   │   │   └── Card.tsx
│   │   ├── layout/            # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── LayoutProvider.tsx
│   │   └── features/          # Feature-specific components
│   │       └── dashboard/     # Dashboard components
│   ├── lib/                   # Utilities and configurations
│   │   ├── api/               # API client
│   │   ├── hooks/             # Custom React hooks
│   │   ├── types/             # TypeScript type definitions
│   │   └── utils/             # Utility functions
│   └── services/              # API service layer
│       ├── dashboard.service.ts
│       └── anomaly.service.ts
├── public/                    # Static assets
├── package.json
└── README.md
```

## Architecture

### API Layer
- **ApiClient**: Centralized HTTP client for backend communication
- **Services**: Feature-specific API services (Dashboard, Anomaly, etc.)
- **Hooks**: Custom React hooks for data fetching and state management

### Component Structure
- **UI Components**: Reusable, styled components (`Button`, `Card`, etc.)
- **Layout Components**: App structure components (`Header`, `Sidebar`)
- **Feature Components**: Domain-specific components (`MetricsGrid`, `RecentAnomalies`)

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Dark Mode**: Built-in dark mode support
- **Responsive**: Mobile-first responsive design

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running (typically on port 8000)

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment variables:**
   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   NEXT_PUBLIC_API_VERSION=v1
   NEXT_PUBLIC_APP_NAME=Abbanoa Dashboard
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build the application for production
- `npm run start` - Start the production server
- `npm run lint` - Run ESLint for code quality

## API Integration

The frontend communicates with the backend through a structured API layer:

### Backend Endpoints Expected
```
GET  /api/v1/dashboard/metrics      # Dashboard metrics
GET  /api/v1/dashboard/monitoring   # Monitoring data
GET  /api/v1/cache/status          # Cache status
POST /api/v1/cache/refresh         # Refresh cache
GET  /api/v1/anomalies             # List anomalies
GET  /api/v1/anomalies/:id         # Get specific anomaly
PUT  /api/v1/anomalies/:id/resolve # Resolve anomaly
POST /api/v1/anomalies/detect      # Run anomaly detection
```

### Configuration
Update the API base URL in your environment variables or in the API client configuration:

```typescript
// src/lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
```

## Components Usage

### UI Components

```tsx
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';

// Button usage
<Button variant="primary" size="md" loading={false}>
  Click me
</Button>

// Card usage
<Card>
  <CardHeader>
    <h3>Title</h3>
  </CardHeader>
  <CardContent>
    Content goes here
  </CardContent>
</Card>
```

### Custom Hooks

```tsx
import { useDashboardMetrics } from '@/lib/hooks/useDashboard';
import { useAnomalies } from '@/lib/hooks/useAnomalies';

function MyComponent() {
  const { metrics, loading, error } = useDashboardMetrics();
  const { anomalies, resolveAnomaly } = useAnomalies();
  
  // Use the data in your component
}
```

### Services

```tsx
import { DashboardService } from '@/services/dashboard.service';
import { AnomalyService } from '@/services/anomaly.service';

// Direct service usage
const metrics = await DashboardService.getMetrics();
const anomalies = await AnomalyService.getAnomalies();
```

## Deployment

### Production Build
```bash
npm run build
npm run start
```

### Docker Deployment
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables for Production
```env
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
NEXT_PUBLIC_API_VERSION=v1
NODE_ENV=production
```

## Development Guidelines

### Adding New Pages
1. Create page component in `src/app/[page-name]/page.tsx`
2. Add navigation entry in `src/components/layout/Sidebar.tsx`
3. Create any necessary service methods
4. Add custom hooks if needed

### Adding New API Endpoints
1. Update type definitions in `src/lib/types/index.ts`
2. Add service methods in appropriate service file
3. Create custom hooks in `src/lib/hooks/`
4. Update API client if needed

### Component Development
- Use TypeScript for all components
- Follow the established naming conventions
- Include proper prop types and documentation
- Implement responsive design with Tailwind classes
- Support dark mode with appropriate color schemes

## Performance Considerations

- **Code Splitting**: Automatic with Next.js App Router
- **Image Optimization**: Use Next.js Image component
- **Bundle Analysis**: Run `npm run build` to see bundle sizes
- **Caching**: Leverage Next.js built-in caching strategies

## Contributing

1. Follow the established project structure
2. Use TypeScript for type safety
3. Write responsive, accessible components
4. Test on both light and dark modes
5. Ensure all API integrations are properly typed

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Verify backend is running
   - Check API_BASE_URL environment variable
   - Ensure CORS is configured on backend

2. **Build Errors**
   - Check TypeScript errors: `npm run lint`
   - Verify all imports are correct
   - Ensure all required environment variables are set

3. **Styling Issues**
   - Verify Tailwind classes are correct
   - Check for dark mode compatibility
   - Ensure responsive breakpoints are working

## Next Steps

The frontend skeleton is ready for development. Key areas for enhancement:

1. **Authentication**: Add user authentication and authorization
2. **Charts & Graphs**: Integrate charting libraries for data visualization
3. **Real-time Updates**: Implement WebSocket connections for live data
4. **Testing**: Add unit and integration tests
5. **PWA Features**: Convert to Progressive Web App
6. **Internationalization**: Add multi-language support

## Support

For questions or issues, please refer to the main project documentation or create an issue in the project repository.
