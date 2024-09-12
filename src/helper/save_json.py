import json
import os
import aiofiles

from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Any, Optional

class DataJsonModel(BaseModel):
    link: str
    tags: List[str]
    source: str
    title: str
    sub_title: Optional[str] = None
    range_data: Optional[int] = None
    create_date: Optional[str] = None
    update_date: Optional[str] = None
    desc: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    path_data_raw: List[str] = Field(default_factory=list)
    crawling_time: str
    crawling_time_epoch: int
    table_name: Optional[str] = None
    country_name: Optional[str] = None
    level: str
    stage: str
    data: Any

class SaveJson:

    def __init__(self, response=None, tags=None, source=None, title=None, sub_title=None, range_date=None, create_date=None, update_date=None, desc=None, category=None, sub_category=None, path_data_raw=None, table_name=None, country_name=None, level=None, stage='Crawling data', data=None):
        self.response = response
        self.tags = tags
        self.source = source
        self.title = title
        self.sub_title = sub_title
        self.range_date = range_date
        self.create_date = create_date
        self.update_date = update_date
        self.desc = desc
        self.category = category
        self.sub_category = sub_category
        self.path_data_raw = path_data_raw or []
        self.table_name = table_name
        self.country_name = country_name
        self.level = level
        self.stage = stage
        self.data = data


    async def save_json_local(self, filename, *folders):
        directory = os.path.join('data', *folders)
        
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as json_file:
            data = self.mapping()
            await json_file.write(json.dumps(data, ensure_ascii=False))


    def mapping(self):
        now = datetime.now()
        current_time = now.strftime('%Y-%m-%d %H:%M:%S')
        current_epoch = int(now.timestamp())

        data_model = DataJsonModel(
            link = self.response,
            tags = self.tags,
            source = self.source,
            title = self.title,
            sub_title = self.sub_title,
            range_data = self.range_date,
            create_date = self.create_date,
            update_date = self.update_date,
            desc = self.desc,
            category = self.category,
            sub_category = self.sub_category,
            path_data_raw = self.path_data_raw,
            crawling_time = current_time,
            crawling_time_epoch = current_epoch,
            table_name = self.table_name,
            country_name = self.country_name,
            level = self.level,
            stage = self.stage,
            data  = self.data
        )

        return data_model.dict()