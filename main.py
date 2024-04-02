from  getInvoices import *
from  extractData import *
from  getData import *
from  highlightImage import *

all_invoice = get_all_invoices()

test_invoice = all_invoice[:1]

for invoice in range(len(test_invoice)):
    print(test_invoice[invoice]['no'])
    data_invoice      = extract_data(test_invoice[invoice]['no'])
    print(data_invoice)
    print('*************************************')
    data_qr           = extract_qr_data(test_invoice[invoice]['no'])
    print(data_qr)
    print('*************************************')
    data_invoice_text = get_brut_format(data_invoice[test_invoice[invoice]['no']])
    get_invoice_data  = get_invoices_basic_data(data_invoice_text)

print(get_invoice_data.total_products)