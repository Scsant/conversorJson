import streamlit as st
import pandas as pd
import pdfplumber
import json
import io

# Função para converter Excel para JSON para arquivos grandes
def convert_excel_to_json_large(excel_file):
    try:
        # Ler o arquivo Excel inteiro
        df = pd.read_excel(excel_file, engine='openpyxl')

        # Converter colunas do tipo datetime para string
        for column in df.select_dtypes(include=[pd.Timestamp, 'datetime']).columns:
            df[column] = df[column].astype(str)

        # Dividir em pedaços menores se for necessário para otimizar a conversão
        json_data = []
        chunk_size = 10000  # Número de linhas por chunk
        num_chunks = len(df) // chunk_size + 1

        for i in range(num_chunks):
            chunk = df[i*chunk_size:(i+1)*chunk_size]
            json_data.extend(chunk.to_dict(orient='records'))

        # Converte a lista completa de registros para JSON estruturado
        return json.dumps(json_data, indent=4)
    
    except Exception as e:
        st.error(f"Erro ao processar arquivo Excel: {e}")
        return None

# Função para converter PDF para Excel com manipulação de grandes PDFs
def convert_pdf_to_excel_large(pdf_file):
    tables = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    df_page = pd.DataFrame(table[1:], columns=table[0])  # Converte a tabela para DataFrame
                    tables.append(df_page)
        
        # Combina todas as tabelas em um único DataFrame, caso existam
        if tables:
            df = pd.concat(tables, ignore_index=True)
            return df
        else:
            st.error("Nenhuma tabela foi encontrada no PDF.")
            return None
    
    except Exception as e:
        st.error(f"Erro ao processar arquivo PDF: {e}")
        return None

# Interface do Streamlit
st.title("Conversor de Arquivos para Grandes Volumes")

# Seção para converter Excel em JSON
st.header("Converter Excel para JSON (para arquivos grandes)")
excel_file = st.file_uploader("Faça o upload de um arquivo Excel", type=["xlsx", "xls"])
if excel_file is not None:
    if st.button("Converter Excel para JSON"):
        json_data = convert_excel_to_json_large(excel_file)
        if json_data:
            st.download_button("Baixar JSON", data=json_data, file_name="dados.json", mime="application/json")

# Seção para converter PDF para Excel
st.header("Converter PDF para Excel (para arquivos grandes)")
pdf_file = st.file_uploader("Faça o upload de um arquivo PDF", type="pdf")
if pdf_file is not None:
    if st.button("Converter PDF para Excel"):
        df = convert_pdf_to_excel_large(pdf_file)
        if df is not None:
            towrite = io.BytesIO()
            df.to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)
            st.download_button("Baixar Excel", data=towrite, file_name="dados.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
