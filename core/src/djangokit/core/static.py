import os

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage as Base


class ManifestStaticFilesStorage(Base):
    """Manifest storage that saves only files with hashed names.

    The purpose of this is to avoid deploying unprocessed static source
    files. Not only are these files typically not needed in production,
    their presence makes static location configuration (in Nginx,
    Apache, etc) more complex, especially with regard to caching.

    When using the base manifest storage, `collectstatic` first copies
    the unprocessed source files to the `STATIC_ROOT` directory (e.g.,
    `./static`). It then post-processes the source files, creating files
    with hashed file names and saves them to the `STATIC_ROOT`
    directory.

    During the post-processing phase, this storage system removes the
    source files that were copied to `STATIC_ROOT` (but keeps source
    files that weren't post-processed).

    """

    def post_process(self, *args, **kwargs):
        process = super().post_process(*args, **kwargs)
        for name, hashed_name, processed in process:
            yield name, hashed_name, processed
            if processed:
                os.remove(self.path(name))
