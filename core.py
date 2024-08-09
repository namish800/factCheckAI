from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ChatMessage
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from prompts import *

import re
from langchain.schema import BaseOutputParser

_ = load_dotenv()


class FactCheckOutput():
    def __init__(self, parsed_output):
        self.assumption = parsed_output['assumption']
        self.followup = parsed_output['followup']


class FactCheckParser(BaseOutputParser):
    """Parse the output of an LLM call """

    def parse(self, text: str):
        """Parse the output of an LLM call."""
        assumption_matches = re.findall(r'Assumption: (.+)', text)
        followup_matches = re.findall(r'Fact Check: (.+)', text)

        return FactCheckOutput({
            'assumption': assumption_matches if len(assumption_matches) > 0 else None,
            'followup': followup_matches if len(followup_matches) > 0 else None
        })


class AgentState(TypedDict):
    post: str
    claims: List[str]
    fact_check_questions: List[str]
    internet_findings: List[str]
    result: str


class Agent:
    def __init__(self):
        memory = SqliteSaver.from_conn_string(":memory:")
        self.model = ChatOpenAI(model="gpt-4o", temperature=0)
        self.client = TavilyClient()
        graph = StateGraph(AgentState)
        # graph.add_node("claim_extractor", self.claim_extractor_node)
        graph.add_node("question_generator", self.generate_question_node)
        graph.add_node("internet_researcher", self.internet_research_node)
        graph.add_node("summarize_results", self.summarize_node)

        # graph.set_entry_point("claim_extractor")
        # graph.add_edge("claim_extractor", "question_generator")
        graph.set_entry_point("question_generator")
        graph.add_edge("question_generator", "internet_researcher")
        graph.add_edge("internet_researcher", "summarize_results")
        graph.add_edge("summarize_results", END)

        self.graph = graph.compile()

    def run(self, post: str):
        return self.graph.invoke({
            'post': post
        })

    def claim_extractor_node(self, state: AgentState):
        output_parser = FactCheckParser()
        messages = [
            SystemMessage(content=CLAIM_EXTRACTOR_PROMPT),
            HumanMessage(content=state['post'])
        ]
        response = self.model.invoke(messages)
        claims = output_parser.parse(response.content)
        return {"claims": claims.assumption}

    def generate_question_node(self, state: AgentState):
        output_parser = FactCheckParser()
        messages = [
            SystemMessage(content=GENERATE_FACT_CHECK_QUESTION_SYS_PROMPT),
            HumanMessage(content=str(state['post']))
        ]
        resp = self.model.invoke(messages)

        questions = output_parser.parse(resp.content)
        return {"fact_check_questions": questions.followup}

    def internet_research_node(self, state: AgentState):
        search_results = []
        for question in state['fact_check_questions']:
            result = []
            tavily_resp = self.client.search(question,
                                             include_answer=True, include_raw_content=True)
            result = [{'url': x['url'], 'content': x['content']} for x in tavily_resp['results']]
            search_results = search_results + result
        return {"internet_findings": str(search_results)}

    def summarize_node(self, state: AgentState):
        data = {"post": state['post'], "claims": str(state['claims']), "questions": str(state['fact_check_questions']),
                "data": str(state['internet_findings'])}

        input_prompt = SUMMARIZE_FINDINGS_USER_INPUT_PROMPT.format(**data)
        messages = [
            SystemMessage(content=SUMMARIZE_FINDINGS_SYS_PROMPT),
            HumanMessage(content=input_prompt)
        ]
        summarizer_response = self.model.invoke(messages)
        return {"result": summarizer_response.content}


if __name__ == "__main__":
    load_dotenv()
    agent = Agent()
    response = agent.run(post="""
        Imane Khalif is a biological women 
    """)

    print(response['result'])
