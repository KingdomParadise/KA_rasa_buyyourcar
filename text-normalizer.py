import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata

import re
import unicodedata


class TextNormalizer(Component):
    """This component preprocess traininig data and input text according to certain rules"""

    name = "text_preprocessor"

    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""

        return []

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Apply text normalization on training data"""

        for _, example in enumerate(training_data.training_examples):
            if example.get("text"):
                print(example.get("text"))
                example.set("text", (self._normalize_text(example.get("text"))))

    def process(self, message: Message, **kwargs: Any) -> None:
        """process input text"""

        # get user text from message object
        text_message = message.get("text")
        if text_message:
            # preprocess text
            preprocessed_text = self._normalize_text(text_message)
            # update message object with the preprocessed text
            message.set("text", preprocessed_text, add_to_output=True)

    def _normalize_text(self, text_message: Text):
        "apply sequence of text normalization steps"

        # lower case input text
        text_message = text_message.lower()
        # removing extra spaces
        text_message = " ".join(text_message.split())
        # normalize english dialects
        text_message = (
            unicodedata.normalize("NFKD", text_message)
            .encode("ascii", "ignore")
            .decode("utf8")
        ).strip()
        # normalize ’ to ' (frequqent case)
        text_message = re.sub(r"[’]", "'", text_message)
        # remove non-english letters/numbers
        text_message = re.sub(r"[^a-z0-9\s.,'?\+()]", r"", text_message)
        # remove repeating characters by single character
        text_message = re.sub(r"(.)\1{2,}", r"\1", text_message)

        return text_message

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""

        pass

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["Component"] = None,
        **kwargs: Any,
    ) -> "Component":
        """Load this component from file."""

        if cached_component:
            return cached_component
        else:
            return cls(meta)
