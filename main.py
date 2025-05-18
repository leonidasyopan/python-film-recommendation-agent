import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import json
import unicodedata # Adicione esta linha

# --- CONFIGURATION ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
# Nova linha para carregar o ID do modelo Gemini do .env
GEMINI_MODEL_ID_FROM_ENV = os.getenv("GEMINI_MODEL_ID", 'gemini-1.5-flash-latest') # Define um fallback

gemini_model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Usa a variável carregada do .env (ou o fallback)
        gemini_model = genai.GenerativeModel(GEMINI_MODEL_ID_FROM_ENV) 
        print(f"✅ API do Gemini configurada com sucesso usando o modelo: {GEMINI_MODEL_ID_FROM_ENV}.") # User-facing: Portuguese
    except Exception as e:
        print(f"🔴 Erro ao configurar a API do Gemini com o modelo '{GEMINI_MODEL_ID_FROM_ENV}': {e}. Funcionalidades do Gemini serão puladas.") # User-facing: Portuguese
else:
    print("⚠️  GEMINI_API_KEY não encontrada no arquivo .env. Funcionalidades do Gemini serão puladas.") # User-facing: Portuguese

if not TMDB_API_KEY:
    print("🔴 TMDB_API_KEY não encontrada no arquivo .env. Funcionalidades do TMDb não funcionarão. Por favor, configure-a e reinicie.") # User-facing: Portuguese

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TARGET_COUNTRY_CODE = "BR" # Hardcoded for Brazil
TARGET_LANGUAGE_TMDB = "pt-BR" # For TMDb results in Portuguese

# --- HELPER FUNCTIONS ---

def make_tmdb_request(endpoint, params=None, method="GET"):
    # Helper function to make requests to TMDb API.
    if not TMDB_API_KEY:
        print("ℹ️ Chave da API do TMDb não disponível. Pulando requisição ao TMDb.") # User-facing: Portuguese
        return None
    if params is None:
        params = {}
    params['api_key'] = TMDB_API_KEY
    if 'language' not in params: # Default language for TMDb
        params['language'] = TARGET_LANGUAGE_TMDB
    
    headers = {"accept": "application/json"}
    full_url = f"{TMDB_BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(full_url, params=params, headers=headers)
        else:
            print(f"🔴 Método HTTP não suportado: {method}") # User-facing: Portuguese
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try:
            error_details = response.json()
        except ValueError:
            error_details = response.text[:200]
        print(f"🔴 Erro HTTP ao fazer requisição ao TMDb para {endpoint}: {http_err} - Status: {response.status_code}, Resposta: {error_details}") # User-facing: Portuguese
    except requests.exceptions.RequestException as e:
        print(f"🔴 Erro geral ao fazer requisição ao TMDb para {endpoint}: {e}") # User-facing: Portuguese
    return None

def get_tmdb_provider_id_from_name(provider_name_input, watch_region="BR"):
    # Simplified mapping of common streaming provider names to their TMDb IDs for Brazil.
    # A production app would fetch and cache these dynamically.
    provider_name_lower = provider_name_input.lower().strip()
    common_provider_map = {
        "netflix": 8, "amazon prime video": 9, "prime video": 9, "amazon video": 9,
        "disney plus": 337, "disney+": 337, "max": 1899, "hbo max": 384, 
        "apple tv plus": 350, "appletv+": 350, "apple tv+": 350,
        "globoplay": 307, "star plus": 619, "star+": 619, "claro video": 167,
        "looke": 484, "paramount plus": 531, "paramount+": 531,
    }
    return common_provider_map.get(provider_name_lower)

# def get_keyword_ids_from_tmdb(keyword_query_list):
#     # Fetches keyword IDs from TMDb for a list of query strings.
#     if not TMDB_API_KEY: return []
#     keyword_ids = set() 
#     # print(f"  -> Buscando IDs de palavras-chave no TMDb para: {keyword_query_list}") # Debug, can be enabled
#     for query in keyword_query_list:
#         if not query.strip(): continue
#         params = {'query': query.strip(), 'page': 1}
#         data = make_tmdb_request("/search/keyword", params=params)
#         if data and 'results' in data and data['results']:
#             for res in data['results'][:2]: # Take top 2 relevant keyword IDs for this query term
#                 keyword_ids.add(res['id'])
#                 # print(f"    Encontrado ID de palavra-chave: {res['id']} para '{res['name']}' (de '{query}')") # Debug
#     return list(keyword_ids)

# --- AGENT FUNCTION DEFINITIONS ---

def agent_user_context_collector():
    # Agent 1: Collects user preferences.
    print("\n--- 🙋 Agente 1: Coletor de Contexto do Usuário ---") # User-facing: Portuguese
    while True:
        try:
            age_str = input("➡️  Digite a idade da criança (ex: 5, 8, 12): ") # User-facing: Portuguese
            age = int(age_str)
            if 1 <= age <= 18: break
            else: print("⚠️  Por favor, digite uma idade válida entre 1 e 18.") # User-facing: Portuguese
        except ValueError: print("⚠️  Entrada inválida. Por favor, digite um número para a idade.") # User-facing: Portuguese

    interests_query = input("➡️  Quais são os interesses da criança hoje (ex: 'animação divertida com animais falantes', 'filmes de aventura espacial')? ") # User-facing: Portuguese
    if not interests_query.strip():
        print("ℹ️  Nenhum interesse específico fornecido. Buscando por conteúdo popular infantil.") # User-facing: Portuguese
        interests_query = "filmes infantis populares animação família" # Default fallback
    else:
        # Normaliza a string para tentar corrigir problemas de codificação com caracteres especiais
        interests_query = unicodedata.normalize('NFC', interests_query)

    platforms_input_str = input("➡️  Digite as plataformas de streaming preferidas, separadas por vírgula (ex: 'Netflix, Disney Plus, Globoplay'): ") # User-facing: Portuguese
    preferred_platform_names_cleaned = [p.strip().lower() for p in platforms_input_str.split(',') if p.strip()]
    
    print("✅ Contexto coletado. País definido como Brasil.") # User-facing: Portuguese
    return {
        "age": age,
        "interests_query": interests_query,
        "preferred_platform_names": preferred_platform_names_cleaned,
        "country_code": TARGET_COUNTRY_CODE 
    }

def agent_content_prospector(user_context):
    """Agente 2: Expande interesses com Gemini e busca conteúdo no TMDb com múltiplas estratégias."""
    print("\n--- 🔎 Agente 2: Investigador de Conteúdo (Estratégias Múltiplas no TMDb) ---") # User-facing: Portuguese
    if not TMDB_API_KEY: return []

    original_interest_query = user_context['interests_query']
    child_age = user_context['age']
    country_code = user_context['country_code']
    
    all_prospects_map = {} # Use a dictionary for unique prospects by ID

    # ETAPA 1: Expansão de Interesses com Gemini para obter termos de busca e possíveis gêneros
    print(f"🧠 Consultando o Gemini para expandir e categorizar o interesse: '{original_interest_query}'...") # User-facing: Portuguese
    search_terms_from_gemini = {original_interest_query} # Start with the original
    genre_hints_from_gemini = []

    if gemini_model:
        try:
            prompt_for_gemini_analysis = (
                f"Uma criança no Brasil está interessada em '{original_interest_query}'.\n"
                f"1. Sugira de 2 a 4 frases ou palavras-chave alternativas e diversas para buscar filmes/séries sobre este tema no TMDb. Não inclua a frase original.\n"
                f"2. Quais seriam os 2 ou 3 principais IDs de gênero do TMDb (ex: Animação=16, Aventura=12, Ficção científica=878, Família=10751, Comédia=35, Drama=18, Fantasia=14) que melhor se encaixam nesse interesse? Se não tiver certeza, não sugira IDs.\n"
                f"Formato da resposta esperada:\n"
                f"TERMOS: termo1, termo2, termo3\n"
                f"GENEROS_IDS: 16, 10751"
            ) # Prompt for Gemini: Portuguese
            response = gemini_model.generate_content(prompt_for_gemini_analysis)

            if hasattr(response, 'text') and response.text:
                # print(f"[DEBUG] Gemini Analysis Response: {response.text}") # Debug
                lines = response.text.split('\n')
                for line in lines:
                    if line.upper().startswith("TERMOS:"):
                        terms_str = line.split(":", 1)[1]
                        additional_terms = [term.strip() for term in terms_str.split(',') if term.strip()]
                        if additional_terms:
                            for term in additional_terms: search_terms_from_gemini.add(term)
                    elif line.upper().startswith("GENEROS_IDS:"):
                        ids_str = line.split(":", 1)[1]
                        try:
                            genre_hints_from_gemini = [int(gid.strip()) for gid in ids_str.split(',') if gid.strip()]
                        except ValueError:
                            print("⚠️ Gemini sugeriu IDs de gênero em formato inválido.") # User-facing: Portuguese
                
                if search_terms_from_gemini != {original_interest_query}: # Check if new terms were added
                    print(f"💡 Termos de busca (original + Gemini): {search_terms_from_gemini}") # User-facing: Portuguese
                if genre_hints_from_gemini:
                    print(f"💡 IDs de Gênero sugeridos por Gemini: {genre_hints_from_gemini}") # User-facing: Portuguese
            else:
                print("⚠️ Gemini não forneceu análise utilizável.") # User-facing: Portuguese
        except Exception as e:
            print(f"🔴 Erro durante a análise de interesses com Gemini: {e}.") # User-facing: Portuguese
    else:
        print("ℹ️ Modelo Gemini não disponível. Usando apenas a consulta de interesse original.") # User-facing: Portuguese

    # ETAPA 2: Busca no TMDb usando /search/multi com os termos coletados (original + Gemini)
    print(f"\nETAPA 2: Tentando /search/multi com termos de busca...") # User-facing: Portuguese
    # Limit to a few search terms to manage API calls
    search_queries_to_try = list(search_terms_from_gemini)[:3] # Max 3 search strings for this step

    for page_num in range(1, 3): # Try to fetch first 2 pages
        if len(all_prospects_map) >= 30 : break # Stop if we have enough prospects
        for term_query in search_queries_to_try:
            if not term_query: continue
            # print(f"  -> Buscando página {page_num} no TMDb /search/multi por: '{term_query}'") # Debug
            search_params = {
                'query': term_query, 'include_adult': 'false',
                'language': TARGET_LANGUAGE_TMDB, 'region': country_code, 'page': page_num
            }
            data = make_tmdb_request("/search/multi", params=search_params)
            if data and 'results' in data:
                for item in data['results']:
                    media_type = item.get('media_type')
                    if media_type in ['movie', 'tv']:
                        title = item.get('title') if media_type == 'movie' else item.get('name')
                        tmdb_id = item.get('id')
                        overview = item.get('overview', '')
                        if title and tmdb_id and len(overview) > 10 and tmdb_id not in all_prospects_map:
                            all_prospects_map[tmdb_id] = {
                                'tmdb_id': tmdb_id, 'title': title, 'media_type': media_type,
                                'overview': overview, 'popularity': item.get('popularity', 0.0)
                            }
            if not data or not data.get('results'): break # Stop fetching pages for this term if no more results

    # ETAPA 3: Se /search/multi rendeu poucos resultados, tentar /discover com GÊNEROS sugeridos por Gemini
    if len(all_prospects_map) < 15 and genre_hints_from_gemini: # Threshold reduced to 15
        print(f"\nETAPA 3: Buscas anteriores renderam {len(all_prospects_map)} resultados. Tentando /discover com GÊNEROS do Gemini: {genre_hints_from_gemini}...") # User-facing: Portuguese
        genre_ids_str = '|'.join(map(str, genre_hints_from_gemini)) # OR logic for genres
        for page_num in range(1, 3): # Try to fetch first 2 pages
            if len(all_prospects_map) >= 30 : break
            for media_type_to_discover in ['movie', 'tv']:
                discover_params = {
                    'with_genres': genre_ids_str, 'include_adult': 'false',
                    'language': TARGET_LANGUAGE_TMDB, 'region': country_code,
                    'sort_by': 'popularity.desc', 'vote_count.gte': 20, # Min 20 votes
                    'page': page_num
                }
                data = make_tmdb_request(f"/discover/{media_type_to_discover}", params=discover_params)
                if data and 'results' in data:
                    for item in data['results']:
                        title = item.get('title') if media_type_to_discover == 'movie' else item.get('name')
                        tmdb_id = item.get('id')
                        overview = item.get('overview', '')
                        if title and tmdb_id and len(overview) > 10 and tmdb_id not in all_prospects_map:
                            all_prospects_map[tmdb_id] = {
                                'tmdb_id': tmdb_id, 'title': title, 'media_type': media_type_to_discover,
                                'overview': overview, 'popularity': item.get('popularity', 0.0)
                            }
                if not data or not data.get('results'): break 
            if not data or not data.get('results'): break # If one media type has no more pages, stop for this genre search

    # ETAPA 4: Fallback por Gêneros Populares para a Idade, se ainda poucos resultados
    if len(all_prospects_map) < 10: # Threshold reduced to 10
        print(f"\nETAPA 4: Buscas anteriores renderam {len(all_prospects_map)} resultados. Tentando /discover por GÊNEROS populares genéricos para a idade...") # User-facing: Portuguese
        genre_ids_for_fallback = []
        if child_age <= 7: genre_ids_for_fallback = [16, 10751]  # Animation, Family
        elif child_age <= 12: genre_ids_for_fallback = [10751, 12, 16, 35] # Family, Adventure, Animation, Comedy
        else: genre_ids_for_fallback = [12, 14, 878, 35, 18] # Adventure, Fantasy, Sci-Fi, Comedy, Drama

        if genre_ids_for_fallback:
            genre_ids_str = '|'.join(map(str, genre_ids_for_fallback))
            for page_num in range(1,3): # Try to fetch first 2 pages
                if len(all_prospects_map) >= 30 : break
                for media_type_to_discover in ['movie', 'tv']:
                    discover_params = {
                        'with_genres': genre_ids_str, 'include_adult': 'false',
                        'language': TARGET_LANGUAGE_TMDB, 'region': country_code,
                        'sort_by': 'popularity.desc', 'vote_count.gte': 50,
                        'page': page_num
                    }
                    data = make_tmdb_request(f"/discover/{media_type_to_discover}", params=discover_params)
                    if data and 'results' in data:
                        for item in data['results']:
                            title = item.get('title') if media_type_to_discover == 'movie' else item.get('name')
                            tmdb_id = item.get('id')
                            overview = item.get('overview', '')
                            if title and tmdb_id and len(overview) > 10 and tmdb_id not in all_prospects_map:
                                all_prospects_map[tmdb_id] = {
                                    'tmdb_id': tmdb_id, 'title': title, 'media_type': media_type_to_discover,
                                    'overview': overview, 'popularity': item.get('popularity', 0.0)
                                }
                    if not data or not data.get('results'): break
                if not data or not data.get('results'): break


    final_prospects_list = sorted(list(all_prospects_map.values()), key=lambda x: x['popularity'], reverse=True)[:30]

    if final_prospects_list:
        print(f"✅ Encontrados {len(final_prospects_list)} prospectos únicos no TMDb após todas as estratégias (ordenados por popularidade).") # User-facing: Portuguese
    else:
        print(f"⚠️  Nenhum prospecto inicial encontrado no TMDb para a consulta: '{user_context['interests_query']}' mesmo após todas as tentativas.") # User-facing: Portuguese
    return final_prospects_list

def agent_detailed_enrichment(prospects_list, country_code_target):
    # Agent 3: Enriches prospects with details like genres, TMDb rating, and country-specific age certification.
    print("\n--- 🧩 Agente 3: Enriquecimento Detalhado (Buscando Detalhes e Classificação Etária) ---") # User-facing: Portuguese
    if not TMDB_API_KEY or not prospects_list: return []
    enriched_prospects = []
    for prospect in prospects_list:
        # print(f"Enriching '{prospect['title']}' (ID: {prospect['tmdb_id']}, Type: {prospect['media_type']})...") # Debug
        endpoint = f"/{prospect['media_type']}/{prospect['tmdb_id']}"
        append_param = "release_dates" if prospect['media_type'] == 'movie' else "content_ratings"
        details = make_tmdb_request(endpoint, params={'append_to_response': append_param, 'language': TARGET_LANGUAGE_TMDB})
        if not details:
            # print(f"  Pulando '{prospect['title']}' - falha ao buscar detalhes.") # Debug
            continue
        enriched_item = prospect.copy()
        enriched_item['genres'] = [genre['name'] for genre in details.get('genres', [])]
        enriched_item['tmdb_vote_average'] = details.get('vote_average', 0.0)
        enriched_item['tmdb_vote_count'] = details.get('vote_count', 0)
        age_certification_in_country = "N/A"
        if prospect['media_type'] == 'movie' and 'release_dates' in details:
            for release_region_info in details['release_dates'].get('results', []):
                if release_region_info.get('iso_3166_1') == country_code_target:
                    if release_region_info.get('release_dates'):
                        for date_entry in release_region_info['release_dates']:
                            cert = date_entry.get('certification')
                            if cert and cert.strip() and date_entry.get('type') in [3, 4, 5, 6]: 
                                age_certification_in_country = cert.strip()
                                break
                        if age_certification_in_country != "N/A": break
        elif prospect['media_type'] == 'tv' and 'content_ratings' in details:
            for rating_region_info in details['content_ratings'].get('results', []):
                if rating_region_info.get('iso_3166_1') == country_code_target:
                    cert = rating_region_info.get('rating')
                    if cert and cert.strip():
                        age_certification_in_country = cert.strip()
                        break
        enriched_item['age_certification_country'] = age_certification_in_country
        enriched_prospects.append(enriched_item)
        # print(f"  -> Gêneros: {enriched_item['genres']}, Nota TMDb: {enriched_item['tmdb_vote_average']:.1f} ({enriched_item['tmdb_vote_count']} votos), Class. Etária ({country_code_target}): {age_certification_in_country}") # Debug
    print("✅ Processo de enriquecimento completo.") # User-facing: Portuguese
    return enriched_prospects

def agent_streaming_availability_verifier(enriched_prospects_list, user_context_details):
    # Agent 4: Checks streaming availability on user's preferred platforms in their country.
    print("\n--- 📺 Agente 4: Verificador de Disponibilidade em Streaming ---") # User-facing: Portuguese
    if not TMDB_API_KEY or not enriched_prospects_list: return []
    target_country_code = user_context_details['country_code']
    user_preferred_platform_names_clean = user_context_details['preferred_platform_names']
    target_provider_ids_map = {}
    for platform_name_clean in user_preferred_platform_names_clean:
        provider_id = get_tmdb_provider_id_from_name(platform_name_clean, watch_region=target_country_code)
        if provider_id:
            target_provider_ids_map[platform_name_clean] = provider_id
    if not target_provider_ids_map:
        print(f"⚠️  Não foi possível mapear nenhuma das suas plataformas preferidas ({', '.join(user_preferred_platform_names_clean)}) para IDs conhecidos do TMDb. Não é possível verificar o streaming com precisão.") # User-facing: Portuguese
    # print(f"Verificando disponibilidade nas plataformas reconhecidas (IDs: {list(target_provider_ids_map.values())}) em {target_country_code}") # Debug
    prospects_with_streaming_info = []
    for item in enriched_prospects_list:
        # print(f"Verificando streaming para '{item['title']}'...") # Debug
        item_copy = item.copy()
        item_copy['available_on_user_platforms'] = []
        providers_data = make_tmdb_request(f"/{item['media_type']}/{item['tmdb_id']}/watch/providers")
        if providers_data and 'results' in providers_data and target_country_code in providers_data['results']:
            country_specific_providers = providers_data['results'][target_country_code]
            if 'flatrate' in country_specific_providers:
                for tmdb_provider_info in country_specific_providers['flatrate']:
                    tmdb_provider_id = tmdb_provider_info.get('provider_id')
                    tmdb_provider_name_from_api = tmdb_provider_info.get('provider_name')
                    if tmdb_provider_id in target_provider_ids_map.values():
                        item_copy['available_on_user_platforms'].append(tmdb_provider_name_from_api)
        if item_copy['available_on_user_platforms']:
            item_copy['available_on_user_platforms'] = sorted(list(set(item_copy['available_on_user_platforms'])))
            # print(f"  -> ✅ Disponível em: {', '.join(item_copy['available_on_user_platforms'])}") # Debug
        # else: # Commented out for less verbose output
            # print(f"  -> ℹ️ Não encontrado nos seus serviços de streaming preferidos em {target_country_code} (ou sem mapeamento para seus serviços).") # User-facing: Portuguese
        prospects_with_streaming_info.append(item_copy)
    print("✅ Verificação de disponibilidade em streaming completa.") # User-facing: Portuguese
    return prospects_with_streaming_info

def agent_recommendation_selector_and_justifier(fully_enriched_prospects, user_context_data):
    # Agent 5: Filters to suitable & available items, selects top recommendations, and gets Gemini justification.
    print("\n--- ⭐ Agente 5: Seletor de Recomendações e Justificador ---") # User-facing: Portuguese
    if not fully_enriched_prospects:
        print("⚠️  Nenhum prospecto disponível para selecionar.") # User-facing: Portuguese
        return []
    child_s_age = user_context_data['age']
    target_country = user_context_data['country_code'] 
    suitable_and_available_options = []
    for item in fully_enriched_prospects:
        if not item.get('available_on_user_platforms'):
            continue
        certification_str = item.get('age_certification_country', "N/A").upper()
        is_age_appropriate_for_child = False
        # Simplified Age Appropriateness Logic for POC - focusing on BR
        if certification_str == "N/A" or certification_str == "NOT RATED" or certification_str == "UNRATED" or certification_str == "":
            is_age_appropriate_for_child = True # Assume parental discretion for unrated
        elif target_country == "BR": 
            if certification_str == "L" : is_age_appropriate_for_child = True
            elif certification_str.startswith("AL") : is_age_appropriate_for_child = True
            elif certification_str == "10" and child_s_age >= 10: is_age_appropriate_for_child = True
            elif certification_str == "12" and child_s_age >= 12: is_age_appropriate_for_child = True
            elif certification_str == "14" and child_s_age >= 14: is_age_appropriate_for_child = True
            elif certification_str == "16" and child_s_age >= 16: is_age_appropriate_for_child = True
            elif certification_str == "18" and child_s_age >= 18: is_age_appropriate_for_child = True
            else: is_age_appropriate_for_child = False 
        else: 
            is_age_appropriate_for_child = certification_str == "N/A" # Default for other countries
        
        if not is_age_appropriate_for_child:
            continue
        suitable_and_available_options.append(item)

    if not suitable_and_available_options:
        print("⚠️  Nenhuma recomendação encontrada que seja apropriada para a idade (baseado na lógica da POC) e disponível em suas plataformas.") # User-facing: Portuguese
        return []
    
    # Select top 2-3 recommendations after all filters
    recommendations_to_justify = sorted(suitable_and_available_options, key=lambda x: x.get('popularity', 0.0), reverse=True)[:3] 
    final_recommendations_with_text = []

    if not gemini_model:
        print("⚠️  Modelo Gemini não disponível. Pulando justificativas.") # User-facing: Portuguese
        for rec in recommendations_to_justify:
             rec['gemini_justification'] = "Justificativa não disponível (API do Gemini não configurada)." # User-facing: Portuguese
             final_recommendations_with_text.append(rec)
        return final_recommendations_with_text

    for rec_item in recommendations_to_justify:
        print(f"🤖 Gerando justificativa com Gemini para '{rec_item['title']}'...") # User-facing: Portuguese
        try:
            platforms_str = ', '.join(rec_item['available_on_user_platforms']) if rec_item['available_on_user_platforms'] else "serviços de streaming selecionados"
            genres_str = ', '.join(rec_item['genres']) if rec_item['genres'] else "diversos gêneros interessantes"
            # Prompt for Gemini: Portuguese
            prompt_for_gemini = (
                f"O usuário é um pai/mãe no Brasil (código do país: {user_context_data['country_code']}) procurando um(a) {rec_item['media_type']} para seu/sua filho(a) de {user_context_data['age']} anos. "
                f"A criança está interessada em: '{user_context_data['interests_query']}'.\n"
                f"Encontrei a seguinte opção: '{rec_item['title']}'.\n"
                f"Sinopse breve: {rec_item['overview']}\n"
                f"Gêneros: {genres_str}.\n"
                f"Nota dos usuários no TMDb: {rec_item['tmdb_vote_average']:.1f}/10 ({rec_item['tmdb_vote_count']} votos).\n"
                f"A classificação indicativa no Brasil ({user_context_data['country_code']}) é '{rec_item['age_certification_country']}'.\n"
                f"Está disponível em: {platforms_str}.\n\n"
                f"Por favor, escreva um parágrafo curto (2-3 frases), amigável e envolvente para o pai/mãe. "
                f"Explique por que '{rec_item['title']}' poderia ser uma ótima escolha para a criança hoje, considerando sua idade e interesses. "
                f"Destaque um ou dois aspectos positivos (ex: dos gêneros, temas da sinopse ou seu apelo geral). "
                f"Sutilmente encoraje-os a assistir em um dos serviços mencionados. Soe entusiasmado e prestativo. "
                f"Não repita a sinopse literalmente. Mantenha conciso e em português do Brasil."
            )
            response = gemini_model.generate_content(prompt_for_gemini)
            if hasattr(response, 'text') and response.text:
                rec_item['gemini_justification'] = response.text.strip()
            elif hasattr(response, 'parts') and response.parts: # Handle multi-part responses if any
                rec_item['gemini_justification'] = "".join(part.text for part in response.parts if hasattr(part, 'text')).strip()
            else:
                print(f"⚠️  Resposta do Gemini para '{rec_item['title']}' vazia ou em formato inesperado.") # User-facing: Portuguese
                rec_item['gemini_justification'] = f"'{rec_item['title']}' parece uma boa opção com base nos seus critérios! Você pode encontrá-lo em {platforms_str}." # User-facing: Portuguese
        except Exception as e:
            print(f"🔴 Erro durante a justificativa com Gemini para '{rec_item['title']}': {e}") # User-facing: Portuguese
            rec_item['gemini_justification'] = f"Não foi possível gerar uma justificativa detalhada devido a um erro, mas '{rec_item['title']}' parece promissor e está em {platforms_str}!" # User-facing: Portuguese
        final_recommendations_with_text.append(rec_item)
    print("✅ Recomendações selecionadas e tentativas de justificativas completas.") # User-facing: Portuguese
    return final_recommendations_with_text

def agent_existence_verifier(recommendations_list, user_context_details):
    # Optional Agent: Verifies title existence and relevance using Google Search via Gemini.
    print("\n--- 🤔 Agente Extra: Verificador de Existência e Relevância (Consultando Gemini com Pesquisa Google) ---") # User-facing: Portuguese
    if not gemini_model or not recommendations_list:
        if not gemini_model: print("⚠️  Modelo Gemini não disponível. Pulando verificação de existência.") # User-facing: Portuguese
        return recommendations_list 

    verified_recommendations = []
    for rec_item in recommendations_list:
        title_to_check = rec_item['title']
        media_type_to_check = rec_item['media_type']
        platform_to_check_mention = rec_item['available_on_user_platforms'][0] if rec_item['available_on_user_platforms'] else "alguma plataforma de streaming"

        # print(f"Verificando '{title_to_check}' ({media_type_to_check})...") # Debug
        
        try:
            # Prompt for Gemini: Portuguese
            prompt_for_verification = (
                f"Com base em informações da Pesquisa Google, o {media_type_to_check} chamado '{title_to_check}' "
                f"é um título real e conhecido? Ele parece ser adequado para uma criança de {user_context_details['age']} anos interessada em '{user_context_details['interests_query']}'? "
                f"Além disso, há alguma menção de que esteja disponível em '{platform_to_check_mention}' no Brasil? "
                f"Responda sobre a existência (SIM/NÃO/INCERTO). Se SIM, comente brevemente sobre a adequação à idade/interesse e sobre a plataforma se houver dados claros. Responda em português do Brasil."
                f"Exemplo se existir e for adequado: SIM. Parece ser um {media_type_to_check} conhecido e adequado. Encontrado em {platform_to_check_mention}."
                f"Exemplo se existir mas não adequado: SIM. Existe, mas pode não ser ideal para a idade/interesse."
                f"Exemplo se não existir: NÃO. Não encontrei informações consistentes sobre este título."
            )
            response = gemini_model.generate_content(prompt_for_verification)
            verification_text = ""
            if hasattr(response, 'text') and response.text:
                verification_text = response.text.strip() 
            elif hasattr(response, 'parts') and response.parts:
                verification_text = "".join(part.text for part in response.parts if hasattr(part, 'text')).strip()

            # print(f"  -> Resposta da verificação Gemini: '{verification_text}'") # Debug

            if "SIM" in verification_text.upper() or title_to_check.lower() in verification_text.lower():
                if "NÃO SER IDEAL" in verification_text.upper() or "NÃO ADEQUADO" in verification_text.upper() or "NÃO RECOMENDADO PARA A IDADE" in verification_text.upper():
                    # print(f"  -> 🟡 '{title_to_check}' existe, mas Gemini indicou que pode não ser adequado. Removendo por precaução.") # Debug
                    pass # Skip adding to verified_recommendations
                else:
                    # print(f"  -> ✅ '{title_to_check}' parece existir e/ou ser relevante.") # Debug
                    rec_item['existence_verified_by_gemini'] = True
                    if platform_to_check_mention.lower() in verification_text.lower() or "ENCONTRADO EM" in verification_text.upper() or "DISPONÍVEL EM" in verification_text.upper():
                        rec_item['platform_mention_verified_by_gemini'] = True
                        # print(f"  -> ✅ Menção à plataforma '{platform_to_check_mention}' encontrada por Gemini.") # Debug
                    verified_recommendations.append(rec_item)
            elif "INCERTO" in verification_text.upper():
                # print(f"  -> ⚠️  Existência de '{title_to_check}' é INCERTA segundo Gemini. Mantendo por ora, mas requer atenção.") # Debug
                rec_item['existence_verified_by_gemini'] = "INCERTO"
                verified_recommendations.append(rec_item) 
            # else: # Assumes NO or inconclusive, item is dropped
                # print(f"  -> ❌ '{title_to_check}' parece NÃO existir ou não foi confirmado pelo Gemini. Removendo.") # Debug
        
        except Exception as e:
            print(f"🔴 Erro durante a verificação de existência com Gemini para '{title_to_check}': {e}") # User-facing: Portuguese
            rec_item['existence_verified_by_gemini'] = "ERRO_NA_VERIFICACAO"
            verified_recommendations.append(rec_item) 

    if not verified_recommendations and recommendations_list: 
        print("⚠️  Nenhuma recomendação pôde ser verificada com confiança pelo Gemini, ou todas foram consideradas não existentes/adequadas. Verifique as recomendações originais do TMDb com cautela.") # User-facing: Portuguese
        for rec in recommendations_list:
            rec['existence_verified_by_gemini'] = "NÃO_VERIFICADO_GEMINI_FALHOU_EM_TODOS"
        return recommendations_list
        
    print("✅ Verificação de existência e relevância (com Gemini) completa.") # User-facing: Portuguese
    return verified_recommendations

def agent_console_display_final(final_recommendations_list, original_user_context):
    # Agent 6: Displays the final, justified recommendations to the user.
    print("\n--- 🎬 Agente 6: Exibição Final das Recomendações ---") # User-facing: Portuguese
    if not final_recommendations_list:
        print("\n😢 Desculpe, não consegui encontrar recomendações que correspondessem perfeitamente a todos os seus critérios desta vez. "
              "Talvez tente uma consulta de interesse um pouco diferente, verifique mais plataformas de streaming ou uma idade diferente, se apropriado.") # User-facing: Portuguese
        return
    print(f"\n✨ Aqui estão algumas sugestões personalizadas para sua criança de {original_user_context['age']} anos, "
          f"interessada em '{original_user_context['interests_query']}', no Brasil ({original_user_context['country_code']}): ✨") # User-facing: Portuguese
    
    for i, rec in enumerate(final_recommendations_list):
        print(f"\n--- Recomendação #{i+1} ---") # User-facing: Portuguese
        print(f"📺 Título: {rec['title']} ({rec['media_type'].upper()})") # User-facing: Portuguese
        print(f"⭐ Nota TMDb: {rec.get('tmdb_vote_average', 'N/A'):.1f}/10 ({rec.get('tmdb_vote_count', 0)} votos)") # User-facing: Portuguese
        print(f"🔞 Classificação Indicativa ({original_user_context['country_code']}): {rec.get('age_certification_country', 'N/A')}") # User-facing: Portuguese
        print(f"🎭 Gêneros: {', '.join(rec.get('genres', ['Não especificado']))}") # User-facing: Portuguese
        print(f"📜 Sinopse: {rec.get('overview', 'Sinopse não disponível.')}") # User-facing: Portuguese
        
        if rec.get('available_on_user_platforms'):
            print(f"💻 Disponível em suas plataformas: {', '.join(rec.get('available_on_user_platforms'))}") # User-facing: Portuguese
        else:
            print(f"💻 Disponibilidade em suas plataformas preferidas: Não confirmado na sua lista especificada.") # User-facing: Portuguese
            
        print(f"\n💡 Por que esta pode ser uma ótima escolha:") # User-facing: Portuguese
        print(f"{rec.get('gemini_justification', 'Nenhuma justificativa específica gerada.')}") # User-facing: Portuguese
    
    print("\n" + "="*50)
    print("Lembre-se de sempre usar seu próprio julgamento e verificar os avisos de conteúdo ao selecionar para sua criança. Aproveitem o filme/série! 🎉") # User-facing: Portuguese

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    print("🎬 Bem-vindo à POC do Selecionador de Filmes (Backend Python)! 🎬") # User-facing: Portuguese
    if not TMDB_API_KEY: 
        print("\n🔴 CRÍTICO: TMDB_API_KEY está ausente. Esta aplicação depende fortemente do TMDb. Por favor, defina-a no seu arquivo .env e reinicie.") # User-facing: Portuguese
    else:
        user_context = agent_user_context_collector()
        initial_prospects = agent_content_prospector(user_context)
        
        final_recommendations = [] 
        if initial_prospects:
            enriched_prospects = agent_detailed_enrichment(initial_prospects, user_context['country_code'])
            prospects_with_streaming = agent_streaming_availability_verifier(enriched_prospects, user_context)
            selected_and_justified_recs = agent_recommendation_selector_and_justifier(prospects_with_streaming, user_context)
            
            if selected_and_justified_recs:
                final_recommendations = agent_existence_verifier(selected_and_justified_recs, user_context)
            # else: # No need for this 'else', final_recommendations is already []
                # final_recommendations = [] 
        else:
            print("\nNenhum filme ou série inicial encontrado com base na sua consulta. Os agentes subsequentes não serão executados.") # User-facing: Portuguese
            
        agent_console_display_final(final_recommendations, user_context)

    print("\n👋 POC do Selecionador de Filmes finalizada. Até logo!") # User-facing: Portuguese