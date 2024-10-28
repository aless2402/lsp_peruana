// Obtener el elemento de video
const video = document.getElementById('video');

// Solicitar acceso a la cámara
navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
        video.srcObject = stream;
    })
    .catch((err) => {
        console.error("Error al acceder a la cámara: ", err);
    });

// Función para actualizar los subtítulos
function updateSubtitles() {
    $.get('/subtitles', function(data) {
        $('#subtitles').text(data.subtitle);
    });
}

// Actualizar subtítulos cada segundo
setInterval(updateSubtitles, 1000);
