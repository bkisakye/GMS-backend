from rest_framework import status
from rest_framework.response import Response


def check_request_data(request, expected_data):
    if not request.data:
        print('No data in request')
        return Response({
            'status': 'failure',
            'error': 'No data in request',
            'data': request.data,
            'expected': expected_data
        }, status=status.HTTP_400_BAD_REQUEST)
    for data in expected_data:
        if data not in request.data:
            print('Please provide ' + data + '. Check your request data')
            return Response({
                'status': 'failure',
                'error': 'Please provide ' + data + '. Check your request data',
                'data': request.data,
                'expected': expected_data
            }, status=status.HTTP_400_BAD_REQUEST)
            print('Please provide ' + data + '. Check your request data')

    return 'ok'
