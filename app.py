from fastapi import FastAPI, HTTPException
from letterboxdpy import user as lb_user

app = FastAPI(
    title="LetterboxdPY Wrapper",
    description="Simple API endpoints for Letterboxd user data via letterboxdpy",
    version="0.1.0",
)

@app.get("/user/{username}", summary="Get basic user info")
def get_user(username: str):
    """
    Returns the JSON-like dict that letterboxdpy produces
    for a given Letterboxd username.
    """
    try:
        u = lb_user.User(username)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch user: {e}")
    return u

@app.get("/user/{username}/following", summary="Get list of usernames this user is following")
def get_user_following(username: str):
    """
    Returns a list of usernames that the given user is following.
    """
    try:
        u = lb_user.User(username)
        following = lb_user.user_following(u)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch following: {e}")
    return {"following": following}

@app.get("/user/{username}/followers", summary="Get list of this user's followers")
def get_user_followers(username: str):
    """
    Returns a list of usernames who follow the given user.
    """
    try:
        u = lb_user.User(username)
        followers = lb_user.user_followers(u)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch followers: {e}")
    return {"followers": followers}

@app.get("/user/{username}/films", summary="Get list of films the user has watched")
def get_user_films(username: str):
    """
    Returns a list of (title, slug) tuples for every film
    the given user has marked as watched.
    """
    try:
        u = lb_user.User(username)
        films = lb_user.user_films_watched(u)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch watched films: {e}")
    return {"films": films}


if __name__ == "__main__":
    import uvicorn
    # host=0.0.0.0 makes it reachable from other machines on your network
    uvicorn.run("app:app", host="0.0.0.0", port=6996, reload=True)
