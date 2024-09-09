import streamlit as st
import mysql.connector
import random
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from tools.app_config import conectar_banco_dados
# .streamlit/secrets.toml


def generate_barcode(code_text):
    # Gerar o código de barras Code128
    code = Code128(code_text, writer=ImageWriter())
    buffer = BytesIO()
    code.write(buffer)
    buffer.seek(0)
    return buffer

def get_product_details(titulo, serial_number):
    try:
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute("""
            SELECT * FROM produtos WHERE titulo = %s AND serial_number = %s
        """, (titulo, serial_number))
        return mycursor.fetchone()
    except mysql.connector.Error as err:
        st.error(f"Erro ao buscar detalhes do produto: {err}")
        return None

def calculate_check_digit(ean12):
    total = 0
    for i, digit in enumerate(ean12):
        digit = int(digit)
        if i % 2 == 0:
            total += digit
        else:
            total += digit * 3
    return (10 - (total % 10)) % 10

def generate_product_id():
    prefix = '547'  # Prefixo da empresa
    product_code = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    ean12 = prefix + product_code
    check_digit = calculate_check_digit(ean12)
    ean13 = ean12 + str(check_digit)
    return ean13

def product_exists(titulo, serial_number):
    try:
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute("""
            SELECT COUNT(*) FROM produtos 
            WHERE titulo = %s AND serial_number = %s
        """, (titulo, serial_number))
        return mycursor.fetchone()[0] > 0
    except mysql.connector.Error as err:
        st.error(f"Erro ao verificar existência do produto: {err}")
        return False