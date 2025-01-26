# backend/app/services/llm_routing_services/llm_router_service.py
import json
from pathlib import Path
from backend.app.services.logging_service.logger import LoggingUtility

logging_utility = LoggingUtility()

class LlmRouter:
    """
    A dynamic routing service for resolving the appropriate LLM (Large Language Model) handler
    based on inference type, provider, and model. This class uses a JSON-based configuration
    to define routing rules and supports priority-based matching and fallback mechanisms.

    The router is designed to be extensible, allowing new models, providers, and inference types
    to be added without modifying the core logic. It adheres to the application's logging guidelines
    and ensures consistent, secure, and maintainable logging practices.

    Attributes:
        routes (list): A list of routing rules loaded from the configuration file.

    Methods:
        __init__(config_path): Initializes the router and loads routing rules.
        resolve_handler(inference_point, provider, model): Resolves the appropriate handler.
        _load_routes(config_path): Loads routing rules from a JSON configuration file.
        _matches_route(route, inference_point, provider, model): Checks if a route matches the request.
        _get_fallback_handler(inference_point): Retrieves the fallback handler for a given inference type.

    Example Usage:
        router = LlmRouter('routing_config.json')
        handler = router.resolve_handler(inference_point='cloud', provider='DeepSeek', model='deepseek-reasoner')
        # handler = 'CloudInference.deep_seekr1'

    Potential for Expansion:
        1. Support for dynamic configuration updates (e.g., reloading the config file without restarting the app).
        2. Integration with a database for storing and managing routing rules.
        3. Advanced matching logic (e.g., regex, custom functions).
        4. Metrics and monitoring for tracking routing decisions and performance.
        5. Caching frequently accessed routes for improved performance.
    """

    def __init__(self, config_path):
        """
        Initialize the LlmRouter with the path to the routing configuration file.

        Args:
            config_path (str): Path to the JSON configuration file containing routing rules.
        """
        self.routes = self._load_routes(config_path)
        self.routes.sort(key=lambda x: x.get('priority', 0), reverse=True)
        logging_utility.info("Router initialized with %d routes.", len(self.routes))

    def _load_routes(self, config_path):
        """
        Load routing rules from the JSON configuration file.

        Args:
            config_path (str): Path to the JSON configuration file.

        Returns:
            list: A list of routing rules.

        Raises:
            Exception: If the configuration file cannot be loaded or parsed.
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logging_utility.info("Successfully loaded routing configuration from %s.", config_path)
            return config.get('routes', [])
        except Exception as e:
            logging_utility.error("Failed to load routing configuration: %s", str(e))
            raise

    def resolve_handler(self, inference_point, provider, model):
        """
        Resolve the appropriate handler based on the request parameters.

        Args:
            inference_point (str): The type of inference ('local' or 'cloud').
            provider (str): The provider name (e.g., 'DeepSeek', 'Llama').
            model (str): The model name (e.g., 'llama3.1', 'deepseek-r1:8b').

        Returns:
            str: The resolved handler in the format 'ClassName.method_name'.

        Raises:
            ValueError: If no matching route or fallback handler is found.
        """
        logging_utility.info(
            "Resolving handler for inference_point=%s, provider=%s, model=%s",
            inference_point, provider, model
        )

        for route in self.routes:
            if self._matches_route(route, inference_point, provider, model):
                handler = route['handler']
                logging_utility.info(
                    "Matched route: inference_point=%s, provider=%s, model=%s → handler=%s",
                    inference_point, provider, model, handler
                )
                return handler

        logging_utility.warning(
            "No matching route found for inference_point=%s, provider=%s, model=%s. Using fallback.",
            inference_point, provider, model
        )
        return self._get_fallback_handler(inference_point)

    def _matches_route(self, route, inference_point, provider, model):
        """
        Check if a route matches the request parameters.

        Args:
            route (dict): A routing rule from the configuration.
            inference_point (str): The type of inference ('local' or 'cloud').
            provider (str): The provider name (e.g., 'DeepSeek', 'Llama').
            model (str): The model name (e.g., 'llama3.1', 'deepseek-r1:8b').

        Returns:
            bool: True if the route matches, False otherwise.
        """
        if route.get('inference_point') != inference_point:
            return False
        if 'provider' in route and route['provider'] != provider:
            return False
        if 'model' in route and route['model'] != model:
            return False
        return True

    def _get_fallback_handler(self, inference_point):
        """
        Get the fallback handler for the given inference type.

        Args:
            inference_point (str): The type of inference ('local' or 'cloud').

        Returns:
            str: The fallback handler in the format 'ClassName.method_name'.

        Raises:
            ValueError: If no fallback handler is found.
        """
        for route in self.routes:
            if route.get('inference_point') == inference_point and route.get('is_fallback', False):
                return route['handler']
        logging_utility.error("No fallback handler found for inference_point=%s.", inference_point)
        raise ValueError(f"No fallback handler found for inference_point={inference_point}")