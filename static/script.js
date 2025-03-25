document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('postForm')) initSharePage();
    fetchPosts(); // Fetch posts when the page loads
});

// Share Page Logic
function initSharePage() {
    const form = document.getElementById('postForm');
    const responseSection = document.getElementById('responseSection');
    const aiResponse = document.getElementById('aiResponse');
    const suggestionsList = document.getElementById('suggestions');
    const contentInput = document.getElementById('content');

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // ✅ Prevents the form from reloading the page

        const content = contentInput.value.trim();
        if (!content) return; // Exit silently if no content is provided

        console.log("User input:", content); // Debugging line to check input

        try {
            // Send user input to the AI API
            const response = await fetch('/api/posts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                throw new Error("Failed to get AI response");
            }

            const data = await response.json();
            console.log("AI Response:", data); // Debugging line to check response

            // Display AI response if available
            if (data.ai_response) {
                aiResponse.textContent = data.ai_response;
                responseSection.classList.remove('hidden');
            } else {
                aiResponse.textContent = "No response received.";
            }

            // Display suggestions if available
            if (data.suggestions && Array.isArray(data.suggestions) && data.suggestions.length > 0) {
                suggestionsList.innerHTML = data.suggestions.map(s => `<li>${s}</li>`).join('');
            } else {
                suggestionsList.innerHTML = "<li>No suggestions available.</li>";
            }

            // ✅ Clear the input field after submission
            contentInput.value = "";

        } catch (error) {
            console.error("Error:", error);
            aiResponse.textContent = "An error occurred while processing your request. Please try again.";
        }
    });
}

// Fetch and display posts from the AI response JSON
async function fetchPosts() {
    try {
        const response = await fetch('/api/get_response');
        console.log('Response:', response);
        if (!response.ok) throw new Error("Failed to fetch responses.");
        
        const data = await response.json();
        console.log('Data:', data);

        if (!data || data.length === 0) {
            document.getElementById('postsContainer').innerHTML = "<p>No posts available.</p>";
            return;
        }

        renderPosts(data); // Pass the array of responses directly
    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('postsContainer').innerHTML = "<p>Could not load posts.</p>";
    }
}

// Function to render posts on the page
function renderPosts(posts) {
    const postsContainer = document.getElementById('postsContainer');
    postsContainer.innerHTML = ""; // Clear previous content

    posts.forEach(post => {
        const postcard = document.createElement("div");
        postcard.classList.add("post-card");

        postcard.innerHTML = `
            <h3>Anonymous</h3>
            <p><strong>Story:</strong> ${post.story}</p>
            <p><strong>AI Response:</strong> ${post.ai_response}</p>
            <div class="suggestions">
                <strong>Suggestions:</strong>
                <ul>
                    ${post.suggestions.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
        `;

        postsContainer.appendChild(postcard);
    });
}
