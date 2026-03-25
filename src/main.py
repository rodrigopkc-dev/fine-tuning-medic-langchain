
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
AVISO_LEGAL = "ESTE RELATÓRIO É UMA MINUTA DE APOIO E NÃO SUBSTITUI A PRESCRIÇÃO E VALIDAÇÃO HUMANA."

class MedicalState(TypedDict):
    perfil: str
    sintomas: str
    analise_ollama: str
    dados_wiki: str
    dados_web: str
    parecer_final: str

# Inicialização das ferramentas
# Temperatura 0.0 para garantir previsibilidade médica
llm = ChatOllama(model='qwen2.5-7b-local', temperature=0.0, num_predict=500) 
search_online = DuckDuckGoSearchRun()
wiki_api = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1500)
search_wiki = WikipediaQueryRun(api_wrapper=wiki_api)

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
    log_evento("WEB", "Buscando protocolos 2026 via Web/Bing (Índice Bing).")
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
    - Se usar a Atualização 2026, cite: (Fonte: Web / Bing)
    
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

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*80)
        print("      ASSISTENTE MÉDICO - EXPLAINABLE AI (XAI) & AUDITORIA")
        print("      Fluxo: IA Local -> Wiki -> DuckDuckGo -> Relatório")
        print("="*80)

        perfil = input("\nPerfil do Paciente (ou 'sair'): ")
        if perfil.lower() == 'sair': break
        
        sintomas = input("Sintomas Observados: ")
        if sintomas.lower() == 'sair': break

        log_evento("USUÁRIO", f"Início de consulta: {perfil} | Sintomas: {sintomas}")

        try:
            # Execução do Grafo
            inputs = {"perfil": perfil, "sintomas": sintomas}
            resultado = graph.invoke(inputs)
            
            # Exibição do Parecer
            print("\n" + "█"*25 + " PARECER TÉCNICO SUGERIDO " + "█"*25)
            print(resultado["parecer_final"])
            print("-" * 80)
            print(f"\033[91m⚠️  {AVISO_LEGAL}\033[0m")
            print("█"*80 + "\n")
            
            log_evento("SISTEMA", "Relatório final gerado e exibido.")

            # Limpeza Pós-Consulta
            del resultado
            del inputs
            liberar_memoria()

        except Exception as e:
            log_evento("GRAFO", f"Erro crítico na execução: {str(e)}", "error")
            print(f"\n❌ Ocorreu um erro: {e}")
            liberar_memoria()

        input("\n[Pressione ENTER para nova consulta]")

if __name__ == "__main__":
    main()
