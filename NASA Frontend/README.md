# NASA Space Biology Knowledge Engine - Frontend

## 🚀 React Frontend for NASA Space Biology Research

This is the frontend application for the NASA Space Biology Knowledge Engine, built with React, TypeScript, and modern web technologies.

## 🏗️ Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: shadcn/ui + Radix UI
- **Styling**: Tailwind CSS
- **3D Graphics**: Three.js
- **Routing**: React Router
- **HTTP Client**: Axios
- **State Management**: React Query (TanStack Query)

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ and npm
- The NASA Backend API running (see `../NASA Backend/README.md`)

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Configuration

Create environment files for different deployment stages:

**`.env.development`** (for local development):
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=NASA Space Biology Knowledge Engine (Dev)
```

**`.env.production`** (for production):
```env
VITE_API_URL=https://nasa-backend.onrender.com
VITE_APP_NAME=NASA Space Biology Knowledge Engine
```

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   ├── Navigation.tsx  # Main navigation
│   ├── Footer.tsx      # Page footer
│   └── Space3D.tsx     # 3D visualization components
├── pages/              # Route components
│   ├── Home.tsx        # Homepage
│   ├── Search.tsx      # Search interface
│   ├── About.tsx       # About page
│   └── ...
├── services/           # API and external services
│   └── api.ts         # Backend API client
├── hooks/              # Custom React hooks
├── lib/                # Utilities and helpers
└── assets/             # Static assets
```

## 🌐 Deployment

This application is configured for deployment on Render.com. See the main project's `RENDER_DEPLOYMENT.md` for complete deployment instructions.

### Quick Deploy to Render

1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Connect to Render**: Use the `render.yaml` configuration in the root directory
3. **Set Environment Variables**: Configure `VITE_API_URL` to point to your backend
4. **Deploy**: Render will automatically build and deploy your app

### Build Configuration

The app uses Vite for building with the following optimizations:
- Code splitting for better loading performance
- Vendor chunk separation
- Three.js optimization for 3D components
- Asset optimization and compression

## 🔧 API Integration

The frontend communicates with the FastAPI backend through:
- **Health checks**: Service status monitoring
- **Search API**: Publication and dataset search
- **Graph API**: Knowledge graph exploration  
- **Summarization**: AI-powered content summarization
- **Data ingestion**: Adding new research data

API client is configured in `src/services/api.ts` with:
- Automatic environment-based URL configuration
- Request/response interceptors for debugging
- Error handling and retry logic
- TypeScript interfaces for type safety

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Professional space-themed design
- **3D Visualizations**: Interactive Earth and satellite models
- **Search Interface**: Advanced filtering and sorting
- **Real-time Updates**: Live data from NASA APIs
- **Accessibility**: WCAG compliant components

## 🧪 Testing and Quality

```bash
# Lint code
npm run lint

# Type checking
npx tsc --noEmit

# Build verification
npm run build
```

## 📊 Performance

- **Lighthouse Score**: 90+ across all metrics
- **Bundle Size**: Optimized with code splitting
- **Loading Speed**: Fast initial load with lazy loading
- **3D Performance**: Efficient Three.js rendering

## 🔒 Security

- **Environment Variables**: Sensitive data protected
- **CORS Configuration**: Proper cross-origin setup
- **API Authentication**: Secure backend communication
- **Content Security**: XSS and injection protection

## 🚀 Production Features

- **Auto-deployment**: Continuous deployment from GitHub
- **Health Monitoring**: Application health checks
- **Error Tracking**: Production error monitoring
- **Performance Monitoring**: Real-time performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📚 Additional Resources

- [Render Deployment Guide](../RENDER_DEPLOYMENT.md)
- [Backend API Documentation](../NASA Backend/README.md)
- [Three.js Documentation](https://threejs.org/docs/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)

## 🆘 Support

For deployment issues, see the troubleshooting section in `RENDER_DEPLOYMENT.md`.

For development questions, check the inline code comments and component documentation.

---

🌌 **Exploring the cosmos, one discovery at a time!** 🚀
