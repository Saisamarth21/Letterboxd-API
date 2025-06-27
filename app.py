import os
import json
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

def cached(key: str, ttl: int, fetch_fn):
    """Get from cache or call fetch_fn() and cache its result."""
    data = cache.get(key)
    if data:
        return json.loads(data)
    payload = fetch_fn()
    cache.set(key, json.dumps(payload), ex=ttl)
    return payload

@app.get("/user/{username}", summary="Get basic user info")
def get_user(username: str):
    """
    Returns the JSON-like dict that letterboxdpy produces
    for a given Letterboxd username.
    """
    try:
        return cached(
            key=f"lb:user:{username}",
            ttl=300,  # cache for 5 minutes
            # vars() will grab the User object's __dict__ and return a plain dict
            fetch_fn=lambda: vars(lb_user.User(username))
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch user: {e}")

@app.get("/user/{username}/following", summary="Get list of usernames this user is following")
def get_user_following(username: str):
    """
    Returns a list of usernames that the given user is following.
    """
    try:
        return cached(
            key=f"lb:following:{username}",
            ttl=300,
            fetch_fn=lambda: {"following": lb_user.user_following(lb_user.User(username))}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch following: {e}")

@app.get("/user/{username}/followers", summary="Get list of this user's followers")
def get_user_followers(username: str):
    """
    Returns a list of usernames who follow the given user.
    """
    try:
        return cached(
            key=f"lb:followers:{username}",
            ttl=300,
            fetch_fn=lambda: {"followers": lb_user.user_followers(lb_user.User(username))}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch followers: {e}")

@app.get("/user/{username}/films", summary="Get list of films the user has watched")
def get_user_films(username: str):
    """
    Returns a list of (title, slug) tuples for every film
    the given user has marked as watched.
    """
    try:
        return cached(
            key=f"lb:films:{username}",
            ttl=300,
            fetch_fn=lambda: {"films": lb_user.user_films_watched(lb_user.User(username))}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch watched films: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=6996, reload=True)
