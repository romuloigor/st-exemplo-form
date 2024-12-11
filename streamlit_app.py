import streamlit as st
import pandas as pd
import hashlib
import json
import os
from datetime import datetime
import socket
from fpdf import FPDF
import hmac

# Nome do arquivo JSON
JSON_FILE      = "dados.json"
JSON_PERGUNTAS = "perguntas.json"
SECRET_KEY     = "token"  # Chave secreta para gerar o HMAC

# Função para gerar o token único para cada usuário
def gerar_token(cpf_ou_cnpj):
    secret_key = "chave_secreta_segura"
    return hashlib.sha256(f"{cpf_ou_cnpj}{secret_key}".encode()).hexdigest()

def carregar_perguntas():
    if os.path.exists(JSON_PERGUNTAS):
        with open(JSON_PERGUNTAS, "r") as f:
            return json.load(f)

# Função para carregar dados do JSON
def carregar_dados():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            return pd.DataFrame(json.load(f))
    else:
        # Cria dados iniciais se o arquivo JSON não existir
        dados_iniciais = [
            {"CPF_ou_CNPJ": "12345678901", "Nome": "João", "Email": "joao@example.com",
             
             "conjugal":0, "profissional":0, "financeira":0, "familiar":0, "proposito_de_vida":0, "rede_de_amigos":0, "emocional":0,
             
             "Token": gerar_token("12345678901"), "Atualizado_Em": None},

            {"CPF_ou_CNPJ": "98765432100", "Nome": "Maria", "Email": "maria@example.com",
             "Codigo_Bancario": "033", "Numero_Agencia": "1234", "Numero_Conta": "54321-0",
             "Token": gerar_token("98765432100"), "Atualizado_Em": None},
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

# Log de usuários e tokens para envio
for _, row in dados_df.iterrows():
    print(f"?cpf_ou_cnpj={row['CPF_ou_CNPJ']}&token={row['Token']}")

# Função para obter os parâmetros da URL
def get_query_params():
    query_params = st.query_params
    cpf_ou_cnpj = query_params.get("cpf_ou_cnpj", None)
    token = query_params.get("token", None)
    return cpf_ou_cnpj, token

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
st.title("Formulário MAP")
st.subheader("Nutricionista Deh")

# Verifica se os dados já foram atualizados
if registro["Atualizado_Em"]:
    st.info(f"Seus dados já foram atualizados em: {registro['Atualizado_Em']}")

perguntas = carregar_perguntas()
f1_options = ["Péssimo","Horrível","Muito ruim","Ruim","Fraco","Mediano","Razoável","Bom","Muito bom","Ótimo","Excelente"]

m1_graus = [
    "imóvel",
    "1 minuto de caminhada ou cerca de 100 passos",
    "2 minutos de caminhada ou cerca de 200 passos",
    "5 minutos de caminhada ou cerca de 500 passos",
    "10 minutos de caminhada ou cerca de 1.000 passos",
    "20 minutos de caminhada ou cerca de 2.000 passos",
    "40 minutos de caminhada ou cerca de 4.000 passos",
    "60 minutos de caminhada ou cerca de 6.000 passos",
    "80 minutos de caminhada ou cerca de 8.000 passos",
    "100 minutos de caminhada ou cerca de 10.000 passos"
]

m2_graus = [
    "Praticamente não tomo",
    "Tomo pouco as vezes",
    "Tomo pouco quase sempre",
    "Tomo pouco sempre",
    "1 copos/dia",
    "2 copos/dia",
    "3 copos/dia",
    "4 copos/dia",
    "5 copos/dia",
    "6 copos/dia"
]

m3_graus = [
    "Como até 'estourar'",
    "Como além do necessário",
    "Como até ficar muito cheio",
    "Como até ficar cheio",
    "Como até um nível acima do satisfeito",
    "Como até ficar satisfeito",
    "Como quase no ponto certo",
    "Como no ponto certo",
    "Como até perto do ideal",
    "Páro de comer quando estou 90% satisfeito"
]

m4_graus = [
    "como porções mais ou menos iguais nas 3 refeições",
    "ajusto levemente o jantar reduzindo carboidratos",
    "reduzo um pouco os carboidratos no jantar",
    "retiro boa parte dos carboidratos do jantar",
    "começo a diminuir carboidratos no café da manhã",
    "reduzo carboidratos tanto no café quanto no jantar",
    "quase não consumo carboidratos no jantar",
    "reduzo muito os carboidratos do café da manhã",
    "consumo poucos carboidratos no café e jantar",
    "quase elimino carboidratos no café e jantar",
    "como bem pouco carboidratos no café da manhã e na janta"
]

m5_graus = [
    "não como salada",
    "provo salada raramente",
    "como pequena porção 1x/dia",
    "como pequena porção regularmente 1x/dia",
    "como porção moderada 1x/dia",
    "como porção moderada 2x/dia, às vezes",
    "como porção moderada 2x/dia regularmente",
    "como grande porção 1x/dia",
    "como grande porção 1x/dia e pequena em outra refeição",
    "quase 2 grandes porções/dia",
    "2 grandes porções/dia"
]

m6_graus = [
    "não como este tipo de fermentado",
    "experimento muito raramente",
    "uma garfada ocasionalmente",
    "uma garfada/dia",
    "duas garfadas/dia",
    "três garfadas/dia",
    "quatro garfadas/dia",
    "cinco garfadas/dia",
    "cinco garfadas/dia regularmente",
    "quase seis garfadas/dia",
    "cerca de seis garfadas/dia"
]

m7_graus = [
    "não como este tipo de gorduras",
    "como muito raramente",
    "como raramente",
    "como ocasionalmente",
    "como moderadamente",
    "como com alguma frequência",
    "como regularmente",
    "como bastante",
    "como bastante intensamente",
    "como quase intensamente",
    "como com muita intensidade"
]

m8_graus = [
    "nunca faço isto",
    "raramente",
    "muito ocasionalmente",
    "ocasionalmente",
    "às vezes",
    "com alguma frequência",
    "frequentemente",
    "quase todos os dias",
    "praticamente todos os dias",
    "quase 100% dos dias",
    "100% dos dias"
]

m9_graus = [
    "estou sempre com sono no outro dia, atrapalhando muito minhas atividades",
    "quase sempre cansado",
    "regularmente acordo cansado",
    "costumo acordar um pouco cansado",
    "às vezes acordo cansado",
    "acordo razoável",
    "geralmente acordo relativamente bem",
    "costumo acordar bem",
    "acordo bem e descansado na maioria dos dias",
    "acordo quase sempre refrescado",
    "acordo refrescado sempre"
]

m10_graus = [
    "nunca faço isto",
    "raramente",
    "muito ocasionalmente",
    "ocasionalmente",
    "às vezes",
    "com alguma frequência",
    "frequentemente",
    "quase todos os dias",
    "praticamente todos os dias",
    "quase 100% dos dias",
    "faço isso em 100% dos dias"
]

c1 = st.container(border=True)

cpf_ou_cnpj = c1.text_input("CPF ou CNPJ", value=registro["CPF_ou_CNPJ"], disabled=True)
nome        = c1.text_input("Nome",        value=registro["Nome"],        disabled=True)
email       = c1.text_input("E-mail",      value=registro["Email"],       disabled=True)

tab1, tab2, tab3 = st.tabs(["Escore de Vida", "Escore MAP", "Inflamação"])

with tab1:
    st.header("Escore de Vida")

    p1 = st.select_slider( perguntas['form_1'][0], options=f1_options)
    p2 = st.select_slider( perguntas['form_1'][1], options=f1_options)
    p3 = st.select_slider( perguntas['form_1'][2], options=f1_options)
    p4 = st.select_slider( perguntas['form_1'][3], options=f1_options)
    p5 = st.select_slider( perguntas['form_1'][4], options=f1_options)
    p6 = st.select_slider( perguntas['form_1'][5], options=f1_options)
    p7 = st.select_slider( perguntas['form_1'][6], options=f1_options)

    escore_vida = (f1_options.index(p1)+f1_options.index(p2)+f1_options.index(p3)+f1_options.index(p4)+f1_options.index(p5)+f1_options.index(p6)+f1_options.index(p7)/7)
    st.write("Seu escore de vida é: ", round(escore_vida, 2))

with tab2:
    st.header("Escore MAP")

    m1  = st.select_slider( perguntas['form_2']['map_1']['pergunta'], options=m1_graus)
    m2  = st.select_slider( perguntas['form_2']['map_2']['pergunta'], options=m2_graus)
    m3  = st.select_slider( perguntas['form_2']['map_3']['pergunta'], options=m3_graus)
    m4  = st.select_slider( perguntas['form_2']['map_4']['pergunta'], options=m4_graus)
    m5  = st.select_slider( perguntas['form_2']['map_5']['pergunta'], options=m5_graus)
    m6  = st.select_slider( perguntas['form_2']['map_6']['pergunta'], options=m6_graus)
    m7  = st.select_slider( perguntas['form_2']['map_7']['pergunta'], options=m7_graus)
    m8  = st.select_slider( perguntas['form_2']['map_8']['pergunta'], options=m8_graus)
    m9  = st.select_slider( perguntas['form_2']['map_9']['pergunta'], options=m9_graus)
    m10 = st.select_slider( perguntas['form_2']['map_10']['pergunta'], options=m10_graus)

    escore_map = (m1_graus.index(m1)+m2_graus.index(m2)+m3_graus.index(m3)+m4_graus.index(m4)+m5_graus.index(m5)+m6_graus.index(m6)+m7_graus.index(m7)+m8_graus.index(m8)+m9_graus.index(m9)+m10_graus.index(m10)/10)
    st.write("Seu escore MAP é: ", round(escore_map, 2))

with tab3:
    st.header("Inflamação")