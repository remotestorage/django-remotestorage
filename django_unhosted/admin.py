from django.contrib.admin.sites import AlreadyRegistered
from django.contrib import admin

from . import models
from oauth2app import models as oauth2app_models


class StoredObjectAdmin(admin.ModelAdmin):
	list_display = 'user', 'path', 'data'
	list_filter = 'user',

admin.site.register(models.StoredObject, StoredObjectAdmin)


try:
	class OAuth2_ClientAdmin(admin.ModelAdmin):
		list_display = 'name', 'user', 'description', 'redirect_uri'
		list_filter = 'name', 'user'

	admin.site.register(oauth2app_models.Client, OAuth2_ClientAdmin)
except AlreadyRegistered: pass


try:
	class OAuth2_AccessTokenAdmin(admin.ModelAdmin):
		list_display = 'client_name', 'user', 'scopes'
		list_filter = 'user',

		def scopes(self, obj):
			return ', '.join(obj.scope.all().values_list('key', flat=True))
		scopes.short_description = 'Scope'

		def client_name(self, obj):
			return obj.client.name
		client_name.short_description = 'Client'

	admin.site.register(oauth2app_models.AccessToken, OAuth2_AccessTokenAdmin)
except AlreadyRegistered: pass
