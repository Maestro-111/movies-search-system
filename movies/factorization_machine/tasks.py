from celery import shared_task
from celery.utils.log import get_task_logger

from .create_user_movie_relationships import output_data
from .train_fm import train_test_output
from .precompute_recommendations import user_playlist_recommendations

from pathlib import Path

logger = get_task_logger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


@shared_task
def model_pipeline():

    """
    create task for training the ranking model

    1) call output_data
    2) call train_test_output
    3) call precompute_recommendations (both playlist and general)
    """

    # output_data(output_file=os.path.join(BASE_DIR, "movies/data/ratings_data.xlsx"))
    # train_test_output(os.path.join(BASE_DIR, "movies/data/ratings_data.xlsx"))
    # user_playlist_recommendations()


    logger.info("model_pipeline is done!")

@shared_task
def sample_task():
    logger.info("The sample task just ran.")



