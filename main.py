# python-film-recommendation-agent/main.py

import os
import requests  # For making HTTP requests to TMDb
import google.generativeai as genai  # For Google Gemini API
from dotenv import load_dotenv  # To load API keys from .env file
import json  # To pretty print JSON for debugging if needed

# --- CONFIGURATION ---

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY") # This should be your TMDb API Key (v3 auth)

# Configure the Gemini API client
gemini_model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest') # Or your preferred model like 'gemini-pro'
        print("✅ Gemini API configured successfully.")
    except Exception as e:
        print(f"🔴 Error configuring Gemini API: {e}. Gemini features will be skipped.")
else:
    print("⚠️ GEMINI_API_KEY not found in .env file. Gemini features will be skipped.")

if not TMDB_API_KEY:
    print("🔴 TMDB_API_KEY not found in .env file. TMDb features will not work. Please set it and restart.")
    # exit() # You might want to exit if TMDb is critical and missing

TMDB_BASE_URL = "[https://api.themoviedb.org/3](https://api.themoviedb.org/3)"

# --- HELPER FUNCTIONS ---

def make_tmdb_request(endpoint, params=None, method="GET"):
    """Helper function to make requests to TMDb API."""
    if not TMDB_API_KEY:
        print("ℹ️ TMDB API key not available. Skipping TMDb request.")
        return None

    if params is None:
        params = {}
    # Add the api_key to every request to TMDb
    params['api_key'] = TMDB_API_KEY
    
    headers = {
        "accept": "application/json"
    }

    full_url = f"{TMDB_BASE_URL}{endpoint}"
    # print(f"ℹ️ Making TMDb request: {method} {full_url} with params: {params}") # Debug line

    try:
        if method.upper() == "GET":
            response = requests.get(full_url, params=params, headers=headers)
        # Add POST, PUT, DELETE here if needed in the future
        else:
            print(f"🔴 Unsupported HTTP method: {method}")
            return None
        
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # Try to get more details from the response if it's JSON
        error_details = ""
        try:
            error_details = response.json()
        except ValueError: # response is not JSON
            error_details = response.text[:200] # First 200 chars
        print(f"🔴 HTTP error occurred making TMDb request to {endpoint}: {http_err} - Status: {response.status_code}, Response: {error_details}")
    except requests.exceptions.RequestException as e:
        print(f"🔴 General error making TMDb request to {endpoint}: {e}")
    return None

def get_country_code_from_name(country_name_input):
    """Maps common country names to ISO 3166-1 alpha-2 codes."""
    country_map = {
        "brazil": "BR",
        "brasil": "BR", # Added Portuguese name for Brazil
        "usa": "US",
        "united states": "US",
        "united states of america": "US",
        "canada": "CA",
        "united kingdom": "GB",
        "uk": "GB",
        "germany": "DE",
        "france": "FR",
        "japan": "JP",
        # Add more common countries as needed by your users
    }
    normalized_input = country_name_input.lower().strip()
    return country_map.get(normalized_input, normalized_input.upper()) # Default to upper if not found, assuming it might be a code already

def get_tmdb_provider_id_from_name(provider_name_input, media_type="all", watch_region="US"):
    """
    Simplified mapping of common streaming provider names to their TMDb IDs.
    In a real app, you'd fetch `/watch/providers/movie` and `/watch/providers/tv`
    for the user's region once, cache them, and use that for accurate ID lookup.
    This POC uses a small hardcoded list for common services.
    Note: Provider IDs can sometimes differ slightly by region or even name variations.
    """
    provider_name_lower = provider_name_input.lower().strip()
    
    common_provider_map = {
        "netflix": 8,
        "amazon prime video": 9, 
        "prime video": 9,
        "amazon video": 9, # Another common way users might type it
        "disney plus": 337,
        "disney+": 337,
        "hbo max": 384, 
        "max": 1899,    
        "apple tv plus": 350, 
        "appletv+": 350,
        "apple tv+": 350,
        "hulu": 15,
        "paramount plus": 531,
        "paramount+": 531,
        # For Brazil (BR) specific:
        "globoplay": 307,
        "star plus": 619, # Star+ in Latin America
        "star+": 619,
        "claro video": 167,
    }
    return common_provider_map.get(provider_name_lower)


# --- AGENT FUNCTION DEFINITIONS ---

def agent_user_context_collector():
    """Agent 1: Collects preferences from the user via console input."""
    print("\n--- 🙋 Agent 1: User Context Collector ---")
    
    while True: 
        try:
            age_str = input("➡️ Enter child's age (e.g., 5, 8, 12): ")
            age = int(age_str)
            if 1 <= age <= 18: 
                break
            else:
                print("⚠️ Please enter a valid age between 1 and 18.")
        except ValueError:
            print("⚠️ Invalid input. Please enter a number for age.")

    interests_query = input("➡️ What is the child interested in today (e.g., 'funny animation with talking animals', 'space adventure movies')? ")
    if not interests_query.strip():
        print("ℹ️ No specific interests provided. Will search for generally popular content.")
        interests_query = "popular kids movies" # Default if empty

    platforms_input_str = input("➡️ Enter preferred streaming platforms, separated by commas (e.g., 'Netflix, Disney Plus, Prime Video'): ")
    preferred_platform_names_cleaned = [p.strip().lower() for p in platforms_input_str.split(',') if p.strip()]
    
    country_name_input = input("➡️ Enter your country for streaming availability (e.g., 'Brazil', 'USA', 'Canada'): ")
    country_code = get_country_code_from_name(country_name_input)
    
    if len(country_code) != 2 or not country_code.isalpha(): # Basic check, TMDb will ultimately validate
        print(f"⚠️ Country '{country_name_input}' mapped to '{country_code}'. This might not be a valid ISO 3166-1 code. TMDb results may be affected or default to a general region.")

    print("✅ Context collected.")
    return {
        "age": age,
        "interests_query": interests_query,
        "preferred_platform_names": preferred_platform_names_cleaned,
        "country_code": country_code
    }

def agent_content_prospector(user_context):
    """Agent 2: Finds initial movie/TV show prospects from TMDb using user's interests."""
    print("\n--- 🔎 Agent 2: Content Prospector (Searching TMDb) ---")
    if not TMDB_API_KEY: return [] 

    print(f"Searching TMDb for content matching: '{user_context['interests_query']}' for country '{user_context['country_code']}'...")

    search_params = {
        'query': user_context['interests_query'],
        'include_adult': 'false',
        'language': 'en-US', 
        'region': user_context['country_code'], 
        'page': 1
    }
    data = make_tmdb_request("/search/multi", params=search_params)

    prospects = []
    if data and 'results' in data:
        for item in data['results']:
            media_type = item.get('media_type')
            if media_type in ['movie', 'tv']:
                title = item.get('title') if media_type == 'movie' else item.get('name')
                tmdb_id = item.get('id')
                # Ensure it has a title, ID, and a decent overview (skip items with very little info)
                overview = item.get('overview', '')
                if title and tmdb_id and len(overview) > 20: # Arbitrary length to ensure some description
                    prospects.append({
                        'tmdb_id': tmdb_id,
                        'title': title,
                        'media_type': media_type,
                        'overview': overview,
                        'popularity': item.get('popularity', 0.0) 
                    })
    
    prospects = sorted(prospects, key=lambda x: x['popularity'], reverse=True)[:7] # Increased to top 7 for more chances

    if prospects:
        print(f"✅ Found {len(prospects)} initial prospects from TMDb (sorted by popularity).")
    else:
        print(f"⚠️ No initial prospects found on TMDb for the query: '{user_context['interests_query']}'. Try a different interest query or check for typos.")
    return prospects

def agent_detailed_enrichment(prospects_list, country_code_target):
    """Agent 3: Enriches prospects with details like genres, TMDb rating, and country-specific age certification."""
    print("\n--- 🧩 Agent 3: Detailed Enrichment (Fetching Details & Age Ratings) ---")
    if not TMDB_API_KEY or not prospects_list: return []

    enriched_prospects = []
    for prospect in prospects_list:
        print(f"Enriching '{prospect['title']}' (ID: {prospect['tmdb_id']}, Type: {prospect['media_type']})...")
        
        endpoint = f"/{prospect['media_type']}/{prospect['tmdb_id']}"
        append_param = "release_dates" if prospect['media_type'] == 'movie' else "content_ratings"
        
        details = make_tmdb_request(endpoint, params={'append_to_response': append_param, 'language': 'en-US'})

        if not details:
            print(f"  Skipping '{prospect['title']}' - failed to fetch details.")
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
                            # Consider theatrical (type 3), digital (type 4), physical (type 5), or TV (type 6) premiere
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
        print(f"  -> Genres: {enriched_item['genres']}, TMDb Rating: {enriched_item['tmdb_vote_average']:.1f} ({enriched_item['tmdb_vote_count']} votes), Age Cert ({country_code_target}): {age_certification_in_country}")

    print("✅ Enrichment process complete.")
    return enriched_prospects

def agent_streaming_availability_verifier(enriched_prospects_list, user_context_details):
    """Agent 4: Checks streaming availability on user's preferred platforms in their country."""
    print("\n--- 📺 Agent 4: Streaming Availability Verifier ---")
    if not TMDB_API_KEY or not enriched_prospects_list: return []

    target_country_code = user_context_details['country_code']
    user_preferred_platform_names_clean = user_context_details['preferred_platform_names'] 
    
    target_provider_ids_map = {} 
    for platform_name_clean in user_preferred_platform_names_clean:
        provider_id = get_tmdb_provider_id_from_name(platform_name_clean, watch_region=target_country_code)
        if provider_id:
            target_provider_ids_map[platform_name_clean] = provider_id # Store mapping for clarity
    
    if not target_provider_ids_map:
        print(f"⚠️ Could not map any of your preferred platforms ({', '.join(user_preferred_platform_names_clean)}) to known TMDb provider IDs. Cannot check streaming accurately.")

    print(f"Checking for availability on recognized platforms (IDs: {list(target_provider_ids_map.values())}) in {target_country_code}")

    prospects_with_streaming_info = []
    for item in enriched_prospects_list:
        print(f"Checking streaming for '{item['title']}'...")
        item_copy = item.copy()
        item_copy['available_on_user_platforms'] = [] 

        providers_data = make_tmdb_request(f"/{item['media_type']}/{item['tmdb_id']}/watch/providers")
        
        if providers_data and 'results' in providers_data and target_country_code in providers_data['results']:
            country_specific_providers = providers_data['results'][target_country_code]
            
            if 'flatrate' in country_specific_providers: # 'flatrate' for subscription
                for tmdb_provider_info in country_specific_providers['flatrate']:
                    tmdb_provider_id = tmdb_provider_info.get('provider_id')
                    tmdb_provider_name_from_api = tmdb_provider_info.get('provider_name') # Use name from API for display
                    
                    if tmdb_provider_id in target_provider_ids_map.values():
                        item_copy['available_on_user_platforms'].append(tmdb_provider_name_from_api)
        
        if item_copy['available_on_user_platforms']:
            item_copy['available_on_user_platforms'] = sorted(list(set(item_copy['available_on_user_platforms'])))
            print(f"  -> ✅ Available on: {', '.join(item_copy['available_on_user_platforms'])}")
        else:
            print(f"  -> ℹ️ Not found on your preferred streaming services in {target_country_code} (or no mapping for your services).")
        prospects_with_streaming_info.append(item_copy)

    print("✅ Streaming availability check complete.")
    return prospects_with_streaming_info

def agent_recommendation_selector_and_justifier(fully_enriched_prospects, user_context_data):
    """Agent 5: Filters to suitable & available items, selects top 1-2, and gets Gemini justification."""
    print("\n--- ⭐ Agent 5: Recommendation Selector & Justifier ---")
    if not fully_enriched_prospects:
        print("⚠️ No prospects available to select from.")
        return []

    child_s_age = user_context_data['age']
    target_country = user_context_data['country_code']
    
    suitable_and_available_options = []
    for item in fully_enriched_prospects:
        if not item.get('available_on_user_platforms'):
            continue

        certification_str = item.get('age_certification_country', "N/A").upper()
        is_age_appropriate_for_child = False
        
        # Simplified Age Appropriateness Logic for POC
        if certification_str == "N/A" or certification_str == "NOT RATED" or certification_str == "UNRATED":
            is_age_appropriate_for_child = True # Assume parental discretion for unrated
        elif target_country == "BR": # Brazil - Classificação Indicativa
            if certification_str == "L" : is_age_appropriate_for_child = True
            elif certification_str.startswith("AL") : is_age_appropriate_for_child = True # Alternative "Livre"
            elif certification_str == "10" and child_s_age >= 10: is_age_appropriate_for_child = True
            elif certification_str == "12" and child_s_age >= 12: is_age_appropriate_for_child = True
            elif certification_str == "14" and child_s_age >= 14: is_age_appropriate_for_child = True
            elif certification_str == "16" and child_s_age >= 16: is_age_appropriate_for_child = True
            elif certification_str == "18" and child_s_age >= 18: is_age_appropriate_for_child = True
            else: is_age_appropriate_for_child = False # If rated but not matching, assume not appropriate
        elif target_country == "US": # USA - MPAA and TV Parental Guidelines
            if certification_str in ["G", "TV-Y", "TV-G"]: is_age_appropriate_for_child = True
            elif certification_str == "PG": is_age_appropriate_for_child = True # Parental Guidance suggested, generally okay for many kids
            elif certification_str == "TV-Y7": is_age_appropriate_for_child = child_s_age >= 7
            elif certification_str == "TV-PG": is_age_appropriate_for_child = True # Parental Guidance suggested
            elif certification_str == "PG-13" and child_s_age >= 13: is_age_appropriate_for_child = True
            elif certification_str == "TV-14" and child_s_age >= 14: is_age_appropriate_for_child = True
            else: is_age_appropriate_for_child = False
        else: # Default for unhandled countries: assume appropriate if unrated, otherwise needs manual check (false for POC)
            is_age_appropriate_for_child = certification_str == "N/A" # Only if unrated

        if not is_age_appropriate_for_child:
            # print(f"ℹ️ Skipping '{item['title']}' (Cert: {certification_str} in {target_country}) - deemed not age-appropriate for {child_s_age} years old based on POC logic.")
            continue
            
        suitable_and_available_options.append(item)

    if not suitable_and_available_options:
        print("⚠️ No recommendations found that are both age-appropriate (based on simplified POC logic) and available on your platforms.")
        return []

    recommendations_to_justify = sorted(suitable_and_available_options, key=lambda x: x.get('popularity', 0.0), reverse=True)[:2]

    final_recommendations_with_text = []
    if not gemini_model: 
        print("⚠️ Gemini model not available. Skipping justifications.")
        for rec in recommendations_to_justify:
             rec['gemini_justification'] = "Justification not available (Gemini API not configured)."
             final_recommendations_with_text.append(rec)
        return final_recommendations_with_text

    for rec_item in recommendations_to_justify:
        print(f"🤖 Generating Gemini justification for '{rec_item['title']}'...")
        try:
            platforms_str = ', '.join(rec_item['available_on_user_platforms']) if rec_item['available_on_user_platforms'] else "selected streaming services"
            genres_str = ', '.join(rec_item['genres']) if rec_item['genres'] else "various interesting genres"

            prompt_for_gemini = (
                f"The user is a parent in {user_context_data['country_code']} looking for a {rec_item['media_type']} for their {user_context_data['age']}-year-old child. "
                f"The child is interested in: '{user_context_data['interests_query']}'.\n"
                f"Here's a movie/show option: '{rec_item['title']}'.\n"
                f"Brief Synopsis: {rec_item['overview']}\n"
                f"Genres: {genres_str}.\n"
                f"TMDb User Rating: {rec_item['tmdb_vote_average']:.1f}/10 ({rec_item['tmdb_vote_count']} votes).\n"
                f"The age certification in their country ({user_context_data['country_code']}) is '{rec_item['age_certification_country']}'.\n"
                f"It's available on: {platforms_str}.\n\n"
                f"Please write a short, friendly, and engaging paragraph (2-3 sentences) for the parent. "
                f"Explain why '{rec_item['title']}' could be a great choice for their child's viewing today, considering their age and interests. "
                f"Highlight a positive aspect (e.g., from genres, synopsis, or its general appeal). "
                f"Subtly encourage them to watch it on one of the mentioned services. Sound enthusiastic and helpful. "
                f"Do not repeat the synopsis verbatim. Keep it concise."
            )
            
            response = gemini_model.generate_content(prompt_for_gemini)
            # Fallback if response or text is empty or an error structure from Gemini
            if hasattr(response, 'text') and response.text:
                rec_item['gemini_justification'] = response.text.strip()
            elif hasattr(response, 'parts') and response.parts: # Check if it's a multi-part response (less likely for text model)
                rec_item['gemini_justification'] = "".join(part.text for part in response.parts if hasattr(part, 'text')).strip()
            else: # If response structure is unexpected or empty
                print(f"⚠️ Gemini response for '{rec_item['title']}' was empty or in an unexpected format.")
                rec_item['gemini_justification'] = f"'{rec_item['title']}' seems like a good option based on your criteria! You can find it on {platforms_str}." # Generic fallback
        
        except Exception as e:
            print(f"🔴 Error during Gemini justification for '{rec_item['title']}': {e}")
            rec_item['gemini_justification'] = f"Could not generate a detailed justification due to an error, but '{rec_item['title']}' looks promising and is on {platforms_str}!"
        final_recommendations_with_text.append(rec_item)

    print("✅ Recommendations selected and justifications attempted.")
    return final_recommendations_with_text

def agent_console_display_final(final_recommendations_list, original_user_context):
    """Agent 6: Displays the final, justified recommendations to the user in the console."""
    print("\n--- 🎬 Agent 6: Final Recommendations Display ---")
    if not final_recommendations_list:
        print("\n😢 I'm sorry, I couldn't find any recommendations that closely matched all your criteria this time. "
              "You could try a slightly different interest query, check more streaming platforms, or a different age if appropriate.")
        return

    print(f"\n✨ Here are some personalized suggestions for your {original_user_context['age']}-year-old, "
          f"interested in '{original_user_context['interests_query']}', in {original_user_context['country_code']}: ✨")
    
    for i, rec in enumerate(final_recommendations_list):
        print(f"\n--- Recommendation #{i+1} ---")
        print(f"📺 Title: {rec['title']} ({rec['media_type'].upper()})")
        print(f"⭐ TMDb Rating: {rec.get('tmdb_vote_average', 'N/A'):.1f}/10 ({rec.get('tmdb_vote_count', 0)} votes)")
        print(f"🔞 Age Certification ({original_user_context['country_code']}): {rec.get('age_certification_country', 'N/A')}")
        print(f"🎭 Genres: {', '.join(rec.get('genres', ['Not specified']))}")
        print(f"📜 Overview: {rec.get('overview', 'No overview available.')}")
        
        if rec.get('available_on_user_platforms'):
            print(f"💻 Available on your platforms: {', '.join(rec.get('available_on_user_platforms'))}")
        else:
            print(f"💻 Availability on your preferred platforms: Not confirmed on your specified list.")
            
        print(f"\n💡 Why this could be a great pick:")
        print(f"{rec.get('gemini_justification', 'No specific justification generated.')}")
    
    print("\n" + "="*50)
    print("Remember to always use your own judgment and check content advisories when selecting for your child. Enjoy your movie time! 🎉")

# --- MAIN EXECUTION BLOCK ---

if __name__ == "__main__":
    print("🎬 Welcome to the Movie Picker POC (Python Backend)! 🎬")
    
    if not TMDB_API_KEY: 
        print("\n🔴 CRITICAL: TMDB_API_KEY is missing. This application cannot function without it. Please set it in your .env file and restart.")
    else:
        # 1. Collect User Context
        user_context = agent_user_context_collector()
        # print("\n[DEBUG] User Context:", json.dumps(user_context, indent=2))

        # 2. Find Initial Prospects from TMDb
        initial_prospects = agent_content_prospector(user_context)
        # print("\n[DEBUG] Initial Prospects:", json.dumps(initial_prospects, indent=2))

        if initial_prospects: # Only proceed if we have some prospects
            # 3. Enrich Prospects with Details (Age Ratings, etc.)
            enriched_prospects = agent_detailed_enrichment(initial_prospects, user_context['country_code'])
            # print("\n[DEBUG] Enriched Prospects:", json.dumps(enriched_prospects, indent=2))

            # 4. Verify Streaming Availability on User's Platforms
            prospects_with_streaming = agent_streaming_availability_verifier(enriched_prospects, user_context)
            # print("\n[DEBUG] Prospects with Streaming Info:", json.dumps(prospects_with_streaming, indent=2))
            
            # 5. Select Top Recommendations and Get Gemini Justification
            final_recommendations = agent_recommendation_selector_and_justifier(prospects_with_streaming, user_context)
            # print("\n[DEBUG] Final Recommendations with Justification:", json.dumps(final_recommendations, indent=2))

            # 6. Display Final Recommendations to User
            agent_console_display_final(final_recommendations, user_context)
        else:
            print("\nNo initial movies or shows found based on your query. The subsequent agents will not run.")

    print("\n👋 Movie Picker POC finished. Goodbye!")