# Quickstart: Phase II — Full-Stack Web Todo Application

---

## 1. Project Setup

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.9 or higher)
- PostgreSQL (or Neon account)
- Git

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/rabia758/Q4-Hackthone2.git
cd Q4-Hackthone2

# Navigate to Phase 2 directory
cd phase-2-web-app
```

---

## 2. Backend Setup (FastAPI)

### Install Backend Dependencies
```bash
# Navigate to backend directory
cd src/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
Create `.env` file in `src/backend/`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/web_todo_app
AUTH_SECRET=your-super-secret-jwt-token-here-change-me
```

### Run Backend Server
```bash
# From src/backend directory
uvicorn main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

---

## 3. Frontend Setup (Next.js)

### Install Frontend Dependencies
```bash
# From phase-2-web-app directory (root)
npm install
```

### Environment Configuration
Create `.env.local` file in project root:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Run Frontend Development Server
```bash
# From phase-2-web-app directory (root)
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## 4. Database Setup

### Neon PostgreSQL Setup
1. Create account at [neon.tech](https://neon.tech)
2. Create a new project
3. Get connection string from Project Dashboard
4. Update `DATABASE_URL` in `.env` file

### Local PostgreSQL (Alternative)
```sql
-- Create database
CREATE DATABASE web_todo_app;

-- The application will create tables automatically on first run
```

---

## 5. API Endpoints

### Authentication
```bash
# Register new user
POST http://localhost:8000/auth/signup
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "securepassword"
}

# Login user
POST http://localhost:8000/auth/signin
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Todo Management
```bash
# Get user's todos (requires Authorization header)
GET http://localhost:8000/todos
Authorization: Bearer <jwt_token>

# Create new todo (requires Authorization header)
POST http://localhost:8000/todos
Content-Type: application/json
Authorization: Bearer <jwt_token>
{
  "title": "My Todo",
  "description": "Todo description (optional)"
}
```

---

## 6. Development Commands

### Backend Commands
```bash
# Run development server
uvicorn main:app --reload

# Run with specific port
uvicorn main:app --reload --port 8000

# Run tests (when implemented)
python -m pytest
```

### Frontend Commands
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run production server
npm run start

# Run linting
npm run lint
```

---

## 7. Project Structure
```
phase-2-web-app/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Home page
│   │   └── globals.css   # Global styles
│   ├── components/       # React components
│   ├── lib/              # Utility functions
│   └── backend/          # FastAPI backend
│       ├── main.py       # FastAPI application
│       ├── models.py     # Data models
│       ├── database.py   # Database configuration
│       ├── auth.py       # Authentication logic
│       └── requirements.txt # Python dependencies
├── public/               # Static assets
├── package.json          # Frontend dependencies
├── tsconfig.json         # TypeScript configuration
├── next.config.js        # Next.js configuration
├── tailwind.config.js    # Tailwind CSS configuration
└── .env.local            # Environment variables
```

---

## 8. Testing the Application

### Frontend Testing
1. Start backend: `cd src/backend && uvicorn main:app --reload`
2. Start frontend: `npm run dev`
3. Open browser to `http://localhost:3000`
4. Register a new account
5. Create and manage todos

### Backend API Testing
1. Use API client like Postman or curl
2. Test endpoints as documented above
3. Verify authentication and authorization work correctly

---

## 9. Common Issues & Solutions

### Port Conflicts
- Backend runs on port 8000
- Frontend runs on port 3000
- Change ports if conflicts exist:
  - Backend: `uvicorn main:app --reload --port <new_port>`
  - Frontend: `npm run dev -- --port <new_port>`

### Database Connection Issues
- Verify PostgreSQL is running
- Check connection string in `.env`
- Ensure database exists and is accessible

### CORS Issues
- Backend allows all origins in development
- Configure specific origins for production

---

## 10. Next Steps

1. Implement additional features from specification
2. Add comprehensive tests
3. Deploy to production environment
4. Set up monitoring and logging