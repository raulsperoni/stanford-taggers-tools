#!/bin/bash
mongo v-mdg-vias --eval "db.dropDatabase()"
mongo sig-cruces-vias --eval "db.dropDatabase()"
mongoimport --db krypton --collection v-mdg-vias --jsonArray < /data/db/recursos_geo/v_mdg_vias.geojson
mongoimport --db krypton --collection sig-cruces-vias --jsonArray < /data/db/recursos_geo/sig_cruces_vias.geojson

