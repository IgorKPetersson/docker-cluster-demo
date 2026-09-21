# Docker Cluster Demo

En minimal svensk webbchatbot som kan köras i en vanlig Docker-container, med
Docker Compose och i ett lokalt Kubernetes-kluster. Appen använder OpenAI
Responses API när `OPENAI_API_KEY` är satt och `DEMO_MODE=false`. För verifiering
utan en nyckel finns ett tydligt markerat demo-läge.

## Förutsättningar

- Docker Desktop
- `kubectl` och aktiverat Kubernetes i Docker Desktop för del c
- En OpenAI API-nyckel för riktiga AI-svar

## Förberedelser

```powershell
Copy-Item .env.example .env
```

För riktiga API-svar: fyll i `OPENAI_API_KEY` i `.env` och sätt
`DEMO_MODE=false`. `.env` ignoreras av Git och kopieras inte in i imagen.

## a) Vanlig Docker-container

```powershell
docker build -t docker-cluster-demo:latest .
docker run --name chatbot-demo --rm -d -p 8080:8080 --env-file .env docker-cluster-demo:latest
```

Öppna <http://localhost:8080>, testa chatboten och ta en skärmbild. Stäng sedan:

```powershell
docker stop chatbot-demo
```

## b) Docker Compose

```powershell
docker compose up --build -d
```

Öppna <http://localhost:8080>, testa och ta en skärmbild. Stäng sedan:

```powershell
docker compose down
```

## c) Kubernetes i Docker Desktop

Aktivera Kubernetes i Docker Desktop under **Settings → Kubernetes**. Kontrollera
att kontexten är `docker-desktop`, bygg imagen lokalt och applicera manifestet:

```powershell
kubectl config use-context docker-desktop
docker build -t docker-cluster-demo:latest .
cmd /c "docker save docker-cluster-demo:latest | docker exec -i desktop-control-plane ctr --namespace k8s.io images import -"
kubectl create secret generic chatbot-env --from-env-file=.env
kubectl apply -f k8s/chatbot.yaml
kubectl rollout status deployment/chatbot
kubectl port-forward service/chatbot 8080:8080
```

Medan `port-forward` kör: öppna <http://localhost:8080>, testa och ta en
skärmbild. Avsluta `port-forward` med Ctrl+C och stäng sedan av arbetslasten:

```powershell
kubectl delete -f k8s/chatbot.yaml
kubectl delete secret chatbot-env
```

Kontrollera att inga resurser är kvar:

```powershell
kubectl get pods,service -l app=chatbot
```

Om även själva klustret ska stängas av: avmarkera **Enable Kubernetes** i
Docker Desktop under **Settings → Kubernetes** och välj **Apply & restart**.

Kubernetes läser API-inställningarna från `chatbot-env`, som skapas direkt från
den Git-ignorerade `.env`-filen. Nyckeln skrivs därför aldrig direkt i YAML.

## Hälsokontroll

```powershell
curl.exe http://localhost:8080/health
```

## Skärmbilder

- [Vanlig Docker-container](screenshots/a-docker-container.png)
- [Docker Compose](screenshots/b-docker-compose.png)
- [Chatbot i Kubernetes](screenshots/c-kubernetes-chatbot.png)

Skärmbilden av själva aktiveringen av Kubernetes tas i Docker Desktop när
**Enable Kubernetes** slås på.

## Licens

Projektet är tillgängligt under [MIT-licensen](LICENSE).
