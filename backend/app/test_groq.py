# Import os so we can read environment variables from the .env file.
import os

# Load variables from the .env file into the application environment.
from dotenv import load_dotenv

# Import the Groq client used to communicate with the Groq API.
from groq import Groq


# Load the variables stored in backend/.env.
load_dotenv()


# Read the Groq API key without hardcoding it in our Python source code.
groq_api_key = os.getenv("GROQ_API_KEY")


# Stop the program with a clear message if the API key is missing.
if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing from the .env file.")


# Create a Groq client using the API key loaded from the environment.
client = Groq(api_key=groq_api_key)


# Send a small test request to verify that our Groq API connection works.
response = client.chat.completions.create(
    # Use the currently supported GPT-OSS 20B model available through Groq.
    model="openai/gpt-oss-20b",

    # Provide a simple message for the connectivity test.
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: Groq connection successful."
        }
    ],

    # Keep the response small because this is only a connectivity test.
    max_tokens=20,
)


# Print the model's direct response returned by Groq.
print("Model response:")
print(response.choices[0].message.content)


# Print the model's reasoning output for debugging during development.
print("\nModel reasoning:")
print(response.choices[0].message.reasoning)


# Print a clear success message after the API request completes.
print("\nGroq API connection test completed successfully.")