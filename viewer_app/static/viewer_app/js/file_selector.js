function updatePathName() {
    const fileInput = document.getElementById('file-upload');
    const selectedPathSpan = document.getElementById('selectedPath');
    
    if (fileInput.files.length > 0) {
        // Obtener el nombre de la carpeta seleccionada
        const folderPath = fileInput.files[0].webkitRelativePath.split('/')[0];
        selectedPathSpan.textContent = folderPath;
        
        // Si quieres enviar la ruta al servidor:
        sendPathToServer(folderPath);
    } else {
        selectedPathSpan.textContent = 'Ninguna carpeta seleccionada';
    }
}

function sendPathToServer(path) {
    fetch('/update_path/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({path: path})
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
