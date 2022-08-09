import logging
from datetime import datetime
import json
import re
import six

logger = logging.getLogger(__name__)
SEARCH_URL_REGEX = re.compile("/v2/(.+)/search/(.*)")


class RequestLoggingMiddleware(object):
    """
        Log details about search requests and responses for easier debugging
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _should_log_details(request):
        return SEARCH_URL_REGEX.match(request.path) is not None

    @staticmethod
    def _get_unique_id(request):
        return request.META.get("UNIQUE_ID", "No Unique ID")

    @staticmethod
    def _extract_request_parameters(request):
        # This function ignores all exceptions, exceptions should be handled
        # by the actual endpoint method.
        search_params = {}
        if request.method == "GET":
            for field, value in six.iteritems(request.GET):
                try:
                    if field in ['filters', 'sort']:
                        search_params = json.loads(value)
                    elif field == 'field':
                        search_params['fields'] = request.GET.getlist('field')
                    else:
                        search_params[field] = value
                except:
                    pass
        elif request.method == "POST":
            try:
                search_params = json.loads(request.body)["criteria"]
            except:
                pass
        return search_params

    def _log_request_info(self, request):
        request_id = self._get_unique_id(request)
        search_type = SEARCH_URL_REGEX.match(request.path)
        params = self._extract_request_parameters(request)
        logger.info("[{}] Starting '{}' search".format(request_id,
                                                       search_type.group(1)))
        logger.info(
            "[{}] Fields: {}".format(request_id, params.get("fields", [])))
        logger.info(
            "[{}] Filters: {}".format(request_id, params.get("filters", {})))
        logger.info(
            "[{}] Pagination: {}".format(request_id, "limit" in params))

    def _log_request_exit(self, request, duration, exception=None):
        request_id = self._get_unique_id(request)
        if exception:
            logger.error(
                "[{}] Search failed after {} seconds".format(request_id,
                                                             duration.seconds))
            logger.exception(exception)
        else:
            logger.info(
                "[{}] Search completed after {} seconds".format(request_id,
                                                                duration.seconds))

    def __call__(self, request):
        if self._should_log_details(request):
            start = datetime.now()
            try:
                self._log_request_info(request)
                response = self.get_response(request)
                self._log_request_exit(request, datetime.now() - start)
                return response
            except Exception as e:
                # We don't actually want to handle exceptions, just give info.
                self._log_request_exit(request, datetime.now() - start,
                                       exception=e)
                raise e
        else:
            return self.get_response(request)
