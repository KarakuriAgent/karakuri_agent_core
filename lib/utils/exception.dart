class UninitializedException implements Exception {
  final Type runtimeType;
  UninitializedException(this.runtimeType);

  @override
  String toString() => "UninitializedViewModelException: ${runtimeType.toString()}";
}
