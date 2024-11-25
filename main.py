from typing import Union

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, FileResponse

import uuid

class Participant(BaseModel):
    name: str
    team_name: str

class UpdateParticipant(BaseModel):
    name: Union[str, None] = None
    team_name: Union[str, None] = None

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


###############-------------------#################
###############|VERY COMPLEX CODE|#################
###############-------------------################

# Function to read the database from db.txt
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

# Function to write a new entry to db.txt
def write_to_db(id_, name, team_name):
    with open('db.txt', 'a') as file:
        file.write(f"{id_} {name} {team_name}\n")

# Function to overwrite the entire db.txt (used for updating or deleting)
def save_db(data):
    with open('db.txt', 'w') as file:
        for entry in data:
            file.write(f"{entry['id']} {entry['name']} {entry['team_name']}\n")

# PUT to update a participant's data completely
@app.put("/data/")
async def update_participant(request: Request, id: str, participant: Union[Participant, None] = None, name: str = None, team_name: str = None):
    # Read existing data
    data = read_db()

    # Check if the participant exists
    for entry in data:
        if entry["id"] == id:
            # If JSON data is sent
            if participant:
                name = participant.name
                team_name = participant.team_name
            else:
                # If data is sent via URL parameters
                params = request.query_params
                name = name or params.get('name')
                team_name = team_name or params.get('team_name')

            if not name or not team_name:
                raise HTTPException(status_code=400, detail="Both 'name' and 'team_name' are required for PUT request.")

            # Update the participant's data
            entry["name"] = name
            entry["team_name"] = team_name

            # Save updated data to the database
            save_db(data)
            return {"msg": "Participant data updated successfully!", "participant": entry}

    raise HTTPException(status_code=404, detail="Participant not found!")

# PATCH to update a participant's data partially
@app.patch("/data/")
async def partial_update_participant(request: Request, id: str, participant: Union[UpdateParticipant, None] = None, name: str = None, team_name: str = None):
    # Read existing data
    data = read_db()

    # Check if the participant exists
    for entry in data:
        if entry["id"] == id:
            # If JSON data is sent
            if participant:
                name = participant.name if participant.name else entry["name"]
                team_name = participant.team_name if participant.team_name else entry["team_name"]
            else:
                # If data is sent via URL parameters
                params = request.query_params
                name = name or params.get('name', entry["name"])
                team_name = team_name or params.get('team_name', entry["team_name"])

            # Update the participant's data partially
            entry["name"] = name
            entry["team_name"] = team_name

            # Save updated data to the database
            save_db(data)
            return {"msg": "Participant data partially updated!", "participant": entry}

    raise HTTPException(status_code=404, detail="Participant not found!")

# DELETE a participant's data
@app.delete("/data/")
async def delete_participant(request: Request, id: str = None):
    # Read existing data
    data = read_db()

    # Look for the participant by ID
    for entry in data:
        if entry["id"] == id:
            data.remove(entry)  # Remove the entry from the list
            save_db(data)  # Save the updated list to the database
            return {"msg": f"Participant with ID {id} deleted successfully!"}

    raise HTTPException(status_code=404, detail="Participant not found!")