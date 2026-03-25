import streamlit as st

from main import executar_consulta, verificar_ollama, OLLAMA_HOST, OLLAMA_MODEL


st.set_page_config(
    page_title="Assistente Medico XAI",
    page_icon="+",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(25, 118, 210, 0.12), transparent 28%),
            radial-gradient(circle at top right, rgba(0, 150, 136, 0.12), transparent 24%),
            linear-gradient(180deg, #f5f9fc 0%, #eef5f7 100%);
    }

    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 22px;
        background: linear-gradient(135deg, #073b4c 0%, #0b6e6e 100%);
        color: #ffffff;
        box-shadow: 0 18px 40px rgba(7, 59, 76, 0.18);
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0 0 0.4rem 0;
        font-size: 2.1rem;
        font-weight: 800;
    }

    .hero p {
        margin: 0;
        font-size: 1rem;
        opacity: 0.92;
    }

    .status-card {
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(7, 59, 76, 0.08);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 0.8rem;
    }

    .status-label {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.7rem;
    }

    .status-ok {
        background: rgba(30, 136, 90, 0.14);
        color: #1e6f47;
    }

    .status-error {
        background: rgba(211, 47, 47, 0.12);
        color: #a12626;
    }

    .panel-title {
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        color: #0f172a;
    }

    .panel-text {
        font-size: 0.95rem;
        color: #334155;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_status_card(ok: bool, mensagem: str | None):
    label_class = "status-ok" if ok else "status-error"
    label_text = "Ollama conectado" if ok else "Ollama indisponivel"
    detalhe = mensagem or "Servico pronto para consultas."

    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-label {label_class}">{label_text}</div>
            <div class="panel-title">Ambiente local</div>
            <p class="panel-text"><strong>Host:</strong> {OLLAMA_HOST}</p>
            <p class="panel-text"><strong>Modelo:</strong> {OLLAMA_MODEL}</p>
            <p class="panel-text" style="margin-top:0.7rem;">{detalhe}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if "resultado_consulta" not in st.session_state:
    st.session_state.resultado_consulta = None

if "erro_consulta" not in st.session_state:
    st.session_state.erro_consulta = None

ollama_ok, ollama_msg = verificar_ollama()

st.markdown(
    """
    <div class="hero">
        <h1>Assistente Medico com XAI e Auditoria</h1>
        <p>Preencha o perfil do paciente, descreva os sintomas e gere o parecer consolidado em uma tela simples.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_form, col_status = st.columns([1.5, 1])

with col_form:
    with st.form("consulta_form"):
        st.subheader("Nova consulta")
        perfil = st.text_input(
            "Perfil do paciente",
            placeholder="Ex.: Adulto, 35 anos, sem comorbidades relatadas",
        )
        sintomas = st.text_area(
            "Sintomas observados",
            placeholder="Ex.: febre ha 3 dias, tosse seca, dor no corpo e fadiga",
            height=180,
        )
        submitted = st.form_submit_button(
            "Gerar parecer tecnico",
            type="primary",
            use_container_width=True,
        )

with col_status:
    render_status_card(ollama_ok, ollama_msg)
    st.markdown(
        """
        <div class="status-card">
            <div class="panel-title">Fluxo da analise</div>
            <p class="panel-text">IA local -> Wikipedia -> DuckDuckGo -> Relatorio final</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if submitted:
    try:
        with st.spinner("Executando a analise clinica..."):
            st.session_state.resultado_consulta = executar_consulta(perfil, sintomas)
            st.session_state.erro_consulta = None
    except Exception as exc:
        st.session_state.resultado_consulta = None
        st.session_state.erro_consulta = str(exc)

if st.session_state.erro_consulta:
    st.error(st.session_state.erro_consulta)

if not ollama_ok:
    st.warning(
        "Para executar a consulta, inicie o Ollama local e garanta que o modelo configurado esteja disponivel."
    )

resultado = st.session_state.resultado_consulta

if resultado:
    st.divider()
    info_col, resumo_col = st.columns([1, 2])

    with info_col:
        st.markdown("### Resumo da consulta")
        st.write(f"**Perfil:** {resultado['perfil']}")
        st.write(f"**Sintomas:** {resultado['sintomas']}")
        st.write(f"**Modelo local:** {resultado['ollama_model']}")
        st.write(f"**Host Ollama:** {resultado['ollama_host']}")
        st.caption(f"AVISO: {resultado['aviso_legal']}")

    with resumo_col:
        st.markdown("### Parecer tecnico sugerido")
        st.markdown(resultado["parecer_final"])

    with st.expander("Rastreabilidade das fontes"):
        st.markdown("**Analise inicial da IA local**")
        st.write(resultado["analise_ollama"] or "Sem retorno.")
        st.markdown("**Base Wikipedia**")
        st.write(resultado["dados_wiki"] or "Sem retorno.")
        st.markdown("**Busca web**")
        st.write(resultado["dados_web"] or "Sem retorno.")
else:
    st.info("Preencha os campos e clique em `Gerar parecer tecnico` para executar o fluxo.")

st.caption("Para abrir esta interface: `streamlit run src/app.py`")
