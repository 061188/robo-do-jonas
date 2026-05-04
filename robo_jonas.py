import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib

# --- CONFIGURAÇÃO DA PÁGINA E LOGO ---
st.set_page_config(page_title="Gestão do Jonas", page_icon="🏗️", layout="centered")

def carregar_logo():
    try:
        st.image("logo_jonas.png", width=150)
    except:
        st.title("🏗️ Gestão: Bar & Obra")

# --- FUNÇÕES DE BANCO DE DADOS ---
conn = sqlite3.connect('gestao_irmao.db', check_same_thread=False)
cursor = conn.cursor()

# Criar tabelas se não existirem
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                  (usuario TEXT PRIMARY KEY, senha TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS financeiro 
                  (data TEXT, negocio TEXT, descricao TEXT, valor REAL, tipo TEXT, categoria TEXT)''')
conn.commit()

def gerar_hash(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

# --- LÓGICA DE ACESSO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

def login():
    carregar_logo()
    st.subheader("Login de Acesso")
    
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

# --- APP PRINCIPAL ---
if not st.session_state['autenticado']:
    login()
else:
    st.sidebar.title("Menu")
    pagina = st.sidebar.selectbox("Ir para:", ["Dashboard", "Configurações"])
    negocio = st.sidebar.radio("Selecione o Negócio:", ["🍺 BAR", "🚧 OBRA"])
    
    if st.sidebar.button("Sair"):
        st.session_state['autenticado'] = False
        st.rerun()

    if pagina == "Dashboard":
        carregar_logo()
        st.subheader(f"📊 Resumo Financeiro - {negocio}")
        
        df_total = pd.read_sql_query(f"SELECT * FROM financeiro WHERE negocio='{negocio}'", conn)

        if not df_total.empty:
            ganhos = df_total[df_total['tipo'].str.contains("Ganho")]['valor'].sum()
            gastos = df_total[df_total['tipo'].str.contains("Gasto")]['valor'].sum()
            saldo = ganhos - gastos
            col1, col2, col3 = st.columns(3)
            col1.metric("Ganhos", f"R$ {ganhos:.2f}")
            col2.metric("Gastos", f"R$ {gastos:.2f}")
            col3.metric("Saldo", f"R$ {saldo:.2f}")

        st.divider()
        st.write(f"📝 Novo Lançamento: {negocio}")
        with st.form("formulario", clear_on_submit=True):
            data = st.date_input("Data", datetime.now())
            desc = st.text_input("O que aconteceu?")
            val = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
            cat = st.selectbox("Categoria", ["Material", "Contas", "Vendas", "Ajudante", "Valor Obra"])
            tp = st.radio("Tipo:", ["Ganho (Entrada 🟢)", "Gasto (Saída 🔴)"])
            if st.form_submit_button("SALVAR"):
                cursor.execute("INSERT INTO financeiro VALUES (?,?,?,?,?,?)", (str(data), negocio, desc, val, tp, cat))
                conn.commit()
                st.rerun()

    elif pagina == "Configurações":
        st.subheader("⚙️ Configurações de Acesso")
        nova_s = st.text_input("Nova Senha", type="password")
        if st.button("ATUALIZAR SENHA"):
            cursor.execute("UPDATE usuarios SET senha = ?", (gerar_hash(nova_s),))
            conn.commit()
            st.success("Senha alterada!")
