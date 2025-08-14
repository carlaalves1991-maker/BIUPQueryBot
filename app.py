import streamlit as st
import openai
import os

st.set_page_config(page_title="Chat de BI com GPT", page_icon="🤖")
st.title("🤖 Chatbot de Indicadores de Negócio")
st.markdown("Faça perguntas sobre os seus dados de BI e receba queries DAX automaticamente.")

# Input da pergunta
pergunta = st.text_input("✍️ Escreve a tua pergunta:", placeholder="Ex: Qual o lucro de 2024 para o produto A?")

# Inicializa histórico na sessão
if "historico" not in st.session_state:
    st.session_state.historico = []

# Processa a pergunta e gera query
if st.button("Gerar Query DAX"):
    if pergunta.strip() == "":
        st.warning("Por favor, escreve uma pergunta primeiro.")
    else:
        with st.spinner("A gerar query..."):
            openai.api_key = os.getenv("OPENAI_API_KEY")

            prompt = f"""
A tua tarefa é converter perguntas em português para queries DAX que possam ser usadas num modelo tabular.
Responde apenas com o código DAX. A pergunta é:
{pergunta}
"""

            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )

                resposta_dax = response.choices[0].message.content.strip()
                st.success("✅ Query DAX gerada:")
                st.code(resposta_dax, language="dax")

                # Adiciona ao histórico
                st.session_state.historico.append((pergunta, resposta_dax))

            except Exception as e:
                st.error(f"❌ Ocorreu um erro ao chamar a API: {e}")

# Exibe histórico
st.markdown("---")
st.subheader("🧾 Histórico")
for i, (q, r) in enumerate(reversed(st.session_state.historico), 1):
    st.write(f"**{i}. Pergunta:** {q}")
    st.code(r, language="dax")
