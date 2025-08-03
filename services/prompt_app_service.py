from services.LLM_factory import LLMFactory


class PromptAppService:
    def __init__(self, LLM="gemini"):
        self.LLMName = LLM

    
    def hello_world(self):
        llm_model = LLMFactory.get_llm(self.LLMName)
        return llm_model.hello_world()