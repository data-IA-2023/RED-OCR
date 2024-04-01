import requests
def get_all_invoices(): 
    url = "https://invoiceocrp3.azurewebsites.net/invoices"

    headers = {
        "accept": "application/json"
    }


    response = requests.get(url, headers=headers)

    data = []
    data = response.json()
    data = data.get('invoices')


    lastDate = data[-1]['dt']
    flag = False
    while not flag : 
        urldata  = f"https://invoiceocrp3.azurewebsites.net/invoices?start_date={lastDate}"
        responseData = requests.get(urldata, headers=headers)
        if responseData.status_code == 200:
                adddata = responseData.json()
                adddata = adddata.get('invoices')
                if len(adddata) == 0:
                    flag = True
                else:
                    data.extend(adddata)
                    lastDate = data[-1]['dt']
                    print(lastDate,data[-1])
        else :
            print(f"Erreur: {response.status_code} - {response.reason}") 
            flag = True

    return data
