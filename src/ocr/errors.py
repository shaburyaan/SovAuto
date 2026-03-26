class OcrProcessingError(RuntimeError):
    pass


class OcrEmptyResultError(OcrProcessingError):
    pass
