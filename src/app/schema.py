"""
After we updated the main method to post instead of get it was using default of hello world
thats why we are creating this schema.
We will have this Query instead of Optional
"""

from pydantic import BaseModel

class Query(BaseModel):
    text: str