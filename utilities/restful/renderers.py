from collections import OrderedDict

from rest_framework.renderers import JSONRenderer as RestJSONRenderer


class JSONRenderer(RestJSONRenderer):
    """
    Custom render class to return uniq object for all API request
    all DRF API request will return object with this criteria
    {
        'error': message of error,
        'result': content of request,
        'status': boolean
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        getattr(renderer_context.get('view').get_serializer().Meta, 'resource_name', 'objects')
        response_data = {}

        if renderer_context.get('response').exception:
            if 'detail' in data:
                response_data.update({'error': data['detail'], 'status': False})
            else:
                response_data.update({'error': data, 'status': False})
        else:
            if type(data) is OrderedDict:
                response_data = data
            else:
                response_data.update({'result': data, 'status': True})

        # call super to render the response
        return super().render(response_data, accepted_media_type, renderer_context)
