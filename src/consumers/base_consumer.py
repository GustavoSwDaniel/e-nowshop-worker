import abc
import json
from decimal import Decimal
from typing import Any, Callable, Dict, Optional

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiologger import Logger
import ssl
from config import Config


class BaseConsumer:
    def __init__(self, url_broker: str,
                 broker_session_timeout: int, broker_request_timeout: int, logger: Logger,
                 req_timeout: float):
        self.url_broker = url_broker
        self.broker_session_timeout = broker_session_timeout
        self.broker_request_timeout = broker_request_timeout
        self.logger = logger
        self.request_attrs = {'headers': {'Content-Type': 'application/json'}}
        self.req_timeout = req_timeout


    @abc.abstractmethod
    async def _processor(self, message: Dict, current_topic: str, next_topic_name: Optional[str] = None) -> None:
        ...

    @abc.abstractmethod
    async def subscribe(self, current_topic: str, next_topic: Optional[str] = None) -> None:
        ...

    async def produce(self, topic_name: str, message: Any) -> None:
        self.logger.info('Starting producer')
        print('alo')
        producer = AIOKafkaProducer(bootstrap_servers=Config.BROKER_SERVER, enable_idempotence=True,
                                    request_timeout_ms=self.broker_request_timeout,
                                    security_protocol="SASL_SSL",
                                    sasl_mechanism="PLAIN",
                                    ssl_context=Config.ssl_context,
                                    sasl_plain_username=Config.BROKER_USERNAME,
                                    sasl_plain_password=Config.BROKER_PASSWORD)
        await producer.start()
        self.logger.info('Producer started')
        try:
            self.logger.info(f'Sending message to topic {topic_name}')
            self.logger.debug(f'Sending message to topic {topic_name}: {message}')
            await producer.send_and_wait(topic_name, message.encode('utf-8'))
            self.logger.info('Message sent')
        finally:
            self.logger.info('Stopping producer')
            await producer.stop()
            self.logger.info('Producer stopped')


    async def consumer_loop(self, processor: Callable, topic_name: str, group_id: str,
                            next_topic_name: Optional[str] = None) -> None:
        self.logger.info(f'Starting consumer on topic {topic_name}')

        consumer = AIOKafkaConsumer(topic_name, bootstrap_servers=self.url_broker, group_id=group_id,
                                    session_timeout_ms=self.broker_session_timeout,
                                    request_timeout_ms=self.broker_request_timeout,
                                    security_protocol="SASL_SSL",
                                    sasl_mechanism="PLAIN",
                                    ssl_context=Config.ssl_context,
                                    sasl_plain_username=Config.BROKER_USERNAME,
                                    sasl_plain_password=Config.BROKER_PASSWORD)
        await consumer.start()

        self.logger.info(f'Starting to consume topic {topic_name}')

        try:
            async for msg in consumer:
                self.logger.info('Processing message')
                await processor(message=json.loads(msg.value.decode()), current_topic=topic_name,
                                next_topic_name=next_topic_name)
                self.logger.info('Message processed')
        finally:
            await consumer.stop()

    @staticmethod
    def txid2uuid(txtid: str) -> str:
        """
        Decode a UUID in a 32-char string format.

        Receive an encoded UUID in a 32-char string format and adds its hyphens
        back.

        Args:
            txtid (str): A 32-char string.

        Returns:
            An UUID.
        """
        return '-'.join([txtid[:8], txtid[8:12], txtid[12:16], txtid[16:20], txtid[20:]])

    @staticmethod
    def _to_float(number: int) -> float:
        return float(round(Decimal(number / 100), 2))
