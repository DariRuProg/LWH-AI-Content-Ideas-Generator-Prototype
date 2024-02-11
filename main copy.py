import asyncio
import json
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI

from serp import search_google_web_automation
from my_functions import get_article_from_url, generate_ideas

app = FastAPI()

prompt = "we are in the german market - give all answers in german. Extract 3 - 5 content ideas from the [post], and return the list in JSON format, [post]: {post}"

# Define die Klasse Ideas
class Ideas(BaseModel):
    ideas: List[str]

# Async-Funktion zur Verarbeitung der Hauptlogik
@app.get("/blog/generate-titles")
async def main(search_query: str):
    try:
        search_results = search_google_web_automation(search_query, 10)
        all_ideas = []

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
            except Exception as e:
                print(f"Error processing search result {result}: {e}")

        # Display URLs and Titles
        print("Websites, von denen die Content-Ideen übernommen wurden:")
        for result in search_results:
            print(result["url"])

            # Display H-Titles
            for h_title in result.get("htitles", []):
                print(f"{h_title}")

        # Display the number of records
        print(f"Anzahl der generierten Ideen: {len(all_ideas)}")

        return {"generated_ideas": all_ideas}

    except Exception as e:
        print(f"Error fetching search results: {e}")
        return {"error": f"Error fetching search results: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
