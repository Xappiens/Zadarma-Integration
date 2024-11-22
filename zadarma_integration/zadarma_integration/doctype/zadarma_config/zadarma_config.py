import frappe
from frappe.model.document import Document
from zadarma_integration.utils.zadarmaapi import ZadarmaAPI


class ZadarmaConfig(Document):
    def test_connection(self):
        """
        Probar la conexión con Zadarma utilizando el API.
        """
        if not self.api_key or not self.api_secret:
            frappe.throw("Por favor, configura la API Key y el API Secret antes de continuar.")

        # Inicializar la API de Zadarma
        zadarma_api = ZadarmaAPI(self.api_key, self.api_secret)

        try:
            # Llamar al endpoint de prueba
            response = zadarma_api.call(http_method='GET', api_path='/v1/info/balance/')
            self.webhook_status = "Active"
            self.last_message = f"Conexión exitosa: Balance {response}"
        except Exception as e:
            self.webhook_status = "Error"
            self.last_message = str(e)

        # Guardar cambios
        self.save()
        frappe.db.commit()
        return self.last_message


@frappe.whitelist()
def trigger_test_connection(docname):
    """
    Acción personalizada para probar la conexión desde el botón.
    """
    config = frappe.get_doc("Zadarma Config", docname)
    return config.test_connection()
