[English Version](README_en-US.md) | [Versão em Português (Brasil)](README_pt-BR.md)
---

# 🎬 Selecionador de Filmes Infantil (Prova de Conceito)

## Descrição Curta
Este projeto é uma **Prova de Conceito (POC)** de uma aplicação de linha de comando em Python. Seu objetivo é ajudar pais e responsáveis a encontrar recomendações de filmes e séries adequadas para crianças, considerando idade, interesses, plataformas de streaming disponíveis no Brasil e classificações indicativas. Ele utiliza a API do The Movie Database (TMDb) para buscar informações sobre os títulos e a API do Google Gemini (através do Google AI Studio) para expandir ideias de busca e gerar justificativas amigáveis para as sugestões.

**Status do Projeto:** provas de conceito (POC) - Em desenvolvimento / Aperfeiçoamento.

## ✨ Funcionalidades Principais
* **Coleta de Preferências:** Pergunta a idade da criança, seus interesses atuais e as plataformas de streaming que a família assina. (Atualmente focado no Brasil).
* **Busca Inteligente no TMDb:**
    * Utiliza o Google Gemini para expandir os termos de interesse fornecidos pelo usuário, buscando uma gama maior de palavras-chave relevantes.
    * Realiza buscas no TMDb usando múltiplas estratégias (palavras-chave, termos diretos, gêneros populares para a idade) para aumentar as chances de encontrar conteúdo.
* **Enriquecimento de Dados:** Para cada título encontrado, busca informações detalhadas como gêneros, sinopse, avaliação dos usuários no TMDb e a classificação indicativa oficial no Brasil.
* **Verificação de Streaming:** Confere em quais das plataformas de streaming preferidas do usuário (no Brasil) o título está disponível para assinatura.
* **Justificativas com IA:** Usa o Google Gemini para criar um parágrafo amigável e personalizado, explicando por que cada sugestão pode ser uma boa escolha para a criança.
* **Verificação de Existência (Opcional):** Um agente adicional usa o Gemini com a Pesquisa Google para tentar confirmar se o título recomendado é amplamente conhecido e relevante, adicionando uma camada extra de checagem.
* **Exibição no Console:** Apresenta as recomendações finais de forma clara no terminal.

## 🚀 Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Bibliotecas Python Principais:**
    * `google-generativeai` (para a API do Google Gemini)
    * `requests` (para interagir com a API do TMDb)
    * `python-dotenv` (para gerenciar as chaves de API de forma segura)
* **APIs Externas:**
    * The Movie Database (TMDb) API (v3)
    * Google Gemini API (via Google AI Studio)

## ⚙️ Configuração do Ambiente e Instalação (Para Iniciantes)

Para executar este projeto em seu computador, você precisará seguir alguns passos. Não se preocupe, vamos detalhar cada um!

**Pré-requisitos:**
* Ter o Python 3 instalado no seu computador. Se não tiver, você pode baixá-lo em [python.org](https://www.python.org/downloads/). Durante a instalação no Windows, marque a opção "Add Python to PATH".
* Um editor de texto simples (como Bloco de Notas, VS Code, Sublime Text, etc.) para criar e editar arquivos.
* Acesso à internet para baixar bibliotecas e para que o programa consulte as APIs.

**Passos de Configuração:**

1.  **Crie uma Pasta para o Projeto:**
    * No seu computador, crie uma nova pasta. Vamos chamá-la, por exemplo, de `selecionador_filmes_poc`.
    * Copie todos os arquivos deste projeto (`main.py`, `requirements.txt`, `.gitignore`, `README.md`, `README_pt-BR.md`) para dentro desta pasta.

2.  **Abra o Terminal (Prompt de Comando):**
    * **Windows:** Procure por "cmd" ou "PowerShell".
    * **macOS:** Procure por "Terminal".
    * **Linux:** Geralmente Ctrl+Alt+T ou procure por "Terminal".
    * Navegue até a pasta do projeto que você criou. Exemplo, se estiver no Windows e sua pasta está em `C:\Projetos\selecionador_filmes_poc`, digite:
        ```bash
        cd C:\Projetos\selecionador_filmes_poc
        ```

3.  **Crie um Ambiente Virtual Python (Boa Prática):**
    Um ambiente virtual isola as bibliotecas deste projeto das outras instaladas no seu sistema. No terminal, dentro da pasta do projeto, digite:
    ```bash
    python -m venv .venv
    ```
    Isso criará uma subpasta chamada `.venv` dentro do seu projeto.

4.  **Ative o Ambiente Virtual:**
    * **Windows (cmd):**
        ```bash
        .venv\Scripts\activate.bat
        ```
    * **Windows (PowerShell):**
        ```bash
        .venv\Scripts\Activate.ps1
        ```
        (Se encontrar um erro sobre execução de scripts no PowerShell, você pode precisar executar `Set-ExecutionPolicy Unrestricted -Scope Process` e tentar novamente).
    * **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```
    Seu prompt de comando deve mudar, mostrando algo como `(.venv)` no início, indicando que o ambiente está ativo.

5.  **Instale as Bibliotecas Necessárias (Dependências):**
    Com o ambiente virtual ativo, instale as bibliotecas listadas no arquivo `requirements.txt`. No terminal, digite:
    ```bash
    pip install -r requirements.txt
    ```
    Aguarde a conclusão da instalação.

6.  **Configure suas Chaves de API (Passo Fundamental!):**
    Este projeto precisa de chaves de API para funcionar. Elas são como senhas que dão ao programa permissão para usar os serviços do TMDb e do Google Gemini.

    * **Crie o arquivo `.env`:**
        * Dentro da pasta principal do seu projeto (`selecionador_filmes_poc`), crie um novo arquivo de texto simples e salve-o com o nome exatamente assim: `.env` (começa com um ponto e não tem extensão como `.txt` no final).
        * Se o seu explorador de arquivos não mostra extensões de arquivo, certifique-se de que ele não foi salvo como `.env.txt`.

    * **Adicione suas chaves ao arquivo `.env`:**
        Abra o arquivo `.env` com um editor de texto e copie o seguinte conteúdo nele:
        ```env
        GEMINI_API_KEY="COLE_SUA_CHAVE_API_DO_GOOGLE_AI_STUDIO_AQUI"
        TMDB_API_KEY="COLE_SUA_CHAVE_API_DO_TMDB_V3_AQUI"
        ```
    * **Como obter a Chave de API do Google AI Studio (Gemini):**
        1.  Vá para [Google AI Studio (anteriormente MakerSuite)](https://makersuite.google.com/).
        2.  Faça login com sua conta Google.
        3.  No menu à esquerda, clique em "**Get API key**" (Obter chave de API).
        4.  Clique em "**Create API key in new project**" (Criar chave de API em novo projeto) ou use uma existente se já tiver.
        5.  Copie a chave gerada e cole no lugar de `"COLE_SUA_CHAVE_API_DO_GOOGLE_AI_STUDIO_AQUI"` no seu arquivo `.env`.
            *Observação: A API do Gemini tem um nível gratuito generoso, mas fique atento aos limites de uso.*

    * **Como obter a Chave de API do TMDb (v3 auth):**
        1.  Vá para o site [The Movie Database (TMDb)](https://www.themoviedb.org/).
        2.  Crie uma conta gratuita ou faça login se já tiver uma.
        3.  Clique no ícone do seu perfil (avatar) no canto superior direito, depois em "**Configurações**" (Settings).
        4.  No menu à esquerda da página de configurações, clique em "**API**".
        5.  Leia os termos de uso e, se concordar, solicite uma chave de API (geralmente para uso como "Desenvolvedor"). Você precisará preencher um breve formulário sobre o uso pretendido.
        6.  Após a aprovação (pode ser imediata ou levar um tempo), você verá sua "**API Key (v3 auth)**". Copie esta chave.
        7.  Cole esta chave no lugar de `"COLE_SUA_CHAVE_API_DO_TMDB_V3_AQUI"` no seu arquivo `.env`.

    **Importante:** O arquivo `.env` nunca deve ser compartilhado publicamente (ex: enviado para o GitHub), pois contém suas chaves secretas. O arquivo `.gitignore` já está configurado para ignorá-lo.

## ▶️ Como Executar a Aplicação

1.  **Certifique-se de que o ambiente virtual esteja ativo:** Você deve ver `(.venv)` no início do seu prompt de comando. Se não estiver, ative-o conforme o Passo 4 da Configuração.
2.  **Navegue até a pasta do projeto:** Se você ainda não estiver nela, use o comando `cd` no terminal para entrar na pasta `selecionador_filmes_poc`.
3.  **Execute o script principal:**
    ```bash
    python main.py
    ```
4.  A aplicação começará a rodar no console. Ela fará algumas perguntas (idade da criança, interesses, plataformas de streaming). Responda a cada uma e pressione Enter.
5.  Após alguns segundos (enquanto busca e processa informações), ela deverá apresentar as recomendações de filmes/séries.

## 📂 Estrutura de Arquivos do Projeto

```

selecionador\_filmes\_poc/
├── .venv/                   \# Pasta do ambiente virtual Python (geralmente ignorada pelo Git)
├── .env                     \# Arquivo para armazenar suas chaves de API secretas (IGNORADO PELO GIT\!)
├── .gitignore               \# Especifica arquivos e pastas que o Git deve ignorar
├── main.py                  \# O script principal da aplicação em Python
├── requirements.txt         \# Lista as bibliotecas Python que o projeto precisa
├── README.md                \# Arquivo de informações em Inglês
└── README\_pt-BR.md          \# Este arquivo, em Português do Brasil

```

## 📝 Observações Importantes para esta POC

* **Chaves de API são Fundamentais:** A aplicação depende totalmente de chaves de API válidas para o TMDb e Google Gemini. Sem elas, ou se estiverem incorretas, o programa não funcionará como esperado ou apresentará erros.
* **Limites de Taxa da API do TMDb:** A API do TMDb possui limites de quantas requisições você pode fazer em um certo período (geralmente 40-50 requisições a cada 10 segundos por IP). Se você executar o script muitas vezes rapidamente, pode encontrar erros temporários. Aguarde alguns minutos antes de tentar novamente.
* **Lógica de Classificação Etária Simplificada:** A forma como o programa determina se um filme é adequado para a idade da criança (baseado na Classificação Indicativa do Brasil "L", "10", "12", etc.) é uma **simplificação para esta Prova de Conceito**. Um sistema de produção real precisaria de um mapeamento muito mais completo e preciso para os diversos sistemas de classificação de diferentes países.
* **Mapeamento de Plataformas de Streaming Simplificado:** A conversão dos nomes das plataformas de streaming que você digita (como "Netflix") para os IDs internos que o TMDb usa também é simplificada, usando uma pequena lista interna de plataformas comuns. Uma solução mais robusta buscaria a lista completa de provedores do TMDb para a sua região.
* **Idioma dos Resultados do TMDb:** As consultas ao TMDb nesta POC estão configuradas para `language=pt-BR`, buscando títulos e descrições em Português do Brasil quando disponíveis. A disponibilidade desses dados localizados pode variar no TMDb.
* **Tratamento de Erros Básico:** O programa inclui um tratamento de erros básico para chamadas de API e algumas entradas do usuário. Uma aplicação finalizada precisaria de um gerenciamento de erros mais robusto e feedback mais claro ao usuário.
* **Interface via Console:** Esta Prova de Conceito é operada inteiramente através da linha de comando (terminal/console). Não possui uma interface gráfica do usuário (GUI).

---
Contribuições e sugestões são bem-vindas (se o projeto fosse público/aberto)!
```