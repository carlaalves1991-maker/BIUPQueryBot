import os
import streamlit as st
import openai
from urllib.parse import quote

# Tentar importar o Keycloak
try:
    from streamlit_keycloak import login
except ModuleNotFoundError:
    st.error("Falta instalar 'streamlit-keycloak'. Confirma o requirements.txt e faz Restart em Manage app.")
    st.stop()

# ---- Configuração da página ----
st.set_page_config(page_title="Chat de BI com GPT", page_icon="📊")

# ---- Configurações do Keycloak ----
KEYCLOAK_URL = os.getenv("KC_URL", "http://<IP_DA_VM>:8080/")   # Exemplo: http://192.168.1.57:8080/
REALM        = os.getenv("KC_REALM", "biup")
CLIENT_ID    = os.getenv("KC_CLIENT_ID", "bi-chat-app")

# ---- Autenticação ----
token = login(
    server_url=KEYCLOAK_URL,
    realm=REALM,
    client_id=CLIENT_ID,
    auto_refresh=True,
    verify_tls=False   # só usar False se o Keycloak não tiver HTTPS
)

if not token:
    st.stop()  # não mostra mais nada sem login

# ---- Usuário logado ----
username = token.get("preferred_username", "utilizador")
st.sidebar.success(f"Bem-vindo(a), {username} 👋")

# ---- Botão de Logout ----
LOGOUT_REDIRECT = "https://biupquerybot.streamlit.app/"  # já deve estar em Post-logout redirect URIs
base = KEYCLOAK_URL.rstrip("/")
logout_url = (
    f"{base}/realms/{REALM}/protocol/openid-connect/logout"
    f"?client_id={CLIENT_ID}"
    f"&post_logout_redirect_uri={quote(LOGOUT_REDIRECT, safe='')}"
)

if st.sidebar.button("Terminar sessão"):
    st.markdown(f'<meta http-equiv="refresh" content="0; url={logout_url}">', unsafe_allow_html=True)
    st.stop()

# ---- App principal (Chatbot BI/DAX) ----
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
