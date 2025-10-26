# generate_erd.py
from eralchemy import render_er
from app.models import Base  # Ensure your Base with metadata is imported

# Generate the ERD image from the SQLAlchemy metadata
render_er(Base.metadata, 'erd_diagram.png')
