from typing import Union

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, FileResponse

import uuid

class Participant(BaseModel):
    name: str
    team_name: str

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.get("/")
def create_item(item: Item):
    return item

# A Static Path with normal response
@app.get("/home/orbit/hackathon")
def orbit_hackathon():
    return {'msg':'Welcome to hackathon'}

# A static path with HTML response
@app.get("/home/orbit/hackathon/html")
def orbit_hackathon():
    html_content = """
    <html>
        <head>
            <title>Orbit Hackathon</title>
        </head>
        <body>
            <h1>Welcome to hackathon</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/home/orbit/hackathon/html/file")
def orbit_hackathon():
    return FileResponse('hackathon.html')

# A dynamic path
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# POST request
@app.post("/items/")
def create_item(item: Item):
    return {"msg": "Item created successfully!", "item": item}

# PUT request
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"msg": "Item updated successfully!", "item_id": item_id, "updated_item": item}

# DELETE Request
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"msg": f"Item with ID {item_id} deleted successfully!"}

# PATCH Request
@app.patch("/items/{item_id}")
def partial_update_item(item_id: int, item: Item):
    return {"msg": "Item partially updated!", "item_id": item_id, "updated_fields": item.dict(exclude_unset=True)}


# More complicated logics
def read_db():
    data = []
    try:
        with open('db.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                id_, name, team_name = line.strip().split(' ')
                data.append({"id": id_, "name": name, "team_name": team_name})
    except FileNotFoundError:
        pass  # File will be created if it doesn't exist
    return data

def write_to_db(id_, name, team_name):
    with open('db.txt', 'a') as file:
        file.write(f"{id_} {name} {team_name}\n")

@app.get("/data/")
def get_data(id: Union[str, None] = None):
    data = read_db()
    if id:
        for entry in data:
            if entry["id"] == id:
                return {"participant": entry}
        return {"msg": "Participant not found!"}
    else:
        return {"all_data": data}
    

# POST new participant data (handle both JSON and URL parameters)
@app.post("/data/")
async def add_participant(request: Request, participant: Union[Participant, None] = None, name: str = None, team_name: str = None):
    if participant:
        # If JSON data is sent
        name = participant.name
        team_name = participant.team_name
    else:
        # If data is sent via URL parameters
        params = request.query_params
        if not name or not team_name:
            name = params.get('name')
            team_name = params.get('team_name')

    # Check if name and team_name are available
    if not name or not team_name:
        return {"error": "Missing required fields 'name' and 'team_name'!"}

    # Generate a unique ID
    unique_id = str(uuid.uuid4())
    # Write new participant to the database
    write_to_db(unique_id, name, team_name)
    return {
        "msg": "New participant added successfully!",
        "participant": {
            "id": unique_id,
            "name": name,
            "team_name": team_name
        }
    }