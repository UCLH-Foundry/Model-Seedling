import logging

def init():
    # TODO: Perform any initialization of the model
    logging.info("Model initialized")
    return {"init": "DONE"}


def run(model_inputs: dict = None):
    # TODO: Add code here that calls your model
    #       model_inputs is a dictionary containing any inputs that were passed to the model endpoint
    #       This function should return a dictionary containing the model results
    
    logging.info("Model run started")
    model_results = {"result": "Hello World!"}
    logging.info("Model run completed")
    
    # return model results
    return model_results
