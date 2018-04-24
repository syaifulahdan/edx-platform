from oauth2_provider.models import AccessToken, Application, Grant, RefreshToken
from oauth_provider.models import Consumer, Token

def delete_user_from(model, user_id):
    user_query_results = model.objects.filter(user_id=user_id)
    return user_query_results.delete()

def delete_is_successful(num_deleted_records, _):
    return num_deleted_records > 0

def delete_from_oauth2_accesstoken(user):
    return delete_is_successful(delete_user_from(model=AccessToken, user_id=user.id))

def delete_from_oauth2_application(user):
    return delete_is_successful(delete_user_from(model=AccessToken, user_id=user.id))

def delete_from_oauth2_grant(user):
    return delete_is_successful(delete_user_from(model=AccessToken, user_id=user.id))

def delete_from_oauth2_refreshtoken(user):
    return delete_is_successful(delete_user_from(model=AccessToken, user_id=user.id))

def delete_from_oauth_consumer(user):
    return delete_is_successful(delete_user_from(model=AccessToken, user_id=user.id))

def delete_from_oauth_token(user):
    return delete_is_successful(delete_user_from(model=AccessToken, user_id=user.id))
