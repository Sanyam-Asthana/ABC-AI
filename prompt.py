import os
import requests
import json

# Linux/macOS: export GEMINI_API_KEY='your_api_key'
# Windows: set GEMINI_API_KEY='your_api_key'
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def call_gemini_api(prompt: str) -> str:
    """
    Calls the Gemini API to generate the enhanced prompt.

    Args:
        prompt: The full prompt to send to the model.

    Returns:
        The generated text from the model.

    Raises:
        Exception: If the API call fails or returns an unexpected response.
    """
    if API_KEY == "YOUR_API_KEY_HERE":
        raise ValueError("API Key not configured. Please set the GEMINI_API_KEY environment variable or replace the placeholder in the script.")

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 8192,
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status() 

        result = response.json()

        if (
            "candidates" in result and
            result["candidates"] and
            "content" in result["candidates"][0] and
            "parts" in result["candidates"][0]["content"] and
            result["candidates"][0]["content"]["parts"]
        ):
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:

            finish_reason = result.get("candidates", [{}])[0].get("finishReason")
            if finish_reason == 'SAFETY':
                raise Exception("The response was blocked due to safety settings. Please modify your prompt.")
            raise Exception(f"The API returned an unexpected response structure: {result}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"An error occurred during the API request: {e}")
    except json.JSONDecodeError:
        raise Exception(f"Failed to decode API response. Raw response: {response.text}")


def main():
    """
    Main function to run the prompt engineering assistant.
    """
    print("--- Prompt Engineering Assistant ---")
    print("Enter your basic idea, and I'll enhance it into a powerful, well-structured prompt.\n")

    try:
        user_prompt = input("Your Basic Prompt: ")
        if not user_prompt.strip():
            print("\nError: Please enter a prompt.")
            return

        meta_prompt = f"""You are an expert prompt engineer. Your task is to take a user's simple idea and transform it into a detailed, well-structured, and effective prompt for a generative AI. 
                
When rewriting, consider the following principles:
1.  **Role & Goal:** Clearly define the AI's role (e.g., "You are a travel blogger," "You are a senior software engineer").
2.  **Context:** Provide background information to set the scene.
3.  **Task:** Be explicit about what the AI needs to do. Use action verbs.
4.  **Constraints:** Specify limitations, such as word count, tone of voice, or things to avoid.
5.  **Format:** Define the desired output structure (e.g., markdown, JSON, a list of bullet points).
6.  **Examples:** Provide a clear example of the desired output if possible.

Now, take the following user prompt and enhance it based on these principles.

Make sure to respond with ONLY the improved prompt and NOTHING ELSE!

User's Prompt: "{user_prompt}"
"""
        
        print("\n✨ Enhancing your prompt... (This might take a moment)")
        
        enhanced_prompt = call_gemini_api(meta_prompt)
        
        print("\n--- Enhanced Prompt ---")
        print(enhanced_prompt)
        print("-----------------------\n")

    except (ValueError, Exception) as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
