# Karakuri Agent

日本語版はこちら [README_JP.md](README_JP.md).

Karakuri Agent is a cross-platform application that enables interactive communication with AI using 2D images.

## Supported Platforms

| Platform       | Support Status |
|----------------|:--------------:|
| Android        |       🟢       |
| iOS            |       ❌       |
| Web            |       🟢       |
| macOS          |       ❌       |
| Linux          |       ❌       |
| Windows        |       ❌       |

## Supported Services and Endpoints

| Service        | Endpoint       | Support Status |
|----------------|----------------|:--------------:|
| OpenAI         | text           |       🟢       |
|                | text to speech |       🟢       |
|                | speech to text |       🟢       |
| VoiceVox       | text to speech |       🟢       |
| StyleBertVITS2 | text to speech |       ❌       |

## Quick Start
[![Open in IDX](https://cdn.idx.dev/btn/open_purple_32.svg)](https://idx.google.com/import?url=https://github.com/0235-jp/karakuri_agent)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/0235-jp/karakuri_agent)

## Development Environment Setup
Development is possible with a Flutter environment.
https://docs.flutter.dev/get-started/install

Easy setup is also possible with Docker compose.

### Installing Docker
```
curl -L https://get.docker.com | sh
```

### To run Docker commands without using sudo, add the current user to the Docker group.

#### If you don't know who the user is, run the following command to check the current user:
```
whoami
```

#### Run the following command. Replace $USER with the result obtained from running the above command:
```
sudo usermod -aG docker $USER
sudo reboot
```

### You can launch the image with the following command, and access it with Visual Studio Code's development container, etc., to develop as if in a local environment:
```
// for app
cd app
docker compose up -d

// for server
cd serer 
docker compose up -d
```

## app Command Examples
Here, as an example, we describe how to build for Web and start the server. For building on each platform, please modify and execute the commands accordingly.

### Initializing the Project
```
dart run rps get default

// for web
dart run rps get web
```

### Running the Build Runner
Generates language files, etc.
```
dart run rps gen
```

### Starting the Web Server
```
dart run rps run-release web
```

### Building for Web
Output to /build.
```
dart run rps build-release web
```

## Using Docker Compose
You can start the Web server in a Docker environment using the following command:
```
docker compose up -d
```
