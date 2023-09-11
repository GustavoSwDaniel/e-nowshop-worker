import asyncio
from datetime import datetime
import json
from typing import Dict, Optional

import httpx
from aiologger import Logger
from httpx import TimeoutException, codes

from config import Config
from consumers.base_consumer import BaseConsumer
from pubnub.pubnub import PubNub



class CheckOrders(BaseConsumer):
    def __init__(self, url_broker: str, 
                 broker_session_timeout: int, 
                 broker_request_timeout: int,
                 logger: Logger, 
                 req_timeout: float, 
                 req_pagination_limit: int):
        super().__init__(url_broker, 
                         broker_session_timeout, 
                         broker_request_timeout, 
                         logger, 
                         req_timeout)
        self.request_attrs = {}
        self.req_params = {}


    async def subscribe(self, current_topic: str, next_topic: Optional[str] = None) -> None:
          await self.consumer_loop(self._processor, topic_name=current_topic, next_topic_name=next_topic, group_id='check_orders')

    async def _processor(self, message: Dict, current_topic: str, next_topic_name: Optional[str] = None) -> None:
        self.logger.info(f'Processing message: {message}')
        await self.check_orders(order=message, next_topic=next_topic_name)


    async def __update_order_status(self, order: Dict, status: str) -> None:
        async with httpx.AsyncClient(**self.request_attrs) as client:
            req = await client.patch(url=f'{Config.URL_GET_ORDERS}/orders/{order["uuid"]}/status', timeout=self.req_timeout, json={'status': status})
        self.logger.info(f'Requests status code {req.status_code}')
        if req.status_code == codes.OK:
            return req.json()['status']
        return 'not_found'

    async def check_orders(self, order: Dict, next_topic: str, offset: int = 0) -> None:
        try:
            self.logger.debug(f'Request attrs check_orders ')
            await self.__update_order_status(order=order, status='canceled')
        except TimeoutException as e:
            self.logger.exception(f'Request Timeout reached at {self.req_timeout}. Error: {str(e)}')
        except Exception as e:
            self.logger.error(f'[QueueOrders] Attempt request ordersv error: {str(e)}')
