import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from serp import search_google_web_automation
from my_functions import get_article_from_url, generate_ideas


# FastAPI app instance
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

        # Initialize output_data
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

        # # Display URLs and Titles
        # print("Websites, von denen die Content-Ideen übernommen wurden:")
        # for result in search_results:
        #     print(result["url"])

        #     # Display H-Titles
        #     for h_title in result.get("htitles", []):
        #         print(f"{h_title}")

        # # Display the number of records
        # print(f"Anzahl der generierten Ideen: {len(all_ideas)}")

        # Return data in a more structured format
        response_data = {
            "websites": [{"url": result["url"], "htitles": result.get("htitles", [])} for result in search_results],
            "num_generated_ideas": len(all_ideas),
            "generated_ideas": all_ideas,
        }

        return response_data

    except Exception as e:
        print(f"Error fetching search results: {e}")
        return {"error": f"Error fetching search results: {e}"}


#if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host="127.0.0.1", port=8000)
