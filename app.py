
import streamlit as st
import openai
import os

st.set_page_config(page_title="Chat de BI com GPT", page_icon="🤖")

if "historico" not in st.session_state:
    st.session_state.historico = []

st.title("🤖 Chatbot de Indicadores de Negócio")
st.markdown("Faça perguntas sobre os seus dados de BI e receba queries DAX automaticamente.")

pergunta = st.text_input("✍️ Escreve a tua pergunta:", placeholder="Ex: Qual o lucro de 2024 para o produto A?")

if st.button("Gerar Query DAX"):
    if pergunta.strip() == "":
        st.warning("Por favor, escreve uma pergunta primeiro.")
    else:
        with st.spinner("🧠 A gerar query..."):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            prompt = f"""
A tua tarefa é converter perguntas em português para queries DAX que possam ser usadas num modelo tabular.

Responde apenas com o código DAX. A pergunta é:
{pergunta}
"""
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                resposta_dax = response.choices[0].message.content.strip()
                st.success("✅ Query DAX gerada:")
                st.code(resposta_dax, language="dax")

                st.session_state.historico.append((pergunta, resposta_dax))
            except Exception as e:
                st.error(f"❌ Ocorreu um erro ao chamar a API: {e}")

st.markdown("---")
st.subheader("🧾 Histórico de Perguntas")

if st.session_state.historico:
    for idx, (pergunta_hist, resposta_hist) in enumerate(reversed(st.session_state.historico), 1):
        st.write(f"**Pergunta {idx}:** {pergunta_hist}")
        st.code(resposta_hist, language="dax")
else:
    st.write("Ainda não há perguntas feitas.")
