import streamlit as st
import pandas as pd
import hashlib
import json
import os
from datetime import datetime
import socket

# Nome do arquivo JSON
JSON_FILE = "dados.json"

# Função para gerar o token único para cada usuário
def gerar_token(cpf_ou_cnpj):
    secret_key = "chave_secreta_segura"
    return hashlib.sha256(f"{cpf_ou_cnpj}{secret_key}".encode()).hexdigest()

# Função para carregar dados do JSON
def carregar_dados():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            return pd.DataFrame(json.load(f))
    else:
        # Cria dados iniciais se o arquivo JSON não existir
        dados_iniciais = [
            {"CPF_ou_CNPJ": "12345678901", "Nome": "João", "Email": "joao@example.com",
             "Codigo_Bancario": "001", "Numero_Agencia": "0001", "Numero_Conta": "12345-6",
             "Token": gerar_token("12345678901"), "Atualizado_Em": None, "IP": None},
            {"CPF_ou_CNPJ": "98765432100", "Nome": "Maria", "Email": "maria@example.com",
             "Codigo_Bancario": "033", "Numero_Agencia": "1234", "Numero_Conta": "54321-0",
             "Token": gerar_token("98765432100"), "Atualizado_Em": None, "IP": None},
        ]
        with open(JSON_FILE, "w") as f:
            json.dump(dados_iniciais, f, indent=4)
        return pd.DataFrame(dados_iniciais)

# Função para salvar dados no JSON
def salvar_dados(df):
    with open(JSON_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=4)

# Função para obter o IP do usuário
def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "IP não disponível"

# Carrega os dados do JSON
dados_df = carregar_dados()

# Log de usuários e tokens para envio
for _, row in dados_df.iterrows():
    print(f"Usuário: {row['Nome']}, CPF/CNPJ: {row['CPF_ou_CNPJ']}, Token: {row['Token']}")

# Função para obter os parâmetros da URL
def get_query_params():
    query_params = st.query_params
    cpf_ou_cnpj = query_params.get("cpf_ou_cnpj", None)
    token = query_params.get("token", None)
    return cpf_ou_cnpj, token

# Obtém CPF ou CNPJ e token da URL
cpf_ou_cnpj_param, token_param = get_query_params()
registro = None

if cpf_ou_cnpj_param and token_param:
    registro = dados_df[dados_df["CPF_ou_CNPJ"] == cpf_ou_cnpj_param]

if registro is not None and not registro.empty:
    registro = registro.iloc[0]
    # Verifica se o token é válido
    if token_param != registro["Token"]:
        st.error("Token inválido. Acesso negado.")
        st.stop()
else:
    st.error("CPF ou CNPJ inválido ou não encontrado.")
    st.stop()

# Título e subtítulo
st.title("Formulário com Validação de Token")
st.subheader("Atualize seus dados bancários ( Banco/Agencia/Conta )")

# Verifica se os dados já foram atualizados
if registro["Atualizado_Em"]:
    st.info(f"Seus dados já foram atualizados em: {registro['Atualizado_Em']}")
    st.write(f"Banco: {registro['Codigo_Bancario']}")
    st.write(f"Agência: {registro['Numero_Agencia']}")
    st.write(f"Conta: {registro['Numero_Conta']}")
    st.stop()

# Início do formulário
with st.form("formulario_exemplo"):
    # Campos do formulário com valores pré-preenchidos
    cpf_ou_cnpj = st.text_input("CPF ou CNPJ", value=registro["CPF_ou_CNPJ"], disabled=True)
    nome = st.text_input("Nome", value=registro["Nome"], disabled=True)
    email = st.text_input("E-mail", value=registro["Email"], disabled=True)
    codigo_bancario = st.text_input("Código Bancário", value=registro["Codigo_Bancario"])
    numero_agencia = st.text_input("Número da Agência", value=registro["Numero_Agencia"])
    numero_conta = st.text_input("Número da Conta", value=registro["Numero_Conta"])

    # Botão para enviar
    submit_button = st.form_submit_button("Enviar")

# Verificação se o botão foi clicado
if submit_button:
    # Atualiza os dados no DataFrame
    atualizado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_usuario = get_ip()
    dados_df.loc[dados_df["CPF_ou_CNPJ"] == cpf_ou_cnpj, ["Codigo_Bancario", "Numero_Agencia", "Numero_Conta", "Atualizado_Em", "IP"]] = [
        codigo_bancario, numero_agencia, numero_conta, atualizado_em, ip_usuario
    ]
    # Salva os dados no JSON
    salvar_dados(dados_df)
    st.success("Dados atualizados com sucesso!")
    st.write(f"Atualizado em: {atualizado_em}")
    st.write(f"IP do usuário: {ip_usuario}")
    st.write(f"Código Bancário: {codigo_bancario}")
    st.write(f"Número da Agência: {numero_agencia}")
    st.write(f"Número da Conta: {numero_conta}")