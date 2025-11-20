# Regnova Frontend

Modern Next.js 14 frontend for the Regnova Knowledge Assistant.

## Features

✅ **Authentication** - Login & Register with JWT
✅ **File Upload** - PDF upload with progress tracking
✅ **Web Scraping** - URL input for content extraction
✅ **AI Chat** - Real-time chat with SSE streaming
✅ **Source Citations** - Grounded answers with references
✅ **Export** - JSON and PDF export functionality
✅ **Responsive Design** - Mobile-first Tailwind CSS
✅ **Dark Mode Ready** - Theme switching support

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: ShadCN UI (Radix UI)
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Visit http://localhost:3000

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js app router
│   │   ├── auth/              # Auth pages
│   │   ├── dashboard/         # Dashboard
│   │   ├── upload/            # Upload page
│   │   ├── chat/              # Chat interface
│   │   └── profile/           # User profile
│   ├── components/            # React components
│   │   └── ui/                # ShadCN UI components
│   ├── hooks/                 # Custom React hooks
│   ├── lib/                   # Utilities & config
│   │   ├── api.ts            # API client
│   │   ├── store.ts          # Zustand stores
│   │   ├── export.ts         # Export utilities
│   │   └── utils.ts          # Helper functions
│   └── public/                # Static assets
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## API Integration

The frontend connects to the backend API:
- Auth endpoints: `/api/auth/*`
- File endpoints: `/api/upload/*`
- Chat endpoints: `/api/chat/*`
- Automation endpoints: `/api/automations/*`

All requests automatically include JWT tokens.

## Features

### Authentication
- Login with email/password
- Register new account
- JWT token management
- Auto-redirect on 401

### File Management
- Upload PDFs (up to 50MB)
- Scrape URLs
- View file list
- Delete files
- File metadata view

### Chat Interface
- Real-time SSE streaming
- Source-grounded answers
- Dual RAG modes (fast/accurate)
- Chat history
- Export conversations

### Export
- Export chat to JSON
- Export chat to PDF
- Download with formatted content

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## License

MIT License

## Support

For issues and questions:
- Check backend: http://localhost:8000/api/docs
- Review logs in browser console
- Check network tab for API calls
