#!/bin/bash

while :; do
    case $1 in
         --action)
            if [[ "$2" ]]; then
                ACTION=$2
                shift
            fi
            ;;
        --zip-file)
            if [[ "$2" ]]; then
                ZIP_FILE=$2
                shift
            fi
            ;;
        *)
            break
    esac

    shift
done

USAGE="Usage: ./deploy.sh --action [build|create|update] --zip-file <function.zip>"

if [[ -z ${ACTION} ]] || [[ -z ${ZIP_FILE} ]]; then
    echo ${USAGE}

    exit -1

else
    if [[ ${ZIP_FILE} != *zip ]]; then
        echo "Unexpected value for zip file [${ZIP_FILE}]"

        echo ${USAGE}

        exit -2
    elif [[ ${ACTION} != "build" ]] && [[ ${ACTION} != "create" ]] && [[ ${ACTION} != "update" ]]; then
        echo "Unexpected value for action [${ACTION}]"

        echo ${USAGE}

        exit -2
    fi
fi


FUNCTION_NAME=thumbnail-generator
FUNCTION_DESCRIPTION="Thumbnail Creator"

ROLE=arn:aws:iam::991099351276:role/lambda-s3-role

AWS=`(which aws)`

build() {
    SAM=`(which sam)`
    ${SAM} build \
    --use-container \
    --build-image Function1=amazon/aws-sam-cli-build-image-python3.9

    PWD=`(which pwd)`
    PROJECT_ROOT_DIR=`${PWD}`
    BUILD_DIR=.aws-sam/build/ThumbnailGeneratorFunction

    cd $BUILD_DIR

    ZIP=`(which zip)`

    ${ZIP} -r ${ZIP_FILE} . \
    -x *.sh  \
    -x events/\*

    CP=`(which cp)`
    ${CP} ${ZIP_FILE}  ${PROJECT_ROOT_DIR}
}

create() {
    ${AWS} --region=us-west-2 lambda create-function \
        --function-name ${FUNCTION_NAME} \
        --zip-file fileb://${ZIP_FILE} \
        --description "${FUNCTION_DESCRIPTION}" \
        --handler lambda_function.lambda_handler \
        --runtime python3.9 \
        --timeout 30 \
        --memory-size 512 \
        --role ${ROLE}
}

update() {
    ${AWS} --region=us-west-2 lambda update-function-code \
        --function-name ${FUNCTION_NAME} \
        --zip-file fileb://${ZIP_FILE}
}


case $ACTION in
    build)
        # invoking build function
        build
        ;;
    create)
        # invoking create function
        create
        ;;
    update)
        # invoking update function
        update
        ;;
esac
