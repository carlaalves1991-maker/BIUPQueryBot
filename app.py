
import streamlit as st

st.set_page_config(page_title="Chat de BI com GPT", page_icon="🤖")

st.title("🤖 Chatbot de Indicadores de Negócio")
st.markdown("Faça perguntas sobre os seus dados de BI e receba queries DAX automaticamente.")

pergunta = st.text_input("✍️ Escreve a tua pergunta:", placeholder="Ex: Qual o lucro de 2024 para o produto A?")

if st.button("Gerar Query DAX"):
    if pergunta.strip() == "":
        st.warning("Por favor, escreve uma pergunta primeiro.")
    else:
        with st.spinner("A gerar query..."):
            resposta_simulada = f"""
            CALCULATE(
                SUM('Fato Vendas'[Lucro]),
                'Dim Data'[Ano] = 2024,
                'Dim Produto'[Produto] = "A"
            )
            """
            st.success("Query DAX gerada:")
            st.code(resposta_simulada, language="dax")

st.markdown("---")
st.subheader("🧾 Histórico (simulado)")
st.write("Pergunta: Qual o lucro de 2024 para o produto A?")
st.code("CALCULATE(SUM('Fato Vendas'[Lucro]), 'Dim Data'[Ano] = 2024, 'Dim Produto'[Produto] = \"A\")", language="dax")
