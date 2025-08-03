from LLM.LLM_interface import LLMInterface
from LLM.gemini import Gemini

class LLMFactory:

    mappings = {
        "gemini": Gemini
    }


    @staticmethod
    def register_llm(llm_name: str, llm_class: type):
        if not issubclass(llm_class, LLMInterface):
            raise ValueError(f"Class {llm_class.__name__} must inherit from LLMInterface.")
        LLMFactory.mappings[llm_name] = llm_class


    @staticmethod
    def get_llm(llm_name: str) -> LLMInterface:
        if llm_name in LLMFactory.mappings:
            return LLMFactory.mappings[llm_name]()
        else:
            raise ValueError(f"LLM '{llm_name}' is not registered/supported.")
