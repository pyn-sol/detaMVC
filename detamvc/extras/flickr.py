import os

import flickr_api

    
def setup_flickr_api():
    flickr_api.set_keys(
        api_key=os.environ['FLICKR_API_KEY'], 
        api_secret=os.environ['FLICKR_API_SECRET'])
    auth_handler = flickr_api.auth.AuthHandler(
        access_token_key=os.environ['FLICKR_ACCESS_TOKEN'], 
        access_token_secret=os.environ['FLICKR_ACCESS_SECRET'])
    flickr_api.set_auth_handler(auth_handler)


def __get_sizes(result: flickr_api.Photo):
    new_dict = dict()
    for nm, vals in result.getSizes().items():
        newname = nm.replace(' ', '_').lower()
        new_dict[newname] = vals
    return new_dict


def upload_photo(filepath: str, title: str, file_data=None):
    result = flickr_api.upload(
        photo_file=filepath, 
        photo_file_data=file_data,
        title=title, 
        is_public="0")
    return {
        'flickr_id': result.id, 
        'sizes': __get_sizes(result)}


def delete_photo(id: str):
    flickr_api.Photo(id=id).delete()


def authorize_app(api_key: str, api_secret: str, permission: str = 'read'):
    """
    Run this from the commandline when you need to authorize an app.

    Permission options: 'read', 'write', 'delete'
    """
    a = flickr_api.auth.AuthHandler(key=api_key, secret=api_secret) 
    url = a.get_authorization_url(permission)
    print('navigate to the following url:', url)
    print("Click 'Accept', you will be taken to an xml.")
    print("Locate the field 'oauth_verifier' and provide the value below.")
    oauth_verifier = input('oauth_verifier: ')
    a.set_verifier(oauth_verifier)
    a.access_token.key 
    a.access_token.secret
    print("add the following to your .env")
    print(f"FLICKR_API_KEY={api_key}")
    print(f"FLICKR_API_SECRET={api_secret}")
    print(f"FLICKR_ACCESS_TOKEN={a.access_token.key}")
    print(f"FLICKR_ACCESS_SECRET={a.access_token.secret}")
