document.addEventListener("DOMContentLoaded", function () {
    const video = document.getElementById("qr-video");
    const qrDataElement = document.getElementById("qr-data");
    const numeroRutElement = document.getElementById("numero-rut");
    const codigoGeneradoElement = document.getElementById("codigo-generado");
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    let videoStream;
    let codigoGenerado = "";



    document.getElementById("start-scan").addEventListener("click", () => {
        // Acceder a la cámara
        navigator.mediaDevices
            .getUserMedia({ video: { facingMode: "environment" } })
            .then(function (stream) {
                video.srcObject = stream;
                videoStream = stream;
            })
            .catch(function (error) {
                console.error("Error al acceder a la cámara:", error);
            });

        // Capturar y analizar el video en busca de códigos QR
        video.addEventListener("loadedmetadata", function () {
            const canvas = document.createElement("canvas");
            const context = canvas.getContext("2d");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const scanner = setInterval(function () {
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = context.getImageData(
                    0,
                    0,
                    canvas.width,
                    canvas.height
                );
                const code = jsQR(imageData.data, imageData.width, imageData.height);

                if (code && code.data) {
                    const numeroRut = obtenerNumeroRutDesdeQR(code.data);
                    if (numeroRut) {
                        qrDataElement.textContent = code.data;
                        numeroRutElement.textContent = `${numeroRut}`;
                        verificarRutEnServidor(numeroRut);

                        stopCamera(videoStream);

                        clearInterval(scanner);
                    } else {
                        console.warn("Formato de código QR no válido.");
                    }
                } else {
                    console.warn("No se pudo encontrar un código QR.");
                }
            }, 100);
        });
    });

        //funcion para cerrar la cámara
        function stopCamera(stream) {
            if (stream) {
                const tracks = stream.getTracks();
                tracks.forEach((track) => {
                    track.stop();
                });
            }
        }
        //funcion para obtener el rut desde el QR.
        function obtenerNumeroRutDesdeQR(qrData) {

            const match = qrData.match(/RUN=(\d+-\d+)/);
            if (match && match[1]) {
                return match[1];
            } else {
                return null;
            }
        }
        
        //Funcion para verificar si existe el rut.
        function verificarRutEnServidor(numeroRut) {
            axios.get(`/verificar_rut/?rut=${numeroRut}`)
                .then(function (response) {
                    if (response.data.exists) {
                        const data = response.data.data;
                        console.log(data)
                        // Si el código no es null, muestra la alerta
                        if (data.codigo !== null) {
                            alert(`La TNE del rut ${data.rut} ya fue entregada`);
                            return; // Termina la ejecución de la función aquí para que no se siga procesando el resto.
                        }
        
                        // Actualiza los campos del formulario con los datos
                        document.getElementById("rut").value = data.rut;
                        document.getElementById("nombre-input").value = data.nombre;
                        document.getElementById("apellido-input").value = data.apellido;
                        document.getElementById("estado-input").value = data.estado ? "Pendiente" : "Entregado";
                        
                        const email = data.email + "@duocuc.cl";
                        console.log("Email a enviar:", email);
                        document.getElementById("email").value = email;
        
                        // Este campo lo dejamos vacío para que el usuario ingrese el código enviado por correo
                        document.getElementById("codigo").value = "";
        
                        // Genera y envía el código por correo
                        codigoGenerado = generarCodigo();
                        
                        enviarCodigoPorCorreo(codigoGenerado);
        
                    } else {
                        // Manejar el caso en el que no existe el RUT
                        
                        alert("El RUT no tiene TNE asociada");
                    }
                })     
        }

        function generarCodigo() {
            const caracteres = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
            let codigo = "";
    
            for (let i = 0; i < 4; i++) {
                const randomIndex = Math.floor(Math.random() * caracteres.length);
                codigo += caracteres.charAt(randomIndex);
            }
            return codigo;
        }
        
        function enviarCodigoPorCorreo(codigo) {
            const emailDestino = document.getElementById("email").value;
            console.log("Email a enviar:", emailDestino);
            axios.post('/send_email/', {
                codigo: codigo,
                email: emailDestino
            }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(function(response) {
                console.log(response.data.message);
                alert(response.data.message);  // Mostrar el mensaje en un alerta
            }).catch(function(error) {
                // En caso de que ocurra un error en la petición, como una respuesta 500
                console.error("Error enviando el correo:", error);
                alert("Error al enviar el código. Por favor, inténtalo de nuevo.");
            });
        }
        function enviarCodigoPorCorreoManual(codigo, emailDestino) {
            axios.post('/send_email/', {
                codigo: codigo,
                email: emailDestino
            }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(function(response) {
                console.log(response.data.message);
                alert(response.data.message);  // Mostrar el mensaje en un alerta
            }).catch(function(error) {
                // En caso de que ocurra un error en la petición, como una respuesta 500
                console.error("Error enviando el correo:", error);
                alert("Error al enviar el código. Por favor, inténtalo de nuevo.");
            });
        }
        function abrirModalEnvioManual() {
            document.getElementById("modal-envio-manual").classList.remove('hidden');
        }
        
        // Función para cerrar el modal
        function cerrarModalEnvioManual() {
            document.getElementById("modal-envio-manual").classList.add('hidden');
        }
        
        // Función para enviar el correo manualmente
        function enviarCorreoManual() {
            const emailManual = document.getElementById("email-manual").value;
            const codigo = generarCodigo(); // Asegúrate de que esta función esté definida y sea accesible desde aquí
        
            // Verificar que el campo de email no esté vacío
            if (emailManual) {
                // Llamar a la función enviarCodigoPorCorreo con el email y código
                enviarCodigoPorCorreoManual(codigo, emailManual);
                cerrarModalEnvioManual(); // Cerrar el modal
            } else {
                alert("Por favor, ingresa un correo electrónico válido.");
            }
        }
        
        // Event listener para el botón que abre el modal
        document.getElementById("envio-manual").addEventListener("click", abrirModalEnvioManual);
        
        // Event listener para el botón que cierra el modal
        document.querySelectorAll(".close-modal").forEach((closeButton) => {
            closeButton.addEventListener("click", cerrarModalEnvioManual);
        });
        
        // Event listener para el botón que envía el correo manualmente
        document.getElementById("submit-email-manual").addEventListener("click", enviarCorreoManual);
        
        
        document.getElementById("tne-form").addEventListener("submit", function(event) {
            event.preventDefault();
        
            const codigoIngresado = document.getElementById("codigo").value;
            console.log("Codigo ingresado:", codigoIngresado);
        
            axios.post('/save_code/', {
                rut: document.getElementById("rut").value,
                codigo: codigoIngresado
            }).then(function(response) {
                if (response.data.verified) {
                    alert("Verificación exitosa");
                     // Limpiar los campos manualmente
                    document.getElementById("rut").value = '';
                    document.getElementById("nombre-input").value = '';
                    document.getElementById("apellido-input").value = '';
                    document.getElementById("estado-input").value = '';
                    document.getElementById("email").value = '';
                    document.getElementById("codigo").value = '';
                } else {
                    alert(response.data.message);
                }
                // Si quieres cambiar el contenido de algún elemento con el mensaje de respuesta, puedes hacerlo aquí.
                // Por ejemplo:
                document.getElementById("codigo").textContent = response.data.message;
            }).catch(function(error) {
                alert("Error al verificar el código. Por favor, inténtalo de nuevo.");
            });
        });

    });
    
