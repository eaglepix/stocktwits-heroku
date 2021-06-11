from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
interval = 5
@sched.scheduled_job('interval', minutes=interval)
def timed_job():
    print(f'This job is run every {interval} minutes.')

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')

sched.start()