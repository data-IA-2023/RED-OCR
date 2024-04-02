from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from dotenv import load_dotenv
from PIL import Image
import regex as re
from io import BytesIO
from pyzbar.pyzbar import decode
import requests
import os
import time


load_dotenv()

'''
Authenticates your credentials and creates a client.
'''
subscription_key = os.environ["VISION_KEY"]
endpoint = os.environ["VISION_ENDPOINT"]

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
'''
END - Authenticate
'''
def extract_data(invoices):
    invoices_data = {}
    '''
    OCR: Read File using the Read API, extract text - remote
    This example will extract text in an image, then print results, line by line.
    This API call can also extract handwriting style text (not shown).
    '''
    # Get an image with text
    read_image_url = f"https://invoiceocrp3.azurewebsites.net/invoices/{invoices}"

    # Call API with URL and raw response (allows you to get the operation location)
    read_response = computervision_client.read(read_image_url,  raw=True)

    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]
    
    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    invoices_data[invoices] = []
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
    # Itérez à travers chaque objet de ligne
            for ligne_objet in text_result.lines:
            # Créez un dictionnaire pour stocker les données de cette ligne
                    donnees_ligne = {
                        "text": ligne_objet.text,
                        #"bounding_box": ligne_objet.bounding_box,
                        # Ajoutez plus d'attributs selon vos besoins
                    }
                    
                    # Ajoutez les données de cette ligne à la liste correspondante dans le dictionnaire principal
                    invoices_data[invoices].append(donnees_ligne)



    return invoices_data



# Fonction pour télécharger une image à partir d'une URL
def download_image(invoices):
    url = f'https://invoiceocrp3.azurewebsites.net/invoices/{invoices}'
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image

# Fonction pour lire les codes-barres à partir d'une image
def read_barcodes(image):
    merged_text =''
    decoded_objects = decode(image)
    for obj in decoded_objects:
        merged_text += obj.data.decode("utf-8") + ' '

    return merged_text

def extract_qr_data(url):
    # URL de l'image en ligne
    image_url = url

    # Télécharger l'image à partir de l'URL
    image = download_image(image_url)



    # Lire les codes-barres à partir de l'image téléchargée
    rep = read_barcodes(image)

    qr_dict = {}

    # Utilisation d'une expression régulière qui considère les sauts de ligne
    pattern = r'(\w+):([^\n]+)'
    matches = re.findall(pattern, rep)

    # Remplissage du dictionnaire avec les correspondances trouvées
    for key, value in matches:
        qr_dict[key.strip()] = value.strip()  # .strip() retire les espaces excédentaires
    separated_values = [{qr_key: qr_value} for qr_key, qr_value in qr_dict.items() if qr_key in ['CUST', 'CAT']]

    return qr_dict

    