# movie_picker_poc/main.py

import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import json

# --- CONFIGURATION ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

gemini_model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("✅ API do Gemini configurada com sucesso.")
    except Exception as e:
        print(f"🔴 Erro ao configurar a API do Gemini: {e}. Funcionalidades do Gemini serão puladas.")
else:
    print("⚠️ GEMINI_API_KEY não encontrada no arquivo .env. Funcionalidades do Gemini serão puladas.")

if not TMDB_API_KEY:
    print("🔴 TMDB_API_KEY não encontrada no arquivo .env. Funcionalidades do TMDb não funcionarão. Por favor, configure-a e reinicie.")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TARGET_COUNTRY_CODE = "BR" # Hardcoded for Brazil
TARGET_LANGUAGE_TMDB = "pt-BR" # For TMDb results in Portuguese

# --- HELPER FUNCTIONS --- (make_tmdb_request remains mostly the same, ensure 'language' can be passed or is defaulted to TARGET_LANGUAGE_TMDB)

def make_tmdb_request(endpoint, params=None, method="GET"):
    if not TMDB_API_KEY:
        print("ℹ️ Chave da API do TMDb não disponível. Pulando requisição ao TMDb.")
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
            print(f"🔴 Método HTTP não suportado: {method}")
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try:
            error_details = response.json()
        except ValueError:
            error_details = response.text[:200]
        print(f"🔴 Erro HTTP ao fazer requisição ao TMDb para {endpoint}: {http_err} - Status: {response.status_code}, Resposta: {error_details}")
    except requests.exceptions.RequestException as e:
        print(f"🔴 Erro geral ao fazer requisição ao TMDb para {endpoint}: {e}")
    return None

# get_tmdb_provider_id_from_name remains useful, ensure it has Brazilian providers
def get_tmdb_provider_id_from_name(provider_name_input, media_type="all", watch_region="BR"): # Default region BR
    provider_name_lower = provider_name_input.lower().strip()
    common_provider_map = {
        "netflix": 8, "amazon prime video": 9, "prime video": 9, "amazon video": 9,
        "disney plus": 337, "disney+": 337, "max": 1899, "hbo max": 384, # Keep HBO Max for older entries
        "apple tv plus": 350, "appletv+": 350, "apple tv+": 350,
        "globoplay": 307, "star plus": 619, "star+": 619, "claro video": 167,
        "looke": 484, "paramount plus": 531, "paramount+": 531,
    }
    return common_provider_map.get(provider_name_lower)

# --- AGENT FUNCTION DEFINITIONS ---

def agent_user_context_collector():
    print("\n--- 🙋 Agente 1: Coletor de Contexto do Usuário ---")
    while True:
        try:
            age_str = input("➡️ Digite a idade da criança (ex: 5, 8, 12): ")
            age = int(age_str)
            if 1 <= age <= 18: break
            else: print("⚠️ Por favor, digite uma idade válida entre 1 e 18.")
        except ValueError: print("⚠️ Entrada inválida. Por favor, digite um número para a idade.")

    interests_query = input("➡️ Quais são os interesses da criança hoje (ex: 'animação divertida com animais falantes', 'filmes de aventura espacial')? ")
    if not interests_query.strip():
        print("ℹ️ Nenhum interesse específico fornecido. Buscando por conteúdo popular infantil.")
        interests_query = "filmes infantis populares animação família"

    platforms_input_str = input("➡️ Digite as plataformas de streaming preferidas, separadas por vírgula (ex: 'Netflix, Disney Plus, Globoplay'): ")
    preferred_platform_names_cleaned = [p.strip().lower() for p in platforms_input_str.split(',') if p.strip()]
    
    # print("✅ Contexto coletado. País definido como Brasil.")
    return {
        "age": age,
        "interests_query": interests_query,
        "preferred_platform_names": preferred_platform_names_cleaned,
        "country_code": TARGET_COUNTRY_CODE # Hardcoded
    }

def get_keyword_ids_from_tmdb(keyword_query_list):
    """Busca IDs de palavras-chave no TMDb para uma lista de strings de consulta."""
    if not TMDB_API_KEY: return []
    keyword_ids = set() # Usar um set para evitar IDs duplicados
    print(f"  -> Buscando IDs de palavras-chave no TMDb para: {keyword_query_list}")
    for query in keyword_query_list:
        if not query.strip(): continue
        params = {'query': query.strip(), 'page': 1}
        data = make_tmdb_request("/search/keyword", params=params)
        if data and 'results' in data and data['results']:
            # Pega o ID da primeira palavra-chave correspondente mais relevante
            # Poderia pegar mais, mas para o POC, o primeiro é um bom começo.
            for res in data['results'][:2]: # Pega os 2 primeiros resultados para ter mais chance
                keyword_ids.add(res['id'])
                print(f"    Encontrado ID de palavra-chave: {res['id']} para '{res['name']}' (de '{query}')")
    return list(keyword_ids)

def agent_content_prospector(user_context):
    """Agente 2: Busca conteúdo no TMDb usando múltiplas estratégias para garantir resultados."""
    print("\n--- 🔎 Agente 2: Investigador de Conteúdo (Estratégias Múltiplas no TMDb) ---")
    if not TMDB_API_KEY: return []

    original_interest_query = user_context['interests_query']
    child_age = user_context['age']
    country_code = user_context['country_code']
    
    all_prospects_map = {} # Usar um dicionário para prospectos únicos por ID

    # --- Estratégia 1: Expansão de Interesses com Gemini e Busca por Palavras-chave no TMDb /discover ---
    print("ETAPA 1: Tentando busca por palavras-chave (Keywords) com expansão do Gemini...")
    search_terms_for_keywords = {original_interest_query}
    if gemini_model:
        print(f"🧠 Consultando o Gemini para expandir o interesse: '{original_interest_query}'...")
        try:
            # (Mesma lógica de expansão com Gemini que você tinha antes)
            prompt_for_gemini_expansion = (
                f"Uma criança no Brasil está interessada em '{original_interest_query}'. "
                f"Sugira de 2 a 3 palavras-chave ou frases curtas, diversas mas relacionadas, que seriam boas para buscar filmes ou séries sobre esse tema no TMDb. "
                f"Foque em termos que o TMDb provavelmente entenderia. Não inclua o termo original na sua resposta."
                f"Forneça apenas as palavras-chave/frases separadas por vírgula."
            )
            response = gemini_model.generate_content(prompt_for_gemini_expansion)
            if hasattr(response, 'text') and response.text:
                additional_terms = [term.strip() for term in response.text.split(',') if term.strip()]
                if additional_terms:
                    for term in additional_terms: search_terms_for_keywords.add(term)
                    print(f"💡 Gemini sugeriu termos adicionais. Conjunto para buscar keywords: {search_terms_for_keywords}")
            else: print("⚠️ Gemini não forneceu expansão utilizável.")
        except Exception as e: print(f"🔴 Erro durante a expansão de interesses com Gemini: {e}.")
    
    keyword_ids_to_use = get_keyword_ids_from_tmdb(list(search_terms_for_keywords))
    
    if keyword_ids_to_use:
        print(f"  -> Usando /discover do TMDb com IDs de palavras-chave: {keyword_ids_to_use}")
        keyword_ids_str = '|'.join(map(str, keyword_ids_to_use)) 
        
        for media_type_to_discover in ['movie', 'tv']:
            # print(f"    Buscando {media_type_to_discover} com keywords...") # Menos verboso
            discover_params = {
                'with_keywords': keyword_ids_str, 'include_adult': 'false',
                'language': TARGET_LANGUAGE_TMDB, 'region': country_code,
                'sort_by': 'popularity.desc', 'page': 1
            }
            data = make_tmdb_request(f"/discover/{media_type_to_discover}", params=discover_params)
            if data and 'results' in data:
                for item in data['results']:
                    title = item.get('title') if media_type_to_discover == 'movie' else item.get('name')
                    tmdb_id = item.get('id')
                    overview = item.get('overview', '')
                    if title and tmdb_id and len(overview) > 10 and tmdb_id not in all_prospects_map: # Overview > 10
                        all_prospects_map[tmdb_id] = {
                            'tmdb_id': tmdb_id, 'title': title, 'media_type': media_type_to_discover,
                            'overview': overview, 'popularity': item.get('popularity', 0.0)
                        }
    else:
        print("  -> Nenhum ID de palavra-chave encontrado ou usado para a busca /discover.")

    # --- Estratégia 2: Busca por String Direta no TMDb /search/multi ---
    # Executar se a Estratégia 1 rendeu poucos resultados (ex: menos de 5)
    if len(all_prospects_map) < 5:
        print(f"\nETAPA 2: Busca por keywords rendeu {len(all_prospects_map)} resultados. Tentando /search/multi com termos originais/expandidos...")
        search_terms_list = list(search_terms_for_keywords)[:3] # Limitar a 3 termos de busca por string
        for term in search_terms_list:
            if not term: continue
            print(f"  -> Buscando no TMDb /search/multi por: '{term}'")
            search_params = {
                'query': term, 'include_adult': 'false',
                'language': TARGET_LANGUAGE_TMDB, 'region': country_code, 'page': 1
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
    
    # --- Estratégia 3: Busca por Gêneros Populares para a Idade (Fallback Mais Genérico) ---
    # Executar se as estratégias anteriores ainda renderam poucos resultados (ex: menos de 3)
    if len(all_prospects_map) < 3:
        print(f"\nETAPA 3: Buscas anteriores renderam {len(all_prospects_map)} resultados. Tentando /discover por gêneros populares para a idade...")
        
        genre_ids_for_fallback = []
        if child_age <= 7:
            genre_ids_for_fallback = [16, 10751]  # Animação, Família
        elif child_age <= 12:
            genre_ids_for_fallback = [10751, 12, 16, 35] # Família, Aventura, Animação, Comédia
        else: # Adolescentes
            genre_ids_for_fallback = [12, 14, 878, 35] # Aventura, Fantasia, Ficção Científica, Comédia

        if genre_ids_for_fallback:
            genre_ids_str = '|'.join(map(str, genre_ids_for_fallback)) # OR entre os gêneros
            print(f"  -> Usando /discover do TMDb com IDs de GÊNERO (fallback): {genre_ids_str}")
            for media_type_to_discover in ['movie', 'tv']:
                # print(f"    Buscando {media_type_to_discover} com gêneros de fallback...") # Menos verboso
                discover_params = {
                    'with_genres': genre_ids_str, 'include_adult': 'false',
                    'language': TARGET_LANGUAGE_TMDB, 'region': country_code,
                    'sort_by': 'popularity.desc', 
                    'vote_count.gte': 50, # Tentar pegar filmes/séries com um mínimo de votos
                    'page': 1
                }
                # Adicionar filtro de certificação etária aqui se tivermos uma lista confiável para BR
                # Ex: discover_params['certification_country'] = 'BR'
                # Ex: discover_params['certification.lte'] = '10' (se a criança tiver 10 anos e '10' for uma classificação válida)

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
        else:
            print("  -> Nenhum gênero de fallback definido para esta faixa etária.")

    final_prospects_list = sorted(list(all_prospects_map.values()), key=lambda x: x['popularity'], reverse=True)[:10]

    if final_prospects_list:
        print(f"✅ Encontrados {len(final_prospects_list)} prospectos únicos no TMDb após todas as estratégias (ordenados por popularidade).")
    else:
        print(f"⚠️ Nenhum prospecto inicial encontrado no TMDb para a consulta: '{user_context['interests_query']}' mesmo após todas as tentativas.")
    return final_prospects_list

def agent_detailed_enrichment(prospects_list, country_code_target):
    print("\n--- 🧩 Agente 3: Enriquecimento Detalhado (Buscando Detalhes e Classificação Etária) ---")
    if not TMDB_API_KEY or not prospects_list: return []
    enriched_prospects = []
    for prospect in prospects_list:
        print(f"Enriquecendo '{prospect['title']}' (ID: {prospect['tmdb_id']}, Tipo: {prospect['media_type']})...")
        endpoint = f"/{prospect['media_type']}/{prospect['tmdb_id']}"
        append_param = "release_dates" if prospect['media_type'] == 'movie' else "content_ratings"
        details = make_tmdb_request(endpoint, params={'append_to_response': append_param, 'language': TARGET_LANGUAGE_TMDB}) # Using target language
        if not details:
            print(f"  Pulando '{prospect['title']}' - falha ao buscar detalhes.")
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
                            if cert and cert.strip() and date_entry.get('type') in [3, 4, 5, 6]: # Theatrical, Digital, Physical, TV Premiere
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
        print(f"  -> Gêneros: {enriched_item['genres']}, Nota TMDb: {enriched_item['tmdb_vote_average']:.1f} ({enriched_item['tmdb_vote_count']} votos), Class. Etária ({country_code_target}): {age_certification_in_country}")
    print("✅ Processo de enriquecimento completo.")
    return enriched_prospects

def agent_streaming_availability_verifier(enriched_prospects_list, user_context_details):
    print("\n--- 📺 Agente 4: Verificador de Disponibilidade em Streaming ---")
    if not TMDB_API_KEY or not enriched_prospects_list: return []
    target_country_code = user_context_details['country_code']
    user_preferred_platform_names_clean = user_context_details['preferred_platform_names']
    target_provider_ids_map = {}
    for platform_name_clean in user_preferred_platform_names_clean:
        provider_id = get_tmdb_provider_id_from_name(platform_name_clean, watch_region=target_country_code)
        if provider_id:
            target_provider_ids_map[platform_name_clean] = provider_id
    if not target_provider_ids_map:
        print(f"⚠️ Não foi possível mapear nenhuma das suas plataformas preferidas ({', '.join(user_preferred_platform_names_clean)}) para IDs conhecidos do TMDb. Não é possível verificar o streaming com precisão.")
    print(f"Verificando disponibilidade nas plataformas reconhecidas (IDs: {list(target_provider_ids_map.values())}) em {target_country_code}")
    prospects_with_streaming_info = []
    for item in enriched_prospects_list:
        print(f"Verificando streaming para '{item['title']}'...")
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
            print(f"  -> ✅ Disponível em: {', '.join(item_copy['available_on_user_platforms'])}")
        else:
            print(f"  -> ℹ️ Não encontrado nos seus serviços de streaming preferidos em {target_country_code} (ou sem mapeamento para seus serviços).")
        prospects_with_streaming_info.append(item_copy)
    print("✅ Verificação de disponibilidade em streaming completa.")
    return prospects_with_streaming_info

def agent_recommendation_selector_and_justifier(fully_enriched_prospects, user_context_data):
    print("\n--- ⭐ Agente 5: Seletor de Recomendações e Justificador ---")
    if not fully_enriched_prospects:
        print("⚠️ Nenhum prospecto disponível para selecionar.")
        return []
    child_s_age = user_context_data['age']
    target_country = user_context_data['country_code'] # Should be "BR"
    suitable_and_available_options = []
    for item in fully_enriched_prospects:
        if not item.get('available_on_user_platforms'):
            continue
        certification_str = item.get('age_certification_country', "N/A").upper()
        is_age_appropriate_for_child = False
        # Simplified Age Appropriateness Logic for POC - focusing on BR
        if certification_str == "N/A" or certification_str == "NOT RATED" or certification_str == "UNRATED" or certification_str == "":
            is_age_appropriate_for_child = True # Assume parental discretion
        elif target_country == "BR": # Brazil - Classificação Indicativa
            if certification_str == "L" : is_age_appropriate_for_child = True
            elif certification_str.startswith("AL") : is_age_appropriate_for_child = True
            elif certification_str == "10" and child_s_age >= 10: is_age_appropriate_for_child = True
            elif certification_str == "12" and child_s_age >= 12: is_age_appropriate_for_child = True
            elif certification_str == "14" and child_s_age >= 14: is_age_appropriate_for_child = True
            elif certification_str == "16" and child_s_age >= 16: is_age_appropriate_for_child = True
            elif certification_str == "18" and child_s_age >= 18: is_age_appropriate_for_child = True
            else: is_age_appropriate_for_child = False # If rated but not matching and not L, assume not appropriate
        else: # Fallback for other countries (though we hardcoded BR)
            is_age_appropriate_for_child = certification_str == "N/A"
        
        if not is_age_appropriate_for_child:
            continue
        suitable_and_available_options.append(item)

    if not suitable_and_available_options:
        print("⚠️ Nenhuma recomendação encontrada que seja apropriada para a idade (baseado na lógica simplificada da POC) e disponível em suas plataformas.")
        return []
    
    recommendations_to_justify = sorted(suitable_and_available_options, key=lambda x: x.get('popularity', 0.0), reverse=True)[:2] # Top 2
    final_recommendations_with_text = []

    if not gemini_model:
        print("⚠️ Modelo Gemini não disponível. Pulando justificativas.")
        for rec in recommendations_to_justify:
             rec['gemini_justification'] = "Justificativa não disponível (API do Gemini não configurada)."
             final_recommendations_with_text.append(rec)
        return final_recommendations_with_text

    for rec_item in recommendations_to_justify:
        print(f"🤖 Gerando justificativa com Gemini para '{rec_item['title']}'...")
        try:
            platforms_str = ', '.join(rec_item['available_on_user_platforms']) if rec_item['available_on_user_platforms'] else "serviços de streaming selecionados"
            genres_str = ', '.join(rec_item['genres']) if rec_item['genres'] else "diversos gêneros interessantes"
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
                f"Não repita a sinopse literalmente. Mantenha conciso."
            )
            response = gemini_model.generate_content(prompt_for_gemini)
            if hasattr(response, 'text') and response.text:
                rec_item['gemini_justification'] = response.text.strip()
            elif hasattr(response, 'parts') and response.parts:
                rec_item['gemini_justification'] = "".join(part.text for part in response.parts if hasattr(part, 'text')).strip()
            else:
                print(f"⚠️ Resposta do Gemini para '{rec_item['title']}' vazia ou em formato inesperado.")
                rec_item['gemini_justification'] = f"'{rec_item['title']}' parece uma boa opção com base nos seus critérios! Você pode encontrá-lo em {platforms_str}."
        except Exception as e:
            print(f"🔴 Erro durante a justificativa com Gemini para '{rec_item['title']}': {e}")
            rec_item['gemini_justification'] = f"Não foi possível gerar uma justificativa detalhada devido a um erro, mas '{rec_item['title']}' parece promissor e está em {platforms_str}!"
        final_recommendations_with_text.append(rec_item)
    print("✅ Recomendações selecionadas e tentativas de justificativas completas.")
    return final_recommendations_with_text

def agent_console_display_final(final_recommendations_list, original_user_context):
    print("\n--- 🎬 Agente 6: Exibição Final das Recomendações ---")
    if not final_recommendations_list:
        print("\n😢 Desculpe, não consegui encontrar recomendações que correspondessem perfeitamente a todos os seus critérios desta vez. "
              "Talvez tente uma consulta de interesse um pouco diferente, verifique mais plataformas de streaming ou uma idade diferente, se apropriado.")
        return
    print(f"\n✨ Aqui estão algumas sugestões personalizadas para sua criança de {original_user_context['age']} anos, "
          f"interessada em '{original_user_context['interests_query']}', no Brasil ({original_user_context['country_code']}): ✨")
    for i, rec in enumerate(final_recommendations_list):
        print(f"\n--- Recomendação #{i+1} ---")
        print(f"📺 Título: {rec['title']} ({rec['media_type'].upper()})")
        print(f"⭐ Nota TMDb: {rec.get('tmdb_vote_average', 'N/A'):.1f}/10 ({rec.get('tmdb_vote_count', 0)} votos)")
        print(f"🔞 Classificação Indicativa ({original_user_context['country_code']}): {rec.get('age_certification_country', 'N/A')}")
        print(f"🎭 Gêneros: {', '.join(rec.get('genres', ['Não especificado']))}")
        print(f"📜 Sinopse: {rec.get('overview', 'Sinopse não disponível.')}")
        if rec.get('available_on_user_platforms'):
            print(f"💻 Disponível em suas plataformas: {', '.join(rec.get('available_on_user_platforms'))}")
        else:
            print(f"💻 Disponibilidade em suas plataformas preferidas: Não confirmado na sua lista especificada.")
        print(f"\n💡 Por que esta pode ser uma ótima escolha:")
        print(f"{rec.get('gemini_justification', 'Nenhuma justificativa específica gerada.')}")
    print("\n" + "="*50)
    print("Lembre-se de sempre usar seu próprio julgamento e verificar os avisos de conteúdo ao selecionar para sua criança. Aproveitem o filme/série! 🎉")

def agent_existence_verifier(recommendations_list, user_context_details): # Nome da função mantido em inglês
    """Agente Opcional: Verifica a existência e relevância do título recomendado usando a Pesquisa Google via Gemini."""
    print("\n--- 🤔 Agente Extra: Verificador de Existência e Relevância (Consultando Gemini com Pesquisa Google) ---")
    if not gemini_model or not recommendations_list:
        if not gemini_model: print("⚠️ Modelo Gemini não disponível. Pulando verificação de existência.")
        return recommendations_list 

    verified_recommendations = []
    for rec_item in recommendations_list:
        title_to_check = rec_item['title']
        media_type_to_check = rec_item['media_type']
        # Pega a primeira plataforma da lista, se houver, para a verificação opcional.
        platform_to_check_mention = rec_item['available_on_user_platforms'][0] if rec_item['available_on_user_platforms'] else "alguma plataforma de streaming" # Alterado para ser mais genérico se não houver plataforma específica

        print(f"Verificando '{title_to_check}' ({media_type_to_check})...")
        
        try:
            prompt_for_verification = (
                f"Com base em informações da Pesquisa Google, o {media_type_to_check} chamado '{title_to_check}' "
                f"é um título real e conhecido? Ele parece ser adequado para uma criança de {user_context_details['age']} anos interessada em '{user_context_details['interests_query']}'? "
                f"Além disso, há alguma menção de que esteja disponível em '{platform_to_check_mention}' no Brasil? "
                f"Responda sobre a existência (SIM/NÃO/INCERTO). Se SIM, comente brevemente sobre a adequação à idade/interesse e sobre a plataforma se houver dados claros."
                f"Exemplo se existir e for adequado: SIM. Parece ser um {media_type_to_check} conhecido e adequado. Encontrado em {platform_to_check_mention}."
                f"Exemplo se existir mas não adequado: SIM. Existe, mas pode não ser ideal para a idade/interesse."
                f"Exemplo se não existir: NÃO. Não encontrei informações consistentes sobre este título."
            )
            
            response = gemini_model.generate_content(prompt_for_verification)
            
            verification_text = ""
            if hasattr(response, 'text') and response.text:
                verification_text = response.text.strip() # Não colocar em UPPER para analisar melhor
            elif hasattr(response, 'parts') and response.parts:
                verification_text = "".join(part.text for part in response.parts if hasattr(part, 'text')).strip()

            print(f"  -> Resposta da verificação Gemini: '{verification_text}'")

            # Lógica de interpretação mais branda
            if "SIM" in verification_text.upper() or title_to_check.lower() in verification_text.lower(): # Procura por SIM ou o próprio título na resposta
                if "NÃO SER IDEAL" in verification_text.upper() or "NÃO ADEQUADO" in verification_text.upper() or "NÃO RECOMENDADO PARA A IDADE" in verification_text.upper():
                    print(f"  -> 🟡 '{title_to_check}' existe, mas Gemini indicou que pode não ser adequado. Removendo por precaução.")
                else:
                    print(f"  -> ✅ '{title_to_check}' parece existir e/ou ser relevante.")
                    rec_item['existence_verified_by_gemini'] = True
                    # Se a plataforma foi mencionada positivamente
                    if platform_to_check_mention.lower() in verification_text.lower() or "ENCONTRADO EM" in verification_text.upper() or "DISPONÍVEL EM" in verification_text.upper():
                        rec_item['platform_mention_verified_by_gemini'] = True
                        print(f"  -> ✅ Menção à plataforma '{platform_to_check_mention}' encontrada por Gemini.")
                    verified_recommendations.append(rec_item)
            elif "INCERTO" in verification_text.upper():
                print(f"  -> ⚠️ Existência de '{title_to_check}' é INCERTA segundo Gemini. Mantendo por ora, mas requer atenção.")
                rec_item['existence_verified_by_gemini'] = "INCERTO"
                verified_recommendations.append(rec_item) 
            else: # Assume NÃO ou não conclusivo
                print(f"  -> ❌ '{title_to_check}' parece NÃO existir ou não foi confirmado pelo Gemini. Removendo.")
        
        except Exception as e:
            print(f"🔴 Erro durante a verificação de existência com Gemini para '{title_to_check}': {e}")
            rec_item['existence_verified_by_gemini'] = "ERRO_NA_VERIFICACAO"
            verified_recommendations.append(rec_item) # Mantém se a verificação falhar, mas com flag

    if not verified_recommendations and recommendations_list: # Se a lista ficou vazia mas havia recomendações antes
        print("⚠️ Nenhuma recomendação pôde ser verificada com confiança pelo Gemini, ou todas foram consideradas não existentes/adequadas. "
              "Verifique as recomendações originais do TMDb com cautela.")
        # Retorna a lista original que veio do TMDb se o verificador esvaziou tudo
        # Adiciona uma flag para o usuário saber que não foi verificada por Gemini
        for rec in recommendations_list:
            rec['existence_verified_by_gemini'] = "NÃO_VERIFICADO_GEMINI_FALHOU_EM_TODOS"
        return recommendations_list
        
    print("✅ Verificação de existência e relevância completa.")
    return verified_recommendations

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    print("🎬 Bem-vindo à POC do Selecionador de Filmes (Backend Python)! 🎬")
    if not TMDB_API_KEY:
        print("\n🔴 CRÍTICO: TMDB_API_KEY está ausente. Esta aplicação depende fortemente do TMDb. Por favor, defina-a no seu arquivo .env e reinicie.")
    else:
        user_context = agent_user_context_collector()
        initial_prospects = agent_content_prospector(user_context)
        
        final_recommendations = [] # Inicializa para o caso de não haver prospectos
        if initial_prospects:
            enriched_prospects = agent_detailed_enrichment(initial_prospects, user_context['country_code'])
            prospects_with_streaming = agent_streaming_availability_verifier(enriched_prospects, user_context)
            
            # Seleciona e justifica antes de verificar
            selected_and_justified_recs = agent_recommendation_selector_and_justifier(prospects_with_streaming, user_context)
            
            # Adiciona o novo agente verificador aqui
            if selected_and_justified_recs:
                final_recommendations = agent_existence_verifier(selected_and_justified_recs, user_context)
            else:
                final_recommendations = [] # Garante que está vazia se o passo anterior não retornou nada
        else:
            print("\nNenhum filme ou série inicial encontrado com base na sua consulta. Os agentes subsequentes não serão executados.")
            
        agent_console_display_final(final_recommendations, user_context)

    print("\n👋 POC do Selecionador de Filmes finalizada. Até logo!")