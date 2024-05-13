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

[Demo video](https://github.com/Pobudi/SpotOn/assets/92460956/2022a645-cbf5-481a-af4e-f8a9cb8eb82d)

## Metrics:
Every metric is explained in a comment above it.

/metric endpoint:

![image](https://github.com/Pobudi/SpotOn/assets/92460956/dc2b8eaf-7449-4ce0-a4ee-b1c5b30ce8eb)

Example metric viusalization in prometheus:


![image](https://github.com/Pobudi/SpotOn/assets/92460956/97a0288f-eccb-43e4-84d2-19a5a6ff5ba3)



## Future enhacements:
In case when one docker container would not be sufficient to handle incoming traffic it would be advised to consider using Kubernetes or similiar service to allow scalability. Other possible solution would hosting on AWS EC2 instance with S3 AWS storage, and using AWS ELB for scalability.

# Warning!
### For testing purposes i set app secret key to a visible string. Before Production deployment, the key should be changed and stored as an environment variable. (Line 17 in main.py: ```app.config["SECRET_KEY"] = "secretsecret"```)
