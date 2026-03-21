
# instalar
# Python versao 312

# 1. Criar o ambiente virtual
# & "C:\Users\rodrigo\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv

# 2. Ativar o ambiente (Windows PowerShell)
# .\.venv\Scripts\activate

# pip list
# pip list | findstr "lang"

# pip install -r requirements.txt

import warnings
import logging
import os
import sys
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Desativar avisos desnecessários
warnings.filterwarnings("ignore")

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def configurar_agente():
    # 1. Configuração do Modelo
    llm = ChatOllama(
        model='qwen2.5-7b-local', 
        temperature=0.1, 
        top_p=0.7
    )

    # 2. Ferramentas
    search_online = DuckDuckGoSearchRun()
    wiki_api = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1500)
    search_wiki = WikipediaQueryRun(api_wrapper=wiki_api)

    tools = [search_online, search_wiki]

    # 3. Prompt ReAct Adaptado (Fontes + Não Prescritivo)
    template = """Você é um Assistente de Apoio à Decisão Clínica. 
Sua tarefa é fornecer hipóteses baseadas em evidências para que um médico valide.

Sintomas do Paciente: {sintomas}
Perfil: {perfil}

REGRAS OBRIGATÓRIAS:
1. JAMAIS prescreva ou afirme diagnósticos. Use termos como "Sugere-se investigar" ou "Hipótese".
2. FONTES: Para cada recomendação ou hipótese baseada em busca, você DEVE citar a fonte no corpo do texto (ex: [Fonte: DuckDuckGo/Protocolo X] ou [Fonte: Wikipedia]).
3. No final da sua resposta, crie uma seção chamada "FONTES CONSULTADAS:" listando o que foi utilizado.
4. Use a Action: duckduckgo_search para buscar "Protocolos atualizados 2026" sobre os sintomas.

Ferramentas: {tools}

Use o formato:
Thought: [Meu raciocínio técnico]

Action: {tool_names}

Action Input: [Busca específica]

Observation: [Resultado da busca]
... (repetir se necessário)

Final Answer: [Seu parecer técnico estruturado]

Thought: {agent_scratchpad}"""

    prompt = PromptTemplate.from_template(template)

    # 4. Construção do Agente
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True,
        max_iterations=5
    )

def analisar_caso():
    limpar_tela()
    print("="*60)
    print("ASSISTENTE MÉDICO (IA) - APOIO E TRIAGEM")
    print("FONTES ATIVAS: DuckDuckGo, Wikipedia")
    print("="*60 + "\n")

    executor = configurar_agente()

    # Mensagem de segurança fixa (Hardcoded)
    AVISO_LEGAL = "ESTE RELATÓRIO É UMA MINUTA DE APOIO E NÃO SUBSTITUI A PRESCRIÇÃO E VALIDAÇÃO HUMANA."

    while True:
        perfil = input("Informe o Perfil do Paciente (ou 'sair'): ")
        if perfil.lower() == 'sair': break
        
        sintomas = input("Informe os Sintomas: ")
        if sintomas.lower() == 'sair': break

        print("\n" + "."*30)
        print("🔍 Pesquisando protocolos e evidências...")
        print("."*30 + "\n")

        try:
            response = executor.invoke({
                "perfil": perfil,
                "sintomas": sintomas
            })

            # EXIBIÇÃO DO PARECER
            print("\n" + "█"*20 + " PARECER TÉCNICO SUGERIDO " + "█"*20)
            print(response["output"])
            
            # EXIBIÇÃO DA TRAVA DE SEGURANÇA (VERMELHO)
            print("-" * 66)
            print(f"\033[91m⚠️  {AVISO_LEGAL}\033[0m") 
            print("█"*66 + "\n")
            
            input("[ENTER para nova consulta]")

        except Exception as e:
            print(f"\n❌ Erro no processamento: {e}")
        
        limpar_tela()

if __name__ == "__main__":
    analisar_caso()
