import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO ---
EMAIL_DONO = "Jonassssantana41@gmail.com" 

st.set_page_config(page_title="Gestão do Jonas", layout="centered")
st.title("🏗️ Gestão: Bar & Obra")

conn = sqlite3.connect('gestao_irmao.db', check_same_thread=False)

# Escolha do negócio
negocio = st.sidebar.radio("Selecione o Negócio:", ["🍺 BAR", "🚧 OBRA"])

# --- PAINEL FINANCEIRO ---
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
        st.success(f"Salvo com sucesso!")
        st.rerun()

# --- ABA DE EDIÇÃO E EXCLUSÃO ---
st.divider()
st.subheader("🗑️ Editar ou Excluir Lançamentos")

if not df_total.empty:
    # Criamos uma lista de descrições para a pessoa escolher qual quer apagar
    opcoes = df_total['descricao'].tolist()
    item_para_excluir = st.selectbox("Selecione o lançamento para excluir:", ["Selecione..."] + opcoes)

    if st.button("EXCLUIR LANÇAMENTO SELECIONADO"):
        if item_para_excluir != "Selecione...":
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM financeiro WHERE descricao = '{item_para_excluir}' AND negocio = '{negocio}'")
            conn.commit()
            st.warning(f"Lançamento '{item_para_excluir}' foi apagado!")
            st.rerun()
        else:
            st.info("Por favor, selecione um item na lista acima.")

# Tabela de histórico
if st.checkbox("Ver tabela completa"):
    st.dataframe(df_total)
