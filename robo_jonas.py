import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib

# --- 1. CONFIGURAÇÃO DA CARA DO APP ---
st.set_page_config(page_title="Gestão do Jonas", page_icon="🏗️", layout="centered")

def mostrar_logo():
    try:
        # Aqui ele procura a imagem que você acabou de renomear!
        st.image("logo_jonas.png", width=150)
    except:
        st.title("🏗️ Gestão: Bar & Obra")

# --- 2. CONECTAR NO CADERNINHO (BANCO DE DADOS) ---
conn = sqlite3.connect('gestao_irmao.db', check_same_thread=False)
cursor = conn.cursor()

# Criando as tabelas (pastas) dentro do banco se elas não existirem
cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, senha TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS financeiro (data TEXT, negocio TEXT, descricao TEXT, valor REAL, tipo TEXT, categoria TEXT)')
conn.commit()

# Função para transformar a senha em um código secreto (Segurança)
def transformar_em_codigo(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

# --- 3. SISTEMA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

def tela_login():
    mostrar_logo()
    st.subheader("🔑 Acesso Restrito")
    
    # Verifica se já tem alguém cadastrado
    check_user = pd.read_sql_query("SELECT * FROM usuarios", conn)
    
    if check_user.empty:
        st.info("Primeiro acesso! Defina quem vai mandar aqui:")
        novo_u = st.text_input("Escolha um nome de usuário")
        nova_s = st.text_input("Escolha uma senha", type="password")
        if st.button("CRIAR MEU ACESSO"):
            cursor.execute("INSERT INTO usuarios VALUES (?, ?)", (novo_u, transformar_em_codigo(nova_s)))
            conn.commit()
            st.success("Acesso criado com sucesso! Agora é só entrar.")
            st.rerun()
    else:
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            senha_secreta = transformar_em_codigo(s)
            busca = cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, senha_secreta)).fetchone()
            if busca:
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("Usuário ou senha errados!")

# --- 4. O QUE APARECE DEPOIS DO LOGIN ---
if not st.session_state['logado']:
    tela_login()
else:
    # Se chegou aqui, é porque logou!
    st.sidebar.title(f"Bem-vindo!")
    opcao = st.sidebar.radio("O que quer fazer?", ["Lançamentos", "Configurar Senha"])
    negocio = st.sidebar.selectbox("Escolha o Negócio", ["🍺 BAR", "🚧 OBRA"])
    
    if st.sidebar.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

    if opcao == "Lançamentos":
        mostrar_logo()
        st.subheader(f"📊 Painel {negocio}")
        
        # Aqui entra aquela parte de mostrar a tabela e o formulário que já conhecemos
        df = pd.read_sql_query(f"SELECT * FROM financeiro WHERE negocio='{negocio}'", conn)
        
        # Mostra o Saldo
        if not df.empty:
            ganhos = df[df['tipo'].str.contains("Ganho")]['valor'].sum()
            gastos = df[df['tipo'].str.contains("Gasto")]['valor'].sum()
            st.metric("Saldo Atual", f"R$ {ganhos - gastos:.2f}")

        # Formulário para salvar novo gasto/ganho
        with st.form("meu_form", clear_on_submit=True):
            d = st.date_input("Data", datetime.now())
            desc = st.text_input("Descrição")
            v = st.number_input("Valor (R$)", min_value=0.0)
            t = st.radio("Tipo", ["Ganho (Entrada 🟢)", "Gasto (Saída 🔴)"])
            if st.form_submit_button("SALVAR NOVO"):
                cursor.execute("INSERT INTO financeiro (data, negocio, descricao, valor, tipo) VALUES (?,?,?,?,?)", 
                               (str(d), negocio, desc, v, t))
                conn.commit()
                st.success("Salvo!")
                st.rerun()

    elif opcao == "Configurar Senha":
        st.subheader("⚙️ Alterar Senha")
        nova_s = st.text_input("Digite a nova senha", type="password")
        if st.button("SALVAR NOVA SENHA"):
            cursor.execute("UPDATE usuarios SET senha = ?", (transformar_em_codigo(nova_s),))
            conn.commit()
            st.success("Senha atualizada!")
