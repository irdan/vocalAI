import logging

class EventManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        """ Static access method. """
        if cls._instance is None:
            logging.debug("Creating new instance of EventManager")
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        if cls._instance:
            cls._instance = None

    def __init__(self):
        """ Virtually private constructor. """
        if EventManager._instance is not None:
            raise Exception("This class is a singleton")
        else:
            EventManager._instance = self
            self.listeners = {}
            self.logger = logging.getLogger(__name__)
            self.logger.debug("EventManager instance created with empty listeners dictionary")

    def subscribe(self, event_type, listener):
        """
        Subscribes a listener to a specific type of event.
        
        Parameters:
            event_type (str): The type of event to listen for.
            listener (callable): The callback function to invoke when the event occurs.
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
            self.logger.debug(f"New event type added: {event_type}")
        self.listeners[event_type].append(listener)
        self.logger.debug(f"Listener subscribed to {event_type}")

    def publish(self, event_type, data):
        """
        Publishes an event to all registered listeners.

        Parameters:
            event_type (str): The type of event to publish.
            data (any): The data to pass to the listeners.
        """
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                try:
                    if data is not None:
                        listener(data)
                    else:
                        listener()
                except Exception as e:
                    self.logger.error(f"Error handling event '{event_type}': {str(e)}")
            self.logger.debug(f"Event published: {event_type} with data: {data}")

    def unsubscribe(self, event_type, listener):
        """
        Unsubscribes a listener from a specific type of event.
        
        Parameters:
            event_type (str): The type of event to unsubscribe from.
            listener (callable): The callback function to remove.
        """
        if event_type in self.listeners:
            self.listeners[event_type].remove(listener)
            self.logger.debug(f"Listener unsubscribed from {event_type}")
            if not self.listeners[event_type]:  # Remove the event type if no listeners are left
                del self.listeners[event_type]
                self.logger.debug(f"No more listeners for {event_type}, event type removed")

