# Intelligent Volunteer Matching System

An AI-powered volunteer matching system that uses multi-agent architecture to connect volunteers with meaningful opportunities. Built for the Information Retrieval and Web Analytics (IT 3041) assignment.

##  Features

### Core Functionality
- **AI-Powered Matching**: Intelligent volunteer-event matching using LLMs and NLP
- **Multi-Agent Architecture**: Skill Profiler, Event Matcher, and Availability Tracker agents
- **Real-time Communication**: Agent-to-agent communication using MCP protocols
- **Comprehensive Profiles**: Detailed volunteer and organization profiles
- **Smart Recommendations**: AI-generated suggestions and insights
- **Simple Development Server**: Lightweight server for testing and development

### Technology Stack
- **Backend**: Python (FastAPI), MongoDB, OpenAI GPT, spaCy, NLTK
- **Frontend**: React, TypeScript, Material-UI, React Query
- **AI/ML**: OpenAI API, sentence-transformers, scikit-learn
- **Security**: JWT authentication, input sanitization, encryption
- **Infrastructure**: Docker, Redis (optional), Celery (optional)
- **Testing**: pytest, comprehensive test utilities, mock services

### Responsible AI Implementation
- Fairness in matching algorithms
- Transparency in AI decision-making
- Data protection and privacy
- Explainable AI recommendations
- Bias detection and mitigation

##  Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB Atlas account (or local MongoDB)
- OpenAI API key

### 1. Clone the Repository
`ash
git clone <repository-url>
cd volunteer-matching-system
`

### 2. Backend Setup
`ash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Download required NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Download spaCy model (optional but recommended)
python -m spacy download en_core_web_sm

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
`

### 3. Frontend Setup
`ash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Start development server
npm start
`

### 4. Start Backend Server

#### Option A: Full Application Server
`ash
# From backend directory
cd ../backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
`

#### Option B: Simple Development Server
`ash
# From backend directory
cd ../backend
python simple_server.py
# OR
python run_simple_server.py
`

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Simple Server: http://localhost:8000 (basic endpoints only)

##  Configuration

### Environment Variables

Create a .env file in the backend directory:

`env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://volunteer:volunteerirwa@volunteer-irwa.jvvay25.mongodb.net/?retryWrites=true&w=majority&appName=volunteer-irwa
MONGODB_USERNAME=volunteer
MONGODB_PASSWORD=volunteerirwa
DATABASE_NAME=volunteer_matching_db

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO

# Server Configuration (for simple server)
HOST=127.0.0.1
PORT=8000
RELOAD=true
`

##  System Architecture

### Multi-Agent Architecture

`
        
  Skill Profiler       Event Matcher      Availability     
     Agent                Agent              Tracker       
                                                           
  NLP Analysis        Smart Matching      Schedule Mgmt 
  Skill Extract   AI Scoring      Conflict Det. 
  Categorization      Optimization        Reminders     
        
                                                       
         
                                 
                    
                     Communication   
                      Orchestrator   
                                     
                      Message Broker
                      Event Bus     
                      Coordination  
                    
`

### Package Structure

`
backend/
 app/
    __init__.py          # Main package exports
    main.py              # FastAPI application
    config.py            # Configuration settings
    database.py          # Database connections
    api/                 # API routes
       __init__.py      # API package exports
       auth.py          # Authentication endpoints
       volunteers.py    # Volunteer endpoints
       events.py        # Event endpoints
       ...
    models/              # Data models
       __init__.py      # Model exports
       user.py          # User models
       volunteer.py     # Volunteer models
       ...
    services/            # Business logic
       __init__.py      # Service exports
       auth_service.py  # Authentication service
       matching_service.py # Matching logic
       ...
    agents/              # AI agents
       __init__.py      # Agent registry
       base_agent.py    # Base agent class
       skill_profiler.py # Skill profiling agent
       ...
    utils/               # Utility functions
       __init__.py      # Utility exports (100+ functions)
       logger.py        # Logging utilities
       validators.py    # Validation functions
       security.py      # Security utilities
    tests/               # Test suite
        __init__.py      # Test configuration
        test_utils.py    # Test utilities (618 lines)
        test_models.py   # Model tests
        test_services.py # Service tests
        test_api.py      # API tests
        test_agents.py   # Agent tests
 simple_server.py         # Simple development server
 run_simple_server.py     # Server runner script
 requirements.txt         # Python dependencies
`

### Data Flow

1. **User Registration**: Users create profiles as volunteers or organizations
2. **Profile Analysis**: Skill Profiler Agent analyzes and enhances profiles using NLP
3. **Event Creation**: Organizations create events with requirements
4. **Intelligent Matching**: Event Matcher Agent finds optimal volunteer-event pairs
5. **Availability Checking**: Availability Tracker ensures schedule compatibility
6. **AI Recommendations**: System provides explainable matching suggestions

##  API Documentation

### Simple Server Endpoints
- GET / - Root endpoint with system information
- GET /health - Health check endpoint
- GET /api/status - API status and available endpoints
- GET /api/test - Test endpoint for basic functionality

### Authentication Endpoints
- POST /api/auth/register - Register new user
- POST /api/auth/login - User login
- GET /api/auth/me - Get current user
- POST /api/auth/logout - User logout

### Volunteer Endpoints
- GET /api/volunteers - List volunteers
- POST /api/volunteers - Create volunteer profile
- GET /api/volunteers/{id} - Get volunteer details
- PUT /api/volunteers/{id} - Update volunteer profile

### Event Endpoints
- GET /api/events - List events
- POST /api/events - Create event
- GET /api/events/{id} - Get event details
- PUT /api/events/{id} - Update event

### Matching Endpoints
- POST /api/matching/find-volunteers - Find volunteers for event
- POST /api/matching/find-events - Find events for volunteer
- GET /api/matching/matches/{id} - Get match details

##  Agent System

### Agent Registry
The system includes a dynamic agent registry for easy agent management:

`python
from app.agents import get_agent, list_available_agents

# List all available agents
agents = list_available_agents()
# ['skill_profiler', 'event_matcher', 'availability_tracker', 'communication_orchestrator']

# Get a specific agent
skill_profiler = get_agent('skill_profiler')
`

### Skill Profiler Agent
- **Purpose**: Analyze and categorize volunteer skills using NLP
- **Technologies**: spaCy, NLTK, OpenAI GPT
- **Functions**:
  - Extract skills from free text
  - Categorize skills by domain
  - Validate skill levels
  - Generate improvement suggestions

### Event Matcher Agent
- **Purpose**: Intelligently match volunteers with events
- **Technologies**: Vector embeddings, cosine similarity, LLM reasoning
- **Functions**:
  - Calculate compatibility scores
  - Consider multiple factors (skills, location, availability)
  - Generate explanations for matches
  - Optimize for both volunteer and organization preferences

### Availability Tracker Agent
- **Purpose**: Manage scheduling and availability
- **Technologies**: Calendar algorithms, conflict detection
- **Functions**:
  - Track volunteer availability
  - Detect scheduling conflicts
  - Send reminders and notifications
  - Optimize event scheduling

##  Testing

### Comprehensive Test Suite

The system includes a comprehensive test suite with utilities for all components:

#### Test Utilities (pp/tests/test_utils.py)
- **TestDataFactory**: Create test data for all models
- **TestDatabaseManager**: Database testing utilities
- **TestAPIClient**: HTTP client for API testing
- **TestAssertions**: Custom assertion utilities
- **MockUtilities**: Mock creation utilities
- **Test Decorators**: Async test support, database mocking

#### Running Tests

`ash
# Run all tests
cd backend
pytest app/tests/ -v

# Run specific test categories
pytest app/tests/ -m unit -v          # Unit tests
pytest app/tests/ -m integration -v   # Integration tests
pytest app/tests/ -m api -v           # API tests
pytest app/tests/ -m database -v      # Database tests

# Run with coverage
pytest app/tests/ --cov=app --cov-report=html
`

#### Test Examples

`python
# Using test utilities
from app.tests.test_utils import TestDataFactory, TestAssertions

# Create test data
user = TestDataFactory.create_user()
volunteer = TestDataFactory.create_volunteer()
event = TestDataFactory.create_event()

# Test assertions
assert TestAssertions.assert_valid_email("test@example.com")
assert TestAssertions.assert_valid_coordinates([-74.006, 40.7128])
`

### Frontend Tests
`ash
cd frontend
npm test
`

##  Development

### Utility Functions

The system includes 100+ utility functions organized by category:

#### Data Validation
`python
from app.utils import validate_email, validate_password, validate_coordinates
`

#### Security
`python
from app.utils import hash_password, verify_password, generate_secure_token
`

#### Data Processing
`python
from app.utils import format_currency, calculate_distance, merge_dicts
`

#### Date/Time
`python
from app.utils import format_datetime, add_days_to_date, is_weekend
`

### Code Style
- Backend: Black formatter, flake8 linting
- Frontend: Prettier, ESLint
- Type checking: mypy (Python), TypeScript

### Git Workflow
`ash
# Feature development
git checkout -b feature/your-feature-name
# Make changes
git commit -m "feat: add new feature"
git push origin feature/your-feature-name
# Create pull request
`

##  Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Secure password hashing (bcrypt)

### Data Protection
- Input sanitization and validation
- SQL injection prevention
- XSS protection
- CSRF tokens

### Privacy
- Data encryption at rest and in transit
- GDPR compliance considerations
- User data anonymization options

##  Deployment

### Using Docker

1. **Build containers**:
`ash
docker-compose build
`

2. **Start services**:
`ash
docker-compose up -d
`

### Manual Deployment

1. **Backend** (Python/FastAPI):
`ash
pip install -r requirements.txt
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
`

2. **Frontend** (React):
`ash
npm run build
# Serve built files with nginx or similar
`

### Simple Server Deployment
`ash
# For development/testing
python simple_server.py

# With custom configuration
HOST=0.0.0.0 PORT=8080 python simple_server.py
`

##  Performance & Scalability

### Optimization Strategies
- Database indexing for fast queries
- Redis caching for frequently accessed data
- Asynchronous processing with Celery
- Load balancing for high availability

### Monitoring
- Application logs with structured logging
- Performance metrics collection
- Error tracking and alerting
- Health check endpoints

##  Commercialization Strategy

### Pricing Model
- **Freemium**: Basic matching for small organizations
- **Professional**: Advanced AI features, analytics (/month)
- **Enterprise**: Custom integrations, dedicated support (/month)

### Target Market
- Non-profit organizations
- Corporate volunteer programs
- Educational institutions
- Government agencies

### Revenue Streams
- Subscription fees
- Premium feature upgrades
- Custom integration services
- Training and consultation

##  Responsible AI

### Fairness
- Bias detection in matching algorithms
- Equal opportunity recommendations
- Diverse representation in training data

### Transparency
- Explainable AI decisions
- Clear matching criteria
- Algorithm audit trails

### Accountability
- Human oversight of AI decisions
- Regular model evaluation
- Feedback loops for improvement

### Privacy
- Data minimization principles
- User consent management
- Right to deletion

##  Support

### Documentation
- API docs: /docs endpoint
- Architecture diagrams in /docs folder
- Video tutorials available

### Contact
- Technical issues: Create GitHub issue
- General questions: Email support
- Urgent matters: Direct message

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- OpenAI for GPT API
- FastAPI framework
- React community
- Material-UI components
- spaCy and NLTK libraries

##  Recent Updates

### Version 1.0.0 - Latest
-  Fixed all __init__.py files with comprehensive exports
-  Created comprehensive test utilities (618 lines)
-  Fixed simple_server.py with proper FastAPI implementation
-  Added 100+ utility functions with full type hints
-  Implemented agent registry system
-  Enhanced package structure and documentation
-  Added development server for testing
-  Comprehensive error handling and logging

---

**Built with  for IT 3041 - Information Retrieval and Web Analytics**
