## Steps to run the app:
1. Download this repository.
2. Run the docker command from the parent directory of this projects Dockerfile:
   
   ```sudo docker build -t file_details .```
   
   ```sudo docker run -p 5000:5000 --mount source=file_details_volume,target=/SpotOn file_details:latest```
3. Go to this local address: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Architecture:
Application uses Flask for template rendering and backend behaviour. Uploaded files are stored on a docker volume 
(```--mount source=file_details_volume,target=/SpotOn``` part of the command above). To avoid collisions between uploaded files, names of the stored 
files are unique and different from the names of the files sent by the user. 

Accepted file formats are: ***.json, .csv, .txt***. 

Metrics about app are available at the **/metrics** endpoint. 
Example behaviour and outputs:

[Screencast from 2024-05-13 12-46-38.webm](https://github.com/Pobudi/SpotOn/assets/92460956/2022a645-cbf5-481a-af4e-f8a9cb8eb82d)

Metrics:

![image](https://github.com/Pobudi/SpotOn/assets/92460956/dc2b8eaf-7449-4ce0-a4ee-b1c5b30ce8eb)

