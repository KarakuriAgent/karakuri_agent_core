class UninitializedException implements Exception {
  final String className;
  UninitializedException(this.className);

  @override
  String toString() => "UninitializedViewModelException: $className";
}

class CancellationException implements Exception {
  final String cancelItem;
  CancellationException(this.cancelItem);

  @override
  String toString() => "$cancelItem was cancelled.";
}

class ServiceException implements Exception {
  final String className;
  final String methodName;
  final String message;
  ServiceException(this.className, this.methodName, {this.message = ""});

  @override
  String toString() => "ServiceException: $className.$methodName: $message";
}
