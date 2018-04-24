from oauth2_provider.models import AccessToken, Application, Grant, RefreshToken
from oauth_provider.models import Consumer, Token

def delete_user_from(model, user_id):
    user_query_results = model.objects.filter(user_id=user_id)
    return user_query_results.delete()

def delete_oauth2_data_by_user_value(user):
    list_of_models = [
        AccessToken,
        Application,
        Grant,
        RefreshToken,
        Consumer,
        Token,
    ]
    for model_class_name in list_of_models:
        delete_user_from(model=model_class_name, user_id=user.id)
    return True

def delete_from_oauth2_accesstoken(user):
    num_deleted_records, _ = delete_user_from(model=AccessToken, user_id=user.id)
    return num_deleted_records > 0

def delete_from_oauth2_application(user):
    num_deleted_records, _ = delete_user_from(model=Application, user_id=user.id)
    return num_deleted_records > 0

def delete_from_oauth2_grant(user):
    num_deleted_records, _ = delete_user_from(model=Grant, user_id=user.id)
    return num_deleted_records > 0

def delete_from_oauth2_refreshtoken(user):
    num_deleted_records, _ = delete_user_from(model=RefreshToken, user_id=user.id)
    return num_deleted_records > 0

def delete_from_oauth_consumer(user):
    num_deleted_records, _ = delete_user_from(model=Consumer, user_id=user.id)
    return num_deleted_records > 0

def delete_from_oauth_token(user):
    num_deleted_records, _ = delete_user_from(model=Token, user_id=user.id)
    return num_deleted_records > 0
