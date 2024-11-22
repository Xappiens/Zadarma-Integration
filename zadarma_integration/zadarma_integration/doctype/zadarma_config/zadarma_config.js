frappe.ui.form.on("Zadarma Config", {
    refresh: function (frm) {
        // Añade un botón directamente a la barra superior
        frm.add_custom_button(
            __("Probar Conexión"), // Texto del botón
            function () {
                frappe.call({
                    method: "zadarma_integration.zadarma_integration.doctype.zadarma_config.zadarma_config.trigger_test_connection",
                    args: {
                        docname: frm.doc.name,
                    },
                    callback: function (r) {
                        if (r.message) {
                            frappe.msgprint(r.message);
                            frm.reload_doc(); // Recargar el formulario para reflejar los cambios
                        }
                    },
                });
            }
        );
    },
});
