import os
import streamlit as st
import openai
from streamlit_keycloak import login, logout

# ---- Configuração da página ----
st.set_page_config(page_title="Chat de BI com GPT", page_icon="📊")

# ---- Configurações do Keycloak ----
KEYCLOAK_URL = os.getenv("KC_URL", "http://<IP_DA_VM>:8080/")   # Ex.: http://192.168.1.57:8080/
REALM        = os.getenv("KC_REALM", "biup")
CLIENT_ID    = os.getenv("KC_CLIENT_ID", "bi-chat-app")

# ---- Autenticação ----
token = login(
    server_url=KEYCLOAK_URL,
    realm=REALM,
    client_id=CLIENT_ID,
    auto_refresh=True,
    verify_tls=False   # só usar False se Keycloak estiver sem HTTPS
)

if not token:
    st.stop()  # não mostra mais nada sem login

# ---- Usuário logado ----
username = token.get("preferred_username", "utilizador")
st.sidebar.success(f"Bem-vindo(a), {username} 👋")

# Botão de logout
if st.sidebar.button("Terminar sessão"):
    logout(
        server_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        redirect_uri="https://biupquerybot.streamlit.app/"
    )
    st.stop()

# ---- App principal (só aparece após login) ----
st.title("🤖 Chatbot de Indicadores de Negócio")
st.markdown("Faça perguntas sobre os seus dados de BI e receba queries DAX automaticamente.")

pergunta = st.text_input("✍️ Escreva a sua pergunta:", placeholder="Ex: Qual o lucro total por região?")

if st.button("Gerar Query DAX"):
    if pergunta.strip() == "":
        st.warning("Por favor, escreva uma pergunta primeiro.")
    else:
        with st.spinner("🔄 A gerar query..."):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            prompt = f"""
            A tua tarefa é converter perguntas em português para queries DAX que possam ser usadas no Power BI.
            Responde apenas com o código DAX. 
            Pergunta: {pergunta}
            """

            try:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "És um assistente especializado em DAX."},
                        {"role": "user", "content": prompt}
                    ]
                )
                resposta = response.choices[0].message.content.strip()
                st.code(resposta, language="DAX")
            except Exception as e:
                st.error(f"Erro ao gerar resposta: {e}")
