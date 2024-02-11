import os
import asyncio
import json
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from serp import search_google_web_automation
from my_functions import get_article_from_url, generate_ideas

app = FastAPI()

# Configuration of CORS Middleware to accept requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # "*" allows requests from any origin; you can restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prompt = "we are in the german market - give all answers in german. Extract 3 - 5 content ideas from the [post], and return the list in JSON format, [post]: {post}"

# Define the Ideas class
class Ideas(BaseModel):
    ideas: List[str]

# Async function for the main logic
@app.get("/blog/generate-titles")
async def main(search_query: str):
    try:
        search_results = search_google_web_automation(search_query, 10)
        all_ideas = []

        output_data = {"websites": [], "num_generated_ideas": 0, "generated_ideas": []}

        total_results = len(search_results)

        for index, result in enumerate(search_results):
            try:
                result_url = result["url"]
                result_content = get_article_from_url(result_url)

                if result_content:
                    result_prompt = prompt.format(post=result_content)
                    ideas_object = await generate_ideas(result_prompt, Ideas)

                    if ideas_object and ideas_object.ideas:
                        all_ideas.extend(ideas_object.ideas)

                        # Add website information to output_data
                        website_info = {"url": result["url"], "htitles": result.get("htitles", [])}
                        output_data["websites"].append(website_info)
            except Exception as e:
                print(f"Error processing search result {result}: {e}")

        # Add the number of generated ideas to output_data
        output_data["num_generated_ideas"] = len(all_ideas)

        # Add generated ideas to output_data
        output_data["generated_ideas"] = all_ideas

        return output_data

    except Exception as e:
        print(f"Error fetching search results: {e}")
        return {"error": f"Error fetching search results: {e}"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))