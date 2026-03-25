# RELATÓRIO TÉCNICO - ASSISTENTE MÉDICO COM EXPLAINABLE AI

**Data:** Março 2026  
**Versão do Projeto:** 1.0  
**Stack:** Python 3.12 | LangChain | LangGraph | Ollama Local

---

## 📋 SUMÁRIO EXECUTIVO

Projeto de um **Assistente Médico Inteligente com Explainability (XAI)** que integra:
- IA Local (Ollama Qwen2.5-7B)
- Conhecimento Wikipedia (fisiopatologia)
- Busca Web em Tempo Real (DuckDuckGo/Bing)
- **Rastreabilidade de Fontes** (citação obrigatória)
- **Auditoria Completa** (logs estruturados)

---

## 🎯 OBJETIVO DO PROJETO

Desenvolver um **Sistema de Apoio à Decisão Clínica (Clinical Decision Support - CDS)** que:

1. **Análise Preliminar Local**: Gera hipóteses diagnósticas usando LLM local (Ollama) com temperatura 0.0 (previsibilidade máxima para contexto médico)

2. **Enriquecimento Científico**: Complementa análises com conhecimento fisiopatológico via Wikipedia

3. **Protocolos Atualizados**: Integra protocolos clínicos 2026 via busca web

4. **Explainability Obrigatória**: Cada afirmação é rastreada até sua fonte (Ollama/Wiki/Web)

5. **Auditoria e Compliance**: Registo completo de todas as consultas com timestamps e erros

### Contexto de Uso
- **Pacientes**: Consultores de saúde, pesquisadores
- **Integração**: Suporte humano (NÃO substitui prescrição médica)
- **Segurança**: Aviso legal em cada parecer gerado

---

## 🔧 TÉCNICAS IMPLEMENTADAS

### 1. **Orquestração de Fluxos (LangGraph)**
   - **StateGraph**: Grafo dirigido acíclico (DAG) de processamento
   - **Estado Estruturado**: TypedDict com 6 campos de estado
   - **Fluxo Sequencial**: Ollama → Wikipedia → DuckDuckGo → Finalizador → END
   
   ```
   [OLLAMA] → [WIKIPEDIA] → [DUCKDUCKGO] → [FINALIZADOR] → [FIM]
   ```

### 2. **Explainable AI (XAI)**
   - Rastreamento obrigatório de fontes em cada afirmação
   - Prompt estruturado com regras de citação
   - Seção "LISTA DE FONTES E PROVEDORES" no parecer final
   - Facilita auditoria e validação clínica

### 3. **State Management**
   - **Classe MedicalState** (TypedDict):
     - `perfil`: Dados do paciente
     - `sintomas`: Queixa principal
     - `analise_ollama`: Saída do modelo local
     - `dados_wiki`: Fundamentação científica
     - `dados_web`: Protocolos atualizados
     - `parecer_final`: Consolidação com XAI

### 4. **Logging Estruturado para Auditoria**
   - Dual-output: Arquivo (`rastreamento_clinico.log`) + Console
   - Timestamps em cada evento
   - Níveis: INFO e ERROR
   - Rastreamento por nó (OLLAMA, WIKI, WEB, FINALIZADOR, SISTEMA)

### 5. **Tratamento de Erros Robusto**
   - Try/except em cada nó
   - Fallbacks explícitos (ex: "[Wikipedia]: Informação não encontrada")
   - Continuidade de execução mesmo com falhas parciais

### 6. **Gerenciamento de Memória**
   - Função `liberar_memoria()` com `gc.collect()`
   - Limpeza pós-consulta (delete de variáveis)
   - Otimizado para ambientes com recursos limitados

---

## 📦 BIBLIOTECAS E DEPENDÊNCIAS

| Biblioteca | Versão | Função |
|-----------|--------|---------|
| **langchain** | 0.3.0 | Framework base para LLM orchestration |
| **langchain-community** | 0.3.0 | Integrações (DuckDuckGo, Wikipedia) |
| **langchain-ollama** | 0.2.0 | Suporte para Ollama local |
| **langgraph** | 0.2.20 | Orquestração de fluxos (StateGraph) |
| **duckduckgo-search** | ≥6.2.11 | Busca web via DuckDuckGo |
| **wikipedia** | 1.4.0 | API Wikipedia |
| **pydantic** | 2.12.5 | Validação de tipos |
| **Python** | 3.12+ | Linguagem base |

### Dependências Transitivas Importantes
- `langchain-*`: Eco-sistema LangChain
- `langgraph-*`: Checkpointing e SDK
- `pydantic-*`: Serialização e settings

---

## 💡 ARQUITETURA TÉCNICA

### 5 Nós Principais

| Nó | Entrada | Processamento | Saída | Propósito |
|----|---------|--------------|-------|-----------|
| **ollama** | `sintomas` | ChatOllama (T=0.0, max=500) | `analise_ollama` | Análise inicial baseada em conhecimento treinado |
| **wikipedia** | `analise_ollama` | WikipediaQueryRun | `dados_wiki` | Enriquecimento fisiopatológico |
| **duckduckgo** | Contexto completo | DuckDuckGoSearchRun | `dados_web` | Protocolos e guidelines 2026 |
| **finalizador** | Todos os dados | Prompt XAI + consolidação | `parecer_final` | Parecer estruturado com rastreabilidade |
| **END** | `parecer_final` | N/A | N/A | Término do fluxo |

### Fluxo de Dados
```
Input: {perfil, sintomas}
  ↓
[State: MedicalState] ← atualizado a cada nó
  ↓
[DAG Execution] ← processamento paralelo possível (atual: sequencial)
  ↓
Output: {parecer_final com fontes}
```

---

## 🎨 USABILIDADE PRÁTICA

### Interface do Usuário
```
┌─────────────────────────────────────────────────────────┐
│   ASSISTENTE MÉDICO - EXPLAINABLE AI & AUDITORIA       │
│   Fluxo: IA Local → Wiki → DuckDuckGo → Relatório      │
└─────────────────────────────────────────────────────────┘

Input 1: "Perfil do Paciente (ou 'sair'): " → homem, 45 anos, diabético
Input 2: "Sintomas Observados: " → fadiga, poliúria, visão borrada

Output:
┌─────────────────────────────────────────────────────────┐
│           PARECER TÉCNICO SUGERIDO                      │
│                                                         │
│ HIPÓTESES DIAGNÓSTICAS:                                │
│ · Diabetes Mellitus Tipo 2 (Fonte: Ollama Local)      │
│ · Cetoacidose Diabética (Fonte: Wikipedia)            │
│                                                         │
│ RACIONAL CIENTÍFICO:                                   │
│ · Protocolo ADA 2026 recomenda... (Fonte: Web/Bing) │
│                                                         │
│ LISTA DE FONTES:                                       │
│ · Wikipedia: https://pt.wikipedia.org/wiki/...        │
│ · Bing Search: www.bing.com/search?q=...             │
│                                                         │
│ ⚠️  Este relatório é uma minuta de apoio...          │
└─────────────────────────────────────────────────────────┘
```

### Fluxo Interativo (Loop Principal)

1. **Entrada de Dados**: Coleta perfil + sintomas
2. **Processamento**: Executa grafo (típico: 10-50 segundos)
3. **Saída**: Exibe parecer formatado com aviso legal
4. **Limpeza**: Libera memória
5. **Retorno ao Loop**: Pronto para nova consulta

### Recursos de UX

| Recurso | Implementação | Benefício |
|---------|---------------|-----------|
| **Enter para próxima consulta** | `input("[Pressione ENTER...]")` | Ritmo controlado |
| **Comando "sair"** | Detecção em inputs de perfil/sintomas | Saída graciosa |
| **Limpeza de tela** | `os.system('cls' / 'clear')` | Interface limpa a cada ciclo |
| **Cores no aviso** | `\033[91m...\033[0m` (vermelho) | Destaque visual |
| **Divisores visuais** | `═` e `█` | Estrutura clara |
| **Logs em tempo real** | FileHandler + StreamHandler | Monitoramento imediato |

---

## 📊 MÉTRICAS DE FUNCIONAMENTO

### Desempenho Esperado
- **Modelo LLM**: ChatOllama Qwen2.5-7B
- **Token Máximo**: 500 tokens
- **Temperatura**: 0.0 (respostas determinísticas)
- **Tempo Estimado do Fluxo**: 10-50 segundos (depende de conectividade)

### Limitações
- **Sequencial**: Nós executam um por um (sem paralelismo)
- **Offline Parcial**: DuckDuckGo requer internet; fallback gracioso
- **Wikipedia**: Top 1 resultado, máximo 1500 caracteres
- **Sem Persistência**: Dados não salvos entre sessões (apenas logs)

---

## 🔐 SEGURANÇA E CONFORMIDADE

### Auditoria
- ✅ Logs estruturados com timestamps
- ✅ Rastreamento por nó (OLLAMA, WIKI, WEB, etc.)
- ✅ Arquivo separado: `rastreamento_clinico.log`
- ✅ Encoding UTF-8 (suporta acentos)

### Aviso Legal
- ✅ Exibido em cada parecer
- ✅ Cores destacadas (vermelho)
- ✅ Mensagem: "MINUTA DE APOIO - NÃO SUBSTITUI PRESCRIÇÃO HUMANA"

### Tratamento de Erros
- ✅ Fallbacks explícitos (ex: Wikipedia não encontrada)
- ✅ Continuidade: falha parcial ≠ falha total
- ✅ Logging de exceções com stack trace

---

## 🚀 CICLO DE VIDA DE UMA CONSULTA

```
┌─────────────────────────────────────────────┐
│ 1. INICIALIZAÇÃO                            │
│    └─ Carrega modelos (Ollama, Chat)       │
│    └─ Inicializa ferramentas (Wiki, Web)   │
│    └─ Configura logging                    │
├─────────────────────────────────────────────┤
│ 2. INPUT DO USUÁRIO                         │
│    └─ Perfil: homem, 45 anos, diabético    │
│    └─ Sintomas: fadiga, poliúria           │
├─────────────────────────────────────────────┤
│ 3. EXECUÇÃO DO GRAFO                        │
│    [OLLAMA]     → Análise preliminar       │
│    [WIKIPEDIA]  → Embasamento científico   │
│    [DUCKDUCKGO] → Protocolos 2026          │
│    [FINALIZADOR]→ Consolidação com XAI     │
├─────────────────────────────────────────────┤
│ 4. OUTPUT                                   │
│    └─ Parecer estruturado                  │
│    └─ Citação de fontes                    │
│    └─ Aviso legal                          │
├─────────────────────────────────────────────┤
│ 5. LIMPEZA PÓS-CONSULTA                     │
│    └─ Delete de variáveis temporárias       │
│    └─ Garbage collection (gc.collect())    │
├─────────────────────────────────────────────┤
│ 6. LOOP: RETORNA AO STEP 2                  │
└─────────────────────────────────────────────┘
```

---

## 📈 CASOS DE USO

### ✅ Uso Recomendado
- **Pesquisa Clínica**: Buscar protocolos e fundamentação
- **Educação Médica**: Ensino de fisiopatologia
- **Triagem Inicial**: Segunda opinião estruturada
- **Auditoria**: Rastreabilidade de decisões

### ❌ Uso Não Recomendado
- **Diagnóstico Final**: Requer validação médica e exames
- **Prescrição Direta**: Não substitui consulta presencial
- **Casos de Urgência**: Tempo insuficiente para análise profunda

---

## 🔄 FUTUROS MELHORAMENTOS (Roadmap)

1. **Paralelismo**: Executar Wikipedia + DuckDuckGo em paralelo
2. **Persistência**: Banco de dados (PostgreSQL / SQLite)
3. **Dashboard Web**: Interface Flask/FastAPI
4. **Modelos Adicionais**: Suporte a GPT-4, Claude, outros Ollama
5. **Validação Clinical**: Integração com SNOMED CT / ICD-10
6. **RAG (Retrieval-Augmented Generation)**: Base de conhecimento customizada
7. **Multi-idioma**: Expandir além de Português/Inglês

---

## 📚 DEPENDÊNCIAS DO AMBIENTE

```bash
# Requerimentos de Sistema
- Python 3.12+
- Ollama instalado e rodando (qwen2.5-7b-local)
- Conexão com internet (para Wiki + DuckDuckGo)
- ~2GB RAM mínimo

# Setup
python -m venv .venv
.\.venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
```

---

## 📄 ESTRUTURA DE ARQUIVOS

```
fine-tuning-medic-langGraph/
├── src/
│   └── main.py                      # Aplicação principal
├── requirements.txt                 # Dependências Python
├── rastreamento_clinico.log        # Log de auditoria (gerado em runtime)
└── RELATORIO_PROJETO.md            # Este documento
```

---

## 🎓 CONCLUSÃO

**Assistente Médico com Explainable AI** é um **MVP (Minimum Viable Product)** completo que demonstra:

✅ **Integração Multi-Fonte**: IA Local + Wikipedia + Web  
✅ **Explainability**: Rastreabilidade obrigatória de fontes  
✅ **Auditoria Completa**: Logs estruturados com timestamps  
✅ **Usabilidade Prática**: Interface interativa e intuitiva  
✅ **Robustez**: Tratamento de erros e fallbacks  
✅ **Escalabilidade**: Preparado para paralelismo e persistência  

**Pronto para**: Pesquisa, Prototipagem, Educação Médica, Sistemas de Apoio Clínico.

---

**Autor**: Projeto de Fine-Tuning em LangGraph  
**Data**: Março 2026  
**Status**: ✅ Operacional
