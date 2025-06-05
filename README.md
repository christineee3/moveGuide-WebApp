# moveGuide WebApp

Deployment of a House price prediction model in a web application moveGuide FYP @ QMUL

- User fills in a form, selecting a location, desired amentities for a property, mode of transport, school types
- Recieves statistcal summaries for the area visualised in graph form, and a price forecast  

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/christineee3/moveGuide-WebApp.git

2. Setup backend
    ```bash
    cd backend
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python app.py
    
note: The XGboost model will take a moment to download when the backend starts, the app will not will not function until this is complete.  

3. Setup frontend
   ```bash
   cd frontend
   npm install
   npm run serve

4. Open the app
   
     http://localhost:8080



   
