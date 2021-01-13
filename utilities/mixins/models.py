from django.core.cache import cache
from django.db import models
from django.db.models.manager import Manager


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    # override default manager and user privet manager
    objects = None
    __objects = Manager()

    def __str__(self):
        return 'Singleton Object'

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls, **kwargs):
        if cache.get(cls.__name__) is None:
            obj, created = cls.__objects.get_or_create(pk=1, defaults=kwargs)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)
