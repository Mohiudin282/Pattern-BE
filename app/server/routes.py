from fastapi import APIRouter, Request
from uuid import uuid4
from fastapi.responses import JSONResponse
from .database import user_collection
import time

router = APIRouter()


@router.get("")
async def habits(request: Request):
    id = request.headers.get("Authorization")
    assert id
    user = await user_collection.find_one({"id": id}, {"_id": False})
    if not user:
        await user_collection.insert_one({"id": id, "habits": [], "created": time.time()})
    
    habits = await user_collection.find_one({"id": id}, {"_id": False})

    return habits

@router.post("/create")
async def create(request: Request):
    id = request.headers.get("Authorization")
    data = await request.json()
    assert id
    user = await user_collection.find_one({"id": id})
    if not user:
        return JSONResponse({"error":"User not found"}, 500)
    
    new_habbit = {
        "id": uuid4().hex,
        "name": data.get("name", "Unnamed"),
        "completed": [],
        "created":time.time()
    }
    
    await user_collection.update_one(
        {"id": id}, {"$push": {"habits": new_habbit}})
    
    habits = user.get("habits", [])
    habits.append(new_habbit)

    return {"habits": habits}

@router.post("/delete")
async def delete(request: Request):
    id = request.headers.get("Authorization")
    data = await request.json()
    habit_id = data.get("id")
    user = await user_collection.find_one({"id": id}, {"_id": False})
    if not user:
        return JSONResponse({"error": "User not found"}, 500)
    
    await user_collection.update_one(
        {"id": id}, {"$pull": {"habits": {"id": habit_id}}})
    
    habits = [habit for habit in user.get("habits", []) if habit.get("id") != habit_id]

    return {"habits": habits}

@router.post("/rename")
async def rename(request: Request):
    id = request.headers.get("ID")
    data = await request.json()
    habit_id = data.get("id")
    habit_name = data.get("name")
    assert id
    assert habit_id
    assert habit_name
    user = await user_collection.find_one({"id": id}, {"_id": False})
    if not user:
        return JSONResponse({"error": "User not found"}, 500)
    
    await user_collection.update_one(
        {"id": id, "habits.id": habit_id},
        {"$set": {"habits.$.name": habit_name}})
    
    habits = await user_collection.find_one({"id": id}, {"_id": False})

    return habits

@router.post("/log")
async def log(request: Request):
    id = request.headers.get("Authorization")
    data = await request.json()
    habit_id = data.get("id")
    day = data.get("day")
    assert id
    assert habit_id
    assert day

    user = await user_collection.find_one({"id": id}, {"_id": False})

    if not user:
        return JSONResponse({"error": "User not found"}, 500)

    result = await user_collection.update_one(
        {
            "id": id,
            "habits.id": habit_id,
        },
        {"$push": {"habits.$.completed": day}},
    )

    habits = await user_collection.find_one({"id": id}, {"_id": False})

    return habits

@router.post("/unlog")
async def unlog(request: Request):
    id = request.headers.get("Authorization")
    data = await request.json()
    habit_id = data.get("id")
    day = data.get("day")
    assert id
    assert habit_id
    assert day

    user = await user_collection.find_one({"id": id}, {"_id": False})

    if not user:
        return JSONResponse({"error": "User not found"}, 500)

    result = await user_collection.update_one(
        {
            "id": id,
            "habits.id": habit_id,
        },
        {"$pull": {"habits.$.completed": day}},
    )

    habits = await user_collection.find_one({"id": id}, {"_id": False})

    return habits