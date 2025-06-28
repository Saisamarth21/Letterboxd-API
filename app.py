import os
import json
import time
from fastapi import FastAPI, HTTPException
from letterboxdpy import user as lb_user
import redis

app = FastAPI(
    title="LetterboxdPY Wrapper",
    description="Simple API endpoints for Letterboxd user data via letterboxdpy",
    version="0.1.0",
)

# Connect to Redis (service name 'redis' in Docker Compose)
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
cache = redis.from_url(redis_url, decode_responses=True)

# How fresh data should be (in seconds) before forcing a refresh
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "300"))  # default 5 minutes

def cached(key: str, fetch_fn):
    """
    Two-tier cache:
      - Store forever (until Redis is torn down).
      - Track last update timestamp and payload.
      - If age > REFRESH_INTERVAL, fetch fresh and overwrite.
    """
    entry = cache.get(key)
    now = time.time()
    if entry:
        # stored as JSON with 'payload' and 'ts'
        data = json.loads(entry)
        age = now - data.get("ts", 0)
        if age < REFRESH_INTERVAL:
            return data["payload"]
    # either no entry or stale
    payload = fetch_fn()
    cache.set(key, json.dumps({"payload": payload, "ts": now}))
    return payload

@app.get("/user/{username}", summary="Get basic user info")
def get_user(username: str):
    try:
        return cached(
            key=f"lb:user:{username}",
            fetch_fn=lambda: vars(lb_user.User(username))
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch user: {e}")

@app.get("/user/{username}/following", summary="Get list of usernames this user is following")
def get_user_following(username: str):
    try:
        return cached(
            key=f"lb:following:{username}",
            fetch_fn=lambda: {"following": lb_user.user_following(lb_user.User(username))}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch following: {e}")

@app.get("/user/{username}/followers", summary="Get list of this user's followers")
def get_user_followers(username: str):
    try:
        return cached(
            key=f"lb:followers:{username}",
            fetch_fn=lambda: {"followers": lb_user.user_followers(lb_user.User(username))}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch followers: {e}")

@app.get("/user/{username}/films", summary="Get list of films the user has watched")
def get_user_films(username: str):
    try:
        return cached(
            key=f"lb:films:{username}",
            fetch_fn=lambda: {"films": lb_user.user_films_watched(lb_user.User(username))}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch watched films: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=6996, reload=True)
