import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib

# --- CONFIGURAÇÃO DA PÁGINA E LOGO ---
# Se você subir um arquivo chamado logo_jonas.png, ele aparecerá no topo
st.set_page_config(page_title="Gestão do Jonas", page_icon="🏗️", layout="centered")

def carregar_logo():
    try:
        st.image("logo_jonas.png", width=150)
    except:
        st.title("🏗️ Gestão: Bar & Obra")

# --- FUNÇÕES DE BANCO DE DADOS ---
conn = sqlite3.connect('gestao_irmao.db', check_same_thread=False)
cursor = conn.cursor()

# Criar tabela de usuários se não existir
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                  (usuario TEXT PRIMARY KEY, senha TEXT)''')
conn.commit()

# Função simples para transformar senha em código secreto (Hash)
def gerar_hash(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

# --- LÓGICA DE ACESSO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

def login():
    carregar_logo()
    st.subheader("Login de Acesso")
    
    # Verifica se já existe algum usuário cadastrado
    usuarios = pd.read_sql_query("SELECT * FROM usuarios", conn)
    
    if usuarios.empty:
        st.warning("Nenhum usuário encontrado. Crie o primeiro acesso:")
        novo_u = st.text_input("Defina seu Usuário")
        nova_s = st.text_input("Defina sua Senha", type="password")
        if st.button("CRIAR MEU ACESSO"):
            cursor.execute("INSERT INTO usuarios VALUES (?, ?)", (novo_u, gerar_hash(nova_s)))
            conn.commit()
            st.success("Acesso criado! Agora faça login.")
            st.rerun()
    else:
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            senha_hash = gerar_hash(pw)
            busca = cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (user, senha_hash)).fetchone()
            if busca:
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")

# --- APP PRINCIPAL (SÓ APARECE SE ESTIVER LOGADO) ---
if not st.session_state['autenticado']:
    login()
else:
    # Menu Lateral
    st.sidebar.title("Menu")
    pagina = st.sidebar.selectbox("Ir para:", ["Dashboard", "Configurações"])
    negocio = st.sidebar.radio("Selecione o Negócio:", ["🍺 BAR", "🚧 OBRA"])
    
    if st.sidebar.button("Sair"):
        st.session_state['autenticado'] = False
        st.rerun()

    if pagina == "Dashboard":
        carregar_logo()
        # ... (Aqui continua todo o código de Ganhos/Gastos que já tínhamos)
        st.subheader(f"📊 Resumo Financeiro - {negocio}")
        df_total = pd.read_sql_query(f"SELECT * FROM financeiro WHERE negocio='{negocio}'", conn)
        # (O resto do seu código de lançamentos e exclusão entra aqui...)
        
    elif pagina == "Configurações":
        st.subheader("⚙️ Configurações de Acesso")
        st.write("Deseja alterar sua senha?")
        nova_senha = st.text_input("Nova Senha", type="password")
        if st.button("ATUALIZAR SENHA"):
            cursor.execute("UPDATE usuarios SET senha = ?", (gerar_hash(nova_senha),))
            conn.commit()
            st.success("Senha alterada com sucesso!")
