# Railway Automation Docker Image

Docker image for running **railway-automation** container using Docker Hub.

[![ss](https://github.com/user-attachments/assets/fb0b82f2-b4ee-4b01-a089-b1614eeef013)](https://hub.docker.com/r/imvickykumar999/railway-automation)

## Docker Image

`imvickykumar999/railway-automation:latest`

---

## Pull Image from Docker Hub

```powershell
docker pull imvickykumar999/railway-automation:latest
```

---

## Run Container

```powershell
docker run -d --name railway-automation -p 5000:5000 imvickykumar999/railway-automation:latest
```

* `-d` → Run in background
* `--name railway-automation` → Assign container name
* `-p 5000:5000` → Map host port to container port

---

## Check Running Containers

```powershell
docker ps
```

To see all containers including stopped ones:

```powershell
docker ps -a
```

---

## Stop Container

```powershell
docker stop railway-automation
```

---

## Start Container Again

```powershell
docker start railway-automation
```

---

## Restart Container

```powershell
docker restart railway-automation
```

---

## Remove Container

First stop it:

```powershell
docker stop railway-automation
```

Then remove:

```powershell
docker rm railway-automation
```

---

## Remove Docker Image

```powershell
docker rmi imvickykumar999/railway-automation:latest
```

---

## View Container Logs

```powershell
docker logs railway-automation
```

---

## Enter Running Container

```powershell
docker exec -it railway-automation powershell
```

For Linux shell:

```powershell
docker exec -it railway-automation sh
```

---

## Pull Latest Version Again

```powershell
docker pull imvickykumar999/railway-automation:latest
```

---

## Full Reset (Remove old + Run fresh)

```powershell
docker stop railway-automation
docker rm railway-automation
docker pull imvickykumar999/railway-automation:latest
docker run -d --name railway-automation -p 5000:5000 imvickykumar999/railway-automation:latest
```

## Deployment Instructions (Windows PowerShell)

1.  **Build the Image:**
    Execute this command in your project root to build the container locally:

```powershell
docker build -t imvickykumar999/railway-automation:latest .
```
    
2.  **Verify the Build:**
    Ensure the image was created successfully:

```powershell
docker images | Select-String "railway-automation"
```
    
3.  **Push to Docker Hub:**
    First, ensure you are logged in, then push the image:

```powershell
docker login
docker push imvickykumar999/railway-automation:latest
```

![ss](https://github.com/user-attachments/assets/5e259979-960b-4738-b176-50ff09d7a5d7)
