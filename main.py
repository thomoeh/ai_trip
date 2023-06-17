from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI()

# start the chatbot pipeline
def start_chatbot_pipeline(request_id):
    ''' Start the chatbot pipeline, for request with id request_id '''
    # Start the chatbot pipeline
    return  


def load_chatbot_answer(request_id):
    ''' returns the final answer from the chat chain with request id request_id '''
    # Load the chatbot answer from file 
    # the chat history is stored in a file with key request_id
    
    # load the chat history file "chat_histories.json"
    with open("chat_chains.json", "r") as f:
        chat_histories = json.load(f)
    # select the chat history with key request_id
    chat_history = chat_histories[request_id]
    # get the last message in the chat history
    if len(last_message) > 0:
        last_message = chat_history[-1]
        return last_message
    else:
        print('no message in chat history')
    
    
class Message(BaseModel):
    inquiry: str

class ChatbotResponse(BaseModel):
    response: str

# POST request for sending user message to the chatbot
@app.post("/user_message/{request_id}")
async def receive_user_message(message: Message):
    # Process the user's message with your chatbot application
    chatbot.send_message(message.content)
    start_chatbot_pipeline(request_id)
    return {"message": "Message received and chatbot pipeline started"}

# GET request for getting chatbot response
@app.get("/chatbot_response/{request_id}")
async def get_chatbot_response(request_id):
    # Get a response from your chatbot application
    response = load_chatbot_answer(request_id)
    return {"response": response}