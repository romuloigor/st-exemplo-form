import streamlit as st
import pandas as pd
import hashlib
import json
import os

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
             "Token": gerar_token("12345678901")},
            {"CPF_ou_CNPJ": "98765432100", "Nome": "Maria", "Email": "maria@example.com",
             "Codigo_Bancario": "033", "Numero_Agencia": "1234", "Numero_Conta": "54321-0",
             "Token": gerar_token("98765432100")},
        ]
        with open(JSON_FILE, "w") as f:
            json.dump(dados_iniciais, f, indent=4)
        return pd.DataFrame(dados_iniciais)

# Função para salvar dados no JSON
def salvar_dados(df):
    with open(JSON_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=4)

# Carrega os dados do JSON
dados_df = carregar_dados()

# Função para obter os parâmetros da URL
def get_query_params():
    query_params = st.experimental_get_query_params()
    cpf_ou_cnpj = query_params.get("cpf_ou_cnpj", [None])[0]
    token = query_params.get("token", [None])[0]
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

# Título do app
st.title("Formulário com Validação de Token e Persistência")

# Início do formulário
with st.form("formulario_exemplo"):
    # Campos do formulário com valores pré-preenchidos
    cpf_ou_cnpj = st.text_input("CPF ou CNPJ", value=registro["CPF_ou_CNPJ"], disabled=True)
    nome = st.text_input("Nome", value=registro["Nome"])
    email = st.text_input("E-mail", value=registro["Email"])
    codigo_bancario = st.text_input("Código Bancário", value=registro["Codigo_Bancario"])
    numero_agencia = st.text_input("Número da Agência", value=registro["Numero_Agencia"])
    numero_conta = st.text_input("Número da Conta", value=registro["Numero_Conta"])

    # Botão para enviar
    submit_button = st.form_submit_button("Enviar")

# Verificação se o botão foi clicado
if submit_button:
    # Atualiza os dados no DataFrame
    dados_df.loc[dados_df["CPF_ou_CNPJ"] == cpf_ou_cnpj, ["Nome", "Email", "Codigo_Bancario", "Numero_Agencia", "Numero_Conta"]] = [
        nome, email, codigo_bancario, numero_agencia, numero_conta
    ]
    # Salva os dados no JSON
    salvar_dados(dados_df)
    st.success("Dados atualizados com sucesso!")
    st.write(f"Nome: {nome}")
    st.write(f"E-mail: {email}")
    st.write(f"Código Bancário: {codigo_bancario}")
    st.write(f"Número da Agência: {numero_agencia}")
    st.write(f"Número da Conta: {numero_conta}")
    st.write(f"CPF ou CNPJ: {cpf_ou_cnpj}")
