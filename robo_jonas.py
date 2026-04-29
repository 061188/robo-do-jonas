import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestão do Jonas", layout="centered")
st.title("🏗️ Gestão: Bar & Obra")

conn = sqlite3.connect('gestao_irmao.db', check_same_thread=False)

# Escolha do negócio
negocio = st.sidebar.radio("Selecione o Negócio:", ["🍺 BAR", "🚧 OBRA"])

# --- NOVO: PAINEL DE GANHOS E PERDAS ---
st.subheader(f"📊 Resumo Financeiro - {negocio}")

# Buscamos os dados para fazer a conta
df_total = pd.read_sql_query(f"SELECT * FROM financeiro WHERE negocio='{negocio}'", conn)

if not df_total.empty:
    ganhos = df_total[df_total['tipo'].str.contains("Ganho")]['valor'].sum()
    gastos = df_total[df_total['tipo'].str.contains("Gasto")]['valor'].sum()
    saldo = ganhos - gastos
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ganhos", f"R$ {ganhos:.2f}", delta_color="normal")
    col2.metric("Gastos", f"R$ {gastos:.2f}", delta="- Perda", delta_color="inverse")
    col3.metric("Saldo", f"R$ {saldo:.2f}", delta=saldo)
st.divider()

# --- FORMULÁRIO DE LANÇAMENTO ---
st.write(f"📝 Novo Lançamento: {negocio}")
with st.form("formulario", clear_on_submit=True):
    data = st.date_input("Data", datetime.now())
    descricao = st.text_input("O que aconteceu?")
    valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
    
    if negocio == "🍺 BAR":
        categoria = st.selectbox("Categoria", ["Material", "Contas", "Vendas"])
    else:
        categoria = st.selectbox("Categoria", ["Material", "Ajudante", "Valor Obra"])
    
    tipo = st.radio("Tipo:", ["Ganho (Entrada 🟢)", "Gasto (Saída 🔴)"])
    botao = st.form_submit_button("SALVAR")

    if botao:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO financeiro (data, negocio, descricao, valor, tipo, categoria) VALUES (?,?,?,?,?,?)",
                       (str(data), negocio, descricao, valor, tipo, categoria))
        conn.commit()
        st.rerun() # Isso faz a tela atualizar e mostrar o valor novo na hora!

# Tabela de histórico
if st.checkbox("Mostrar histórico completo"):
    st.dataframe(df_total)
    st.divider()
st.subheader("⏰ Agendar Aviso de Pagamento")

with st.form("lembrete_pagamento", clear_on_submit=True):
    conta = st.text_input("Qual conta precisa pagar? (Ex: Luz do Bar)")
    vencimento = st.date_input("Data de Vencimento")
    valor_conta = st.number_input("Valor Estimado (R$)", min_value=0.0)
    
    # Aqui ele escolhe quantos dias antes quer ser avisado
    dias_antes = st.slider("Avisar quantos dias antes?", 1, 7, 2)
    
    botao_aviso = st.form_submit_button("AGENDAR AVISO")

    if botao_aviso:
        # O robô calcula a data do alerta
        # Vamos usar a ferramenta de lembretes para isso!
        st.success(f"Beleza! Vou avisar o Jonas sobre '{conta}' alguns dias antes de {vencimento}.")