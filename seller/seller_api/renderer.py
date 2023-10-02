from rest_framework import renderers
import json

class Seller_Signup_Renderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ''
        if  ('seller detail' and 'message') in data:
            response = json.dumps({'api result': True, "Data": data})
            return response
        else:
            response = json.dumps({'api result': False, "error": data})
            return response


class Seller_Renderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ''
        if 'message' in data:
            response = json.dumps({'api result':True,"Data":data})
            return response
        else:
            response = json.dumps({'api result':False,"errors":data})
            return response

class Seller_RUD_Renderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if "Seller" in data:
            response = json.dumps({'api result':True,"Data":data})
            return response
        elif "message" in data:
            response = json.dumps({'api result': True, "Data": data})
            return response

        else:
            response = json.dumps({'api result':False,'errors':data})
            return response


class Hotel_Image_LCRD_Renderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if ("Images") in data:
            response = json.dumps({'api result':True,"Data":data})
            return response
        elif "Image" in data:
            response = json.dumps({'api result': True, "Data": data})
            return response
        elif "message" in data:
            response = json.dumps({'api result': True, "Data": data})
            return response

        else:
            response = json.dumps({'api result':False,'errors':data})
            return response


class Room_LCRUD_Renderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if ("Rooms" in data) or ("Room" in data):
            response = json.dumps({'api result':True,"Data":data})
            return response
        if ("message" in data):
            response = json.dumps({'api result': True, "Data": data})
            return response
        else:
            response = json.dumps({'api result':False,"errors":data})
            return response


class Room_Images_LCRUD_Renderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if ("Room Images" in data) or ("Room Image" in data):
            response = json.dumps({'api result':True,"Data":data})
            return response
        elif "message" in data:
            response = json.dumps({'api result': True, "message": data['message']})
            return response
        else:
            response = json.dumps({'api result': False, "message": data})
            return response

class Room_Amenities_LCRUD_Renderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if ("amenities" in data) or ("amenity" in data):
            response = json.dumps({'api result': True, "Data": data})
            return response
        else:
            response = json.dumps({'api result': False, "message": "Something went wrong"})
            return response


class Pending_Reservations_LU_Rendrer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if ("reservations" in data):
            response = json.dumps({'api result':True,"Pending Reservation":data})
            return response
        elif ("reservation" in data):
            response = json.dumps({'api result': True, "Reservation": data})
            return response
        else:
            response = json.dumps({'api result': False, "message": "Something went wrong"})
            return response