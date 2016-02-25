#!/bin/bash

# Given we have a structure of service and consumer repositories
#   And a consumer needs to know the schema of a service and stores that schema somewhere in its repository
#  Then that stored schema should be updated automatically if the service schema was changed
#
# This script will push the changed schema to all consumers of a service if the consumers register themselves
# in the service repository. There needs to be a ".consumers.txt" file in the service repository.
# Expected structure: <owner/repo>:<path_to_schemas_folder>:<push_to_master|create_pr>
# Example:
# mycompany/api-sun:/api/sun/some/path/schemas/:create_pr
# mycompany/api-rain:/api/rain/another/path/schemas/:push_to_master
#
# In the file ".travis.yml" of the service repository, a hook needs to be added to run the script.
# Example:
# - if [ $TRAVIS_PYTHON_VERSION = "2.7" ] && [ $TRAVIS_PULL_REQUEST = "false" ] && [ $TRAVIS_BRANCH = "master" ]; then git clone --depth=1 git@github.com:deliveryhero/lymph-schema.git && ./lymph-schema/scripts/push-new-schema-to-consumers.sh this-service-repo; fi


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
printf "# -*- coding=utf-8 -*-\n\nimport json\n\nschema = json.loads('" >> ${schema_file_name}
lymph gen-schema conf/${pure_service_name}.yml >> ${schema_file_name}
printf "')" >> ${schema_file_name}
schema_file="$(pwd)/${schema_file_name}"


######################### UPDATE CONSUMERS #########################
create_pr () {
    branch_name="${service}_schema_update"
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

    # go to path and copy the new schema here and set name and email for github
    cd ${full_path_to_schema}
    git config --local user.email "travis@dhh-docs.com"
    git config --local user.name "Travis"
    cp ${schema_file} .

    # update the consumer according to the desired method (3. param)
    if [ "${3}" == "create_pr" ]; then
        create_pr
    elif [ "${3}" == "push_to_master" ]; then
        push_to_master
    else
        echo "command not found: ${3}"
    fi

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
