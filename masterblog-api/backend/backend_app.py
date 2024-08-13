from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
# Initialize Limiter
limiter = Limiter(
    get_remote_address,  # Function to identify clients
    app=app  # Pass the Flask app instance
)

DATA_FILE = 'posts.json'


def read_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def write_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)
        print("Data written to file:", data)  # Debug print


@app.route('/api/posts', methods=['GET'])
@limiter.limit("5 per minute")  # Apply rate limit to this endpoint
def get_posts():
    data = read_data()
    # Retrieve query parameters for sorting
    sort_field = request.args.get("sort", "")
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

    # Format comments field
    for post in paginated_posts:
        if len(post['comments']) == 1:
            post['comments'] = post['comments'][0]  # Convert single comment to string
        # Ensure comments remain a list for multiple comments
        elif len(post['comments']) > 1:
            post['comments'] = post['comments']

    return jsonify(data)


@app.route("/api/posts", methods=["POST"])
@limiter.limit("5 per minute")  # Apply rate limit to this endpoint
def add_post():
    data = read_data()
    new_post = request.get_json()
    if not new_post.get('title') or not new_post.get('content'):
        return jsonify({"error": "Title and content are required"}), 400

    # Generate a new ID for the post
    new_post['id'] = max((post['id'] for post in data), default=0) + 1

    # Add the new post to the list
    data.append(new_post)
    write_data(data)

    # Return the new post with status code 201
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    data = read_data()
    post = next((post for post in data if post['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    return jsonify(post)


@app.route("/api/posts/<int:id>", methods=["PUT"])
def update_post(id):
    data = read_data()
    # Find the post with the given ID
    post = next((post for post in data if post['id'] == id), None)

    # If the post wasn't found, return a 404 error
    if post is None:
        return "", 404

    # Update the post with the new data
    updates = request.get_json()
    if 'title' in updates:
        post['title'] = updates['title']
    if 'content' in updates:
        post['content'] = updates['content']

    # Return the updated post
    write_data(data)
    return jsonify(post)


@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    data = read_data()  # Read data from the JSON file
    post = next((p for p in data if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    comment = request.get_json().get("comment")
    if not comment:
        return jsonify({"error": "Comment is required"}), 400

    if 'comments' not in post:
        post['comments'] = []

    post['comments'].append(comment)
    write_data(data)  # Write updated data back to the JSON file
    return jsonify(post), 200


@app.route("/api/posts/<int:id>", methods=["DELETE"])
def delete_post(id):
    data = read_data()
    # Find the post with the given ID
    post = next((post for post in data if post['id'] == id), None)

    # If the post wasn't found, return a 404 error
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    data.remove(post)
    write_data(data)
    return '', 204


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    # Retrieve query parameters
    title_query = request.args.get("title", "")
    content_query = request.args.get("content", "")

    # Read posts from file
    data = read_data()

    # Filter posts based on query parameters
    filtered_posts = [
        post
        for post in data
        if (title_query.lower() in post.get("title", "").lower())
           or (content_query.lower() in post.get("content", "").lower())
    ]

    return jsonify(filtered_posts)


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
