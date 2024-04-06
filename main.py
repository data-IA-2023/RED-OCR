from  getInvoices import *
from  extractData import *
from  getData import *
from  highlightImage import *
from ocrdb import *


conn = connectBd()

session = createsession(conn)

if session:
    print("connection succes")


all_invoice = get_all_invoices()
"""get_last_date_from_database_because_azure_server_suck = session.query(InvoiceTable.Invoice_date).order_by(InvoiceTable.Invoice_id.desc()).first()._asdict()
get_all_invoices_from_lastdate_in_database_because_azure_suck = get_all_invoices_from_dates(get_last_date_from_database_because_azure_server_suck.get('Invoice_date'))
print(len(get_all_invoices_from_lastdate_in_database_because_azure_suck))
print(len(all_invoice))

data_invoice      = extract_data(test_invoice[0]['no'])
print(data_invoice)
print('*************************************')
data_qr           = extract_qr_data(test_invoice[0]['no'])
print(data_qr)
print('*************************************')
data_invoice_text = get_brut_format(data_invoice[test_invoice[0]['no']])
get_products_data = get_invoice_products_data(data_invoice_text)
get_invoice_data  = get_invoices_basic_data(data_invoice_text)
get_client_data   = get_invoices_client_data(data_qr,data_invoice_text)
print(get_client_data.client_id)"""



for invoice in range(len(all_invoice)):
    #print(all_invoice[invoice]['no'])
    data_invoice      = extract_data(all_invoice[invoice]['no'])
    print(data_invoice)
    print('*************************************')
    data_qr           = extract_qr_data(all_invoice[invoice]['no'])
    print(data_qr)
    print('*************************************')
    data_invoice_text = get_brut_format(data_invoice[all_invoice[invoice]['no']])
    get_products_data = get_invoice_products_data(data_invoice_text)
    get_invoice_data  = get_invoices_basic_data(data_invoice_text)
    get_client_data   = get_invoices_client_data(data_qr,data_invoice_text)


    existing_client = session.query(ClientTable).filter_by(Client_id=get_client_data.client_id).first()
    if not existing_client:
        clientDb = ClientTable(
            Client_name    = get_client_data.client_name,
            Client_address = get_client_data.client_address,
            Client_id      = get_client_data.client_id,
            Category       = get_client_data.client_cat,  # Assurez-vous que le nom de la colonne est correct
        )
        session.add(clientDb)
        session.commit()
        print('client added to db')

    existing_invoice  = session.query(InvoiceTable).filter_by(Invoice_ref=get_invoice_data.invoice_ref).first()
    if not existing_invoice:
        invoiceDb = InvoiceTable(
            Invoice_ref=get_invoice_data.invoice_ref,
            Invoice_date=get_invoice_data.invoice_date,
            Client_id=get_client_data.client_id,
            Total=get_invoice_data.total_products
        )
        session.add(invoiceDb)
        session.commit()
        print('invoice added to db')
    for product_key, product_instance in get_products_data.items():
        existing_product = session.query(ProductTable).filter_by(Product_name=product_instance.name_product).first()
        
        if not existing_product:
            # Créer une instance de ProductTable et l'ajouter à la session
            existing_product  = ProductTable(
                Product_name  = product_instance.name_product,
                Product_price = product_instance.price,
            )
            session.add(existing_product)
            session.commit()  # Committer pour obtenir l'id généré
            print('product added to db')

            quantityDb      = InvoiceProductQuantity(
                Invoice_id  = invoiceDb.Invoice_id,
                Product_id  = existing_product.Product_id,  # Utilisez l'id du produit existant
                quantity    = product_instance.quantity,
            )
            session.add(quantityDb)
            session.commit()
            print('quantity from new product added to db')

        else :
                quantityDb    = InvoiceProductQuantity(
                Invoice_id    = invoiceDb.Invoice_id,
                Product_id    = existing_product.Product_id,  # Utilisez l'id du produit existant
                quantity      = product_instance.quantity,
                    )
                session.add(quantityDb)
                session.commit()
                print('quantity from product who already exist added to db')

#print(get_products_data)"""