import streamlit as st
import pandas as pd
import mysql.connector
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_types import AgentType
from tools.app_config import conectar_banco_dados
import os

# Carregar segredos do Streamlit
db_host = st.secrets["DB_HOST"]
db_user = st.secrets["DB_USER"]
db_password = st.secrets["DB_PASSWORD"]
db_database = st.secrets["DB_DATABASE"]
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Conectar ao banco de dados
mydb, mycursor = conectar_banco_dados()

# Funções auxiliares
def clear_submit():
    """Limpar o estado do botão de envio"""
    st.session_state["submit"] = False

@st.cache_data(ttl="2h")
def load_data(table_name):
    try:
        query = f"SELECT * FROM {table_name}"
        mycursor.execute(query)
        colunas = [desc[0] for desc in mycursor.description]
        dados = mycursor.fetchall()
        df = pd.DataFrame(dados, columns=colunas)

        # Ajustar os valores conforme necessário
        for coluna in ['preco_custo', 'preco_venda', 'estoque']:
            if coluna in df.columns:
                df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

        return df
    except mysql.connector.Error as err:
        st.error(f"Erro ao carregar dados da tabela {table_name}: {err}")
        return pd.DataFrame()

# Interface do usuário



tabela_selecionada = st.sidebar.radio(
    "Escolha a tabela:",
    ["produtos", "inventario", "anuncio", "ficha_tecnica_do_produto", "vendas"]
)

# Carregar dados com base na tabela selecionada
df = load_data(tabela_selecionada)

if df.empty:
    st.warning("Nenhum dado encontrado na tabela selecionada.")
else:
    st.info("Dados carregados com sucesso.")
    # st.dataframe(df)  # Exibir o DataFrame carregado

    # Limpar histórico de conversas
    if "messages" not in st.session_state or st.sidebar.button("Limpar histórico de conversas"):
        st.session_state["messages"] = [{"role": "assistant", "content": "Como posso ajudar você?"}]

    # Exibir mensagens anteriores
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Entrada do usuário
    if prompt := st.chat_input(placeholder="Sobre o que é este dado?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if not openai_api_key:
            st.info("Por favor, adicione sua chave de API OpenAI para continuar.")
            st.stop()

        # Configuração do modelo OpenAI
        llm = ChatOpenAI(
            temperature=0, model="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True
        )

        # Criar agente do DataFrame
        pandas_df_agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True,
            allow_dangerous_code=True
        )

        # Processar resposta
        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = pandas_df_agent.run(st.session_state.messages, callbacks=[st_cb])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
