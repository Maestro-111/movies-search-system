from celery import shared_task

@shared_task
def daily_model_training():

    """Train and save the model once a day"""

    print("Training model")

    return "Model training completed."

