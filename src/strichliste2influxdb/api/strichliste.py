import os
from typing import Any, Optional, List
from datetime import datetime
from urllib.parse import urljoin
from dataclasses import dataclass
from marshmallow import EXCLUDE

import marshmallow_dataclass

from requests import Session

@dataclass
class Article:
    id: int
    name: str
    usageCount: int

articles_schema = marshmallow_dataclass.class_schema(Article)(many=True, unknown=EXCLUDE)


class StrichlisteClient(Session):
    """
    >>> lol = StrichlisteClient("http://172.16.0.107/api/").get_articles()
    >>> for page in lol:
    ...     print(page)
    """
    def __init__(self, base_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._base_url = base_url

    def get_articles(self):
        count = None
        cursor = 0
        while count is None or count > cursor:
            res = self.get(
                urljoin(self._base_url, "article"), 
                params={
                    "offset": cursor
                }).json()

            if not count:
                count = res["count"]

            articles = articles_schema.load(res["articles"])

            cursor += len(articles)

            for a in articles:
                yield a

            
            