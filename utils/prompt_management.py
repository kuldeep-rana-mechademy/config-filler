import os
from typing import Dict, Any, List, Optional, Callable
from langfuse import Langfuse
from langchain_core.prompts import ChatPromptTemplate


class LangfusePromptManager:
    def __init__(self, logging: bool = True):
        """
        Initialize the Langfuse Prompt Manager.

        Args:
            api_key: Your Langfuse API key (defaults to LANGFUSE_API_KEY env variable)
            public_key: Your Langfuse public key (defaults to LANGFUSE_PUBLIC_KEY env variable)
            host: Langfuse API host
        """

        self.langfuse = Langfuse(
            secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
            public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
            host=os.environ.get("LANGFUSE_ENDPOINT"),
        )

        # Store prompts with their configurations
        self.prompts = {}

        # Define default configurations for different models
        self.default_configs = {
            "gpt-4o": {"temperature": 0.7, "max_tokens": 1000},
            "llama3.2:latest": {"temperature": 0.7},
        }
        self.logging = logging

    def get_prompt(self, name: str, label: str = "latest") -> Optional[Dict[str, Any]]:
        """
        Retrieve a prompt by its name.

        Args:
            name: Unique identifier for the prompt

        Returns:
            The prompt configuration if found, otherwise None
        """
        return self.langfuse.get_prompt(name, label=label, fallback=True)

    def add_prompt(
        self,
        name: str,
        prompt_text: str,
        config: Optional[Dict[str, Any]] = None,
        labels: Optional[List[str]] = None,
    ) -> None:
        """
        Add a new prompt to the manager.

        Args:
            name: Unique identifier for the prompt
            prompt_text: The prompt template with {{placeholders}}
            config: Configuration for the model (temperature, etc.)
            labels: Tags for categorizing and filtering prompts
        """
        # Use default config if none provided
        if config and "model" in config:
            model = config["model"]
            default = self.default_configs.get(model, {})
            # Merge with provided config, with provided values taking precedence
            merged_config = {**default, **config}
        else:
            merged_config = config or {"model": "llama3.2:latest", "temperature": 0}

        self.prompts[name] = {
            "name": name,
            "prompt": prompt_text,
            "config": merged_config,
            "labels": labels or [],
        }

        # Register the prompt with Langfuse
        return self.langfuse.create_prompt(
            name=name,
            prompt=prompt_text,
            config=merged_config,
            labels=labels or [],
        )

    def get_langchain_prompt(
        self, prompt_function: Callable[[], str], prompt_type=None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a Langchain prompt by its name.

        Args:
            name: Unique identifier for the prompt

        Returns:
            The prompt configuration if found, otherwise None
        """
        try:
            self.langfuse.client.health.health()
        except Exception as e:
            print(f"Error connecting to Langfuse: {e}")
            self.logging = False
        if self.logging:
            function_name = prompt_function.__name__
            prompt_text = prompt_function()
            langfuse_prompt = self.get_prompt(function_name)
            if langfuse_prompt.is_fallback:
                langfuse_prompt = self.add_prompt(
                    name=function_name,
                    prompt_text=prompt_text,
                    labels=["production"],
                )
            else:
                # update the prompt text if it has changed
                if langfuse_prompt.prompt != prompt_text:
                    langfuse_prompt = self.add_prompt(
                        name=function_name,
                        prompt_text=prompt_text,
                        labels=["production"],
                    )
            if prompt_type:
                prompt = ChatPromptTemplate.from_template(
                    langfuse_prompt.get_langchain_prompt(),
                    metadata={"langfuse_prompt": langfuse_prompt},
                )
            prompt = ChatPromptTemplate.from_template(
                langfuse_prompt.get_langchain_prompt(),
                metadata={"langfuse_prompt": langfuse_prompt},
            )
            return prompt
        else:
            # If logging is disabled, return a simple Langchain prompt
            return ChatPromptTemplate.from_template(
                prompt_function(), metadata={"langfuse_prompt": None}
            )
