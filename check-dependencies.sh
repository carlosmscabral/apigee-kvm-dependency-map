#!/bin/bash

# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if [ -z "$APIGEE_PROJECT_ID" ]; then
  echo "No APIGEE_PROJECT_ID variable set"
  exit
fi

if [ -z "$APIGEE_KVM_ENV" ]; then
  echo "No APIGEE_KVM_ENV variable set"
  exit
fi


echo "Installing apigeecli"
curl -s https://raw.githubusercontent.com/apigee/apigeecli/main/downloadLatest.sh | bash
export PATH=$PATH:$HOME/.apigeecli/bin

TOKEN=$(gcloud auth print-access-token)
gcloud config set project "$APIGEE_PROJECT_ID"

echo "Listing KVMs for Env $APIGEE_KVM_ENV ..."
KVM_LIST=$(apigeecli kvms list -e $APIGEE_KVM_ENV -o $APIGEE_PROJECT_ID -t $TOKEN)
echo "Found KVMs for Env $APIGEE_KVM_ENV :"
echo $KVM_LIST

echo "Exporting proxies to local temporary folder ..."

mkdir -p ./tmp/proxies
mkdir -p ./tmp/sharedflows
cd ./tmp/proxies
apigeecli apis export -o $APIGEE_PROJECT_ID -t $TOKEN

for zipfile in *.zip; do
  # Extract the name without the .zip extension
  foldername="${zipfile%.*}"

  # Create the directory if it doesn't exist
  mkdir -p "$foldername"

  # Unzip the file into the directory
  unzip "$zipfile" -d "$foldername"

  echo "Extracted '$zipfile' into '$foldername'"
done

cd ../sharedflows/
apigeecli sharedflows export  -o $APIGEE_PROJECT_ID -t $TOKEN

for zipfile in *.zip; do
  # Extract the name without the .zip extension
  foldername="${zipfile%.*}"

  # Create the directory if it doesn't exist
  mkdir -p "$foldername"

  # Unzip the file into the directory
  unzip "$zipfile" -d "$foldername"

  echo "Extracted '$zipfile' into '$foldername'"
done

cd ../../
echo "Done exporting proxies and sharedflows"

echo "DEPENDENCIES - PROXIES"
echo "========================"

python build-dependencies.py "$KVM_LIST" "./tmp/proxies"

echo "DEPENDENCIES - SHARED FLOWS"
echo "========================"

python build-dependencies.py "$KVM_LIST" "./tmp/sharedflows"

echo "Done!"