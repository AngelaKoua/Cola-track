import httpx
import json
import logging
import os
from app.config import settings

logger = logging.getLogger(__name__)

async def generate_chat_response(messages: list, context_data: dict) -> dict:
    """
    Generates a contextual response using Gemini based on structured requirements.
    Uses the REST API via httpx to avoid legacy package issues.
    `messages` is a list of {"role": "user"|"model", "content": string}.
    `context_data` contains { "page": str, "machine": str, "indicators": str }.
    
    Returns a dict with format: { "Explication": "...", "Interprétation": "...", "Actions": [...] }
    """
    if not settings.GEMINI_API_KEY:
        return {
            "Explication": "[MOCK] Je suis un assistant Colatrack (Clé non configurée).",
            "Interprétation": f"Vous êtes sur la page {context_data.get('page')}.",
            "Actions": ["Vérifiez votre configuration .env", "Ajoutez GEMINI_API_KEY"]
        }
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        
        # Read the Colatrack Guide to use as context
        guide_path = os.path.join(os.path.dirname(__file__), "colatrack_guide.txt")
        guide_content = ""
        try:
            with open(guide_path, "r", encoding="utf-8") as f:
                guide_content = f.read()
        except Exception as e:
            print(f"Guide not found: {e}")

        system_prompt = f"""
        Tu es ColaAssist, l'assistant expert industriel et plateforme de Colatrack (maintenance prédictive, traitement d'eau, ligne de production, IoT industriel).
        Ton rôle est de répondre aux questions techniques (ex: pH, TDS, turbidité), questions métier (maintenance, production), d'interprétation des indicateurs ou des actions sur la plateforme.
        Tes réponses doivent être exactes, techniques, éviter les approximations et toujours contextualisées pour le domaine industriel (impact machine, qualité, production).
        Si la question est hors-sujet par rapport à l'industrie ou la plateforme, recadre poliment.
        
        Contexte actuel de l'utilisateur:
        - Page: {context_data.get('page', 'Inconnue')}
        - Machine sélectionnée: {context_data.get('machine', 'Aucune')}
        - Indicateurs: {context_data.get('indicators', 'Aucun')}
        
        Ta réponse DOIT être en JSON avec EXACTEMENT cette structure (ne déroge jamais) :
        {{
            "Explication": "Réponse claire, directe et précise à la question.",
            "Interprétation": "Interprétation industrielle : lien avec le contexte réel (impact équipement, qualité, production).",
            "Actions": ["Action concrète 1", "Action 2"] // Liste optionnelle d'étapes de résolution ou d'investigation
        }}
        
        ====== BASE DE CONNAISSANCES COLATRACK ======
        {guide_content}
        =============================================
        """
        
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": contents,
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            
            if response.status_code != 200:
                logger.error(f"Gemini Error: {response.text}")
                response.raise_for_status()
                
            data = response.json()
            try:
                # Extract text from response
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                result = json.loads(text)
                return result
            except (KeyError, IndexError, json.JSONDecodeError) as parse_err:
                logger.error(f"Failed to parse JSON from Gemini: {data}")
                return {
                    "Explication": "La réponse n'a pas pu être analysée.",
                    "Interprétation": None,
                    "Actions": []
                }
                
    except Exception as e:
        logger.error(f"Error calling Gemini REST API: {e}")
        return {
            "Explication": "Une erreur s'est produite lors de la communication avec l'assistant.",
            "Interprétation": "Veuillez réessayer ultérieurement.",
            "Actions": []
        }
