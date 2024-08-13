# Masterblog API

## Overview

Masterblog API is a simple RESTful API built with Flask that allows you to manage blog posts and comments. This project includes features to create, read, update, delete posts, and add comments to posts. The backend is complemented by a frontend application that interacts with the API to display posts and comments, and allows users to add new posts and comments.

## Features

- **Create, Read, Update, Delete (CRUD) Posts**
- **Add Comments to Posts**
- **Sort and Paginate Posts**
- **Rate Limiting**
- **Cross-Origin Resource Sharing (CORS) Enabled**

## Technologies Used

- **Flask**: Python web framework for building the API.
- **Flask-Limiter**: To apply rate limiting to API endpoints.
- **Flask-CORS**: To handle cross-origin requests.
- **JavaScript**: For frontend interactions and dynamic content loading.

## Getting Started

### Prerequisites

- **Python 3.x**: Ensure Python 3 is installed on your machine.
- **Pip**: Python package installer.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/blog-api.git
   cd blog-api
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a `posts.json` file in the root directory (if it doesn't exist) with the following content:**
   ```json
   []
   ```

### Running the API

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

   The server will run on `http://127.0.0.1:5002`.

### Frontend

1. **Open `index.html`** in a web browser. Ensure that the API base URL is set correctly in the browser’s local storage.

2. **Use the interface** to add, view, update, and delete posts, as well as add comments.

### API Endpoints

- **GET `/api/posts`**: Retrieve a list of posts.
- **POST `/api/posts`**: Create a new post.
- **GET `/api/posts/<post_id>`**: Retrieve a specific post.
- **PUT `/api/posts/<post_id>`**: Update a specific post.
- **DELETE `/api/posts/<post_id>`**: Delete a specific post.
- **POST `/api/posts/<post_id>/comments`**: Add a comment to a specific post.
- **GET `/api/posts/search`**: Search for posts by title or content.

### Example Usage

- **Add a New Post:**
  ```bash
  curl -X POST http://127.0.0.1:5002/api/posts -H "Content-Type: application/json" -d '{"title": "My First Post", "content": "This is the content of my first post."}'
  ```

- **Add a Comment:**
  ```bash
  curl -X POST http://127.0.0.1:5002/api/posts/1/comments -H "Content-Type: application/json" -d '{"comment": "Great post!"}'
  ```

## Contributing

If you'd like to contribute to this project, please fork the repository and submit a pull request with your changes. Be sure to follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to the branch.
5. Open a pull request.



