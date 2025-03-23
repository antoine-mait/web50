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