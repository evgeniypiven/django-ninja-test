"""
Base Utils
"""

# Standard library imports.
import typing

# Related third party imports.

# Local application/library specific imports.


class UploadToGeneratorBase:
    def __call__(self, instance, filename) -> str:
        return self.generate(instance, filename)

    def generate(self, instance, filename) -> str:
        path = self.construct_path(instance, filename)
        delimiter = '/' if not path.endswith('/') else ''
        file_name = self.construct_filename(instance, filename)
        return f'{path}{delimiter}{file_name}'

    def construct_path(self, instance, filename) -> str:
        raise NotImplementedError

    def construct_filename(self, instance, filename) -> str:
        raise NotImplementedError

    @classmethod
    def get_extension(cls, filename: str, with_dot: bool = False, as_blank: bool = False) -> typing.Optional[str]:
        result = '' if as_blank else None
        parts = filename.split('.')

        if len(parts) > 1:
            result = parts[-1]
            if with_dot:
                result = f'.{result}'

        return result