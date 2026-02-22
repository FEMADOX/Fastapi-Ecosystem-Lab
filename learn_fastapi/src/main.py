if __name__ == "__main__":
    import uvicorn

    uvicorn.run("learn_fastapi.src.first_steps.my_app:app", host="0.0.0.0", reload=True)
