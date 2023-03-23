import yaml

def generate_about_json():

    # load model.yaml
    with open("model.yaml", "r") as f:
        model_endpoint = yaml.load(f, Loader=yaml.FullLoader)

    return {
        "name": model_endpoint["name"],
        "description": model_endpoint["description"]
    }
