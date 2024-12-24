# Copyright (c) 2024, Xappiens and contributors
# For license information, please see license.txt

# import frappe
import frappe
import requests
from frappe.model.document import Document
from zadarma_integration.utils.zadarmaapi import ZadarmaAPI


class ZadarmaSMS(Document):
	pass



@frappe.whitelist()
def send_sms(phone_number, prefix, message):
    """
    Envía un SMS directamente al número proporcionado utilizando Zadarma.
    """
    if not phone_number or not message:
        return {"success": False, "error": "Número de teléfono o mensaje no proporcionado."}

    # Obtener configuración de Zadarma
    config = frappe.get_single("Zadarma Config")
    zadarma_api = ZadarmaAPI(config.api_key, config.api_secret)
    
    # Formatear el número para Zadarma (con +)
    full_number = f"{prefix}{phone_number}"
    
    # Formatear el número para el DocType (formato: [código_país]-[número])
    # Removemos el + y añadimos el guion que Frappe espera para el campo Phone
    db_number = f"+{prefix.replace('+', '')}-{phone_number}"

    try:
        # Enviar el SMS
        response = zadarma_api.call(
            method="/v1/sms/send/",
            params={
                "number": full_number,
                "message": message
            },
            request_type="POST"
        )
        
        response = frappe.parse_json(response)
        
        if response.get("status") == "success":
            try:
                sms_doc = frappe.get_doc({
                    "doctype": "Zadarma SMS",
                    "phone_number": db_number,
                    "message": message,
                    "status": "Sent",
                    "user": frappe.session.user or "Guest"
                })

                sms_doc.insert(ignore_permissions=True)
                frappe.db.commit()

                return {"success": True, "response": response}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": response.get("message", "Error desconocido de Zadarma.")}

    except Exception as e:
        return {"success": False, "error": str(e)}