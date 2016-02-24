#!/bin/bash


######################### READ ARGUMENTS #########################
# please give in the command line the service repository which should update
# its consumers. it needs to have in the base folder a .consumers.txt file
if (( $# < 1))
then
    echo "you need to give the name of the service repo, ie 'dhh-orders'"
    exit 1
fi

service=${1}


######################### CREATE SCHEMA #########################
# create schema file and update it with up-to-date schema for $service
service_dir=$(pwd)
pure_service_name=${service#dhh-}
schema_file_name="${service}-schema.py"
schema_file_name="${schema_file_name//-/_}"
touch ${schema_file_name}
printf "# -*- coding=utf-8 -*-\n\nimport json\n\nschema = " >> ${schema_file_name}
lymph gen-schema conf/${pure_service_name}.yml >> ${schema_file_name}
schema_file="$(pwd)/${schema_file_name}"


######################### UPDATE CONSUMERS #########################
create_pr () {
    branch_name="testing_schema_update"
    git checkout -b ${branch_name}
    git add --all :/
    git commit -m "update schema file ${schema_file_name}"
    git status
    git push -f origin ${branch_name}:${branch_name}
}

push_to_master () {
    git add --all :/
    git commit -m "update schema file ${schema_file_name}"
    git push -f origin master
}

update_repo () {
    # takes 3 arguments:
    # 1. repository name
    # 2. path to schema folder
    # 3. desired method to be updated ["push_to_master"|"create_pr"]

    repo_path="/tmp/${1}"
    full_path_to_schema="${repo_path}/${2}"

    # clone repo to path
    git clone git@github.com:${repo}.git ${repo_path}

    # go to path and copy the new schema here
    cd ${full_path_to_schema}
    cp ${schema_file} .

    # update the consumer according to the desired method (3. param)
    `${3}`

    # move out of $consumer folder and clean up
    cd ${service_dir}
    rm -rf ${repo_path}
}

######################### READ CONSUMERS FILE #########################
# read_.consumers.txt file. for every entry in it, call update_repo
while IFS='' read -r line || [[ -n "$line" ]]; do
    case "$line" in \#*) continue ;; esac
    if [ "$line" == "" ]; then
        continue
    fi
    repo=$(echo ${line} | cut -f1 -d:)
    path=$(echo ${line} | cut -f2 -d:)
    method=$(echo ${line} | cut -f3 -d:)
    update_repo ${repo} ${path} ${method}
done < ".consumers.txt"


######################### CLEAN UP #########################
# move out of $service folder and clean up
popd
rm -rf ${service}
