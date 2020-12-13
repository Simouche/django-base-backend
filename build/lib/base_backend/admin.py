from . import SETTINGS


def register_app_models(app_name: str) -> None:
    """
    registers all models of a django app.
    should be called in the app's admin module.
    example:
        from base_backend.admin import register_app_models
        register_app_models('app_name')
    :param app_name: the django app name
    :return: None
    """
    from django.contrib import admin
    from django.apps import apps
    from django.contrib.admin.sites import AlreadyRegistered
    app_models = apps.get_app_config(app_name).get_models()
    for model in app_models:
        try:
            admin.site.register(model)
        except AlreadyRegistered:
            pass


if SETTINGS.get("REGISTER_BASE_BACKEND_MODELS", False):
    register_app_models("base_backend")
