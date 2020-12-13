from rest_framework.renderers import JSONRenderer


class DefaultApiResponse(object):
    def __init__(self, user=None, **kwargs):
        self.response = dict(
            status=kwargs.get('status', True),
            error=kwargs.get('error', 200),
            data=kwargs.get('data', []),
            message=kwargs.get('message', 'success')
        )


class CustomJSONRenderer(JSONRenderer):
    """
    Override the render method of the django rest framework JSONRenderer to allow the following:
    * adding a resource_name root element to all GET requests formatted with JSON
    * reformatting paginated results to the following structure {meta: {}, resource_name: [{},{}]}

    NB: This solution requires a custom pagination serializer and an attribute of 'resource_name'
    defined in the serializer
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = dict()
        # determine the resource name for this request - default to objects if not defined
        resource = getattr(renderer_context.get('view').get_serializer().Meta, 'resource_name', 'objects')

        # check if the results have been paginated
        if data.get('paginated_results'):
            # add the resource key and copy the results
            response_data['meta'] = data.get('meta')
            response_data[resource] = data.get('paginated_results')
        else:
            response_data[resource] = data

        # call super to render the response
        response = super(CustomJSONRenderer, self).render(response_data, accepted_media_type, renderer_context)

        return response
