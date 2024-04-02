
import regex as re

class Product:
    def __init__(self, name_product, quantity, price):
        self.name_product = name_product
        self.quantity     = quantity
        self.price        = price

class Invoice:
    def __init__(self, invoice_ref, invoice_date, total_products):
        self.invoice_ref    = invoice_ref
        self.invoice_date   = invoice_date
        self.total_products = total_products

class Client:
    def __init__(self,client_id,client_cat,client_address,client_name):
        self.client_id      = client_id
        self.client_address = client_address
        self.client_name    = client_name
        self.client_cat     = client_cat


def get_brut_format(invoices):
    brut_format = ''
    for row in invoices:
        brut_format += row['text'] + "\n"
    
    return brut_format

def get_invoices_basic_data(brut_format):
   

    regex_invoice     = r"fac_\d{4}_\d{4}"
    regex_date        = r"date.*?(\d+)-(\d+)-(\d+).(\d+).(\d+).(\d+)"
    regex_total       = r"total\s(\d+(?:\.\d+)?)\seuro"

    match_invoice     = re.search(regex_invoice, brut_format.lower())
    match_date        = re.search(regex_date, brut_format.lower())
    match_total       = re.search(regex_total, brut_format.lower())

    if match_invoice:
        invoice_ref = match_invoice.group()
    else:
        invoice_ref = None

    if match_date:
        result_date = match_date.group(0)
        invoice_date = re.sub(r'^date\s*', '', result_date)
    else:
        invoice_date = None

    if match_total:
        total_products = match_total.group(1)
    else:
        total_products = None

    data_invoice = Invoice(invoice_ref, invoice_date, total_products)
   
    return data_invoice



def get_invoices_client_data(qr_data,brut_format):


    regex_address     = r"address\s.*\n.*"
    regex_name        = r"bill\sto\s(.*?)\s(.*?ing)"
    match_address     = re.search(regex_address, brut_format.lower())
    match_name        = re.search(regex_name, brut_format.lower())


    if match_address:
        result_address = match_address.group(0)
        client_address = re.sub(r'^address\s*', '', result_address).replace('\n', ' ')
    else:
        client_address = None

    if match_name:
        client_name = match_name.group(1)
    else:
        client_name = None


    data_client  = Client(client_name,client_address)

    return data_client



def get_invoices_client_data(brut_format):
    regex_products    = r"(.+)\n(\d+)\sx\s(?:\D*)(\d+\.\d+)\sEuro"
       
    match_products    = re.findall(regex_products, brut_format.lower(),re.IGNORECASE)

    products = {}
    if match_products:
        for i, product_info in enumerate(match_products,1):
            product_list = Product(product_info[0].replace('.', ''), product_info[1], product_info[2].replace(' ',''))
            products[f'product {i}'] = product_list

    data_products  = Product(products)
       
    return data_products
