# Utility for formats placeholders

# the concept:
# - create 2 class inherited from list (array mutable)
# - create 3 attributes (first, last, current) inside each classes
# - Use the class for placeholders object for volume and single formats
# - profit


class _Base(list):
    def __init__(self, *args, **kwargs):
        self.first = None
        self.last = None


# For `volume` placeholder in volume format
class VolumePlaceholder:
    def __init__(self, value):
        self.__value = value
        self.chapters = VolumeChaptersPlaceholder()

    def __str__(self) -> str:
        return str(self.__value)


# For `volume.chapters` placeholder in volume format
class VolumeChaptersPlaceholder(_Base):
    pass


# For `chapters` placeholder in single format
class SingleChaptersPlaceholder(_Base):
    pass
