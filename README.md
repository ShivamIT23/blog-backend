# Blog Backend API

A FastAPI-based backend for a blog application with user authentication, post management, and file upload capabilities.

## Features

- 🔐 JWT-based authentication
- 👤 User management (registration, login, profile photo)
- 📝 Post management (CRUD operations)
- 📊 Post count tracking (max 50 posts per user)
- 🖼️ Cloudinary integration for image uploads
- 🗄️ MongoDB database with Motor async driver

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt with passlib
- **File Upload**: Cloudinary
- **Validation**: Pydantic

## Setup

### Prerequisites

- Python 3.8+
- MongoDB instance
- Cloudinary account

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd blog-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=blog
JWT_SECRET=your_jwt_secret_key
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

5. Run the application:
```bash
uvicorn app.main:api --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Docker

To run with Docker:

```bash
docker build -t blog-backend .
docker run -p 5000:5000 blog-backend
```

## License

This project is licensed under the MIT License.


Hello