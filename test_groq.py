import asyncio
import os
from dotenv import load_dotenv
from litellm import acompletion

# Load the .env file explicitly
load_dotenv()

async def test_bare_metal_groq():
    print("🔍 INITIATING BARE-METAL GROQ TEST")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY is completely missing from the .env file!")
        return

    print(f"✅ API Key found (starts with: {api_key[:8]}...)")
    print("📡 Sending ping to Groq servers...")

    try:
        response = await acompletion(
            model="groq/llama3-8b-8192",
            messages=[{"role": "user", "content": "Respond with exactly three words: 'Groq is alive!'"}]
        )
        print(f"\n🟢 SUCCESS! Groq Replied: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"\n🔴 THE REAL ERROR EXPOSED:\n{str(e)}")

if __name__ == "__main__":
    asyncio.run(test_bare_metal_groq())