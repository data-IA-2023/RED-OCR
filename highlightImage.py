import requests
import time
import numpy as np
import io
import cv2




def highlight_text(image_url):
    try:
        # Récupérer l'image en ligne
        response = requests.get(image_url)
        response.raise_for_status()  # Vérifie si la requête a réussi
        image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
        
        # Convertir l'image en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Appliquer une binarisation adaptative pour séparer le texte du fond
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Inverser les couleurs (texte en blanc)
        binary = cv2.bitwise_not(binary)
        
        # Trouver les contours des régions de texte
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Créer un masque pour les régions de texte
        mask = np.zeros_like(gray)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
        
        # Mettre en évidence le texte dans l'image d'origine
        highlighted_text = cv2.bitwise_and(image, image, mask=mask)
        
        # Afficher l'image résultante
        cv2.imshow("Highlighted Text", highlighted_text)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return highlighted_text
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")



        
"""
# URL de l'image en ligne
image_url = f"https://invoiceocrp3.azurewebsites.net/invoices/{dataset[4]['no']}"

# Appeler la fonction pour mettre en évidence le texte depuis l'URL de l'image
image = highlight_text(image_url)

        # Convertir l'image prétraitée en flux d'octets
image_bytes = cv2.imencode('.png', image)[1].tobytes()

        # Appel à l'API pour lire le texte de l'image en utilisant le flux d'octets
read_result = computervision_client.read_in_stream(io.BytesIO(image_bytes), raw=True)
time.sleep(5)
read_operation_location = read_result.headers["Operation-Location"]
        # Grab the ID from the URL
operation_id = read_operation_location.split("/")[-1]

        # Call the "GET" API and wait for it to retrieve the results 
while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

        # Afficher le texte extrait de l'image
print("Texte extrait de l'image :")
for result in read_result.analyze_result.read_results:
        for line in result.lines:
           donnees_ligne = {
               'text': line.text,
               'bbox': line.bounding_box,
           }
        
print()"""
