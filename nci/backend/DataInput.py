from pydantic import BaseModel
from typing import List, Dict

class DataInput(BaseModel):
	params: Dict[str, float]
	filename: str
	dataframe: List[Dict]