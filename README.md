# PCKonfigApp - PC Build Optimizer

A sophisticated web application for building and optimizing PC configurations with AI-powered recommendations.

## 🚀 Features

- **PC Builder**: Interactive component selection with real-time pricing
- **AI Optimization**: ChromaDB + OpenAI powered build recommendations
- **Build Gallery**: Share and browse community builds
- **User Authentication**: Secure registration and login system
- **Build Management**: Save, edit, and manage your PC builds
- **Compatibility Analysis**: Automatic compatibility checking and suggestions

## 🏗️ Architecture

### Backend
- **FastAPI**: High-performance async Python web framework
- **PostgreSQL**: Reliable relational database for user data and components
- **ChromaDB**: Vector database for AI-powered component recommendations
- **OpenAI**: GPT integration for intelligent build optimization
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations

### Frontend
- **React 18**: Modern UI with hooks and context
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **React Router**: Client-side routing

### Deployment
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and static file serving

## 🔧 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.12+ (for development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd pckonfigApp
cp .env.example backend/app/.env
# Edit .env with your configuration
```

### 2. Database Setup
```bash
# Start PostgreSQL and ChromaDB
docker-compose up -d db chromadb

# Run database migrations
cd backend
python -m alembic upgrade head
```

### 3. Start Development Servers
```bash
# Backend
cd backend/app
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### 4. Production Deployment
```bash
docker-compose up -d
```

## 🔒 Security Features

- **Rate Limiting**: Protection against brute force attacks
- **CORS Protection**: Restricted origins for API access
- **Password Validation**: Strong password requirements
- **Secure Authentication**: Bcrypt password hashing
- **Input Validation**: Pydantic schemas for data validation

## ⚡ Performance Optimizations

- **Database Query Optimization**: Efficient SQL queries with proper indexing
- **Lazy Loading**: React components loaded on demand
- **Caching**: Component data caching to reduce database load
- **Pagination**: Efficient data loading for large datasets
- **Error Boundaries**: Graceful error handling in React

## 📁 Project Structure

```
pckonfigApp/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/    # API routes
│   │   ├── core/            # Security, config, dependencies
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── main.py         # FastAPI application
│   ├── ChromaDB/           # Vector database setup
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context providers
│   │   └── App.jsx        # Main application
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Vite configuration
├── nginx/                 # Nginx configuration
├── docker-compose.yml     # Container orchestration
└── README.md             # This file
```

## 🛠️ Development

### Backend Development
```bash
cd backend/app
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --port 8000

# Create database migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend Development
```bash
cd frontend
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📊 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

- `DB_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Docker Configuration

The application uses Docker Compose with the following services:
- `frontend`: React application served by Nginx
- `backend`: FastAPI application
- `db`: PostgreSQL database
- `chromadb`: Vector database for AI features

## 🚀 Deployment

### Production Deployment
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Scaling
```bash
# Scale backend instances
docker-compose up -d --scale backend=3
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

## 🎯 Recent Improvements

### Security Enhancements
- ✅ Implemented rate limiting on authentication endpoints
- ✅ Restricted CORS origins for better security
- ✅ Added password strength validation
- ✅ Improved error handling and logging

### Performance Optimizations
- ✅ Added database query optimization with eager loading
- ✅ Implemented React lazy loading for better initial load times
- ✅ Added loading states and error boundaries
- ✅ Optimized component data caching

### Code Quality
- ✅ Refactored large functions into smaller, maintainable pieces
- ✅ Added comprehensive error boundaries
- ✅ Improved type safety with Pydantic schemas
- ✅ Enhanced documentation and code comments

### Developer Experience
- ✅ Created comprehensive environment variable documentation
- ✅ Added development setup instructions
- ✅ Improved project structure documentation
- ✅ Added testing guidelines 