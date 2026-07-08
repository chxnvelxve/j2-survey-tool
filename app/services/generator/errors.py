"""Generator stage exceptions."""


class GeneratorError(Exception):
    """Base class for generator failures."""


class UnresolvedFlagsError(GeneratorError):
    """Generation blocked because merge flags are not all resolved."""


class EmptyMergedJobError(GeneratorError):
    """Generation blocked because the merged job has no access points."""


class MissingTemplateError(GeneratorError):
    """The .docx template file does not exist."""


class MissingPhotoFileError(GeneratorError):
    """A photo referenced in the merge snapshot is missing or unreadable."""


class NoAttachmentsError(GeneratorError):
    """Generation blocked because the job has no attachments."""
