document.addEventListener('DOMContentLoaded', function() {
    // Event listeners for Next and Previous buttons
    document.querySelectorAll('.pagination a').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const url = this.href;

            fetch(url)
                .then(response => response.text())
                .then(data => {
                    const newDoc = new DOMParser().parseFromString(data, 'text/html');
                    document.querySelector('.post-list').innerHTML = newDoc.querySelector('.post-list').innerHTML;
                    document.querySelector('.pagination').innerHTML = newDoc.querySelector('.pagination').innerHTML;
                })
                .catch(error => console.error('Error:', error));
        });
    });
})

console.log("CSRF Token:", getCookie("csrftoken"));

// Alternative CSRF token getter
function getCsrfToken() {
    // First try to get it from a meta tag
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    // Then try to get it from a form
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    // Finally fall back to cookie method
    return getCookie('csrftoken');
}

function getCookie(name){
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}`);
    if(parts.length == 2) return parts.pop().split(';').shift();

}

function submitHandler(id) {
    const textareaValue = document.getElementById(`textarea_${id}`).value;
    const content = document.getElementById(`content_${id}`);
    const modal = document.getElementById(`modal_edit_post_${id}`)
    const csrftoken = getCsrfToken();
    console.log("Using CSRF Token:", csrftoken);



    fetch(`/edit/${id}`, {
        method: "POST",
        credentials: 'same-origin', 
        headers: {
            "Content-Type": "application/json", 
            "X-CSRFToken": csrftoken 
        },
        body: JSON.stringify({
            description: textareaValue
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(result => {

        content.innerHTML = result.data;
        
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden','true');
        modal.setAttribute('style','display: none');

        const modalsBackdrops = document.getElementsByClassName('modal-backdrop');
        for(let i=0; i < modalsBackdrops.length; i++) {
            document.body.removeChild(modalsBackdrops[i]);
        }
    })
}

function toggleLike(postId) {
    const likeBtn = document.querySelector(`#like-btn-${postId}`);
    const likeCount = document.querySelector(`#like-count-${postId}`);
    const csrftoken = getCsrfToken();
    
    fetch(`/like/toggle/${postId}/`, {
        method: "POST",
        credentials: 'same-origin',
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        // Update like count
        likeCount.textContent = `${result.count_likes} Likes`;
        
        // Update like button icon based on like status
        if (result.liked) {
            likeBtn.innerHTML = `
                <img class="like" src="${result.media_url}full_heart.png" alt="full_heart" width="20">
                <p class="text-overlay">Unlike</p>
            `;
        } else {
            likeBtn.innerHTML = `
                <img class="like" src="${result.media_url}empty_heart.png" alt="empty_heart" width="20">
                <p class="text-overlay">Like</p>
            `;
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}