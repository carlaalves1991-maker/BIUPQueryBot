
import streamlit as st
import openai
import os

st.set_page_config(page_title="Chat de BI com GPT", page_icon="🤖")

# Aplica o estilo customizado
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🤖 Chatbot de Indicadores de Negócio")
st.markdown("Faça perguntas sobre os seus dados de BI e receba queries DAX automaticamente.")

# Inicializa histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

pergunta = st.text_input("✍️ Escreve a tua pergunta:", placeholder="Ex: Qual o lucro de 2024 para o produto A?")

if st.button("Gerar Query DAX"):
    if pergunta.strip() == "":
        st.warning("Por favor, escreve uma pergunta primeiro.")
    else:
        with st.spinner("A gerar query..."):
            openai_api_key = os.getenv("OPENAI_API_KEY")

            prompt = f"""
A tua tarefa é converter perguntas em português para queries DAX que possam ser usadas num modelo tabular.
Responde apenas com o código DAX. A pergunta é:

{pergunta}
"""

            try:
                client = openai.OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                )
                resposta_dax = response.choices[0].message.content.strip()
                st.success("✅ Query DAX gerada:")
                st.code(resposta_dax, language="dax")
                st.session_state.historico.append((pergunta, resposta_dax))
            except Exception as e:
                st.error(f"❌ Ocorreu um erro ao chamar a API: {e}")

if st.session_state.historico:
    st.markdown("---")
    st.subheader("🧾 Histórico")
    for idx, (q, a) in enumerate(reversed(st.session_state.historico)):
        st.write(f"**Pergunta {len(st.session_state.historico)-idx}:** {q}")
        st.code(a, language="dax")
