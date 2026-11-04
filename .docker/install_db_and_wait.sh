set -e

# Install the full structure (StaR-Eau schemas and plugin schema),
# in the same order as the processing algorithm "Create database structure",
# so that SchemaSpy documents all the schemas and their relationships
SQL_DIR=/src/${MODULE_NAME}/install/sql

echo 'Installation of the full structure from latest version'
for sql_file in \
  "00_initialize_database.sql" \
  "StaR-Eau/00-creation schemas.sql" \
  "StaR-Eau/01-creation domaines.sql" \
  "StaR-Eau/02-creation tables principales.sql" \
  "StaR-Eau/03-creation tables communes.sql" \
  "StaR-Eau/04-creation assainissement.sql" \
  "StaR-Eau/05-creation branchement assainissement.sql" \
  "StaR-Eau/06-creation eau potable.sql" \
  "StaR-Eau/07-creation branchement eau potable.sql" \
  "StaR-Eau/08-creation gestion pei.sql" \
  "StaR-Eau/09-creation table valeur.sql" \
  "StaR-Eau/10-creation_com_materiau.sql" \
  "StaR-Eau/210-contraintes_sur_liste_valeurs_AEP.sql" \
  "StaR-Eau/220-contraintes_sur_liste_valeurs_ASS.sql" \
  "StaR-Eau/220-contraintes_sur_liste_valeurs_COM.sql"
do
  echo "${sql_file}"
  psql service=test -v ON_ERROR_STOP=1 -f "${SQL_DIR}/${sql_file}" > /dev/null
done
for sql_file in `ls -d -v ${SQL_DIR}/${SCHEMA}/*.sql`; do
  echo "${sql_file}"
  psql service=test -v ON_ERROR_STOP=1 -f ${sql_file} > /dev/null
done
psql service=test -v ON_ERROR_STOP=1 -f "${SQL_DIR}/99_finalize_database.sql" > /dev/null

touch /tmp/.db-runner-ok
sleep infinity
