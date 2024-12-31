Repository: Karakuri Agent
Description: Karakuri Agent is an open-source project aiming to create an AI agent accessible from any environment—whether it's a smart speaker, chat tool, or web application. By integrating various endpoints and services, it aims to realize a world where you can access a single agent from anywhere.
You can also define multiple agents simultaneously, each with unique roles, personalities, voices, and models.

Directory Structure:
- app/: Main application code

Setup:
- Run `apt update && apt install -y build-essential libsndf` and `pip install -r requirements.txt` to install dependencies
- Use `./start.sh` for run server

Guidelines:
- Run `ruff check` and `ruff format` and `pyright` after modifying code
- This project is powered by FastAPI.
- Use python for new code