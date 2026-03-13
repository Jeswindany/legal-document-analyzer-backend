# Legal Document Analyzer Backend

## How can I run this code?

If you want to work locally using your own IDE, you can clone this repo.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

To run the frontend:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <GIT_URL>

# Step 2: Navigate to the project directory.
cd legal-document-analyzer-backend

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

To run the backend:

```sh
# Step 1: Navigate to fast api folder
cd api

# Step 2: Download necessary dependencies
pip install -r requirements.txt

# Step 3: Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS
