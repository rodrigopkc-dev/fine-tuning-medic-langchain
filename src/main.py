
# instalar
# Python versao 312

# 1. Criar o ambiente virtual
# & "C:\Users\rodrigo\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv

# 2. Ativar o ambiente (Windows PowerShell)
# .\.venv\Scripts\activate

# pip list
# pip list | findstr "lang"

# pip install -r requirements.txt

import os
import gc
import logging
from typing import TypedDict

from ollama import Client
from langgraph.graph import StateGraph, END

# Componentes do LangChain
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# --- 1. CONFIGURAÇÃO DE LOGGING (AUDITORIA E RASTREAMENTO) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rastreamento_clinico.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_evento(node, mensagem, level="info"):
    """Registra eventos com o nome do nó no corpo da mensagem para evitar conflitos de formatação."""
    msg_formatada = f"[{node}] {mensagem}"
    if level == "error": 
        logger.error(msg_formatada)
    else: 
        logger.info(msg_formatada)

# --- 2. CONFIGURAÇÃO GLOBAL E ESTADO ---
AVISO_LEGAL = "ESTE RELATORIO E UMA MINUTA DE APOIO E NAO SUBSTITUI A PRESCRICAO E VALIDACAO HUMANA."
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-7b-local")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

class MedicalState(TypedDict):
    perfil: str
    sintomas: str
    analise_ollama: str
    dados_wiki: str
    dados_web: str
    parecer_final: str

# Inicialização das ferramentas
# Temperatura 0.0 para garantir previsibilidade médica
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_HOST,
    temperature=0.0,
    num_predict=500,
)
search_online = DuckDuckGoSearchRun()
wiki_api = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1500)
search_wiki = WikipediaQueryRun(api_wrapper=wiki_api)


def verificar_ollama():
    """Valida se o servidor Ollama esta ativo e se o modelo esperado existe."""
    try:
        client = Client(host=OLLAMA_HOST)
        response = client.list()
        models = []

        for item in getattr(response, "models", []):
            model_name = getattr(item, "model", None) or getattr(item, "name", None)
            if model_name:
                models.append(model_name)

        normalized_target = OLLAMA_MODEL.split(":", 1)[0]
        normalized_models = {name.split(":", 1)[0] for name in models}

        if OLLAMA_MODEL in models or normalized_target in normalized_models:
            return True, None

        disponiveis = ", ".join(models) if models else "nenhum modelo encontrado"
        return (
            False,
            f"Modelo '{OLLAMA_MODEL}' nao encontrado no Ollama. Modelos disponiveis: {disponiveis}.",
        )
    except Exception as exc:
        return (
            False,
            f"Nao foi possivel conectar ao Ollama em {OLLAMA_HOST}. "
            f"Inicie o servico e carregue o modelo '{OLLAMA_MODEL}'. Detalhe: {exc}",
        )

# --- 3. DEFINIÇÃO DOS NÓS DO GRAFO (NODES) ---

def no_primeira_analise(state: MedicalState):
    log_evento("OLLAMA", "Gerando hipóteses iniciais baseadas em treinamento interno.")
    try:
        prompt = f"Como assistente médico, forneça uma análise técnica preliminar para: {state['sintomas']}."
        res = llm.invoke(prompt)
        return {"analise_ollama": f"[Ollama Local - Modelo Qwen2.5]: {res.content}"}
    except Exception as e:
        log_evento("OLLAMA", f"Erro no processamento local: {str(e)}", "error")
        raise

def no_enriquecimento_wiki(state: MedicalState):
    log_evento("WIKI", "Consultando Wikipedia para embasamento fisiopatológico.")
    try:
        res = search_wiki.run(f"Fisiopatologia de {state['sintomas']}")
        return {"dados_wiki": f"[Wikipedia]: {res}"}
    except Exception as e:
        log_evento("WIKI", f"Falha ao acessar Wikipedia: {str(e)}", "error")
        return {"dados_wiki": "[Wikipedia]: Informação não encontrada."}

def no_busca_protocolos(state: MedicalState):
    log_evento("WEB", "Buscando protocolos 2026 via Web (Índice Bing).")
    try:
        res = search_online.run(f"Protocolos clínicos médicos 2026 para {state['sintomas']}")
        return {"dados_web": f"[DuckDuckGo Search / Bing]: {res}"}
    except Exception as e:
        log_evento("WEB", f"Falha na busca web: {str(e)}", "error")
        return {"dados_web": "[DuckDuckGo Search / Bing]: Busca web indisponível."}

def no_formatador_final(state: MedicalState):
    log_evento("FINALIZADOR", "Consolidando parecer final com rastreabilidade de fontes (XAI).")
    
    prompt_explicabilidade = f"""
    Você é um Assistente de Apoio à Decisão Clínica. Consolide os dados abaixo em um parecer técnico CURTO, DIRETO e SEM REPETIÇÕES.
    
    FONTES DISPONÍVEIS:
    1. CONHECIMENTO BASE (IA LOCAL): {state['analise_ollama']}
    2. FUNDAMENTAÇÃO CIENTÍFICA (WIKI): {state['dados_wiki']}
    3. ATUALIZAÇÃO 2026 (WEB): {state['dados_web']}
    
    REGRAS OBRIGATÓRIAS DE CITAÇÃO (EXPLAINABILITY):
    - Para cada afirmação técnica, indique a fonte entre parênteses.
    - Se usar o Conhecimento Base, cite: (Fonte: Ollama Local)
    - Se usar a Fundamentação Científica, cite: (Fonte: Wikipedia)
    - Se usar a Atualização 2026, cite: (Fonte: Web Search / Bing)
    
    ESTRUTURA DO PARECER:
    - Hipóteses Diagnósticas
    - Racional Científico e Protocolos
    - Seção final: 'LISTA DE FONTES E PROVEDORES' detalhando cada origem.

    PACIENTE: {state['perfil']} | SINTOMAS: {state['sintomas']}
    """
    
    res = llm.invoke(prompt_explicabilidade)
    return {"parecer_final": res.content}

# --- 4. MONTAGEM DO FLUXO (LANGGRAPH) ---
builder = StateGraph(MedicalState)
builder.add_node("ollama", no_primeira_analise)
builder.add_node("wikipedia", no_enriquecimento_wiki)
builder.add_node("duckduckgo", no_busca_protocolos)
builder.add_node("finalizador", no_formatador_final)

builder.set_entry_point("ollama")
builder.add_edge("ollama", "wikipedia")
builder.add_edge("wikipedia", "duckduckgo")
builder.add_edge("duckduckgo", "finalizador")
builder.add_edge("finalizador", END)

graph = builder.compile()

# --- 5. UTILITÁRIOS E LOOP PRINCIPAL ---

def liberar_memoria():
    """Garante a limpeza de objetos e coleta de lixo do Python."""
    gc.collect()
    log_evento("SISTEMA", "Limpeza de memória executada com sucesso.")

def executar_consulta(perfil: str, sintomas: str):
    """Executa o fluxo clínico completo e retorna os dados para CLI ou UI."""
    perfil = perfil.strip()
    sintomas = sintomas.strip()

    if not perfil:
        raise ValueError("Informe o perfil do paciente.")

    if not sintomas:
        raise ValueError("Informe os sintomas observados.")

    log_evento("USUÁRIO", f"Início de consulta: {perfil} | Sintomas: {sintomas}")
    ollama_ok, ollama_msg = verificar_ollama()

    if not ollama_ok:
        log_evento("OLLAMA", ollama_msg, "error")
        raise RuntimeError(ollama_msg)

    try:
        resultado = graph.invoke({"perfil": perfil, "sintomas": sintomas})
        log_evento("SISTEMA", "Relatório final gerado e exibido.")
        return {
            "perfil": perfil,
            "sintomas": sintomas,
            "parecer_final": resultado["parecer_final"],
            "analise_ollama": resultado.get("analise_ollama", ""),
            "dados_wiki": resultado.get("dados_wiki", ""),
            "dados_web": resultado.get("dados_web", ""),
            "aviso_legal": AVISO_LEGAL,
            "ollama_model": OLLAMA_MODEL,
            "ollama_host": OLLAMA_HOST,
        }
    except Exception as e:
        log_evento("GRAFO", f"Erro crítico na execução: {str(e)}", "error")
        raise
    finally:
        liberar_memoria()

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*80)
        print("      ASSISTENTE MÉDICO - EXPLAINABLE AI (XAI) & AUDITORIA")
        print("      Fluxo: IA Local -> Wiki -> Web -> Relatório")
        print("="*80)

        perfil = input("\nPerfil do Paciente (ou 'sair'): ")
        if perfil.lower() == 'sair': break
        
        sintomas = input("Sintomas Observados: ")
        if sintomas.lower() == 'sair': break

        try:
            resultado = executar_consulta(perfil, sintomas)

            # Exibição do Parecer
            print("\n" + "="*25 + " PARECER TECNICO SUGERIDO " + "="*25)
            print(resultado["parecer_final"])
            print("-" * 80)
            print(f"AVISO: {AVISO_LEGAL}")
            print("="*80 + "\n")

        except Exception as e:
            print(f"\nERRO: {e}")

        input("\n[Pressione ENTER para nova consulta]")

if __name__ == "__main__":
    main()
