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


AGENT_TYPES = [
('5e6f49759090ee0588405615', 'Fixed | B2B | Retention & Loyalty Advisor'),
('5d4973edd6cb00e5f3817795', 'Fixed | B2B | Sales Advisor'),
('5cb85a21920026399882a18b', 'Fixed | B2B | Service Advisor | Web'),
('5c59976e9200265b356e5fd4', 'Fixed | B2C | OEC Advisor'),
('5d7a37f39090ee2bcfd9f4bb', 'Facturen en betalen'),
('5d7a38279090ee1e45953aad', 'Wifi Specialists (vh: Internet)'),
('5d7a38339090ee24b42e6ca7', 'Monteur'),
('5d7a390a9090ee102c931ea8', 'Overige vragen'),
('5d832b4a9090ee4fda3f8e7b', 'Televisie'),
('5f7ec5333298c90c81b34680', 'Wifi Case Manager'),
]

@app.get("/healthcheck")
async def healthcheck():
    return {"message": "Hello World", "timestamp": datetime.now(timezone.utc)}


@app.post("/message")
async def query(body: ChatQuestion = Body(), api_key_header: str = Security(api_key_header), session_id: str = Header()):
    if api_key_header != '605c68d5-19f1-4ab7-ab72-b660d8964861':
        raise HTTPException(status_code=401, detail="Incorrect API Key.")

    cur_time = datetime.now(timezone.utc)
    dice_roll = random.randint(1,6)
    if dice_roll >= 5:
        selected_agent = random.choice(AGENT_TYPES)
        metadata = {
            "handover": True,
            "agent_type_id": selected_agent[0],
            "agent_type_name": selected_agent[1]
        }
    else:
        metadata = {}
    
    msg1 = AIMessage(content=f"Hi! Your message was '{body.question}'", timestamp=str(cur_time))
    msg2 = AIMessage(content=f"Random number: {random.randint(1,99)}", timestamp=str(cur_time))

    return {"messages": [msg1, msg2], "metadata": metadata, "timestamp": cur_time, "session_id": session_id}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)
