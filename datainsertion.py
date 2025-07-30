#Create an Azure Table based on the File / Private Knowledge Base

import csv
import streamlit as st
from azure.data.tables import TableServiceClient, TableEntity

# Set up your Azure Table Storage connection
connection_string = st.secrets['AZURE_STORAGE_CONNECTION_STRING']
table_name = "RevaFAQ"

# Create a TableServiceClient
table_service = TableServiceClient.from_connection_string(conn_str=connection_string)

# Create a table if it doesn't exist
try:
    table_service.create_table(table_name)
except Exception as e:
    print(f"Table already exists: {e}")

# Read the CSV file and upload the data
csv_file_path = "reva_faq.csv"

with open(csv_file_path,  encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row)
        # Create a new entity
        entity = TableEntity()
        entity['PartitionKey'] = "REVAFAQ"  # You can set this to whatever makes sense
        entity['RowKey'] = row['id']  # Use ID as RowKey
        entity['Question'] = row['question']
        entity['Answer'] = row['answer']

        # Upload the entity to the table
        try:
            table_service.get_table_client(table_name).create_entity(entity=entity)
            print(f"Uploaded: {entity['RowKey']} - {entity['Question']}")
        except Exception as e:
            print(e)
print("Data upload complete.")