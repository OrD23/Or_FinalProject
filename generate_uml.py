from sqlalchemy import create_engine
from sqlalchemy_schemadisplay import create_schema_graph
from app.models import Base

# Option with an engine:
engine = create_engine("sqlite:///:memory:")

graph = create_schema_graph(
    metadata=Base.metadata,
    engine=engine,  # Now the engine parameter is provided
    show_datatypes=True,
    show_indexes=False,
    rankdir='LR',
    concentrate=False
)

graph.write_png('uml_diagram.png')
