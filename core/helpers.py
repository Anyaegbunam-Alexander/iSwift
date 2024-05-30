def response_dict(message: str, data: dict = None) -> dict:
    if data is None:
        data = {}
    response = {"message": message}
    if data:
        response["data"] = data
    return response
