# Setlist 🎵

A music playing platform + promotion tool + networking tool for local bands.

## Vision

Setlist is designed to be a mobile-friendly web app that will eventually become a full mobile application. It serves as a comprehensive platform for local music communities, connecting artists, promoters, venues, and music lovers.

## User Types & Features

### Artists/DJs/Bands
- Basic profile information
- Upload demos and music
- Stream music from the app
- Upload or link to YouTube videos (with Google OAuth)
- Collaborate with other artists

### Promoters/Venues
- Find bands by genre for shows
- Secure in-app communication with bands
- Create show bills and export for social media

### Regular Users
- Discover shows and bands
- Find local music
- Create playlists from app music
- Upvote favorite tracks

## Tech Stack

### Backend
- **Python 3.11+** with comprehensive typing
- **FastAPI** for minimal, fast API development
- **Pydantic** for data validation
- **SQLAlchemy** for database operations
- **Alembic** for database migrations

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **React Query** for state management
- **React Router** for navigation

### Database
- **Supabase** (PostgreSQL)
- **Row Level Security** for data protection

### Testing
- **pytest** for backend testing
- **Jest + React Testing Library** for frontend testing
- **Test Driven Development** approach

## Project Structure

```
setlist/
├── backend/                 # FastAPI backend
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   ├── tests/
│   └── package.json
├── shared/                 # Shared types and utilities
├── docker-compose.yml      # Development environment
└── README.md
```

## Development Approach

We follow **Test Driven Development (TDD)** with the Red-Green-Refactor cycle:
1. **Red**: Write failing tests first
2. **Green**: Write minimal code to pass tests
3. **Refactor**: Clean up and optimize code

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Supabase account

### Quick Start
1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your Supabase credentials
3. Run `docker-compose up` to start the development environment
4. Backend will be available at `http://localhost:8000`
5. Frontend will be available at `http://localhost:3000`

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Run All Tests
```bash
npm run test:all
```

## Contributing

1. Write tests first (Red)
2. Implement minimal functionality (Green)
3. Refactor and optimize (Refactor)
4. Ensure all tests pass
5. Submit pull request

## License

MIT License - see LICENSE file for details
