import streamlit as st
import openai
import os

st.set_page_config(page_title="Chat de BI com GPT", page_icon="🤖")

st.markdown('<link rel="stylesheet" href="style.css">', unsafe_allow_html=True)

st.title("🤖 Chatbot de Indicadores de Negócio")
st.markdown("Faça perguntas sobre os seus dados de BI e receba queries DAX automaticamente.")

pergunta = st.text_input("✍️ Escreve a tua pergunta:", placeholder="Ex: Qual o lucro de 2024 para o produto A?")

if st.button("Gerar Query DAX"):
    if pergunta.strip() == "":
        st.warning("Por favor, escreve uma pergunta primeiro.")
    else:
        with st.spinner("🧠 A gerar query..."):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            prompt = f'''
A tua tarefa é converter perguntas em português para queries DAX que possam ser usadas num modelo tabular.
Responde apenas com o código DAX. A pergunta é:
{pergunta}
'''
            try:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                resposta_dax = response.choices[0].message.content.strip()
                st.success("✅ Query DAX gerada:")
                st.code(resposta_dax, language="dax")
            except Exception as e:
                st.error(f"❌ Ocorreu um erro ao chamar a API: {e}")
