// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
class UninitializedException implements Exception {
  final String className;
  UninitializedException(this.className);

  @override
  String toString() => "UninitializedException: $className";
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

class RepositoryException implements Exception {
  final String className;
  final String methodName;
  final String message;
  RepositoryException(this.className, this.methodName, {this.message = ""});

  @override
  String toString() => "RepositoryException: $className.$methodName: $message";
}

class ProviderException implements Exception {
  final String providerName;
  final String message;
  ProviderException(this.providerName, {this.message = ""});

  @override
  String toString() => "ProviderException: $providerName: $message";
}
