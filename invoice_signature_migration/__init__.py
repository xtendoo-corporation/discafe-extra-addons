import base64
import os
from odoo import registry

def _post_init_hook(cr, registry):
    print("*" * 80)
    # Ejecuta la consulta para obtener las facturas con una firma digital
    cr.execute("SELECT number, digital_signature FROM account_invoice WHERE digital_signature IS NOT NULL LIMIT 1")
    # Obtener todas las facturas
    account_invoices = cr.fetchall()
    # Verifica si se encontraron facturas
    if account_invoices:
        print(f"Se han encontrado {len(account_invoices)} facturas con firma digital.")

        # Bucle para procesar cada factura
        for invoice in account_invoices:
            invoice_number = invoice[0]  # Número de factura
            digital_signature_bytes = bytes(invoice[1])  # Firma digital de la factura
            print(f"Procesando la factura {invoice_number}...")
            digital_signature_base64 = base64.b64encode(digital_signature_bytes).decode('utf-8')  # Codificamos los datos en base64

            # Buscar las coincidencias en la tabla account_move
            cr.execute("SELECT id, name FROM account_move WHERE name = %s", (invoice_number,))
            account_moves = cr.fetchall()
            for account_move in account_moves:
                name=account_move[1]
                name = name.replace('/', '')

                filestore_path = "/var/lib/odoo/cf"
                print(f"Procesando la factura {filestore_path}...")
                # Crear un nombre único para la imagen (por ejemplo, basado en el número de la factura)
                image_filename = f'digital_signature_{name}.png'
                image_path = os.path.join(filestore_path, image_filename)
                print(f"Procesando la factura {image_path}...")

                # Guardar la firma digital como una imagen PNG
                with open(image_path, 'wb') as img_file:
                    img_file.write(digital_signature_bytes)


            # # Crear los valores del attachment
            # vals = {
            #     'name': 'digital_signature',  # Nombre del attachment
            #     'type': 'binary',  # Tipo de archivo (usualmente binary para imágenes)
            #     'datas': digital_signature_base64,  # La firma digital codificada en base64
            #     'mimetype': 'image/png',  # Tipo MIME (asumimos que es una imagen PNG)
            #     'res_model': 'account.invoice',  # El modelo relacionado, en este caso account.invoice
            #     'res_id': number,  # ID de la factura relacionada
            #     'store_fname': f'digital_signature_{number}.png',  # Nombre del archivo guardado
            # }

    print("*" * 80)
