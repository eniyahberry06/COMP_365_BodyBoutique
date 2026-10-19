from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from recommendation import get_recommendations, create_AI_explanation, check_conflicts

app = FastAPI(title="The Body Boutique API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    desired_ingredients: List[str]
    skin_concerns: Optional[List[str]] = []
    product_type: Optional[str] = None
    scent_preference: Optional[str] = "any"
    texture_preference: Optional[str] = "any"

@app.post("/recommendations")
async def recommendations_endpoint(request: RecommendationRequest):
    user_query = " ".join(request.desired_ingredients + request.skin_concerns)

    raw_results = get_recommendations(
        user_query=user_query,
        product_type=request.product_type,
        desired_ingredients=request.desired_ingredients,
        skin_concerns=request.skin_concerns,
        texture_preference=request.texture_preference,
        sensory_weight=0.3,
        top_n=4
    )

    warnings = check_conflicts(request.desired_ingredients)

    user_input = {
        "desired_ingredients": (
            ", ".join(request.desired_ingredients)
            if request.desired_ingredients
            else "None specified"
        ),
        "skin_concerns": (
            ", ".join(request.skin_concerns)
            if request.skin_concerns
            else "General skincare"
        ),
        "scent_preference": request.scent_preference,
        "texture_preference": request.texture_preference,
    }

    async def fetch_reason(item):
        try:
            reason = create_AI_explanation(
                user_input=user_input,
                product_name=item.get("product_name", ""),
                product_ingredients=item.get("clean_ingreds", ""),
            )
            item["match_reason"] = reason
        except Exception as e:
            print(f"Error generating match reason for {item.get('product_name')}: {e}")
            item["match_reason"] = (
                f"Formulated with key ingredients targeting {user_input['desired_ingredients']}."
            )
        return item

    enhanced_results = await asyncio.gather(
        *(fetch_reason(item) for item in raw_results)
    )

    return {"recommendations": list(enhanced_results), "warnings": warnings}