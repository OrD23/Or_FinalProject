from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment='Data Structure Diagram for Models and CRUD Operations')

# ---------------------
# Define Model Nodes
# ---------------------
dot.node('User', '''User
- id: Integer
- name: String(100)
- email: String(100)
- role: String(10)
- password_hash: Text''')

dot.node('Scan', '''Scan
- id: Integer
- user_id: Integer (FK)
- target: String(255)
- scan_time: DateTime
- status: String(20)
- aggregated_data: JSON''')

dot.node('Vulnerability', '''Vulnerability
- id: Integer
- scan_id: Integer (FK)
- cve_id: String(50) [Unique]
- name: String(150)
- description: Text
- severity_score: String(20)
- severity: String(20)
- ... (other attributes)''')

dot.node('Fix', '''Fix
- id: Integer
- vulnerability_id: Integer (FK)
- recommended_fix: Text
- status: String(20)''')

# ---------------------
# Define Model Associations
# ---------------------
# User to Scan (one-to-many)
dot.edge('User', 'Scan', label='1..*', dir='both')

# Scan to Vulnerability (one-to-many)
dot.edge('Scan', 'Vulnerability', label='1..*', dir='both')

# Vulnerability to Fix (one-to-many)
dot.edge('Vulnerability', 'Fix', label='1..*', dir='both')

# ---------------------
# Define CRUD Function Nodes
# ---------------------
dot.node('create_user', 'create_user()')
dot.node('create_scan', 'create_scan()')
dot.node('add_vulnerability', 'add_vulnerability()')
dot.node('upsert_vulnerability', 'upsert_vulnerability()')
dot.node('add_fix', 'add_fix()')

# ---------------------
# Define CRUD-to-Model Relationships
# ---------------------
dot.edge('create_user', 'User', label='creates')
dot.edge('create_scan', 'Scan', label='creates')
dot.edge('add_vulnerability', 'Vulnerability', label='creates')
dot.edge('upsert_vulnerability', 'Vulnerability', label='updates/inserts')
dot.edge('add_fix', 'Fix', label='creates')

# ---------------------
# Render the Diagram
# ---------------------
dot.render('data_structure_diagram', format='png', view=True)
