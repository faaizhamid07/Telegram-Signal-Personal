import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pathlib import Path
from app import db
from app.auth import login, require_auth
from app.telegram_listener import start_listener
from app.config import DASHBOARD_PASSWORD

logging.basicConfig(level=logging.INFO)
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    task = asyncio.create_task(start_listener())
    app.state.listener_task = task
    yield
    task.cancel()

app = FastAPI(title="Telegram Signal", version="0.1.0", lifespan=lifespan)

class LoginBody(BaseModel):
    password: str

class GroupBody(BaseModel):
    peer: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=200)

class KeywordBody(BaseModel):
    term: str = Field(min_length=1, max_length=120)

@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/login")
def do_login(body: LoginBody):
    return {"token": login(body.password)}

@app.get("/api/groups")
def get_groups(_: bool = Depends(require_auth)):
    return db.all_rows("SELECT * FROM groups ORDER BY title COLLATE NOCASE")

@app.post("/api/groups")
def add_group(body: GroupBody, _: bool = Depends(require_auth)):
    try:
        db.run("INSERT INTO groups(peer,title,enabled) VALUES(?,?,1)", (body.peer.strip().lstrip("@"), body.title.strip()))
    except Exception as e:
        raise HTTPException(409, "Group already exists or could not be added") from e
    return {"ok": True}

@app.patch("/api/groups/{group_id}")
def toggle_group(group_id: int, _: bool = Depends(require_auth)):
    rows = db.all_rows("SELECT enabled FROM groups WHERE id=?", (group_id,))
    if not rows:
        raise HTTPException(404, "Group not found")
    db.run("UPDATE groups SET enabled=? WHERE id=?", (0 if rows[0]["enabled"] else 1, group_id))
    return {"ok": True}

@app.delete("/api/groups/{group_id}")
def delete_group(group_id: int, _: bool = Depends(require_auth)):
    db.run("DELETE FROM groups WHERE id=?", (group_id,))
    return {"ok": True}

@app.get("/api/keywords")
def get_keywords(_: bool = Depends(require_auth)):
    return db.all_rows("SELECT * FROM keywords ORDER BY term COLLATE NOCASE")

@app.post("/api/keywords")
def add_keyword(body: KeywordBody, _: bool = Depends(require_auth)):
    term = body.term.strip()
    try:
        db.run("INSERT INTO keywords(term,enabled) VALUES(?,1)", (term,))
    except Exception as e:
        raise HTTPException(409, "Keyword already exists") from e
    return {"ok": True}

@app.patch("/api/keywords/{keyword_id}")
def toggle_keyword(keyword_id: int, _: bool = Depends(require_auth)):
    rows = db.all_rows("SELECT enabled FROM keywords WHERE id=?", (keyword_id,))
    if not rows:
        raise HTTPException(404, "Keyword not found")
    db.run("UPDATE keywords SET enabled=? WHERE id=?", (0 if rows[0]["enabled"] else 1, keyword_id))
    return {"ok": True}

@app.delete("/api/keywords/{keyword_id}")
def delete_keyword(keyword_id: int, _: bool = Depends(require_auth)):
    db.run("DELETE FROM keywords WHERE id=?", (keyword_id,))
    return {"ok": True}

@app.get("/api/matches")
def get_matches(limit: int = 100, _: bool = Depends(require_auth)):
    limit = max(1, min(limit, 250))
    return db.all_rows("SELECT * FROM matches ORDER BY id DESC LIMIT ?", (limit,))

@app.delete("/api/matches")
def clear_matches(_: bool = Depends(require_auth)):
    db.run("DELETE FROM matches")
    return {"ok": True}

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")
    @app.get("/{path:path}")
    def frontend(path: str):
        requested = FRONTEND_DIST / path
        if path and requested.is_file() and FRONTEND_DIST in requested.resolve().parents:
            return FileResponse(requested)
        index = FRONTEND_DIST / "index.html"
        if index.exists():
            return FileResponse(index)
        raise HTTPException(404, "Frontend is not built. Run npm --prefix frontend run build.")
else:
    @app.get("/")
    def root():
        return {"name": "Telegram Signal", "docs": "/docs", "message": "Build the frontend with npm --prefix frontend run build."}
