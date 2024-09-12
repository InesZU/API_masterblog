// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to load all posts and display them
function loadPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    fetch(baseUrl + '/posts?limit=10')
        .then(response => response.json())
        .then(data => {
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';

                let commentsHTML = '';
                if (Array.isArray(post.comments) && post.comments.length > 0) {
                    commentsHTML = post.comments.map(comment => `<p>${comment}</p>`).join('');
                }
                postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p>${post.content}</p>
                    <button onclick="deletePost(${post.id})" class="delete-button">Delete</button>
                    <button onclick="toggleComments(${post.id})" class="comment-button">Add Comment</button>
                    <div class="comments-section" id="comments-section-${post.id}" style="display: none;">
                        <h3>Comments</h3>
                        ${commentsHTML}
                        <form onsubmit="addComment(event, ${post.id})">
                            <input type="text" name="comment" placeholder="Add a comment" required>
                            <button type="submit">Submit Comment</button>
                        </form>
                    </div>
                `;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: postTitle, content: postContent })
    })
    .then(response => response.json())  // Parse the JSON data from the response
    .then(post => {
        console.log('Post added:', post);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to show the comment form
function showCommentForm(postId) {
    document.getElementById(`comment-form-${postId}`).style.display = 'block';
}

// Function to add a comment
function addComment(event, postId) {
    event.preventDefault();  // Prevent the form from submitting the traditional way
    var baseUrl = document.getElementById('api-base-url').value;
    var comment = document.querySelector(`#comments-section-${postId} input[name="comment"]`).value.trim();

    if (!comment) {
        console.error('Comment cannot be empty');
        return;
    }

    fetch(`${baseUrl}/posts/${postId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: comment })
    })
    .then(response => response.json())
    .then(post => {
        // Update the post with the new comment
        document.getElementById(`comments-section-${postId}`).innerHTML = `
            <h3>Comments</h3>
            ${post.comments.map(c => `<p>${c}</p>`).join('')}
            <form onsubmit="addComment(event, ${postId})">
                <input type="text" name="comment" placeholder="Add a comment" required>
                <button type="submit">Submit Comment</button>
            </form>
        `;
        document.querySelector(`#comments-section-${postId} input[name="comment"]`).value = ''; // Clear input field
    })
    .catch(error => console.error('Error:', error));
}

// Function to toggle the visibility of the comments section
function toggleComments(postId) {
    var commentsSection = document.getElementById(`comments-section-${postId}`);
    var commentButton = document.querySelector(`#post-container .comment-button[onclick="toggleComments(${postId})"]`);
    if (commentsSection.style.display === 'none') {
        commentsSection.style.display = 'block';
        commentButton.textContent = 'Hide Comments';  // Change button text
    } else {
        commentsSection.style.display = 'none';
        commentButton.textContent = 'Show Comments';  // Change button text
    }
}
var currentPage = 1;
function loadMorePosts() {
    currentPage++;  // Increment page number
    fetch(baseUrl + `/posts?page=${currentPage}&limit=4`)  // Adjust limit as needed
        .then(response => response.json())
        .then(data => {
            const postContainer = document.getElementById('post-container');
            data.forEach(post => {
                // (same logic to append posts to the container)
            });
        });
}