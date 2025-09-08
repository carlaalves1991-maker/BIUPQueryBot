import streamlit as st
import openai
import os
import socket
import datetime

st.set_page_config(page_title="Chat de BI com GPT", page_icon="🤖")

# ==============================
# Config de ligação ao cubo
# ==============================
# Define aqui o IP do servidor do cubo (ou usa variáveis de ambiente)
CUBO_IP = os.getenv("CUBO_IP", "192.168.68.115")   # ← substitui pelo IP que já sabes
CUBO_PORT = int(os.getenv("CUBO_PORT", "2382"))

# ==============================
# Estilos
# ==============================
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🤖 Chatbot de Indicadores de Negócio")
st.markdown("Faça perguntas sobre os seus dados de BI e receba queries DAX automaticamente.")

# ==============================
# Estado / Logs
# ==============================
if "historico" not in st.session_state:
    st.session_state.historico = []

if "logs" not in st.session_state:
    st.session_state.logs = []

def log(msg: str, level: str = "INFO"):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append(f"[{ts}] [{level}] {msg}")

# ==============================
# Teste de ligação ao cubo (TCP)
# ==============================
def testar_ligacao_cubo(ip: str, port: int, timeout: float = 5.0):
    log(f"Tentar ligação ao cubo em {ip}:{port} (timeout {timeout}s)...")
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            log("Ligação TCP estabelecida com sucesso ao cubo.", "SUCCESS")
            return True, None
    except socket.timeout as e:
        err = f"Timeout ao ligar ao {ip}:{port} — verifica firewall/serviço. Detalhe: {e}"
        log(err, "ERROR")
        return False, err
    except ConnectionRefusedError as e:
        err = f"Ligação recusada por {ip}:{port} — o serviço pode não estar a correr. Detalhe: {e}"
        log(err, "ERROR")
        return False, err
    except OSError as e:
        err = f"Erro de SO ao ligar a {ip}:{port}. Detalhe: {e}"
        log(err, "ERROR")
        return False, err
    except Exception as e:
        err = f"Erro inesperado ao ligar a {ip}:{port}. Detalhe: {e}"
        log(err, "ERROR")
        return False, err

# ==============================
# Sidebar: ligação ao cubo
# ==============================
with st.sidebar:
    st.header("🔌 Ligação ao Cubo")
    cubo_ip_input = st.text_input("IP do Cubo", value=CUBO_IP, help="Define o IP do servidor do cubo.")
    cubo_port_input = st.number_input("Porta", value=CUBO_PORT, step=1, help="Porta do serviço (ex.: 2382).")
    if st.button("Testar ligação"):
        ok, err = testar_ligacao_cubo(cubo_ip_input.strip(), int(cubo_port_input))
        if ok:
            st.success(f"Conectado ao cubo em {cubo_ip_input}:{cubo_port_input} ✅")
        else:
            st.error("Falha ao conectar ao cubo. Vê os logs para detalhes.")

    with st.expander("📜 Logs", expanded=True):
        if st.session_state.logs:
            st.code("\n".join(st.session_state.logs), language="text")
        else:
            st.caption("Sem logs ainda. Usa 'Testar ligação' ou gera uma query para ver activity.")

# ==============================
# Input principal
# ==============================
pergunta = st.text_input("✍️ Escreve a tua pergunta:", placeholder="Ex: Qual o lucro de 2024 para o produto A?")

# ==============================
# Botão: Gerar Query DAX
# ==============================
if st.button("Gerar Query DAX"):
    if pergunta.strip() == "":
        st.warning("Por favor, escreve uma pergunta primeiro.")
    else:
        with st.spinner("A gerar query..."):
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                st.error("❌ OPENAI_API_KEY não definido nas variáveis de ambiente.")
                log("OPENAI_API_KEY ausente.", "ERROR")
            else:
                prompt = f"""
A tua tarefa é converter perguntas em português para queries DAX que possam ser usadas num modelo tabular.
Responde apenas com o código DAX. A pergunta é:

{pergunta}
"""
                try:
                    log("Chamada à API OpenAI para gerar DAX...")
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
                    log("Query DAX gerada com sucesso.", "SUCCESS")
                except Exception as e:
                    msg = f"Erro ao chamar a API OpenAI: {e}"
                    st.error(f"❌ {msg}")
                    log(msg, "ERROR")

# ==============================
# Histórico
# ==============================
if st.session_state.historico:
    st.markdown("---")
    st.subheader("🧾 Histórico")
    for idx, (q, a) in enumerate(reversed(st.session_state.historico)):
        st.write(f"**Pergunta {len(st.session_state.historico)-idx}:** {q}")
        st.code(a, language="dax")
