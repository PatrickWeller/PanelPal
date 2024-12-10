import sqlite3
import json

# Connect to DB
conn = sqlite3.connect("panelpal.db")
cursor = conn.cursor()

# Initialise empty panel_data dictionary
empty_panel_data = {"panel_id": "", "panel_version": 0.0, "genome_build": ""}

# Convert the dictionary to JSON string
panel_data_json = json.dumps(empty_panel_data)

# Insert into the gene_list table with an empty panel_data JSON
cursor.execute(
    """
    INSERT INTO gene_list (bed_file_id, panel_data)
    VALUES (?, ?)
""",
    (1, panel_data_json),
)  # Replace '1' with the actual bed_file_id you want to associate

# Commit changes and close the connection
conn.commit()
conn.close()


# Connect to DB
conn = sqlite3.connect("panelpal.db")
cursor = conn.cursor()

# Retrieve the panel_data as JSON string from the database
cursor.execute("SELECT panel_data FROM gene_list WHERE id = ?", (1,))
result = cursor.fetchone()

# Convert the JSON string back to a Python dictionary
panel_data = json.loads(result[0])

# Now you can access the panel_data as a dictionary
print(panel_data)  # Output will be the current JSON data as a Python dictionary

# Close the connection
conn.close()
