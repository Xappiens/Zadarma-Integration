# Copyright (c) 2024, Xappiens and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from zadarma_integration.utils.zadarmaapi import ZadarmaAPI


class ZadarmaCallLog(Document):
	pass

@frappe.whitelist()
def initiate_call(phone_number):
    """
    Inicia una llamada a través de Zadarma y registra los detalles.
    """
    config = frappe.get_single("Zadarma Config")
    zadarma_api = ZadarmaAPI(config.api_key, config.api_secret)
    frappe.log_error(f"Llamada iniciada al número: {phone_number}")
    
    from_number = config.from_number
    from_number = from_number.lstrip('+')
    if not from_number:
        return {"success": False, "message": "Número 'from' no configurado."}

    try:
        # Llamar al endpoint de Zadarma para iniciar la llamada
        response = zadarma_api.call(
            api_path='/v1/request/callback/',
            parameters={
                'from': 100,
                'to': 696999283
            },
            http_method='GET'
        )
        frappe.log_error(message=response, title="Respuesta de Zadarma")

        # Crear un registro en Zadarma Call Log
        call_log = frappe.get_doc({
            "doctype": "Zadarma Call Log",
            "phone_number": phone_number,
            "call_status": "Success",
            "user": frappe.session.user,
            "timestamp": frappe.utils.now()
        })
        call_log.insert(ignore_permissions=True)

        return {"success": True, "response": response}
    except Exception as e:
        frappe.log_error(message=str(e), title="Error al iniciar la llamada con Zadarma")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_recent_calls():
    """
    Obtiene las últimas 20 llamadas del registro, ordenadas de más reciente a más antigua.
    """
    try:
        recent_calls = frappe.get_all(
            "Zadarma Call Log",
            fields=["phone_number", "call_status", "timestamp", "user"],
            order_by="timestamp desc",
            limit_page_length=20
        )
        return recent_calls
    except Exception as e:
        return {"error": str(e)}

@frappe.whitelist()
def get_webrtc_key():
    """
    Obtiene la clave WebRTC desde Zadarma.
    """
    config = frappe.get_single("Zadarma Config")
    zadarma_api = ZadarmaAPI(config.api_key, config.api_secret)

    try:
        # Llama al API de Zadarma para obtener la clave WebRTC
        response = zadarma_api.call(
            method="/v1/webrtc/get_key",
            params={"sip": "192652"},  # Cambia este valor si el SIP es diferente
            request_type="GET"
        )

        # Convertir la respuesta a JSON
        response = frappe.parse_json(response)

        if "key" in response:
            frappe.log_error(message=response, title="Respuesta WebRTC")
            return {
                "success": True,
                "webrtc_key": response["key"],
                "login": "192652"  # Usuario para WebRTC
            }
        else:
            frappe.log_error(response, "Error en respuesta WebRTC")
            return {"success": False, "message": "Error al obtener la clave WebRTC"}
    except Exception as e:
        frappe.log_error(message=str(e), title="Error al obtener clave WebRTC")
        return {"success": False, "message": str(e)}


