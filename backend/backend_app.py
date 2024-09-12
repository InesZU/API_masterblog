from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Initialize Limiter to apply rate limits to API endpoints
limiter = Limiter(
    get_remote_address,  # Function to identify clients by IP address
    app=app  # Pass the Flask app instance
)

DATA_FILE = 'posts.json'


def read_data():
    """Read data from the JSON file.

    If the file does not exist, create an empty file and return an empty list.
    Also handle file reading errors such as JSON decoding issues.

    Returns:
        list: List of posts stored in the JSON file.
    """
    if not os.path.isfile(DATA_FILE):
        # Create an empty file if it doesn't exist
        with open(DATA_FILE, 'w', encoding='utf8') as file:
            json.dump([], file)
        return []

    try:
        with open(DATA_FILE, 'r', encoding='utf8') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_data(data):
    """Write data to the JSON file.

    Args:
        data (list): The list of posts to be written to the file.
    """
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


@app.route('/api/posts', methods=['GET'])
@limiter.limit("5 per minute")
def get_posts():
    """Retrieve and return a paginated list of posts with optional sorting.

    Query parameters:
        - sort: Field to sort by ('title' or 'content').
        - direction: Sort direction ('asc' or 'desc').
        - page: Page number for pagination.
        - limit: Number of posts per page.

    Returns:
        json: Paginated and optionally sorted list of posts.
    """
    data = read_data()

    # Retrieve query parameters for sorting
    sort_field = request.args.get("sort", "").lower()
    sort_direction = request.args.get("direction", "asc").lower()

    # Retrieve query parameters for pagination
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    # Validate sort parameters
    if sort_field and sort_field not in ["title", "content"]:
        return jsonify({"error": "Invalid sort field"}), 400
    if sort_direction not in ["asc", "desc"]:
        return jsonify({"error": "Invalid sort direction"}), 400

    # Sort posts if sort parameters are provided
    if sort_field:
        data.sort(
            key=lambda post: post.get(sort_field, ""),
            reverse=(sort_direction == "desc"),
        )

    # Paginate posts
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_posts = data[start_index:end_index]

    # Ensure comments field exists and is an array for each post
    for post in paginated_posts:
        if 'comments' not in post:
            post['comments'] = []

    return jsonify(paginated_posts)


@app.route("/api/posts", methods=["POST"])
@limiter.limit("5 per minute")
def add_post():
    """Add a new post to the list.

    The request body must include 'title' and 'content'.

    Returns:
        json: The newly added post, or an error message if validation fails.
    """
    data = read_data()
    new_post = request.get_json()
    if not new_post.get('title') or not new_post.get('content'):
        return jsonify({"error": "Title and content are required"}), 400

    # Generate a new ID for the post
    new_post['id'] = max((post['id'] for post in data), default=0) + 1

    # Add the new post to the list
    data.append(new_post)
    write_data(data)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Retrieve a single post by its ID.

    Args:
        post_id (int): The ID of the post to retrieve.

    Returns:
        json: The requested post, or a 404 error if not found.
    """
    data = read_data()
    post = next((post for post in data if post['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    return jsonify(post)


@app.route("/api/posts/<int:id>", methods=["PUT"])
def update_post(id):
    """Update an existing post by its ID.

    The request body may include 'title' and/or 'content'.

    Args:
        id (int): The ID of the post to update.

    Returns:
        json: The updated post, or a 404 error if the post is not found.
    """
    data = read_data()
    post = next((post for post in data if post['id'] == id), None)

    if post is None:
        return jsonify({"error": "Post not found"}), 404

    updates = request.get_json()
    if 'title' in updates:
        post['title'] = updates['title']
    if 'content' in updates:
        post['content'] = updates['content']

    write_data(data)
    return jsonify(post)


@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    """Add a comment to a specific post.

    Args:
        post_id (int): The ID of the post to comment on.

    Returns:
        json: The updated post with the new comment, or an error if the post or comment is invalid.
    """
    data = read_data()
    post = next((p for p in data if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    comment = request.get_json().get("comment")
    if not comment:
        return jsonify({"error": "Comment is required"}), 400

    if 'comments' not in post:
        post['comments'] = []

    post['comments'].append(comment)
    write_data(data)
    return jsonify(post), 200


@app.route("/api/posts/<int:id>", methods=["DELETE"])
def delete_post(id):
    """Delete a post by its ID.

    Args:
        id (int): The ID of the post to delete.

    Returns:
        json: A success message, or a 404 error if the post is not found.
    """
    data = read_data()
    post = next((post for post in data if post['id'] == id), None)

    if post is None:
        return jsonify({"error": "Post not found"}), 404

    data.remove(post)
    write_data(data)
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search for posts by title or content.

    Query parameters:
        - title: Partial or full title to search for.
        - content: Partial or full content to search for.

    Returns:
        json: List of posts that match the search criteria.
    """
    title_query = request.args.get("title", "")
    content_query = request.args.get("content", "")

    data = read_data()

    filtered_posts = [
        post
        for post in data
        if (title_query.lower() in post.get("title", "").lower())
           or (content_query.lower() in post.get("content", "").lower())
    ]

    return jsonify(filtered_posts)


@app.errorhandler(404)
def not_found_error(error):
    """Return a JSON response for 404 errors."""
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    """Return a JSON response for 405 errors."""
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)