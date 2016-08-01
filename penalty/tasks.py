from celery.utils.log import get_task_logger
from tequilla.celery import app

from penalty.utils import init_set_penalties

logger = get_task_logger(__name__)


@app.task
def set_penalty():
    logger.info("Saved image from Flickr")
    init_set_penalties()
