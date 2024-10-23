import streamlit as st
import pdfplumber
import re
import os

# Custom function to format numbers in Brazilian currency format
def format_currency(value):
    # Format the number as a string with commas and periods for thousands and decimal places
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Function to extract and sum financial values (R$) from the PDF
def extract_and_sum_financial_values(pdf_path):
    total_sum = 0
    pattern = re.compile(r'R\$ ?[\d\.,]+')
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    financial_values = pattern.findall(text)
                    for value in financial_values:
                        # Replace commas with periods for decimal conversion
                        value_cleaned = value.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                        total_sum += float(value_cleaned)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
    
    return total_sum

# Function to extract and sum 'Quantidade de Protesto' values from the PDF
def extract_and_sum_quantidade_de_protesto(pdf_path):
    total_protesto = 0
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Search for the "Quantidade de Protesto" field in the text
                    lines = text.split('\n')
                    for line in lines:
                        if "Quantidade de Protesto" in line:
                            try:
                                # Extract the number from the line
                                value = extract_number_from_line(line)
                                total_protesto += value
                            except ValueError:
                                st.warning(f"Could not extract a number from line: {line}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
    
    return total_protesto

# Helper function to extract numbers from a line
def extract_number_from_line(line):
    match = re.search(r'\d+', line)  # A basic regular expression to find numbers
    if match:
        return int(match.group())  # Return the found number as an integer
    else:
        raise ValueError("No number found in the line.")

# Streamlit UI layout
st.title("GRC/CP - Somador de R$ e Quantidade de Protesto")
st.write("Faça o upload de um arquivo PDF para somar os valores em (R$) e a quantidade de protesto dentro dele.")

# Upload file
uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

# Process file if uploaded
if uploaded_file is not None:
    # Save uploaded file temporarily
    temp_file_path = os.path.join("temp", uploaded_file.name)
    if not os.path.exists("temp"):
        os.makedirs("temp")
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract and sum financial values
    financial_result = extract_and_sum_financial_values(temp_file_path)
    if financial_result is not None:
        formatted_financial_result = format_currency(financial_result)
        st.success(f"Soma total dos valores em (R$): {formatted_financial_result}")
    else:
        st.error("Falha ao processar os valores financeiros no arquivo PDF.")
    
    # Extract and sum 'Quantidade de Protesto' values
    protesto_result = extract_and_sum_quantidade_de_protesto(temp_file_path)
    if protesto_result is not None:
        st.success(f"Quantidade total de protestos: {protesto_result}")
    else:
        st.error("Falha ao processar a quantidade de protestos no arquivo PDF.")

