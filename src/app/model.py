import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

"""
In cassandra, we don't want primary keys to be integers because cassandra is or can be
distrubuted accross multiple machines in the bigger cluster. UUID does at least indentifes 
data uniqely using UUID1.
We can only have one primary key in cassandra
"""

class SpamInference(Model):
    __keyspace__ = "spam_inferences"
    uuid = columns.UUID(primary_key=True, default=uuid.uuid1)
    query = columns.Text() # if query if big indexing it not a good idea 
    label = columns.Text()
    confidence = columns.Float()
    model_version = columns.Text(default='v1')