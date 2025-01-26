# app1/main.py
from fastapi import FastAPI
from models import Base
import uvicorn
import pickle
import base64
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/metadata")
def get_metadata():
    metadata_dict = {}
    metadata = Base.metadata.tables.items()
    for table_name, table in metadata:
        metadata_dict[table_name] = {
            "columns": [
                {
                    "name": column.name,
                    "type": str(column.type),
                    "primary_key": column.primary_key,
                    "nullable": column.nullable,
                }
                for column in table.columns
            ]
        }
    return metadata_dict


@app.get("/metadata1")
def get_metadata():
    metadata_dict = {}
    print(str(Base.metadata.tables.items()))
    for table_name, table in Base.metadata.tables.items():
        metadata_dict[table_name] = table

    # Pickle the dictionary of metadata
    pickled_metadata = pickle.dumps(metadata_dict)

    # Encode the pickled data in base64
    base64_metadata = base64.b64encode(pickled_metadata)
    
    pickled_metadata_decode = base64.b64decode(base64_metadata)
    metadata_dict_decode = pickle.loads(pickled_metadata_decode)
    
    # Return the base64 encoded metadata as part of the response
    return {"metadata": base64_metadata}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)