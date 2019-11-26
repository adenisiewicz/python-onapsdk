#!/bin/sh

INITIAL_FOLDER=${PWD}
INITIAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ -e requirements.txt ]
then 
    pip install -r requirements.txt
fi
if [ -e doc-requirements.txt ]
then 
    pip install -r doc-requirements.txt
fi
if [ -e requirements.txt ]
then 
    pip install .
fi

# Generating documentation for each other branch in a subdirectory
for BRANCH in $(git branch --remotes --format '%(refname:lstrip=3)' | grep -Ev '^(HEAD)$'); do
    git checkout $BRANCH
    cd ${DOC_PATH}
    make html
    mkdir -p public/$BRANCH
    mv _build/html/ public/$BRANCH
    rm -rf _build/html/
    cd ${INITIAL_FOLDER}
done
ln public/develop public/latest
git checkout $INITIAL_BRANCH
