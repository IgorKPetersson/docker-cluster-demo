# Docker Cluster Demo

A minimal web chatbot that can run as a regular Docker container, with Docker
Compose, or in a local Kubernetes cluster. The application uses the OpenAI
Responses API when `OPENAI_API_KEY` is configured and `DEMO_MODE=false`. A
clearly marked demo mode is also available for testing without an API key.

## Prerequisites

- Docker Desktop
- `kubectl` and Kubernetes enabled in Docker Desktop for part c
- An OpenAI API key for real AI responses

## Setup

```powershell
Copy-Item .env.example .env
```

To use the OpenAI API, add `OPENAI_API_KEY` to `.env` and set
`DEMO_MODE=false`. The `.env` file is ignored by Git and is never copied into
the Docker image.

## a) Regular Docker container

```powershell
docker build -t docker-cluster-demo:latest .
docker run --name chatbot-demo --rm -d -p 8080:8080 --env-file .env docker-cluster-demo:latest
```

Open <http://localhost:8080>, test the chatbot, and take a screenshot. Stop the
container when finished:

```powershell
docker stop chatbot-demo
```

## b) Docker Compose

```powershell
docker compose up --build -d
```

Open <http://localhost:8080>, test the chatbot, and take a screenshot. Stop and
remove the Compose resources when finished:

```powershell
docker compose down
```

## c) Kubernetes in Docker Desktop

Enable Kubernetes under **Docker Desktop → Settings → Kubernetes**. Confirm
that the active context is `docker-desktop`, build the image locally, and
apply the manifest:

```powershell
kubectl config use-context docker-desktop
docker build -t docker-cluster-demo:latest .
cmd /c "docker save docker-cluster-demo:latest | docker exec -i desktop-control-plane ctr --namespace k8s.io images import -"
kubectl create secret generic chatbot-env --from-env-file=.env
kubectl apply -f k8s/chatbot.yaml
kubectl rollout status deployment/chatbot
kubectl port-forward service/chatbot 8080:8080
```

While the port-forward is running, open <http://localhost:8080>, test the
chatbot, and take a screenshot. Stop the port-forward with Ctrl+C, then remove
the workload and API secret:

```powershell
kubectl delete -f k8s/chatbot.yaml
kubectl delete secret chatbot-env
```

Confirm that no chatbot resources remain:

```powershell
kubectl get pods,service -l app=chatbot
```

To stop the Kubernetes cluster itself, clear **Enable Kubernetes** under
**Docker Desktop → Settings → Kubernetes**, then select **Apply & restart**.

Kubernetes loads the API configuration from the `chatbot-env` Secret, which is
created from the Git-ignored `.env` file. The API key is never written directly
to the Kubernetes manifest.

## Health check

```powershell
curl.exe http://localhost:8080/health
```

## Screenshots

- [Regular Docker container](screenshots/a-docker-container.png)
- [Docker Compose](screenshots/b-docker-compose.png)
- [Chatbot running in Kubernetes](screenshots/c-kubernetes-chatbot.png)

The screenshot showing Kubernetes being enabled must be captured in Docker
Desktop when **Enable Kubernetes** is selected.

## License

This project is available under the [MIT License](LICENSE).
