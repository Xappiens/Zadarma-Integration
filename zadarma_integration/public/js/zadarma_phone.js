// Incluir los scripts de Zadarma para el Webphone
$(document).ready(function () {
    /*
    // Inicializar el widget de Zadarma al cargar el documento y ocultarlo
    frappe.call({
        method: 'zadarma_integration.zadarma_integration.doctype.zadarma_call_log.zadarma_call_log.get_webrtc_key',
        callback: function (response) {
            if (response.message.success) {
                console.log(response.message);
                initializeZadarmaWidget(response.message.webrtc_key, response.message.login);
            } else {
                console.error('Error al obtener la clave WebRTC: ', response.message.message);
            }
        }
    });
    */

    const phoneIcon = $('<div>', {
        id: 'zadarma-phone-icon',
        html: '<i class="fa fa-comment"></i>',  // Cambiado a icono de mensaje
        title: 'Enviar SMS'  // Cambiado el título
    }).css({
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        width: '50px',
        height: '50px',
        backgroundColor: '#171717',
        borderRadius: '20%',
        color: '#fff',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.2)',
        cursor: 'pointer',
        zIndex: 1000,
    });

    $('body').append(phoneIcon);

    // Crear el modal o panel del teléfono
    const phonePanel = $(
        `<div id="zadarma-phone-panel" style="display: none; position: fixed; bottom: 80px; right: 20px; width: 400px; max-height:500px; background: #f9fafc; border-radius: 12px; box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.2); z-index: 1001;">
            <div style="padding: 15px; display: flex; justify-content: space-between; align-items: center; background-color: #171717; color: white; border-top-left-radius: 12px; border-top-right-radius: 12px;">
                <span style="font-weight: bold;">Enviar SMS</span>
                <button id="close-zadarma-panel" style="background: none; border: none; color: white; font-size: 16px; cursor: pointer;">✖</button>
            </div>
            <div class="modal-body" style="padding: 15px;">
                <div id="zadarma-tab-sms" class="zadarma-tab-content" style="display: block;">
                    <div id="zadarma-sms-section">
                        <div style="margin-bottom: 10px;">
                            <div style="display: flex; align-items: center;">
                                <select id="zadarma-sms-prefix" class="form-control" style="width: 30%; margin-right: 5px; height: 40px; font-size: 14px; margin-bottom:10px;">
                                    <option value="+34" selected>🇪🇸 +34</option>
                                    <option value="+1">🇺🇸 +1</option>
                                    <option value="+44">🇬🇧 +44</option>
                                    <option value="+33">🇫🇷 +33</option>
                                    <option value="+49">🇩🇪 +49</option>
                                </select>
                                <input type="text" id="zadarma-sms-number" class="form-control" style="text-align: center; font-size: 20px; height: 40px; flex-grow: 1; margin-bottom:10px;" placeholder="Introduce el número">
                            </div>
                            <textarea id="zadarma-sms-message" class="form-control" style="text-align: left; font-size: 20px; height: 205px; flex-grow: 1; margin-bottom:10px;" placeholder="Escribe tu mensaje aquí..." rows="4"></textarea>
                        </div>
                        <button id="zadarma-send-sms-button" class="btn btn-success btn-block" style="margin-bottom: 15px;">Enviar SMS</button>
                    </div>
                </div>
            </div>
        </div>`
    );
    
    /*
    // Comprobar si el widget se carga y ocultarlo
    const zadarmaInterval = setInterval(() => {
        const widget = $('#zdrmWPhI');
        if (widget.length) {
            widget.attr('style', 'display: none !important;');
            clearInterval(zadarmaInterval);
        }
    }, 500);
    */
    
    $('body').append(phonePanel);
    
    // Mostrar u ocultar el panel al hacer clic en el ícono
    $('#zadarma-phone-icon').on('click', function () {
        $('#zadarma-phone-panel').toggle();
    });
    
    // Cerrar el panel
    $('#close-zadarma-panel').on('click', function () {
        $('#zadarma-phone-panel').hide();
    });

    // Lógica para enviar el SMS
    $('#zadarma-send-sms-button').on('click', function () {
        const prefix = $('#zadarma-sms-prefix').val();
        const phoneNumber = $('#zadarma-sms-number').val();
        if (!phoneNumber) {
            frappe.msgprint({
                title: __('Error'),
                message: __('Por favor, introduce un número de teléfono.'),
                indicator: 'red'
            });
            return;
        }

        const message = $('#zadarma-sms-message').val();

        // Validar que los campos no estén vacíos
        if (!phoneNumber || !message) {
            frappe.msgprint({
                title: __('Error'),
                message: __('Por favor, introduce el número de teléfono y el mensaje.'),
                indicator: 'red'
            });
            return;
        }

        // Enviar datos al backend para procesar el SMS
        frappe.call({
            method: 'zadarma_integration.zadarma_integration.doctype.zadarma_sms.zadarma_sms.send_sms',
            args: {
                phone_number: phoneNumber,
                prefix: prefix,
                message: message
            },
            callback: function (response) {
                if (response.message.success) {
                    console.log(response.message);
                    frappe.msgprint({
                        title: __('Éxito'),
                        message: __('El SMS ha sido enviado correctamente.'),
                        indicator: 'green'
                    });
                    // Limpiar los campos del formulario
                    $('#zadarma-sms-number').val('');
                    $('#zadarma-sms-message').val('');
                } else {
                    frappe.msgprint({
                        title: __('Error'),
                        message: __('No se pudo enviar el SMS. Error: ' + response.message.error),
                        indicator: 'red'
                    });
                }
            }
        });
    });
});