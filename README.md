# GEOMETRY Project - 1st MVP

GEOMETRY is a natural-language geometry solving application. It accepts geometry word problems, converts them into structured mathematical intent, solves them through the backend Geometry Math Engine, and visualizes the result in 2D or 3D.

This chatbot is an MVP and testbed for the custom Geometry Math Engine. The long-term project is an adaptive geometry-learning platform that will teach learners from beginner to advanced levels through personalized teaching, interactive geometry, animations, simulations, guided explanations, practice, and adaptive progression.

The MVP focuses on reliable semantic routing: the system must solve the operation the user actually requested, not a simpler related operation. For example, a cylinder volume problem must not be solved as circle area, and a cone height/volume problem must not be reduced to a final Pythagorean triangle answer.

## Architecture

![Architecture Diagram](./assets/Geo.png)

```text
User question
-> Gemini interpretation provider
-> structured semantic problem / operation JSON
-> backend validation and solution planning
-> Geometry Math Engine
-> authoritative result
-> explanation builder
-> visualization adapter
-> React frontend
-> Canvas 2D or Three.js 3D visualization
-> saved History replay when appropriate
```

### Backend Responsibilities

- Receive direct operation requests or natural-language word problems.
- Use Gemini only to interpret the user's geometry intent.
- Normalize parsed data into supported backend operation names and parameters.
- Validate operation compatibility, required parameters, and geometry constraints.
- Use the Geometry Math Engine as the authoritative calculation layer.
- Build student-friendly explanations.
- Produce visualization payloads for the frontend.
- Persist successful solves to anonymous session-based History.
- Expose backend-driven Topics from actual supported engine capabilities.

### Frontend Responsibilities

- Provide the chat-style solving interface.
- Display final results and structured explanations.
- Render 2D diagrams with Canvas.
- Render 3D geometry with Three.js.
- Let users browse Topics and prefill example questions.
- Let users restore History items without re-calling Gemini.
- Never calculate authoritative mathematical answers.

## Tech Stack

### Backend

- Python
- Django
- Django REST Framework
- Google GenAI SDK for Gemini interpretation
- python-dotenv for local environment configuration
- NumPy and SciPy for advanced math-engine modules
- SQLite for local development

### Frontend

- React
- Vite
- Three.js
- KaTeX / react-katex
- Playwright for frontend visual smoke tests

## Project Structure

```text
.
|-- Backend/
|   |-- .env
|   `-- geometry/
|       |-- manage.py
|       |-- geometry/
|       `-- euclidean/
|           |-- Math_Engine/
|           |-- parser/
|           |-- solver/
|           |-- migrations/
|           |-- explanations.py
|           |-- topics.py
|           `-- views.py
|-- Frontend/
|   |-- package.json
|   `-- src/
|       |-- components/
|       `-- services/
|-- assets/
|   `-- Geo.png
`-- README.md
```

## Prerequisites

Install these before running the project:

- Python 3.12 or newer
- Node.js 20 or newer
- npm
- A valid Gemini API key

## Backend Setup

From the repository root:

```powershell
cd Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install django djangorestframework google-genai python-dotenv numpy scipy
```

This repository currently does not include a committed `requirements.txt`. If one is added later, prefer:

```powershell
python -m pip install -r requirements.txt
```

Create or update `Backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_PRIMARY_MODEL=gemini-3.6-flash
GEMINI_FALLBACK_MODEL=gemini-3.5-flash
LLM_FALLBACK_ENABLED=false
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver
```

Do not commit real API keys.

Run database migrations:

```powershell
cd Backend\geometry
python manage.py migrate
```

Start the backend server:

```powershell
python manage.py runserver 127.0.0.1:8000
```

Backend health check:

```text
http://127.0.0.1:8000/api/health/
```

Core backend endpoints:

```text
POST   /api/solve/
GET    /api/history/
GET    /api/history/<id>/
DELETE /api/history/<id>/
DELETE /api/history/
GET    /api/topics/
```

## Frontend Setup

Open a second terminal from the repository root:

```powershell
cd Frontend
npm install
npm run dev
```

The frontend will usually run at:

```text
http://127.0.0.1:5173/
```

## Running the Full Project

Use two terminals.

Terminal 1 - backend:

```powershell
cd Backend\geometry
python manage.py runserver 127.0.0.1:8000
```

Terminal 2 - frontend:

```powershell
cd Frontend
npm run dev
```

Then open:

```text
http://127.0.0.1:5173/
```

## Testing

Run backend tests:

```powershell
cd Backend\geometry
python manage.py test euclidean
```

Run Django system checks:

```powershell
cd Backend\geometry
python manage.py check
```

Build the frontend:

```powershell
cd Frontend
npm run build
```

Run the Playwright visual smoke tests:

```powershell
cd Frontend
npx playwright test phase3.visual.spec.js
```

If Playwright browsers are not installed yet:

```powershell
cd Frontend
npx playwright install
```

## Supported MVP Operation Areas

The current MVP supports a growing set of Euclidean and analytical geometry operations, including:

- distance between two points
- midpoint
- slope
- circle area and circumference
- circle-circle intersection
- triangle area, perimeter, and missing angle
- Pythagorean theorem
- rectangle area and perimeter
- geometric transformations
- 3D distance, midpoint, vectors, lines, triangles, planes, and cuboid volume
- cylinder volume and surface-area operations
- cone height derivation and cone volume planning

## History

History stores successful solved problems for the current anonymous browser session. Each record stores the original question or direct-operation label, operation metadata, result JSON, explanation JSON, and visualization JSON.

Opening a History item restores the saved structured response directly in the frontend. It does not send the old question back through Gemini, which avoids extra AI cost, quota use, and interpretation drift.

Failed provider calls, unsupported operations, invalid geometry, and incomplete requests are not saved.

## Topics

Topics provide a compact map of the chatbot MVP's supported geometry areas. Topic data is served by the backend from centralized metadata and checked against the current operation registry.

Topic statuses:

- `available`: exposed through the chatbot and backed by registered operations
- `partial`: some operations in the area are available
- `experimental`: engine modules exist, but the chatbot does not fully expose them yet
- `coming_later`: not supported in this MVP

Clicking a topic example returns to the solver and places the example question in the input. It does not automatically submit, so the learner can edit it first.

## Semantic Routing Rule

The solver follows this rule:

```text
Supported requested operation -> solve correctly
Unsupported requested operation -> return a controlled unsupported-operation error
Never silently solve a related easier problem
```

Gemini is responsible for interpreting intent. The backend is responsible for validation, planning, mathematical execution, and request-satisfaction checks.

## Current Limitations

- The chatbot is anonymous-session based; there is no production user account system yet.
- History is local to the current browser session cookie.
- Gemini availability and quota can affect new natural-language interpretations.
- Advanced engine areas such as topology, non-Euclidean geometry, computational geometry, and differential geometry are not fully exposed through the MVP chatbot.
- The system is not a full adaptive learning platform yet; it is the working chatbot foundation for that larger product.
