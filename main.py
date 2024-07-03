import random
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

import uvicorn
from fastapi import Body, FastAPI, Header, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    # default might not be ideal due to async logic
    timestamp: str
    content: str
    type: str


class UserMessage(Message):
    type: str = "human"


class AIMessage(Message):
    type: str = "ai"
    context_ids: Optional[List[str]] = None


class ChatQuestion(BaseModel):
    question: str

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


AGENT_TYPES = [("5e21b19e0e69dc2fc7e23715", "Fixed || B2C || Service"),
("5e21b1b40e69dc45071f618c", "Fixed || B2C || Sales"),
("5e21b1c20e69dc2fc7e23729", "Fixed || B2B || Service"),
("5e21b1d40e69dc584ad07e5f", "Fixed || B2B || Sales"),
("5e5f74d4526722271b4bd359", "Fixed | B2C | Bright"),
("5e5f75075267221e2d3fd8f5", "Fixed | B2C | Bright Selfservice"),
("5e79d5c8dbddbb7c8e82df57", "Fixed | Wifi Assistant"),
("5e7b6e165267223069a86dc4", "Consumer"),
("5e7b6e2552672229004df65c", "Business"),
("5e7dad545267223078f57026", "VodafoneZiggo || Marketing Tribe"),
("5e833059dbddbb604f148460", "VZ Marketing Tribe"),
("5eb51980dbddbb20eacc45f8", "Training"),
("5eb51a82dbddbb28b91fd042", "Training LWD"),
("5ed656280e69dc3dc1725d5c", "Warm Handover")]

@app.get("/healthcheck")
async def healthcheck():
    return {"message": "Hello World", "timestamp": datetime.now(timezone.utc)}


@app.post("/message")
async def query(body: ChatQuestion = Body(), api_key_header: str = Security(api_key_header), session_id: str = Header()):
    if api_key_header != '605c68d5-19f1-4ab7-ab72-b660d8964861':
        raise HTTPException(status_code=401, detail="Incorrect API Key.")

    cur_time = datetime.now(timezone.utc)

    msg1 = AIMessage(content=f"Hi! Your message was '{body.question}'", timestamp=str(cur_time))
    msg2 = AIMessage(content=f"Random number: {random.randint(1,99)}", timestamp=str(cur_time))

    dice_roll = random.randint(1,6)
    if dice_roll >= 5:
        selected_agent = random.choice(AGENT_TYPES)
        metadata = {
            "handover": True,
            "agent_type_id": selected_agent[0],
            "agent_type_name": selected_agent[1]
        }
        transfer_msg = AIMessage(content=f"Transferring to agent '{selected_agent[1]}' (ID: {selected_agent[0]})", timestamp=str(cur_time))
        return {"messages": [msg1, msg2, transfer_msg], "metadata": metadata, "timestamp": cur_time, "session_id": session_id}
    else:
        return {"messages": [msg1, msg2], "timestamp": cur_time, "session_id": session_id}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)
