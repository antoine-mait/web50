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
    
   
}

function submitHandler(id) {
    const textareaValue = document.getElementById(`textarea_${id}`).value;
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
        
        
    })
}