"""
Posts Utils
"""

# Standard library imports.

# Related third party imports.
from django.utils import timezone
from rest_framework.authtoken.models import Token

# Local application/library specific imports.
from django_ninja_test.utils.files.utils import UploadToGeneratorBase
from authorization.models import CustomUser


class LocationUploadGenerator(UploadToGeneratorBase):
    def construct_path(self, instance, filename) -> str:
        return f'posts/title_photo/'

    def construct_filename(self, instance, filename) -> str:
        dt_part = timezone.now().strftime('%Y%m%d_%H%M%S')
        ext = self.get_extension(filename, True, True)
        name = f'posts_{instance.pk}_{dt_part}'
        return f'{name}{ext}'


location_upload_to = LocationUploadGenerator().generate


def get_user_with_token(token):
    if Token.objects.filter(key=token).exists():
        token_object = Token.objects.get(key=token)
        return CustomUser.objects.get(id=token_object.user_id)
    else:
        return None


def get_token_with_user(user_id):
    if CustomUser.objects.filter(id=user_id).exists():
        if Token.objects.filter(user_id=user_id).exists():
            return Token.objects.get(user_id=user_id).key
        else:
            return None
    else:
        return None
