import streamlit as st
import os
import openai

st.set_page_config(page_title="Chat de BI com GPT", page_icon="🤖")
st.title("🤖 Chatbot de Indicadores de Negócio")
st.markdown("Faça perguntas sobre os seus dados de BI e receba queries DAX automaticamente.")

pergunta = st.text_input("✍️ Escreve a tua pergunta:", placeholder="Ex: Qual o Lucro de 2024 para o produto A?")

if st.button("Gerar Query DAX"):
    if pergunta.strip() == "":
        st.warning("Por favor, escreve uma pergunta primeiro.")
    else:
        with st.spinner("A gerar query..."):
            try:
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if not openai_api_key:
                    st.error("🔑 A chave da API não está configurada.")
                else:
                    client = openai.OpenAI(api_key=openai_api_key)
                    st.info("🔌 Ligação com API criada com sucesso.")
                    prompt = f"""
                    A tua tarefa é converter perguntas em português para queries DAX que possam ser usadas num modelo tabular.
                    Responde apenas com o código DAX. A pergunta é:

                    {pergunta}
                    """

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0,
                    )
                    resposta_dax = response.choices[0].message.content.strip()
                    st.success("✅ Query DAX gerada com sucesso!")
                    st.code(resposta_dax, language="dax")
            except Exception as e:
                st.error(f"❌ Ocorreu um erro ao chamar a API: {e}")

st.markdown("---")
st.subheader("🧾 Histórico (simulado)")
st.write("Pergunta: Qual o lucro de 2024 para o produto A?")
st.code("CALCULATE(SUM('Fato Vendas'[Lucro]), 'Dim Data'[Ano] = 2024, 'Dim Produto'[Produto] = \"A\")", language="dax")