document.addEventListener('DOMContentLoaded')

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