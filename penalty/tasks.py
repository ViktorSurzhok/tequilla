from celery.utils.log import get_task_logger
from tequilla.celery import app as celery

from penalty.utils import init_set_penalties

logger = get_task_logger(__name__)


@celery.task
def set_penalty():
    init_set_penalties()
