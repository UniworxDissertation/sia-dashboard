
# SIA Dashboard

This project is designed to provide a Sustainable Investment Analysis dashboard with integrated ESG metrics, financial data, and market sentiment. Below are the steps to run the project locally.

## Prerequisites

- Python 3.x
- Node.js
- Git

## Steps to Run the Project

1. **Clone the Repository**  
   Clone the repository to your local machine:

   ```bash
   git clone https://github.com/UniworxDissertation/sia-dashboard.git
   ```

2. **Backend Setup**  
   Follow the steps below to set up the backend:

   - Navigate to the `backend` directory:

     ```bash
     cd sia-dashboard/backend
     ```

   - Create a virtual environment:

     ```bash
     python -m venv venv
     ```

   - Activate the virtual environment:

     - On Windows:

       ```bash
       venv\Scripts\activate
       ```

     - On Mac/Linux:

       ```bash
       source venv/bin/activate
       ```

   - Install the required Python packages:

     ```bash
     pip install -r requirements.txt
     ```

   - Run database migrations:

     ```bash
     python manage.py migrate
     ```

   - Start the Django development server:

     ```bash
     python manage.py runserver
     ```

3. **Frontend Setup**  
   Follow the steps below to set up the frontend:

   - Navigate to the `frontend` directory:

     ```bash
     cd ../frontend
     ```

   - Install the required npm packages:

     ```bash
     npm install
     ```

   - Start the React development server:

     ```bash
     npm start
     ```

4. **Access the Application**  
   Once both the backend and frontend servers are running, open your web browser and go to:

   ```
   http://localhost:3000
   ```

   This will load the dashboard interface where you can interact with the features of the project.

## Additional Information

- The backend is powered by Django.
- The frontend is built using React.
