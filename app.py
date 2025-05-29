import streamlit as st
import mysql.connector
from datetime import date

# Função para criar conexão com o banco MySQL
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="gestao_manutencao"
    )

# Tela principal com menu lateral para navegar entre funcionalidades
def tela_inicial():
    st.title("Sistema de Gestão de Manutenção")

    menu = ["Cadastrar Manutenção", "Listar Equipamentos", "Listar Técnicos", "Listar Manutenções"]
    escolha = st.sidebar.selectbox("Menu", menu)

    # Chama a função correspondente à escolha do menu
    if escolha == "Cadastrar Manutenção":
        cadastrar_manutencao()
    elif escolha == "Listar Equipamentos":
        listar_equipamentos()
    elif escolha == "Listar Técnicos":
        listar_tecnicos()
    elif escolha == "Listar Manutenções":
        listar_manutencoes()

# Formulário para cadastrar nova manutenção
def cadastrar_manutencao():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Busca equipamentos e técnicos para popular os dropdowns
    cursor.execute("SELECT id_equipamento, nome FROM equipamento")
    equipamentos = cursor.fetchall()

    cursor.execute("SELECT id_tecnico, nome FROM tecnico")
    tecnicos = cursor.fetchall()

    st.header("Cadastrar Nova Manutenção")

    # Campos do formulário para cadastrar manutenção
    equipamento = st.selectbox("Equipamento", options=equipamentos, format_func=lambda x: x['nome'])
    tecnico = st.selectbox("Técnico", options=tecnicos, format_func=lambda x: x['nome'])
    tipo = st.radio("Tipo de Manutenção", options=["Preventiva", "Corretiva"])
    data_inicio = st.date_input("Data de Início", date.today())
    data_fim = st.date_input("Data de Fim", date.today())
    descricao = st.text_area("Descrição")
    status = st.selectbox("Status", ["Pendente", "Concluída", "Atrasada"])

    # Quando o botão salvar for clicado, insere no banco
    if st.button("Salvar"):
        sql = """
        INSERT INTO manutencao (id_equipamento, id_tecnico, tipo, descricao, data_inicio, data_fim, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (equipamento['id_equipamento'], tecnico['id_tecnico'], tipo, descricao, data_inicio, data_fim, status)
        cursor.execute(sql, valores)
        conn.commit()
        st.success("Manutenção cadastrada com sucesso!")

    cursor.close()
    conn.close()

# Tela para listar todos os equipamentos
def listar_equipamentos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM equipamento")
    dados = cursor.fetchall()

    st.header("Equipamentos")

    if dados:
        import pandas as pd
        df = pd.DataFrame(dados)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum equipamento cadastrado.")

    cursor.close()
    conn.close()


# Tela para listar técnicos, com filtro opcional por especialidade
def listar_tecnicos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Busca especialidades
    cursor.execute("SELECT DISTINCT especialidade FROM tecnico")
    especialidades = [row['especialidade'] for row in cursor.fetchall()]
    especialidade_sel = st.selectbox("Filtrar por Especialidade", options=["Todas"] + especialidades)

    # Filtra técnicos por especialidade
    if especialidade_sel == "Todas":
        cursor.execute("SELECT * FROM tecnico")
    else:
        cursor.execute("SELECT * FROM tecnico WHERE especialidade = %s", (especialidade_sel,))
    tecnicos = cursor.fetchall()

    st.header("Técnicos")

    if tecnicos:
        import pandas as pd
        df = pd.DataFrame(tecnicos)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum técnico encontrado.")

    cursor.close()
    conn.close()

# Tela para listar manutenções com filtros por técnico, equipamento e período
def listar_manutencoes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Busca técnicos para filtro
    cursor.execute("SELECT id_tecnico, nome FROM tecnico")
    tecnicos = cursor.fetchall()
    tecnico_sel = st.selectbox("Selecionar Técnico (opcional)", options=[None] + tecnicos, format_func=lambda x: x['nome'] if x else "Todos")

    # Busca equipamentos para filtro
    cursor.execute("SELECT id_equipamento, nome FROM equipamento")
    equipamentos = cursor.fetchall()
    equipamento_sel = st.selectbox("Selecionar Equipamento (opcional)", options=[None] + equipamentos, format_func=lambda x: x['nome'] if x else "Todos")

    # Filtros de data
    data_inicio = st.date_input("Data Início", value=date(2000, 1, 1))
    data_fim = st.date_input("Data Fim", value=date.today())

    # Consulta base para listar manutenções
    query = """
        SELECT m.*, t.nome as tecnico_nome, e.nome as equipamento_nome
        FROM manutencao m
        JOIN tecnico t ON m.id_tecnico = t.id_tecnico
        JOIN equipamento e ON m.id_equipamento = e.id_equipamento
        WHERE m.data_inicio >= %s AND m.data_fim <= %s
    """
    params = [data_inicio, data_fim]

    # Adiciona filtro por técnico se selecionado
    if tecnico_sel:
        query += " AND m.id_tecnico = %s"
        params.append(tecnico_sel['id_tecnico'])
    # Adiciona filtro por equipamento se selecionado
    if equipamento_sel:
        query += " AND m.id_equipamento = %s"
        params.append(equipamento_sel['id_equipamento'])

    cursor.execute(query, params)
    manutencoes = cursor.fetchall()

    st.header("Manutenções")
    st.write(manutencoes)  # Exibe as manutenções filtradas

    cursor.close()
    conn.close()

if __name__ == "__main__":
    tela_inicial()
