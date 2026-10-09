const message = document.getElementById('message');
const button = document.getElementById('test-button');

button.addEventListener('click', () => {
    message.textContent = 'javascript active';
});