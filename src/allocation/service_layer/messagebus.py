# pylint: disable=bare-except
from __future__ import annotations
import logging
from typing import List, Dict, Callable, Type, Union, TYPE_CHECKING
from allocation.domain import commands, events
from . import handlers

if TYPE_CHECKING:
    from allocation.service_layer import unit_of_work

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork):
    if isinstance(message, events.Event):
        handle_event(message, uow)
    elif isinstance(message, commands.Command):
        return handle_command(message, uow)
    else:
        raise Exception(f'{message} was not an Event or Command')


def handle_event(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug('handling event %s with handler %s', event, handler)
            handler(event, uow=uow)
        except:
            logger.exception('Exception handling event %s', event)
            continue


def handle_command(command, uow: unit_of_work.AbstractUnitOfWork):
    logger.debug('handling command %s', command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        return handler(command, uow=uow)
    except Exception:
        logger.exception('Exception handling command %s', command)
        raise


EVENT_HANDLERS = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.Allocate: handlers.allocate,
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}  # type: Dict[Type[commands.Command], Callable]
