# GEOMETRY-PROJECT---1ST-MVP-
This is the first sprint of the geometry project to test our geometry math engine.
We're building a chatbot that:
1. Takes a geometry word problem.
2. Extracts entities (Points, Lines and Shapes).
3. Solves using math engine.
4. Visualises the results(2D First, minimal-3D).

# ARCHITECTURE.
USER INPUT PROBLEM ----> GEMINI PARSES PROBLEM ----> STRUCTURED JSON ----> MATH ENGINE PROCESS ----> OUTPUT SOLUTIONS AND FRONTEND VISUALISE.
    
### TECH STACK.
Backend: Django, Django REST Framework, Gemini API(for NLP + Reasoning).
Frontend: React, Canvas API(Canvas.js)-2D, Three.js-3D.
