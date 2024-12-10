#!/bin/bash

PYTHON_LICENSE="# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root."

DART_LICENSE="// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root."

find client/lib -name "*.dart" -type f | while read file; do
    if ! grep -q "Copyright" "$file"; then
        echo "$DART_LICENSE" | cat - "$file" > temp && mv temp "$file"
    fi
done

find server/app -name "*.py" -type f | while read file; do
    if ! grep -q "Copyright" "$file"; then
        echo "$PYTHON_LICENSE" | cat - "$file" > temp && mv temp "$file"
    fi
done
