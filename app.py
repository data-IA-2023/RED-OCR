# Importation de Streamlit
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from  getInvoices import *
from  extractData import *
from  getData import *
from  highlightImage import *
from ocrdb import *
from collections import Counter
from main import *

from sqlalchemy.orm import join
conn = connectBd()

session = createsession(conn)

if session:
    print("connection succes")

def page_accueil():
    st.title('Accueil')
    all_invoice = get_all_invoices()
    invoices_in_db  = len(session.query(InvoiceTable).all())
    # Nombre de factures depuis la dernière date (pour ajuster le problème Azure)
    total_invoices = len(all_invoice)

    # Calcul du nombre ajusté de factures
    adjusted_invoice_count = total_invoices - invoices_in_db
    

    count_client  = len(session.query(ClientTable).all())
    count_product = len(session.query(ProductTable.Product_id).all())
    # Création d'un titre pour votre application
    st.title('OCR INVOICES')
    if st.button("mettre à jour la base de donnée"):
        get_data_from_all_invoice()
    st.write(f"nombres total de nouvelles factures:", adjusted_invoice_count)
    st.write(f"nombres total de factures:", total_invoices)
    st.write(f"nombres total de factures en base de données:", invoices_in_db)
    st.write(f"nombres de clients", count_client)
    st.write(f"nombres de produits", count_product)

    st.subheader('Nombre de clients')
    client_cat_a = len(session.query(ClientTable).filter(ClientTable.Category == 'A').all())
    client_cat_b = len(session.query(ClientTable).filter(ClientTable.Category == 'B').all())
    client_cat_c = len(session.query(ClientTable).filter(ClientTable.Category == 'C').all())
    # Données
    categories = ['Catégorie A', 'Catégorie B', 'Catégorie C']
    clients = [client_cat_a, client_cat_b, client_cat_c]

    # Créer le graphique
    fig, ax = plt.subplots()
    ax.bar(categories, clients)

    # Ajouter des étiquettes
    for i, v in enumerate(clients):
        ax.text(i, v + 0.1, str(v), ha='center')

    # Personnalisation
    ax.set_xlabel('Catégorie')
    ax.set_ylabel('Nombre de clients')
    ax.set_title('Nombre de clients par catégorie')

    # Afficher le graphique dans Streamlit
    st.pyplot(fig)

    st.subheader('Gestion de produits')

    all_products    = session.query(InvoiceProductQuantity.Product_id).all()

    # Compter le nombre de fois que chaque élément est répété
    comptages = Counter(all_products)

    # Récupérer les cinq éléments les plus fréquents
    top_5 = comptages.most_common(5)

    # Extraire les noms des produits et leurs fréquences
    products_top_5 = []
    frequences = []
    for element, count in top_5:
        product_name = session.query(ProductTable.Product_name).filter(ProductTable.Product_id == element[0]).scalar()
        if product_name:
            products_top_5.append(product_name)
            frequences.append(count)

    # Définition du backend Matplotlib compatible avec Streamlit
    plt.switch_backend('module://ipykernel.pylab.backend_inline')

    # Créer le graphique à colonnes
    plt.figure(figsize=(10, 6))
    plt.bar(products_top_5, frequences, color='skyblue')
    plt.xlabel('Produits')
    plt.ylabel('Fréquence')
    plt.title('Top 5 des produits les plus commandés')
    plt.xticks(rotation=45)  # Rotation des étiquettes de l'axe des x pour une meilleure lisibilité

    # Afficher le graphique dans Streamlit
    st.pyplot(plt)



    # Récupérer les quantités depuis la base de données
    quantities = session.query(InvoiceProductQuantity.quantity).all()

    # Vérifier et formater les données de quantités
    quantities = [int(q[0]) for q in quantities if q[0] is not None]  # Filtrer les valeurs non nulles et les convertir en entiers

    # Vérifier si des données sont présentes
    if quantities:
        # Création du boxplot
        plt.figure(figsize=(10, 6))
        sns.boxplot(y=quantities)
        plt.title('Distribution des Quantités')
        plt.ylabel('Quantités')
        st.pyplot(plt)


def page_invoice():
    st.title('Page Facture')
    invoices   = session.query(InvoiceTable.Invoice_ref).all()
    invoices   = [i[0] for i in invoices]

    selected_invoices = st.selectbox("Sélectionnez une facture:", invoices)
    if selected_invoices :
        Total_by_product_quantity_price = 0
        # Récupérer l'ID de la facture en fonction de la relation entre selected_invoices et Invoice_ref
        invoice_id = session.query(InvoiceTable.Invoice_id).filter(InvoiceTable.Invoice_ref == selected_invoices).first()[0]

        # Récupérer l'ID du client en fonction de la relation entre invoice_id et Invoice_id
        clientId = session.query(InvoiceTable.Client_id).filter(InvoiceTable.Invoice_id == invoice_id).first()[0]

        # Récupérer le nom du client en fonction de l'ID du client
        client = session.query(ClientTable.Client_name).filter(ClientTable.Client_id == clientId).first()[0]

        # Récupérer l'adresse du client en fonction de l'ID du client
        client_address = session.query(ClientTable.Client_address).filter(ClientTable.Client_id == clientId).first()[0]

        productsId     =  session.query(InvoiceProductQuantity.Product_id).filter(InvoiceProductQuantity.Invoice_id == invoice_id).all()

        # Récupérer le total de la facture en fonction de l'ID de la facture
        total = session.query(InvoiceTable.Total).filter(InvoiceTable.Invoice_id == invoice_id).first()[0]

        st.write(client)
        st.write(f"Adresse: {client_address}")
        for product_id in productsId:
            product_name = session.query(ProductTable.Product_name).filter(ProductTable.Product_id == product_id[0]).first()[0]
            product_price = session.query(ProductTable.Product_price).filter(ProductTable.Product_id == product_id[0]).first()[0]
            product_quantity = session.query(InvoiceProductQuantity.quantity).filter(InvoiceProductQuantity.Product_id == product_id[0]).first()[0]
            st.write(f"{product_name}: {product_quantity} x {product_price} €")
            product_quantity_price = product_quantity * product_price
            Total_by_product_quantity_price = product_quantity_price + Total_by_product_quantity_price
        st.write(f"Total: {total} €")
        st.write(f"Total en fonction de ce qui a été récupéré : {Total_by_product_quantity_price} €")
        st.write (f"Différence: {Total_by_product_quantity_price - total } €")




def page_client():
    st.title('Page client')
    client   = session.query(ClientTable.Client_id).all()
    client   = [i[0] for i in client]

    selected_client = st.selectbox("Sélectionnez un client:", client)
    if selected_client :
                # Récupérer l'adresse du client en fonction de l'ID du client


        client_address = session.query(ClientTable.Client_address).filter(ClientTable.Client_id == selected_client).first()[0]


                # Récupérer l'ID du client en fonction de la relation entre invoice_id et Invoice_id
        client_name = session.query(ClientTable.Client_name).filter(ClientTable.Client_id == selected_client).first()[0]

        # Récupérer l'ID de la facture en fonction de la relation entre selected_invoices et Invoice_ref
        invoice_ref = session.query(InvoiceTable.Invoice_ref).filter(InvoiceTable.Client_id == selected_client).all()
                
                # Récupérer l'ID de la facture en fonction de la relation entre selected_invoices et Invoice_ref
        invoice_id = session.query(InvoiceTable.Invoice_id).filter(InvoiceTable.Client_id == selected_client).all()

        st.write(client_name)
        st.write(f"Adresse: {client_address}")

        st.write("Facture du client: ")
        for invoices in invoice_ref:
            st.write(invoices[0])

        all_product_bought_from_client = []

        for id in invoice_id:
            products_bought = session.query(InvoiceProductQuantity.Product_id).filter(InvoiceProductQuantity.Invoice_id == id[0]).all()
            all_product_bought_from_client.extend(products_bought)


        all_product_bought_from_client_name =[]
        for product in all_product_bought_from_client : 
            products_bought_name = session.query(ProductTable.Product_name).filter(ProductTable.Product_id == product[0]).all()
            all_product_bought_from_client_name.extend(products_bought_name)

        # Compter le nombre de fois que chaque élément est répété
        comptages = Counter(all_product_bought_from_client_name)

        # Trouver l'élément le plus fréquent
        element_plus_frequent = comptages.most_common(1)[0][0]

        st.write(f"Produit le plus acheté : {element_plus_frequent[0]}")

def page_produit():
    st.title('Page produit')
    product   = session.query(ProductTable.Product_name).all()
    product   = [i[0] for i in product]

    selected_product = st.selectbox("Sélectionnez un client:", product)
    if selected_product :
        
        product_price = session.query(ProductTable.Product_price).filter(ProductTable.Product_name == selected_product).first()[0]
        product_id    = session.query(ProductTable.Product_id).filter(ProductTable.Product_name == selected_product).first()[0]

        bought_times  = len(session.query(InvoiceProductQuantity.Product_id).filter(InvoiceProductQuantity.Product_id == product_id).all())

        st.write(selected_product)
        st.write(f"prix: {product_price} €")
        st.write(f'Nombre de fois commandé: {bought_times}')


def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choisissez une page", ["Accueil", "Facture", "Client",'Produit'])

    if page == "Accueil":
        page_accueil()
    elif page == "Facture":
        page_invoice()
    elif page == "Client":
        page_client()
    elif page == "Produit":
        page_produit()

if __name__ == "__main__":
    main()

