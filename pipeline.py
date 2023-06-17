import json
import os
import random

import weaviate
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

PROMPTS_FILEPATH = "user_prompts.json"
SYSTEM_MESSAGES_FILEPATH = "system_prompts.json"

WEAVIATE_KEY = os.environ.get("WEAVIATE_KEY")
OPEN_AI_KEY = os.environ.get("OPENAI_KEY")


def create_first_prompt(system_message: str) -> ChatPromptTemplate:
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message)
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        "{query}.\n"
        + "Please create the perfect tour description in the style of the example for me based on my inquiry."
    )

    return ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )


def create_hard_requirements(system_message: str) -> ChatPromptTemplate:
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message)

    human_message_prompt = HumanMessagePromptTemplate.from_template("{query}.")

    return ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )


def run_chain(query: str) -> list:
    with open(SYSTEM_MESSAGES_FILEPATH, "r") as system_messages_file:
        system_messages = json.load(system_messages_file)

    first_system_message = system_messages["foundation_prompt"]

    chat_prompt = create_first_prompt(first_system_message)
    llm = ChatOpenAI(model="gpt-4")
    first_query_chain = LLMChain(prompt=chat_prompt, llm=llm, verbose=True)

    hard_requirements_query = create_hard_requirements(
        system_messages["extract_information_from_user_message"]
    )
    hard_requirements_chain = LLMChain(
        prompt=hard_requirements_query, llm=llm, verbose=True
    )
    # hard_requirements_response = hard_requirements_chain.run(query)
    # hard_requirements = json.loads(hard_requirements_response)

    auth_config = weaviate.AuthApiKey(api_key=WEAVIATE_KEY)
    client = weaviate.Client(
        "https://hackathon-mlops-64e23r2k.weaviate.network",
        auth_client_secret=auth_config,
        additional_headers={"X-Openai-Api-Key": OPEN_AI_KEY},
    )

    query_output = first_query_chain.run(query)

    similar_items = (
        client.query.get("aitrippers", ["tour_name", "about_tour"])
        .with_near_text({"concepts": query_output})
        .with_limit(3)
        # .with_where(hard_requirements)
        .do()
    )

    return similar_items


def main():
    with open(PROMPTS_FILEPATH, "r") as prompts_file:
        prompts = json.load(prompts_file)

    first_query = random.choice(list(prompts.values()))

    print(run_chain(first_query))


if __name__ == "__main__":
    main()
