from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, DateTime, ARRAY, Float,Text,Table,and_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import pyodbc

Base = declarative_base()

class InvoiceTable(Base):
    __tablename__ = 'Invoice'
    __table_args__ = {'schema': 'OCRdb'}

    Invoice_id    = Column(Integer, primary_key=True)
    Invoice_ref   = Column(String(20))
    Invoice_date  = Column(String(50))
    Client_id     = Column(String(10), ForeignKey('OCRdb.Client.Client_id'))
    Total         = Column(Float)

    client = relationship("ClientTable", back_populates="invoices")
    quantities = relationship("InvoiceProductQuantity", back_populates="invoice")


class ClientTable(Base):
    __tablename__  = 'Client'
    __table_args__ = {'schema': 'OCRdb'}

    Client_name    = Column(String(50))
    Client_address = Column(String(100))
    Client_id      = Column(String(10), primary_key=True)
    Category       = Column(String(1))

    invoices = relationship("InvoiceTable", back_populates="client")


class ProductTable(Base):
    __tablename__   = 'Product'
    __table_args__ = {'schema': 'OCRdb'}

    Product_id      = Column(Integer, primary_key=True)
    Product_name    = Column(String(50))
    Product_price   = Column(Float)

    quantities = relationship("InvoiceProductQuantity", back_populates="product")


class InvoiceProductQuantity(Base):
    __tablename__  = 'Invoice_Product_Quantity'
    __table_args__ = {'schema': 'OCRdb'}

    quantity_id   = Column(Integer,primary_key=True)
    Invoice_id    = Column(Integer, ForeignKey('OCRdb.Invoice.Invoice_id'))
    Product_id    = Column(Integer, ForeignKey('OCRdb.Product.Product_id'))
    quantity      = Column(Integer)

    invoice = relationship("InvoiceTable", back_populates="quantities")
    product = relationship("ProductTable", back_populates="quantities")

def connectBd():
    try:
        load_dotenv('.env')

        SERVER   = os.environ['SERVER']
        DATABASE = os.environ['DATABASE']
        USERNAME = os.environ['DBUSERNAME']
        PASSWORD = os.environ['PASSWORD']
        
        # connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
        connectionString = f'mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver=ODBC+Driver+18+for+SQL+Server'
        print(connectionString)
       
        conn = create_engine(connectionString) 
    
    except Exception  as e:
        print(f"Erreur lors de la connexion à la BD OCR: {e}")
        return None
    else:
        return conn

def createsession(engine):
    # Création de la session en utilisant l'engine passé en paramètre
    Session = sessionmaker(bind=engine,autoflush=False)
    session = Session()
    session.autocommit = True
    return session
