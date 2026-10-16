"""
MIT License

Copyright (c) 2026 Arquiteto de Software / Aluno

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import streamlit as st
from openai import AzureOpenAI

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Extrator de Dados Inteligente - Azure OpenAI",
    page_icon="🤖",
    layout="centered"
)

# ==============================================================================
# GUIA DIDÁTICO: COMO CONFIGURAR OS SECRETS LOCALMENTE (.streamlit/secrets.toml)
# ==============================================================================
"""
COMO CONFIGURAR SUAS CREDENCIAIS LOCALMENTE:

1. Na raiz do seu projeto (onde está o arquivo `app.py`), crie uma pasta chamada `.streamlit`.
2. Dentro da pasta `.streamlit`, crie um arquivo chamado `secrets.toml`.
3. Adicione suas credenciais fornecidas pela Microsoft Foundry no formato abaixo:

   [azure_openai]
   api_key = "SEU_API_KEY_AQUI"
   endpoint = "https://seu-recurso.services.ai.azure.com/"
   deployment_name = "gpt-4.1-mini"

O Streamlit carrega automaticamente esses segredos de forma segura através de `st.secrets`.
Caso esteja testando sem o arquivo secrets configurado, o código abaixo utiliza fallbacks de demonstração.
"""

# ==============================================================================
# RECUPERAÇÃO DE CREDENCIAIS (SECRETS OU FALLBACK)
# ==============================================================================
try:
    AZURE_API_KEY = st.secrets["azure_openai"]["api_key"]
    AZURE_ENDPOINT = st.secrets["azure_openai"]["endpoint"]
    AZURE_DEPLOYMENT = st.secrets["azure_openai"]["deployment_name"]
except Exception:
    # Fallback para fins educacionais caso o secrets.toml ainda não tenha sido criado
    AZURE_API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
    AZURE_ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
    AZURE_DEPLOYMENT = "gpt-4.1-mini"

# ==============================================================================
# INICIALIZAÇÃO DO CLIENTE AZURE OPENAI
# ==============================================================================
# Utilizamos a classe oficial AzureOpenAI conforme as diretrizes da SDK da OpenAI
client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version="2024-02-01-preview",  # Versão recomendada para Azure OpenAI Chat Completions
    azure_endpoint=AZURE_ENDPOINT
)

# ==============================================================================
# INTERFACE GRÁFICA (UI) COM STREAMLIT
# ==============================================================================
st.title("🤖 Extrator de Dados Inteligente")
st.markdown("Aplicação corporativa alimentada por **Azure OpenAI** para análise estruturada de textos.")

st.divider()

# Campo de entrada de texto do usuário
texto_usuario = st.text_area(
    "Digite ou cole o texto para análise:",
    placeholder="Ex: Reunião urgente marcada com o Carlos e a Ana para discutir o atraso no projeto Alpha amanhã às 10h...",
    height=150
)

# Botão de processamento
if st.button("Processar Texto", type="primary", use_container_width=True):
    if not texto_usuario.strip():
        st.warning("⚠️ Por favor, insira um texto válido antes de processar.")
    else:
        with st.spinner("Processando dados com Azure OpenAI..."):
            try:
                # System Prompt Rígido exigindo retorno estrito em JSON
                system_prompt = """
                Você é um Arquiteto de Software e Analista de Dados Especialista em IA.
                Sua tarefa é analisar o texto fornecido pelo usuário e retornar ESTRITAMENTE UM JSON válido (sem formatação markdown adicional fora do JSON, ou com parse correto) contendo exatamente as seguintes chaves:
                1. "sentimento": string indicando o sentimento predominante ("Positivo", "Negativo" ou "Neutro").
                2. "porcentagem_sentimento": número inteiro de 0 a 100 representando a porcentagem de intensidade ou confiança desse sentimento.
                3. "assunto_principal": string resumindo o tema central do texto em poucas palavras.
                4. "pessoas_citadas": lista (array) de strings contendo os nomes de todas as pessoas mencionadas no texto. Se nenhuma, retorne uma lista vazia.
                5. "nivel_de_urgencia": string com valor estrito entre "Baixo", "Medio" ou "Alto".
                """

                # Chamada à API utilizando o modelo configurado
                response = client.chat.completions.create(
                    model=AZURE_DEPLOYMENT,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": texto_usuario}
                    ],
                    response_format={"type": "json_object"}  # Força o modelo a retornar JSON válido
                )

                # Extração e conversão do conteúdo da resposta
                conteudo_resposta = response.choices[0].message.content
                dados_extraidos = json.loads(conteudo_resposta)

                st.success("✨ Processamento concluído com sucesso!")
                st.divider()

                # ==============================================================
                # EXIBIÇÃO ESTRUTURADA DOS RESULTADOS
                # ==============================================================
                st.subheader("📊 Resultados da Extração")

                # Métricas principais em colunas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Sentimento Predominante",
                        value=dados_extraidos.get("sentimento", "N/A")
                    )
                
                with col2:
                    porcentagem = dados_extraidos.get("porcentagem_sentimento", 0)
                    st.metric(
                        label="Intensidade / Confiança",
                        value=f"{porcentagem}%"
                    )
                
                with col3:
                    urgencia = dados_extraidos.get("nivel_de_urgencia", "Baixo")
                    st.metric(
                        label="Nível de Urgência",
                        value=urgencia
                    )

                # Assunto Principal
                st.markdown("### 📌 Assunto Principal")
                st.info(dados_extraidos.get("assunto_principal", "Não informado"))

                # Pessoas Citadas
                st.markdown("### 👥 Pessoas Citadas")
                pessoas = dados_extraidos.get("pessoas_citadas", [])
                if pessoas:
                    for pessoa in pessoas:
                        st.markdown(f"- {pessoa}")
                else:
                    st.write("Nenhuma pessoa citada no texto.")

                # Exibição do JSON bruto para auditoria ou debug
                with st.expander("🔍 Ver JSON Bruto Retornado pela API"):
                    st.json(dados_extraidos)

            except json.JSONDecodeError:
                st.error("❌ Erro ao decodificar a resposta do modelo como JSON. Tente novamente.")
            except Exception as e:
                st.error(f"❌ Ocorreu um erro na comunicação com o Azure OpenAI: {e}")
