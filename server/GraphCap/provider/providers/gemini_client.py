from typing import Any, Dict, List, Type, Union

from loguru import logger
from pydantic import BaseModel

from .base_client import BaseClient


class GeminiClient(BaseClient):
    """Client for Google's Gemini API with OpenAI compatibility layer"""

    def __init__(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"):
        # Ensure base_url doesn't end with a slash
        base_url = base_url.rstrip("/")
        logger.info(f"GeminiClient initialized with base_url: {base_url}")
        super().__init__(api_key=api_key, base_url=base_url)

    def _format_vision_content(self, text: str, image_data: str) -> List[Dict]:
        """Format vision content for Gemini API"""
        return [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
        ]

    def create_structured_completion(
        self, messages: List[Dict], schema: Union[Dict, Type[BaseModel], BaseModel], model: str, **kwargs
    ) -> Any:
        json_schema = self._get_schema_from_input(schema)

        try:
            completion = self.chat.completions.create(
                model=model, messages=messages, response_format={"type": "json_schema", "schema": json_schema}, **kwargs
            )

            if isinstance(schema, type) and issubclass(schema, BaseModel):
                return schema.model_validate_json(completion.choices[0].message.content)
            elif isinstance(schema, BaseModel):
                return schema.__class__.model_validate_json(completion.choices[0].message.content)
            return completion

        except Exception as e:
            logger.error(f"Failed to create structured completion: {str(e)}")
            raise
