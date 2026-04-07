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
