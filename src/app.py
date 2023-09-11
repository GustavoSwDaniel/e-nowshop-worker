import asyncio
import datetime
import os
import sys
from typing import List, Union

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import Config
from consumers.queue_orders import QueueOrders
from consumers.check_orders import CheckOrders


command_line_args = ['run_queue_order', 'run_check_status_order']

def choose_consumer_with_cmd_line(argv: List) -> Union[str, None]:
    print(':: Loading command line arguments')

    arg = argv[1]
    selected_consumer = argv[1]
    if arg not in command_line_args:
        print('Invalid argument')
        return

    return selected_consumer


def greetings(consumer: str) -> None:
    print(f':: Running {consumer} consumer with log_level {Config.LOG_LEVEL}')


async def run_jobs(selected_consumer):
    run_check_status_order = False
    if selected_consumer == 'run_check_status_order':
        run_check_status_order = True

    try:
        greetings(selected_consumer)
        print(f'Press Crtl+{"Break" if os.name == "nt" else "C"} to exit')

        if run_check_status_order:
            check_order = CheckOrders(url_broker=Config.BROKER_SERVER, 
                                      broker_session_timeout=Config.BROKER_SESSION_TIMEOUT,
                                      broker_request_timeout=Config.BROKER_REQUEST_TIMEOUT, 
                                      logger=Config.logger, 
                                      req_timeout=Config.REQUEST_TIMEOUT,
                                      req_pagination_limit=Config.QUEUE_ORDERS_PAGINATION_LIMIT)

            await check_order.subscribe(current_topic=Config.TOPIC_CHECK_ORDER)
       
    except(KeyboardInterrupt, SystemExit):
        pass

    except Exception as e:
        print(f'error {str(e)}')


def run_queue():
    greetings('run_queue')
    print(f'Press Crtl+{"Break" if os.name == "nt" else "C"} to exit')

    scheduler = AsyncIOScheduler()
    queue_orders = QueueOrders(url_broker=Config.BROKER_SERVER,
                               url_get_all_orders=Config.URL_GET_ORDERS,
                               broker_session_timeout=Config.BROKER_SESSION_TIMEOUT,
                               broker_request_timeout=Config.BROKER_REQUEST_TIMEOUT,
                               logger=Config.logger, 
                               req_timeout=Config.REQUEST_TIMEOUT,
                               req_pagination_limit=Config.QUEUE_ORDERS_PAGINATION_LIMIT)
    
    scheduler.add_job(queue_orders.queue_orders, trigger='interval',
                      kwargs=dict(next_topic=Config.TOPIC_CHECK_ORDER), id='queue_orders',
                      minutes=Config.INTERVAL)

    scheduler.start()
    asyncio.get_event_loop().run_forever()


def main(argv):
    if not len(argv) > 1:
        print(f'We need at least one argument to work properly and it must be one of {command_line_args}')
        return

    selected_consumer = choose_consumer_with_cmd_line(argv=argv)

    if selected_consumer == 'run_queue_order':
        run_queue()
    else:
        asyncio.run(run_jobs(selected_consumer))


if __name__ == '__main__':
    main(sys.argv)
