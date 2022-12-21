docker build -f Dockerfile_edemineduc/Dockerfile -t etl:latest .
docker tag etl:latest edemineduc/etl:latest


docker build -f Dockerfile -t edecoderestapi:latest .
docker tag edecoderestapi:latest edemineduc/edecoderestapi:latest
docker run --name db -d --env-file .env -v /root/reporte-ede/data:/var/lib/postgresql/data -p 5432:5432 postgres:14.1-alpine

#--env DEBUG=True --link db:db --env DB_HOST=db
docker run --env DEBUG=True --link db:db --env DB_HOST=db -it --restart=always  --mount type=tmpfs,destination=/app/tmp -v /root/reporte-ede:/app -w /app -p 80:8080 edemineduc/edecoderestapi:latest
#docker compose up
#docker compose build