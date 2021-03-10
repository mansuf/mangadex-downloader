class MangadexError(BaseException):
	"""Base Exception"""
	pass

class FetcherError(MangadexError):
	"""Raised when error happened during fetching manga"""
	pass
