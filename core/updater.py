from apscheduler.schedulers.background import BackgroundScheduler
from . import yahoo_api
import logging

logger = logging.getLogger(__name__)

def start():
        scheduler = BackgroundScheduler(job_default={'max_instances':1}, timezone='America/Sao_Paulo')
        #scheduler.add_job(yahoo_api.get_yahoo_cotacao, 'interval', minutes=1, max_instances=1, id="yahoo_api")
        scheduler.add_job(yahoo_api.get_yahoo_cotacao, 'cron', day_of_week='mon-sun', minute="*/5", replace_existing=True, id="yahoo_api")
        print(scheduler)
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.remove_job('yahoo_api')
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")    