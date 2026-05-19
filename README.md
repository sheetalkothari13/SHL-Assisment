# SHL Assessment Recommender  

A premium, high-fidelity conversational AI agent and dashboard that helps recruiters and hiring managers find the perfect SHL assessments through natural language dialogue.

## Key Features

1. **Intelligent Conversational Agent**: Powered by Claude 3.5 Sonnet to clarify vague queries, make curated recommendations, handle multi-turn constraint refinements, and compare tests.
2. **Interactive Glassmorphic Front-End (SPA)**: A stunning, responsive dark-mode dashboard featuring:
   - Dynamic chat module with typing indicator and direct recommendation cards.
   - Interactive turn counter (visualizing progress towards the 8-turn limit).
   - Real-time catalog browser showing measured skills, dimensions, subtests, and use cases.
   - Live filters and fuzzy search across all SHL Individual Test Solutions.
   - Quick-start scenario templates for fast testing.
3. **Robust Backend API**: Engineered in FastAPI with strict Pydantic schemas, alternating role validations, and automatic request timeouts.
4. **Scope Control**: Double-layer keyword inspection prevents out-of-scope compliance or general hiring inquiries.
5. **Full Test Suite**: Automated verification script testing schema integrity, timing, catalog completeness, and scope enforcement.

---

## Workspace Directory Structure

```
SHL Assessment/
  ├── main.py                # FastAPI Service & Static serving
  ├── agent.py               # Dialogue state logic, Claude 3.5 integrations, & recommendation parser
  ├── catalog.py             # Curated metadata dictionary of 20+ SHL assessments
  ├── static/
  │    └── index.html        # Premium, responsive HTML/JS/CSS Glassmorphic Dashboard
  ├── test_agent.py          # Complete integration test suite
  ├── requirements.txt       # Dependencies
  ├── APPROACH.md            # System architecture, strategies, and limitations
  └── README.md              # Setup and user guide
```

---

## Quick Start

### 1. Install Dependencies
Ensure you have Python 3.9+ installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory (based on `.env.template`):
```bash
GEMINI_API_KEY=your-actual-api-key-here
GEMINI_MODEL=gemini-2.5-flash
```

### 3. Run the Service
Start the FastAPI server:
```bash
python main.py
```
By default, the server runs on `http://localhost:8000`.

### 4. Open the Interface
Open your web browser and navigate to:
```
http://localhost:8000/
```
Enjoy the stunning premium dashboard! You can also view the auto-generated Swagger interactive API documentation at `http://localhost:8000/docs`.

---

## API Endpoints

### GET `/health`
Check if the service is ready.
- **Response**: `{"status": "ok"}`

### POST `/chat`
Execute a dialogue turn.
- **Request Body**:
```json
{
  "messages": [
    {"role": "user", "content": "I need to hire a software engineer."}
  ]
}
```
- **Response Body**:
```json
{
  "reply": "I can help with that! Could you tell me: what language (e.g. Java, Python, JavaScript) and what seniority level (Entry, Mid, Senior)?",
  "recommendations": [],
  "end_of_conversation": false
}
```

### GET `/catalog`
Retrieve the complete catalog database.
- **Response**: Full structured categories (Knowledge, Personality, Ability, Industry-Specific).

---

## Testing

Verify the code by running the test suite:
```bash
python test_agent.py
```
This tests:
- Catalog schema compliance
- Dialog state machine transition
- 30-second response latency
- Custom url matching and validation
- Out-of-scope query blockades

---

## Customizing the Catalog
To add new assessments, simply modify `SHL_CATALOG` in `catalog.py` using the following schema:
```python
{
    "name": "New Assessment Name",
    "code": "CODE",
    "url": "https://www.shl.com/solutions/products/...",
    "type": "K",  # K=Knowledge, P=Personality, A=Ability, I=Industry
    "description": "Short description...",
    "skills": ["Skill1", "Skill2"]
}
```
The front-end Catalog Browser and the agent will automatically update on server refresh!
