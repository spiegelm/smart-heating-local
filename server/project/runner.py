from django.test.runner import DiscoverRunner  # Django 1.6's default
from colour_runner.django_runner import ColourRunnerMixin


class ColouredTestRunner(ColourRunnerMixin, DiscoverRunner):
    pass