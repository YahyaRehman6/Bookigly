import json

from rest_framework import renderers



class Customer_Renderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if ('Customer' in data) or ("message" in data):
            response = json.dumps({'api result':True,'Data':data})
            return response
        elif ("hotel" in data) and ("hotel images" in data):
            response = json.dumps({'api result': True, 'Data': data})
            return response
        elif ("Rooms" in data) and ("Room Amenities" in data) and ("Room Images" in data):
            response = json.dumps({'api result': True, 'Data': data})
            return response
        elif ("reservations" in data) or ("reservation" in data):
            # print(data)
            response = json.dumps({'api result': True, 'Data': data})
            return response
        elif ("message" in data):
            response = json.dumps({'api result': True, 'Data': data})
            return response
        else:
            response = json.dumps({'api result':False,"Message":"Something went wrong"})
            return response
