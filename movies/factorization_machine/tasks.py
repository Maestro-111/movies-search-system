from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task
def sample_task():

    """
    create task for training the ranking model

    1) call output_data
    2) call train_test_output
    3) call precompute_recommendations (both playlist and general)
    """


    logger.info("The sample task just ran.")



