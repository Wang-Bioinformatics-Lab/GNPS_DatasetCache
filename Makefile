#Docker Compose
server-compose-interactive:
	docker-compose --compatibility build --parallel
	docker-compose --compatibility up 

server-compose-background:
	docker-compose --compatibility build
	docker-compose --compatibility up -d 

server-compose-production:
	docker-compose --compatibility build
	docker-compose --compatibility up -d 

attach:
	docker exec -i -t gnps_datasetcache_gnps-datasetcache-web_1 /bin/bash

attach-worker:
	docker exec -i -t gnps_datasetcache_gnps-datasetcache-worker_1  /bin/bash
