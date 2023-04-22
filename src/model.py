from typing import Union, List, Dict
from pydantic import BaseModel, validator


class Query(BaseModel):
    index: str
    from_: Union[int, None] = 0
    size: Union[int, None] = 2
    key_words: Dict[str, str]
    offset: Union[List[str], None] = None

    @validator("index")
    def index_must_be_logs(cls, v):
        if v != "logs":
            raise ValueError("index must be 'logs'")
        return v

    @validator("key_words")
    def key_word_must_contain_k8s_labels_app(cls, v):
        if 'kubernetes.labels.app' not in v:
            raise ValueError("key_words must contain 'kubernetes.labels.app'")
        return v
