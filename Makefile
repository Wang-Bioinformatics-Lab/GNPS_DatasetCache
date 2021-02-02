#Docker Compose
server-compose-interactive:
	docker-compose build
	docker-compose up 

server-compose-background:
	docker-compose build
	docker-compose up -d 

attach:
	docker exec -i -t gnps_datasetcache_gnps-datasetcache-web_1 /bin/bash

attach-worker:
	docker exec -i -t gnps_datasetcache_gnps-datasetcache-worker_1  /bin/bash

