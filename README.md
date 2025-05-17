[English](README_en-US.md) | [Português (Brasil)](README.md)
---

# Prova de Conceito (POC): Selecionador de Filmes com TMDb e Google Gemini

Esta Prova de Conceito (POC) é uma aplicação de linha de comando em Python que recomenda filmes ou séries para crianças com base na idade, interesses, plataformas de streaming preferidas e país do usuário. Ela utiliza a API do The Movie Database (TMDb) para dados de filmes e disponibilidade de streaming, e a API do Google Gemini para gerar justificativas úteis para as recomendações.

## Funcionalidades

* Coleta as preferências do usuário: idade da criança, interesses atuais, serviços de streaming preferidos e país de residência.
* Busca filmes e séries no TMDb com base nos interesses fornecidos.
* Obtém informações detalhadas dos títulos em potencial, incluindo gêneros, classificações dos usuários no TMDb e tenta encontrar certificações de idade específicas do país.
* Verifica a disponibilidade desses títulos nas plataformas de streaming especificadas pelo usuário, dentro do seu país.
* Utiliza a API do Google Gemini para gerar um parágrafo amigável e contextual explicando por que uma seleção pode ser uma boa escolha.
* Exibe as recomendações finais e detalhadas diretamente para o usuário no console.

## Instruções de Configuração

1.  **Diretório do Projeto:**
    Certifique-se de que todos os arquivos do projeto (`main.py`, `requirements.txt`, `.env`, este `README_pt-BR.md`, `README.md` e `.gitignore`) estejam no mesmo diretório principal do projeto (por exemplo, `python-film-recommendation-agent/`).

2.  **Crie um Ambiente Virtual Python (Altamente Recomendado):**
    Abra o terminal ou prompt de comando do seu computador. Navegue até o diretório do seu projeto.
    Execute o seguinte comando para criar um ambiente virtual (chamado `venv` aqui):
    ```bash
    python3 -m venv .venv
    ```
    Ative o ambiente virtual criado:
    * No Windows:
        ```bash
        venv\Scripts\activate
        ```
    * No macOS ou Linux:
        ```bash
        source .venv/bin/activate
        ```
    Seu prompt de comando agora deve normalmente mostrar `(venv)` no início da linha, indicando que o ambiente virtual está ativo.

3.  **Instale as Dependências:**
    Com o ambiente virtual ativo, instale as bibliotecas Python necessárias listadas no arquivo `requirements.txt` executando:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as Chaves de API (Passo Crucial) no Arquivo `.env`:**
    * Na raiz do diretório do seu projeto (no mesmo local que `main.py`), crie um novo arquivo chamado exatamente `.env`.
    * Abra este arquivo `.env` com um editor de texto simples.
    * Adicione suas chaves de API secretas a este arquivo no seguinte formato:
        ```env
        GEMINI_API_KEY="SUA_CHAVE_DE_API_REAL_DO_GEMINI"
        TMDB_API_KEY="SUA_CHAVE_DE_API_REAL_DO_TMDB_V3"
        ```
    * **Importante:** Substitua `"SUA_CHAVE_DE_API_REAL_DO_GEMINI"` pela sua chave de API real obtida no Google AI Studio (makersuite.google.com).
    * **Importante:** Substitua `"SUA_CHAVE_DE_API_REAL_DO_TMDB_V3"` pela sua chave de API real do TMDb (especificamente, a chave "API Key (v3 auth)"). Você pode obtê-la registrando-se/logando no themoviedb.org e, em seguida, navegando até as Configurações da sua conta -> seção API.

## Como Executar a Aplicação

1.  Certifique-se de que seu ambiente virtual Python (por exemplo, `venv`) esteja ativado (você deve ver `(venv)` no seu prompt).
2.  No seu terminal ou prompt de comando, certifique-se de que você está no diretório raiz do projeto (onde `main.py` está localizado).
3.  Execute o script principal usando o interpretador Python:
    ```bash
    python main.py
    ```
4.  A aplicação então iniciará no console e fará uma série de perguntas para coletar suas preferências. Por favor, responda conforme solicitado.

## Estrutura de Arquivos do Projeto

O projeto deve ter os seguintes arquivos e pastas:

* `python-film-recommendation-agent/` (Sua pasta principal do projeto)
    * `.env` (Este arquivo armazena suas chaves de API secretas. Ele deve estar listado no `.gitignore`.)
    * `.gitignore` (Este arquivo informa ao Git quais arquivos/pastas ignorar.)
    * `main.py` (Este é o script Python principal contendo toda a lógica da aplicação e as funções dos agentes.)
    * `requirements.txt` (Este arquivo lista as dependências de pacotes Python necessárias para o projeto.)
    * `README.md` (O arquivo README principal, geralmente em inglês.)
    * `README_pt-BR.md` (Este arquivo, fornecendo instruções e informações sobre o projeto em Português do Brasil.)
    * `venv/` (Esta pasta contém seu ambiente virtual Python, se você criou um. Geralmente é ignorada pelo Git.)

## Observações Importantes para esta POC

* **Chaves de API são Essenciais:** A aplicação depende fortemente de chaves de API válidas tanto para o TMDb quanto para o Google Gemini. Ela não funcionará corretamente, ou de forma alguma para certas funcionalidades, se essas chaves estiverem ausentes ou inválidas.
* **Limites de Taxa da API do TMDb:** A API do The Movie Database impõe limites de taxa (tipicamente em torno de 40-50 requisições a cada 10 segundos por endereço IP). Se você executar o script muitas vezes seguidas rapidamente, poderá encontrar erros temporários do TMDb. Se isso acontecer, por favor, aguarde alguns minutos antes de tentar novamente.
* **Lógica de Classificação Etária (Simplificada):** A lógica implementada em `main.py` para determinar se a classificação etária de um filme (por exemplo, "L", "10" para o Brasil; "G", "PG" para os EUA) é apropriada para a idade da criança fornecida é uma **simplificação básica para esta Prova de Conceito**. Uma aplicação em nível de produção exigiria um sistema de mapeamento muito mais abrangente e preciso para diferentes países e seus sistemas de classificação específicos.
* **Mapeamento de Plataformas de Streaming (Simplificado):** O mapeamento dos nomes das plataformas de streaming inseridos pelo usuário (como "Netflix" ou "Disney Plus") para os IDs numéricos internos usados pelo TMDb também é simplificado nesta POC. Ele usa uma pequena lista codificada de provedores comuns. Uma solução mais robusta envolveria buscar a lista completa de provedores disponíveis no TMDb para a região do usuário e implementar um mecanismo de correspondência ou seleção mais flexível.
* **Configurações de Idioma:** As consultas ao TMDb nesta POC estão atualmente configuradas para usar `language=en-US` para buscar detalhes do conteúdo. Isso pode ser modificado dentro do script `main.py` se você desejar priorizar resultados ou descrições em outros idiomas (por exemplo, `pt-BR` para Português do Brasil). No entanto, a disponibilidade de dados totalmente localizados pode variar no TMDb.
* **Tratamento de Erros:** Um tratamento básico de erros para requisições de API e algumas entradas do usuário está incluído. Uma aplicação em produção exigiria um gerenciamento de erros e mecanismos de feedback ao usuário significativamente mais extensos.
* **Interface Baseada em Console:** Esta Prova de Conceito é operada inteiramente através da linha de comando (console). Não inclui uma interface gráfica do usuário (GUI).

---

Lembre-se de adicionar o link para este arquivo no seu `README.md` principal (em inglês) e vice-versa, como discutimos:

No seu `README.md` (inglês), adicione no topo:
```markdown
Read this in other languages: [Português (Brasil)](README_pt-BR.md)