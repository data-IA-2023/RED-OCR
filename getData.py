
import regex as re
from  extractData import *
from unidecode import unidecode

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
    def __init__(self,client_name,client_address,client_id,client_cat):
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



def get_invoices_client_data(qr_data, brut_format):
    regex_address = r"address\s.*\n.*"
    regex_name    = r"bill\sto\s(.*?)\s(.*?ing)"
    
    match_address = re.search(regex_address, brut_format.lower())
    match_name    = re.search(regex_name, brut_format.lower())

    client_name    = None
    client_address = None
    client_id      = None
    client_cat     = None

    if match_address:
        result_address = match_address.group(0)
        client_address = re.sub(r'^address\s*', '', result_address).replace('\n', ' ')
 

    if match_name:
        client_name_brut = match_name.group(1)
        client_name      = unidecode(client_name_brut)


    if qr_data:
        client_id = qr_data.get('CUST', None)
        client_cat = qr_data.get('CAT', None)


    # Créez un objet Client avec les valeurs extraites
    data_client = Client(client_name, client_address, client_id, client_cat)

    return data_client



def get_invoice_products_data(brut_format):

    regex_invoice           = r"fac_\d{4}_\d{4}"
    regex_address           = r"address\s.*\n.*"
    regex_date              = r"date.*?(\d+)-(\d+)-(\d+).(\d+).(\d+).(\d+)"
    regex_total             = r'total\s*(.*?\b(?:euro|$))'

    regex_products_name             = r"([^\d\n]+\.)\n"
    regex_products_quantity         = r"(?:\b(\d+)?\s*x?\s*)?(.*?\b(?:euro|$))"
    regex_products_price            = r"(\d+\.\s*\d+)\s*euro"


    text_without_total         = re.sub(regex_total, '', brut_format.lower())
    #text_without_price          = re.sub(regex_products_price,'',text_without_total)
    text_without_invoice       = re.sub(regex_invoice, '', text_without_total)
    text_without_date          = re.sub(regex_date, '', text_without_invoice)
    text_without_adress        = re.sub(regex_address,'',text_without_date)
    #print(text_without_adress)

    #text_for_quantity = re.sub(regex_address, '', text_for_quantity)"""


    match_products_name             = re.findall(regex_products_name, text_without_total,re.IGNORECASE)
    match_products_quantity         = re.findall(regex_products_quantity, text_without_adress,re.IGNORECASE)
    match_products_price            = re.findall(regex_products_price, text_without_total,re.IGNORECASE)
   
    print(match_products_quantity)
    products = {}
    if match_products_name and match_products_quantity and match_products_price:
        for i, (product_info, quantity_match, price_match) in enumerate(zip(match_products_name, match_products_quantity, match_products_price), 1):
            product_name = product_info if product_info != '' else None
            #print(product_name)
            quantity = quantity_match[0] if quantity_match and quantity_match[0] != '' else None
            #print(quantity)
            price = price_match if price_match != '' else None
            #print(price)
    

            product_list = Product(product_name.replace('.', ''), quantity, price.replace(' ', ''))
            products[f'product {i}'] = product_list

    data_products  = products
       
    return data_products
