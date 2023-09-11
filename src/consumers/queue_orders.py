import asyncio
import json
from typing import Dict, Optional
import datetime

import httpx
from aiologger import Logger
from httpx import TimeoutException, codes

from config import Config
from consumers.base_consumer import BaseConsumer


class QueueOrders(BaseConsumer):
    def __init__(self, url_broker: str, 
                 url_get_all_orders: str, 
                 broker_session_timeout: int, 
                 broker_request_timeout: int,
                 logger: Logger, 
                 req_timeout: float, 
                 req_pagination_limit: int) -> None:
        super().__init__(url_broker, 
                         broker_session_timeout, 
                         broker_request_timeout, 
                         logger, 
                         req_timeout)
        self.url_get_all_orders = url_get_all_orders
        self.request_attrs = {}
        self.req_params = {}


    async def subscribe(self, current_topic: str, next_topic: Optional[str] = None) -> None:
        ...

    async def _processor(self, message: Dict, current_topic: str, next_topic_name: Optional[str] = None) -> None:
        ...

    async def queue_orders(self, next_topic: str, offset: int = 0) -> None:
        try:
            print(datetime.datetime.now())
            self.logger.debug(f'Request attrs [{self.request_attrs}]')

            self.req_params['offset'] = offset
            have_orders = True
            while have_orders:
                async with httpx.AsyncClient(**self.request_attrs) as client:
                    req = await client.get(url=f'{self.url_get_all_orders}/orders?status=pending&expirate=True', timeout=self.req_timeout)
                self.logger.info(f'Requests status code {req.status_code}')

                if req.status_code == codes.OK:
                    orders = req.json()['data']
                    self.logger.info(f'Found {len(orders)} orders')
                    
                    for order in orders:
                        self.logger.debug(f'[QueueOrders][{order["uuid"]}] - Get order: {order}')
                        self.logger.info(f'[QueueOrders][{order["uuid"]}] - Producing')
                        await self.produce(topic_name=next_topic, message=json.dumps(order))
                        orders.remove(order)
                        self.logger.info(f'[QueueOrders][{order["uuid"]}] - Order produced to {next_topic}')
                    if not orders:
                       self.logger.info('Finished paginated request of orders.')
                       have_orders = False
                       break
        except TimeoutException as e:
            self.logger.exception(f'Request Timeout reached at {self.req_timeout}. Error: {str(e)}')

        except Exception as e:
            self.logger.error(f'[QueueOrders] Attempt request ordersv error: {str(e)}')
