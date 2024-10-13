class UninitializedViewModelException implements Exception {
  final String message;
  UninitializedViewModelException([this.message = "ViewModel not initialized"]);

  @override
  String toString() => "UninitializedViewModelException: $message";
}