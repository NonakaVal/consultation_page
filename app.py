import streamlit as st
import mysql.connector
from tools.app_config import login, logout


# Configuração da página do Streamlit
st.set_page_config(page_title="consultation_page-collectorsguardian", page_icon="📦")

# Inicializar a sessão ,layout= "wide" 
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# Navegação de páginas
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")


# chat = st.Page("consultas/Chat.py", title="Agente AI", icon=":material/bug_report:")
home = st.Page("pages/home.py", title="Home", icon=":material/home:", default=True)
consulta = st.Page("pages/search_product.py", title="Buscar", icon=":material/search:")
product_table = st.Page("pages/table_products.py", title="Tabela de produtos", icon=":material/dashboard:")
chat = st.Page("pages/chat.py", title="AI Chat", icon=":material/chat:")
inventario = st.Page("pages/inventario_itens_de_envio.py", title="Inventario", icon=":material/history:")
historico = st.Page("pages/historico.py", title="Historico de Atividades", icon=":material/history:")

# Estabeleça uma conexão com o servidor MySQL usando os secrets do Streamlit
try:
    mydb = mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password= st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_DATABASE"]
    )
    mycursor = mydb.cursor()
    # st.info("Conexão Estabelecida")
except mysql.connector.Error as err:
    st.error(f"Erro ao conectar ao banco de dados: {err}")



# Configuração das páginas
if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Account":  [logout_page, home],
            "Produtos": [product_table, consulta,  chat],
            "Controle": [inventario, historico], 
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()