import streamlit as st
import mysql.connector
from tools.load_from_db import conectar_banco_dados, obter_nome_e_imagem_produto, obter_nome_e_preco_produto, obter_nome_e_quantidade_produto
from tools.insert_to_bd import registrar_historico

# Conectar ao banco de dados
mydb, mycursor = conectar_banco_dados()
if mydb and mycursor:
    # Realize suas operações com mydb e mycursor aqui
    pass
def atualizar_anunciado():
    # Formulário para atualizar o campo "Anunciado"
    st.subheader("Atualizar Status Anúncio de Produto")
    
    with st.form("update_anunciado_form"):
        # Solicitar o ID do produto
        id_produto = st.text_input("ID do Produto")
        
        # Solicitar o novo valor para o campo "Anunciado"
        novo_anunciado = st.radio("Anunciado", [True, False])
        
        submit_button = st.form_submit_button("Atualizar Anunciado")
        
        if submit_button:
            if not id_produto:
                st.error("O ID do produto é obrigatório.")
            else:
                try:
                    # Verificar se o produto existe
                    mycursor.execute(
                        "SELECT COUNT(*) FROM produtos WHERE id_produto = %s",
                        (id_produto,)
                    )
                    count = mycursor.fetchone()[0]
                    
                    if count == 0:
                        st.error("Produto não encontrado.")
                    else:
                        # Atualizar o campo "Anunciado"
                        sql_update = """
                            UPDATE produtos
                            SET anunciado = %s
                            WHERE id_produto = %s
                        """
                        mycursor.execute(sql_update, (novo_anunciado, id_produto))
                        mydb.commit()
                        
                        st.success("O status 'Anunciado' do produto foi atualizado com sucesso!")
                        
                        # Registrar no histórico
                        detalhes = f"Produto com ID '{id_produto}' teve o status 'Anunciado' atualizado para {novo_anunciado}."
                        registrar_historico("Atualização", "produtos", detalhes)

                except mysql.connector.Error as err:
                    st.error(f"Erro ao atualizar o status 'Anunciado': {err}")



def atualizar_quantidade():
    with st.form("update_quantity_form"):
        id_produto = st.text_input("ID do Produto")
        nova_quantidade = st.number_input("Nova Quantidade", min_value=0)

        submit_button = st.form_submit_button("Atualizar Quantidade")
        
        if submit_button:
            if not id_produto:
                st.error("ID do produto é obrigatório.")
            elif nova_quantidade < 0:
                st.error("A quantidade deve ser um valor válido e não negativa.")
            else:
                nome_produto, qtd_estoque = obter_nome_e_quantidade_produto(id_produto)
                if nome_produto:
                    sql = "UPDATE produtos SET estoque = %s WHERE id_produto = %s"
                    mycursor.execute(sql, (nova_quantidade, id_produto))
                    mydb.commit()
                    detalhes = f"Quantidade do produto com ID {id_produto} atualizada de {qtd_estoque} para {nova_quantidade}"
                    registrar_historico("Atualização", "produtos", detalhes)
                    st.success("Quantidade Atualizada com Sucesso!")
                else:
                    st.error("ID do produto não encontrado. Atualização não realizada.")

# Função para atualizar o preço
def atualizar_preco():
    with st.form("update_price_form"):
        id_produto = st.text_input("ID do Produto")
        novo_preco = st.number_input("Novo Preço", min_value=0.0, format="%.2f")

        submit_button = st.form_submit_button("Atualizar Preço")
        
        if submit_button:
            if not id_produto:
                st.error("ID do produto é obrigatório.")
            elif novo_preco < 0:
                st.error("O preço deve ser um valor válido e não negativo.")
            else:
                nome_produto, preco_atual = obter_nome_e_preco_produto(id_produto)
                if nome_produto:
                    sql = "UPDATE produtos SET preco_venda = %s WHERE id_produto = %s"
                    mycursor.execute(sql, (novo_preco, id_produto))
                    mydb.commit()
                    detalhes = f"Preço do produto com ID {id_produto} atualizado de R$ {preco_atual:.2f} para R$ {novo_preco:.2f}"
                    registrar_historico("Atualização", "produtos", detalhes)
                    st.success("Preço Atualizado com Sucesso!")
                else:
                    st.error("ID do produto não encontrado. Atualização não realizada.")

# Função para atualizar a imagem
def atualizar_imagem():
    with st.form("update_image_form"):
        id_produto = st.text_input("ID do Produto")
        nova_imagem = st.text_input("Nova URL da Imagem")

        submit_button = st.form_submit_button("Atualizar Imagem")
        
        if submit_button:
            if not id_produto:
                st.error("ID do produto é obrigatório.")
            elif not nova_imagem:
                st.error("A URL da imagem não pode estar vazia.")
            else:
                nome_produto, imagem_atual = obter_nome_e_imagem_produto(id_produto)
                if nome_produto:
                    sql = "UPDATE produtos SET imagem = %s WHERE id_produto = %s"
                    mycursor.execute(sql, (nova_imagem, id_produto))
                    mydb.commit()
                    detalhes = f"Imagem do produto com ID {id_produto} atualizada de {imagem_atual} para {nova_imagem}"
                    registrar_historico("Atualização", "produtos", detalhes)
                    st.success("Imagem Atualizada com Sucesso!")
                else:
                    st.error("ID do produto não encontrado. Atualização não realizada.")

