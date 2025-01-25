import base64
from pathlib import Path
from typing import Any, Dict, List, Type, Union

from loguru import logger
from pydantic import BaseModel

from .base_client import BaseClient


class OpenAIClient(BaseClient):
    """Client for OpenAI API"""

    def _format_vision_content(self, text: str, image_data: str) -> List[Dict]:
        """Format vision content for OpenAI API"""
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

    def create_structured_vision_completion(
        self,
        prompt: str,
        image: Union[str, Path],
        schema: Union[Dict, Type[BaseModel], BaseModel],
        model: str,
        **kwargs,
    ) -> Any:
        """
        Create a vision completion with structured output following a JSON schema.
        """
        json_schema = self._get_schema_from_input(schema)

        # Handle image input
        if isinstance(image, (str, Path)) and not str(image).startswith("data:"):
            with open(image, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode("utf-8")
        else:
            image_data = image.split("base64,")[1] if "base64," in image else image

        # Get provider-specific message format
        content = self._format_vision_content(prompt, image_data)

        try:
            completion = self.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": json_schema.get("title", "response"),
                        "strict": True,
                        "schema": json_schema,
                    },
                },
                **kwargs,
            )

            # If schema is a Pydantic model, parse the response
            if isinstance(schema, type) and issubclass(schema, BaseModel):
                return schema.model_validate_json(completion.choices[0].message.content)
            elif isinstance(schema, BaseModel):
                return schema.__class__.model_validate_json(completion.choices[0].message.content)
            return completion

        except Exception as e:
            logger.error(f"Failed to create structured vision completion: {str(e)}")
            raise
