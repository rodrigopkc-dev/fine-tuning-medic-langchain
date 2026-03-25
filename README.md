# 🏥 Assistente Médico XAI

Um assistente médico alimentado por Inteligência Artificial com capacidade de explicabilidade (XAI), desenvolvido com Streamlit, LangChain e Ollama. Fornece análises complementares baseadas em sintomas e perfil do paciente.

## ⚠️ Aviso Legal

**ESTE RELATÓRIO É UMA MINUTA DE APOIO E NÃO SUBSTITUI A PRESCRIÇÃO E VALIDAÇÃO HUMANA.**

Este assistente é destinado apenas para fins educacionais e de pesquisa. Qualquer diagnóstico ou recomendação médica deve ser validada por um profissional de saúde qualificado.

## 📋 Características

- **Interface Web Intuitiva**: Desenvolvida com Streamlit com design responsivo
- **Integração com IA Local**: Usa Ollama para processamento local e privado
- **Busca de Conhecimento**: Integra Wikipedia e DuckDuckGo para complementar análises
- **Rastreamento Auditável**: Mantém logs detalhados de todas as consultas em `rastreamento_clinico.log`
- **Temperatura de IA Controlada**: Configuração para máxima previsibilidade em contextos médicos (temperatura: 0.0)
- **LangGraph**: Utiliza grafos de estado para fluxos de processamento robustos

## 🛠️ Pré-requisitos

- **Python 3.12**
- **Ollama** (com modelo `qwen2.5-7b-local` instalado)
- **pip** (gerenciador de pacotes Python)

### Instalação do Ollama

1. Baixe e instale o Ollama em: [https://ollama.ai](https://ollama.ai)
2. Puxe o modelo necessário:
   ```powershell
   ollama pull qwen2.5
   ```
3. Inicie o servidor Ollama (será executado em `http://127.0.0.1:11434` por padrão)

# ollama create qwen2.5-7b-local -f Modelfile

# ollama run qwen2.5-7b-local



## 📦 Instalação

### 1. Clonar o Repositório

```powershell
git clone <https://github.com/rodrigopkc-dev/fine-tuning-medic-langchain.git>

cd fine-tuning-feat-interface
```

### 2. Criar Ambiente Virtual

```powershell
python -m venv .venv
```

### 3. Ativar o Ambiente Virtual (Windows PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar Dependências

```powershell
pip install -r requirements.txt
```

## 🚀 Execução

### Opção 1: Usar o Script PowerShell (Recomendado)

```powershell
.\run_ui.ps1
```

### Opção 2: Execução Manual

```powershell
python -m streamlit run src/app.py
```

A aplicação será aberta automaticamente em `http://localhost:8501`

## ⚙️ Configuração

As seguintes variáveis de ambiente podem ser configuradas:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `OLLAMA_MODEL` | `qwen2.5-7b-local` | Nome do modelo Ollama a usar |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | URL do servidor Ollama |

### Definir Variáveis de Ambiente (PowerShell)

```powershell
$env:OLLAMA_MODEL = "seu-modelo"
$env:OLLAMA_HOST = "http://seu-host:11434"

# ollama create qwen2.5-7b-local -f Modelfile

# ollama run qwen2.5-7b-local


```

## 📂 Estrutura do Projeto

```
fine-tuning-feat-interface/
├── src/
│   ├── app.py              # Interface Streamlit
│   ├── main.py             # Lógica principal e orquestração
│   └── __pycache__/        # Cache Python
├── .venv/                  # Ambiente virtual
├── requirements.txt        # Dependências do projeto
├── run_ui.ps1             # Script de execução
├── rastreamento_clinico.log # Logs de auditoria (gerado ao executar)
└── README.md              # Este arquivo
```

## 📚 Dependências Principais

- **Streamlit** (≥1.41, <2): Framework para interface web
- **LangChain** (0.3.0): Orquestração de componentes IA
- **LangGraph** (0.2.20): Construção de grafos de estado
- **Ollama**: Execução local de modelos LLM
- **DuckDuckGo Search**: Busca online
- **Wikipedia**: Acesso a conhecimento enciclopédico
- **Pydantic** (2.12.5): Validação de dados

## 🔍 Como Usar

1. **Inicie a aplicação** usando um dos métodos acima
2. **Visualize o Status do Ollama** - A interface mostrará se o servidor está conectado
3. **Insira o Perfil do Paciente** - Informações básicas do paciente
4. **Descreva os Sintomas** - Lista detalhada de sintomas apresentados
5. **Receba a Análise** - O assistente processará e fornecerá:
   - Análise do modelo LLM
   - Dados complementares da Wikipedia
   - Resultados de busca online
   - Parecer final sintetizado

## 📝 Logs de Auditoria

Todas as consultas são registradas em `rastreamento_clinico.log` para fins de auditoria e rastreamento. Os logs incluem:

- Timestamp de cada operação
- Nível de log (INFO, ERROR, etc.)
- Nó do fluxo onde a operação ocorreu
- Detalhes da mensagem

## 🐛 Troubleshooting

### Erro: "Ollama indisponível"

- Certifique-se de que o Ollama está em execução
- Verifique a URL em `OLLAMA_HOST`
- Confirme que o modelo foi instalado com `ollama list`

### Erro: "Modelo não encontrado"

```powershell
ollama pull qwen2.5
```

### Ambiente virtual não encontrado

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📞 Suporte

Para questões ou problemas, consulte:

- [Documentação Streamlit](https://docs.streamlit.io)
- [LangChain Documentation](https://python.langchain.com)
- [Ollama Documentation](https://github.com/ollama/ollama)

## 📄 Licença

Especifique sua licença aqui.

---

**Desenvolvido para fins educacionais e de pesquisa em IA e Saúde.**
