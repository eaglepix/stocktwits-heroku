"""Basic Flask Example Using APScheduler"""

from flask import Flask
from flask_apscheduler import APScheduler
import time

class Config:
    """App configuration."""

    JOBS = [
        {
            "id": "job1",
            "func": "__main__:job1",
            "args": (),
            "trigger": "interval",
            "minutes": 4,
        }
    ]

    SCHEDULER_API_ENABLED = True

def job1():
    """job function to run main_process """

    from scrape_stocktwits_v1_4heroku import main_process
    print('Executing main process now...')
    start = time.time()
    main_process()
    time_elapsed = time.time() - start
    return print('Main process completed, time_elapsed:', time_elapsed)


if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(Config())
    scheduler = APScheduler()
    # it is also possible to enable the API directly
    # scheduler.api_enabled = True  # noqa: E800
    scheduler.init_app(app)
    scheduler.start()

    app.run()